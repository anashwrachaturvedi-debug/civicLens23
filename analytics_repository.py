"""Data-access layer for the DailyAnalyticsSnapshot model.

Contains queries for reading and upserting persisted daily analytics
snapshots, used to serve historical/trend data efficiently without
recomputing aggregates from raw issue rows on every request.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import DailyAnalyticsSnapshot


class AnalyticsRepository:
    """Encapsulates all database access for the DailyAnalyticsSnapshot model."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_date(self, snapshot_date: date) -> DailyAnalyticsSnapshot | None:
        """Fetch the snapshot for a specific date, if one has been computed."""
        result = await self._db.execute(
            select(DailyAnalyticsSnapshot).where(
                DailyAnalyticsSnapshot.snapshot_date == snapshot_date
            )
        )
        return result.scalar_one_or_none()

    async def get_range(
        self, start_date: date, end_date: date
    ) -> list[DailyAnalyticsSnapshot]:
        """Fetch all snapshots within an inclusive date range, oldest first."""
        result = await self._db.execute(
            select(DailyAnalyticsSnapshot)
            .where(DailyAnalyticsSnapshot.snapshot_date.between(start_date, end_date))
            .order_by(DailyAnalyticsSnapshot.snapshot_date.asc())
        )
        return list(result.scalars().all())

    async def upsert(self, snapshot: DailyAnalyticsSnapshot) -> DailyAnalyticsSnapshot:
        """Insert a new snapshot, or update the existing one for the same date."""
        existing = await self.get_by_date(snapshot.snapshot_date)
        if existing is None:
            self._db.add(snapshot)
        else:
            existing.total_issues = snapshot.total_issues
            existing.new_issues = snapshot.new_issues
            existing.resolved_issues = snapshot.resolved_issues
            existing.pending_issues = snapshot.pending_issues
            existing.high_priority_count = snapshot.high_priority_count
            existing.medium_priority_count = snapshot.medium_priority_count
            existing.low_priority_count = snapshot.low_priority_count
            existing.average_resolution_hours = snapshot.average_resolution_hours
            existing.category_breakdown = snapshot.category_breakdown
            snapshot = existing

        await self._db.commit()
        await self._db.refresh(snapshot)
        return snapshot