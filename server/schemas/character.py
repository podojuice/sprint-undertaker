from datetime import datetime

from pydantic import BaseModel


class CharacterResponse(BaseModel):
    id: int
    name: str
    character_class: str
    level: int
    exp: int
    exp_to_next_level: int = 0
    impl: int
    focus: int
    stability: int
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterActivityItemResponse(BaseModel):
    id: int
    event_type: str
    provider: str
    occurred_at: datetime
    session_id: str | None
    summary: str
    stat_hints: list[str]


class CharacterActivityListResponse(BaseModel):
    items: list[CharacterActivityItemResponse]


class WeeklyProjectStatusResponse(BaseModel):
    project_title: str
    description: str
    progress_value: int
    target_progress: int
    is_completed: bool
    ends_at: datetime


class CharacterStatusResponse(BaseModel):
    name: str
    character_class: str
    level: int
    exp: int
    exp_to_next_level: int
    impl: int
    stability: int
    focus: int
    title: str | None
    upgrade_notice: str | None = None
