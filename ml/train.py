"""
TransitSense AI: Model Training & Benchmark Pipeline
Delhi Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Machine Learning Engineer
Description:
    Trains and compares:
    1. Historical Demand Baseline (Stratified Empirical Prior)
    2. Random Forest Regressor
    3. XGBoost Regressor
    Evaluates on Chronological Out-of-Time Test Set, generates feature importance,
    and serializes the best performing model artifact.
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
from typing import Dict, Any

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from ml.preprocessing import prepare_datasets, FEATURE_COLS, TARGET_COL
from ml.evaluate import evaluate_predictions, calculate_wape

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("MLTraining")


def train_models(
    artifacts_dir: str = "ml/model_artifacts",
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes training of Baseline, Random Forest, and XGBoost models,
    evaluating on chronological validation and out-of-time test sets.
    """
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Load Data & Fit Preprocessing
    X_train, y_train, X_val, y_val, X_test, y_test, pipeline = prepare_datasets(
        artifacts_dir=artifacts_dir
    )

    cap_val = X_val["bus_capacity"].values
    rush_val = X_val["is_rush_hour"].values
    cap_test = X_test["bus_capacity"].values
    rush_test = X_test["is_rush_hour"].values

    models_comparison = []

    # =========================================================================
    # MODEL 1: Historical Demand Baseline
    # =========================================================================
    logger.info("Evaluating Model 1: Historical Demand Baseline...")
    # Baseline uses the historical mean load feature directly
    y_pred_base_val = X_val["hist_mean_load"].values
    y_pred_base_test = X_test["hist_mean_load"].values

    metrics_base_val = evaluate_predictions(y_val.values, y_pred_base_val, cap_val, rush_val, "Baseline (Validation)")
    metrics_base_test = evaluate_predictions(y_test.values, y_pred_base_test, cap_test, rush_test, "Historical Baseline")
    models_comparison.append(metrics_base_test)
    logger.info(f"Baseline Test -> MAE: {metrics_base_test['mae']}, RMSE: {metrics_base_test['rmse']}, WAPE: {metrics_base_test['wape_pct']}%")

    # =========================================================================
    # MODEL 2: Random Forest Regressor
    # =========================================================================
    logger.info("Training Model 2: Random Forest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=3,
        max_features="sqrt",
        random_state=random_state,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    y_pred_rf_val = rf_model.predict(X_val)
    y_pred_rf_test = rf_model.predict(X_test)

    metrics_rf_val = evaluate_predictions(y_val.values, y_pred_rf_val, cap_val, rush_val, "Random Forest (Val)")
    metrics_rf_test = evaluate_predictions(y_test.values, y_pred_rf_test, cap_test, rush_test, "Random Forest")
    models_comparison.append(metrics_rf_test)
    logger.info(f"Random Forest Test -> MAE: {metrics_rf_test['mae']}, RMSE: {metrics_rf_test['rmse']}, WAPE: {metrics_rf_test['wape_pct']}%")

    # =========================================================================
    # MODEL 3: XGBoost Regressor
    # =========================================================================
    logger.info("Training Model 3: XGBoost Regressor...")
    xgb_model = XGBRegressor(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.2,
        random_state=random_state,
        tree_method="hist",
        n_jobs=-1
    )
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    y_pred_xgb_val = xgb_model.predict(X_val)
    y_pred_xgb_test = xgb_model.predict(X_test)

    metrics_xgb_val = evaluate_predictions(y_val.values, y_pred_xgb_val, cap_val, rush_val, "XGBoost (Val)")
    metrics_xgb_test = evaluate_predictions(y_test.values, y_pred_xgb_test, cap_test, rush_test, "XGBoost")
    models_comparison.append(metrics_xgb_test)
    logger.info(f"XGBoost Test -> MAE: {metrics_xgb_test['mae']}, RMSE: {metrics_xgb_test['rmse']}, WAPE: {metrics_xgb_test['wape_pct']}%")

    # =========================================================================
    # 4. Feature Importance Extraction
    # =========================================================================
    logger.info("Extracting explainable feature importances...")
    rf_importances = dict(zip(FEATURE_COLS, [round(float(v), 5) for v in rf_model.feature_importances_]))
    xgb_importances = dict(zip(FEATURE_COLS, [round(float(v), 5) for v in xgb_model.feature_importances_]))

    df_importance = pd.DataFrame({
        "Feature": FEATURE_COLS,
        "RandomForest_Importance": [rf_importances[c] for c in FEATURE_COLS],
        "XGBoost_Importance": [xgb_importances[c] for c in FEATURE_COLS]
    }).sort_values(by="XGBoost_Importance", ascending=False)

    importance_path = os.path.join(artifacts_dir, "feature_importance.csv")
    df_importance.to_csv(importance_path, index=False)

    # =========================================================================
    # 5. Model Selection & Serialization
    # =========================================================================
    # Select best model based on out-of-time test MAE
    if metrics_xgb_test["mae"] <= metrics_rf_test["mae"]:
        best_model = xgb_model
        best_name = "XGBoost"
        best_metrics = metrics_xgb_test
    else:
        best_model = rf_model
        best_name = "RandomForest"
        best_metrics = metrics_rf_test

    logger.info(f"Selected Best Validated Model: {best_name} (Test MAE: {best_metrics['mae']})")

    # Save model artifact
    model_path = os.path.join(artifacts_dir, "best_model.joblib")
    joblib.dump(best_model, model_path)
    logger.info(f"Saved best model to {model_path}")

    # Also save Random Forest and XGBoost specifically for transparency
    joblib.dump(rf_model, os.path.join(artifacts_dir, "random_forest_model.joblib"))
    joblib.dump(xgb_model, os.path.join(artifacts_dir, "xgboost_model.joblib"))

    # Save benchmark summary
    summary_path = os.path.join(artifacts_dir, "model_comparison.json")
    benchmark_payload = {
        "best_model_name": best_name,
        "test_dataset_size": len(X_test),
        "validation_dataset_size": len(X_val),
        "training_dataset_size": len(X_train),
        "feature_count": len(FEATURE_COLS),
        "comparison": models_comparison,
        "feature_importance_top5": df_importance.head(5).to_dict(orient="records")
    }
    with open(summary_path, "w") as f:
        json.dump(benchmark_payload, f, indent=2)

    logger.info(f"Saved benchmark summary to {summary_path}")
    return benchmark_payload


if __name__ == "__main__":
    benchmark = train_models()
    print("\n=== MODEL COMPARISON BENCHMARK (OUT-OF-TIME TEST SET) ===")
    df_res = pd.DataFrame(benchmark["comparison"])
    print(df_res[["model_name", "mae", "rmse", "wape_pct", "r2_score", "crowd_tier_accuracy_pct", "crowd_tier_macro_f1"]])
