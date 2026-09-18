"""
app/services/location_service.py

Geolocation service responsible for validating coordinates, calculating
distances between points using the Haversine formula, and finding nearby
issues within a given search radius.

Persistence is abstracted behind a small `IssueLocationRepository` Protocol
so this service stays decoupled from any specific database. Inject a real
repository (SQL with spatial indexing, MongoDB geospatial queries, etc.)
without changing any logic here.

This module intentionally contains NO API route logic.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

EARTH_RADIUS_KM: float = 6371.0088
EARTH_RADIUS_MILES: float = 3958.7613

MIN_LATITUDE: float = -90.0
MAX_LATITUDE: float = 90.0
MIN_LONGITUDE: float = -180.0
MAX_LONGITUDE: float = 180.0


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class LocationServiceError(Exception):
    """Base exception for all location service related errors."""


class InvalidCoordinateError(LocationServiceError):
    """Raised when latitude/longitude values are missing or out of range."""


class InvalidRadiusError(LocationServiceError):
    """Raised when a search radius is missing, zero, or negative."""


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Coordinates:
    """A validated latitude/longitude pair."""

    latitude: float
    longitude: float

    def to_dict(self) -> dict[str, float]:
        """Serialize coordinates to a plain dict."""
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass(frozen=True)
class NearbyIssue:
    """An issue paired with its computed distance from a search origin."""

    issue_id: str
    coordinates: Coordinates
    distance_km: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the nearby issue result to a plain dict."""
        return {
            "issue_id": self.issue_id,
            "coordinates": self.coordinates.to_dict(),
            "distance_km": round(self.distance_km, 4),
            "metadata": self.metadata,
        }


# --------------------------------------------------------------------------- #
# Repository abstraction
# --------------------------------------------------------------------------- #

