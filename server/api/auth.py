from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from server.api.deps import DbSession
from server.models.character import Character
from server.models.email_code import CodeType, EmailCode
from server.models.user import User
from server.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from server.services.auth import (
    create_access_token,
    generate_verification_code,
    hash_password,
    verification_code_expires_at,
    verify_password,
)
from server.services.email import send_password_reset_code, send_verification_code

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def _issue_code(db: DbSession, email: str, code_type: CodeType) -> str:
    code = generate_verification_code()
    db.add(EmailCode(
        email=email,
        code=code,
        type=code_type,
        expires_at=verification_code_expires_at(),
    ))
    await db.commit()
    return code


async def _consume_code(db: DbSession, email: str, code: str, code_type: CodeType) -> EmailCode:
    record = (
        await db.execute(
            select(EmailCode)
            .where(
                EmailCode.email == email,
                EmailCode.code == code,
                EmailCode.type == code_type,
                EmailCode.used_at.is_(None),
            )
            .order_by(EmailCode.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if record is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")
    if record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code has expired")

    record.used_at = datetime.now(UTC)
    return record


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def register(payload: RegisterRequest, db: DbSession) -> MessageResponse:
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing is not None:
        if existing.is_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        # Unverified user: resend code
        code = await _issue_code(db, payload.email, CodeType.EMAIL_VERIFICATION)
        await send_verification_code(payload.email, code)
        return MessageResponse(message="Verification code resent. Check your email.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    character = Character(user_id=user.id, name=payload.character_name)
    db.add(character)
    await db.flush()

    code = await _issue_code(db, payload.email, CodeType.EMAIL_VERIFICATION)
    await send_verification_code(payload.email, code)

    return MessageResponse(message="Verification code sent. Check your email.")


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(payload: VerifyEmailRequest, db: DbSession) -> AuthResponse:
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await _consume_code(db, payload.email, payload.code, CodeType.EMAIL_VERIFICATION)

    user.is_verified = True
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
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    return AuthResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: DbSession) -> MessageResponse:
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    # Always return success to avoid email enumeration
    if user is not None and user.is_verified:
        code = await _issue_code(db, payload.email, CodeType.PASSWORD_RESET)
        await send_password_reset_code(payload.email, code)

    return MessageResponse(message="If that email is registered, a reset code has been sent.")


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(payload: ResetPasswordRequest, db: DbSession) -> AuthResponse:
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

    await _consume_code(db, payload.email, payload.code, CodeType.PASSWORD_RESET)

    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    await db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        email=user.email,
        created_at=user.created_at,
    )
