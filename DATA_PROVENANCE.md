# TransitSense AI: Data Provenance & Lineage Architecture
**Delhi Transport Stack Hackathon 2026 — Problem 2: Crowdedness-Aware Journey Planner**  
**Role:** Principal Data Engineering and ML Validation Lead  
**Standard:** Open Transit Data Provenance Protocol (OTD-PP v1.0)  

---

## 1. Provenance Classification Taxonomy

To ensure complete transparency, avoid false claims, and guarantee that synthetic demonstration artifacts are never misrepresented as real-world validated performance, TransitSense AI enforces a strict three-tier classification taxonomy across all data assets, models, and API responses:

```
                               ┌────────────────────────────────────────────────┐
                               │           TransitSense AI Taxonomy             │
                               └──────────────────────┬─────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────────┐
                    │                                 │                                 │
                    ▼                                 ▼                                 ▼
        ┌───────────────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
        │       OFFICIAL        │         │       SYNTHETIC       │         │        DERIVED        │
        │ Direct from DTC/DIMTS │         │ Statistically modeled │         │ Formed via pipeline   │
        │ or Delhi OTD Portal   │         │ simulation dataset    │         │ from known upstream   │
        └───────────────────────┘         └───────────────────────┘         └───────────────────────┘
```

### 1.1 `OFFICIAL`
- **Definition:** Data originating directly and authoritatively from government transit systems (Delhi Transport Corporation, DIMTS, or the Delhi Open Transit Data portal `otd.delhi.gov.in`) without generative modification.
- **Verification Criteria:** Verifiable source URL, official event release archive, or authoritative cryptographic hash (SHA-256).
- **Current State:** No official ETM/AFC input is staged in this project copy. A path alone does not establish official provenance; record its verifiable source and explicitly register it after review.

### 1.2 `SYNTHETIC`
- **Definition:** Data generated through statistical simulation, heuristic generation, or mathematical sampling designed to replicate the operational schema, diurnal curves, and edge cases of Delhi bus operations.
- **Verification Criteria:** Generated via internal scripts (`scripts/generate_delhi_october_data.py`).
- **Current State:** `data/raw/delhi_etm_october_2026.csv` (84,814 transactions).
- **Mandatory Disclosure:** Must **never** be presented as real commuter logs or real-world model validation.

### 1.3 `DERIVED`
- **Definition:** Data tables, cleaned datasets, feature matrices, or serialized machine learning artifacts produced deterministically by applying a documented pipeline (e.g., Flow Conservation solver, cyclical time transformations, XGBoost training) to an upstream dataset.
- **Lineage Attribution:** Every derived asset must explicitly document whether its parent source was `OFFICIAL` or `SYNTHETIC`.

---

## 2. Complete Asset Provenance Inventory

| Asset Path | Provenance Tier | Upstream Parent Source | Authoritative? | Description & Contents |
| :--- | :---: | :--- | :---: | :--- |
| `data/raw/delhi_etm_october_2026.csv` | `SYNTHETIC` | `scripts/generate_delhi_october_data.py` | ❌ No | 84,814 simulated ETM transaction logs across October 2026. |
| `data/official/` | Empty staging area | None staged | ❌ No | Contains instructions only; no official dataset is present. |
| `data/gtfs/agency.txt` | `DERIVED` | Demo metadata; source not independently verified | ❌ No | Transport authority identifiers and timezone specifications. |
| `data/gtfs/routes.txt` | `DERIVED` | Demo corridor definitions | ❌ No | Route definitions for Routes 534, 764, 427, 502, and 620. |
| `data/gtfs/stops.txt` | `DERIVED` | Small demo stop network; sources not independently verified | ❌ No | 47 physical arterial bus stops across Delhi. |
| `data/gtfs/trips.txt` | `DERIVED` | Operating schedule duty sheets | ❌ No | 28 scheduled round trips across the 5 monitored corridors. |
| `data/gtfs/stop_times.txt` | `DERIVED` | Sequential scheduled arrival/departure times | ❌ No | 724 scheduled stop arrival time records. |
| `data/processed/cleaned_etm_october_2026.csv` | `DERIVED` | `delhi_etm_october_2026.csv` [SYNTHETIC] | ❌ No | 83,743 deduplicated, fare-validated transaction records. |
| `data/processed/reconstructed_segment_crowd.csv` | `DERIVED` | `cleaned_etm_october_2026.csv` [SYNTHETIC] | ❌ No | 18,500 segment occupancy records from Flow Conservation solver. |
| `data/processed/train_features.csv` | `DERIVED` | `reconstructed_segment_crowd.csv` [SYNTHETIC] | ❌ No | 12,500 chronological training rows (Oct 1–21, 2026). |
| `data/processed/val_features.csv` | `DERIVED` | `reconstructed_segment_crowd.csv` [SYNTHETIC] | ❌ No | 3,535 chronological validation rows (Oct 22–26, 2026). |
| `data/processed/test_features.csv` | `DERIVED` | `reconstructed_segment_crowd.csv` [SYNTHETIC] | ❌ No | 2,465 chronological test rows (Oct 27–31, 2026). |
| `ml/model_artifacts/best_model.joblib` | `DERIVED` | `train_features.csv` [SYNTHETIC] | ❌ No | Serialized XGBoost Regressor model artifact (1.13 MB). |
| `ml/model_artifacts/model_comparison.json` | `DERIVED` | `test_features.csv` [SYNTHETIC] | ❌ No | Benchmark metrics evaluated strictly on synthetic test set. |
| `ml/model_artifacts/official_validation_comparison.json` | `DERIVED` | Official ETM data [OFFICIAL] | ✅ Yes | Intended comparison output path; not evidence of an official benchmark. |

