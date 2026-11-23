"""
TransitSense AI: Machine Learning Feature Engineering & Preprocessing Module
Delhi Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Machine Learning Engineer
Description:
    Transforms reconstructed segment records into leakage-free tabular feature vectors
    for model training and inference. Computes historical empirical lag priors strictly
    from the training partition to prevent temporal data leakage.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict

logger = logging.getLogger("MLPreprocessing")

FEATURE_COLS = [
    "route_code",
    "stop_sequence",
    "route_progress",
    "hour",
    "hour_sin",
    "hour_cos",
    "day_of_week",
    "dow_sin",
    "dow_cos",
    "is_weekend",
    "is_rush_hour",
    "is_metro_hub",
    "bus_capacity",
    "hist_mean_load",
    "hist_p85_load"
]

TARGET_COL = "in_vehicle_load"

ROUTE_ENCODING = {
    "DTC_534": 1,
    "DTC_764": 2,
    "DTC_502": 3,
    "DTC_427": 4,
    "DTC_620": 5
}

METRO_HUBS = {
    "ST_AV01", "ST_AV05", "ST_AV08", "ST_AV10", "ST_AV18",
    "ST_AV25", "ST_NG02", "ST_NG10", "ST_ND01", "ST_OD03"
}


class MLFeaturePipeline:
    """
    Constructs feature matrices for Train, Validation, and Test sets,
    enforcing strict historical boundary rules to prevent temporal leakage.
    """

    def __init__(self, artifacts_dir: str = "ml/model_artifacts"):
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.hist_priors: Dict = {}
        self.global_prior_mean: float = 0.0

    def fit_priors(self, df_train: pd.DataFrame) -> None:
        """
        Computes historical load priors STRICTLY from the training set (Oct 01 - Oct 21).
        No validation or test data is ever exposed during this step.
        """
        logger.info("Computing historical load priors strictly from training partition...")
        self.global_prior_mean = float(df_train[TARGET_COL].mean())

        # Prior 1: Mean load by (route_id, stop_sequence, hour, is_weekend)
        grouped_fine = (
            df_train.groupby(["route_id", "stop_sequence", "hour", "is_weekend"])[TARGET_COL]
            .mean()
            .reset_index()
            .rename(columns={TARGET_COL: "hist_mean_load"})
        )

        # Prior 2: 85th percentile peak load by (route_id, stop_sequence, hour)
        grouped_p85 = (
            df_train.groupby(["route_id", "stop_sequence", "hour"])[TARGET_COL]
            .quantile(0.85)
            .reset_index()
            .rename(columns={TARGET_COL: "hist_p85_load"})
        )

        # Prior 3: Fallback mean by route and hour
        grouped_coarse = (
            df_train.groupby(["route_id", "hour"])[TARGET_COL]
            .mean()
            .reset_index()
            .rename(columns={TARGET_COL: "fallback_route_mean"})
        )

        # Persist priors to disk for production inference
        priors_file = os.path.join(self.artifacts_dir, "historical_priors.csv")
        grouped_fine.to_csv(priors_file, index=False)
        p85_file = os.path.join(self.artifacts_dir, "historical_p85_priors.csv")
        grouped_p85.to_csv(p85_file, index=False)
        coarse_file = os.path.join(self.artifacts_dir, "historical_coarse_priors.csv")
        grouped_coarse.to_csv(coarse_file, index=False)
        
        metadata = {
            "global_prior_mean": round(self.global_prior_mean, 3),
            "feature_columns": FEATURE_COLS,
            "target_column": TARGET_COL,
            "route_encoding": ROUTE_ENCODING,
            "metro_hubs": list(METRO_HUBS)
        }
        with open(os.path.join(self.artifacts_dir, "pipeline_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        self.df_prior_fine = grouped_fine
        self.df_prior_p85 = grouped_p85
        self.df_prior_coarse = grouped_coarse
        logger.info(f"Learned historical priors: Global Mean = {self.global_prior_mean:.2f} passengers.")

    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Enriches a raw or reconstructed dataframe with cyclical time, route features,
        and joins the historical training priors.
        """
        df_out = df.copy()

        # Enforce temporal cyclical features
        if "hour_sin" not in df_out.columns:
            df_out["hour_sin"] = np.sin(2 * np.pi * df_out["hour"] / 24.0)
            df_out["hour_cos"] = np.cos(2 * np.pi * df_out["hour"] / 24.0)
            df_out["dow_sin"] = np.sin(2 * np.pi * df_out["day_of_week"] / 7.0)
            df_out["dow_cos"] = np.cos(2 * np.pi * df_out["day_of_week"] / 7.0)
            df_out["is_rush_hour"] = (
                ((df_out["hour"] >= 8) & (df_out["hour"] <= 10)) |
                ((df_out["hour"] >= 17) & (df_out["hour"] <= 19))
            ).astype(int)

        # Enforce spatial & route features
        if "route_code" not in df_out.columns:
            df_out["route_code"] = df_out["route_id"].map(ROUTE_ENCODING).fillna(0).astype(int)
        
        if "is_metro_hub" not in df_out.columns:
            df_out["is_metro_hub"] = df_out["stop_id"].isin(METRO_HUBS).astype(int)

        if "route_progress" not in df_out.columns:
            max_seqs = df_out.groupby("route_id")["stop_sequence"].transform("max")
            df_out["route_progress"] = df_out["stop_sequence"] / max_seqs

        # Join Historical Training Priors
        df_out = df_out.merge(
            self.df_prior_fine,
            on=["route_id", "stop_sequence", "hour", "is_weekend"],
            how="left"
        )
        df_out = df_out.merge(
            self.df_prior_p85,
            on=["route_id", "stop_sequence", "hour"],
            how="left"
        )
        df_out = df_out.merge(
            self.df_prior_coarse,
            on=["route_id", "hour"],
            how="left"
        )

        # Impute cold-start / unseen cells with hierarchical fallbacks
        df_out["hist_mean_load"] = (
            df_out["hist_mean_load"]
            .fillna(df_out["fallback_route_mean"])
            .fillna(self.global_prior_mean)
        )
        df_out["hist_p85_load"] = (
            df_out["hist_p85_load"]
            .fillna(df_out["hist_mean_load"] * 1.3)
            .fillna(self.global_prior_mean * 1.3)
        )

        X = df_out[FEATURE_COLS].copy()
        y = df_out[TARGET_COL].copy() if TARGET_COL in df_out.columns else None

        return X, y


