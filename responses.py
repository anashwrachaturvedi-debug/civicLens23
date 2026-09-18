"""Standardized API response envelopes.

Every successful endpoint in the application returns a
:class:`SuccessResponse`, and every handled error returns an
:class:`ErrorResponse` (via the global exception handlers in
``app.middleware.exception_handler``), so API consumers can rely on a
single, predictable response shape across the entire platform.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard envelope wrapping every successful API response."""

    success: bool = True
    message: str
    data: T | None = None


class ErrorDetail(BaseModel):
    """A single structured error item, used for field-level validation errors."""

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standard envelope wrapping every error API response."""

    success: bool = False
    message: str
    errors: list[ErrorDetail] | None = None


class PaginationMeta(BaseModel):
    """Shared pagination metadata attached to any paginated listing."""

    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def build(cls, *, page: int, page_size: int, total: int) -> "PaginationMeta":
        """Compute total_pages and construct pagination metadata."""
        total_pages = (total + page_size - 1) // page_size if page_size else 0
        return cls(page=page, page_size=page_size, total=total, total_pages=total_pages)