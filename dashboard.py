"""Dashboard analytics API routes.

This module exposes read-only HTTP endpoints that power the authority
dashboard: high-level KPIs, recent activity, and aggregated breakdowns
of issues by priority, category, and location. All aggregation,
querying, and computation are delegated to
:class:`app.services.dashboard_service.DashboardService`. Route handlers
are intentionally thin and contain no business logic.

All endpoints are restricted to authenticated authority or admin users,
since these views expose city-wide operational data rather than data
scoped to an individual citizen.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import require_roles
from app.dependencies.services import get_dashboard_service
from app.models.user import User
from app.schemas.analytics import (
    ActivityFeedItemResponse,
    CategoryDistributionResponse,
    DashboardOverviewResponse,
    DashboardStatsResponse,
    PriorityDistributionResponse,
    RecentIssueResponse,
    ResolutionRateResponse,
    TopLocationResponse,
)
from app.services.dashboard_service import DashboardService
from app.utils.responses import SuccessResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

DashboardServiceDep = Annotated[
    DashboardService, Depends(get_dashboard_service)
]
AuthorityUserDep = Annotated[
    User, Depends(require_roles("admin", "authority"))
]

DateRangeStart = Annotated[
    date | None,
    Query(description="Inclusive start date for the reporting window."),
]
DateRangeEnd = Annotated[
    date | None,
    Query(description="Inclusive end date for the reporting window."),
]


@router.get(
    "/overview",
    response_model=SuccessResponse[DashboardOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get high-level dashboard overview",
    description=(
        "Returns headline counts for the dashboard landing view, "
        "including total users, total issues, resolved issues, pending "
        "issues, and currently high-priority issues."
    ),
    response_description="Headline counts for the dashboard overview.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_overview(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
) -> SuccessResponse[DashboardOverviewResponse]:
    """Return headline counts for the dashboard overview panel."""
    overview = await dashboard_service.get_overview()
    return SuccessResponse(
        message="Dashboard overview retrieved successfully.",
        data=overview,
    )


@router.get(
    "/recent-issues",
    response_model=SuccessResponse[list[RecentIssueResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get the most recently reported issues",
    description=(
        "Returns the most recently reported issues, ordered from newest "
        "to oldest, for display in the dashboard's recent activity panel."
    ),
    response_description="A list of the most recently reported issues.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_recent_issues(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of issues to return.")
    ] = 10,
) -> SuccessResponse[list[RecentIssueResponse]]:
    """Return the most recently reported issues."""
    issues = await dashboard_service.get_recent_issues(limit=limit)
    return SuccessResponse(
        message="Recent issues retrieved successfully.",
        data=issues,
    )


@router.get(
    "/stats",
    response_model=SuccessResponse[DashboardStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics and KPIs",
    description=(
        "Returns a broader set of key performance indicators for the "
        "reporting window, such as issue volume trends, average severity, "
        "and throughput metrics, beyond the headline overview counts."
    ),
    response_description="Dashboard KPIs for the given reporting window.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_stats(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
    start_date: DateRangeStart = None,
    end_date: DateRangeEnd = None,
) -> SuccessResponse[DashboardStatsResponse]:
    """Return dashboard KPIs for the given optional reporting window."""
    stats = await dashboard_service.get_stats(
        start_date=start_date, end_date=end_date
    )
    return SuccessResponse(
        message="Dashboard statistics retrieved successfully.",
        data=stats,
    )


@router.get(
    "/activity",
    response_model=SuccessResponse[list[ActivityFeedItemResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get recent user and admin activity",
    description=(
        "Returns a chronological feed of recent actions taken on the "
        "platform, such as issue creation, status changes, and "
        "assignments, for the dashboard activity panel."
    ),
    response_description="A list of recent activity feed entries.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_activity_feed(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of activity entries to return.")
    ] = 20,
) -> SuccessResponse[list[ActivityFeedItemResponse]]:
    """Return a chronological feed of recent platform activity."""
    activity = await dashboard_service.get_activity_feed(limit=limit)
    return SuccessResponse(
        message="Activity feed retrieved successfully.",
        data=activity,
    )


@router.get(
    "/top-locations",
    response_model=SuccessResponse[list[TopLocationResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get the areas with the most reported issues",
    description=(
        "Returns the geographic areas or zones with the highest number "
        "of reported issues, ranked in descending order, to help "
        "authorities identify recurring hotspots."
    ),
    response_description="A list of top locations ranked by issue count.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_top_locations(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
    limit: Annotated[
        int, Query(ge=1, le=50, description="Maximum number of locations to return.")
    ] = 10,
) -> SuccessResponse[list[TopLocationResponse]]:
    """Return the areas with the highest number of reported issues."""
    locations = await dashboard_service.get_top_locations(limit=limit)
    return SuccessResponse(
        message="Top locations retrieved successfully.",
        data=locations,
    )


@router.get(
    "/priority-distribution",
    response_model=SuccessResponse[PriorityDistributionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get issue counts by priority level",
    description=(
        "Returns the current count of issues at each priority level "
        "(high, medium, low), for visualizing overall workload urgency."
    ),
    response_description="Issue counts broken down by priority level.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_priority_distribution(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
) -> SuccessResponse[PriorityDistributionResponse]:
    """Return issue counts broken down by priority level."""
    distribution = await dashboard_service.get_priority_distribution()
    return SuccessResponse(
        message="Priority distribution retrieved successfully.",
        data=distribution,
    )


@router.get(
    "/category-distribution",
    response_model=SuccessResponse[list[CategoryDistributionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get issue counts by category",
    description=(
        "Returns the current count and percentage share of issues for "
        "each category (for example, potholes, garbage, waterlogging, "
        "and streetlight damage)."
    ),
    response_description="Issue counts and percentages broken down by category.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_category_distribution(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
) -> SuccessResponse[list[CategoryDistributionResponse]]:
    """Return issue counts and percentage share broken down by category."""
    distribution = await dashboard_service.get_category_distribution()
    return SuccessResponse(
        message="Category distribution retrieved successfully.",
        data=distribution,
    )


@router.get(
    "/resolution-rate",
    response_model=SuccessResponse[ResolutionRateResponse],
    status_code=status.HTTP_200_OK,
    summary="Get issue resolution rate and average resolution time",
    description=(
        "Returns the percentage of reported issues that have been "
        "resolved and the average time taken to resolve them, optionally "
        "scoped to a specific reporting window."
    ),
    response_description="Resolution percentage and average resolution time.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to view dashboard data."
        },
    },
)
async def get_resolution_rate(
    current_user: AuthorityUserDep,
    dashboard_service: DashboardServiceDep,
    start_date: DateRangeStart = None,
    end_date: DateRangeEnd = None,
) -> SuccessResponse[ResolutionRateResponse]:
    """Return the resolution rate and average resolution time for issues."""
    resolution_rate = await dashboard_service.get_resolution_rate(
        start_date=start_date, end_date=end_date
    )
    return SuccessResponse(
        message="Resolution rate retrieved successfully.",
        data=resolution_rate,
    )