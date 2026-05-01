"""NPS Hikes Python SDK -- a typed client for the NPS Hikes trail API."""

from nps_hikes.client import Client
from nps_hikes.exceptions import APIError, NPSHikesError, ParkNotFoundError, ValidationError
from nps_hikes.models import (
    HikedPoint,
    HikedPointsResponse,
    PaginationMetadata,
    Park,
    ParkStats,
    ParkStatsResponse,
    ParkSummaryResponse,
    ParksResponse,
    SourceBreakdown,
    StatsResponse,
    Trail,
    TrailSummary,
    TrailsResponse,
)

__all__ = [
    "Client",
    # Exceptions
    "NPSHikesError",
    "APIError",
    "ParkNotFoundError",
    "ValidationError",
    # Models
    "HikedPoint",
    "HikedPointsResponse",
    "PaginationMetadata",
    "Park",
    "ParkStats",
    "ParkStatsResponse",
    "ParkSummaryResponse",
    "ParksResponse",
    "SourceBreakdown",
    "StatsResponse",
    "Trail",
    "TrailSummary",
    "TrailsResponse",
]
