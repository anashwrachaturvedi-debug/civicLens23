"""
app/dependencies/database.py

Reusable async database session dependencies built on SQLAlchemy 2.0's
`AsyncSession`.

Responsible for:
    - Creating the async engine and session factory from environment
      configuration
    - Providing `get_db()`, a FastAPI dependency that yields a session per
      request
    - Automatically committing on success, rolling back on error, and
      always closing the session afterward

Usage in a route:

    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.dependencies.database import get_db

    @router.get("/issues")
    async def list_issues(db: AsyncSession = Depends(get_db)):
        ...

This module intentionally contains NO business logic or query definitions —
only session lifecycle management.
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from typing import Final

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DATABASE_URL: Final[str | None] = os.getenv("DATABASE_URL")
DB_ECHO: Final[bool] = os.getenv("DB_ECHO", "false").lower() == "true"
DB_POOL_SIZE: Final[int] = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: Final[int] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT: Final[int] = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE: Final[int] = int(os.getenv("DB_POOL_RECYCLE", "1800"))

if not DATABASE_URL:
    logger.warning(
        "DATABASE_URL environment variable is not set. Database access will "
        "fail until it is configured (expected an async driver URL, e.g. "
        "'postgresql+asyncpg://user:pass@host:5432/dbname')."
    )


# --------------------------------------------------------------------------- #
# Engine & session factory
# --------------------------------------------------------------------------- #

def _create_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine from environment configuration.

    Returns:
        A configured `AsyncEngine` instance.
    """
    if not DATABASE_URL:
        # Defer the hard failure until first actual use rather than at
        # import time, so the app can still start (e.g. for docs/health
        # checks) in environments where the DB isn't configured yet.
        logger.error("Cannot create database engine: DATABASE_URL is not set.")

    engine = create_async_engine(
        DATABASE_URL or "sqlite+aiosqlite:///./_unconfigured.db",
        echo=DB_ECHO,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
    logger.info("Async database engine created (echo=%s).", DB_ECHO)
    return engine


engine: Final[AsyncEngine] = _create_engine()
"""Module-level async engine, shared across the application's lifetime."""

async_session_factory: Final[async_sessionmaker[AsyncSession]] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
"""Factory for creating new `AsyncSession` instances bound to `engine`."""


# --------------------------------------------------------------------------- #
# Dependency
# --------------------------------------------------------------------------- #

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session.

    Commits the transaction automatically if the request completes without
    error, rolls back on any exception, and always closes the session
    afterward — regardless of outcome.

    Yields:
        An `AsyncSession` bound to the shared engine, scoped to the
        lifetime of a single request.

    Raises:
        Exception: Re-raises any exception encountered by the route/service
            layer, after rolling back the transaction, so upstream error
            handlers (see `app.middleware.exception_handler`) can still
            process it.
    """
    session: AsyncSession = async_session_factory()
    try:
        yield session
        await session.commit()
        logger.debug("Database session committed successfully.")
    except Exception:
        await session.rollback()
        logger.exception("Database session rolled back due to an error.")
        raise
    finally:
        await session.close()
        logger.debug("Database session closed.")


# --------------------------------------------------------------------------- #
# Lifecycle helpers
# --------------------------------------------------------------------------- #

async def dispose_engine() -> None:
    """Dispose of the engine's connection pool.

    Call this during application shutdown (e.g. in a FastAPI lifespan
    handler) to cleanly release all pooled database connections.
    """
    await engine.dispose()
    logger.info("Database engine connection pool disposed.")