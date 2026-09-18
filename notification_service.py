"""
app/services/notification_service.py

Notification service responsible for creating notifications, delivering them
to users, tracking read/unread state, and reporting unread counts.

Persistence and real-time delivery are abstracted behind small Protocols
(`NotificationRepository` and `NotificationBroadcaster`) so this service stays
decoupled from any specific database or transport. A ready-to-use in-memory
repository is provided as a default/dev implementation; swap in a real
database-backed repository without touching this service's logic. Similarly,
a no-op broadcaster is provided by default, ready to be replaced by a
WebSocket-based broadcaster later without changing the public API.

This module intentionally contains NO API route logic.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class NotificationServiceError(Exception):
    """Base exception for all notification service related errors."""


class NotificationNotFoundError(NotificationServiceError):
    """Raised when a requested notification does not exist."""


class NotificationDeliveryError(NotificationServiceError):
    """Raised when a notification fails to be delivered/broadcast."""


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #

class NotificationType(str, Enum):
    """Category of a notification, useful for client-side rendering/routing."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ISSUE_UPDATE = "issue_update"
    SYSTEM = "system"


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Notification:
    """A single notification addressed to a specific user."""

    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    metadata: dict[str, Any] = field(default_factory=dict)
    is_read: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    read_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the notification to a plain, JSON-friendly dict."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "metadata": self.metadata,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }


# --------------------------------------------------------------------------- #
# Repository & broadcaster abstractions
# --------------------------------------------------------------------------- #

class NotificationRepository(Protocol):
    """
    Storage abstraction for notifications.

    Implement this against your real database (SQL, Mongo, Redis, etc.) and
    inject it into NotificationService. This keeps persistence concerns fully
    decoupled from notification business logic.
    """

    async def save(self, notification: Notification) -> Notification:
        """Persist a new notification and return the stored representation."""
        ...

    async def get_by_id(self, notification_id: str) -> Notification | None:
        """Fetch a single notification by its ID, or None if not found."""
        ...

    async def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """List notifications belonging to a user, most recent first."""
        ...

    async def update(self, notification: Notification) -> Notification:
        """Persist changes to an existing notification."""
        ...

    async def count_unread(self, user_id: str) -> int:
        """Count unread notifications for a given user."""
        ...


class NotificationBroadcaster(Protocol):
    """
    Real-time delivery abstraction for notifications.

    Implement this with a WebSocket connection manager (or pub/sub layer such
    as Redis) and inject it into NotificationService to push notifications to
    connected clients in real time. A no-op default is provided so the
    service works standalone before real-time transport is wired up.
    """

    async def broadcast_to_user(
        self, user_id: str, notification: Notification
    ) -> None:
        """Push a single notification to a specific user's active connections."""
        ...

    async def broadcast_unread_count(self, user_id: str, unread_count: int) -> None:
        """Push an updated unread count to a specific user's active connections."""
        ...


# --------------------------------------------------------------------------- #
# Default implementations (in-memory / no-op)
# --------------------------------------------------------------------------- #

class InMemoryNotificationRepository:
    """
    Simple in-memory implementation of NotificationRepository.

    Suitable for local development, testing, or as a placeholder until a
    real database-backed repository is implemented. NOT suitable for
    multi-process production deployments (state is process-local).
    """

    def __init__(self) -> None:
        self._store: dict[str, Notification] = {}
        self._lock = asyncio.Lock()

    async def save(self, notification: Notification) -> Notification:
        async with self._lock:
            self._store[notification.id] = notification
        return notification

    async def get_by_id(self, notification_id: str) -> Notification | None:
        return self._store.get(notification_id)

    async def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        items = [n for n in self._store.values() if n.user_id == user_id]
        if unread_only:
            items = [n for n in items if not n.is_read]
        items.sort(key=lambda n: n.created_at, reverse=True)
        return items[offset : offset + limit]

    async def update(self, notification: Notification) -> Notification:
        async with self._lock:
            if notification.id not in self._store:
                raise NotificationNotFoundError(
                    f"Notification '{notification.id}' does not exist."
                )
            self._store[notification.id] = notification
        return notification

    async def count_unread(self, user_id: str) -> int:
        return sum(
            1
            for n in self._store.values()
            if n.user_id == user_id and not n.is_read
        )


