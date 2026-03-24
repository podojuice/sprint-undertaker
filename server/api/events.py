from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select

from server.api.deps import DbSession, check_plugin_upgrade, get_current_installation
from server.models.character import Character
from server.models.event import ActivityEvent
from server.models.installation import ProviderInstallation
from server.models.notification import Notification
from server.models.user import User
from server.models.weekly_project import ProjectProgress, WeeklyProject
from server.schemas.event import CharacterStatusCache, EventBatchRequest, EventBatchResponse, EventIngestRequest, EventIngestResponse, ProjectStatusCache
from server.services.progression import apply_turn_summary
from server.services.projects import apply_weekly_project_progress
from server.services.titles import award_titles

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    payload: EventIngestRequest,
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
    x_plugin_version: Annotated[str | None, Header()] = None,
) -> EventIngestResponse:
    if installation.provider != payload.provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider mismatch")

    user = await db.get(User, installation.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    character = (
        await db.execute(select(Character).where(Character.user_id == installation.user_id))
    ).scalar_one_or_none()
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    event = ActivityEvent(
        installation_id=installation.id,
        provider=payload.provider,
        session_id=payload.session_id,
        canonical_event_type=payload.event_type,
        payload={"metrics": payload.metrics.model_dump(), "metadata": payload.metadata},
        occurred_at=payload.occurred_at,
    )
    db.add(event)

    progression = apply_turn_summary(character, payload.metrics)
    installation.last_seen_at = datetime.now(UTC)
    project_update = await apply_weekly_project_progress(db, installation, user, payload.metrics)
    awarded = await award_titles(db, user, character)
    notifications = progression.notifications + project_update.notifications + awarded.notifications

    notification_rows = (
        [(msg, "level_up") for msg in progression.notifications]
        + [(msg, "project_clear") for msg in project_update.notifications]
        + [(msg, "title_unlock") for msg in awarded.notifications]
    )
    for message, category in notification_rows:
        db.add(Notification(user_id=user.id, message=message, category=category))

    await db.commit()

    return EventIngestResponse(
        stat_changes=progression.stat_changes,
        exp_gained=progression.exp_gained,
        level_up=progression.level_up,
        new_titles=awarded.names,
        notifications=notifications,
        upgrade_notice=check_plugin_upgrade(x_plugin_version),
    )


@router.post("/batch", response_model=EventBatchResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event_batch(
    payload: EventBatchRequest,
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
    x_plugin_version: Annotated[str | None, Header()] = None,
) -> EventBatchResponse:
    user = await db.get(User, installation.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    character = (
        await db.execute(select(Character).where(Character.user_id == installation.user_id))
    ).scalar_one_or_none()
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    total_stat_changes: dict[str, int] = {}
    total_exp = 0
    any_level_up = False
    all_new_titles: list[str] = []
    all_notifications: list[str] = []

    for event in payload.events:
        if installation.provider != event.provider:
            continue

        db.add(ActivityEvent(
            installation_id=installation.id,
            provider=event.provider,
            session_id=event.session_id,
            canonical_event_type=event.event_type,
            payload={"metrics": event.metrics.model_dump(), "metadata": event.metadata},
            occurred_at=event.occurred_at,
        ))

        progression = apply_turn_summary(character, event.metrics)
        project_update = await apply_weekly_project_progress(db, installation, user, event.metrics)
        awarded = await award_titles(db, user, character)

        for k, v in progression.stat_changes.items():
            total_stat_changes[k] = total_stat_changes.get(k, 0) + v
        total_exp += progression.exp_gained
        if progression.level_up:
            any_level_up = True
        all_new_titles.extend(awarded.names)

        notifications = progression.notifications + project_update.notifications + awarded.notifications
        all_notifications.extend(notifications)
        notification_rows = (
            [(msg, "level_up") for msg in progression.notifications]
            + [(msg, "project_clear") for msg in project_update.notifications]
            + [(msg, "title_unlock") for msg in awarded.notifications]
        )
        for message, category in notification_rows:
            db.add(Notification(user_id=user.id, message=message, category=category))

    installation.last_seen_at = datetime.now(UTC)
    await db.commit()

    now = datetime.now(UTC)
    project_row = (
        await db.execute(
            select(WeeklyProject).where(
                WeeklyProject.active.is_(True),
                WeeklyProject.starts_at <= now,
                WeeklyProject.ends_at >= now,
            ).order_by(WeeklyProject.id.desc())
        )
    ).scalar_one_or_none()

    project_cache: ProjectStatusCache | None = None
    if project_row is not None:
        progress_row = (
            await db.execute(
                select(ProjectProgress).where(
                    ProjectProgress.project_id == project_row.id,
                    ProjectProgress.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        project_cache = ProjectStatusCache(
            title=project_row.title,
            progress_value=progress_row.progress_value if progress_row else 0,
            target_progress=project_row.target_progress,
            is_completed=progress_row.is_completed if progress_row else False,
        )

    required_exp = int(100 * character.level ** 1.5)
    return EventBatchResponse(
        processed=len(payload.events),
        stat_changes=total_stat_changes,
        exp_gained=total_exp,
        level_up=any_level_up,
        new_titles=list(dict.fromkeys(all_new_titles)),
        notifications=all_notifications,
        upgrade_notice=check_plugin_upgrade(x_plugin_version),
        character=CharacterStatusCache(
            level=character.level,
            title=character.title,
            exp=character.exp,
            exp_to_next_level=required_exp,
        ),
        project=project_cache,
    )
