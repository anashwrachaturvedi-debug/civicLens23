"""Activity log ORM model.

Records a chronological, auditable trail of significant actions taken
on the platform — issue creation, status transitions, assignments,
and account changes — used to power the dashboard's activity feed and
to support after-the-fact auditing.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.user import User


class ActivityAction(StrEnum):
    """Types of actions recorded in the activity feed."""

    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_DELETED = "issue_deleted"
    USER_REGISTERED = "user_registered"
    USER_LOGGED_IN = "user_logged_in"


class ActivityLog(TimestampMixin, Base):
    """A single recorded action performed by a user, optionally on an issue."""

    __tablename__ = "activity_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issue_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("issues.id", ondelete="CASCADE"), nullable=True, index=True
    )
    action: Mapped[ActivityAction] = mapped_column(
        Enum(ActivityAction, name="activity_action"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="activity_logs")
    issue: Mapped[Issue | None] = relationship(
        "Issue", back_populates="activity_logs"
    )

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action!r} user_id={self.user_id}>"