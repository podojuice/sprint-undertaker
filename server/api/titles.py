from fastapi import APIRouter, Depends
from sqlalchemy import and_, select

from server.api.deps import DbSession, get_current_user
from server.models.title import Title, TitleVisibility, UserTitle
from server.models.user import User
from server.schemas.title import TitleListItemResponse
from server.services.titles import build_title_status, title_sort_key

router = APIRouter(prefix="/api/titles", tags=["titles"])


@router.get("/me", response_model=list[TitleListItemResponse])
async def list_my_titles(
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> list[TitleListItemResponse]:
    rows = (
        await db.execute(
            select(Title, UserTitle.earned_at)
            .outerjoin(
                UserTitle,
                and_(
                    UserTitle.title_id == Title.id,
                    UserTitle.user_id == current_user.id,
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

    items: list[TitleListItemResponse] = []
    for title, earned_at in visible_rows:
        status_label, status_note = build_title_status(title, earned_at)
        items.append(
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
        )
    return items
