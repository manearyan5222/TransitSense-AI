# TransitSense AI: API Specification (OpenAPI 3.1 Standards)
**Transport Stack Hackathon 2026 — Problem 2: Crowdedness-Aware Journey Planner**  
**Backend Framework:** Python FastAPI (ASGI / Uvicorn)  
**Base URL:** `/api/v1`  
**Document Version:** 1.0.0  

---

## 1. Global API Standards & Conventions

### 1.1 Base Headers & Formats
- All requests and responses use `Content-Type: application/json`.
- Standard coordinate ordering throughout the API: `[latitude, longitude]` in high-level objects, and `[longitude, latitude]` for GeoJSON standard specifications.
- Timestamps adhere to ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ` or local `YYYY-MM-DDTHH:MM:SS+05:30`).

### 1.2 Standard Success Response Envelope
```json
{
  "status": "success",
  "data": {},
  "metadata": {
    "execution_time_ms": 14.2,
    "timestamp": "2026-11-20T22:15:00+05:30"
  }
}
```

### 1.3 Standard Error Response Envelope
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_ORIGIN_DESTINATION",
    "message": "Origin and destination stops must be at least 150 meters apart.",
    "details": null
  },
  "metadata": {
    "timestamp": "2026-11-20T22:15:00+05:30"
  }
}
```

---

## 2. API Endpoints Catalog

| Domain | Method | Endpoint Path | Description |
| :--- | :---: | :--- | :--- |
| **System** | `GET` | `/api/v1/health` | Service health, DB connectivity, model registry status. |
| **System** | `GET` | `/api/v1/system/stats` | GTFS route/stop counts, ETM sample size, active ML model. |
| **Stops** | `GET` | `/api/v1/stops/search` | Search stops by name or stage with fuzzy matching. |
| **Stops** | `GET` | `/api/v1/stops/nearby` | Find nearest bus stops within radius using PostGIS. |
| **Stops** | `GET` | `/api/v1/stops/{stop_id}` | Detailed stop info, servicing routes, and coordinates. |
| **Stops** | `GET` | `/api/v1/stops/{stop_id}/crowd-profile` | 24-hour temporal crowd load curve (for Recharts). |
| **Routes** | `GET` | `/api/v1/routes` | Search and filter transit routes (DTC / DIMTS / AC). |
| **Routes** | `GET` | `/api/v1/routes/{route_id}` | Detailed route metadata and terminal definitions. |
| **Routes** | `GET` | `/api/v1/routes/{route_id}/stops` | Sequential ordered stop list for directional trip. |
| **Routes** | `GET` | `/api/v1/routes/{route_id}/polyline` | GeoJSON LineString of roadway route trajectory. |
| **Routes** | `GET` | `/api/v1/routes/{route_id}/crowd-forecast` | Segment-by-segment crowd prediction for scheduled trip. |
| **Journey** | `POST`| `/api/v1/journey/plan` | **Core:** Multi-objective journey planner (Fast vs Comfortable). |
| **Crowd** | `POST`| `/api/v1/crowd/predict-segment` | Dynamic XGBoost inference on custom feature inputs. |
| **Crowd** | `GET` | `/api/v1/crowd/network-heatmap` | Network-wide crowd tiers for Leaflet choropleth layer. |
| **Crowd** | `GET` | `/api/v1/crowd/compare-routes` | Side-by-side corridor comparison of competing lines. |

---

## 3. Detailed Endpoint Specifications

### 3.1 `GET /api/v1/health`
Checks backend readiness, database connection pool, and ML model loaded into memory.