---

## 3. Directory Isolation Strategy

To physically prevent synthetic data from mingling with official data:

```
TransitSense-AI/data/
├── official/                   # STRICTLY OFFICIAL: Isolated intake for authentic OTD/DTC dumps
│   ├── README.md               # Staging protocols and checksum guidelines
│   ├── etm_transactions_*.csv  # Official ETM transaction logs
│   └── gtfs_official.zip       # Official full GTFS static archive
│
├── raw/                        # SYNTHETIC STAGING: Simulation files for architecture benchmarking
│   ├── PROVENANCE.json         # Explicit classification badge
│   └── delhi_etm_october_2026.csv
│
├── processed/                  # DERIVED DATASETS: Pipeline transformations
│   ├── PROVENANCE.json         # Lineage metadata
│   ├── cleaned_etm_october_2026.csv
│   └── reconstructed_segment_crowd.csv
│
└── provenance/                 # PROVENANCE GOVERNANCE
    ├── registry.json           # Machine-readable provenance database
    └── provenance_tracker.py   # Guard utilities and validation assertion hooks
```

---

## 4. API & Pipeline Provenance Enforcement

### 4.1 Programmatic Provenance Verification
The validation pipeline (`ml/validate_official.py`) invokes `ProvenanceTracker.assert_provenance()` before executing model training:

```python
from data.provenance.provenance_tracker import ProvenanceTracker

# Rejects synthetic data from entering official validation benchmarks
prov = ProvenanceTracker.get_file_provenance(etm_file)
if prov != "OFFICIAL":
    raise ValueError(
        f"PROVENANCE ERROR: {etm_file} is tagged as SYNTHETIC. "
        "This pipeline only processes verified OFFICIAL datasets to prevent metric confusion."
    )
```

### 4.2 API Response Metadata
Every crowd prediction payload emitted by the backend includes transparent provenance metadata:

```json
{
  "route_id": "DTC_534",
  "stop_sequence": 15,
  "timestamp": "2026-11-21 09:15:00",
  "predicted_passenger_load": 35.1,
  "occupancy_ratio": 0.54,
  "crowd_tier": 1,
  "crowd_label": "MODERATE",
  "seating_probability": 0.74,
  "data_provenance": "SYNTHETIC_DEMONSTRATION",
  "is_live_vehicle_gps": false,
  "model_version": "XGBoost-v1-October2026",
  "scientific_disclosure": "Prediction computed via XGBoost model trained on synthetic October 2026 ETM data."
}
```

---

## 5. Scientific Integrity Commitments

1. **No Metric Conflation:** The benchmark figures ($MAE = 5.19$, $WAPE = 19.17\%$) must always be accompanied by the explicit clarification: *"Evaluated on out-of-time partition of synthetic October 2026 ETM demonstration dataset"*.
2. **No Fake Telemetry:** The application shall never present model predictions as "live bus tracking". The configured feed adapter is unverified; do not describe a feed as official or live until its source and response are independently checked.
3. **Auditable Reproducibility:** Every table, feature set, and model can be reconstructed from scratch using `scripts/generate_delhi_october_data.py`, `preprocessing.py`, and `ml/train.py`.
