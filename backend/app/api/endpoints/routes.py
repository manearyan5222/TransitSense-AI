"""
TransitSense AI: Route Information & Forecast Endpoints
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.gtfs_service import GTFSService
from backend.app.services.ml_service import predict_trip_profile
from backend.app.schemas.route import RouteResponse, RouteStopsResponse, RoutePolylineResponse
from backend.app.core.exceptions import RouteNotFoundException

router = APIRouter(tags=["Routes"])


@router.get("/routes", response_model=List[RouteResponse])
def list_routes(
    is_ac: Optional[bool] = Query(None, description="Filter by AC vs Non-AC bus"),
    db: Session = Depends(get_db)
):
    """Lists transit routes across the Delhi bus network."""
    return GTFSService.get_all_routes(db, is_ac=is_ac)


@router.get("/routes/{route_id}", response_model=RouteResponse)
def get_route(route_id: str, db: Session = Depends(get_db)):
    """Fetches details for a single route."""
    route = GTFSService.get_route_by_id(db, route_id)
    if not route:
        raise RouteNotFoundException(route_id)
    return route


@router.get("/routes/{route_id}/stops", response_model=RouteStopsResponse)
def get_route_stops(route_id: str, db: Session = Depends(get_db)):
    """Returns the ordered sequence of physical bus stops along a route."""
    route = GTFSService.get_route_by_id(db, route_id)
    if not route:
        raise RouteNotFoundException(route_id)

    ordered_stops = GTFSService.get_ordered_stops_for_route(db, route_id)
    return {
        "route_id": route.route_id,
        "route_short_name": route.route_short_name,
        "route_long_name": route.route_long_name,
        "direction_id": 0,
        "total_stops": len(ordered_stops),
        "stops": ordered_stops
    }


@router.get("/routes/{route_id}/polyline", response_model=RoutePolylineResponse)
def get_route_polyline(route_id: str, db: Session = Depends(get_db)):
    """Returns a GeoJSON Feature representing the roadway geometry of the route."""
    route = GTFSService.get_route_by_id(db, route_id)
    if not route:
        raise RouteNotFoundException(route_id)

    ordered_stops = GTFSService.get_ordered_stops_for_route(db, route_id)
    coords = [[s["stop_lon"], s["stop_lat"]] for s in ordered_stops]

    return {
        "route_id": route.route_id,
        "route_short_name": route.route_short_name,
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        },
        "properties": {
            "route_id": route.route_id,
            "route_short_name": route.route_short_name,
            "route_long_name": route.route_long_name,
            "is_ac": route.is_ac,
            "bus_capacity": route.bus_capacity
        }
    }


@router.get("/routes/{route_id}/crowd-forecast")
def get_route_crowd_forecast(
    route_id: str,
    departure_time: Optional[str] = Query(None, description="ISO timestamp (defaults to current time)"),
    db: Session = Depends(get_db)
):
    """
    Predicts stop-by-stop passenger occupancy across an entire scheduled trip
    using the trained XGBoost model.
    """
    route = GTFSService.get_route_by_id(db, route_id)
    if not route:
        raise RouteNotFoundException(route_id)

    if not departure_time:
        departure_time = "2026-11-21 09:00:00"

    ordered_stops = GTFSService.get_ordered_stops_for_route(db, route_id)
    forecast = predict_trip_profile(
        route_id=route_id,
        departure_time=departure_time,
        ordered_stops=ordered_stops,
        bus_capacity=route.bus_capacity
    )

    return {
        "route_id": route.route_id,
        "route_short_name": route.route_short_name,
        "departure_time": departure_time,
        "bus_capacity": route.bus_capacity,
        "segments_count": len(forecast),
        "forecast": forecast
    }