#### Response `200 OK`
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "database": {
      "connected": true,
      "postgis_enabled": true
    },
    "ml_engine": {
      "model_loaded": true,
      "model_version": "xgb_v1_delhi_2026",
      "algorithm": "XGBoost 2.0.3",
      "inference_latency_p95_ms": 4.8
    }
  }
}
```

---

### 3.2 `GET /api/v1/stops/search`
Autocomplete search for stops and transit hubs (e.g., "Kashmere Gate", "Nehru Place", "Dhaula Kuan").

#### Query Parameters
- `query` (string, required): Partial name or stage prefix (min length: 2).
- `limit` (integer, optional, default: 10): Max items to return.

#### Response `200 OK`
```json
{
  "status": "success",
  "data": [
    {
      "stop_id": "DTC_00192",
      "stop_name": "Kashmere Gate ISBT",
      "lat": 28.667231,
      "lon": 77.228945,
      "routes_serviced_count": 48,
      "is_metro_hub": true
    },
    {
      "stop_id": "DTC_00193",
      "stop_name": "Kashmere Gate Metro Station",
      "lat": 28.666810,
      "lon": 77.229850,
      "routes_serviced_count": 22,
      "is_metro_hub": true
    }
  ]
}
```

---

### 3.3 `GET /api/v1/stops/{stop_id}/crowd-profile`
Fetches the 24-hour hourly expected crowdedness distribution for a stop. Serves directly into frontend **Recharts** area/bar charts.

#### Path & Query Parameters
- `stop_id` (string, required): GTFS stop identifier.
- `day_type` (string, optional, default: `"WEEKDAY"`): `"WEEKDAY" | "SATURDAY" | "SUNDAY"`.

#### Response `200 OK`
```json
{
  "status": "success",
  "data": {
    "stop_id": "DTC_00192",
    "stop_name": "Kashmere Gate ISBT",
    "day_type": "WEEKDAY",
    "hourly_data": [
      {
        "hour": 6,
        "time_label": "06:00",
        "avg_boardings": 28,
        "avg_alightings": 12,
        "avg_through_crowd_tier": 0.4,
        "crowd_label": "LOW",
        "peak_category": "OFF_PEAK"
      },
      {
        "hour": 9,
        "time_label": "09:00",
        "avg_boardings": 285,
        "avg_alightings": 240,
        "avg_through_crowd_tier": 2.8,
        "crowd_label": "CRUSH",
        "peak_category": "MORNING_RUSH"
      },
      {
        "hour": 18,
        "time_label": "18:00",
        "avg_boardings": 310,
        "avg_alightings": 290,
        "avg_through_crowd_tier": 2.9,
        "crowd_label": "CRUSH",
        "peak_category": "EVENING_RUSH"
      }
    ]
  }
}
```

---

### 3.4 `POST /api/v1/journey/plan` (Core Innovation Endpoint)
Executes a multi-objective pathfinding query across the Delhi transit network with crowdedness penalty weighting.

#### Request Body
```json
{
  "origin": {
    "lat": 28.6289,
    "lon": 77.2065,
    "name": "Connaught Place"
  },
  "destination": {
    "lat": 28.5494,
    "lon": 77.2536,
    "name": "Nehru Place Terminal"
  },
  "departure_time": "2026-11-21T09:00:00+05:30",
  "preference": "COMFORT_FIRST",
  "max_transfers": 1,
  "max_walk_distance_meters": 600,
  "include_alternatives": true
}
```

**Allowed `preference` values:**
- `FASTEST`: Minimum journey time; crowd penalties minimized.
- `COMFORT_FIRST`: Strong penalty on high/crush-loaded buses; routes commuter towards lower-occupancy alternatives (or slightly later/parallel lines).
- `BALANCED`: Standard trade-off balancing delay against standing comfort.
- `FEWEST_TRANSFERS`: Minimizes modal interchanges.

#### Response `200 OK`
```json
{
  "status": "success",
  "data": {
    "query_id": "q_78f13bda-69c2-40de",
    "origin": { "lat": 28.6289, "lon": 77.2065, "name": "Connaught Place" },
    "destination": { "lat": 28.5494, "lon": 77.2536, "name": "Nehru Place Terminal" },
    "recommended_plan": "comfort_choice",
    "plans": [
      {
        "plan_id": "fastest_choice",
        "tag": "FASTEST",
        "title": "Direct Route 505 (High Overcrowding)",
        "summary": {
          "total_duration_minutes": 42,
          "total_walking_minutes": 6,
          "total_walking_meters": 380,
          "transfers_count": 0,
          "estimated_fare_inr": 15,
          "overall_crowd_tier": 3,
          "overall_crowd_label": "CRUSH",
          "seating_probability": 0.08
        },
        "legs": [
          {
            "leg_type": "WALK",
            "duration_minutes": 4,
            "distance_meters": 240,
            "from_name": "Connaught Place",
            "to_name": "Scindia House Bus Stop",
            "instruction": "Walk to Scindia House Bus Stop"
          },
          {
            "leg_type": "TRANSIT",
            "mode": "BUS",
            "route_id": "DTC_505",
            "route_short_name": "505",
            "route_long_name": "Kamla Market to Mehrauli",
            "agency_name": "Delhi Transport Corporation",
            "is_ac": false,
            "departure_time": "09:06:00",
            "arrival_time": "09:44:00",
            "duration_minutes": 38,
            "stops_count": 14,
            "crowd_assessment": {
              "tier": 3,
              "label": "CRUSH",
              "mean_occupancy_ratio": 1.24,
              "color": "#EF4444",
              "explanation": "Severe crowd: Conductor punch density is high; standing room only from India Gate onwards."
            },
            "intermediate_stops": [
              { "stop_sequence": 1, "stop_name": "Scindia House", "predicted_load": 48, "tier": 1 },
              { "stop_sequence": 4, "stop_name": "National Stadium", "predicted_load": 72, "tier": 2 },
              { "stop_sequence": 7, "stop_name": "Sundar Nagar", "predicted_load": 82, "tier": 3 },
              { "stop_sequence": 14, "stop_name": "Nehru Place", "predicted_load": 54, "tier": 1 }
            ],
            "polyline_geojson": {
              "type": "LineString",
              "coordinates": [
                [77.2201, 28.6312],
                [77.2345, 28.6120],
                [77.2536, 28.5494]
              ]
            }
          },
          {
            "leg_type": "WALK",
            "duration_minutes": 2,
            "distance_meters": 140,
            "from_name": "Nehru Place Bus Stop",
            "to_name": "Nehru Place Terminal",
            "instruction": "Arrive at destination"
          }
        ]
      },
      {
        "plan_id": "comfort_choice",
        "tag": "MOST_COMFORTABLE",
        "title": "Route 427 AC Bus (Seats Readily Available)",
        "summary": {
          "total_duration_minutes": 48,
          "total_walking_minutes": 8,
          "total_walking_meters": 460,
          "transfers_count": 0,
          "estimated_fare_inr": 25,
          "overall_crowd_tier": 1,
          "overall_crowd_label": "MODERATE",
          "seating_probability": 0.86,
          "comfort_tradeoff": "Adds 6 mins travel time, but 86% probability of a guaranteed seat."
        },
        "legs": [
          {
            "leg_type": "WALK",
            "duration_minutes": 5,
            "distance_meters": 310,
            "from_name": "Connaught Place",
            "to_name": "Super Bazar Stop",
            "instruction": "Walk to Super Bazar Stop"
          },
          {
            "leg_type": "TRANSIT",
            "mode": "BUS",
            "route_id": "DTC_427_AC",
            "route_short_name": "427-AC",
            "route_long_name": "New Delhi Rly Station to Badarpur",
            "agency_name": "Delhi Transport Corporation",
            "is_ac": true,
            "departure_time": "09:09:00",
            "arrival_time": "09:52:00",
            "duration_minutes": 43,
            "stops_count": 16,
            "crowd_assessment": {
              "tier": 1,
              "label": "MODERATE",
              "mean_occupancy_ratio": 0.58,
              "color": "#F59E0B",
              "explanation": "Seats available; AC feeder passenger turnover allows comfortable travel."
            },
            "polyline_geojson": {
              "type": "LineString",
              "coordinates": [
                [77.2215, 28.6320],
                [77.2390, 28.6050],
                [77.2536, 28.5494]
              ]
            }
          },
          {
            "leg_type": "WALK",
            "duration_minutes": 3,
            "distance_meters": 150,
            "from_name": "Paras Cinema Stop",
            "to_name": "Nehru Place Terminal",
            "instruction": "Walk to destination"
          }
        ]
      }
    ]
  },
  "metadata": {
    "routing_time_ms": 68.4,
    "evaluated_routes_count": 18
  }
}
```

---

### 3.5 `GET /api/v1/crowd/network-heatmap`
Fetches GeoJSON segment features with predicted crowdedness tiers for a specific hour and day of week. Renders directly onto the Leaflet map as a visual transit congestion layer.

#### Query Parameters
- `hour` (integer, required): 0 to 23.
- `day_of_week` (integer, required): 0 (Sunday) to 6 (Saturday).
- `min_crowd_tier` (integer, optional, default: 0): Minimum tier to include (filter out empty routes).

#### Response `200 OK`
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [77.2289, 28.6672],
          [77.2350, 28.6540]
        ]
      },
      "properties": {
        "route_id": "DTC_534",
        "route_short_name": "534",
        "from_stop_name": "Kashmere Gate ISBT",
        "to_stop_name": "Red Fort",
        "predicted_crowd_tier": 3,
        "mean_occupancy_ratio": 1.18,
        "color": "#EF4444",
        "sample_size": 142
      }
    }
  ]
}
```

---

### 3.6 `POST /api/v1/crowd/predict-segment`
Direct ML scoring endpoint for testing individual feature vectors or synthetic trips against the trained XGBoost model.

#### Request Body
```json
{
  "route_id": "DTC_534",
  "direction_id": 0,
  "stop_sequence": 8,
  "departure_hour": 9,
  "day_of_week": 1,
  "is_ac": false,
  "bus_capacity": 65
}
```

#### Response `200 OK`
```json
{
  "status": "success",
  "data": {
    "predicted_passenger_load": 74.2,
    "occupancy_ratio": 1.14,
    "crowd_tier": 3,
    "crowd_label": "CRUSH",
    "class_probabilities": {
      "tier_0_low": 0.02,
      "tier_1_moderate": 0.08,
      "tier_2_high": 0.22,
      "tier_3_crush": 0.68
    },
    "model_version": "xgb_v1_delhi_2026",
    "inference_time_ms": 3.1
  }
}
```
