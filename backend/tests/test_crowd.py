"""
Unit & Integration Tests: Crowd Prediction Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_predict_segment_crowd_morning_peak():
    payload = {
        "route_id": "DTC_534",
        "stop_sequence": 15,
        "timestamp": "2026-11-21 09:15:00",
        "stop_id": "ST_AV15",
        "bus_capacity": 65
    }
    response = client.post("/api/v1/crowd/predict-segment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["route_id"] == "DTC_534"
    assert data["predicted_passenger_load"] > 0
    assert 0.0 <= data["occupancy_ratio"] <= 2.0
    assert data["crowd_tier"] in [0, 1, 2, 3]
    assert data["crowd_label"] in ["LOW", "MODERATE", "HIGH", "CRUSH"]
    assert data["is_live_ml_prediction"] is True
    assert data["model_version"] == "XGBoost-v1-October2026"


def test_predict_segment_crowd_validation_error():
    # Negative sequence
    bad_payload = {
        "route_id": "DTC_534",
        "stop_sequence": -5,
        "timestamp": "2026-11-21 09:15:00"
    }
    response = client.post("/api/v1/crowd/predict-segment", json=bad_payload)
    assert response.status_code == 422


def test_network_crowd_heatmap():
    response = client.get("/api/v1/crowd/network-heatmap?hour=9&is_weekend=false")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 10
    feature = data["features"][0]
    assert feature["type"] == "Feature"
    assert "color_code" in feature["properties"]
    assert "occupancy_ratio" in feature["properties"]
