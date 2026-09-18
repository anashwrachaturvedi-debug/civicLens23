"""
app/dependencies/current_user.py

Reusable, role-specific "current user" dependencies for FastAPI routes:

    - get_current_admin
    - get_current_authority
    - get_current_citizen

Each dependency builds on top of `get_current_active_user` (JWT
authentication + active-account check, from `app.dependencies.auth`) and
additionally enforces that the authenticated user holds the required role,
raising a 403 Forbidden if not.

This module intentionally contains NO business logic or database queries —
only authentication/authorization composition for use with `Depends()`.
"""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import AuthenticatedUser, get_current_active_user
from app.middleware.admin import UserRole

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _forbidden(detail: str) -> HTTPException:
    """Build a standardized 403 Forbidden HTTPException.

    Args:
        detail: Human-readable reason for the rejection.

    Returns:
        A configured HTTPException with status 403.
    """
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _normalize_role(role: UserRole | str) -> str:
    """Normalize a role value (enum or raw string) for consistent comparison.

    Args:
        role: The role to normalize, either a `UserRole` enum member or a
            plain string.

    Returns:
        The normalized, lowercase role string.
    """
    value = role.value if isinstance(role, UserRole) else str(role)
    return value.strip().lower()


def _ensure_role(user: AuthenticatedUser, required_role: UserRole) -> AuthenticatedUser:
    """Verify that a user holds the required role, raising 403 otherwise.

    Args:
        user: The authenticated, active user to check.
        required_role: The role required to proceed.

    Returns:
        The user, unchanged, if authorized.

    Raises:
        HTTPException: 403 if the user's role does not match `required_role`.
    """
    if _normalize_role(user.role) != _normalize_role(required_role):
        logger.warning(
            "Access denied for user_id=%s: role='%s' does not match "
            "required role='%s'.",
            user.id,
            user.role,
            required_role.value,
        )
        raise _forbidden(
            f"This action requires the '{required_role.value}' role."
        )

    logger.debug(
        "Role check passed for user_id=%s (role='%s').", user.id, required_role.value
    )
    return user


# --------------------------------------------------------------------------- #
# Role-specific dependencies
# --------------------------------------------------------------------------- #

async def get_current_admin(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
) -> AuthenticatedUser:
    """Resolve the current authenticated user and require the Admin role.

    Args:
        current_user: The authenticated, active user, resolved by
            `get_current_active_user` (JWT validation + active-account check).

    Returns:
        The authenticated user, if they hold the Admin role.

    Raises:
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not an Admin.
    """
    return _ensure_role(current_user, UserRole.ADMIN)


async def get_current_authority(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
) -> AuthenticatedUser:
    """Resolve the current authenticated user and require the Authority role.

    Args:
        current_user: The authenticated, active user, resolved by
            `get_current_active_user` (JWT validation + active-account check).

    Returns:
        The authenticated user, if they hold the Authority role.

    Raises:
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not an
            Authority.
    """
    return _ensure_role(current_user, UserRole.AUTHORITY)


async def get_current_citizen(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
) -> AuthenticatedUser:
    """Resolve the current authenticated user and require the Citizen role.

    Args:
        current_user: The authenticated, active user, resolved by
            `get_current_active_user` (JWT validation + active-account check).

    Returns:
        The authenticated user, if they hold the Citizen role.

    Raises:
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not a
            Citizen.
    """
    return _ensure_role(current_user, UserRole.CITIZEN)