class NoOpNotificationBroadcaster:
    """
    No-op broadcaster used as a safe default when no real-time transport
    (e.g. WebSockets) has been wired up yet. Logs at debug level so the
    absence of real-time delivery is visible during development.
    """

    async def broadcast_to_user(
        self, user_id: str, notification: Notification
    ) -> None:
        logger.debug(
            "NoOpNotificationBroadcaster: would broadcast notification "
            "%s to user %s.",
            notification.id,
            user_id,
        )

    async def broadcast_unread_count(self, user_id: str, unread_count: int) -> None:
        logger.debug(
            "NoOpNotificationBroadcaster: would push unread_count=%d to user %s.",
            unread_count,
            user_id,
        )


# --------------------------------------------------------------------------- #
# Notification Service
# --------------------------------------------------------------------------- #

class NotificationService:
    """
    Core notification service: creates notifications, sends/delivers them to
    users, tracks read state, and reports unread counts.

    Storage and real-time delivery are injected as dependencies, so this
    class contains no direct database or WebSocket code — only orchestration
    and business rules. This makes it straightforward to plug in a real
    database repository and a WebSocket-based broadcaster later without
    changing any of the methods below.

    Usage:
        service = NotificationService()  # in-memory + no-op defaults
        notification = await service.create_notification(
            user_id="user-123",
            title="Issue resolved",
            message="Your reported pothole has been fixed.",
            notification_type=NotificationType.ISSUE_UPDATE,
        )
        await service.send_notification(notification)
    """

    def __init__(
        self,
        repository: NotificationRepository | None = None,
        broadcaster: NotificationBroadcaster | None = None,
    ) -> None:
        """
        Initialize the NotificationService.

        Args:
            repository: Storage backend for notifications. Defaults to an
                        in-memory repository if not provided.
            broadcaster: Real-time delivery backend (e.g. WebSocket manager).
                         Defaults to a no-op broadcaster if not provided,
                         allowing seamless future WebSocket integration.
        """
        self._repository: NotificationRepository = repository or InMemoryNotificationRepository()
        self._broadcaster: NotificationBroadcaster = broadcaster or NoOpNotificationBroadcaster()

    # ------------------------------------------------------------------- #
    # Creation
    # ------------------------------------------------------------------- #

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """
        Create and persist a new notification for a user.

        Args:
            user_id: ID of the user this notification is addressed to.
            title: Short notification title/headline.
            message: Full notification body text.
            notification_type: Category of the notification.
            metadata: Optional structured payload (e.g. related entity IDs).

        Returns:
            The newly created, persisted Notification.

        Raises:
            NotificationServiceError: If validation fails or persistence fails.
        """
        if not user_id:
            raise NotificationServiceError("user_id is required to create a notification.")
        if not title or not message:
            raise NotificationServiceError("Both title and message are required.")

        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            metadata=metadata or {},
        )

        try:
            saved = await self._repository.save(notification)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to persist notification for user=%s.", user_id)
            raise NotificationServiceError(f"Failed to create notification: {exc}") from exc

        logger.info(
            "Created notification %s for user=%s (type=%s).",
            saved.id,
            user_id,
            notification_type.value,
        )
        return saved

    # ------------------------------------------------------------------- #
    # Sending / delivery
    # ------------------------------------------------------------------- #

    async def send_notification(self, notification: Notification) -> None:
        """
        Deliver a notification to its target user in real time, if a
        real-time transport (e.g. WebSocket broadcaster) is configured.

        This is safe to call even without a WebSocket integration in place —
        the default no-op broadcaster simply logs the attempt, so callers can
        adopt real-time delivery later with zero changes to their call sites.

        Args:
            notification: The notification to deliver.

        Raises:
            NotificationDeliveryError: If the broadcaster raises an error
                                        while attempting delivery.
        """
        try:
            await self._broadcaster.broadcast_to_user(notification.user_id, notification)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Failed to broadcast notification %s to user=%s.",
                notification.id,
                notification.user_id,
            )
            raise NotificationDeliveryError(
                f"Failed to deliver notification '{notification.id}': {exc}"
            ) from exc

        logger.info(
            "Delivered notification %s to user=%s.",
            notification.id,
            notification.user_id,
        )

    async def create_and_send(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """
        Convenience method: create a notification and immediately attempt
        real-time delivery, then push the updated unread count.

        Args:
            user_id: ID of the user this notification is addressed to.
            title: Short notification title/headline.
            message: Full notification body text.
            notification_type: Category of the notification.
            metadata: Optional structured payload.

        Returns:
            The newly created, persisted Notification.

        Raises:
            NotificationServiceError: If creation fails.
            NotificationDeliveryError: If real-time delivery fails.
        """
        notification = await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            metadata=metadata,
        )
        await self.send_notification(notification)

        unread_count = await self.get_unread_count(user_id)
        try:
            await self._broadcaster.broadcast_unread_count(user_id, unread_count)
        except Exception as exc:  # noqa: BLE001
            # Unread count push is best-effort; don't fail the whole operation.
            logger.warning(
                "Failed to broadcast unread count to user=%s: %s", user_id, exc
            )

        return notification

    # ------------------------------------------------------------------- #
    # Read state
    # ------------------------------------------------------------------- #

    async def mark_as_read(self, notification_id: str) -> Notification:
        """
        Mark a single notification as read.

        Args:
            notification_id: ID of the notification to mark as read.

        Returns:
            The updated Notification.

        Raises:
            NotificationNotFoundError: If no notification with that ID exists.
        """
        notification = await self._repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFoundError(
                f"Notification '{notification_id}' not found."
            )

        if notification.is_read:
            logger.debug("Notification %s already marked as read.", notification_id)
            return notification

        updated = replace(
            notification,
            is_read=True,
            read_at=datetime.now(timezone.utc),
        )
        saved = await self._repository.update(updated)

        logger.info("Marked notification %s as read.", notification_id)

        unread_count = await self.get_unread_count(saved.user_id)
        try:
            await self._broadcaster.broadcast_unread_count(saved.user_id, unread_count)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to broadcast updated unread count to user=%s: %s",
                saved.user_id,
                exc,
            )

        return saved

    async def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all unread notifications for a user as read.

        Args:
            user_id: ID of the user whose notifications should be marked read.

        Returns:
            The number of notifications that were updated.
        """
        unread = await self._repository.list_for_user(user_id, unread_only=True, limit=10_000)

        updated_count = 0
        for notification in unread:
            updated = replace(
                notification,
                is_read=True,
                read_at=datetime.now(timezone.utc),
            )
            await self._repository.update(updated)
            updated_count += 1

        logger.info("Marked %d notification(s) as read for user=%s.", updated_count, user_id)

        if updated_count:
            try:
                await self._broadcaster.broadcast_unread_count(user_id, 0)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to broadcast updated unread count to user=%s: %s",
                    user_id,
                    exc,
                )

        return updated_count

    # ------------------------------------------------------------------- #
    # Retrieval
    # ------------------------------------------------------------------- #

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """
        Retrieve notifications for a user, most recent first.

        Args:
            user_id: ID of the user whose notifications to fetch.
            unread_only: If True, only unread notifications are returned.
            limit: Maximum number of notifications to return.
            offset: Number of notifications to skip (for pagination).

        Returns:
            A list of Notification objects.
        """
        return await self._repository.list_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
        )

    async def get_unread_count(self, user_id: str) -> int:
        """
        Get the number of unread notifications for a user.

        Args:
            user_id: ID of the user to check.

        Returns:
            The count of unread notifications.
        """
        return await self._repository.count_unread(user_id)