"""
app/dependencies/pagination.py

Reusable pagination dependency for FastAPI routes.

Provides `PaginationParams`, a small value object exposing `page`, `limit`,
and a derived `offset`, built via FastAPI's `Query()` so validation
(minimums, maximum page size) and OpenAPI documentation are handled
automatically at the framework level.

Usage:

    from fastapi import Depends
    from app.dependencies.pagination import PaginationParams, get_pagination_params

    @router.get("/issues")
    async def list_issues(
        pagination: PaginationParams = Depends(get_pagination_params),
    ):
        issues = await repository.list_issues(
            limit=pagination.limit, offset=pagination.offset
        )
        ...

This module intentionally contains NO business logic or database queries —
only parameter parsing, validation, and offset computation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from fastapi import Query

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DEFAULT_PAGE: Final[int] = 1
DEFAULT_LIMIT: Final[int] = 20
MIN_PAGE: Final[int] = 1
MIN_LIMIT: Final[int] = 1
MAX_PAGE_SIZE: Final[int] = 100


# --------------------------------------------------------------------------- #
# Data structure
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class PaginationParams:
    """Validated pagination parameters for a paged list endpoint.

    Attributes:
        page: The 1-indexed page number being requested.
        limit: The maximum number of items to return per page.
        offset: The computed number of items to skip, derived from
            `page` and `limit` — i.e. `(page - 1) * limit`.
    """

    page: int
    limit: int
    offset: int

    def to_dict(self) -> dict[str, int]:
        """Serialize the pagination parameters to a plain dict.

        Useful for including pagination metadata in API responses.

        Returns:
            A dict with `page`, `limit`, and `offset` keys.
        """
        return {"page": self.page, "limit": self.limit, "offset": self.offset}


# --------------------------------------------------------------------------- #
# Dependency
# --------------------------------------------------------------------------- #

def get_pagination_params(
    page: int = Query(
        default=DEFAULT_PAGE,
        ge=MIN_PAGE,
        description="The 1-indexed page number to retrieve.",
    ),
    limit: int = Query(
        default=DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_PAGE_SIZE,
        description=f"Maximum number of items per page (1-{MAX_PAGE_SIZE}).",
    ),
) -> PaginationParams:
    """Resolve and validate pagination parameters from query strings.

    `page` and `limit` are validated directly by FastAPI's `Query()`
    constraints (minimum values, maximum page size); FastAPI returns a
    422 Unprocessable Entity automatically if either constraint is
    violated, before this function body ever runs.

    Args:
        page: The 1-indexed page number, from the `page` query parameter.
        limit: The number of items per page, from the `limit` query
            parameter. Capped at `MAX_PAGE_SIZE`.

    Returns:
        A `PaginationParams` instance with `page`, `limit`, and the
        computed `offset`.
    """
    offset = (page - 1) * limit
    return PaginationParams(page=page, limit=limit, offset=offset)