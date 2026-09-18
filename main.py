"""
app/main.py

Application entrypoint for CivicLens AI Backend.

Wires together everything assumed to already exist and be production-ready:
    - app.core.config           -> Settings (env-driven configuration)
    - app.core.database         -> Async SQLAlchemy engine/session, init/dispose helpers
    - app.core.logging_config   -> Centralized logging setup
    - app.dependencies          -> limiter, rate-limit decorators, analytics, admin, auth
    - app.api.routers.*         -> auth, users, issues, ai_detection, admin, etc.
    - app.exceptions            -> Custom domain exception classes
    - app.exception_handlers    -> Handlers mapping domain exceptions to HTTP responses

Responsibilities of this module:
    1. Configure logging before anything else initializes.
    2. Manage application lifespan (DB engine startup/shutdown).
    3. Register SlowAPI limiter, state, and middleware.
    4. Register CORS and any other cross-cutting middleware.
    5. Register global and domain-specific exception handlers.
    6. Include all API routers under a versioned prefix.
    7. Expose health/readiness endpoints.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import dispose_engine, init_engine
from app.core.logging_config import setup_logging
from app.dependencies.rate_limit import limiter
from app.exception_handlers import register_exception_handlers
from app.api.routers import (
    admin_router,
    ai_detection_router,
    auth_router,
    issues_router,
    users_router,
)

# --------------------------------------------------------------------------- #
# Logging (must run before other modules emit logs)
# --------------------------------------------------------------------------- #

setup_logging()
logger = logging.getLogger("civiclens.main")


# --------------------------------------------------------------------------- #
# Application lifespan
# --------------------------------------------------------------------------- #

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage startup and shutdown of shared resources (DB engine, etc.).
    """
    logger.info("Starting CivicLens AI Backend (env=%s)", settings.ENVIRONMENT)
    await init_engine()
    logger.info("Database engine initialized.")

    yield

    logger.info("Shutting down CivicLens AI Backend...")
    await dispose_engine()
    logger.info("Database engine disposed. Shutdown complete.")


# --------------------------------------------------------------------------- #
# FastAPI app instance
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="CivicLens AI Backend",
    description="Backend API powering CivicLens AI — civic issue detection and reporting.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)


# --------------------------------------------------------------------------- #
# Rate limiting (SlowAPI)
# --------------------------------------------------------------------------- #

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# --------------------------------------------------------------------------- #
# CORS
# --------------------------------------------------------------------------- #

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Global / domain exception handlers
# --------------------------------------------------------------------------- #

register_exception_handlers(app)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Last-resort safety net so unexpected errors never leak stack traces to
    clients while still being fully logged for debugging.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# --------------------------------------------------------------------------- #
# Routers
# --------------------------------------------------------------------------- #

API_PREFIX = settings.API_V1_PREFIX  # e.g. "/api/v1"

app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(issues_router, prefix=f"{API_PREFIX}/issues", tags=["Issue Reporting"])
app.include_router(ai_detection_router, prefix=f"{API_PREFIX}/ai-detection", tags=["AI Detection"])
app.include_router(admin_router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])


# --------------------------------------------------------------------------- #
# Health & readiness endpoints
# --------------------------------------------------------------------------- #

@app.get("/health", tags=["System"], summary="Liveness check")
async def health_check() -> dict[str, str]:
    """Basic liveness probe — confirms the process is running."""
    return {"status": "ok"}


@app.get("/", tags=["System"], summary="Service banner")
async def root() -> dict[str, str]:
    """Root endpoint with basic service metadata."""
    return {
        "service": "CivicLens AI Backend",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }