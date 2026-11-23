"""
TransitSense AI: Consolidated API Router
"""

from fastapi import APIRouter
from backend.app.api.endpoints import (
    health,
    routes,
    stops,
    journey,
    crowd,
    historical,
    comparison,
    analytics
)

api_router = APIRouter()

# Mount all domain routers
api_router.include_router(health.router)
api_router.include_router(comparison.router)
api_router.include_router(routes.router)
api_router.include_router(stops.router)
api_router.include_router(journey.router)
api_router.include_router(crowd.router)
api_router.include_router(historical.router)
api_router.include_router(analytics.router)
