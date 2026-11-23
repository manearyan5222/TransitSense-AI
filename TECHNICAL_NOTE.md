# TransitSense AI: Technical Note
## Multi-Objective Crowdedness-Aware Journey Planning & Real-Data Readiness Architecture
**Transport Stack Hackathon 2026 — Problem Statement 2**  
*Phase 1 Submission Technical Note | Author: TransitSense AI Engineering Team*

---

## 1. Executive Summary

Urban public transit journey planners (e.g., standard GTFS engines, Google Maps) traditionally optimize for a single objective: **minimum physical travel time** or **minimum transfer count**. In mega-cities like Delhi, however, passenger experience on the bus network (Delhi Transport Corporation [DTC] and DIMTS) is heavily governed by **physical crowdedness, standing discomfort, and boarding feasibility**. A commuter often prefers a route that takes 6 minutes longer if it offers a 70% probability of finding a seat rather than enduring a crush-load standing journey.

**TransitSense AI** is an end-to-end mobility intelligence platform that solves Problem Statement 2 of the Transport Stack Hackathon 2026. It integrates:
1. **Passenger Load Reconstruction:** Reconstructing bus segment occupancy from electronic ticketing machine (ETM) logs via the Flow Conservation Law.
2. **Predictive Machine Learning Engine:** Sub-10ms inference using an optimized XGBoost Regressor benchmarked against Random Forest and a Historical Prior Baseline.
3. **Multi-Objective Journey Planner:** A multi-criteria routing algorithm using a **Generalized Transit Impedance Cost Function** that balances in-vehicle travel time against predicted crowd discomfort, generating distinct **Fastest**, **Comfort-First**, and **Balanced** itineraries.
4. **Transparent Data Provenance & Real-Data Readiness:** A formal lineage tracking architecture (`OFFICIAL`, `SYNTHETIC`, `DERIVED`) and a preliminary scaffold for future official data validation.

---

## 2. Ticketing Data Realities & Flow Conservation Formulation

### 2.1 ETM Data Characteristics & Inherent Limitations
In the Delhi bus transit network, conductors use handheld Electronic Ticketing Machines (ETMs) to issue tickets upon passenger boarding. The raw transaction stream contains transaction timestamps, machine IDs, fare categories, passenger counts, and boarding stages. However, real-world ETM logs have structural characteristics that must be scientifically accounted for:

1. **Boarding-Only Information (Missing Alightings):**
   - In flat-fare and distance-tiered bus systems where exit validation (tap-out) is not enforced, passengers do not scan tickets upon exit.
   - The synthetic demonstration audit reports **44.98%** missing alighting values in its generated records. This is not a measured statistic from official Delhi data.
2. **Zero-Fare Pink Passes (Ridership Invisibility):**
   - Under GNCTD policy, female passengers travel free using Single-Journey Pink Passes.
   - The synthetic demonstration generator assigns Pink Pass categories; its 37.88% ticket share is a simulation parameter, not an official ridership measurement.
3. **Transaction Timestamp Latency:**
   - ETM tickets are printed sequentially as the conductor walks through the aisle. A transaction timestamp reflects the ticket issuance moment, which may lag the physical bus stop departure by 1 to 4 minutes.
4. **Boundary and Off-Peak Truncation:**
   - Raw transaction totals cannot simply be summed as bus occupancy without adjusting for passenger exit dynamics.

### 2.2 Passenger Load Reconstruction (Flow Conservation Law)
To reconstruct the true passenger load $L_{r,s}$ on route $r$ at stop sequence $s$, TransitSense AI applies the discrete **Flow Conservation Law**:

$$L_{r, s} = \max\left(0, \min\left(C_{\text{bus}}, L_{r, s-1} + B_{r, s} - A_{r, s}\right)\right)$$

Where:
- $L_{r, s}$: In-vehicle passenger load on segment leaving stop $s$.
- $L_{r, 0} = 0$: Initial condition at terminal departure.
- $B_{r, s}$: Observed boardings at stop $s$ (including full fare, discounted, and Pink Passes).
- $A_{r, s}$: Estimated alightings at stop $s$.
- $C_{\text{bus}}$: Physical vehicle capacity limit (65 passengers for Standard CNG, 46 for Low-Floor AC Electric).

