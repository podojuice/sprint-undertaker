from datetime import UTC, datetime, timedelta
from secrets import randbelow, token_urlsafe

from jose import jwt
from passlib.context import CryptContext

from server.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def generate_api_key() -> str:
    return f"su_sk_{token_urlsafe(24)}"


def generate_verification_code() -> str:
    """Generate a cryptographically random 6-digit numeric code."""
    return f"{randbelow(1_000_000):06d}"


def verification_code_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=15)
