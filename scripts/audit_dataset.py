import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/delhi_etm_october_2026.csv')

print('=== 1. SHAPE & COLUMNS ===')
print('Total Rows:', len(df), 'Total Columns:', len(df.columns))
for col in df.columns:
    print(f"  {col:<22} | dtype: {str(df[col].dtype):<10} | nulls: {df[col].isnull().sum():<6} ({df[col].isnull().mean()*100:5.2f}%) | unique: {df[col].nunique()}")

print('\n=== 2. MISSING VALUES ===')
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df)) * 100
missing_df = pd.DataFrame({'null_count': null_counts, 'null_pct': null_pct})
print(missing_df[missing_df['null_count'] > 0])

print('\n=== 3. DUPLICATES ===')
exact_dups = df.duplicated().sum()
ticket_dups = df['ticket_id'].duplicated().sum()
print('Exact duplicate rows:', exact_dups)
print('Duplicate ticket_id occurrences:', ticket_dups)

print('\n=== 4. TIMESTAMP DISTRIBUTION ===')
df['dt'] = pd.to_datetime(df['ticket_timestamp'])
print('Min Timestamp:', df['dt'].min())
print('Max Timestamp:', df['dt'].max())
print('Total Calendar Days Covered:', df['dt'].dt.date.nunique())

print('\n=== 5. ROUTE DISTRIBUTION ===')
route_counts = df['route_id'].value_counts()
route_pct = df['route_id'].value_counts(normalize=True) * 100
routes_summary = pd.DataFrame({'count': route_counts, 'pct': route_pct})
print(routes_summary)

print('\n=== 6. PASSENGER COUNT ===')
print(df['passenger_count'].describe())
print(df['passenger_count'].value_counts().sort_index())

print('\n=== 7. UNUSUAL RECORDS ===')
print('Passenger count <= 0:', int((df['passenger_count'] <= 0).sum()))
print('Passenger count >= 10:', int((df['passenger_count'] >= 10).sum()))
print('Fare amount < 0:', int((df['fare_amount'] < 0).sum()))
print('Fare amount >= 100 (non-pass):', int(((df['fare_amount'] >= 100) & (df['ticket_type'] != 'DAILY_PASS')).sum()))
print('Pink pass with fare > 0:', int(((df['ticket_type'] == 'PINK_PASS') & (df['fare_amount'] > 0)).sum()))

print('\n=== 8. HOURLY DEMAND ===')
df['hour'] = df['dt'].dt.hour
hourly = df['hour'].value_counts().sort_index()
print(hourly)

print('\n=== 9. WEEKDAY VS WEEKEND ===')
df['dow'] = df['dt'].dt.day_name()
df['is_weekend'] = df['dt'].dt.dayofweek >= 5
print(df.groupby('is_weekend')['ticket_id'].count())
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
print(df['dow'].value_counts().reindex(dow_order))

print('\n=== 10. ALIGHTING SUFFICIENCY ===')
missing_alight = df['alighting_stop_id'].isnull().sum()
pct_missing_alight = df['alighting_stop_id'].isnull().mean() * 100
print(f"Missing alighting_stop_id count: {missing_alight} ({pct_missing_alight:.2f}%)")
print(f"Missing boarding_stop_id count: {df['boarding_stop_id'].isnull().sum()}")

# Ticket type distribution
print('\n=== TICKET TYPE DISTRIBUTION ===')
print(df['ticket_type'].value_counts())
print(df['ticket_type'].value_counts(normalize=True)*100)

# GTFS Inspection
print('\n=== GTFS AUDIT ===')
routes_gtfs = pd.read_csv('data/gtfs/routes.txt')
stops_gtfs = pd.read_csv('data/gtfs/stops.txt')
trips_gtfs = pd.read_csv('data/gtfs/trips.txt')
stop_times_gtfs = pd.read_csv('data/gtfs/stop_times.txt')

print(f"GTFS Routes: {len(routes_gtfs)}")
print(f"GTFS Stops: {len(stops_gtfs)}")
print(f"GTFS Trips: {len(trips_gtfs)}")
print(f"GTFS Stop Times: {len(stop_times_gtfs)}")

# Check referential integrity between ETM and GTFS
etm_routes = set(df['route_id'].unique())
gtfs_routes_set = set(routes_gtfs['route_id'].unique())
print(f"ETM Routes in GTFS: {len(etm_routes.intersection(gtfs_routes_set))} / {len(etm_routes)}")

etm_boarding_stops = set(df['boarding_stop_id'].dropna().unique())
gtfs_stops_set = set(stops_gtfs['stop_id'].unique())
print(f"ETM Boarding Stops in GTFS: {len(etm_boarding_stops.intersection(gtfs_stops_set))} / {len(etm_boarding_stops)}")
