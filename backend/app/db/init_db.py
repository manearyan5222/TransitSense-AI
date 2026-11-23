"""
TransitSense AI: Database Initialization & GTFS Seeder
"""

import os
import logging
import pandas as pd
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.models.gtfs import AgencyModel, RouteModel, StopModel, TripModel, StopTimeModel
from backend.app.models.analytics import SegmentCrowdModel, StopHourlyIndexModel
from backend.app.config import settings

logger = logging.getLogger("DBInit")


def init_database():
    """Initializes tables and seeds initial GTFS and analytics records."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(RouteModel).first() is not None:
            logger.info("Database already seeded with GTFS topology.")
            return

        logger.info("Seeding GTFS routes, stops, and schedules from data/gtfs...")
        gtfs_dir = settings.GTFS_DIR

        # Agencies
        agencies_file = os.path.join(gtfs_dir, "agency.txt")
        if os.path.exists(agencies_file):
            df_agency = pd.read_csv(agencies_file)
            for _, row in df_agency.iterrows():
                db.add(AgencyModel(
                    agency_id=str(row["agency_id"]),
                    agency_name=str(row["agency_name"]),
                    agency_url=str(row.get("agency_url", "")),
                    agency_timezone=str(row.get("agency_timezone", "Asia/Kolkata"))
                ))

        # Routes
        routes_file = os.path.join(gtfs_dir, "routes.txt")
        route_caps = {"DTC_534": 65, "DTC_764": 65, "DTC_427": 65, "DTC_502": 65, "DTC_620": 46}
        if os.path.exists(routes_file):
            df_routes = pd.read_csv(routes_file)
            for _, row in df_routes.iterrows():
                r_id = str(row["route_id"])
                db.add(RouteModel(
                    route_id=r_id,
                    agency_id=str(row["agency_id"]),
                    route_short_name=str(row["route_short_name"]),
                    route_long_name=str(row["route_long_name"]),
                    route_type=int(row.get("route_type", 3)),
                    is_ac=bool(row.get("is_ac", 0)),
                    bus_capacity=route_caps.get(r_id, 65)
                ))

        # Stops
        metro_hubs = {"ST_AV01", "ST_AV05", "ST_AV08", "ST_AV10", "ST_AV18", "ST_AV25", "ST_NG02", "ST_NG10", "ST_ND01", "ST_OD03"}
        stops_file = os.path.join(gtfs_dir, "stops.txt")
        if os.path.exists(stops_file):
            df_stops = pd.read_csv(stops_file)
            for _, row in df_stops.iterrows():
                s_id = str(row["stop_id"])
                db.add(StopModel(
                    stop_id=s_id,
                    stop_name=str(row["stop_name"]),
                    stop_lat=float(row["stop_lat"]),
                    stop_lon=float(row["stop_lon"]),
                    zone_id=str(row.get("zone_id", "DELHI_NCT")),
                    is_metro_hub=(s_id in metro_hubs)
                ))

        # Trips
        trips_file = os.path.join(gtfs_dir, "trips.txt")
        if os.path.exists(trips_file):
            df_trips = pd.read_csv(trips_file)
            for _, row in df_trips.iterrows():
                db.add(TripModel(
                    trip_id=str(row["trip_id"]),
                    route_id=str(row["route_id"]),
                    service_id=str(row.get("service_id", "OCT_2026_ALL")),
                    trip_headsign=str(row.get("trip_headsign", "")),
                    direction_id=int(row.get("direction_id", 0)),
                    shape_id=str(row.get("shape_id", ""))
                ))

        # Stop Times
        st_file = os.path.join(gtfs_dir, "stop_times.txt")
        if os.path.exists(st_file):
            df_st = pd.read_csv(st_file)
            for _, row in df_st.iterrows():
                db.add(StopTimeModel(
                    trip_id=str(row["trip_id"]),
                    stop_id=str(row["stop_id"]),
                    arrival_time=str(row["arrival_time"]),
                    departure_time=str(row["departure_time"]),
                    stop_sequence=int(row["stop_sequence"])
                ))

        db.commit()
        logger.info("GTFS topology committed successfully to database.")

        # Seed analytics stop hourly index from reconstructed dataset if available
        recon_file = os.path.join(settings.PROCESSED_DATA_DIR, "reconstructed_segment_crowd.csv")
        if os.path.exists(recon_file):
            logger.info("Seeding hourly stop index from reconstructed segment crowd data...")
            df_recon = pd.read_csv(recon_file)
            
            # Compute stop hourly aggregates
            agg = df_recon.groupby(["stop_id", "hour", "is_weekend"]).agg(
                avg_boardings=("boardings", "mean"),
                avg_through_load=("in_vehicle_load", "mean"),
                avg_occupancy_ratio=("occupancy_ratio", "mean")
            ).reset_index()

            for _, row in agg.iterrows():
                h = int(row["hour"])
                if (8 <= h <= 10):
                    peak = "MORNING_RUSH"
                elif (17 <= h <= 19):
                    peak = "EVENING_RUSH"
                elif (12 <= h <= 15):
                    peak = "MIDDAY_LULL"
                else:
                    peak = "OFF_PEAK"

                db.add(StopHourlyIndexModel(
                    stop_id=str(row["stop_id"]),
                    hour=h,
                    is_weekend=bool(row["is_weekend"]),
                    avg_boardings=round(float(row["avg_boardings"]), 2),
                    avg_through_load=round(float(row["avg_through_load"]), 2),
                    avg_occupancy_ratio=round(float(row["avg_occupancy_ratio"]), 3),
                    peak_category=peak
                ))
            db.commit()
            logger.info(f"Seeded {len(agg):,} stop hourly index records.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
