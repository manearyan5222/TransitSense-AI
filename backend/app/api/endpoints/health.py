"""
TransitSense AI: Health & Stats Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.gtfs import RouteModel, StopModel, TripModel
from backend.app.services.ml_service import MLService

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Checks database connectivity and active ML model."""
    try:
        route_count = db.query(RouteModel).count()
        db_status = "connected"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    try:
        predictor = MLService.get_predictor()
        ml_status = f"ready ({type(predictor.model).__name__})"
    except Exception as e:
        ml_status = f"unavailable: {e}"

    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": db_status,
        "ml_engine": ml_status
    }


@router.get("/stats")
def network_stats(db: Session = Depends(get_db)):
    """Returns total counts of routes, stops, and scheduled trips."""
    return {
        "active_routes_count": db.query(RouteModel).count(),
        "total_stops_count": db.query(StopModel).count(),
        "total_trips_count": db.query(TripModel).count(),
        "target_city": "Delhi NCT",
        "dataset": "Official Delhi Transport Stack October 2026",
        "ml_algorithm": "XGBoost Regressor + Flow Conservation"
    }
