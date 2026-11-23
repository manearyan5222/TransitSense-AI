"""
TransitSense AI: Route API Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class RouteBase(BaseModel):
    route_id: str
    agency_id: str
    route_short_name: str
    route_long_name: str
    route_type: int = 3
    is_ac: bool = False
    bus_capacity: int = 65


class RouteResponse(RouteBase):
    model_config = ConfigDict(from_attributes=True)


class RouteStopItem(BaseModel):
    stop_sequence: int
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    is_metro_hub: bool = False


class RouteStopsResponse(BaseModel):
    route_id: str
    route_short_name: str
    route_long_name: str
    direction_id: int
    total_stops: int
    stops: List[RouteStopItem]


class RoutePolylineResponse(BaseModel):
    route_id: str
    route_short_name: str
    type: str = "Feature"
    geometry: dict
    properties: dict
