"""
TransitSense AI: Application Configuration
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "TransitSense AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database URL: Supports PostgreSQL (e.g. postgresql://user:pass@localhost:5432/transitsense)
    # with automatic SQLite fallback for lightweight local dev/testing
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./transitsense.db")
    
    # Path configs
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    GTFS_DIR: str = os.getenv("GTFS_DIR", os.path.join(PROJECT_ROOT, "data", "gtfs"))
    ML_ARTIFACTS_DIR: str = os.getenv("ML_ARTIFACTS_DIR", os.path.join(PROJECT_ROOT, "ml", "model_artifacts"))
    PROCESSED_DATA_DIR: str = os.getenv("PROCESSED_DATA_DIR", os.path.join(PROJECT_ROOT, "data", "processed"))
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Server configs
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))


settings = Settings()