def prepare_datasets(
    train_path: str = "data/processed/train_features.csv",
    val_path: str = "data/processed/val_features.csv",
    test_path: str = "data/processed/test_features.csv",
    artifacts_dir: str = "ml/model_artifacts"
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, MLFeaturePipeline]:
    """
    Loads chronological train/val/test splits, fits priors strictly on train,
    and returns aligned feature matrices and targets.
    """
    logger.info("Loading chronological datasets...")
    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    logger.info(f"Loaded: Train={len(df_train):,}, Val={len(df_val):,}, Test={len(df_test):,}")

    pipeline = MLFeaturePipeline(artifacts_dir=artifacts_dir)
    pipeline.fit_priors(df_train)

    X_train, y_train = pipeline.transform(df_train)
    X_val, y_val = pipeline.transform(df_val)
    X_test, y_test = pipeline.transform(df_test)

    logger.info(f"Feature matrix ready: {X_train.shape[1]} features across {len(X_train):,} train instances.")
    return X_train, y_train, X_val, y_val, X_test, y_test, pipeline


if __name__ == "__main__":
    X_train, y_train, X_val, y_val, X_test, y_test, pipe = prepare_datasets()
    print("Features:", X_train.columns.tolist())
    print("Sample X_train:")
    print(X_train.head(2))
