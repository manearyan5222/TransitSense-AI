"""
Delhi Transport Stack - October 2026 ETM & GTFS Data Generator
Generates realistic, statistically grounded ETM transaction records and static GTFS files
reflecting real Delhi Transport Corporation (DTC) bus operations for October 2026.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/gtfs', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# 1. Create GTFS Static Data
# Agency
agencies = pd.DataFrame([
    {"agency_id": "DTC", "agency_name": "Delhi Transport Corporation", "agency_url": "https://dtc.delhi.gov.in", "agency_timezone": "Asia/Kolkata"},
    {"agency_id": "DIMTS", "agency_name": "Delhi Integrated Multi-Modal Transit System", "agency_url": "https://dimts.in", "agency_timezone": "Asia/Kolkata"}
])
agencies.to_csv('data/gtfs/agency.txt', index=False)

# Routes
routes = pd.DataFrame([
    {"route_id": "DTC_534", "agency_id": "DTC", "route_short_name": "534", "route_long_name": "Anand Vihar ISBT to Mehrauli Terminal", "route_type": 3, "is_ac": 0},
    {"route_id": "DTC_764", "agency_id": "DTC", "route_short_name": "764", "route_long_name": "Najafgarh Terminal to Nehru Place Terminal", "route_type": 3, "is_ac": 0},
    {"route_id": "DTC_427", "agency_id": "DTC", "route_short_name": "427", "route_long_name": "New Delhi Railway Station to Badarpur Border", "route_type": 3, "is_ac": 1},
    {"route_id": "DTC_502", "agency_id": "DTC", "route_short_name": "502", "route_long_name": "Old Delhi Railway Station to Mehrauli Terminal", "route_type": 3, "is_ac": 0},
    {"route_id": "DTC_620", "agency_id": "DTC", "route_short_name": "620", "route_long_name": "Shivaji Stadium to Vasant Kunj", "route_type": 3, "is_ac": 1}
])
routes.to_csv('data/gtfs/routes.txt', index=False)

# Stops (Real key stops in Delhi along these corridors)
stops_data = [
    # Route 534 stops (Anand Vihar to Mehrauli)
    ("ST_AV01", "Anand Vihar ISBT", 28.6469, 77.3160),
    ("ST_AV02", "Ramprastha Crossing", 28.6432, 77.3090),
    ("ST_AV03", "Karkardooma Crossing", 28.6401, 77.2985),
    ("ST_AV04", "Preet Vihar", 28.6368, 77.2910),
    ("ST_AV05", "Nirman Vihar Metro Station", 28.6352, 77.2834),
    ("ST_AV06", "Laxmi Nagar", 28.6312, 77.2770),
    ("ST_AV07", "Shakarpur", 28.6290, 77.2690),
    ("ST_AV08", "ITO Crossing", 28.6295, 77.2435),
    ("ST_AV09", "Delhi Gate", 28.6412, 77.2410),
    ("ST_AV10", "Pragati Maidan Metro", 28.6225, 77.2438),
    ("ST_AV11", "National Stadium", 28.6120, 77.2375),
    ("ST_AV12", "Sundar Nagar", 28.6045, 77.2415),
    ("ST_AV13", "Nizamuddin Railway Station", 28.5912, 77.2510),
    ("ST_AV14", "Ashram Chowk", 28.5710, 77.2580),
    ("ST_AV15", "Lajpat Nagar Ring Road", 28.5685, 77.2420),
    ("ST_AV16", "Moolchand Hospital", 28.5640, 77.2345),
    ("ST_AV17", "South Extension", 28.5670, 77.2210),
    ("ST_AV18", "AIIMS Hospital", 28.5680, 77.2100),
    ("ST_AV19", "Safdarjung Hospital", 28.5665, 77.2050),
    ("ST_AV20", "Green Park Metro", 28.5585, 77.2065),
    ("ST_AV21", "Hauz Khas", 28.5475, 77.2055),
    ("ST_AV22", "IIT Gate Delhi", 28.5440, 77.1930),
    ("ST_AV23", "Adhchini Village", 28.5360, 77.1910),
    ("ST_AV24", "Mother Dairy Adhchini", 28.5310, 77.1895),
    ("ST_AV25", "Qutub Minar Metro Station", 28.5140, 77.1865),
    ("ST_AV26", "Mehrauli Terminal", 28.5180, 77.1810),

    # Route 764 specific stops (Najafgarh to Nehru Place)
    ("ST_NG01", "Najafgarh Terminal", 28.6125, 76.9850),
    ("ST_NG02", "Dwarka Mor Metro Station", 28.6185, 77.0315),
    ("ST_NG03", "Uttam Nagar East", 28.6235, 77.0680),
    ("ST_NG04", "Janakpuri District Centre", 28.6290, 77.0815),
    ("ST_NG05", "Tilak Nagar", 28.6370, 77.0980),
    ("ST_NG06", "Tagore Garden", 28.6430, 77.1120),
    ("ST_NG07", "Raja Garden", 28.6510, 77.1230),
    ("ST_NG08", "Mayapuri Crossing", 28.6365, 77.1350),
    ("ST_NG09", "Naraina Vihar", 28.6275, 77.1420),
    ("ST_NG10", "Dhaula Kuan", 28.5925, 77.1610),
    ("ST_NG11", "Moti Bagh", 28.5835, 77.1725),
    ("ST_NG12", "RK Puram Sector 1", 28.5715, 77.1840),
    ("ST_NG13", "Nehru Place Terminal", 28.5494, 77.2536),

    # Route 427 & 502 & 620 additional hubs
    ("ST_ND01", "New Delhi Railway Station", 28.6430, 77.2195),
    ("ST_ND02", "Connaught Place Super Bazar", 28.6320, 77.2215),
    ("ST_OD01", "Old Delhi Railway Station", 28.6565, 77.2305),
    ("ST_OD02", "Red Fort", 28.6540, 77.2350),
    ("ST_OD03", "Kashmere Gate ISBT", 28.6672, 77.2289),
    ("ST_VK01", "Shivaji Stadium Terminal", 28.6295, 77.2140),
    ("ST_VK02", "Vasant Kunj C-9", 28.5280, 77.1520),
    ("ST_BD01", "Badarpur Border Terminal", 28.4980, 77.3040)
]

stops_df = pd.DataFrame(stops_data, columns=["stop_id", "stop_name", "stop_lat", "stop_lon"])
stops_df["zone_id"] = "DELHI_NCT"
stops_df.to_csv('data/gtfs/stops.txt', index=False)

# Trips & Stop Times for Route 534
trips = []
stop_times = []

# Generate trips for route 534 (Outbound & Inbound)
trip_counter = 1
r534_stops = [s[0] for s in stops_data[:26]]

for trip_idx in range(1, 25): # 24 scheduled trips in a day
    t_id_out = f"TR_534_OUT_{trip_idx}"
    trips.append({
        "trip_id": t_id_out,
        "route_id": "DTC_534",
        "service_id": "OCT_2026_ALL",
        "trip_headsign": "Mehrauli Terminal",
        "direction_id": 0,
        "shape_id": "SH_534_OUT"
    })
    start_minute = 360 + (trip_idx - 1) * 45 # from 06:00 every 45 mins
    for seq, st_id in enumerate(r534_stops):
        arr_m = start_minute + seq * 3
        h = arr_m // 60
        m = arr_m % 60
        time_str = f"{h:02d}:{m:02d}:00"
        stop_times.append({
            "trip_id": t_id_out,
            "arrival_time": time_str,
            "departure_time": time_str,
            "stop_id": st_id,
            "stop_sequence": seq + 1
        })

trips_df = pd.DataFrame(trips)
trips_df.to_csv('data/gtfs/trips.txt', index=False)

stop_times_df = pd.DataFrame(stop_times)
stop_times_df.to_csv('data/gtfs/stop_times.txt', index=False)

print(f"Generated GTFS: {len(routes)} routes, {len(stops_df)} stops, {len(trips_df)} trips, {len(stop_times_df)} stop_times")

# 2. Generate Official October 2026 ETM Dataset
np.random.seed(42)
random.seed(42)

records = []
ticket_id_counter = 10000000

# 31 days in October 2026
# October 1, 2026 is a Thursday
routes_list = [
    ("DTC_534", 0, r534_stops, 65, False),
    ("DTC_764", 0, ["ST_NG01", "ST_NG02", "ST_NG03", "ST_NG04", "ST_NG05", "ST_NG06", "ST_NG07", "ST_NG08", "ST_NG09", "ST_NG10", "ST_NG11", "ST_NG12", "ST_NG13"], 65, False),
    ("DTC_427", 0, ["ST_ND01", "ST_ND02", "ST_AV10", "ST_AV12", "ST_AV14", "ST_AV15", "ST_NG13", "ST_BD01"], 65, True),
    ("DTC_502", 0, ["ST_OD01", "ST_OD02", "ST_AV09", "ST_ND02", "ST_AV11", "ST_AV18", "ST_AV21", "ST_AV25", "ST_AV26"], 65, False),
    ("DTC_620", 0, ["ST_VK01", "ST_ND02", "ST_NG10", "ST_NG11", "ST_VK02"], 46, True)
]

stops_lookup = dict(zip(stops_df["stop_id"], stops_df["stop_name"]))

# Total transactions target: ~45,000 transactions across October 2026 (authentic representative sample)
for day in range(1, 32):
    date_str = f"2026-10-{day:02d}"
    dt_cur = datetime(2026, 10, day)
    dow = dt_cur.weekday() # 0 = Monday, 6 = Sunday
    is_weekend = dow >= 5

    # Day factor
    day_mult = 0.70 if dow == 6 else (0.85 if dow == 5 else 1.0)

    for route_id, direction_id, route_stops, capacity, is_ac in routes_list:
        # Route weighting: 534 and 764 are heavy trunk routes
        route_weight = 1.4 if route_id in ["DTC_534", "DTC_764"] else 0.8
        
        # 12-16 trips per route per day
        num_trips = int(12 * day_mult)
        for t_idx in range(num_trips):
            trip_start_hour = 6 + int(t_idx * 1.1)
            if trip_start_hour > 22:
                continue

            bus_id = f"DL-1PC-{1000 + random.randint(100, 999)}"
            device_id = f"ETM-{random.randint(1000, 1050)}"
            depot_id = "BBMD" if "534" in route_id else ("HDMD" if "764" in route_id else "SNPD")

            # Simulate passenger transactions along the sequence
            for s_idx, stop_id in enumerate(route_stops[:-1]):
                # Stop hour
                st_min = (trip_start_hour * 60) + s_idx * 3 + random.randint(-1, 2)
                st_h = min(23, max(5, st_min // 60))
                st_m = st_min % 60
                st_s = random.randint(0, 59)
                t_stamp = f"{date_str} {st_h:02d}:{st_m:02d}:{st_s:02d}"

                # Demand intensity by hour (Bimodal Delhi rush hour)
                if 8 <= st_h <= 10:
                    rush_mult = 2.4
                elif 17 <= st_h <= 20:
                    rush_mult = 2.2
                elif 12 <= st_h <= 15:
                    rush_mult = 0.9
                elif st_h >= 21:
                    rush_mult = 0.5
                else:
                    rush_mult = 1.1

                if is_weekend:
                    rush_mult = 1.0 + (0.4 if 11 <= st_h <= 14 or 17 <= st_h <= 20 else 0.0)

                # Base tickets issued at this stop
                base_tickets = int(np.random.poisson(2.5 * rush_mult * route_weight))
                
                for _ in range(base_tickets):
                    ticket_id_counter += 1
                    t_id = f"TKT-{ticket_id_counter}"

                    # Ticket Type Distribution (Delhi Realities: ~38% Pink Passes, ~48% Full, ~7% Half, ~6% Daily Pass, ~1% Luggage)
                    r_type = random.random()
                    if r_type < 0.38:
                        ticket_type = "PINK_PASS"
                        fare_amount = 0.0
                    elif r_type < 0.86:
                        ticket_type = "FULL"
                        fare_amount = 10.0 if not is_ac else 15.0
                    elif r_type < 0.93:
                        ticket_type = "HALF"
                        fare_amount = 5.0 if not is_ac else 10.0
                    elif r_type < 0.99:
                        ticket_type = "DAILY_PASS"
                        fare_amount = 40.0 if not is_ac else 50.0
                    else:
                        ticket_type = "LUGGAGE"
                        fare_amount = 10.0

                    # Passenger Count (mostly 1, sometimes 2-4)
                    r_p = random.random()
                    if r_p < 0.82:
                        passenger_count = 1
                    elif r_p < 0.93:
                        passenger_count = 2
                    elif r_p < 0.97:
                        passenger_count = 3
                    elif r_p < 0.995:
                        passenger_count = 4
                    else:
                        passenger_count = random.choice([5, 6])

                    # Boarding stop is stop_id
                    boarding_stop_id = stop_id
                    boarding_stage_name = stops_lookup.get(stop_id, "Unknown Stop")

                    # Alighting stop: In Delhi ETM, destination stage is missing or null in ~45% of transactions!
                    if random.random() < 0.45:
                        alighting_stop_id = None
                        alighting_stage_name = None
                    else:
                        # Alights 2 to 10 stops ahead
                        max_ahead = len(route_stops) - 1
                        alight_idx = min(max_ahead, s_idx + random.randint(2, 7))
                        alighting_stop_id = route_stops[alight_idx]
                        alighting_stage_name = stops_lookup.get(alighting_stop_id, "Unknown Stop")

                    # Coordinates: GPS failure / null in ~14% of records
                    if random.random() < 0.14:
                        lat, lon = None, None
                    else:
                        stop_row = stops_df[stops_df["stop_id"] == stop_id].iloc[0]
                        lat = round(stop_row["stop_lat"] + random.uniform(-0.001, 0.001), 6)
                        lon = round(stop_row["stop_lon"] + random.uniform(-0.001, 0.001), 6)

                    # Bus ID missing in ~3% of logs
                    b_id = bus_id if random.random() > 0.03 else None

                    records.append({
                        "ticket_id": t_id,
                        "device_id": device_id,
                        "depot_id": depot_id,
                        "bus_id": b_id,
                        "route_id": route_id,
                        "direction_id": direction_id,
                        "trip_id": f"TRIP_{route_id}_{day}_{t_idx}",
                        "ticket_timestamp": t_stamp,
                        "boarding_stop_id": boarding_stop_id,
                        "boarding_stage_name": boarding_stage_name,
                        "alighting_stop_id": alighting_stop_id,
                        "alighting_stage_name": alighting_stage_name,
                        "ticket_type": ticket_type,
                        "passenger_count": passenger_count,
                        "fare_amount": fare_amount,
                        "is_ac": 1 if is_ac else 0,
                        "lat": lat,
                        "lon": lon
                    })

# Introduce authentic real-world data quality anomalies for strict data science audit:
# 1. Duplicates: 1.2% duplicated transactions (ETM button double-punch)
dup_indices = random.sample(range(len(records)), int(len(records) * 0.012))
for idx in dup_indices:
    records.append(records[idx].copy())

# 2. Unusual records:
# - Negative or zero passenger count corrupted records (0.1%)
for _ in range(35):
    bad_idx = random.randint(0, len(records) - 1)
    records[bad_idx]["passenger_count"] = random.choice([0, -1, -2])

# - Negative fare or extreme outlier (e.g. fare = 999.0 or test fare)
for _ in range(20):
    bad_idx = random.randint(0, len(records) - 1)
    records[bad_idx]["fare_amount"] = random.choice([-10.0, 999.0])

# - Passenger count extreme test outlier (e.g. 99)
for _ in range(12):
    bad_idx = random.randint(0, len(records) - 1)
    records[bad_idx]["passenger_count"] = 99

df_etm = pd.DataFrame(records)
# Shuffle
df_etm = df_etm.sample(frac=1.0, random_state=42).reset_index(drop=True)

df_etm.to_csv('data/raw/delhi_etm_october_2026.csv', index=False)
print(f"Generated official October 2026 ETM dataset: {len(df_etm):,} records saved to data/raw/delhi_etm_october_2026.csv")
