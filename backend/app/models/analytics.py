"""
TransitSense AI: Analytics & Historical Crowd SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from backend.app.db.session import Base


class SegmentCrowdModel(Base):
    __tablename__ = "analytics_route_segment_crowd"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(64), nullable=False, index=True)
    stop_sequence = Column(Integer, nullable=False)
    stop_id = Column(String(64), nullable=False, index=True)
    hour = Column(Integer, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, default=False)
    mean_load = Column(Float, nullable=False)
    p85_load = Column(Float, nullable=False)
    occupancy_ratio = Column(Float, nullable=False)
    crowd_tier = Column(Integer, nullable=False)
    crowd_label = Column(String(16), nullable=False)


class StopHourlyIndexModel(Base):
    __tablename__ = "analytics_stop_hourly_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stop_id = Column(String(64), nullable=False, index=True)
    hour = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, default=False)
    avg_boardings = Column(Float, nullable=False)
    avg_through_load = Column(Float, nullable=False)
    avg_occupancy_ratio = Column(Float, nullable=False)
    peak_category = Column(String(32), default="OFF_PEAK")
