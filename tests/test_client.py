"""Tests for the NPS Hikes client with mocked HTTP responses."""

from unittest.mock import MagicMock, patch

import pytest

from nps_hikes import Client
from nps_hikes.exceptions import APIError, ParkNotFoundError, ValidationError
from nps_hikes.models import (
    HikedPointsResponse,
    ParkStatsResponse,
    ParkSummaryResponse,
    ParksResponse,
    StatsResponse,
    TrailsResponse,
)


@pytest.fixture
def client():
    return Client(base_url="https://test-api.example.com")


def _mock_response(status_code=200, json_data=None, text=""):
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = 200 <= status_code < 300
    mock.json.return_value = json_data or {}
    mock.text = text
    return mock


# -- Parks --


PARKS_JSON = {
    "park_count": 1,
    "visited_count": 1,
    "parks": [
        {
            "park_code": "yose",
            "park_name": "Yosemite",
            "full_name": "Yosemite National Park",
            "states": "CA",
            "latitude": 37.8651,
            "longitude": -119.5383,
            "url": "https://www.nps.gov/yose/index.htm",
            "designation": "National Park",
            "visit_month": "July",
            "visit_year": 2023,
        }
    ],
}


class TestGetParks:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_parks_response(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARKS_JSON)
        result = client.get_parks()
        assert isinstance(result, ParksResponse)
        assert result.park_count == 1
        assert result.parks[0].park_code == "yose"

    @patch("nps_hikes.client.requests.Session.request")
    def test_passes_filter_params(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARKS_JSON)
        client.get_parks(state="CA", visited=True, visit_year=2023)
        _, kwargs = mock_request.call_args
        params = kwargs["params"]
        assert params["state"] == "CA"
        assert params["visited"] is True
        assert params["visit_year"] == 2023

    @patch("nps_hikes.client.requests.Session.request")
    def test_no_params_when_defaults(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARKS_JSON)
        client.get_parks()
        _, kwargs = mock_request.call_args
        assert kwargs["params"] == {}


# -- Park Summary --


PARK_SUMMARY_JSON = {
    "park_code": "yose",
    "park_name": "Yosemite",
    "full_name": "Yosemite National Park",
    "designation": "National Park",
    "states": "CA",
    "latitude": 37.8651,
    "longitude": -119.5383,
    "total_trails": 42,
    "total_miles": 187.3,
    "avg_trail_length": 4.46,
    "hiked_trails": 15,
    "hiked_miles": 67.2,
    "source_breakdown": {"tnm": 30, "osm": 12},
    "viz_3d_count": 10,
}


class TestGetParkSummary:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_summary(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARK_SUMMARY_JSON)
        result = client.get_park_summary("yose")
        assert isinstance(result, ParkSummaryResponse)
        assert result.hiked_trails == 15

    @patch("nps_hikes.client.requests.Session.request")
    def test_calls_correct_url(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARK_SUMMARY_JSON)
        client.get_park_summary("yose")
        args, _ = mock_request.call_args
        assert args[1] == "https://test-api.example.com/parks/yose/summary"


# -- Trails --


TRAILS_JSON = {
    "trail_count": 1,
    "total_miles": 8.2,
    "trails": [
        {
            "trail_id": "550779",
            "trail_name": "Mono Pass Trail",
            "park_code": "yose",
            "park_name": "Yosemite",
            "states": "CA",
            "source": "TNM",
            "length_miles": 8.2,
            "geometry_type": "LineString",
            "hiked": True,
            "viz_3d_available": True,
            "viz_3d_slug": "mono_pass_trail",
        }
    ],
    "pagination": {
        "limit": 50,
        "offset": 0,
        "total_count": 1,
        "has_next": False,
        "has_prev": False,
    },
}


