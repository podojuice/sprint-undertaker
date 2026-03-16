from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from server.api.deps import DbSession, get_current_user
from server.models.installation import ProviderInstallation
from server.models.user import User
from server.schemas.installation import InstallationCreateRequest, InstallationResponse
from server.services.auth import generate_api_key

router = APIRouter(prefix="/api/installations", tags=["installations"])


@router.post("", response_model=InstallationResponse, status_code=status.HTTP_201_CREATED)
async def create_installation(
    payload: InstallationCreateRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> InstallationResponse:
    installation = ProviderInstallation(
        user_id=current_user.id,
        provider=payload.provider,
        installation_name=payload.installation_name,
        api_key=generate_api_key(),
    )
    db.add(installation)
    await db.commit()
    await db.refresh(installation)
    return InstallationResponse.model_validate(installation)


@router.get("", response_model=list[InstallationResponse])
async def list_installations(
    db: DbSession, current_user: User = Depends(get_current_user)
) -> list[InstallationResponse]:
    installations = (
        await db.execute(
            select(ProviderInstallation).where(ProviderInstallation.user_id == current_user.id)
        )
    ).scalars().all()
    return [InstallationResponse.model_validate(installation) for installation in installations]


@router.post("/{installation_id}/rotate-key", response_model=InstallationResponse)
async def rotate_installation_key(
    installation_id: int,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> InstallationResponse:
    installation = await db.get(ProviderInstallation, installation_id)
    if installation is None or installation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")

    installation.api_key = generate_api_key()
    installation.last_seen_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(installation)
    return InstallationResponse.model_validate(installation)

