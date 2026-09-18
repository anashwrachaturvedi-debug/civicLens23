"""
app/middleware/rate_limit.py

Reusable rate-limiting infrastructure built on SlowAPI, protecting
sensitive/expensive endpoints from abuse:

    - Login
    - Register
    - Forgot Password
    - AI Detection

Rate limits are configured via environment variables so they can be tuned
per-environment (e.g. relaxed in dev, strict in production) without code
changes.

Usage in a route module:

    from fastapi import APIRouter
    from app.middleware.rate_limit import login_rate_limit

    router = APIRouter()

    @router.post("/login")
    @login_rate_limit
    async def login(request: Request, ...):
        ...

Note: SlowAPI's decorator requires the decorated endpoint function to accept
a `request: Request` parameter, per SlowAPI's own requirements.

Call `setup_rate_limiting(app)` once during application startup to wire the
limiter, its exception handler, and its ASGI middleware into the app.

This module intentionally contains NO route logic — only reusable
rate-limiting configuration and dependencies for use inside route
definitions elsewhere.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Final

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DEFAULT_LOGIN_RATE_LIMIT: Final[str] = "5/minute"
DEFAULT_REGISTER_RATE_LIMIT: Final[str] = "3/minute"
DEFAULT_FORGOT_PASSWORD_RATE_LIMIT: Final[str] = "3/minute"
DEFAULT_AI_DETECTION_RATE_LIMIT: Final[str] = "10/minute"
DEFAULT_GLOBAL_RATE_LIMIT: Final[str] = "100/minute"

LOGIN_RATE_LIMIT: Final[str] = os.getenv("RATE_LIMIT_LOGIN", DEFAULT_LOGIN_RATE_LIMIT)
REGISTER_RATE_LIMIT: Final[str] = os.getenv(
    "RATE_LIMIT_REGISTER", DEFAULT_REGISTER_RATE_LIMIT
)
FORGOT_PASSWORD_RATE_LIMIT: Final[str] = os.getenv(
    "RATE_LIMIT_FORGOT_PASSWORD", DEFAULT_FORGOT_PASSWORD_RATE_LIMIT
)
AI_DETECTION_RATE_LIMIT: Final[str] = os.getenv(
    "RATE_LIMIT_AI_DETECTION", DEFAULT_AI_DETECTION_RATE_LIMIT
)
GLOBAL_RATE_LIMIT: Final[str] = os.getenv(
    "RATE_LIMIT_GLOBAL", DEFAULT_GLOBAL_RATE_LIMIT
)

logger.info(
    "Rate limits configured: login=%s, register=%s, forgot_password=%s, "
    "ai_detection=%s, global=%s",
    LOGIN_RATE_LIMIT,
    REGISTER_RATE_LIMIT,
    FORGOT_PASSWORD_RATE_LIMIT,
    AI_DETECTION_RATE_LIMIT,
    GLOBAL_RATE_LIMIT,
)


# --------------------------------------------------------------------------- #
# Key function
# --------------------------------------------------------------------------- #

def rate_limit_key(request: Request) -> str:
    """Derive the rate-limiting key for an incoming request.

    Prefers an authenticated user's ID (if already resolved onto
    `request.state.user` by an upstream auth dependency) so a single user
    can't bypass limits by rotating IPs; otherwise falls back to the
    client's remote address.

    Args:
        request: The incoming request.

    Returns:
        A string key uniquely identifying the caller for rate-limiting
        purposes.
    """
    user = getattr(request.state, "user", None)
    user_id = getattr(user, "id", None)
    if user_id:
        return f"user:{user_id}"
    return get_remote_address(request)


# --------------------------------------------------------------------------- #
# Shared limiter instance
# --------------------------------------------------------------------------- #

limiter: Final[Limiter] = Limiter(
    key_func=rate_limit_key,
    default_limits=[GLOBAL_RATE_LIMIT],
)
"""Shared SlowAPI Limiter instance. Import this in route modules if you need
to apply ad-hoc limits beyond the predefined decorators below."""


# --------------------------------------------------------------------------- #
# Predefined, reusable rate-limit decorators
# --------------------------------------------------------------------------- #

login_rate_limit: Callable[..., Any] = limiter.limit(LOGIN_RATE_LIMIT)
"""Rate limit decorator for the login endpoint."""

register_rate_limit: Callable[..., Any] = limiter.limit(REGISTER_RATE_LIMIT)
"""Rate limit decorator for the registration endpoint."""

forgot_password_rate_limit: Callable[..., Any] = limiter.limit(FORGOT_PASSWORD_RATE_LIMIT)
"""Rate limit decorator for the forgot-password endpoint."""

ai_detection_rate_limit: Callable[..., Any] = limiter.limit(AI_DETECTION_RATE_LIMIT)
"""Rate limit decorator for AI detection endpoints."""


# --------------------------------------------------------------------------- #
# Exception handler
# --------------------------------------------------------------------------- #

async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handle `RateLimitExceeded` errors with a standardized JSON response.

    Args:
        request: The incoming request that exceeded its rate limit.
        exc: The `RateLimitExceeded` error raised by SlowAPI, carrying the
            configured limit that was violated.

    Returns:
        A `JSONResponse` with status 429, a `Retry-After` header, and a
        standardized error envelope consistent with the rest of the API's
        error responses.
    """
    key = rate_limit_key(request)
    logger.warning(
        "Rate limit exceeded on %s %s by '%s': limit=%s",
        request.method,
        request.url.path,
        key,
        exc.detail,
    )

    retry_after = getattr(exc, "retry_after", None)
    headers = {"Retry-After": str(retry_after)} if retry_after else {}

    body: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status_code": 429,
        "error": "Too Many Requests",
        "message": f"Rate limit exceeded: {exc.detail}. Please try again later.",
        "path": request.url.path,
        "details": None,
    }
    return JSONResponse(status_code=429, content=body, headers=headers)


# --------------------------------------------------------------------------- #
# Registration
# --------------------------------------------------------------------------- #

def setup_rate_limiting(app: FastAPI) -> None:
    """Wire the shared limiter, its exception handler, and its ASGI
    middleware into the FastAPI application.

    Call this once during application startup, e.g.:

        app = FastAPI()
        setup_rate_limiting(app)

    Args:
        app: The FastAPI application instance to configure.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    logger.info("Rate limiting configured and attached to application.")