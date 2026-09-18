"""Notification ORM model.

Represents an in-app notification delivered to a user — for example,
a status change on an issue they reported, or an assignment alert for
an authority user.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(StrEnum):
    """Categories of notifications the platform can send."""

    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_RESOLVED = "issue_resolved"
    SYSTEM_ALERT = "system_alert"


class Notification(TimestampMixin, Base):
    """A single notification delivered to a specific user."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_issue_id: Mapped[UUID | None] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} type={self.type!r}>"