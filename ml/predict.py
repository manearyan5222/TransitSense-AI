"""
TransitSense AI: Production Inference Engine
Delhi Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Machine Learning Engineer
Description:
    Exposes sub-10ms vectorized inference for predicting segment-level passenger demand,
    occupancy ratios, crowdedness tiers, and seating probabilities for any route and time.
"""

import os
import sys
import json
import joblib
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Union

from ml.preprocessing import (
    FEATURE_COLS, TARGET_COL, ROUTE_ENCODING, METRO_HUBS
)

logger = logging.getLogger("MLPredictor")


class TransitSensePredictor:
    """
    Production-grade inference service for TransitSense AI.
    Loads trained model and historical priors for real-time journey planning evaluation.
    """

    def __init__(self, artifacts_dir: str = "ml/model_artifacts"):
        self.artifacts_dir = artifacts_dir
        self.model = None
        self.metadata = {}
        self.df_priors = None
        self.df_p85 = None
        self.df_coarse = None
        self.global_prior_mean = 28.5
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Loads serialized model artifact, priors, and metadata."""
        model_path = os.path.join(self.artifacts_dir, "best_model.joblib")
        metadata_path = os.path.join(self.artifacts_dir, "pipeline_metadata.json")
        priors_path = os.path.join(self.artifacts_dir, "historical_priors.csv")
        p85_path = os.path.join(self.artifacts_dir, "historical_p85_priors.csv")
        coarse_path = os.path.join(self.artifacts_dir, "historical_coarse_priors.csv")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model artifact not found at {model_path}. Please run ml/train.py first.")

        self.model = joblib.load(model_path)
        
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)
                self.global_prior_mean = self.metadata.get("global_prior_mean", 28.5)

        if os.path.exists(priors_path):
            self.df_priors = pd.read_csv(priors_path)
        if os.path.exists(p85_path):
            self.df_p85 = pd.read_csv(p85_path)
        if os.path.exists(coarse_path):
            self.df_coarse = pd.read_csv(coarse_path)

        logger.info(f"Loaded TransitSensePredictor ({type(self.model).__name__}) successfully.")

    def predict_segment(
        self,
        route_id: str,
        stop_sequence: int,
        timestamp: Union[str, datetime],
        stop_id: str = None,
        bus_capacity: int = 65,
        total_trip_stops: int = 26
    ) -> Dict[str, Any]:
        """
        Predicts passenger demand and crowdedness tier for a single segment at a specific time.
        """
        if isinstance(timestamp, str):
            dt = pd.to_datetime(timestamp)
        else:
            dt = timestamp

        hour = dt.hour
        day_of_week = dt.day_of_week
        is_weekend = int(day_of_week >= 5)

        # Build single row DataFrame
        row_dict = {
            "route_id": route_id,
            "route_code": ROUTE_ENCODING.get(route_id, 1),
            "stop_sequence": stop_sequence,
            "route_progress": stop_sequence / max(1, total_trip_stops),
            "hour": hour,
            "hour_sin": np.sin(2 * np.pi * hour / 24.0),
            "hour_cos": np.cos(2 * np.pi * hour / 24.0),
            "day_of_week": day_of_week,
            "dow_sin": np.sin(2 * np.pi * day_of_week / 7.0),
            "dow_cos": np.cos(2 * np.pi * day_of_week / 7.0),
            "is_weekend": is_weekend,
            "is_rush_hour": int(((hour >= 8) and (hour <= 10)) or ((hour >= 17) and (hour <= 19))),
            "is_metro_hub": int(stop_id in METRO_HUBS if stop_id else 0),
            "bus_capacity": bus_capacity
        }
        df_query = pd.DataFrame([row_dict])

        # Join priors
        if self.df_priors is not None:
            df_query = df_query.merge(
                self.df_priors,
                on=["route_id", "stop_sequence", "hour", "is_weekend"],
                how="left"
            )
        else:
            df_query["hist_mean_load"] = self.global_prior_mean

        if self.df_p85 is not None:
            df_query = df_query.merge(
                self.df_p85,
                on=["route_id", "stop_sequence", "hour"],
                how="left"
            )
        else:
            df_query["hist_p85_load"] = self.global_prior_mean * 1.3

        if self.df_coarse is not None:
            df_query = df_query.merge(
                self.df_coarse,
                on=["route_id", "hour"],
                how="left"
            )
        else:
            df_query["fallback_route_mean"] = self.global_prior_mean

        # Impute missing priors
        df_query["hist_mean_load"] = (
            df_query["hist_mean_load"]
            .fillna(df_query.get("fallback_route_mean", self.global_prior_mean))
            .fillna(self.global_prior_mean)
        )
        df_query["hist_p85_load"] = (
            df_query["hist_p85_load"]
            .fillna(df_query["hist_mean_load"] * 1.3)
            .fillna(self.global_prior_mean * 1.3)
        )

        X_input = df_query[FEATURE_COLS]
        pred_load = float(self.model.predict(X_input)[0])
        pred_load = max(0.0, round(pred_load, 1))

        occupancy_ratio = round(pred_load / max(1, bus_capacity), 3)

        # Determine Crowdedness Tier
        if occupancy_ratio <= 0.50:
            crowd_tier = 0
            crowd_label = "LOW"
            color = "#10B981"
            seating_prob = round(max(0.80, 1.0 - (occupancy_ratio * 0.4)), 2)
            desc = "Seats readily available; high seating probability."
        elif occupancy_ratio <= 0.80:
            crowd_tier = 1
            crowd_label = "MODERATE"
            color = "#F59E0B"
            seating_prob = round(max(0.35, 0.80 - ((occupancy_ratio - 0.50) * 1.5)), 2)
            desc = "Few seats available; comfortable standing room with clear aisles."
        elif occupancy_ratio <= 1.00:
            crowd_tier = 2
            crowd_label = "HIGH"
            color = "#F97316"
            seating_prob = round(max(0.05, 0.35 - ((occupancy_ratio - 0.80) * 1.5)), 2)
            desc = "All seats occupied; standing room only; dense boarding."
        else:
            crowd_tier = 3
            crowd_label = "CRUSH"
            color = "#EF4444"
            seating_prob = 0.02
            desc = "Crush load; severe overcrowding; boarding may be delayed."

        return {
            "route_id": route_id,
            "stop_sequence": stop_sequence,
            "timestamp": str(dt),
            "predicted_passenger_load": pred_load,
            "bus_capacity": bus_capacity,
            "occupancy_ratio": occupancy_ratio,
            "crowd_tier": crowd_tier,
            "crowd_label": crowd_label,
            "color_code": color,
            "seating_probability": seating_prob,
            "explanation": desc
        }

    def predict_trip_profile(
        self,
        route_id: str,
        departure_time: Union[str, datetime],
        ordered_stops: List[Dict[str, Any]],
        bus_capacity: int = 65
    ) -> List[Dict[str, Any]]:
        """
        Generates segment-level crowd predictions for an entire trip across all sequential stops.
        Used directly by the Journey Planner and Leaflet map polylines.
        """
        if isinstance(departure_time, str):
            cur_time = pd.to_datetime(departure_time)
        else:
            cur_time = departure_time

        trip_profile = []
        total_stops = len(ordered_stops)

        for idx, stop in enumerate(ordered_stops):
            stop_seq = stop.get("stop_sequence", idx + 1)
            stop_id = stop.get("stop_id", f"STOP_{stop_seq}")
            stop_name = stop.get("stop_name", f"Stage {stop_seq}")
            
            # Advance time by ~2.5 mins per stop
            step_time = cur_time + pd.Timedelta(minutes=idx * 2.5)

            pred = self.predict_segment(
                route_id=route_id,
                stop_sequence=stop_seq,
                timestamp=step_time,
                stop_id=stop_id,
                bus_capacity=bus_capacity,
                total_trip_stops=total_stops
            )
            pred["stop_name"] = stop_name
            trip_profile.append(pred)

        return trip_profile


if __name__ == "__main__":
    predictor = TransitSensePredictor()
    # Test morning rush segment on Route 534
    res_morning = predictor.predict_segment(
        route_id="DTC_534",
        stop_sequence=15,
        timestamp="2026-11-21 09:15:00",
        stop_id="ST_AV15",
        bus_capacity=65
    )
    print("Inference Test 1 (Route 534 @ Morning Rush 09:15):")
    print(json.dumps(res_morning, indent=2))

    # Test afternoon off-peak segment on Route 534
    res_afternoon = predictor.predict_segment(
        route_id="DTC_534",
        stop_sequence=15,
        timestamp="2026-11-21 14:30:00",
        stop_id="ST_AV15",
        bus_capacity=65
    )
    print("\nInference Test 2 (Route 534 @ Afternoon Lull 14:30):")
    print(json.dumps(res_afternoon, indent=2))
