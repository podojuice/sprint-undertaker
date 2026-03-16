from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from server.api.deps import DbSession
from server.models.character import Character
from server.models.user import User
from server.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from server.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DbSession) -> AuthResponse:
    existing_user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.flush()

    character = Character(user_id=user.id, name=payload.character_name)
    db.add(character)
    await db.commit()
    await db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: DbSession) -> AuthResponse:
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return AuthResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
        created_at=user.created_at,
    )

