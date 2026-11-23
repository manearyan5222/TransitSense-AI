"""
TransitSense AI: Journey Planning Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.journey import JourneyPlanRequest, JourneyPlanResponse
from backend.app.services.journey_planner import JourneyPlannerEngine
from backend.app.core.exceptions import JourneyPlanningException

router = APIRouter(tags=["Journey Planner"])


@router.post("/journey/plan", response_model=JourneyPlanResponse)
def plan_journey(
    req: JourneyPlanRequest,
    db: Session = Depends(get_db)
):
    """
    Executes multi-objective journey planning:
    Uses the configured crowd estimator to compare the 'Fastest Route' and
    a 'Comfort-First Route'. Demo outputs are estimates, not live readings or
    a guarantee of seating.
    """
    try:
        res = JourneyPlannerEngine.plan_journey(
            db=db,
            origin_lat=req.origin.lat,
            origin_lon=req.origin.lon,
            dest_lat=req.destination.lat,
            dest_lon=req.destination.lon,
            departure_time=req.departure_time,
            preference=req.preference,
            max_walk_meters=req.max_walk_meters,
            origin_name=req.origin.name or "Origin",
            dest_name=req.destination.name or "Destination"
        )
        return res
    except Exception as e:
        raise JourneyPlanningException(f"Failed to compute journey plan: {e}")
