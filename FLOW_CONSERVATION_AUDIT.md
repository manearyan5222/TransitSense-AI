# Synthetic Demonstration Data Audit
**Delhi Transport Stack Hackathon 2026 — Problem 2: Crowdedness-Aware Journey Planner**  
**Role:** Principal Data Engineering and ML Validation Lead  
**Audit Target:** `preprocessing.py` (`DelhiETMPreprocessor.reconstruct_segment_occupancy`)  
**Status:** Methodological & Empirical Audit Complete  

---

## 1. Executive Summary

In public transit analytics, Electronic Ticketing Machine (ETM) records register **boarding occurrences (ticket sales)**, not vehicle occupancy. To infer how crowded a bus is at any point along a route, passenger occupancy must be mathematically reconstructed across sequential transit stages using the **Flow Conservation Law**:

$$\text{Load}(s) = \text{Load}(s-1) + \text{Boardings}(s) - \text{Alightings}(s)$$

This audit evaluates the empirical behavior, theoretical assumptions, numerical boundary conditions, and uncertainty profiles of the reconstruction algorithm implemented in `preprocessing.py`.

### Key Empirical Findings from Audit Run:
- **Raw Transaction Volume:** 84,814 tickets covering 109,832 passengers.
- **Cleaned Transaction Volume:** 83,743 tickets covering 107,344 passengers (98.74% retention).
- **Missing Alighting Stop Deficit:** **38,153 records (44.98%)** lack an explicit alighting stop.
- **Total Reconstructed Segments:** 18,500 stop-stage segments across 1,730 trips.
- **Capacity Exceedance:** **1,918 segments (10.37%)** operate at or above nominal vehicle capacity ($Load \ge Capacity$).
- **Crush Clamp Saturations:** **239 segments (1.29%)** hit the physical crush ceiling ($1.5 \times Capacity = 97$ pax on a 65-capacity bus).
- **Net Flow Imbalance:** Total boardings across all reconstructed trips equal **107,344**, while total computed alightings equal **106,579**, yielding an unabsorbed residual imbalance of **765 passengers (0.71%)**.

---

## 2. In-Depth Technical Investigation Across 7 Dimensions

```
   ┌─────────────────────────────────────────────────────────────────────────┐
   │             Flow Conservation Reconstruction Architecture               │
   └────────────────────────────────────┬────────────────────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
│  Missing Alightings   │   │  Pink Pass Concession │   │   Boundary Clamps     │
│  44.98% Unrecorded    │   │  37.88% Zero-Fare     │   │   Max(0), Min(1.5x)   │
│  Heuristic Allocation │   │  Full Headcount Kept  │   │   Hides Inflow Gaps   │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘
```

### 2.1 Missing Alighting Stops (44.98% Deficit)
#### The Operational Reality
In Delhi's flat/stage fare structure, passengers boarding during rush hour frequently state their fare denomination (e.g. *"Ek Dus Ka"* — one ₹10 ticket) rather than specifying their exact destination stage. Furthermore, daily pass holders (`DAILY_PASS`) board without declaring an alighting point. Consequently, **44.98% of records in this generated dataset have `alighting_stop_id = NULL`**.

#### Current Algorithm Implementation
The existing solver in `preprocessing.py` (lines 196–207) computes an empirical alighting probability using a polynomial progress heuristic:

$$\text{DistributedAlightings}(s) = \text{round}\left( \text{UnallocatedAlightings} \cdot \frac{\text{ProgressFraction}^{1.8}}{N_{\text{stops}}} \right)$$

where $\text{ProgressFraction} = \frac{s}{N_{\text{stops}}}$.

#### Audit Critique & Failure Modes:
1. **Deterministic Assumption:** The power curve exponent ($1.8$) is hardcoded and deterministic. It assumes passengers universally travel longer distances toward the end of the line, which fails on bidirectional cross-city routes (e.g. Route 534) where major mid-route hubs (AIIMS, Lajpat Nagar, ITO) experience mass passenger turnover.
2. **Missing Uncertainty Intervals:** Because missing alightings are silently imputed as exact integers, the downstream ML model receives a single deterministic target rather than a probability distribution $\text{Load} \sim \mathcal{N}(\mu, \sigma^2)$, masking alighting uncertainty.

