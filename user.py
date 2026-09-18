"""Pydantic v2 schemas for user data.

These schemas define the public shape of user data returned by the
API. They never expose sensitive fields like ``hashed_password`` or
``refresh_token_hash``.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserResponse(BaseModel):
    """Public-facing representation of a user, safe to return from any endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    """Fields a user is permitted to update on their own profile."""

    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone_number: str | None = Field(default=None, max_length=20)


class UserSummary(BaseModel):
    """Minimal user representation embedded within other resources (e.g. an issue's reporter)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    role: UserRole