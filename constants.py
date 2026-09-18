"""Shared application-wide constants.

Centralizes magic numbers and fixed values referenced from multiple
layers, so thresholds and limits are defined exactly once.
"""

from typing import Final

# --- Severity scoring ---
SEVERITY_HIGH_THRESHOLD: Final[float] = 70.0
SEVERITY_MEDIUM_THRESHOLD: Final[float] = 35.0

CATEGORY_RISK_WEIGHTS: Final[dict[str, float]] = {
    "pothole": 1.0,
    "waterlogging": 0.9,
    "streetlight": 0.7,
    "damaged_signage": 0.6,
    "garbage": 0.5,
    "other": 0.4,
}

LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.5

# --- Geospatial ---
EARTH_RADIUS_KM: Final[float] = 6371.0
DEFAULT_NEARBY_RADIUS_KM: Final[float] = 2.0
MAX_NEARBY_RADIUS_KM: Final[float] = 50.0

# --- Pagination ---
DEFAULT_PAGE: Final[int] = 1
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# --- Uploads ---
MAX_UPLOAD_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_CONTENT_TYPES: Final[set[str]] = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

# --- Rate limiting ---
DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60

# --- Notifications ---
NOTIFICATION_UNREAD_DEFAULT_LIMIT: Final[int] = 20