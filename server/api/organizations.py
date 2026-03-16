from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from server.api.deps import DbSession, get_current_user
from server.models.character import Character
from server.models.organization import Organization
from server.models.user import OrgRole, User
from server.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationMemberResponse,
    OrganizationResponse,
)

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreateRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> OrganizationResponse:
    if current_user.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in organization")

    existing = (
        await db.execute(select(Organization).where(Organization.name == payload.name))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization name exists")

    organization = Organization(name=payload.name)
    db.add(organization)
    await db.flush()

    organization.owner_id = current_user.id
    current_user.organization_id = organization.id
    current_user.org_role = OrgRole.OWNER

    await db.commit()
    await db.refresh(organization)
    return OrganizationResponse.model_validate(organization)


@router.post("/{organization_id}/join", response_model=OrganizationResponse)
async def join_organization(
    organization_id: int,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> OrganizationResponse:
    if current_user.organization_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in organization")

    organization = await db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    current_user.organization_id = organization.id
    current_user.org_role = OrgRole.MEMBER
    await db.commit()
    await db.refresh(organization)
    return OrganizationResponse.model_validate(organization)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> OrganizationResponse:
    organization = await db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if current_user.organization_id != organization.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return OrganizationResponse.model_validate(organization)


@router.get("/{organization_id}/members", response_model=list[OrganizationMemberResponse])
async def get_organization_members(
    organization_id: int,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> list[OrganizationMemberResponse]:
    if current_user.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    organization = (
        await db.execute(
            select(Organization)
            .options(selectinload(Organization.members).selectinload(User.character))
            .where(Organization.id == organization_id)
        )
    ).scalar_one_or_none()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    members: list[OrganizationMemberResponse] = []
    for member in organization.members:
        character = member.character
        if character is None:
            continue
        members.append(
            OrganizationMemberResponse(
                user_id=member.id,
                email=member.email,
                character_name=character.name,
                level=character.level,
                title=character.title,
            )
        )
    return members

