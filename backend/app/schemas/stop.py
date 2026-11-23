"""
TransitSense AI: Stop API Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class StopBase(BaseModel):
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    zone_id: str = "DELHI_NCT"
    is_metro_hub: bool = False


class StopResponse(StopBase):
    serviced_routes: List[str] = []
    model_config = ConfigDict(from_attributes=True)


class NearbyStopItem(StopBase):
    distance_meters: int
    walking_duration_minutes: int
    serviced_routes: List[str] = []


class NearbyStopsResponse(BaseModel):
    search_lat: float
    search_lon: float
    radius_meters: int
    count: int
    stops: List[NearbyStopItem]
