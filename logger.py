"""Convenience access point for the application logger.

``app.core.logging`` owns *configuring* Loguru's sinks at startup.
This module simply re-exports the already-configured ``logger``
instance so other layers (services, repositories, middleware) can do
``from app.utils.logger import logger`` without depending on
``app.core.logging`` directly.
"""

from loguru  import logger

__all__ = ["logger"]