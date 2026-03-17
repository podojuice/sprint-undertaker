from fastapi import APIRouter, Depends
from sqlalchemy import select

from server.api.deps import DbSession, get_current_installation
from server.models.installation import ProviderInstallation
from server.models.notification import Notification
from server.schemas.notification import NotificationItem, NotificationListResponse

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/me", response_model=NotificationListResponse)
async def get_my_notifications(
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
) -> NotificationListResponse:
    rows = (
        await db.execute(
            select(Notification)
            .where(Notification.user_id == installation.user_id, Notification.is_read == False)
            .order_by(Notification.created_at.desc())
            .limit(20)
        )
    ).scalars().all()

    return NotificationListResponse(
        items=[NotificationItem.model_validate(n) for n in rows],
        unread_count=len(rows),
    )


@router.post("/me/read", status_code=204)
async def mark_notifications_read(
    db: DbSession,
    installation: ProviderInstallation = Depends(get_current_installation),
) -> None:
    rows = (
        await db.execute(
            select(Notification).where(
                Notification.user_id == installation.user_id, Notification.is_read == False
            )
        )
    ).scalars().all()

    for notification in rows:
        notification.is_read = True

    await db.commit()
