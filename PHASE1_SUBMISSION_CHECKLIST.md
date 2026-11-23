# Phase 1 Submission Checklist

## First: confirm the demo runs

From the project folder:

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open `http://localhost:8000/`. Try one journey with stops that appear in the demo. Use only the route details and modules that load successfully. Keep the synthetic-data disclosure visible during the presentation.

## Run the existing backend checks

```bash
python -m pytest backend/tests/ -v
```

Report the actual result from this run; the result written in older notes may be stale.

## State the data accurately

- The local ETM dataset is simulated, not official passenger data.
- The model benchmark metrics are from synthetic demo data and are not real-world validation.
- No official Problem 2 ETM dataset, AFC dataset, or live feed credentials are staged in this copy.
- The current official-data validation script expects a fixed schema and does not integrate AFC. Do not call it drop-in ready.
- AFC is listed for Problem 5 (Phase 2); do not claim it is part of this Problem 2 prototype.

## Before submission

- [ ] Confirm the local app opens and demonstrate one supported origin/destination.
- [ ] Capture a short screen recording of the working interface.
- [ ] Check the submission portal for its required format and deadline.
- [ ] Ensure the README, technical note, and demo script all disclose the synthetic data.
- [ ] Avoid claims of official-data accuracy, live tracking, guaranteed seats, exact route predictions, or production readiness unless independently verified.
