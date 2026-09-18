"""Issue management API routes.

This module exposes HTTP endpoints for creating, retrieving, updating,
deleting, and geospatially querying infrastructure issues. All business
logic, persistence access, severity/priority handling, and geospatial
computation are delegated to :class:`app.services.issue_service.IssueService`.
Route handlers are intentionally thin and contain no business rules.

Note: static sub-paths (``/nearby``, ``/heatmap``) are declared before the
dynamic ``/{issue_id}`` route so that FastAPI's path-matching resolves them
correctly instead of treating them as an issue identifier.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.schemas.issue import (
    HeatmapPointResponse,
    IssueAssignRequest,
    IssueCreateRequest,
    IssueResponse,
    IssueSortField,
    IssueStatus,
    IssueStatusUpdateRequest,
    IssueUpdateRequest,
    NearbyIssueResponse,
    PaginatedIssueResponse,
    SortOrder,
)
from app.services.issue_service import IssueService
from app.utils.responses import SuccessResponse

router = APIRouter(prefix="/issues", tags=["Issues"])

IssueServiceDep = Annotated[IssueService, Depends(IssueService)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AuthorityUserDep = Annotated[
    User, Depends(require_roles("admin", "authority"))
]


@router.post(
    "/",
    response_model=SuccessResponse[IssueResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Report a new infrastructure issue",
    description=(
        "Creates a new issue report submitted by an authenticated citizen, "
        "including its category, location, and associated image reference. "
        "Severity and priority are computed asynchronously by the AI and "
        "scoring pipeline and are not required in the request payload."
    ),
    response_description="The newly created issue record.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request payload failed validation."
        },
    },
)
async def create_issue(
    payload: IssueCreateRequest,
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[IssueResponse]:
    """Create a new issue report on behalf of the authenticated user."""
    issue = await issue_service.create_issue(
        reporter_id=current_user.id, payload=payload
    )
    return SuccessResponse(
        message="Issue reported successfully.",
        data=issue,
    )


@router.get(
    "/nearby",
    response_model=SuccessResponse[list[NearbyIssueResponse]],
    status_code=status.HTTP_200_OK,
    summary="Find issues near a geographic location",
    description=(
        "Returns issues located within a given radius of the provided "
        "latitude and longitude, ordered by distance from the query point."
    ),
    response_description="Issues near the given coordinates, ordered by distance.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Latitude, longitude, or radius failed validation."
        },
    },
)
async def get_nearby_issues(
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
    latitude: Annotated[
        float, Query(ge=-90, le=90, description="Query point latitude.")
    ],
    longitude: Annotated[
        float, Query(ge=-180, le=180, description="Query point longitude.")
    ],
    radius_km: Annotated[
        float,
        Query(gt=0, le=50, description="Search radius in kilometers."),
    ] = 2.0,
    limit: Annotated[
        int, Query(ge=1, le=200, description="Maximum number of results.")
    ] = 50,
) -> SuccessResponse[list[NearbyIssueResponse]]:
    """Return issues within a given radius of a geographic coordinate."""
    issues = await issue_service.get_nearby_issues(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
    )
    return SuccessResponse(
        message="Nearby issues retrieved successfully.",
        data=issues,
    )


@router.get(
    "/heatmap",
    response_model=SuccessResponse[list[HeatmapPointResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get issue coordinates for heatmap visualization",
    description=(
        "Returns lightweight coordinate and weight data for every issue "
        "matching the optional filters, intended for rendering a density "
        "heatmap on the dashboard map."
    ),
    response_description="A list of weighted geographic points for heatmap rendering.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
    },
)
async def get_heatmap_points(
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
    status_filter: Annotated[
        IssueStatus | None,
        Query(alias="status", description="Filter points by issue status."),
    ] = None,
    category: Annotated[
        str | None, Query(description="Filter points by issue category.")
    ] = None,
) -> SuccessResponse[list[HeatmapPointResponse]]:
    """Return issue coordinates and severity weights for heatmap rendering."""
    points = await issue_service.get_heatmap_points(
        status=status_filter, category=category
    )
    return SuccessResponse(
        message="Heatmap data retrieved successfully.",
        data=points,
    )


@router.get(
    "/",
    response_model=SuccessResponse[PaginatedIssueResponse],
    status_code=status.HTTP_200_OK,
    summary="List issues with pagination, filtering, sorting, and search",
    description=(
        "Returns a paginated list of issues. Supports filtering by status, "
        "category, and priority, free-text search across issue titles and "
        "descriptions, and sorting by a configurable field and order."
    ),
    response_description="A paginated list of issues matching the given filters.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
    },
)
async def list_issues(
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
    page: Annotated[
        int, Query(ge=1, description="Page number, starting at 1.")
    ] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Number of items per page.")
    ] = 20,
    status_filter: Annotated[
        IssueStatus | None,
        Query(alias="status", description="Filter by issue status."),
    ] = None,
    category: Annotated[
        str | None, Query(description="Filter by issue category.")
    ] = None,
    priority: Annotated[
        str | None, Query(description="Filter by issue priority level.")
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Free-text search across title and description."),
    ] = None,
    sort_by: Annotated[
        IssueSortField,
        Query(description="Field to sort results by."),
    ] = IssueSortField.CREATED_AT,
    sort_order: Annotated[
        SortOrder, Query(description="Sort direction.")
    ] = SortOrder.DESC,
) -> SuccessResponse[PaginatedIssueResponse]:
    """List issues with pagination, filtering, search, and sorting."""
    result = await issue_service.list_issues(
        page=page,
        page_size=page_size,
        status=status_filter,
        category=category,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return SuccessResponse(
        message="Issues retrieved successfully.",
        data=result,
    )


@router.get(
    "/{issue_id}",
    response_model=SuccessResponse[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="Get an issue by ID",
    description="Returns the full details of a single issue by its unique identifier.",
    response_description="The requested issue record.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No issue exists with the given ID."
        },
    },
)
async def get_issue(
    issue_id: UUID,
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[IssueResponse]:
    """Retrieve a single issue by its unique identifier."""
    issue = await issue_service.get_issue_by_id(issue_id=issue_id)
    return SuccessResponse(
        message="Issue retrieved successfully.",
        data=issue,
    )


@router.patch(
    "/{issue_id}",
    response_model=SuccessResponse[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="Update an issue",
    description=(
        "Partially updates an existing issue's editable fields, such as "
        "its description or category. Authorization to edit is enforced "
        "by the service layer based on ownership and role."
    ),
    response_description="The updated issue record.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User is not permitted to update this issue."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No issue exists with the given ID."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request payload failed validation."
        },
    },
)
async def update_issue(
    issue_id: UUID,
    payload: IssueUpdateRequest,
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[IssueResponse]:
    """Partially update an existing issue's editable fields."""
    issue = await issue_service.update_issue(
        issue_id=issue_id, requester=current_user, payload=payload
    )
    return SuccessResponse(
        message="Issue updated successfully.",
        data=issue,
    )


