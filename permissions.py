"""
app/dependencies/permissions.py

Reusable, role-based access control (RBAC) dependency factories:

    - require_admin()
    - require_authority()
    - require_citizen()
    - require_super_admin()

Each factory returns a FastAPI dependency that layers on top of
`get_current_active_user` (JWT validation + active-account check, from
`app.dependencies.auth`) and additionally enforces that the authenticated
user holds the required role, raising a 403 Forbidden if not.

Usage:

    from fastapi import Depends
    from app.dependencies.permissions import require_admin

    @router.delete("/issues/{issue_id}", dependencies=[Depends(require_admin())])
    async def delete_issue(issue_id: str) -> None:
        ...

    # Or capture the resolved user in the route:
    @router.get("/admin/dashboard")
    async def dashboard(user=Depends(require_admin())) -> dict:
        ...

This module intentionally contains NO business logic or database queries —
only authorization composition for use with `Depends()`.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import AuthenticatedUser, get_current_active_user
from app.middleware.admin import UserRole

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Super admin configuration
# --------------------------------------------------------------------------- #

SUPER_ADMIN_ROLE: str = "super_admin"
"""Role value identifying a super admin.

Super admin is treated as a privilege level above the standard `UserRole`
set (Admin, Authority, Citizen), rather than a fourth peer role — it is
granted either via a dedicated `role` value of "super_admin" or via an
optional `is_super_admin` boolean flag on the user record, whichever the
upstream user model exposes.
"""


PermissionDependency = Callable[[AuthenticatedUser], Awaitable[AuthenticatedUser]]


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


def _ensure_role(user: AuthenticatedUser, required_role: UserRole) -> None:
    """Verify that a user holds the required role, raising 403 otherwise.

    Args:
        user: The authenticated, active user to check.
        required_role: The role required to proceed.

    Raises:
        HTTPException: 403 if the user's role does not match `required_role`.
    """
    if _normalize_role(user.role) != _normalize_role(required_role):
        logger.warning(
            "Permission denied for user_id=%s: role='%s' does not match "
            "required role='%s'.",
            user.id,
            user.role,
            required_role.value,
        )
        raise _forbidden(f"This action requires the '{required_role.value}' role.")


def _is_super_admin(user: AuthenticatedUser) -> bool:
    """Determine whether a user holds super admin privileges.

    Checks an optional `is_super_admin` boolean attribute first (if the
    user model exposes one), falling back to comparing `role` against
    `SUPER_ADMIN_ROLE`.

    Args:
        user: The authenticated, active user to check.

    Returns:
        True if the user has super admin privileges, False otherwise.
    """
    if getattr(user, "is_super_admin", False):
        return True
    return _normalize_role(user.role) == SUPER_ADMIN_ROLE


# --------------------------------------------------------------------------- #
# Permission dependency factories
# --------------------------------------------------------------------------- #

def require_admin() -> PermissionDependency:
    """Build a dependency that restricts access to users with the Admin role.

    Returns:
        A FastAPI dependency callable, for use with `Depends()`.

    Raises (when used as a dependency):
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not an Admin.
    """

    async def dependency(
        current_user: AuthenticatedUser = Depends(get_current_active_user),
    ) -> AuthenticatedUser:
        _ensure_role(current_user, UserRole.ADMIN)
        logger.debug("Admin permission granted for user_id=%s.", current_user.id)
        return current_user

    return dependency


def require_authority() -> PermissionDependency:
    """Build a dependency that restricts access to users with the Authority role.

    Returns:
        A FastAPI dependency callable, for use with `Depends()`.

    Raises (when used as a dependency):
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not an
            Authority.
    """

    async def dependency(
        current_user: AuthenticatedUser = Depends(get_current_active_user),
    ) -> AuthenticatedUser:
        _ensure_role(current_user, UserRole.AUTHORITY)
        logger.debug("Authority permission granted for user_id=%s.", current_user.id)
        return current_user

    return dependency


def require_citizen() -> PermissionDependency:
    """Build a dependency that restricts access to users with the Citizen role.

    Returns:
        A FastAPI dependency callable, for use with `Depends()`.

    Raises (when used as a dependency):
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user is not a
            Citizen.
    """

    async def dependency(
        current_user: AuthenticatedUser = Depends(get_current_active_user),
    ) -> AuthenticatedUser:
        _ensure_role(current_user, UserRole.CITIZEN)
        logger.debug("Citizen permission granted for user_id=%s.", current_user.id)
        return current_user

    return dependency


def require_super_admin() -> PermissionDependency:
    """Build a dependency that restricts access to super admin users only.

    Super admin is the highest privilege level in the system, intended for
    operations above standard Admin scope (e.g. managing other admins,
    system-wide configuration).

    Returns:
        A FastAPI dependency callable, for use with `Depends()`.

    Raises (when used as a dependency):
        HTTPException: 401 if the JWT is missing/invalid/expired (propagated
            from `get_current_active_user`); 403 if the user does not have
            super admin privileges.
    """

    async def dependency(
        current_user: AuthenticatedUser = Depends(get_current_active_user),
    ) -> AuthenticatedUser:
        if not _is_super_admin(current_user):
            logger.warning(
                "Super admin permission denied for user_id=%s (role='%s').",
                current_user.id,
                current_user.role,
            )
            raise _forbidden("This action requires super admin privileges.")

        logger.debug("Super admin permission granted for user_id=%s.", current_user.id)
        return current_user

    return dependency