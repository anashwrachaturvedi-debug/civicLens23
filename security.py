"""Password hashing and JWT token utilities.

This module contains the only code in the application permitted to
hash/verify passwords or encode/decode JWTs. Services call these
functions rather than implementing cryptographic logic themselves.
"""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.core.config import settings

_password_hasher = PasswordHash.recommended()


class TokenType(StrEnum):
    """Distinguishes JWT purposes so one token type cannot be replayed as another."""

    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


class TokenPayloadError(Exception):
    """Raised when a JWT is malformed, expired, invalid, or of the wrong type."""


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using the recommended modern algorithm."""
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return _password_hasher.verify(plain_password, hashed_password)


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    secret_key: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Encode a JWT with standard claims plus any additional custom claims."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str, extra_claims: dict[str, Any] | None = None
) -> str:
    """Create a short-lived JWT access token for the given subject (user ID)."""
    return _create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.JWT_SECRET_KEY,
        extra_claims=extra_claims,
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived JWT refresh token for the given subject (user ID)."""
    return _create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        secret_key=settings.JWT_REFRESH_SECRET_KEY,
    )


def create_password_reset_token(subject: str) -> str:
    """Create a short-lived JWT used exclusively for password reset flows."""
    return _create_token(
        subject=subject,
        token_type=TokenType.PASSWORD_RESET,
        expires_delta=timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        ),
        secret_key=settings.JWT_SECRET_KEY,
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    """Decode and validate a JWT, enforcing its expected token type.

    Raises:
        TokenPayloadError: If the token is expired, malformed, signed
            with the wrong key, or does not match ``expected_type``.
    """
    secret_key = (
        settings.JWT_REFRESH_SECRET_KEY
        if expected_type is TokenType.REFRESH
        else settings.JWT_SECRET_KEY
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenPayloadError("Token is invalid or expired.") from exc

    if payload.get("type") != expected_type.value:
        raise TokenPayloadError(
            f"Expected a '{expected_type.value}' token but received a different type."
        )
    return payload