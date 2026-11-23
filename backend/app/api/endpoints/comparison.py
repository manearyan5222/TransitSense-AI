"""
TransitSense AI: Route Comparison Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.gtfs_service import GTFSService
from backend.app.services.ml_service import predict_segment_crowd
from backend.app.schemas.analytics import RouteComparisonResponse, RouteComparisonItem
from backend.app.models.gtfs import RouteModel

router = APIRouter(tags=["Comparison"])


@router.get("/routes/compare", response_model=RouteComparisonResponse)
def compare_competing_routes(
    route_ids: str = Query("DTC_534,DTC_427", description="Comma-separated route IDs to compare"),
    departure_time: str = Query("2026-11-21 09:00:00", description="Departure timestamp"),
    db: Session = Depends(get_db)
):
    """
    Compares parallel or competing bus routes along shared corridors
    on travel time, crowdedness, seating feasibility, and fares.
    """
    ids = [r.strip() for r in route_ids.split(",") if r.strip()]
    items = []

    for r_id in ids:
        route = GTFSService.get_route_by_id(db, r_id)
        if not route:
            continue

        ordered = GTFSService.get_ordered_stops_for_route(db, r_id)
        mid_seq = max(1, len(ordered) // 2)

        pred = predict_segment_crowd(
            route_id=r_id,
            stop_sequence=mid_seq,
            timestamp=departure_time,
            bus_capacity=route.bus_capacity
        )

        travel_mins = int(round(len(ordered) * 2.8))
        fare = (25 if travel_mins > 30 else 15) if route.is_ac else (15 if travel_mins > 30 else 10)

        # Comfort advantage explanation
        if route.is_ac and pred["occupancy_ratio"] < 0.8:
            adv = "Air-conditioned route with lower estimated occupancy; seating is not guaranteed."
        elif pred["crowd_tier"] == 3:
            adv = "Frequent service, but severe standing crush-load expected."
        elif pred["seating_probability"] > 0.6:
            adv = "Low occupancy; seats readily available."
        else:
            adv = "Standard direct transit option."

        items.append({
            "route_id": route.route_id,
            "route_short_name": route.route_short_name,
            "route_long_name": route.route_long_name,
            "is_ac": route.is_ac,
            "bus_capacity": route.bus_capacity,
            "departure_time": departure_time,
            "estimated_travel_minutes": travel_mins,
            "predicted_load": pred["predicted_passenger_load"],
            "occupancy_ratio": pred["occupancy_ratio"],
            "crowd_tier": pred["crowd_tier"],
            "crowd_label": pred["crowd_label"],
            "seating_probability": pred["seating_probability"],
            "fare_inr": fare,
            "comfort_advantage": adv
        })

    # Recommended route: lowest crowd tier or lowest travel time
    if items:
        recommended = min(items, key=lambda x: (x["crowd_tier"], x["estimated_travel_minutes"]))["route_id"]
    else:
        recommended = "None"

    return {
        "query_corridor": "Delhi Central-South Arterial Corridor",
        "departure_time": departure_time,
        "recommended_route_id": recommended,
        "routes": items
    }
