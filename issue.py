"""Pydantic v2 schemas for issue endpoints.

Covers issue creation/update, status transitions, assignment,
paginated listing, and the lightweight response shapes used by the
nearby-search and heatmap endpoints.

``IssueCategory``, ``IssueStatus``, and ``IssuePriority`` are the same
enums used by the ORM layer (:mod:`app.models.issue`) and are re-exported
here so route modules only need to import from ``app.schemas.issue``.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.issue import IssueCategory, IssuePriority, IssueStatus
from app.schemas.user import UserSummary

__all__ = [
    "IssueCategory",
    "IssueStatus",
    "IssuePriority",
    "IssueSortField",
    "SortOrder",
    "IssueCreateRequest",
    "IssueUpdateRequest",
    "IssueStatusUpdateRequest",
    "IssueAssignRequest",
    "IssueResponse",
    "PaginatedIssueResponse",
    "NearbyIssueResponse",
    "HeatmapPointResponse",
]


class IssueSortField(StrEnum):
    """Fields that issue listings can be sorted by."""

    CREATED_AT = "created_at"
    SEVERITY_SCORE = "severity_score"
    PRIORITY = "priority"
    STATUS = "status"


class SortOrder(StrEnum):
    """Sort direction for issue listings."""

    ASC = "asc"
    DESC = "desc"


class IssueCreateRequest(BaseModel):
    """Payload required to report a new issue.

    The image referenced by ``image_url`` is expected to have already
    been uploaded (see the ``ai``/upload endpoints); category, severity,
    and priority are deliberately absent here since they are computed
    by the AI and severity-scoring pipeline rather than supplied by the
    citizen.
    """

    title: str = Field(min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    image_url: str = Field(max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = Field(default=None, max_length=255)


class IssueUpdateRequest(BaseModel):
    """Fields an issue's reporter or an authority may edit after creation."""

    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    address: str | None = Field(default=None, max_length=255)


class IssueStatusUpdateRequest(BaseModel):
    """Payload required to transition an issue to a new status."""

    status: IssueStatus
    note: str | None = Field(
        default=None,
        max_length=500,
        description="Optional note explaining the status change.",
    )


class IssueAssignRequest(BaseModel):
    """Payload required to assign an issue to an authority or admin user."""

    assignee_id: UUID
    note: str | None = Field(default=None, max_length=500)


class IssueResponse(BaseModel):
    """Full representation of an issue, returned by create/read/update endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    image_url: str
    category: IssueCategory
    status: IssueStatus
    priority: IssuePriority
    severity_score: float
    confidence_score: float
    latitude: float
    longitude: float
    address: str | None
    upvote_count: int
    reporter: UserSummary
    assignee: UserSummary | None
    created_at: datetime
    updated_at: datetime


class PaginatedIssueResponse(BaseModel):
    """A page of issue results plus pagination metadata."""

    items: list[IssueResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NearbyIssueResponse(BaseModel):
    """A lightweight issue representation annotated with distance from a query point."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    category: IssueCategory
    status: IssueStatus
    priority: IssuePriority
    latitude: float
    longitude: float
    distance_km: float


class HeatmapPointResponse(BaseModel):
    """A single weighted geographic point for heatmap rendering."""

    latitude: float
    longitude: float
    weight: float = Field(description="Relative intensity, typically the severity score.")
    category: IssueCategory