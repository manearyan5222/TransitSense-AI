"""
TransitSense AI: Crowd Prediction API Schemas
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SegmentPredictRequest(BaseModel):
    route_id: str = Field(..., description="GTFS Route ID, e.g. DTC_534")
    stop_sequence: int = Field(..., ge=1, le=50, description="Sequential stop index along route")
    timestamp: str = Field(..., description="Departure ISO timestamp, e.g. 2026-11-21 09:15:00")
    stop_id: Optional[str] = Field(None, description="Optional GTFS Stop ID")
    bus_capacity: Optional[int] = Field(65, ge=30, le=100, description="Bus vehicle capacity")


class SegmentPredictResponse(BaseModel):
    route_id: str
    stop_sequence: int
    timestamp: str
    predicted_passenger_load: float
    bus_capacity: int
    occupancy_ratio: float
    crowd_tier: int
    crowd_label: str
    color_code: str
    seating_probability: float
    explanation: str
    is_live_ml_prediction: bool = True
    model_version: str = "XGBoost-v1-October2026"
    is_live_vehicle_gps: bool = False
    data_provenance: str = "SYNTHETIC_DEMONSTRATION"
    scientific_disclosure: str = "Prediction computed via XGBoost model trained on synthetic October 2026 ETM data."
