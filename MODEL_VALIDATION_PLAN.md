# TransitSense AI: Official Model Validation Plan
**Delhi Transport Stack Hackathon 2026 — Problem 2: Crowdedness-Aware Journey Planner**  
**Role:** Principal Data Engineering and ML Validation Lead  
**Scope:** Machine Learning Verification Protocol for Official Government Datasets  

---

## 1. Objective & Scientific Integrity Mandate

The TransitSense AI crowd prediction engine is engineered to forecast segment-level passenger occupancy along Delhi bus corridors. This document defines the **formal verification and benchmarking protocol** to be executed as soon as authentic Delhi Transport Stack ETM and GTFS records are loaded into `data/official/`.

### ⚠️ Non-Negotiable Integrity Protocol:
1. **Decoupling of Metrics:** The preliminary benchmark metrics obtained on synthetic demonstration data (**MAE: 5.19, WAPE: 19.17%**) must remain strictly quarantined in `ml/model_artifacts/model_comparison.json`. They must **never** be cited or merged with official data metrics.
2. **Dedicated Output Channel:** Official evaluation results must be written exclusively to `ml/model_artifacts/official_validation_comparison.json`.
3. **Reproducibility Guarantee:** Any technical auditor or hackathon judge must be able to reproduce the full official benchmark with a single terminal command:
   ```bash
   python ml/validate_official.py --etm-file data/official/etm_transactions_october_2026_official.csv
   ```

---

## 2. Chronological Train-Validation-Test Splitting

In temporal transit systems, random k-fold cross-validation is **strictly prohibited** because it creates severe lookahead data leakage (e.g., using evening rush hour patterns to predict morning rush hour loads on the same date). 

TransitSense AI enforces a strict **chronological out-of-time partition**:

```
 ◄───────────────────────── Chronological Calendar Month ────────────────────────►
 ┌───────────────────────────────────────┬───────────────────┬───────────────────┐
 │               TRAIN                   │    VALIDATION     │       TEST        │
 │           Days 01 to 21               │   Days 22 to 26   │   Days 27 to 31   │
 │           (~70% Volume)               │   (~15% Volume)   │   (~15% Volume)   │
 └───────────────────────────────────────┴───────────────────┴───────────────────┘
   ▲                                       ▲                   ▲
   │ Compute Historical Priors             │ Hyperparameter    │ Final Locked
   │ (hist_mean_load, hist_p85_load)       │ Early Stopping    │ Out-of-Time Eval
```

### Partitioning Rules:
- **Historical Priors Isolation:** Lag features (`hist_mean_load`, `hist_p85_load`) must be computed **strictly from the Training window (Days 01–21)**. 
- **Zero Future Exposure:** Under no circumstances may transactions from Days 22–31 be included when computing historical route-stop-hour priors.
- **Unseen Stop Combinations:** Any stop-hour combinations appearing in the test set that were unobserved in the training window must gracefully fall back to coarse route-level priors.

---

## 3. Evaluation Metric Definitions

To provide a 360-degree assessment of passenger volume regression and safety-critical crowdedness classification, models are evaluated across 8 metrics:

### 3.1 Mean Absolute Error (MAE)
Measures the average absolute deviation in passengers per segment:
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$
- *Target for Official Data:* $\le 6.5$ passengers on a 65-capacity bus.

### 3.2 Root Mean Squared Error (RMSE)
Penalizes large outlier estimation errors:
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$

### 3.3 Weighted Absolute Percentage Error (WAPE)
Standard Mean Absolute Percentage Error (MAPE) divides by $y_i$, exploding to infinity when in-vehicle load is near zero (e.g. early morning runs). TransitSense AI mandates **WAPE**:
$$\text{WAPE} = \frac{\sum_{i=1}^{N} |y_i - \hat{y}_i|}{\sum_{i=1}^{N} y_i} \times 100\%$$
- *Target for Official Data:* $\le 22.0\%$.

### 3.4 Coefficient of Determination ($R^2$)
Measures the proportion of passenger load variance explained by the model:
$$R^2 = 1 - \frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{N} (y_i - \bar{y})^2}$$

