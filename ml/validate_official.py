"""
TransitSense AI: Official Data Validation Pipeline
Transport Stack Hackathon 2026 - Problem 2

Author: Principal Data Engineering and ML Validation Lead
Description:
    Dedicated validation pipeline that trains and benchmarks Historical Baseline,
    Random Forest, and XGBoost models exclusively on official Delhi Transport Stack
    data when staged in data/official/.
    
    Guarantees strict chronological splitting, leak-free feature extraction,
    and isolates official evaluation metrics from synthetic benchmark numbers.
"""

import os
import sys
import json
import argparse
import logging
import numpy as np
import pandas as pd
from datetime import datetime

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.provenance.provenance_tracker import ProvenanceTracker
from ml.evaluate import evaluate_predictions
from ml.preprocessing import FEATURE_COLS, TARGET_COL, MLFeaturePipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [OfficialValidation] %(message)s"
)
logger = logging.getLogger("OfficialValidation")


def run_official_validation(
    etm_file: str,
    afc_file: str = "data/official/afc_boarding_alighting.csv",
    gtfs_dir: str = "data/gtfs",
    output_dir: str = "ml/model_artifacts",
    dry_run: bool = False
):
    """
    Executes end-to-end model training, validation, and benchmarking
    on an official Delhi Transport Stack ETM and AFC dataset.
    """
    logger.info("=" * 70)
    logger.info("TRANSITSENSE AI: OFFICIAL DELHI TRANSPORT STACK VALIDATION SUITE")
    logger.info("=" * 70)

    # 1. Provenance & Existence Check
    if not os.path.exists(etm_file):
        logger.warning(f"Official ETM file not found at: {etm_file}")
        logger.info("Current Status: Download the Problem 2 dataset from the hackathon portal if available.")
        logger.info("Expected location: data/official/delhi_etm_official.csv")
        logger.info("Validation scaffold only; inspect schema and complete integration before official evaluation.")
        return {
            "status": "PENDING_OFFICIAL_DATA",
            "expected_file": etm_file,
            "pipeline_ready": False,
            "next_step": "Obtain the official dataset, review its schema, and complete the validation integration."
        }

    # Verify Provenance
    prov = ProvenanceTracker.get_file_provenance(etm_file)
    if prov != "OFFICIAL":
        raise ValueError(
            f"PROVENANCE ERROR: {etm_file} has provenance '{prov}', not OFFICIAL. "
            "Register and verify the downloaded source before official evaluation."
        )

    logger.info(f"Loading official ETM transaction dataset: {etm_file}...")
    df_raw = pd.read_csv(etm_file)
    logger.info(f"Loaded {len(df_raw):,} official transaction records across {len(df_raw.columns)} columns.")

    if afc_file and os.path.exists(afc_file):
        logger.warning("AFC file found, but AFC calibration is not implemented; this run will not use it.")
    else:
        logger.info("AFC dataset not provided; no AFC calibration is implemented in this scaffold.")

    # 2. Schema Validation
    required_cols = [
        "ticket_id", "route_id", "trip_id", "ticket_timestamp",
        "boarding_stop_id", "passenger_count", "fare_amount", "ticket_type"
    ]
    missing_cols = [c for c in required_cols if c not in df_raw.columns]
    if missing_cols:
        raise ValueError(f"Official dataset schema mismatch. Missing required columns: {missing_cols}")

    logger.info("Official schema verified successfully.")

    if dry_run:
        logger.info("Dry-run verification completed. Schema is valid and ready for training.")
        return {"status": "DRY_RUN_PASSED", "records_count": len(df_raw)}

    # 3. Clean and Run Flow Reconstruction with Uncertainty Bounds
    from preprocessing import DelhiETMPreprocessor
    preprocessor = DelhiETMPreprocessor(
        raw_etm_path=etm_file,
        gtfs_dir=gtfs_dir,
        output_dir="data/official/processed"
    )
    preprocessor.load_datasets()
    df_cleaned = preprocessor.clean_transactions()
    df_reconstructed = preprocessor.reconstruct_segment_occupancy()

    # 4. Chronological Splitting (70% Train, 15% Val, 15% Test)
    df_reconstructed["dt"] = pd.to_datetime(df_reconstructed["timestamp"])
    df_reconstructed = df_reconstructed.sort_values("dt").reset_index(drop=True)
    
    n_total = len(df_reconstructed)
    idx_train = int(n_total * 0.70)
    idx_val = int(n_total * 0.85)

    df_train = df_reconstructed.iloc[:idx_train].copy()
    df_val = df_reconstructed.iloc[idx_train:idx_val].copy()
    df_test = df_reconstructed.iloc[idx_val:].copy()

    logger.info(
        f"Chronological Out-of-Time Partitions: Train ({len(df_train):,} segments: {df_train['dt'].min()} to {df_train['dt'].max()}) | "
        f"Val ({len(df_val):,} segments: {df_val['dt'].min()} to {df_val['dt'].max()}) | "
        f"Test ({len(df_test):,} segments: {df_test['dt'].min()} to {df_test['dt'].max()})"
    )

    # 5. Leak-Free Feature Extraction
    pipeline = MLFeaturePipeline(artifacts_dir="data/official/artifacts")
    pipeline.fit_priors(df_train)
    X_train, y_train = pipeline.transform(df_train)
    X_val, y_val = pipeline.transform(df_val)
    X_test, y_test = pipeline.transform(df_test)

    results = []

    # 6. Model 1: Historical Baseline
    logger.info("Evaluating Model 1: Historical Median Baseline on official data...")
    y_pred_base = X_test["hist_mean_load"].values
    metrics_base = evaluate_predictions(
        y_test.values, y_pred_base,
        bus_capacity=df_test["bus_capacity"].values if "bus_capacity" in df_test.columns else None,
        is_rush_hour=df_test["is_rush_hour"].values if "is_rush_hour" in df_test.columns else None,
        model_name="Historical Baseline"
    )
    results.append(metrics_base)

    # 7. Model 2: Random Forest Regressor
    logger.info("Training Model 2: Random Forest Regressor on official data...")
    from sklearn.ensemble import RandomForestRegressor
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    metrics_rf = evaluate_predictions(
        y_test.values, y_pred_rf,
        bus_capacity=df_test["bus_capacity"].values if "bus_capacity" in df_test.columns else None,
        is_rush_hour=df_test["is_rush_hour"].values if "is_rush_hour" in df_test.columns else None,
        model_name="Random Forest"
    )
    results.append(metrics_rf)

    # 8. Model 3: XGBoost Regressor
    logger.info("Training Model 3: XGBoost Regressor on official data...")
    from xgboost import XGBRegressor
    xgb = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.08, subsample=0.85, random_state=42, n_jobs=-1)
    xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    y_pred_xgb = xgb.predict(X_test)
    metrics_xgb = evaluate_predictions(
        y_test.values, y_pred_xgb,
        bus_capacity=df_test["bus_capacity"].values if "bus_capacity" in df_test.columns else None,
        is_rush_hour=df_test["is_rush_hour"].values if "is_rush_hour" in df_test.columns else None,
        model_name="XGBoost"
    )
    results.append(metrics_xgb)

    # 9. Format Report Output
    report = {
        "validation_type": "OFFICIAL_DATA_VALIDATION",
        "provenance": "OFFICIAL",
        "data_source_file": etm_file,
        "evaluation_timestamp": datetime.utcnow().isoformat(),
        "total_official_segments": n_total,
        "train_segments": len(df_train),
        "validation_segments": len(df_val),
        "test_segments": len(df_test),
        "comparison": results
    }

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "official_validation_comparison.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Official validation comparison saved cleanly to {out_file}.")
    logger.info("Completed official model validation.")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TransitSense AI Official Data Validation Pipeline")
    parser.add_argument("--data", "--etm-file", dest="etm_file", default="data/official/delhi_etm_official.csv", help="Path to official raw ETM CSV")
    parser.add_argument("--afc", dest="afc_file", default="data/official/afc_boarding_alighting.csv", help="Path to official AFC boarding/alighting CSV")
    parser.add_argument("--gtfs-dir", default="data/gtfs", help="Path to GTFS directory")
    parser.add_argument("--dry-run", action="store_true", help="Perform schema verification only")
    args = parser.parse_args()

    run_official_validation(args.etm_file, afc_file=args.afc_file, gtfs_dir=args.gtfs_dir, dry_run=args.dry_run)
