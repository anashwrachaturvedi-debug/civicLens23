"""Pydantic v2 schemas for dashboard and analytics endpoints.

These are all response-only schemas: every dashboard endpoint is a
read (GET) operation, so there are no corresponding request schemas
in this module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.activity import ActivityAction
from app.models.issue import IssueCategory, IssuePriority, IssueStatus


class DashboardOverviewResponse(BaseModel):
    """Headline counts shown on the dashboard landing view."""

    total_users: int
    total_issues: int
    resolved_issues: int
    pending_issues: int
    high_priority_issues: int


class RecentIssueResponse(BaseModel):
    """A trimmed-down issue representation for the recent-issues panel."""

    id: UUID
    title: str
    category: IssueCategory
    status: IssueStatus
    priority: IssuePriority
    reporter_name: str
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    """Broader KPIs beyond the headline overview counts, for a reporting window."""

    period_start: datetime | None
    period_end: datetime | None
    total_issues_in_period: int
    average_severity_score: float
    average_confidence_score: float
    issues_per_day_avg: float
    resolution_rate_percent: float


class ActivityFeedItemResponse(BaseModel):
    """A single entry in the recent activity feed."""

    id: UUID
    actor_name: str
    action: ActivityAction
    description: str
    issue_id: UUID | None
    created_at: datetime


class TopLocationResponse(BaseModel):
    """A geographic area ranked by the number of issues reported there."""

    address: str
    latitude: float
    longitude: float
    issue_count: int


class PriorityDistributionResponse(BaseModel):
    """Current issue counts broken down by priority level."""

    high: int
    medium: int
    low: int


class CategoryDistributionResponse(BaseModel):
    """Current issue count and percentage share for a single category."""

    category: IssueCategory
    count: int
    percentage: float = Field(ge=0, le=100)


class ResolutionRateResponse(BaseModel):
    """Resolution percentage and average resolution time for a reporting window."""

    period_start: datetime | None
    period_end: datetime | None
    total_issues: int
    resolved_issues: int
    resolution_rate_percent: float = Field(ge=0, le=100)
    average_resolution_hours: float