"""Data-access layer for the Issue model.

Contains every database query related to issues, including paginated
listing with filtering/search/sorting, geospatial bounding-box
pre-filtering for nearby search, and the raw aggregate queries that
back the dashboard and analytics endpoints. Services call these
methods rather than issuing SQLAlchemy queries themselves.
"""

import math
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.issue import Issue, IssueCategory, IssuePriority, IssueStatus
from app.schemas.issue import IssueSortField, SortOrder
from app.utils.constants import EARTH_RADIUS_KM
from app.utils.helpers import haversine_distance_km, paginate_offset

_EAGER_LOAD = (selectinload(Issue.reporter), selectinload(Issue.assignee))


class IssueRepository:
    """Encapsulates all database access for the Issue model."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, issue: Issue) -> Issue:
        """Persist a new issue and return it with relationships loaded."""
        self._db.add(issue)
        await self._db.commit()
        return await self.get_by_id(issue.id)  # type: ignore[return-value]

    async def get_by_id(self, issue_id: UUID) -> Issue | None:
        """Fetch a single issue by ID, with reporter and assignee eagerly loaded."""
        result = await self._db.execute(
            select(Issue).where(Issue.id == issue_id).options(*_EAGER_LOAD)
        )
        return result.scalar_one_or_none()

    async def update(self, issue: Issue) -> Issue:
        """Persist changes made to an already-tracked issue instance."""
        await self._db.commit()
        return await self.get_by_id(issue.id)  # type: ignore[return-value]

    async def delete(self, issue: Issue) -> None:
        """Permanently delete an issue."""
        await self._db.delete(issue)
        await self._db.commit()

    def _apply_filters(
        self,
        stmt: Select,
        *,
        status: IssueStatus | None,
        category: str | None,
        priority: str | None,
        search: str | None,
    ) -> Select:
        """Apply optional status/category/priority/search filters to a query."""
        if status is not None:
            stmt = stmt.where(Issue.status == status)
        if category is not None:
            stmt = stmt.where(Issue.category == category)
        if priority is not None:
            stmt = stmt.where(Issue.priority == priority)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Issue.title.ilike(pattern), Issue.description.ilike(pattern))
            )
        return stmt

    async def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        status: IssueStatus | None,
        category: str | None,
        priority: str | None,
        search: str | None,
        sort_by: IssueSortField,
        sort_order: SortOrder,
    ) -> tuple[list[Issue], int]:
        """Return a page of issues matching the given filters, plus the total count."""
        base_stmt = self._apply_filters(
            select(Issue),
            status=status,
            category=category,
            priority=priority,
            search=search,
        )

        count_result = await self._db.execute(
            select(func.count()).select_from(base_stmt.subquery())
        )
        total = count_result.scalar_one() or 0

        sort_column = getattr(Issue, sort_by.value)
        ordered_column = sort_column.desc() if sort_order == SortOrder.DESC else sort_column.asc()

        stmt = (
            base_stmt.options(*_EAGER_LOAD)
            .order_by(ordered_column)
            .offset(paginate_offset(page, page_size))
            .limit(page_size)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_nearby(
        self, *, latitude: float, longitude: float, radius_km: float, limit: int
    ) -> list[tuple[Issue, float]]:
        """Return issues within a radius of a point, each paired with its distance in km.

        Uses a coarse latitude/longitude bounding-box filter in SQL to
        avoid scanning the entire table, then refines and sorts by exact
        haversine distance in Python for the (small) candidate set.
        """
        lat_delta = radius_km / EARTH_RADIUS_KM * (180 / math.pi)
        lon_delta = lat_delta / max(math.cos(math.radians(latitude)), 0.01)

        stmt = select(Issue).where(
            Issue.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Issue.longitude.between(longitude - lon_delta, longitude + lon_delta),
        )
        result = await self._db.execute(stmt)
        candidates = result.scalars().all()

        scored: list[tuple[Issue, float]] = []
        for issue in candidates:
            distance = haversine_distance_km(
                latitude, longitude, issue.latitude, issue.longitude
            )
            if distance <= radius_km:
                scored.append((issue, distance))

        scored.sort(key=lambda pair: pair[1])
        return scored[:limit]

    async def get_heatmap_points(
        self, *, status: IssueStatus | None, category: str | None
    ) -> list[Issue]:
        """Return issues (lat/lon/severity/category) matching optional filters."""
        stmt = self._apply_filters(
            select(Issue), status=status, category=category, priority=None, search=None
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_total(self) -> int:
        """Return the total number of issues."""
        result = await self._db.execute(select(func.count()).select_from(Issue))
        return result.scalar_one() or 0

    async def count_by_status(self, status: IssueStatus) -> int:
        """Return the number of issues with a given status."""
        result = await self._db.execute(
            select(func.count()).select_from(Issue).where(Issue.status == status)
        )
        return result.scalar_one() or 0

    async def count_by_priority(self, priority: IssuePriority) -> int:
        """Return the number of issues with a given priority."""
        result = await self._db.execute(
            select(func.count()).select_from(Issue).where(Issue.priority == priority)
        )
        return result.scalar_one() or 0

    async def count_by_category(self, category: IssueCategory) -> int:
        """Return the number of issues in a given category."""
        result = await self._db.execute(
            select(func.count()).select_from(Issue).where(Issue.category == category)
        )
        return result.scalar_one() or 0

    async def count_created_between(self, start: datetime, end: datetime) -> int:
        """Return the number of issues created within a datetime range."""
        result = await self._db.execute(
            select(func.count())
            .select_from(Issue)
            .where(Issue.created_at.between(start, end))
        )
        return result.scalar_one() or 0

    async def count_resolved_between(self, start: datetime, end: datetime) -> int:
        """Return the number of issues resolved within a datetime range."""
        result = await self._db.execute(
            select(func.count())
            .select_from(Issue)
            .where(
                Issue.status == IssueStatus.RESOLVED,
                Issue.updated_at.between(start, end),
            )
        )
        return result.scalar_one() or 0

    async def average_resolution_hours(
        self, start: datetime | None, end: datetime | None
    ) -> float:
        """Return the average time (in hours) between creation and resolution."""
        stmt = select(
            func.avg(
                func.extract("epoch", Issue.updated_at - Issue.created_at) / 3600.0
            )
        ).where(Issue.status == IssueStatus.RESOLVED)
        if start is not None:
            stmt = stmt.where(Issue.updated_at >= start)
        if end is not None:
            stmt = stmt.where(Issue.updated_at <= end)
        result = await self._db.execute(stmt)
        return float(result.scalar_one() or 0.0)

    async def average_severity_score(self) -> float:
        """Return the average severity score across all issues."""
        result = await self._db.execute(select(func.avg(Issue.severity_score)))
        return float(result.scalar_one() or 0.0)

    async def average_confidence_score(self) -> float:
        """Return the average AI confidence score across all issues."""
        result = await self._db.execute(select(func.avg(Issue.confidence_score)))
        return float(result.scalar_one() or 0.0)

    async def get_recent(self, limit: int) -> list[Issue]:
        """Return the most recently created issues, newest first."""
        stmt = (
            select(Issue)
            .options(*_EAGER_LOAD)
            .order_by(Issue.created_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_top_locations(self, limit: int) -> list[tuple[str, float, float, int]]:
        """Return the addresses with the most reported issues.

        Returns tuples of (address, avg_latitude, avg_longitude, issue_count),
        ordered by issue_count descending. Issues without an address are
        excluded, since they cannot be meaningfully grouped by location name.
        """
        stmt = (
            select(
                Issue.address,
                func.avg(Issue.latitude),
                func.avg(Issue.longitude),
                func.count().label("issue_count"),
            )
            .where(Issue.address.is_not(None))
            .group_by(Issue.address)
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return [tuple(row) for row in result.all()]

    async def get_category_counts(self) -> dict[IssueCategory, int]:
        """Return the number of issues per category."""
        stmt = select(Issue.category, func.count()).group_by(Issue.category)
        result = await self._db.execute(stmt)
        return {category: count for category, count in result.all()}