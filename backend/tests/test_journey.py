"""
Unit & Integration Tests: Journey Planner & Comparison Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_journey_plan_direct_route():
    payload = {
        "origin": {"lat": 28.6469, "lon": 77.3160, "name": "Anand Vihar ISBT"},
        "destination": {"lat": 28.5180, "lon": 77.1810, "name": "Mehrauli Terminal"},
        "departure_time": "2026-11-21T09:00:00",
        "preference": "FASTEST"
    }
    response = client.post("/api/v1/journey/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["plans"]) >= 1
    assert data["data_provenance"] == "SYNTHETIC_DEMONSTRATION"
    assert data["recommendation_explanation"] is not None
    assert len(data["recommendation_explanation"]) > 10
    
    first_plan = data["plans"][0]
    assert "summary" in first_plan
    assert first_plan["summary"]["total_duration_minutes"] > 0
    assert "overall_crowd_tier" in first_plan["summary"]
    assert "seating_probability" in first_plan["summary"]
    assert len(first_plan["legs"]) >= 3  # Walk -> Transit -> Walk


def test_journey_plan_comfort_first_preference():
    payload = {
        "origin": {"lat": 28.6469, "lon": 77.3160, "name": "Anand Vihar ISBT"},
        "destination": {"lat": 28.5180, "lon": 77.1810, "name": "Mehrauli Terminal"},
        "departure_time": "2026-11-21T09:00:00",
        "preference": "COMFORT_FIRST"
    }
    response = client.post("/api/v1/journey/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_plan_id"] == "plan_comfort"
    assert "comfort" in data["recommendation_explanation"].lower()


def test_journey_plan_balanced_preference():
    payload = {
        "origin": {"lat": 28.6469, "lon": 77.3160, "name": "Anand Vihar ISBT"},
        "destination": {"lat": 28.5180, "lon": 77.1810, "name": "Mehrauli Terminal"},
        "departure_time": "2026-11-21T09:00:00",
        "preference": "BALANCED"
    }
    response = client.post("/api/v1/journey/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["recommendation_explanation"] is not None
    assert "Balanced" in data["recommendation_explanation"]


def test_historical_stop_profile():
    response = client.get("/api/v1/historical/stops/ST_AV01/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["stop_id"] == "ST_AV01"
    assert len(data["hourly_curve"]) >= 10
    first_point = data["hourly_curve"][0]
    assert "avg_boardings" in first_point
    assert "avg_through_load" in first_point
    assert "peak_category" in first_point


def test_route_comparison():
    response = client.get("/api/v1/routes/compare?route_ids=DTC_534,DTC_427&departure_time=2026-11-21%2009:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 2
    r534 = [r for r in data["routes"] if r["route_id"] == "DTC_534"][0]
    assert r534["route_short_name"] == "534"
    assert "comfort_advantage" in r534


def test_analytics_dashboard():
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_active_routes"] >= 5
    assert data["october_transactions_analyzed"] == 84814
    assert data["model_mae"] == 5.1913