#### Alighting Estimation Protocol
When alighting stops are missing, the current synthetic pipeline uses a heuristic distribution over later stops:
1. **Trip-Length Decay Heuristic:**
   $$P(\text{Alight at } s \mid \text{Boarded at } b) = \frac{\exp(-\beta \cdot d(b, s))}{\sum_{k > b}^{S} \exp(-\beta \cdot d(b, k))}$$
   Where $d(b, s)$ is the transit distance between stops and $\beta$ is the urban decay parameter ($\beta \approx 0.18\text{ km}^{-1}$).
2. **AFC calibration:** Not implemented. AFC data is listed for Problem 5 (Phase 2) in the hackathon catalogue and is not used by this Problem 2 demo.

Loads are clamped to $[0, C_{\text{bus}}]$ to guarantee that non-physical negative occupancy never occurs.

---

## 3. Machine Learning Architecture & Benchmark

### 3.1 Feature Engineering Pipeline
The ML pipeline extracts 18 predictive features without future data leakage:
- **Temporal Cyclical Signals:** Sine and cosine encodings for time-of-day:
  $$\sin\left(\frac{2\pi \cdot t_{\text{hour}}}{24}\right), \quad \cos\left(\frac{2\pi \cdot t_{\text{hour}}}{24}\right)$$
- **Calendar Indicators:** Day-of-week, `is_weekend`, morning peak (08:00–11:00), evening peak (17:00–20:00).
- **Route Topology:** Stop sequence ratio $\frac{s}{S_{\text{max}}}$, cumulative route distance, inter-stop segment length.
- **Historical Priors:** Moving historical mean occupancy and variance for the given route, stop sequence, and 30-minute time bucket derived strictly from the training period.

### 3.2 Chronological Validation Protocol
To prevent temporal data leakage, records are partitioned strictly by date:
- **Training Set:** October 1 – October 20, 2026 (54,281 records)
- **Validation Set:** October 21 – October 27, 2026 (18,998 records)
- **Out-of-Time Test Set:** October 28 – October 31, 2026 (11,535 records)

### 3.3 Benchmark Evaluation Results
Evaluated on the out-of-time test set:

| Model Architecture | Test MAE | Test RMSE | Test WAPE | $R^2$ Score | Tier Accuracy | False-Low Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Historical Baseline Prior** | 5.29 pax | 7.68 | 19.55% | 0.9000 | 84.22% | 0.00% |
| **Random Forest (100 Trees)** | 5.21 pax | **7.27** | 19.22% | **0.9103** | **85.19%** | 0.00% |
| **XGBoost (Best Selected)** | **5.19 pax** | 7.29 | **$19.17\%$** | 0.9099 | 84.99% | **0.00%** |

*Critical Safety Metric:* The **False-Low Rate** (predicting LOW or MODERATE crowd when actual occupancy is CRUSH >100%) is strictly **0.00%**, preventing commuters from being misdirected into severely overcrowded vehicles.

> [!NOTE]
> **Data Transparency Disclosure:** The benchmark metrics above were computed on 84,814 statistically simulated October 2026 ETM transactions calibrated to Delhi transit patterns. These figures demonstrate model convergence and pipeline stability, not validated real-world performance on unreleased official datasets.

---

## 4. Multi-Objective Crowdedness-Aware Journey Planning Algorithm

### 4.1 Generalized Transit Impedance Cost Function
Standard journey planners evaluate transit legs using physical travel time: $C(e) = t_e$. TransitSense AI formulates a **Generalized Impedance Cost Function** incorporating crowd discomfort:

$$C(e) = t_e \cdot \left(1.0 + \lambda \cdot \Phi(\text{Tier}_e)\right) + \mu \cdot \max(0, \text{OccRatio}_e - 1.0)$$

Where:
- $t_e$: In-vehicle and walking transit time (minutes).
- $\lambda$: Commuter crowd sensitivity coefficient ($\lambda = 0.40$ for balanced routing).
- $\Phi(\text{Tier}_e)$: Discomfort multiplier by crowd tier:
  - $\Phi(\text{LOW}) = 0.00$ (Seated, relaxed)
  - $\Phi(\text{MODERATE}) = 0.25$ (Standing with ample room)
  - $\Phi(\text{HIGH}) = 0.65$ (Dense standing)
  - $\Phi(\text{CRUSH}) = 1.20$ (Crush load >100%, boarding restricted)
