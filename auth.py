"""Pydantic v2 schemas for authentication endpoints.

Covers registration, login, token refresh/logout, and password
change/reset flows. Password fields carry minimum-strength validation
so weak credentials are rejected before ever reaching the service layer.
"""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserResponse

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def _validate_password_strength(value: str) -> str:
    """Shared password strength rule: at least 8 characters, letters and digits."""
    if len(value) < _PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long."
        )
    if not _PASSWORD_PATTERN.match(value):
        raise ValueError("Password must contain both letters and numbers.")
    return value


class RegisterRequest(BaseModel):
    """Payload required to register a new citizen account."""

    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone_number: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class LoginRequest(BaseModel):
    """Credentials required to authenticate an existing user."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Access/refresh token pair returned after successful login or refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Payload required to obtain a new access token."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Payload required to invalidate the current session's refresh token."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Payload required for an authenticated user to change their own password."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class ForgotPasswordRequest(BaseModel):
    """Payload required to initiate a password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Payload required to complete a password reset using a reset token."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password_strength(value)