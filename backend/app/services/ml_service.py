"""
TransitSense AI: ML Inference Service Wrapper
Integrates the actual trained model from ml/model_artifacts/best_model.joblib
"""

import os
import sys
import logging
from typing import Dict, Any, List
from backend.app.config import settings

# Ensure ml module is importable
if settings.PROJECT_ROOT not in sys.path:
    sys.path.insert(0, settings.PROJECT_ROOT)

from ml.predict import TransitSensePredictor

logger = logging.getLogger("MLService")


class MLService:
    _instance = None
    predictor: TransitSensePredictor = None

    @classmethod
    def get_predictor(cls) -> TransitSensePredictor:
        if cls.predictor is None:
            logger.info("Initializing TransitSensePredictor in backend service...")
            cls.predictor = TransitSensePredictor(artifacts_dir=settings.ML_ARTIFACTS_DIR)
        return cls.predictor


def predict_segment_crowd(
    route_id: str,
    stop_sequence: int,
    timestamp: str,
    stop_id: str = None,
    bus_capacity: int = 65
) -> Dict[str, Any]:
    """Generates a model-based estimate from the synthetic demo training data."""
    predictor = MLService.get_predictor()
    res = predictor.predict_segment(
        route_id=route_id,
        stop_sequence=stop_sequence,
        timestamp=timestamp,
        stop_id=stop_id,
        bus_capacity=bus_capacity
    )
    res["is_live_ml_prediction"] = False
    res["model_version"] = "XGBoost-v1-October2026"
    res["is_live_vehicle_gps"] = False
    res["data_provenance"] = "SYNTHETIC_DEMONSTRATION"
    res["scientific_disclosure"] = "Prediction computed via XGBoost model trained on synthetic October 2026 ETM data."
    return res


def predict_trip_profile(
    route_id: str,
    departure_time: str,
    ordered_stops: List[Dict[str, Any]],
    bus_capacity: int = 65
) -> List[Dict[str, Any]]:
    """Predicts crowdedness across all sequential stops for a scheduled route."""
    predictor = MLService.get_predictor()
    return predictor.predict_trip_profile(
        route_id=route_id,
        departure_time=departure_time,
        ordered_stops=ordered_stops,
        bus_capacity=bus_capacity
    )