- $\mu$: Penalty for severe over-capacity ($>100\%$).

### 4.2 Pareto Frontier & Multi-Criteria Selection
Instead of presenting a single route, TransitSense AI generates distinct candidate itineraries along the Pareto-optimal frontier:
1. **Fastest Choice:** Minimizes $\sum t_e$. Recommended for time-critical travel.
2. **Comfort-First Choice:** Minimizes peak crowd tier and maximizes seating probability:
   $$P(\text{Seat}) = \max\left(0.05, 1.0 - 0.85 \cdot \text{MeanOccRatio}\right)$$
3. **Balanced Choice:** Evaluates impedance trade-offs. If a comfort route adds minimal travel time (+4 minutes) while avoiding a crush-load route, the balanced engine recommends the comfort route and explains the trade-off in plain language.

### 4.3 Explainable Recommendations
Every journey query returns a natural-language `recommendation_explanation` detailing *why* a particular route is suggested:
- *Example (Balanced):* `"Balanced recommendation: Route 534 significantly reduces crowd discomfort (MODERATE vs CRUSH) for only +4 min extra travel time (impedance score: 38.5 vs 49.2)."`
- *Example (Comfort):* `"Recommended for comfort: Route 502 offers lower crowding (LOW) with a 72% seating probability (+38% vs fastest route) for +6 mins additional transit time."`

---

## 5. Real-Data Readiness & Data Provenance Architecture

To maintain absolute scientific integrity and enable instant ingestion of official hackathon data:

### 5.1 Three-Tier Data Provenance System
Every record, API response, and visualization carries an immutable provenance tag:
1. `OFFICIAL`: Sourced directly from verified Delhi Open Transit Data (OTD) portal endpoints or signed hackathon distributions.
2. `SYNTHETIC`: Generated via calibrated statistical simulation based on official DTC schemas.
3. `DERIVED`: Computed via flow conservation, feature extraction, or machine learning inference.

### 5.2 Drop-In Official Validation Runner (`ml/validate_official.py`)
A dedicated validation script is pre-built to evaluate models on official Delhi Transport Stack data:
```bash
python ml/validate_official.py --data data/official/delhi_etm_official.csv --afc data/official/afc_boarding_alighting.csv
```
Before official validation can be claimed, obtain the Problem 2 ETM dataset, verify its origin and schema, register its provenance, then implement and review schema mapping and validation. The optional `--afc` argument currently only warns that AFC calibration is not implemented.

### 5.3 Configurable Feed Adapter (`backend/app/services/otd_client.py`)
The client is an adapter scaffold, not a verified Delhi Transport Stack integration. It uses only explicit URL/key configuration; no official endpoint URL or credentials are shipped. Without them, the app uses synthetic demo positions. A configured response should be independently checked before describing it as an official live feed.

## 6. Verification & Automated Test Suite

TransitSense AI is thoroughly verified with **23 automated unit and integration tests** covering:
- XGBoost crowd inference on morning peak inputs.
- Schema validation and boundary error handling.
- Network crowd heatmaps and corridor profiles.
- Journey planning across `FASTEST`, `COMFORT_FIRST`, and `BALANCED` modes.
- Natural language recommendation explainability.
- Route details, stop searches, and GTFS spatial topology.

```bash
python -m pytest backend/tests/ -v
# 23 passed, 0 failed in 7.12s
```

---

## 7. Limitations & Phase 2 Roadmap

| Current Limitation | Cause | Phase 2 Solution |
| :--- | :--- | :--- |
| **Simulated ETM Data** | The official Problem 2 e-ticketing dataset is not staged in this project copy. | Obtain the official dataset from the hackathon portal, verify its schema and provenance, and complete the validator before reporting real-data results. |
| **Stop-Stage Granularity** | Conductor ETM transactions are recorded per fare stage rather than sub-meter GPS coordinates. | Integrate live GTFS-RT vehicle position streams to correlate ETM timestamps with exact GPS vehicle trajectory. |
| **Fixed Bus Capacities** | Bus capacity assumed by fleet class (65 for CNG, 46 for AC Electric). | Ingest dynamic vehicle assignment feeds from depot operational logs to map exact vehicle registration IDs. |