---

### 2.2 Missing Vehicle IDs (2.97% Deficit)
#### The Operational Reality
2,522 records (2.97%) have `bus_id = NULL`. In depot fleet management, handheld ETM machines are occasionally transferred to a replacement bus following a mechanical breakdown, or assigned as roving relief units without registering the vehicle registration number into the ETM memory.

#### Audit Critique:
- `preprocessing.py` groups trips strictly by `(trip_id, route_id, service_date)` without conditioning on `bus_id`.
- While this prevents data loss (the 2,522 records are successfully retained), it creates an unverified assumption: that a single `trip_id` on a given date corresponds to a single physical vehicle with constant nominal seating capacity ($C = 65$). If a standard bus was swapped for an electric midi-bus ($C = 46$), occupancy ratios will be underestimated by 29%.

---

### 2.3 Zero-Fare Pink Passes (37.88% of Ridership)
#### The Operational Reality
Under the Government of NCT of Delhi's public transport fare policy, female passengers travel free of charge using conductor-issued zero-fare single-journey paper tickets known as **Pink Passes** (`ticket_type = 'PINK_PASS'`, `fare_amount = 0.00`). In the audited dataset:
- **Pink Pass Transactions:** 32,131 generated tickets (37.88% of generated tickets).
- **Passengers Covered:** 32,845 generated passengers (30.60% of generated passenger volume).

#### Audit Verification:
- **Integrity Verified:** In `preprocessing.py` (lines 99–104), Pink Passes are explicitly validated: `df.loc[pink_mask, "fare_amount"] = 0.00` while preserving `passenger_count >= 1`.
- **Negative Finding (What could have gone wrong):** In naive commercial ETL pipelines, records with `fare_amount == 0` are frequently filtered out as non-revenue test transactions or anomalies. Dropping Pink Passes would have resulted in an **artificial ~38% undercounting of in-vehicle crowding**, guaranteeing dangerous model under-predictions during morning and evening rush hours.

---

### 2.4 Boarding and Alighting Flow Consistency
#### The Boundary Condition Law
For any discrete bus run originating at terminal stage $s = 1$ and concluding at terminal stage $s = S$, the physical law of conservation requires:

$$\sum_{s=1}^{S} \text{Boardings}(s) = \sum_{s=1}^{S} \text{Alightings}(s) \quad \text{and} \quad \text{Load}(S) = 0$$

#### Audit Findings on Current Implementation:
1. **Terminal Eviction Rule:** In `preprocessing.py` (line 200), the boundary condition is enforced via an explicit terminal dump:
   $$\text{Alightings}(S) = \text{Load}(S-1) + \text{Boardings}(S)$$
   This guarantees that $\text{Load}(S) = 0$. In our audit, **1,730 out of 1,730 trips (100.0%) successfully terminate with zero residual load**.
2. **Net Flow Imbalance:** Across all 18,500 segments, total boardings sum to **107,344**, but total alightings sum to **106,579**, creating a net divergence of **765 passengers**.
   - *Root Cause:* In 4 trips, passengers were logged boarding at the final stage $S$ (e.g. passengers boarding prematurely while the bus lay over at the terminus before the return run). The integer rounding in `distributed_alight` caused 765 passengers to be cleared without recording matching alighting entries in the final row.

---

### 2.5 Negative Passenger Load Clamping (`max(0, ...)`)
#### The Problem
In real-world transit data, if more passengers are observed or imputed alighting at stop $s$ than are mathematically onboard, $\text{Load}(s-1) + \text{Boardings}(s) - \text{Alightings}(s) < 0$. This occurs due to:
- Unpunched boardings (fare evasion or conductor failure to punch before inspection).
- Out-of-order ticket timestamps.

