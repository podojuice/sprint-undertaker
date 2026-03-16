from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from server.api.deps import DbSession, get_current_installation
from server.models.character import Character
from server.models.event import ActivityEvent
from server.models.installation import ProviderInstallation
from server.models.user import User
from server.schemas.event import EventIngestRequest, EventIngestResponse
from server.services.progression import apply_turn_summary
from server.services.projects import apply_weekly_project_progress
from server.services.titles import award_titles

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("", response_model=EventIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    payload: EventIngestRequest,
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
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

    await db.commit()

    return EventIngestResponse(
        stat_changes=progression.stat_changes,
        exp_gained=progression.exp_gained,
        level_up=progression.level_up,
        new_titles=awarded.names,
        notifications=notifications,
    )
