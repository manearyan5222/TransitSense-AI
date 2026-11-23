# Official data staging area

This folder currently contains no official ETM/AFC dataset. Keep this directory limited to files downloaded from the official hackathon portal, and record the source URL, download date, and checksum before registering a file as `OFFICIAL`.

## Problem 2 data

The hackathon lists an October 2026 bus e-ticketing/ETM dataset for Problem 2, with GTFS route and stop information. It is not included in this local project copy. Obtain it from the official Problem 2 page or catalogue and follow any access terms shown there.

## Important scope

AFC boarding/alighting data is associated with Problem 5 (Phase 2) in the hackathon catalogue. This project does not use AFC, and `ml/validate_official.py --afc ...` currently only warns that AFC calibration is not implemented.

## Current validation limitations

`ml/validate_official.py` is an early scaffold. It expects the canonical columns documented in the script, requires explicit provenance registration, and does not normalize vendor column names or integrate the full official GTFS feed. Do not claim official-data validation based on this script until those steps are completed and reviewed.