@router.delete(
    "/{issue_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete an issue",
    description=(
        "Permanently deletes an issue record. Authorization is enforced "
        "by the service layer based on ownership and role."
    ),
    response_description="Confirmation that the issue was deleted.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User is not permitted to delete this issue."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No issue exists with the given ID."
        },
    },
)
async def delete_issue(
    issue_id: UUID,
    current_user: CurrentUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[None]:
    """Permanently delete an issue by its unique identifier."""
    await issue_service.delete_issue(issue_id=issue_id, requester=current_user)
    return SuccessResponse(
        message="Issue deleted successfully.",
        data=None,
    )


@router.patch(
    "/{issue_id}/status",
    response_model=SuccessResponse[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="Update an issue's status",
    description=(
        "Transitions an issue to a new status (for example, from "
        "'reported' to 'in_progress' or 'resolved'). Restricted to "
        "authenticated authority or admin users."
    ),
    response_description="The issue record with its updated status.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to change issue status."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No issue exists with the given ID."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Requested status transition is invalid."
        },
    },
)
async def update_issue_status(
    issue_id: UUID,
    payload: IssueStatusUpdateRequest,
    current_user: AuthorityUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[IssueResponse]:
    """Update the status of an issue, restricted to authority and admin roles."""
    issue = await issue_service.update_status(
        issue_id=issue_id, updated_by=current_user, payload=payload
    )
    return SuccessResponse(
        message="Issue status updated successfully.",
        data=issue,
    )


@router.post(
    "/{issue_id}/assign",
    response_model=SuccessResponse[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign an issue to an authority or admin",
    description=(
        "Assigns responsibility for resolving an issue to a specific "
        "authority or admin user. Restricted to authenticated authority "
        "or admin users."
    ),
    response_description="The issue record with its updated assignee.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing, invalid, or expired access token."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "User does not have permission to assign issues."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No issue or assignee exists with the given ID."
        },
        status.HTTP_409_CONFLICT: {
            "description": "Issue is already assigned or cannot be reassigned."
        },
    },
)
async def assign_issue(
    issue_id: UUID,
    payload: IssueAssignRequest,
    current_user: AuthorityUserDep,
    issue_service: IssueServiceDep,
) -> SuccessResponse[IssueResponse]:
    """Assign an issue to an authority or admin user for resolution."""
    issue = await issue_service.assign_issue(
        issue_id=issue_id, assigned_by=current_user, payload=payload
    )
    return SuccessResponse(
        message="Issue assigned successfully.",
        data=issue,
    )