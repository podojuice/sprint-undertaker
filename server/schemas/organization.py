from datetime import datetime

from pydantic import BaseModel


class OrganizationCreateRequest(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    owner_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberResponse(BaseModel):
    user_id: int
    email: str
    character_name: str
    level: int
    title: str | None

