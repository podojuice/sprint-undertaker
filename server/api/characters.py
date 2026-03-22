from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, select

from server.api.deps import DbSession, check_plugin_upgrade, get_current_installation, get_current_user
from server.models.character import Character
from server.models.event import ActivityEvent
from server.models.installation import ProviderInstallation
from server.models.title import Title, TitleVisibility, UserTitle
from server.models.user import User
from server.models.weekly_project import ProjectProgress, WeeklyProject
from server.schemas.character import (
    CharacterActivityItemResponse,
    CharacterActivityListResponse,
    CharacterResponse,
    CharacterStatusResponse,
    PublicProfileResponse,
    WeeklyProjectStatusResponse,
)
from server.schemas.title import TitleListItemResponse
from server.services.progression import required_exp_for_level
from server.services.titles import build_title_status, title_sort_key

router = APIRouter(prefix="/api/characters", tags=["characters"])


def _activity_summary(event: ActivityEvent) -> tuple[str, list[str]]:
    metrics = event.payload.get("metrics", {})
    if event.canonical_event_type == "project_cleared":
        project_title = event.payload.get("project_title", "Weekly project")
        clear_title_name = event.payload.get("clear_title_name")
        summary = f"Cleared weekly project {project_title}."
        stat_hints = ["title"] if clear_title_name else []
        return summary, stat_hints
    if event.canonical_event_type != "turn_completed":
        return ("Activity recorded.", [])

    summary_parts: list[str] = []
    stat_hints: list[str] = []

    edit_count = int(metrics.get("edit_success_count", 0))
    if edit_count > 0:
        summary_parts.append(f"{edit_count} edit success")
        stat_hints.append("impl")

    validation_success_count = int(metrics.get("validation_success_count", 0))
    validation_failure_count = int(metrics.get("validation_failure_count", 0))
    if validation_success_count > 0:
        summary_parts.append(f"{validation_success_count} validation success")
        stat_hints.append("stability")
    if validation_failure_count > 0:
        summary_parts.append(f"{validation_failure_count} validation failure")

    prompt_count = int(metrics.get("prompt_count", 0))
    prompt_length_bucket = metrics.get("prompt_length_bucket")
    if prompt_count > 0:
        bucket_text = f" ({prompt_length_bucket})" if prompt_length_bucket else ""
        summary_parts.append(f"{prompt_count} prompt{bucket_text}")
        stat_hints.append("focus")

    tool_failure_count = int(metrics.get("tool_failure_count", 0))
    if tool_failure_count > 0:
        summary_parts.append(f"{tool_failure_count} tool failure")

    model_name = metrics.get("model_name")
    if model_name:
        summary_parts.append(f"model {model_name}")

    if not summary_parts:
        return ("Turn completed.", [])
    return (", ".join(summary_parts) + ".", list(dict.fromkeys(stat_hints)))


@router.get("/status", response_model=CharacterStatusResponse)
async def get_character_status(
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
    x_plugin_version: Annotated[str | None, Header()] = None,
) -> CharacterStatusResponse:
    character = (
        await db.execute(select(Character).where(Character.user_id == installation.user_id))
    ).scalar_one_or_none()
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    exp_to_next = max(0, required_exp_for_level(character.level) - character.exp)
    return CharacterStatusResponse(
        name=character.name,
        character_class=character.character_class,
        level=character.level,
        exp=character.exp,
        exp_to_next_level=exp_to_next,
        impl=character.impl,
        stability=character.stability,
        focus=character.focus,
        title=character.title,
        upgrade_notice=check_plugin_upgrade(x_plugin_version),
    )


@router.get("/weekly-project", response_model=WeeklyProjectStatusResponse | None)
async def get_weekly_project_status(
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
) -> WeeklyProjectStatusResponse | None:
    from datetime import UTC, datetime
    now = datetime.now(UTC)
    project = (
        await db.execute(
            select(WeeklyProject).where(
                WeeklyProject.active.is_(True),
                WeeklyProject.starts_at <= now,
                WeeklyProject.ends_at >= now,
            ).order_by(WeeklyProject.id.desc())
        )
    ).scalar_one_or_none()

    if project is None:
        return None

    progress = (
        await db.execute(
            select(ProjectProgress).where(
                ProjectProgress.project_id == project.id,
                ProjectProgress.user_id == installation.user_id,
            )
        )
    ).scalar_one_or_none()

    return WeeklyProjectStatusResponse(
        project_title=project.title,
        description=project.description,
        progress_value=progress.progress_value if progress else 0,
        target_progress=project.target_progress,
        is_completed=progress.is_completed if progress else False,
        ends_at=project.ends_at,
    )


