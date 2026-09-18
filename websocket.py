"""WebSocket connection management.

Provides a single, process-wide :class:`ConnectionManager` used to push
real-time events (new issues, status changes, notifications) to
connected dashboard clients without requiring them to poll the REST API.
"""

import asyncio
from uuid import UUID

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """Tracks active WebSocket connections and broadcasts JSON-serializable events.

    Connections are grouped by user ID so events can be sent either to a
    specific user (e.g. a personal notification) or broadcast to every
    connected client (e.g. a new issue appearing on the dashboard map).
    """

    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """Register a new WebSocket connection for the given user."""
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(user_id, set()).add(websocket)
        logger.debug("WebSocket connected for user_id={}", user_id)

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        """Remove a WebSocket connection, cleaning up empty user entries."""
        async with self._lock:
            connections = self._connections.get(user_id)
            if connections is not None:
                connections.discard(websocket)
                if not connections:
                    self._connections.pop(user_id, None)
        logger.debug("WebSocket disconnected for user_id={}", user_id)

    async def send_to_user(self, user_id: UUID, event: dict) -> None:
        """Send an event to every connection belonging to a specific user."""
        connections = self._connections.get(user_id, set()).copy()
        await self._send_to_many(connections, event)

    async def broadcast(self, event: dict) -> None:
        """Send an event to every currently connected client, across all users."""
        all_connections: set[WebSocket] = set()
        for connections in self._connections.values():
            all_connections.update(connections)
        await self._send_to_many(all_connections, event)

    async def _send_to_many(
        self, connections: set[WebSocket], event: dict
    ) -> None:
        """Send an event to a set of connections, dropping any that fail."""
        if not connections:
            return
        results = await asyncio.gather(
            *(connection.send_json(event) for connection in connections),
            return_exceptions=True,
        )
        for connection, result in zip(connections, results, strict=True):
            if isinstance(result, Exception):
                logger.warning(
                    "Failed to send WebSocket event, dropping connection: {}",
                    result,
                )
                for user_id, user_connections in list(self._connections.items()):
                    user_connections.discard(connection)
                    if not user_connections:
                        self._connections.pop(user_id, None)


connection_manager = ConnectionManager()