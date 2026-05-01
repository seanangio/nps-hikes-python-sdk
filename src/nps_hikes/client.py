"""NPS Hikes API client."""

from __future__ import annotations

import requests

from nps_hikes.exceptions import APIError, ParkNotFoundError, ValidationError
from nps_hikes.models import (
    HikedPointsResponse,
    ParkStatsResponse,
    ParkSummaryResponse,
    ParksResponse,
    StatsResponse,
    TrailsResponse,
)

DEFAULT_BASE_URL = "https://seanangio-nps-hikes.onrender.com"


class Client:
    """Python client for the NPS Hikes trail API.

    Args:
        base_url: Base URL of the API. Defaults to the production deployment.
        timeout: Request timeout in seconds. Defaults to 120 to accommodate
            Render free-tier cold starts.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def _request(self, method: str, path: str, params: dict | None = None) -> dict:
        """Send an HTTP request and return the parsed JSON response."""
        url = f"{self.base_url}{path}"
        response = self._session.request(
            method, url, params=params, timeout=self.timeout
        )

        if response.status_code == 404:
            raise ParkNotFoundError(
                params.get("park_code", "") if params else path.split("/")[-2]
            )
        if response.status_code == 422:
            detail = response.json().get("detail", [])
            raise ValidationError(detail)
        if not response.ok:
            raise APIError(response.status_code, response.text)

        return response.json()

    # -- Parks endpoints --

    def get_parks(
        self,
        *,
        park_code: str | None = None,
        state: str | None = None,
        visited: bool | None = None,
        visit_year: int | None = None,
        visit_month: list[str] | None = None,
        description: bool = False,
        boundary: bool = False,
    ) -> ParksResponse:
        """Get all parks with optional filtering.

        Args:
            park_code: 4-character park code (e.g., ``"yose"``).
            state: 2-letter state code (e.g., ``"CA"``).
            visited: Filter by visit status. ``True`` for visited only,
                ``False`` for unvisited, ``None`` for all.
            visit_year: Filter by visit year (e.g., ``2024``).
            visit_month: Filter by visit month(s) (e.g., ``["Jun", "Jul"]``).
            description: Include full park descriptions.
            boundary: Include simplified park boundary GeoJSON.
        """
        params: dict = {}
        if park_code is not None:
            params["park_code"] = park_code
        if state is not None:
            params["state"] = state
        if visited is not None:
            params["visited"] = visited
        if visit_year is not None:
            params["visit_year"] = visit_year
        if visit_month is not None:
            params["visit_month"] = visit_month
        if description:
            params["description"] = True
        if boundary:
            params["boundary"] = True

        data = self._request("GET", "/parks", params=params)
        return ParksResponse.model_validate(data)

    def get_park_summary(self, park_code: str) -> ParkSummaryResponse:
        """Get a detailed summary for a single park.

        Args:
            park_code: 4-character park code (e.g., ``"yose"``).

        Raises:
            ParkNotFoundError: If the park code does not exist.
        """
        data = self._request("GET", f"/parks/{park_code}/summary")
        return ParkSummaryResponse.model_validate(data)

    # -- Trails endpoints --

    def get_trails(
        self,
        *,
        park_code: str | None = None,
        state: str | None = None,
        source: str | None = None,
        hiked: bool | None = None,
        min_length_mi: float | None = None,
        max_length_mi: float | None = None,
        trail_type: str | None = None,
        viz_3d: bool | None = None,
        limit: int = 50,
        offset: int = 0,
        page: int | None = None,
        page_size: int | None = None,
        geojson: bool = False,
    ) -> TrailsResponse:
        """Get trails with optional filtering and pagination.

        Args:
            park_code: 4-character park code (e.g., ``"yose"``).
            state: 2-letter state code (e.g., ``"CA"``).
            source: Data source filter (``"TNM"`` or ``"OSM"``).
            hiked: Filter by hiking status.
            min_length_mi: Minimum trail length in miles.
            max_length_mi: Maximum trail length in miles.
            trail_type: OSM highway type (e.g., ``"path"``, ``"footway"``).
            viz_3d: Filter by 3D visualization availability.
            limit: Number of trails per page (1--1000). Defaults to 50.
            offset: Number of trails to skip. Defaults to 0.
            page: Page number (alternative to offset).
            page_size: Items per page (alternative to limit).
            geojson: Include trail geometry GeoJSON.
        """
        params: dict = {}
        if park_code is not None:
            params["park_code"] = park_code
        if state is not None:
            params["state"] = state
        if source is not None:
            params["source"] = source
        if hiked is not None:
            params["hiked"] = hiked
        if min_length_mi is not None:
            params["min_length"] = min_length_mi
        if max_length_mi is not None:
            params["max_length"] = max_length_mi
        if trail_type is not None:
            params["trail_type"] = trail_type
        if viz_3d is not None:
            params["viz_3d"] = viz_3d
        if limit != 50:
            params["limit"] = limit
        if offset != 0:
            params["offset"] = offset
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if geojson:
            params["geojson"] = True

        data = self._request("GET", "/trails", params=params)
        return TrailsResponse.model_validate(data)

    def get_hiked_points(
        self,
        *,
        park_code: str | None = None,
    ) -> HikedPointsResponse:
        """Get GPS marker points representing actual hikes.

        Args:
            park_code: 4-character park code to filter by (e.g., ``"yose"``).
        """
        params: dict = {}
        if park_code is not None:
            params["park_code"] = park_code

        data = self._request("GET", "/trails/hiked-points", params=params)
        return HikedPointsResponse.model_validate(data)

    # -- Stats endpoints --

    def get_stats(
        self,
        *,
        hiked: bool | None = None,
    ) -> StatsResponse:
        """Get aggregate hiking statistics.

        Args:
            hiked: Filter by hiking status. ``True`` for hiked only,
                ``False`` for unvisited, ``None`` for all.
        """
        params: dict = {}
        if hiked is not None:
            params["hiked"] = hiked

        data = self._request("GET", "/stats", params=params)
        return StatsResponse.model_validate(data)

    def get_park_stats(
        self,
        *,
        hiked: bool | None = None,
    ) -> ParkStatsResponse:
        """Get per-park hiking statistics.

        Args:
            hiked: Filter by hiking status. ``True`` for hiked only,
                ``False`` for unvisited, ``None`` for all.
        """
        params: dict = {}
        if hiked is not None:
            params["hiked"] = hiked

        data = self._request("GET", "/stats/parks", params=params)
        return ParkStatsResponse.model_validate(data)
