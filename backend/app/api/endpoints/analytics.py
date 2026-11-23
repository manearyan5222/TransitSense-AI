"""
TransitSense AI: Analytics Dashboard Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.analytics import NetworkOverviewStats
from backend.app.models.gtfs import RouteModel, StopModel, TripModel

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/dashboard", response_model=NetworkOverviewStats)
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """
    Returns high-level network operational and ML benchmark statistics
    for the executive dashboard.
    """
    routes_count = db.query(RouteModel).count()
    stops_count = db.query(StopModel).count()

    return {
        "total_active_routes": routes_count,
        "total_bus_stops": stops_count,
        "october_transactions_analyzed": 84814,
        "fleet_vehicles_tracked": 768,
        "peak_morning_rush": "08:30 - 10:30 AM (Peak: 10,483 tickets/hr)",
        "peak_evening_rush": "17:30 - 19:30 PM (Peak: 8,071 tickets/hr)",
        "active_ml_model": "XGBoost Regressor (15-D Ensembles)",
        "model_mae": 5.1913,
        "model_wape_pct": 19.17
    }
