"""
TransitSense AI: FastAPI Application Entrypoint
Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Python Backend Developer
"""

import os
import sys
import logging
import mimetypes
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".jsx")

from backend.app.config import settings
from backend.app.api.router import api_router
from backend.app.db.init_db import init_database
from backend.app.services.ml_service import MLService
from backend.app.core.exceptions import (
    TransitSenseException,
    transitsense_exception_handler,
    global_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TransitSenseApp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes database and pre-warms ML inference engine."""
    logger.info("Initializing TransitSense AI Backend...")
    # Initialize DB & GTFS tables
    init_database()
    # Pre-warm ML Predictor
    MLService.get_predictor()
    logger.info("TransitSense AI Backend is ready for traffic.")
    yield
    logger.info("TransitSense AI Backend is shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "TransitSense AI: a crowdedness-aware journey-planning prototype demonstrated with "
        "synthetic ETM-style data and a small demo network. Official-data validation is not complete."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(TransitSenseException, transitsense_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Mount API Routers under /api/v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount Static Files for Web Interface
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
@app.get("/app", include_in_schema=False)
def serve_spa():
    """Serves the TransitSense AI interactive dashboard application."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
