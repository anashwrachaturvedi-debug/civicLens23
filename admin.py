"""
app/middleware/admin.py

Role-based access control (RBAC) dependencies for restricting routes to
specific user roles (Admin, Authority, Citizen).

These are implemented as FastAPI dependencies (not raw ASGI middleware) since
that is the idiomatic, testable way to enforce per-route authorization in
FastAPI — they compose cleanly with `Depends()`, integrate with OpenAPI docs,
and have access to already-resolved request state (e.g. the authenticated
user) without needing to re-parse the request.

Assumption: an existing authentication dependency `get_current_user` resolves
the authenticated user from the request (e.g. by validating a JWT bearer
token) and returns an object exposing a `role` attribute. Adjust the import
below to match your actual auth module if the path differs.

This module intentionally contains NO route logic — only reusable
dependencies for use inside route definitions.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Protocol, runtime_checkable

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user  # existing auth dependency

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Roles
# --------------------------------------------------------------------------- #

class UserRole(str, Enum):
    """Supported user roles within the application."""

    ADMIN = "admin"
    AUTHORITY = "authority"
    CITIZEN = "citizen"


# --------------------------------------------------------------------------- #
# Current user contract
# --------------------------------------------------------------------------- #

@runtime_checkable
class CurrentUser(Protocol):
    """
    Minimal shape required of whatever `get_current_user` returns.

    Using a Protocol here decouples this module from any specific User ORM
    model/schema — any object with `id` and `role` attributes satisfies it.
    """

    id: str
    role: UserRole | str


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _normalize_role(role: UserRole | str) -> str:
    """
    Normalize a role value (enum or raw string) to a lowercase string for
    consistent comparison.

    Args:
        role: The role to normalize, either a UserRole enum member or a
              plain string.

    Returns:
        The normalized, lowercase role string.
    """
    value = role.value if isinstance(role, UserRole) else str(role)
    return value.strip().lower()


def _forbidden(detail: str) -> HTTPException:
    """
    Build a standardized 403 Forbidden HTTPException.

    Args:
        detail: Human-readable reason for the rejection.

    Returns:
        A configured HTTPException with status 403.
    """
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# --------------------------------------------------------------------------- #
# Role-checking dependency factory
# --------------------------------------------------------------------------- #

class RoleChecker:
    """
    Reusable FastAPI dependency that restricts access to users holding one
    of a set of allowed roles.

    Usage:
        require_admin = RoleChecker(UserRole.ADMIN)

        @router.delete("/issues/{issue_id}", dependencies=[Depends(require_admin)])
        async def delete_issue(issue_id: str) -> None:
            ...

        # Or capture the resolved user in the route:
        @router.get("/admin/dashboard")
        async def admin_dashboard(user: CurrentUser = Depends(require_admin)) -> dict:
            ...
    """

    def __init__(self, *allowed_roles: UserRole) -> None:
        """
        Configure a role checker for one or more allowed roles.

        Args:
            *allowed_roles: One or more UserRole values permitted to access
                             the protected route. At least one must be given.

        Raises:
            ValueError: If no roles are provided.
        """
        if not allowed_roles:
            raise ValueError("RoleChecker requires at least one allowed role.")

        self._allowed_roles: frozenset[str] = frozenset(
            _normalize_role(role) for role in allowed_roles
        )

    async def __call__(
        self, current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        """
        Validate that the authenticated user holds an allowed role.

        Args:
            current_user: The authenticated user, resolved by the upstream
                           `get_current_user` dependency.

        Returns:
            The authenticated user, unchanged, if authorized.

        Raises:
            HTTPException: 403 Forbidden if the user's role is not permitted.
        """
        user_role = _normalize_role(current_user.role)

        if user_role not in self._allowed_roles:
            logger.warning(
                "Access denied for user_id=%s: role='%s' not in allowed roles=%s.",
                getattr(current_user, "id", "unknown"),
                user_role,
                sorted(self._allowed_roles),
            )
            raise _forbidden(
                "You do not have sufficient permissions to access this resource."
            )

        logger.debug(
            "Access granted for user_id=%s with role='%s'.",
            getattr(current_user, "id", "unknown"),
            user_role,
        )
        return current_user


# --------------------------------------------------------------------------- #
# Ready-to-use dependencies for common cases
# --------------------------------------------------------------------------- #

require_admin: RoleChecker = RoleChecker(UserRole.ADMIN)
"""Restricts a route to users with the ADMIN role only."""

require_authority: RoleChecker = RoleChecker(UserRole.AUTHORITY)
"""Restricts a route to users with the AUTHORITY role only."""

require_citizen: RoleChecker = RoleChecker(UserRole.CITIZEN)
"""Restricts a route to users with the CITIZEN role only."""

require_admin_or_authority: RoleChecker = RoleChecker(UserRole.ADMIN, UserRole.AUTHORITY)
"""Restricts a route to users with either the ADMIN or AUTHORITY role."""


def require_roles(*allowed_roles: UserRole) -> RoleChecker:
    """
    Factory for building an ad-hoc role-restriction dependency inline in a
    route definition, for cases not covered by the predefined checkers above.

    Args:
        *allowed_roles: One or more UserRole values permitted to access the
                         protected route.

    Returns:
        A configured RoleChecker instance usable with `Depends()`.

    Example:
        @router.post(
            "/issues/{issue_id}/escalate",
            dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.AUTHORITY))],
        )
        async def escalate_issue(issue_id: str) -> None:
            ...
    """
    return RoleChecker(*allowed_roles)