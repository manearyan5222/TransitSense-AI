"""
Unit & Integration Tests: System Health & Stats Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "ready" in data["ml_engine"]


def test_network_stats_returns_metrics():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["active_routes_count"] >= 5
    assert data["total_stops_count"] >= 40
    assert data["target_city"] == "Delhi NCT"
