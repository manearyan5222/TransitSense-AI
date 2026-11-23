# TransitSense AI: Short Prototype Demo

## Before presenting

1. Start the app from the project folder: `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`.
2. Open `http://localhost:8000/` and confirm the page loads.
3. Keep the provenance disclosure visible or ready to open.

## 2-minute walkthrough

**0:00–0:20 — Problem**  
“TransitSense explores how crowding information could help people compare bus journeys, alongside travel time. This is a working prototype for the crowdedness-aware journey-planning problem.”

**0:20–1:15 — Plan a journey**  
Enter an origin and destination supported by the demo and request routes. Show the route alternatives and available crowd explanations. Switch the preference if available. Describe what the screen actually displays; do not promise a specific route, seat probability, response time, or live rider count.

**1:15–1:40 — Explain the data**  
Open the data disclosure. “This copy uses simulated ETM records and a small demonstration network. The model metrics are from the synthetic demonstration data; they are not official-data or real-world validation results. No live vehicle feed is configured.”

**1:40–2:00 — Close honestly**  
“The prototype demonstrates the journey-planning flow. Official Problem 2 ETM data has not been staged in this copy, and official-data validation is still a scaffold. The next step is to obtain and verify that dataset, map its schema, and evaluate the model before making real-world performance claims.”

## If asked

- **Is this live?** No. The displayed data is synthetic and no live feed is configured.
- **Was the model validated on official ETM data?** No. Metrics shown are from a synthetic dataset.
- **Does it use AFC alighting records?** No. AFC calibration is not implemented; it is listed for Problem 5 (Phase 2), not this Problem 2 demo.
- **What is complete?** A prototype journey-planning interface and a preliminary official-data validation scaffold. Explain only the parts you can show working in the running app.
