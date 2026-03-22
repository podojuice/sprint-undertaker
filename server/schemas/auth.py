from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    character_name: str

    @field_validator("character_name")
    @classmethod
    def no_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Character name cannot be empty")
        if any(c.isspace() for c in v):
            raise ValueError("Character name cannot contain spaces")
        return v


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class MessageResponse(BaseModel):
    message: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: EmailStr
    created_at: datetime

