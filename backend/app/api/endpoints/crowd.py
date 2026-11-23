"""
TransitSense AI: Crowd Prediction & Corridor Heatmap Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.crowd import SegmentPredictRequest, SegmentPredictResponse
from backend.app.schemas.analytics import HeatmapResponse
from backend.app.services.ml_service import predict_segment_crowd
from backend.app.services.gtfs_service import GTFSService
from backend.app.models.gtfs import RouteModel

router = APIRouter(tags=["Crowd Intelligence"])


@router.post("/crowd/predict-segment", response_model=SegmentPredictResponse)
def predict_segment(
    req: SegmentPredictRequest
):
    """
    Direct model evaluation:
    Feeds a route segment and timestamp to the trained XGBoost model
    and returns passenger demand, occupancy ratio, and crowdedness tier.
    """
    pred = predict_segment_crowd(
        route_id=req.route_id,
        stop_sequence=req.stop_sequence,
        timestamp=req.timestamp,
        stop_id=req.stop_id,
        bus_capacity=req.bus_capacity or 65
    )
    return pred


@router.get("/crowd/network-heatmap", response_model=HeatmapResponse)
def network_crowd_heatmap(
    hour: int = Query(9, ge=0, le=23, description="Hour of day (0-23)"),
    is_weekend: bool = Query(False, description="Weekday vs Weekend"),
    db: Session = Depends(get_db)
):
    """
    Generates a city-wide GeoJSON FeatureCollection of all transit corridors
    color-coded by their predicted crowdedness tier for a specific hour.
    """
    routes = GTFSService.get_all_routes(db)
    features = []

    for route in routes:
        ordered_stops = GTFSService.get_ordered_stops_for_route(db, route.route_id)
        if len(ordered_stops) < 2:
            continue

        # Evaluate each sub-segment between stop i and i+1
        for i in range(len(ordered_stops) - 1):
            s1 = ordered_stops[i]
            s2 = ordered_stops[i + 1]

            mock_date = "2026-11-22" if is_weekend else "2026-11-20"
            t_str = f"{mock_date} {hour:02d}:30:00"

            pred = predict_segment_crowd(
                route_id=route.route_id,
                stop_sequence=s1["stop_sequence"],
                timestamp=t_str,
                stop_id=s1["stop_id"],
                bus_capacity=route.bus_capacity
            )

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [s1["stop_lon"], s1["stop_lat"]],
                        [s2["stop_lon"], s2["stop_lat"]]
                    ]
                },
                "properties": {
                    "route_id": route.route_id,
                    "route_short_name": route.route_short_name,
                    "from_stop_name": s1["stop_name"],
                    "to_stop_name": s2["stop_name"],
                    "hour": hour,
                    "is_weekend": is_weekend,
                    "occupancy_ratio": pred["occupancy_ratio"],
                    "crowd_tier": pred["crowd_tier"],
                    "crowd_label": pred["crowd_label"],
                    "color_code": pred["color_code"],
                    "seating_probability": pred["seating_probability"]
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
