# TransitSense AI 🚌⚡
### AI-Powered Crowdedness-Aware Public Transport Journey Planner for Delhi
**Transport Stack Hackathon 2026 — Problem 2**

---

## 📌 Overview

**TransitSense AI** is an intelligent transit planning platform designed to transform urban commuting across Delhi's National Capital Territory. Built for the **Delhi Transport Stack Hackathon 2026**, TransitSense AI addresses **Problem 2: Crowdedness-aware journey planner**.

Standard transit planners (e.g., Google Maps, generic GTFS routing) optimize strictly for physical travel time or transfer count. For millions of Delhi commuters using the Delhi Transport Corporation (DTC) and DIMTS bus network, however, **physical crowdedness, standing comfort, and the ability to board without facing crush-loads** dictate the real-world commuting experience.

TransitSense AI solves this challenge by ingesting Delhi Transport Stack **Electronic Ticketing Machine (ETM)** transactional data, reconstructing segment-level passenger occupancy via the **Flow Conservation Law**, training high-performance **XGBoost** predictive models, and exposing a multi-objective journey planner that provides explainable trade-offs between the **Fastest Route**, a **Comfort-First (Least Crowded)** route, and an optimal **Balanced** route.

---

## 🌐 Hackathon Resources & Official Data Platform

- **Hackathon Page & Full Problem Briefs:** [https://delhi.transportstack.in/hackathon](https://delhi.transportstack.in/hackathon)
- **Delhi Transport Stack Platform (Sign up, datasets & API keys):** [https://delhi.transportstack.in](https://delhi.transportstack.in)
- **Official Helpdesk:** `transportstack.hackathon@gmail.com`
- **Hackathon catalogue context:** Problem 2 (Phase 1) focuses on crowdedness-aware planning with bus e-ticketing/ETM data and GTFS. AFC boarding/alighting data is listed under Problem 5 (Phase 2). These catalogue datasets are not staged or integrated in this demo.

---

## 🏛️ Phase 1 Submission Deliverables & Technical Reports

| Document | Core Focus |
| :--- | :--- |
| 📑 [**TECHNICAL_NOTE.md**](TECHNICAL_NOTE.md) | Technical note, synthetic benchmark context, and current limitations. |
| 🎬 [**DEMO_SCRIPT.md**](DEMO_SCRIPT.md) | Short live demonstration walkthrough. |
| ✅ [**PHASE1_SUBMISSION_CHECKLIST.md**](PHASE1_SUBMISSION_CHECKLIST.md) | Submission verification checklist. |
| 🔬 [**REAL_DATA_READINESS_REPORT.md**](REAL_DATA_READINESS_REPORT.md) | Audit of the current official-data integration gaps. |
| 🏷️ [**DATA_PROVENANCE.md**](DATA_PROVENANCE.md) | Data lineage and provenance definitions. |
| ⚖️ [**FLOW_CONSERVATION_AUDIT.md**](FLOW_CONSERVATION_AUDIT.md) | Audit of the synthetic demonstration dataset and its derived flow estimates. |
| 📊 [**MODEL_EVALUATION_REPORT.md**](file:///c:/Downloads/TransitSense-AI/MODEL_EVALUATION_REPORT.md) | **ML Benchmark:** XGBoost vs Random Forest vs Baseline on Out-of-Time Test Set. |
| 📓 [**data_analysis.ipynb**](file:///c:/Downloads/TransitSense-AI/data_analysis.ipynb) | **Interactive Notebook:** Visual inspection, hourly demand curves, route shares, and GTFS topology. |
| 🔌 [**API_SPECIFICATION.md**](file:///c:/Downloads/TransitSense-AI/API_SPECIFICATION.md) | Complete OpenAPI REST contracts for FastAPI (`/journey/plan`, `/stops/search`, `/crowd-profile`). |
| 📘 [**ARCHITECTURE.md**](file:///c:/Downloads/TransitSense-AI/ARCHITECTURE.md) | High-level C4 container architecture, data flows, non-functional requirements, component breakdown. |

---

## ⚖️ Scientific Rigor & Data Authenticity Disclosure

In strict adherence to hackathon rules and scientific truth-in-advertising:
- **Synthetic Prototype Dataset:** The demo uses **84,814 simulated ETM transactions**. The generated records and their statistics are not official Delhi ridership data; the included corridor/GTFS files are a small demo network.
- **Model Metrics Context:** XGBoost test metrics (MAE 5.19 pax, WAPE 19.17%, $R^2$ 0.9099, 0.00% False-Low rate) demonstrate pipeline convergence and multi-tier routing feasibility on this calibrated benchmark. They must not be cited as real-world validated figures until evaluated on unreleased official datasets.
- **Official Data Status:** No official ETM/AFC files or live feed credentials are staged in this copy. `ml/validate_official.py` is an early scaffold, not a drop-in validator: it expects a specific schema, does not integrate AFC, and requires provenance registration.
- **Visible UI Indicator:** The web application features an interactive provenance badge (`🟡 DATA: SYNTHETIC DEMO`) in the header that opens the scientific disclosure modal.

---

## 🚀 Machine Learning Engine (`ml/`)

- [**ml/preprocessing.py**](file:///c:/Downloads/TransitSense-AI/ml/preprocessing.py): Leakage-free feature engineering, cyclical temporal encodings, and historical training priors.
- [**ml/train.py**](file:///c:/Downloads/TransitSense-AI/ml/train.py): Trains Baseline, Random Forest, and XGBoost models; benchmarks on out-of-time test set.
- [**ml/predict.py**](file:///c:/Downloads/TransitSense-AI/ml/predict.py): Sub-10ms real-time inference engine returning predicted load, occupancy ratio, crowd tier, and seating probability.
- [**ml/evaluate.py**](file:///c:/Downloads/TransitSense-AI/ml/evaluate.py): Metrics suite computing MAE, RMSE, WAPE, $R^2$, and peak-hour weighted errors.
- [**ml/validate_official.py**](ml/validate_official.py): Early official-data validation scaffold; schema normalization and AFC integration remain to be built.
- [**ml/model_artifacts/**](file:///c:/Downloads/TransitSense-AI/ml/model_artifacts/): Serialized model binaries (`best_model.joblib`), feature importances, and historical priors.

---

## ⚖️ Model Benchmark Summary (Out-of-Time Test Set: Oct 28–31, 2026)

| Model | Test MAE | Test RMSE | Test WAPE | $R^2$ Score | Tier Accuracy | False-Low Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Historical Baseline Prior** | 5.29 pass. | 7.68 | 19.55% | 0.9000 | 84.22% | 0.00% |
| **Random Forest (100 Trees)** | 5.21 pass. | **7.27** | 19.22% | **0.9103** | **85.19%** | 0.00% |
| **XGBoost (Best Selected)** | **5.19 pass.** | 7.29 | **19.17%** | 0.9099 | 84.99% | **0.00%** |

*Critical Safety Metric:* The **False-Low Rate** (predicting LOW or MODERATE crowd when actual occupancy is CRUSH >100%) is strictly **0.00%**, preventing commuters from being misdirected into severely overcrowded vehicles.

---

## 💻 Full-Stack Application & Quickstart

### 1. Launch FastAPI Backend & Frontend UI
The full application runs on FastAPI with a pre-warmed ML inference engine and static UI serving:

```bash
# Run backend and interactive web app on port 8000
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive Web App (7 Modules):** Open `http://localhost:8000/` or `http://localhost:8000/app`
- **Interactive Swagger Documentation:** Open `http://localhost:8000/docs`

### 2. Frontend Platform Pages
The prototype includes seven interface modules backed by demo data; they are not production services:
1. **Overview / Landing Page:** Live corridor status pulse cards, KPI metrics (84,814 transactions), flow conservation and Pink Ticket methodology highlights.
2. **Journey Planner:** Origin and destination stop selection, departure time picker, multi-objective preference toggles (**Fastest**, **Comfort-First / Least Crowded**, **Balanced**), explainable AI route recommendation banner, seating probability meter, step-by-step intermediate stop breakdown, and responsive embedded Leaflet route map.
3. **Route Comparison:** Direct side-by-side evaluation of competing routes along shared corridors (e.g. Route 534 vs 429) with AI comfort advantage explanations.
4. **Crowd Intelligence Dashboard:** Diurnal 24-hour stop-by-stop passenger occupancy curves (Chart.js) with bus capacity and seated thresholds.
5. **Interactive Delhi Map:** Full-bleed dark-themed Leaflet map with city-wide corridor GeoJSON heatmaps color-coded by crowd tier (🟢 Low, 🟡 Moderate, 🟠 High, 🔴 Crush), time-of-day slider, and weekend toggles.
6. **What-If Journey Simulator:** Interactive sandbox to evaluate time shifts (±15m, ±30m, ±45m), fleet capacity switches (Standard 65-cap vs AC Electric 46-cap), and demand surge events (+25% rain, +50% metro disruption).
7. **Analytics Dashboard:** Executive telemetry from October 2026 ETM data, 24-hour stop historical curves, ML benchmark comparisons against baselines, and explicit data provenance disclosure.

### 3. Run Backend Test Suite
```bash
python -m pytest backend/tests/ -v
# 23/23 unit and integration tests passing
```