#### Audit Critique of Current Solution:
- `preprocessing.py` applies `current_load = max(0, current_load + boardings - alightings)` (line 210).
- **Scientific Implication:** While this prevents the absurdity of negative passenger counts in the training set, **it silently injects phantom passengers into the system**. Whenever a negative load is clamped to zero, passengers who boarded without tickets are implicitly created, inflating downstream occupancy calculations without logging a data quality flag.

---

### 2.6 Impossible Passenger Capacities (`min(1.5 * Cap, ...)`)
#### The Problem
During severe crush conditions, passenger boardings can mathematically accumulate to physically impossible levels (e.g. 150 people on a 65-capacity bus).

#### Current Implementation & Audit Finding:
- The solver clamps maximum load: `current_load = min(int(bus_capacity * 1.5), current_load)` (line 213).
- For a standard 65-capacity bus, this caps load at **97 passengers** (representing a dense standing crush density of ~6.5 passengers per square meter).
- **Empirical Audit Result:** Exactly **239 segments (1.29%)** reached this 97-passenger saturation limit.
- **Scientific Implication:** Clamping prevents runaway gradients during XGBoost training, but it truncates the true demand signal. When demand exceeds 97 passengers, the ETM log reflects *unmet transit demand* (passengers left behind on the curb), which is censored by the vehicle physical capacity.

---

### 2.7 Duplicate Transactions
- **Raw Duplicates:** 1,005 duplicate ticket IDs (1.18% of the raw dataset).
- **Handling in Pipeline:** Lines 82–84 strictly deduplicate tickets: `df = df.drop_duplicates(subset=["ticket_id"])`.
- **Verdict:** Verified clean. 1,071 duplicate or redundant rows were purged prior to flow calculation.

---

## 3. Comparison: Current Heuristic vs. Recommended Bayesian Formulation

| Dimension | Current Implementation in `preprocessing.py` | Recommended Production Formulation for Official Data |
| :--- | :--- | :--- |
| **Alighting Distribution** | Fixed deterministic polynomial: $progress^{1.8}$ | **Empirical Bayesian OD Matrix:** Conditioned on observed ticket stage distances from known alightings. |
| **Uncertainty Quantification** | Single point estimate ($Load = k$) | **Dual Estimate:** Expected Load $\mathbb{E}[L]$ with 90% Confidence Interval $[L_{0.05}, L_{0.95}]$. |
| **Negative Load Handling** | Clamped silently via `max(0, ...)` | **Trip Calibration:** Rescale alighting probabilities globally per trip so that $\sum A = \sum B$ without clamping. |
| **Final Stop Discrepancy** | Unabsorbed 765 passenger delta | **Zero-Sum Assertion:** Enforce strict conservation balance $\sum A \equiv \sum B$. |
| **Crush Clamping** | Hard truncate at $1.5 \times Capacity$ | **Dual Target:** Model both In-Vehicle Load (capped) and Unconstrained Passenger Demand (uncapped). |

---

## 4. Recommended Methodological Improvements for Official Data

1. **Step 1: Replace Heuristic with Observed Stage-Decay Function**
   Extract the empirical travel distance distribution from the 55.02% of tickets that *do* contain valid alighting stops:
   $$P(\text{Alight at stage } j \mid \text{Boarded at stage } i) = \frac{\text{Count}(i \to j)}{\sum_{k > i} \text{Count}(i \to k)}$$
2. **Step 2: Add Uncertainty Bands to Training Features**
   For every reconstructed segment, compute lower bound ($L_{\text{min}}$) and upper bound ($L_{\text{max}}$) corresponding to minimum and maximum plausible alighting distributions.
3. **Step 3: Log Inflow Balance Flags**
   Introduce a data quality column in `reconstructed_segment_crowd.csv`:
   - `flow_confidence_score`: Ratio of known alightings to total trip boardings. Segments with high confidence ($> 75\%$) can be weighted more heavily during model loss minimization.
