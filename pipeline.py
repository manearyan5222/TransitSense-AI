"""
TransitSense AI: Cleaned Dataset Pipeline Orchestrator
Delhi Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Data Scientist & Transportation Analytics Specialist
Description:
    End-to-end data pipeline that transforms raw October 2026 Delhi ETM transaction logs
    into leakage-free, flow-reconstructed ML train/val/test feature matrices.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple
from preprocessing import DelhiETMPreprocessor

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DatasetPipeline")


class CleanedDatasetPipeline:
    """
    Orchestrates ingestion, data cleaning, flow reconstruction, feature engineering,
    and anti-leakage temporal block splitting for TransitSense AI.
    """

    def __init__(
        self,
        raw_etm_path: str = "data/raw/delhi_etm_october_2026.csv",
        gtfs_dir: str = "data/gtfs",
        processed_dir: str = "data/processed"
    ):
        self.raw_etm_path = raw_etm_path
        self.gtfs_dir = gtfs_dir
        self.processed_dir = processed_dir
        self.preprocessor = DelhiETMPreprocessor(raw_etm_path, gtfs_dir, processed_dir)

    def run(self) -> Dict[str, str]:
        """Executes the complete pipeline end-to-end."""
        logger.info("==================================================")
        logger.info("STARTING TRANSITSENSE AI CLEANED DATASET PIPELINE")
        logger.info("==================================================")

        # Step 1: Preprocessing & Flow Reconstruction
        self.preprocessor.load_datasets()
        self.preprocessor.clean_transactions()
        df_reconstructed = self.preprocessor.reconstruct_segment_occupancy()
        cleaned_path, segment_path = self.preprocessor.export_processed_datasets()

        # Step 2: Feature Engineering & Encoding
        logger.info("Building ML feature matrix with temporal encodings and spatial lags...")
        df_ml = self._build_ml_features(df_reconstructed)

        # Step 3: Strict Anti-Leakage Temporal Splitting
        logger.info("Performing Time-Series Block Split (No Random K-Fold Leakage)...")
        train_path, val_path, test_path = self._time_series_split(df_ml)

        logger.info("==================================================")
        logger.info("DATASET PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Cleaned ETM Logs:        {cleaned_path}")
        logger.info(f"Reconstructed Segments:  {segment_path}")
        logger.info(f"ML Training Partition:   {train_path}")
        logger.info(f"ML Validation Partition: {val_path}")
        logger.info(f"ML Out-of-Time Test:     {test_path}")
        logger.info("==================================================")

        return {
            "cleaned_etm": cleaned_path,
            "reconstructed_segments": segment_path,
            "train": train_path,
            "val": val_path,
            "test": test_path
        }

    def _build_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineers cyclical temporal features, route progress, and metro hub indicators."""
        df_feat = df.copy()

        # Cyclical Sine/Cosine Hour encoding
        df_feat["hour_sin"] = np.sin(2 * np.pi * df_feat["hour"] / 24.0)
        df_feat["hour_cos"] = np.cos(2 * np.pi * df_feat["hour"] / 24.0)

        # Day of week cyclical encoding
        df_feat["dow_sin"] = np.sin(2 * np.pi * df_feat["day_of_week"] / 7.0)
        df_feat["dow_cos"] = np.cos(2 * np.pi * df_feat["day_of_week"] / 7.0)

        # Delhi Metro Interchanges (Hubs)
        metro_hub_stops = {"ST_AV01", "ST_AV05", "ST_AV08", "ST_AV10", "ST_AV18", "ST_AV25", "ST_NG02", "ST_NG10", "ST_ND01", "ST_OD03"}
        df_feat["is_metro_hub"] = df_feat["stop_id"].isin(metro_hub_stops).astype(int)

        # Route Progress Ratio (sequence normalized by max sequence)
        max_seqs = df_feat.groupby("route_id")["stop_sequence"].transform("max")
        df_feat["route_progress"] = df_feat["stop_sequence"] / max_seqs

        # Route Encoding
        route_encoding = {"DTC_534": 1, "DTC_764": 2, "DTC_502": 3, "DTC_427": 4, "DTC_620": 5}
        df_feat["route_code"] = df_feat["route_id"].map(route_encoding)

        return df_feat

    def _time_series_split(self, df: pd.DataFrame) -> Tuple[str, str, str]:
        """
        Splits data chronologically by date:
        - Train:      Oct 01 - Oct 21 (Days 1–21, ~68% of data)
        - Validation: Oct 22 - Oct 27 (Days 22–27, ~18% of data)
        - Test:       Oct 28 - Oct 31 (Days 28–31, ~14% out-of-time test set)
        """
        df["service_date"] = pd.to_datetime(df["service_date"])
        
        train_mask = df["service_date"] <= "2026-10-21"
        val_mask = (df["service_date"] >= "2026-10-22") & (df["service_date"] <= "2026-10-27")
        test_mask = df["service_date"] >= "2026-10-28"

        df_train = df[train_mask]
        df_val = df[val_mask]
        df_test = df[test_mask]

        logger.info(f"Split sizes: Train={len(df_train):,} ({len(df_train)/len(df)*100:.1f}%), "
                    f"Val={len(df_val):,} ({len(df_val)/len(df)*100:.1f}%), "
                    f"Test={len(df_test):,} ({len(df_test)/len(df)*100:.1f}%)")

        train_path = os.path.join(self.processed_dir, "train_features.csv")
        val_path = os.path.join(self.processed_dir, "val_features.csv")
        test_path = os.path.join(self.processed_dir, "test_features.csv")

        df_train.to_csv(train_path, index=False)
        df_val.to_csv(val_path, index=False)
        df_test.to_csv(test_path, index=False)

        return train_path, val_path, test_path


if __name__ == "__main__":
    pipeline = CleanedDatasetPipeline()
    pipeline.run()
