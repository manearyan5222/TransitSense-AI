"""
TransitSense AI: GTFS Topology & Spatial Query Service
"""

import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.models.gtfs import RouteModel, StopModel, StopTimeModel, TripModel


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class GTFSService:

    @staticmethod
    def get_all_routes(db: Session, is_ac: bool = None) -> List[RouteModel]:
        query = db.query(RouteModel)
        if is_ac is not None:
            query = query.filter(RouteModel.is_ac == is_ac)
        return query.all()

    @staticmethod
    def get_route_by_id(db: Session, route_id: str) -> RouteModel:
        return db.query(RouteModel).filter(RouteModel.route_id == route_id).first()

    @staticmethod
    def get_ordered_stops_for_route(db: Session, route_id: str) -> List[Dict[str, Any]]:
        """Returns ordered stops for a given route using scheduled trip stop times."""
        # Find first trip for this route
        trip = db.query(TripModel).filter(TripModel.route_id == route_id).first()
        if not trip:
            return []

        stop_times = (
            db.query(StopTimeModel, StopModel)
            .join(StopModel, StopTimeModel.stop_id == StopModel.stop_id)
            .filter(StopTimeModel.trip_id == trip.trip_id)
            .order_by(StopTimeModel.stop_sequence.asc())
            .all()
        )

        results = []
        for st, s in stop_times:
            results.append({
                "stop_sequence": st.stop_sequence,
                "stop_id": s.stop_id,
                "stop_name": s.stop_name,
                "stop_lat": s.stop_lat,
                "stop_lon": s.stop_lon,
                "is_metro_hub": s.is_metro_hub,
                "arrival_time": st.arrival_time
            })
        return results

    @staticmethod
    def search_stops(db: Session, query_str: str, limit: int = 10) -> List[StopModel]:
        pattern = f"%{query_str.strip()}%"
        return (
            db.query(StopModel)
            .filter(StopModel.stop_name.ilike(pattern))
            .limit(limit)
            .all()
        )

    @staticmethod
    def find_nearby_stops(
        db: Session,
        lat: float,
        lon: float,
        max_radius_meters: int = 1000
    ) -> List[Dict[str, Any]]:
        """Finds stops within max_radius_meters, sorted by distance."""
        all_stops = db.query(StopModel).all()
        nearby = []

        for s in all_stops:
            dist = haversine_distance_meters(lat, lon, s.stop_lat, s.stop_lon)
            if dist <= max_radius_meters:
                # Calculate walking duration at 1.2 m/s (~72 m/min)
                walk_mins = max(1, int(round(dist / 72.0)))
                
                # Find passing routes
                passing_routes = (
                    db.query(RouteModel.route_short_name)
                    .join(TripModel, TripModel.route_id == RouteModel.route_id)
                    .join(StopTimeModel, StopTimeModel.trip_id == TripModel.trip_id)
                    .filter(StopTimeModel.stop_id == s.stop_id)
                    .distinct()
                    .all()
                )
                route_names = [r[0] for r in passing_routes]

                nearby.append({
                    "stop_id": s.stop_id,
                    "stop_name": s.stop_name,
                    "stop_lat": s.stop_lat,
                    "stop_lon": s.stop_lon,
                    "zone_id": s.zone_id,
                    "is_metro_hub": s.is_metro_hub,
                    "distance_meters": int(round(dist)),
                    "walking_duration_minutes": walk_mins,
                    "serviced_routes": route_names
                })

        nearby.sort(key=lambda x: x["distance_meters"])
        return nearby
