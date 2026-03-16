from datetime import datetime

from pydantic import BaseModel


class TitleListItemResponse(BaseModel):
    id: int
    name: str
    description: str
    theme_color: str
    status_label: str
    status_note: str
    unlocked: bool
    earned_at: datetime | None
