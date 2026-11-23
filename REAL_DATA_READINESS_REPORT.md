# TransitSense AI: Real-Data Readiness

**Transport Stack Hackathon 2026 — Problem 2**  
**Checked:** 23 November 2026

## Official data relevant to this prototype

The [hackathon brief](https://delhi.transportstack.in/hackathon/) describes Problem 2 as a crowdedness-aware planner using 4–5 weeks of bus e-ticketing and ETM data, with route and stop information. It lists an October 2026 e-ticketing download of about 2.56 million tickets. The brief describes about one month of AFC boarding/alighting data under **Problem 5**, a Phase 2 problem; this project does not currently use AFC data.

The [Delhi Transport Stack data catalogue](https://delhi.transportstack.in/data-services) lists public GTFS and GTFS-RT catalogue entries. This project has not verified an API endpoint, credentials, or a live feed connection. Do not present the feed adapter as live integration.

## What is present locally

- The demo uses 84,814 statistically simulated ETM-like records. Its ML metrics are synthetic-benchmark results, not official-data performance.
- `data/official/` contains only its README; no official ETM, AFC, GTFS, or GPS file was present during this check.
- No project-root `.env` file was present during this check.
- The small `data/gtfs/` files are demo topology and are not the full official network feed.
- The UI labels the demo data synthetic. No live GPS data is configured.

## Validation code status

`ml/validate_official.py` is an early validation scaffold. It currently expects a fixed canonical CSV schema. It does not normalize alternate source schemas, load or use AFC observations, ingest the full official GTFS feed, save a trained model, or produce an official validation report. The optional `--afc` argument only detects a file; it is not used in calculations. Register an ETM file explicitly as `OFFICIAL` in `data/provenance/registry.json` after checking its source; a folder name alone is not provenance evidence.

The feed adapter in `backend/app/services/otd_client.py` returns clearly tagged synthetic demo positions unless both an API key and an explicitly configured feed URL are provided. The endpoint format and response have not been verified against an authenticated hackathon feed.

## Next steps after obtaining official access

1. Download the Problem 2 ticketing file and route/stop resources from the official hackathon links.
2. Keep the original files unchanged; record their source URL and SHA-256 in the provenance registry.
3. Inspect and map the actual columns to the validator’s canonical schema, or update the validator based on the published data README.
4. Run schema-only validation first, then evaluate with a chronological split. Keep official and synthetic metrics separate.
5. Treat AFC calibration and live vehicle feeds as future work until the project has the appropriate files, access, and working integration.

**Submission wording:** “TransitSense AI is a working prototype demonstrated on synthetic ETM-like data. The official Problem 2 dataset is identified in the hackathon brief; live data access and official-data validation are not yet verified in this codebase.”
