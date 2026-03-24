from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from server.models.installation import Provider


PromptLengthBucket = Literal["short", "medium", "long"]


class TurnSummaryMetrics(BaseModel):
    prompt_count: int = Field(ge=1)
    prompt_length_bucket: PromptLengthBucket
    edit_success_count: int = Field(ge=0)
    validation_success_count: int = Field(ge=0)
    validation_failure_count: int = Field(ge=0)
    tool_failure_count: int = Field(ge=0)
    model_name: str = Field(min_length=1, max_length=100)


class EventIngestRequest(BaseModel):
    provider: Literal[Provider.CLAUDE_CODE]
    event_type: Literal["turn_completed"]
    session_id: str | None = None
    occurred_at: datetime
    metrics: TurnSummaryMetrics
    metadata: dict = Field(default_factory=dict)


class EventIngestResponse(BaseModel):
    stat_changes: dict[str, int]
    exp_gained: int
    level_up: bool
    new_titles: list[str]
    notifications: list[str]
    upgrade_notice: str | None = None


class EventBatchRequest(BaseModel):
    events: list[EventIngestRequest] = Field(min_length=1, max_length=50)


class CharacterStatusCache(BaseModel):
    level: int
    title: str | None
    exp: int
    exp_to_next_level: int


class ProjectStatusCache(BaseModel):
    title: str
    progress_value: int
    target_progress: int
    is_completed: bool


class EventBatchResponse(BaseModel):
    processed: int
    stat_changes: dict[str, int]
    exp_gained: int
    level_up: bool
    new_titles: list[str]
    notifications: list[str]
    upgrade_notice: str | None = None
    character: CharacterStatusCache | None = None
    project: ProjectStatusCache | None = None
