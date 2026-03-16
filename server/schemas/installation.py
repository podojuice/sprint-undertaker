from datetime import datetime

from pydantic import BaseModel

from server.models.installation import InstallationStatus, Provider


class InstallationCreateRequest(BaseModel):
    provider: Provider
    installation_name: str


class InstallationResponse(BaseModel):
    id: int
    provider: Provider
    installation_name: str
    status: InstallationStatus
    api_key: str
    last_seen_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

