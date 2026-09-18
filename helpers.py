"""Small, pure, reusable helper functions shared across layers.

Nothing in this module touches the database, the network, or request
objects — anything requiring I/O belongs in a service or repository,
not here.
"""

import math
import os
from datetime import UTC, datetime

from app.utils.constants import EARTH_RADIUS_KM


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)


def haversine_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Compute the great-circle distance in kilometers between two coordinates."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def paginate_offset(page: int, page_size: int) -> int:
    """Convert a 1-indexed page number and page size into a SQL OFFSET value."""
    return max(page - 1, 0) * page_size


def total_pages(total_items: int, page_size: int) -> int:
    """Compute the total number of pages for a given item count and page size."""
    if page_size <= 0:
        return 0
    return (total_items + page_size - 1) // page_size


def get_file_extension(filename: str) -> str:
    """Return the lowercase file extension (including the leading dot)."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_image_extension(filename: str, allowed_extensions: set[str]) -> bool:
    """Check whether a filename's extension is in the allowed set."""
    return get_file_extension(filename) in allowed_extensions


def percentage(count: int, total: int) -> float:
    """Compute a rounded percentage, safely handling a zero total."""
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def mask_email(email: str) -> str:
    """Partially mask an email address for safe logging (e.g. 'j***@example.com')."""
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    visible = local[:1] or "*"
    return f"{visible}***@{domain}"