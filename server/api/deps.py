from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.config import get_settings
from server.database import get_session
from server.models.installation import InstallationStatus, ProviderInstallation
from server.models.user import User


async def get_db_session() -> AsyncSession:
    async for session in get_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    db: DbSession, authorization: Annotated[str | None, Header()] = None
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = authorization.removeprefix("Bearer ").strip()
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_installation(
    db: DbSession, x_api_key: Annotated[str | None, Header()] = None
) -> ProviderInstallation:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    installation = (
        await db.execute(
            select(ProviderInstallation).where(ProviderInstallation.api_key == x_api_key)
        )
    ).scalar_one_or_none()

    if installation is None or installation.status != InstallationStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return installation


def check_plugin_upgrade(client_version: str | None) -> str | None:
    latest = get_settings().plugin_version_latest
    if client_version and client_version != latest:
        return f"Plugin update available: {latest} (yours: {client_version})"
    return None

