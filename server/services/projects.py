from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.event import ActivityEvent
from server.models.installation import ProviderInstallation
from server.models.title import Title, TitleType, TitleVisibility, UserTitle
from server.models.user import User
from server.models.weekly_project import ProjectProgress, WeeklyProject
from server.schemas.event import TurnSummaryMetrics


DEFAULT_PROJECT = {
    "slug": "launch-the-orbital-stack",
    "title": "Launch the Orbital Stack",
    "theme": "space",
    "description": "Push the orbital stack over the line before the weekly window closes.",
    "target_progress": 100,
    "clear_title_name": "Orbital Breaker",
}


@dataclass
class ProjectUpdateResult:
    progress_added: int
    project_title: str | None
    project_completed: bool
    notifications: list[str]


async def seed_weekly_projects(session: AsyncSession) -> None:
    existing = (
        await session.execute(select(WeeklyProject).where(WeeklyProject.slug == DEFAULT_PROJECT["slug"]))
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    if existing is None:
        session.add(
            WeeklyProject(
                slug=DEFAULT_PROJECT["slug"],
                title=DEFAULT_PROJECT["title"],
                theme=DEFAULT_PROJECT["theme"],
                description=DEFAULT_PROJECT["description"],
                target_progress=DEFAULT_PROJECT["target_progress"],
                clear_title_name=DEFAULT_PROJECT["clear_title_name"],
                starts_at=now - timedelta(days=1),
                ends_at=now + timedelta(days=6),
                active=True,
            )
        )
        await session.commit()


def calculate_turn_project_progress(metrics: TurnSummaryMetrics) -> int:
    focus_delta = 1
    if metrics.prompt_length_bucket == "long":
        focus_delta += 1
    base_progress = metrics.edit_success_count * 5
    stability_bonus = metrics.validation_success_count * 2
    focus_bonus = focus_delta
    failure_drag = min(metrics.tool_failure_count, 2)
    return max(0, base_progress + stability_bonus + focus_bonus - failure_drag)


async def _ensure_project_title(session: AsyncSession, title_name: str, project_title: str) -> Title:
    title = (await session.execute(select(Title).where(Title.name == title_name))).scalar_one_or_none()
    if title is None:
        title = Title(
            name=title_name,
            description=f"주간 프로젝트 클리어: {project_title}",
            type=TitleType.PERSONAL,
            visibility=TitleVisibility.PUBLIC,
            condition=f"weekly_project_clear:{project_title}",
            theme_color="#6f8f4a",
            active_start_at=None,
            active_end_at=None,
        )
        session.add(title)
        await session.flush()
    return title


async def apply_weekly_project_progress(
    session: AsyncSession,
    installation: ProviderInstallation,
    user: User,
    metrics: TurnSummaryMetrics,
) -> ProjectUpdateResult:
    now = datetime.now(UTC)
    project = (
        await session.execute(
            select(WeeklyProject)
            .where(
                WeeklyProject.active.is_(True),
                WeeklyProject.starts_at <= now,
                WeeklyProject.ends_at >= now,
            )
            .order_by(WeeklyProject.id.desc())
        )
    ).scalar_one_or_none()

    if project is None:
        return ProjectUpdateResult(
            progress_added=0,
            project_title=None,
            project_completed=False,
            notifications=[],
        )

    progress_added = calculate_turn_project_progress(metrics)
    if progress_added <= 0:
        return ProjectUpdateResult(
            progress_added=0,
            project_title=project.title,
            project_completed=False,
            notifications=[],
        )

    progress = (
        await session.execute(
            select(ProjectProgress).where(
                ProjectProgress.project_id == project.id,
                ProjectProgress.user_id == user.id,
            )
        )
    ).scalar_one_or_none()

    if progress is None:
        progress = ProjectProgress(project_id=project.id, user_id=user.id)
        session.add(progress)
        await session.flush()

    if progress.is_completed:
        return ProjectUpdateResult(
            progress_added=0,
            project_title=project.title,
            project_completed=False,
            notifications=[],
        )

    progress.progress_value += progress_added
    notifications: list[str] = []
    project_completed = False

    if progress.progress_value >= project.target_progress:
        progress.is_completed = True
        progress.completed_at = now
        project_completed = True
        notifications.append(f"Project clear! {project.title}")
        notifications.append(f"Congratulations! Weekly boss defeated: {project.title}")

        title = await _ensure_project_title(session, project.clear_title_name, project.title)
        existing_user_title = (
            await session.execute(
                select(UserTitle).where(UserTitle.user_id == user.id, UserTitle.title_id == title.id)
            )
        ).scalar_one_or_none()
        if existing_user_title is None:
            session.add(UserTitle(user_id=user.id, title_id=title.id))
            notifications.append(f"Title unlocked: {project.clear_title_name}")

        session.add(
            ActivityEvent(
                installation_id=installation.id,
                provider=installation.provider,
                session_id=None,
                canonical_event_type="project_cleared",
                payload={
                    "project_slug": project.slug,
                    "project_title": project.title,
                    "clear_title_name": project.clear_title_name,
                },
                occurred_at=now,
            )
        )

    return ProjectUpdateResult(
        progress_added=progress_added,
        project_title=project.title,
        project_completed=project_completed,
        notifications=notifications,
    )
