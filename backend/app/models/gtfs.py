"""
TransitSense AI: GTFS Topology SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base


class AgencyModel(Base):
    __tablename__ = "gtfs_agencies"

    agency_id = Column(String(32), primary_key=True)
    agency_name = Column(String(128), nullable=False)
    agency_url = Column(String(255))
    agency_timezone = Column(String(64), default="Asia/Kolkata")


class RouteModel(Base):
    __tablename__ = "gtfs_routes"

    route_id = Column(String(64), primary_key=True)
    agency_id = Column(String(32), ForeignKey("gtfs_agencies.agency_id"), nullable=False)
    route_short_name = Column(String(64), nullable=False, index=True)
    route_long_name = Column(String(255), nullable=False)
    route_type = Column(Integer, default=3)
    is_ac = Column(Boolean, default=False)
    bus_capacity = Column(Integer, default=65)


class StopModel(Base):
    __tablename__ = "gtfs_stops"

    stop_id = Column(String(64), primary_key=True)
    stop_name = Column(String(255), nullable=False, index=True)
    stop_lat = Column(Float, nullable=False)
    stop_lon = Column(Float, nullable=False)
    zone_id = Column(String(64), default="DELHI_NCT")
    is_metro_hub = Column(Boolean, default=False)


class TripModel(Base):
    __tablename__ = "gtfs_trips"

    trip_id = Column(String(128), primary_key=True)
    route_id = Column(String(64), ForeignKey("gtfs_routes.route_id"), nullable=False, index=True)
    service_id = Column(String(64), default="OCT_2026_ALL")
    trip_headsign = Column(String(255))
    direction_id = Column(Integer, default=0)
    shape_id = Column(String(64))


class StopTimeModel(Base):
    __tablename__ = "gtfs_stop_times"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(String(128), ForeignKey("gtfs_trips.trip_id"), nullable=False, index=True)
    stop_id = Column(String(64), ForeignKey("gtfs_stops.stop_id"), nullable=False, index=True)
    arrival_time = Column(String(16), nullable=False)
    departure_time = Column(String(16), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
