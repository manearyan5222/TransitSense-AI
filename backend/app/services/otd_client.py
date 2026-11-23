"""Feed adapter scaffold. Live requests require an endpoint supplied by the user.

The project does not ship verified Transport Stack API endpoint URLs or credentials.
Without both an explicitly configured endpoint and key, this service returns
synthetic demo positions with SYNTHETIC_DEMONSTRATION provenance.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger("DelhiTransportStackClient")

VEHICLE_POSITIONS_URL = os.getenv("DELHI_TRANSPORT_STACK_VEHICLE_POSITIONS_URL", "").strip()
TRIP_UPDATES_URL = os.getenv("DELHI_TRANSPORT_STACK_TRIP_UPDATES_URL", "").strip()


class DelhiTransportStackClient:
    """
    Adapter for a user-configured JSON feed. This is not a verified live integration.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key 
            or os.getenv("DELHI_TRANSPORT_STACK_API_KEY") 
            or os.getenv("DELHI_OTD_API_KEY", "")
        )
        self.timeout = int(os.getenv("TRANSPORT_STACK_TIMEOUT", "8"))

    def is_live_configured(self, endpoint: str = "") -> bool:
        """A key alone is insufficient; require an explicitly configured feed URL."""
        return bool(endpoint and self.api_key and len(self.api_key.strip()) > 5)

    def fetch_vehicle_positions(self, route_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves positions from an explicitly configured JSON endpoint, or returns
        clearly disclosed synthetic demo positions when the adapter is unconfigured.
        """
        if not self.is_live_configured(VEHICLE_POSITIONS_URL):
            logger.info("Verified vehicle feed URL/key not configured. Serving synthetic demo telemetry.")
            return self._generate_simulated_vehicle_positions(route_id)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "TransitSenseAI-Hackathon2026/1.0"
        }

        try:
            resp = requests.get(VEHICLE_POSITIONS_URL, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            vehicles = data.get("vehicles") or data.get("entity", [])
            if route_id:
                vehicles = [v for v in vehicles if v.get("route_id") == route_id or v.get("route_short_name") == route_id]
            return {
                "status": "success",
                "data_provenance": "OFFICIAL",
                "is_live_vehicle_gps": True,
                "source": VEHICLE_POSITIONS_URL,
                "count": len(vehicles),
                "vehicles": vehicles,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.warning(f"Configured vehicle feed unavailable or invalid: {e}")

        # Fall back to synthetic demonstration positions if the configured feed fails.
        sim = self._generate_simulated_vehicle_positions(route_id)
        sim["warning"] = "Configured feed unavailable; showing synthetic demonstration positions."
        return sim

    def fetch_trip_updates(self, route_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetches GTFS-RT Trip Updates for delay and headway tracking."""
        if not self.is_live_configured(TRIP_UPDATES_URL):
            return {
                "status": "success",
                "data_provenance": "SYNTHETIC_DEMONSTRATION",
                "is_live_vehicle_gps": False,
                "updates": [],
                "note": "Synthetic trip updates. Configure a verified URL and API key to use a live feed."
            }

        url = TRIP_UPDATES_URL
        headers = {"Authorization": f"Bearer {self.api_key}", "x-api-key": self.api_key}
        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                return {
                    "status": "success",
                    "data_provenance": "OFFICIAL",
                    "is_live_vehicle_gps": True,
                    "updates": resp.json().get("updates", [])
                }
        except Exception as e:
            logger.error(f"Error fetching TripUpdates: {e}")

        return {
            "status": "fallback",
            "data_provenance": "SYNTHETIC_DEMONSTRATION",
            "is_live_vehicle_gps": False,
            "updates": []
        }

    def _generate_simulated_vehicle_positions(self, route_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthetic demonstration bus positions across sample corridors
        for hackathon demonstration and offline testing.
        """
        sample_fleet = [
            {"vehicle_id": "DL-1PC-4012", "route_id": "DTC_534", "route_name": "534", "lat": 28.5682, "lon": 77.2435, "speed_kmh": 24.5, "bearing": 182, "is_ac": False},
            {"vehicle_id": "DL-1PD-8821", "route_id": "DTC_534", "route_name": "534", "lat": 28.6210, "lon": 77.2910, "speed_kmh": 18.0, "bearing": 210, "is_ac": False},
            {"vehicle_id": "DL-1PC-1102", "route_id": "DTC_429", "route_name": "429", "lat": 28.5830, "lon": 77.2280, "speed_kmh": 28.0, "bearing": 95, "is_ac": False},
            {"vehicle_id": "DL-1PD-9031", "route_id": "DTC_429", "route_name": "429", "lat": 28.5412, "lon": 77.2640, "speed_kmh": 15.2, "bearing": 120, "is_ac": False},
            {"vehicle_id": "DL-1PC-3319", "route_id": "DTC_TMS", "route_name": "TMS+", "lat": 28.6250, "lon": 77.1950, "speed_kmh": 32.0, "bearing": 45, "is_ac": False},
            {"vehicle_id": "DL-1PE-7704", "route_id": "DTC_502", "route_name": "502", "lat": 28.5290, "lon": 77.2080, "speed_kmh": 22.1, "bearing": 190, "is_ac": True},
            {"vehicle_id": "DL-1PE-6512", "route_id": "DTC_781", "route_name": "781", "lat": 28.5720, "lon": 77.1120, "speed_kmh": 29.4, "bearing": 270, "is_ac": True},
        ]

        if route_id:
            sample_fleet = [v for v in sample_fleet if v["route_id"] == route_id or v["route_name"] == route_id]

        return {
            "status": "success",
            "data_provenance": "SYNTHETIC_DEMONSTRATION",
            "is_live_vehicle_gps": False,
            "scientific_disclosure": "Positions are synthetic demonstration data; no live vehicle feed is configured.",
            "count": len(sample_fleet),
            "vehicles": sample_fleet,
            "timestamp": time.time()
        }


# Maintain backward compatibility aliases
DelhiOTDClient = DelhiTransportStackClient
otd_client = DelhiTransportStackClient()
