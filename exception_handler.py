"""
app/middleware/exception_handler.py

Global exception handlers for the FastAPI application.

Every handler in this module returns a standardized JSON error envelope of
the shape:

    {
        "timestamp": "2026-07-04T10:42:28.123456+00:00",
        "status_code": 404,
        "error": "Not Found",
        "message": "Issue with id 'abc123' was not found.",
        "path": "/api/v1/issues/abc123",
        "details": null
    }

so that API consumers can rely on one consistent error shape regardless of
what failed internally (routing, validation, the database layer, auth, or
an unhandled bug).

Register all handlers on app startup via `register_exception_handlers(app)`.

This module intentionally contains NO business logic — only error
translation, formatting, and logging.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Custom authentication exception
# --------------------------------------------------------------------------- #

class AuthenticationError(Exception):
    """Raised by auth-related dependencies/services for credential failures
    that should be reported as 401 Unauthorized, independent of FastAPI's
    own HTTPException flow (e.g. errors raised deep in a token/service
    layer rather than directly inside a route dependency).

    Attributes:
        message: Human-readable description of the authentication failure.
    """

    def __init__(self, message: str = "Authentication failed.") -> None:
        self.message = message
        super().__init__(message)


# --------------------------------------------------------------------------- #
# Standard error envelope
# --------------------------------------------------------------------------- #

def _build_error_response(
    request: Request,
    status_code: int,
    message: str,
    details: Any = None,
) -> JSONResponse:
    """Build a standardized JSON error response.

    Args:
        request: The incoming request that triggered the error, used to
            capture the request path.
        status_code: The HTTP status code to return.
        message: A human-readable summary of what went wrong.
        details: Optional structured detail payload (e.g. field-level
            validation errors). Omitted from the response body if None.

    Returns:
        A `JSONResponse` containing the standardized error envelope.
    """
    try:
        error_name = HTTPStatus(status_code).phrase
    except ValueError:
        error_name = "Error"

    body: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status_code": status_code,
        "error": error_name,
        "message": message,
        "path": request.url.path,
        "details": details,
    }
    return JSONResponse(status_code=status_code, content=body)


# --------------------------------------------------------------------------- #
# Handlers
# --------------------------------------------------------------------------- #

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle FastAPI/Starlette `HTTPException`s (e.g. 400, 401, 403, 404).

    Args:
        request: The incoming request that triggered the exception.
        exc: The raised `HTTPException`, carrying a status code and detail.

    Returns:
        A standardized JSON error response matching the exception's
        original status code.
    """
    logger.info(
        "HTTPException on %s %s: [%d] %s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )
    return _build_error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation failures (invalid query params, body, etc.).

    Args:
        request: The incoming request that failed validation.
        exc: The raised `RequestValidationError`, carrying Pydantic's
            structured list of field errors.

    Returns:
        A standardized 422 JSON error response, including per-field
        validation error details.
    """
    field_errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", []) if part != "body"),
            "message": error.get("msg"),
            "type": error.get("type"),
        }
        for error in exc.errors()
    ]

    logger.info(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        field_errors,
    )

    return _build_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed.",
        details=field_errors,
    )


async def authentication_exception_handler(
    request: Request, exc: AuthenticationError
) -> JSONResponse:
    """Handle custom `AuthenticationError`s raised outside the normal
    `HTTPException` flow.

    Args:
        request: The incoming request that triggered the exception.
        exc: The raised `AuthenticationError`.

    Returns:
        A standardized 401 JSON error response.
    """
    logger.warning(
        "Authentication error on %s %s: %s",
        request.method,
        request.url.path,
        exc.message,
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=exc.message,
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle database errors raised by SQLAlchemy.

    Integrity violations (e.g. unique constraint failures, foreign key
    violations) are reported as 409 Conflict with a safe, generic message.
    All other SQLAlchemy errors are treated as 500 Internal Server Error.
    In both cases, the full exception is logged server-side; raw database
    error details are never leaked to the client.

    Args:
        request: The incoming request that triggered the database error.
        exc: The raised `SQLAlchemyError` (or subclass).

    Returns:
        A standardized 409 or 500 JSON error response.
    """
    logger.error(
        "Database error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )

    if isinstance(exc, IntegrityError):
        return _build_error_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            message="The request could not be completed due to a data conflict.",
        )

    return _build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="A database error occurred. Please try again later.",
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any exception not caught by a more specific handler.

    Acts as a safety net so the client never receives an unformatted
    traceback or raw framework error page. The full exception is logged
    server-side with a stack trace; only a generic message is returned to
    the client.

    Args:
        request: The incoming request that triggered the exception.
        exc: The unhandled exception.

    Returns:
        A standardized 500 JSON error response.
    """
    logger.critical(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
    )


# --------------------------------------------------------------------------- #
# Registration
# --------------------------------------------------------------------------- #

def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI application.

    Call this once during application startup, e.g.:

        app = FastAPI()
        register_exception_handlers(app)

    Args:
        app: The FastAPI application instance to attach handlers to.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AuthenticationError, authentication_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Global exception handlers registered.")