@router.get("/titles", response_model=list[TitleListItemResponse])
async def get_character_titles(
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
) -> list[TitleListItemResponse]:
    rows = (
        await db.execute(
            select(Title, UserTitle.earned_at)
            .outerjoin(
                UserTitle,
                and_(
                    UserTitle.title_id == Title.id,
                    UserTitle.user_id == installation.user_id,
                ),
            )
            .order_by(Title.id)
        )
    ).all()

    visible_rows = [
        (title, earned_at)
        for title, earned_at in rows
        if title.visibility == TitleVisibility.PUBLIC or earned_at is not None
    ]
    visible_rows.sort(key=lambda row: title_sort_key(row[0], row[1]))

    return [
        TitleListItemResponse(
            id=title.id,
            name=title.name,
            description=title.description,
            theme_color=title.theme_color,
            status_label=status_label,
            status_note=status_note,
            unlocked=earned_at is not None,
            earned_at=earned_at,
        )
        for title, earned_at in visible_rows
        for status_label, status_note in [build_title_status(title, earned_at)]
    ]


@router.get("/me", response_model=CharacterResponse)
async def get_my_character(
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> CharacterResponse:
    character = (
        await db.execute(
            select(Character).where(Character.user_id == current_user.id)
        )
    ).scalar_one()
    data = CharacterResponse.model_validate(character)
    data.exp_to_next_level = max(0, required_exp_for_level(character.level) - character.exp)
    return data


class EquipTitleRequest(BaseModel):
    title: str | None


@router.patch("/me/title", response_model=CharacterResponse)
async def equip_title(
    body: EquipTitleRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> CharacterResponse:
    character = (
        await db.execute(
            select(Character).where(Character.user_id == current_user.id)
        )
    ).scalar_one()

    if body.title is not None:
        owned = (
            await db.execute(
                select(UserTitle)
                .join(Title, Title.id == UserTitle.title_id)
                .where(
                    UserTitle.user_id == current_user.id,
                    Title.name == body.title,
                )
            )
        ).scalar_one_or_none()
        if owned is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title not owned")

    character.title = body.title
    await db.commit()
    await db.refresh(character)
    data = CharacterResponse.model_validate(character)
    data.exp_to_next_level = max(0, required_exp_for_level(character.level) - character.exp)
    return data


@router.get("/me/activity", response_model=CharacterActivityListResponse)
async def get_my_activity(
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> CharacterActivityListResponse:
    rows = (
        await db.execute(
            select(ActivityEvent)
            .join(
                ProviderInstallation,
                ProviderInstallation.id == ActivityEvent.installation_id,
            )
            .where(ProviderInstallation.user_id == current_user.id)
            .order_by(ActivityEvent.occurred_at.desc(), ActivityEvent.id.desc())
            .limit(10)
        )
    ).scalars().all()

    items = []
    for event in rows:
        summary, stat_hints = _activity_summary(event)
        items.append(
            CharacterActivityItemResponse(
                id=event.id,
                event_type=event.canonical_event_type,
                provider=event.provider.value,
                occurred_at=event.occurred_at,
                session_id=event.session_id,
                summary=summary,
                stat_hints=stat_hints,
            )
        )

    return CharacterActivityListResponse(items=items)


class VisibilityRequest(BaseModel):
    is_public: bool


@router.patch("/me/visibility")
async def set_visibility(
    body: VisibilityRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    character = (
        await db.execute(select(Character).where(Character.user_id == current_user.id))
    ).scalar_one()
    character.is_public = body.is_public
    await db.commit()
    return {"is_public": character.is_public}


@router.get("/profile/{nickname}", response_model=PublicProfileResponse)
async def get_public_profile(nickname: str, db: DbSession) -> PublicProfileResponse:
    character = (
        await db.execute(
            select(Character).where(Character.name == nickname, Character.is_public.is_(True))
        )
    ).scalar_one_or_none()
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    unlocked_public_titles = (
        await db.execute(
            select(Title.name)
            .join(UserTitle, UserTitle.title_id == Title.id)
            .where(
                UserTitle.user_id == character.user_id,
                Title.visibility == TitleVisibility.PUBLIC,
            )
            .order_by(UserTitle.earned_at)
        )
    ).scalars().all()

    return PublicProfileResponse(
        name=character.name,
        character_class=character.character_class,
        level=character.level,
        exp=character.exp,
        exp_to_next_level=max(0, required_exp_for_level(character.level) - character.exp),
        impl=character.impl,
        focus=character.focus,
        stability=character.stability,
        title=character.title,
        titles=list(unlocked_public_titles),
    )
