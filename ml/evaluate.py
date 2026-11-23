"""
TransitSense AI: Machine Learning Evaluation Module
Delhi Transport Stack Hackathon 2026 - Problem 2: Crowdedness-Aware Journey Planner

Author: Senior Machine Learning Engineer
Description:
    Computes rigorous transit-domain regression and classification metrics:
    MAE, RMSE, WAPE (Weighted Absolute Percentage Error), R2, and Peak-Hour Error.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, f1_score, accuracy_score


def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes Weighted Absolute Percentage Error (WAPE):
        WAPE = sum(|y_true - y_pred|) / sum(y_true) * 100%
    Avoids zero-division pitfalls of standard MAPE in transit demand.
    """
    total_actual = np.sum(y_true)
    if total_actual == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_actual * 100.0)


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    bus_capacity: np.ndarray = None,
    is_rush_hour: np.ndarray = None,
    model_name: str = "Model"
) -> Dict[str, Any]:
    """
    Evaluates passenger demand predictions across standard and transit-specific metrics.
    """
    # Enforce non-negativity
    y_pred_clipped = np.clip(y_pred, 0, None)

    mae = float(mean_absolute_error(y_true, y_pred_clipped))
    mse = float(mean_squared_error(y_true, y_pred_clipped))
    rmse = float(np.sqrt(mse))
    wape = calculate_wape(y_true, y_pred_clipped)
    r2 = float(r2_score(y_true, y_pred_clipped))

    results = {
        "model_name": model_name,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "wape_pct": round(wape, 2),
        "r2_score": round(r2, 4)
    }

    # Peak hour evaluation if indicator provided
    if is_rush_hour is not None:
        rush_mask = np.array(is_rush_hour) == 1
        if np.sum(rush_mask) > 0:
            rush_mae = float(mean_absolute_error(y_true[rush_mask], y_pred_clipped[rush_mask]))
            rush_wape = calculate_wape(y_true[rush_mask], y_pred_clipped[rush_mask])
            results["peak_hour_mae"] = round(rush_mae, 4)
            results["peak_hour_wape_pct"] = round(rush_wape, 2)

    # Crowd Tier Classification Accuracy if bus capacity is provided
    if bus_capacity is not None:
        # Occupancy Ratio
        cap = np.where(bus_capacity <= 0, 65, bus_capacity)
        true_ratio = y_true / cap
        pred_ratio = y_pred_clipped / cap

        # 0: Low (<=0.50), 1: Mod (0.50-0.80), 2: High (0.80-1.00), 3: Crush (>1.00)
        true_tier = np.select(
            [true_ratio <= 0.50, true_ratio <= 0.80, true_ratio <= 1.00],
            [0, 1, 2],
            default=3
        )
        pred_tier = np.select(
            [pred_ratio <= 0.50, pred_ratio <= 0.80, pred_ratio <= 1.00],
            [0, 1, 2],
            default=3
        )

        tier_acc = float(accuracy_score(true_tier, pred_tier)) * 100.0
        tier_macro_f1 = float(f1_score(true_tier, pred_tier, average="macro"))

        # Safety Metric: False-Low (Predicting Low when actual is Crush)
        false_low_mask = (true_tier == 3) & (pred_tier == 0)
        false_low_rate = float(np.sum(false_low_mask) / max(1, np.sum(true_tier == 3))) * 100.0

        results["crowd_tier_accuracy_pct"] = round(tier_acc, 2)
        results["crowd_tier_macro_f1"] = round(tier_macro_f1, 4)
        results["false_low_rate_pct"] = round(false_low_rate, 2)

    return results


def print_comparison_table(metrics_list: list) -> pd.DataFrame:
    """Formats a list of model metric dictionaries into a clean summary DataFrame."""
    df_metrics = pd.DataFrame(metrics_list)
    return df_metrics


if __name__ == "__main__":
    y_dummy_true = np.array([10, 25, 45, 65, 80])
    y_dummy_pred = np.array([12, 22, 48, 60, 85])
    cap = np.array([65, 65, 65, 65, 65])
    metrics = evaluate_predictions(y_dummy_true, y_dummy_pred, bus_capacity=cap, model_name="TestDummy")
    print("Evaluation Module Ready:")
    for k, v in metrics.items():
        print(f"  {k:<25}: {v}")
