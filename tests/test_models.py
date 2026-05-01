"""Tests for Pydantic model validation."""

import pytest
from pydantic import ValidationError as PydanticValidationError

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


class TestPark:
    def test_minimal(self):
        park = Park(park_code="yose")
        assert park.park_code == "yose"
        assert park.park_name is None

    def test_full(self):
        park = Park(
            park_code="yose",
            park_name="Yosemite",
            full_name="Yosemite National Park",
            states="CA",
            latitude=37.8651,
            longitude=-119.5383,
            url="https://www.nps.gov/yose/index.htm",
            designation="National Park",
            visit_month="July",
            visit_year=2023,
        )
        assert park.full_name == "Yosemite National Park"
        assert park.visit_year == 2023

    def test_invalid_park_code_rejected(self):
        with pytest.raises(PydanticValidationError):
            Park(park_code="INVALID")


class TestParksResponse:
    def test_valid(self):
        resp = ParksResponse(
            park_count=1,
            visited_count=1,
            parks=[Park(park_code="yose", park_name="Yosemite")],
        )
        assert resp.park_count == 1
        assert len(resp.parks) == 1


class TestTrail:
    def test_minimal(self):
        trail = Trail(
            trail_id="550779",
            park_code="yose",
            source="TNM",
            length_miles=8.2,
            geometry_type="LineString",
            hiked=True,
            viz_3d_available=True,
        )
        assert trail.trail_id == "550779"
        assert trail.hiked is True

    def test_optional_fields(self):
        trail = Trail(
            trail_id="123",
            trail_name="Mist Trail",
            park_code="yose",
            park_name="Yosemite",
            states="CA",
            source="OSM",
            length_miles=6.3,
            geometry_type="LineString",
            highway_type="path",
            hiked=False,
            viz_3d_available=False,
        )
        assert trail.trail_name == "Mist Trail"
        assert trail.highway_type == "path"


class TestTrailsResponse:
    def test_valid(self):
        resp = TrailsResponse(
            trail_count=1,
            total_miles=8.2,
            trails=[
                Trail(
                    trail_id="550779",
                    park_code="yose",
                    source="TNM",
                    length_miles=8.2,
                    geometry_type="LineString",
                    hiked=True,
                    viz_3d_available=True,
                )
            ],
            pagination=PaginationMetadata(
                limit=50,
                offset=0,
                total_count=1,
                has_next=False,
                has_prev=False,
            ),
        )
        assert resp.trail_count == 1
        assert resp.pagination.total_count == 1


class TestHikedPoint:
    def test_valid(self):
        point = HikedPoint(
            id=1,
            park_code="yose",
            location_name="Vernal Fall",
            latitude=37.7268,
            longitude=-119.5428,
        )
        assert point.location_name == "Vernal Fall"


class TestHikedPointsResponse:
    def test_valid(self):
        resp = HikedPointsResponse(
            count=1,
            hiked_points=[
                HikedPoint(id=1, park_code="yose", location_name="Vernal Fall")
            ],
        )
        assert resp.count == 1


class TestSourceBreakdown:
    def test_valid(self):
        sb = SourceBreakdown(tnm=200, osm=147)
        assert sb.tnm == 200
        assert sb.osm == 147


class TestStatsResponse:
    def test_valid(self):
        resp = StatsResponse(
            total_trails=347,
            total_miles=1523.4,
            avg_trail_length=4.39,
            parks_count=36,
            states_count=22,
            source_breakdown=SourceBreakdown(tnm=200, osm=147),
            longest_trail=TrailSummary(
                trail_name="Half Dome Trail",
                park_code="yose",
                length_miles=14.2,
            ),
            shortest_trail=TrailSummary(
                trail_name="Mist Trail",
                park_code="yose",
                length_miles=0.3,
            ),
        )
        assert resp.total_trails == 347
        assert resp.longest_trail.trail_name == "Half Dome Trail"


class TestParkStats:
    def test_valid(self):
        ps = ParkStats(
            park_code="yose",
            park_name="Yosemite",
            trail_count=42,
            total_miles=187.3,
            avg_trail_length=4.46,
        )
        assert ps.trail_count == 42


class TestParkStatsResponse:
    def test_valid(self):
        resp = ParkStatsResponse(
            park_count=1,
            parks=[
                ParkStats(
                    park_code="yose",
                    park_name="Yosemite",
                    trail_count=42,
                    total_miles=187.3,
                    avg_trail_length=4.46,
                )
            ],
        )
        assert resp.park_count == 1


class TestParkSummaryResponse:
    def test_valid(self):
        resp = ParkSummaryResponse(
            park_code="yose",
            park_name="Yosemite",
            full_name="Yosemite National Park",
            total_trails=42,
            total_miles=187.3,
            avg_trail_length=4.46,
            hiked_trails=15,
            hiked_miles=67.2,
            source_breakdown=SourceBreakdown(tnm=30, osm=12),
            viz_3d_count=10,
        )
        assert resp.park_code == "yose"
        assert resp.hiked_trails == 15
