"""
TransitSense AI: Bus Stop Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.gtfs_service import GTFSService
from backend.app.schemas.stop import StopResponse, NearbyStopsResponse
from backend.app.core.exceptions import StopNotFoundException
from backend.app.models.gtfs import StopModel, RouteModel, TripModel, StopTimeModel

router = APIRouter(tags=["Stops"])


@router.get("/stops/search", response_model=List[StopResponse])
def search_stops(
    query: str = Query(..., min_length=2, description="Stop name query, e.g. 'Kashmere Gate' or 'AIIMS'"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Searches for transit stops by name with fuzzy pattern matching."""
    stops = GTFSService.search_stops(db, query, limit=limit)
    res = []
    for s in stops:
        # Get passing routes
        passing_routes = (
            db.query(RouteModel.route_short_name)
            .join(TripModel, TripModel.route_id == RouteModel.route_id)
            .join(StopTimeModel, StopTimeModel.trip_id == TripModel.trip_id)
            .filter(StopTimeModel.stop_id == s.stop_id)
            .distinct()
            .all()
        )
        route_names = [r[0] for r in passing_routes]
        res.append({
            "stop_id": s.stop_id,
            "stop_name": s.stop_name,
            "stop_lat": s.stop_lat,
            "stop_lon": s.stop_lon,
            "zone_id": s.zone_id,
            "is_metro_hub": s.is_metro_hub,
            "serviced_routes": route_names
        })
    return res


@router.get("/stops/nearby", response_model=NearbyStopsResponse)
def nearby_stops(
    lat: float = Query(..., ge=28.0, le=29.0, description="WGS84 Latitude"),
    lon: float = Query(..., ge=76.5, le=77.8, description="WGS84 Longitude"),
    radius_meters: int = Query(1000, ge=100, le=5000),
    db: Session = Depends(get_db)
):
    """Finds bus stops within a walking radius of a geographic coordinate."""
    nearby = GTFSService.find_nearby_stops(db, lat, lon, max_radius_meters=radius_meters)
    return {
        "search_lat": lat,
        "search_lon": lon,
        "radius_meters": radius_meters,
        "count": len(nearby),
        "stops": nearby
    }


@router.get("/stops/{stop_id}", response_model=StopResponse)
def get_stop(stop_id: str, db: Session = Depends(get_db)):
    """Fetches details for a single bus stop."""
    s = db.query(StopModel).filter(StopModel.stop_id == stop_id).first()
    if not s:
        raise StopNotFoundException(stop_id)

    passing_routes = (
        db.query(RouteModel.route_short_name)
        .join(TripModel, TripModel.route_id == RouteModel.route_id)
        .join(StopTimeModel, StopTimeModel.trip_id == TripModel.trip_id)
        .filter(StopTimeModel.stop_id == s.stop_id)
        .distinct()
        .all()
    )
    return {
        "stop_id": s.stop_id,
        "stop_name": s.stop_name,
        "stop_lat": s.stop_lat,
        "stop_lon": s.stop_lon,
        "zone_id": s.zone_id,
        "is_metro_hub": s.is_metro_hub,
        "serviced_routes": [r[0] for r in passing_routes]
    }
