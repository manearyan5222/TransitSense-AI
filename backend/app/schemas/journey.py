"""
TransitSense AI: Journey Planning API Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = Field(..., ge=28.0, le=29.0, description="Latitude in Delhi NCR")
    lon: float = Field(..., ge=76.5, le=77.8, description="Longitude in Delhi NCR")
    name: Optional[str] = None


class JourneyPlanRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    departure_time: str = Field(..., description="ISO 8601 string, e.g. 2026-11-21T09:00:00")
    preference: str = Field("BALANCED", description="Routing preference: FASTEST, COMFORT_FIRST, BALANCED")
    max_walk_meters: int = Field(800, ge=200, le=2000, description="Maximum walking radius to transit stop")
    max_transfers: int = Field(1, ge=0, le=3)


class CrowdAssessment(BaseModel):
    crowd_tier: int
    crowd_label: str
    color_code: str
    mean_occupancy_ratio: float
    seating_probability: float
    comfort_description: str


class IntermediateStopItem(BaseModel):
    stop_sequence: int
    stop_id: str
    stop_name: str
    predicted_load: float
    occupancy_ratio: float
    crowd_tier: int
    crowd_label: str


class TransitLeg(BaseModel):
    leg_type: str = "TRANSIT"
    mode: str = "BUS"
    route_id: str
    route_short_name: str
    route_long_name: str
    is_ac: bool
    from_stop_id: str
    from_stop_name: str
    to_stop_id: str
    to_stop_name: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops_count: int
    crowd_assessment: CrowdAssessment
    intermediate_stops: List[IntermediateStopItem] = []
    polyline: Dict[str, Any]


class WalkLeg(BaseModel):
    leg_type: str = "WALK"
    duration_minutes: int
    distance_meters: int
    from_name: str
    to_name: str
    instruction: str


class ItinerarySummary(BaseModel):
    total_duration_minutes: int
    total_walking_minutes: int
    total_walking_meters: int
    transfers_count: int
    estimated_fare_inr: int
    overall_crowd_tier: int
    overall_crowd_label: str
    seating_probability: float
    comfort_tradeoff: Optional[str] = None


class ItineraryPlan(BaseModel):
    plan_id: str
    tag: str  # FASTEST, MOST_COMFORTABLE, BALANCED
    title: str
    summary: ItinerarySummary
    legs: List[Any]


class JourneyPlanResponse(BaseModel):
    status: str = "success"
    query: Dict[str, Any]
    recommended_plan_id: str
    recommendation_explanation: Optional[str] = None
    data_provenance: str = "SYNTHETIC_DEMONSTRATION"
    plans: List[ItineraryPlan]
    execution_time_ms: float
