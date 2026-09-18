"""
app/dependencies/issue_filters.py

Reusable filtering dependency for issue list endpoints.

Provides `IssueFilters`, a small value object built from query parameters
via FastAPI's `Query()`, covering:

    - status
    - priority
    - category
    - severity
    - city
    - assigned_to
    - date range (from_date / to_date)

Usage:

    from fastapi import Depends
    from app.dependencies.issue_filters import IssueFilters, get_issue_filters

    @router.get("/issues")
    async def list_issues(filters: IssueFilters = Depends(get_issue_filters)):
        issues = await repository.list_issues(**filters.to_query_kwargs())
        ...

This module intentionally contains NO business logic or database queries —
only query-parameter parsing, validation, and structuring for use with
`Depends()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from fastapi import HTTPException, Query, status


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #

class IssueStatus(str, Enum):
    """Lifecycle status of a reported issue."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class IssuePriority(str, Enum):
    """Priority level assigned to an issue."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class IssueCategory(str, Enum):
    """Category classifying the type of issue reported."""

    ROAD_DAMAGE = "road_damage"
    SANITATION = "sanitation"
    VANDALISM = "vandalism"
    INFRASTRUCTURE = "infrastructure"
    WATER_SUPPLY = "water_supply"
    ELECTRICITY = "electricity"
    OTHER = "other"


class IssueSeverity(str, Enum):
    """Severity level indicating the impact of an issue."""

    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


# --------------------------------------------------------------------------- #
# Data structure
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class IssueFilters:
    """Validated set of optional filters for querying issues.

    Every field is optional; a `None` value means "no filter applied" for
    that dimension. Attach these to a repository/query layer to build a
    dynamic `WHERE` clause.

    Attributes:
        status: Restrict to issues with this lifecycle status.
        priority: Restrict to issues with this priority level.
        category: Restrict to issues in this category.
        severity: Restrict to issues with this severity level.
        city: Restrict to issues reported in this city (case-insensitive
            match is expected to be applied by the query layer).
        assigned_to: Restrict to issues assigned to this user ID.
        from_date: Restrict to issues reported on or after this date.
        to_date: Restrict to issues reported on or before this date.
    """

    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    category: IssueCategory | None = None
    severity: IssueSeverity | None = None
    city: str | None = None
    assigned_to: str | None = None
    from_date: date | None = None
    to_date: date | None = None

    def to_query_kwargs(self) -> dict[str, Any]:
        """Serialize the filters to a dict, omitting unset (`None`) fields.

        Convenient for passing directly as `**kwargs` into a repository
        method that only expects the filters actually provided.

        Returns:
            A dict containing only the filters that were set.
        """
        return {
            field_name: value
            for field_name, value in (
                ("status", self.status),
                ("priority", self.priority),
                ("category", self.category),
                ("severity", self.severity),
                ("city", self.city),
                ("assigned_to", self.assigned_to),
                ("from_date", self.from_date),
                ("to_date", self.to_date),
            )
            if value is not None
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize all filters (including unset ones) to a plain dict.

        Useful for echoing the applied filter set back in an API response
        for transparency/debugging.

        Returns:
            A dict with every filter field, `None` where not applied.
        """
        return {
            "status": self.status.value if self.status else None,
            "priority": self.priority.value if self.priority else None,
            "category": self.category.value if self.category else None,
            "severity": self.severity.value if self.severity else None,
            "city": self.city,
            "assigned_to": self.assigned_to,
            "from_date": self.from_date.isoformat() if self.from_date else None,
            "to_date": self.to_date.isoformat() if self.to_date else None,
        }


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #

def _bad_request(detail: str) -> HTTPException:
    """Build a standardized 400 Bad Request HTTPException.

    Args:
        detail: Human-readable reason for the rejection.

    Returns:
        A configured HTTPException with status 400.
    """
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _normalize_city(city: str | None) -> str | None:
    """Normalize a city filter value by trimming whitespace.

    Args:
        city: The raw city query parameter value, if provided.

    Returns:
        The trimmed city string, or None if it was empty/not provided.
    """
    if city is None:
        return None
    trimmed = city.strip()
    return trimmed or None


def _normalize_assigned_to(assigned_to: str | None) -> str | None:
    """Normalize an assigned_to filter value by trimming whitespace.

    Args:
        assigned_to: The raw assigned_to query parameter value, if provided.

    Returns:
        The trimmed user ID string, or None if it was empty/not provided.
    """
    if assigned_to is None:
        return None
    trimmed = assigned_to.strip()
    return trimmed or None


# --------------------------------------------------------------------------- #
# Dependency
# --------------------------------------------------------------------------- #

def get_issue_filters(
    status_: IssueStatus | None = Query(
        default=None,
        alias="status",
        description="Filter issues by lifecycle status.",
    ),
    priority: IssuePriority | None = Query(
        default=None,
        description="Filter issues by priority level.",
    ),
    category: IssueCategory | None = Query(
        default=None,
        description="Filter issues by category.",
    ),
    severity: IssueSeverity | None = Query(
        default=None,
        description="Filter issues by severity level.",
    ),
    city: str | None = Query(
        default=None,
        max_length=100,
        description="Filter issues by reported city.",
    ),
    assigned_to: str | None = Query(
        default=None,
        max_length=100,
        description="Filter issues by the ID of the assigned user/authority.",
    ),
    from_date: date | None = Query(
        default=None,
        description="Filter issues reported on or after this date (YYYY-MM-DD).",
    ),
    to_date: date | None = Query(
        default=None,
        description="Filter issues reported on or before this date (YYYY-MM-DD).",
    ),
) -> IssueFilters:
    """Resolve and validate issue filter parameters from query strings.

    Enum-typed filters (`status`, `priority`, `category`, `severity`) are
    validated directly by FastAPI/Pydantic — an invalid value automatically
    produces a 422 Unprocessable Entity before this function body runs.
    Date range consistency (`from_date <= to_date`) is validated here
    explicitly, since it spans two parameters.

    Args:
        status_: The `status` query parameter (bound via alias to avoid
            shadowing the `status` module import).
        priority: The `priority` query parameter.
        category: The `category` query parameter.
        severity: The `severity` query parameter.
        city: The `city` query parameter.
        assigned_to: The `assigned_to` query parameter.
        from_date: The `from_date` query parameter.
        to_date: The `to_date` query parameter.

    Returns:
        An `IssueFilters` instance with all validated, normalized filters.

    Raises:
        HTTPException: 400 if `from_date` is after `to_date`.
    """
    if from_date is not None and to_date is not None and from_date > to_date:
        raise _bad_request("'from_date' must not be after 'to_date'.")

    return IssueFilters(
        status=status_,
        priority=priority,
        category=category,
        severity=severity,
        city=_normalize_city(city),
        assigned_to=_normalize_assigned_to(assigned_to),
        from_date=from_date,
        to_date=to_date,
    )