class TestGetTrails:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_trails_response(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=TRAILS_JSON)
        result = client.get_trails()
        assert isinstance(result, TrailsResponse)
        assert result.trails[0].trail_name == "Mono Pass Trail"

    @patch("nps_hikes.client.requests.Session.request")
    def test_pythonic_param_names(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=TRAILS_JSON)
        client.get_trails(min_length_mi=5.0, max_length_mi=10.0)
        _, kwargs = mock_request.call_args
        params = kwargs["params"]
        assert params["min_length"] == 5.0
        assert params["max_length"] == 10.0

    @patch("nps_hikes.client.requests.Session.request")
    def test_pagination_params(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=TRAILS_JSON)
        client.get_trails(page=2, page_size=25)
        _, kwargs = mock_request.call_args
        params = kwargs["params"]
        assert params["page"] == 2
        assert params["page_size"] == 25


# -- Hiked Points --


HIKED_POINTS_JSON = {
    "count": 1,
    "hiked_points": [
        {
            "id": 1,
            "park_code": "yose",
            "park_name": "Yosemite",
            "location_name": "Vernal Fall",
            "latitude": 37.7268,
            "longitude": -119.5428,
            "matched_trail_name": "Mist Trail",
            "source": "TNM",
        }
    ],
}


class TestGetHikedPoints:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_hiked_points(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=HIKED_POINTS_JSON)
        result = client.get_hiked_points()
        assert isinstance(result, HikedPointsResponse)
        assert result.hiked_points[0].location_name == "Vernal Fall"


# -- Stats --


STATS_JSON = {
    "total_trails": 347,
    "total_miles": 1523.4,
    "avg_trail_length": 4.39,
    "parks_count": 36,
    "states_count": 22,
    "source_breakdown": {"tnm": 200, "osm": 147},
    "longest_trail": {
        "trail_name": "Half Dome Trail",
        "park_code": "yose",
        "park_name": "Yosemite",
        "length_miles": 14.2,
    },
    "shortest_trail": {
        "trail_name": "Mist Trail",
        "park_code": "yose",
        "park_name": "Yosemite",
        "length_miles": 0.3,
    },
}


class TestGetStats:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_stats(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=STATS_JSON)
        result = client.get_stats()
        assert isinstance(result, StatsResponse)
        assert result.total_trails == 347

    @patch("nps_hikes.client.requests.Session.request")
    def test_hiked_filter(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=STATS_JSON)
        client.get_stats(hiked=True)
        _, kwargs = mock_request.call_args
        assert kwargs["params"]["hiked"] is True


# -- Park Stats --


PARK_STATS_JSON = {
    "park_count": 1,
    "parks": [
        {
            "park_code": "yose",
            "park_name": "Yosemite",
            "trail_count": 42,
            "total_miles": 187.3,
            "avg_trail_length": 4.46,
        }
    ],
}


class TestGetParkStats:
    @patch("nps_hikes.client.requests.Session.request")
    def test_returns_park_stats(self, mock_request, client):
        mock_request.return_value = _mock_response(json_data=PARK_STATS_JSON)
        result = client.get_park_stats()
        assert isinstance(result, ParkStatsResponse)
        assert result.parks[0].trail_count == 42


# -- Error handling --


class TestErrorHandling:
    @patch("nps_hikes.client.requests.Session.request")
    def test_404_raises_park_not_found(self, mock_request, client):
        mock_request.return_value = _mock_response(status_code=404)
        with pytest.raises(ParkNotFoundError):
            client.get_park_summary("xxxx")

    @patch("nps_hikes.client.requests.Session.request")
    def test_422_raises_validation_error(self, mock_request, client):
        mock_request.return_value = _mock_response(
            status_code=422,
            json_data={
                "detail": [
                    {"loc": ["query", "park_code"], "msg": "invalid", "type": "value_error"}
                ]
            },
        )
        with pytest.raises(ValidationError):
            client.get_parks(park_code="bad!")

    @patch("nps_hikes.client.requests.Session.request")
    def test_500_raises_api_error(self, mock_request, client):
        mock_request.return_value = _mock_response(
            status_code=500, text="Internal Server Error"
        )
        with pytest.raises(APIError) as exc_info:
            client.get_stats()
        assert exc_info.value.status_code == 500