### 3.5 Peak-Hour MAE and Peak-Hour WAPE
Evaluates performance strictly during high-stakes morning and evening rush hour corridors:
- **Morning Peak:** 08:30 – 10:30 AM
- **Evening Peak:** 17:30 – 19:30 PM

### 3.6 Crowd-Tier Classification Accuracy & Macro $F_1$
Every continuous prediction $\hat{y}_i$ is converted to a discrete operational crowd tier:
- **Tier 0 (Low):** $\text{Load} \le 50\%$ vehicle capacity
- **Tier 1 (Moderate):** $51\% - 80\%$ vehicle capacity
- **Tier 2 (High):** $81\% - 100\%$ vehicle capacity
- **Tier 3 (Crush):** $> 100\%$ nominal capacity

Because transit crowding is naturally imbalanced (off-peak hours outnumber peak hours), standard accuracy is supplemented by **Macro $F_1$**:
$$\text{Macro } F_1 = \frac{1}{4} \sum_{k=0}^{3} F_{1, k}$$

### 3.7 False-Low Safety Rate (Critical Safety Metric)
The most dangerous failure mode for a journey planner is recommending an overcrowded bus to a commuter by falsely classifying a **Crush load (Tier 3)** as a **Low crowd (Tier 0)**:
$$\text{False-Low Rate} = \frac{\sum \mathbb{I}(y_{\text{true}} = 3 \land \hat{y}_{\text{pred}} = 0)}{\sum \mathbb{I}(y_{\text{true}} = 3)} \times 100\%$$
- **Safety Mandate:** $\text{False-Low Rate} \equiv 0.00\%$. Any model producing non-zero False-Low classifications fails safety qualification.

---

## 4. Competitive Model Benchmarking Suite

The validation pipeline benchmarks three distinct model architectures against the exact same out-of-time test set:

```
                               ┌────────────────────────────────────────────────┐
                               │           Tri-Model Benchmark Suite            │
                               └──────────────────────┬─────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
                    ▼                                 ▼                                 ▼
        ┌───────────────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
        │  Historical Baseline  │         │     Random Forest     │         │   XGBoost Regressor   │
        │ Route-Stop-Hour Mean  │         │ 100 Trees, Depth 12   │         │ 100 Trees, Depth 6    │
        │ Zero Parameters       │         │ Non-linear Bagging    │         │ Gradient Boosted 15-D │
        └───────────────────────┘         └───────────────────────┘         └───────────────────────┘
```

### 4.1 Historical Median Baseline
- **Mechanism:** Lookup table of median historical passenger load grouped by `(route_id, stop_sequence, hour, is_weekend)` learned from the training set.
- **Role:** Demonstrates minimum acceptable heuristic accuracy without machine learning.

### 4.2 Random Forest Regressor
- **Hyperparameters:** `n_estimators=100`, `max_depth=12`, `min_samples_split=5`, `random_state=42`, `n_jobs=-1`.
- **Role:** Robust non-parametric bagging baseline capable of capturing non-linear corridor interactions.

### 4.3 XGBoost Regressor (Champion Candidate)
- **Hyperparameters:** `n_estimators=100`, `max_depth=6`, `learning_rate=0.08`, `subsample=0.85`, `colsample_bytree=0.85`, `reg_alpha=0.1`, `reg_lambda=1.0`.
- **Validation Stopping:** Monitored against validation set with early stopping patience of 10 rounds on validation WAPE.

---

## 5. Execution Protocol & Verification Harness

### 5.1 Verification Workflow
1. Place official raw ETM export in `data/official/etm_transactions_october_2026_official.csv`.
2. Run schema verification in dry-run mode:
   ```bash
   python ml/validate_official.py --dry-run
   ```
3. Run full validation benchmark:
   ```bash
   python ml/validate_official.py
   ```
4. Output payload generated at:
   `ml/model_artifacts/official_validation_comparison.json`

### 5.2 Success Criteria for Official Deployment
To promote an official-data model to production serving:
1. **Error Reduction:** $\text{WAPE}(\text{XGBoost}) \le \text{WAPE}(\text{Baseline}) - 3.0\%$.
2. **Safety Bound:** $\text{False-Low Rate} = 0.00\%$.
3. **Inference Latency:** Sub-10ms latency per 25-stop trip profile.
4. **Referential Integrity:** 100% stop sequence referential integrity against static GTFS stops.
