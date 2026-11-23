"""
Unit & Integration Tests: Route Information Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_all_routes():
    response = client.get("/api/v1/routes")
    assert response.status_code == 200
    routes = response.json()
    assert len(routes) >= 5
    route_ids = [r["route_id"] for r in routes]
    assert "DTC_534" in route_ids
    assert "DTC_764" in route_ids


def test_filter_routes_by_ac():
    response_ac = client.get("/api/v1/routes?is_ac=true")
    assert response_ac.status_code == 200
    ac_routes = response_ac.json()
    assert all(r["is_ac"] is True for r in ac_routes)


def test_get_valid_route_details():
    response = client.get("/api/v1/routes/DTC_534")
    assert response.status_code == 200
    data = response.json()
    assert data["route_short_name"] == "534"
    assert data["bus_capacity"] == 65


def test_get_invalid_route_returns_404():
    response = client.get("/api/v1/routes/NON_EXISTENT_ROUTE")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "ROUTE_NOT_FOUND"


def test_get_route_stops():
    response = client.get("/api/v1/routes/DTC_534/stops")
    assert response.status_code == 200
    data = response.json()
    assert data["total_stops"] == 26
    assert data["stops"][0]["stop_name"] == "Anand Vihar ISBT"


def test_get_route_polyline_geojson():
    response = client.get("/api/v1/routes/DTC_534/polyline")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "Feature"
    assert data["geometry"]["type"] == "LineString"
    assert len(data["geometry"]["coordinates"]) == 26


def test_get_route_crowd_forecast():
    response = client.get("/api/v1/routes/DTC_534/crowd-forecast?departure_time=2026-11-21%2009:00:00")
    assert response.status_code == 200
    data = response.json()
    assert data["segments_count"] == 26
    assert len(data["forecast"]) == 26
    first_seg = data["forecast"][0]
    assert "predicted_passenger_load" in first_seg
    assert "crowd_label" in first_seg
