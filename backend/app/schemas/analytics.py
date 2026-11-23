"""
TransitSense AI: Analytics Dashboard & Corridor Comparison Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class NetworkOverviewStats(BaseModel):
    total_active_routes: int
    total_bus_stops: int
    october_transactions_analyzed: int
    fleet_vehicles_tracked: int
    peak_morning_rush: str
    peak_evening_rush: str
    active_ml_model: str
    model_mae: float
    model_wape_pct: float


class RouteComparisonItem(BaseModel):
    route_id: str
    route_short_name: str
    route_long_name: str
    is_ac: bool
    bus_capacity: int
    departure_time: str
    estimated_travel_minutes: int
    predicted_load: float
    occupancy_ratio: float
    crowd_tier: int
    crowd_label: str
    seating_probability: float
    fare_inr: int
    comfort_advantage: str


class RouteComparisonResponse(BaseModel):
    query_corridor: str
    departure_time: str
    recommended_route_id: str
    routes: List[RouteComparisonItem]


class HeatmapFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict


class HeatmapResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[HeatmapFeature]
