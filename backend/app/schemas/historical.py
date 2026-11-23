"""
TransitSense AI: Historical Demand Schemas
"""

from typing import List
from pydantic import BaseModel


class HourlyProfilePoint(BaseModel):
    hour: int
    time_label: str
    avg_boardings: float
    avg_through_load: float
    avg_occupancy_ratio: float
    crowd_tier: int
    crowd_label: str
    peak_category: str


class StopHistoricalProfileResponse(BaseModel):
    stop_id: str
    stop_name: str
    is_weekend: bool
    hourly_curve: List[HourlyProfilePoint]


class RouteHourlyPoint(BaseModel):
    hour: int
    time_label: str
    mean_load: float
    p85_load: float
    occupancy_ratio: float
    crowd_label: str


class RouteHistoricalProfileResponse(BaseModel):
    route_id: str
    route_short_name: str
    is_weekend: bool
    hourly_curve: List[RouteHourlyPoint]