class IssueLocationRepository(Protocol):
    """
    Storage abstraction for retrieving geotagged issues.

    Implement this against your real database. For large datasets, the
    implementation should ideally push a coarse bounding-box filter down to
    the database (e.g. via a spatial index) before returning candidates;
    LocationService then applies the exact Haversine filter/sort on top.
    """

    async def list_candidate_issues(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> list[dict[str, Any]]:
        """
        Return candidate issues whose coordinates fall within a bounding box.

        Each returned dict is expected to contain at least:
            - "id": str
            - "latitude": float
            - "longitude": float
        Any additional keys are treated as metadata and passed through.
        """
        ...


# --------------------------------------------------------------------------- #
# Location Service
# --------------------------------------------------------------------------- #

class LocationService:
    """
    Core geolocation service: validates coordinates, computes distances, and
    finds nearby issues within a radius.

    Usage:
        service = LocationService(repository=my_issue_repository)
        origin = service.validate_coordinates(28.6139, 77.2090)
        nearby = await service.find_nearby_issues(origin, radius_km=5)
    """

    def __init__(self, repository: IssueLocationRepository | None = None) -> None:
        """
        Initialize the LocationService.

        Args:
            repository: Storage backend used to fetch candidate issues for
                        proximity search. Required for `find_nearby_issues`;
                        may be omitted if only distance/validation helpers
                        are needed.
        """
        self._repository = repository

    # ------------------------------------------------------------------- #
    # Validation
    # ------------------------------------------------------------------- #

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> Coordinates:
        """
        Validate that latitude/longitude values are well-formed and within
        valid geographic ranges.

        Args:
            latitude: Latitude value in decimal degrees.
            longitude: Longitude value in decimal degrees.

        Returns:
            A validated Coordinates instance.

        Raises:
            InvalidCoordinateError: If either value is missing, non-numeric,
                                     or out of valid range.
        """
        if latitude is None or longitude is None:
            raise InvalidCoordinateError("Both latitude and longitude are required.")

        try:
            lat = float(latitude)
            lon = float(longitude)
        except (TypeError, ValueError) as exc:
            raise InvalidCoordinateError(
                f"Latitude/longitude must be numeric: {exc}"
            ) from exc

        if math.isnan(lat) or math.isnan(lon) or math.isinf(lat) or math.isinf(lon):
            raise InvalidCoordinateError("Latitude/longitude must be finite numbers.")

        if not (MIN_LATITUDE <= lat <= MAX_LATITUDE):
            raise InvalidCoordinateError(
                f"Latitude {lat} out of range [{MIN_LATITUDE}, {MAX_LATITUDE}]."
            )

        if not (MIN_LONGITUDE <= lon <= MAX_LONGITUDE):
            raise InvalidCoordinateError(
                f"Longitude {lon} out of range [{MIN_LONGITUDE}, {MAX_LONGITUDE}]."
            )

        return Coordinates(latitude=lat, longitude=lon)

    @staticmethod
    def validate_radius(radius_km: float) -> float:
        """
        Validate a search radius value.

        Args:
            radius_km: Search radius in kilometers.

        Returns:
            The validated radius as a float.

        Raises:
            InvalidRadiusError: If the radius is missing, non-numeric, zero,
                                 or negative.
        """
        if radius_km is None:
            raise InvalidRadiusError("A search radius is required.")

        try:
            radius = float(radius_km)
        except (TypeError, ValueError) as exc:
            raise InvalidRadiusError(f"Radius must be numeric: {exc}") from exc

        if math.isnan(radius) or math.isinf(radius):
            raise InvalidRadiusError("Radius must be a finite number.")

        if radius <= 0:
            raise InvalidRadiusError("Radius must be greater than zero.")

        return radius

    # ------------------------------------------------------------------- #
    # Distance calculation
    # ------------------------------------------------------------------- #

    @staticmethod
    def calculate_distance(
        origin: Coordinates,
        destination: Coordinates,
        unit: str = "km",
    ) -> float:
        """
        Calculate the great-circle distance between two coordinates using
        the Haversine formula.

        Args:
            origin: Starting point coordinates.
            destination: Ending point coordinates.
            unit: Either "km" (kilometers) or "mi" (miles).

        Returns:
            The distance between the two points in the requested unit.

        Raises:
            LocationServiceError: If an unsupported unit is provided.
        """
        if unit not in ("km", "mi"):
            raise LocationServiceError(f"Unsupported distance unit: '{unit}'.")

        radius = EARTH_RADIUS_KM if unit == "km" else EARTH_RADIUS_MILES

        lat1_rad = math.radians(origin.latitude)
        lat2_rad = math.radians(destination.latitude)
        delta_lat = math.radians(destination.latitude - origin.latitude)
        delta_lon = math.radians(destination.longitude - origin.longitude)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return radius * c

    # ------------------------------------------------------------------- #
    # Bounding box helper (used to narrow DB candidates before Haversine)
    # ------------------------------------------------------------------- #

    @staticmethod
    def _bounding_box(
        origin: Coordinates, radius_km: float
    ) -> tuple[float, float, float, float]:
        """
        Compute a rough latitude/longitude bounding box around an origin
        point for a given radius, used to cheaply narrow down candidates
        before applying the exact Haversine calculation.

        Args:
            origin: Center point of the search.
            radius_km: Search radius in kilometers.

        Returns:
            A tuple of (min_lat, max_lat, min_lon, max_lon).
        """
        lat_delta = radius_km / 111.32  # ~ km per degree of latitude

        # Guard against division by zero near the poles.
        cos_lat = math.cos(math.radians(origin.latitude))
        lon_delta = radius_km / (111.32 * max(cos_lat, 1e-6))

        min_lat = max(origin.latitude - lat_delta, MIN_LATITUDE)
        max_lat = min(origin.latitude + lat_delta, MAX_LATITUDE)
        min_lon = max(origin.longitude - lon_delta, MIN_LONGITUDE)
        max_lon = min(origin.longitude + lon_delta, MAX_LONGITUDE)

        return min_lat, max_lat, min_lon, max_lon

    # ------------------------------------------------------------------- #
    # Nearby search
    # ------------------------------------------------------------------- #

    async def find_nearby_issues(
        self,
        origin: Coordinates,
        radius_km: float,
        limit: int | None = None,
    ) -> list[NearbyIssue]:
        """
        Find issues located within a given radius of an origin point,
        sorted by ascending distance.

        Args:
            origin: Center point of the search.
            radius_km: Search radius in kilometers.
            limit: Optional maximum number of results to return.

        Returns:
            A list of NearbyIssue results within the radius, nearest first.

        Raises:
            InvalidRadiusError: If radius_km is invalid.
            LocationServiceError: If no repository has been configured.
        """
        if self._repository is None:
            raise LocationServiceError(
                "No IssueLocationRepository configured; cannot search for "
                "nearby issues."
            )

        validated_radius = self.validate_radius(radius_km)
        min_lat, max_lat, min_lon, max_lon = self._bounding_box(origin, validated_radius)

        try:
            candidates = await self._repository.list_candidate_issues(
                min_lat=min_lat,
                max_lat=max_lat,
                min_lon=min_lon,
                max_lon=max_lon,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to fetch candidate issues from repository.")
            raise LocationServiceError(
                f"Failed to fetch candidate issues: {exc}"
            ) from exc

        logger.debug(
            "Fetched %d candidate issue(s) within bounding box for radius=%.2fkm.",
            len(candidates),
            validated_radius,
        )

        results: list[NearbyIssue] = []
        for candidate in candidates:
            try:
                candidate_coords = self.validate_coordinates(
                    candidate["latitude"], candidate["longitude"]
                )
            except (KeyError, InvalidCoordinateError) as exc:
                logger.warning("Skipping malformed candidate issue: %s", exc)
                continue

            distance = self.calculate_distance(origin, candidate_coords, unit="km")
            if distance <= validated_radius:
                metadata = {
                    k: v
                    for k, v in candidate.items()
                    if k not in ("id", "latitude", "longitude")
                }
                results.append(
                    NearbyIssue(
                        issue_id=str(candidate["id"]),
                        coordinates=candidate_coords,
                        distance_km=distance,
                        metadata=metadata,
                    )
                )

        results.sort(key=lambda r: r.distance_km)

        if limit is not None:
            results = results[:limit]

        logger.info(
            "Found %d issue(s) within %.2fkm of (%.6f, %.6f).",
            len(results),
            validated_radius,
            origin.latitude,
            origin.longitude,
        )
        return results

    # ------------------------------------------------------------------- #
    # Geolocation helpers
    # ------------------------------------------------------------------- #

    @staticmethod
    def is_within_radius(
        origin: Coordinates, destination: Coordinates, radius_km: float
    ) -> bool:
        """
        Check whether a destination point falls within a given radius of an
        origin point.

        Args:
            origin: Center point.
            destination: Point to test.
            radius_km: Radius in kilometers.

        Returns:
            True if the destination is within the radius, False otherwise.
        """
        return LocationService.calculate_distance(origin, destination) <= radius_km

    @staticmethod
    def midpoint(origin: Coordinates, destination: Coordinates) -> Coordinates:
        """
        Calculate the geographic midpoint between two coordinates along the
        great-circle path.

        Args:
            origin: First point.
            destination: Second point.

        Returns:
            The midpoint as a Coordinates instance.
        """
        lat1_rad = math.radians(origin.latitude)
        lon1_rad = math.radians(origin.longitude)
        lat2_rad = math.radians(destination.latitude)
        delta_lon = math.radians(destination.longitude - origin.longitude)

        bx = math.cos(lat2_rad) * math.cos(delta_lon)
        by = math.cos(lat2_rad) * math.sin(delta_lon)

        mid_lat_rad = math.atan2(
            math.sin(lat1_rad) + math.sin(lat2_rad),
            math.sqrt((math.cos(lat1_rad) + bx) ** 2 + by ** 2),
        )
        mid_lon_rad = lon1_rad + math.atan2(by, math.cos(lat1_rad) + bx)

        return Coordinates(
            latitude=math.degrees(mid_lat_rad),
            longitude=math.degrees(mid_lon_rad),
        )

    @staticmethod
    def format_coordinates(coordinates: Coordinates, precision: int = 6) -> str:
        """
        Format coordinates as a human-readable "lat, lon" string.

        Args:
            coordinates: The coordinates to format.
            precision: Number of decimal places to include.

        Returns:
            A formatted string, e.g. "28.613900, 77.209000".
        """
        return (
            f"{coordinates.latitude:.{precision}f}, "
            f"{coordinates.longitude:.{precision}f}"
        )