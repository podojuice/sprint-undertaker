from datetime import datetime

from pydantic import BaseModel


class NotificationItem(BaseModel):
    id: int
    message: str
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    unread_count: int
