"""
Unit & Integration Tests: Bus Stop Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_search_stops_by_name():
    response = client.get("/api/v1/stops/search?query=Kashmere")
    assert response.status_code == 200
    stops = response.json()
    assert len(stops) >= 1
    assert any("Kashmere Gate" in s["stop_name"] for s in stops)


def test_search_stops_short_query_validation():
    response = client.get("/api/v1/stops/search?query=A")
    assert response.status_code == 422  # Fails min_length=2 validation


def test_get_valid_stop_by_id():
    response = client.get("/api/v1/stops/ST_AV01")
    assert response.status_code == 200
    data = response.json()
    assert data["stop_name"] == "Anand Vihar ISBT"
    assert data["is_metro_hub"] is True


def test_get_invalid_stop_returns_404():
    response = client.get("/api/v1/stops/INVALID_STOP_ID")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "STOP_NOT_FOUND"


def test_nearby_stops():
    # Coordinates around Anand Vihar
    response = client.get("/api/v1/stops/nearby?lat=28.6469&lon=77.3160&radius_meters=1500")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    closest = data["stops"][0]
    assert closest["stop_name"] == "Anand Vihar ISBT"
    assert closest["distance_meters"] <= 50
