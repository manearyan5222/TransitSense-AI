import pandas as pd
import numpy as np

df_raw = pd.read_csv('data/raw/delhi_etm_october_2026.csv')
df_clean = pd.read_csv('data/processed/cleaned_etm_october_2026.csv')
df_recon = pd.read_csv('data/processed/reconstructed_segment_crowd.csv')

print('=== 1. RAW DATASET STATS ===')
print(f'Raw total records: {len(df_raw):,}')
print(f'Missing alighting_stop_id: {df_raw["alighting_stop_id"].isnull().sum():,} ({df_raw["alighting_stop_id"].isnull().mean()*100:.2f}%)')
print(f'Missing bus_id: {df_raw["bus_id"].isnull().sum():,} ({df_raw["bus_id"].isnull().mean()*100:.2f}%)')
print(f'Missing lat/lon: {df_raw["lat"].isnull().sum():,} ({df_raw["lat"].isnull().mean()*100:.2f}%)')
print(f'Pink passes: {(df_raw["ticket_type"] == "PINK_PASS").sum():,} ({(df_raw["ticket_type"] == "PINK_PASS").mean()*100:.2f}%)')
print(f'Duplicates in raw ticket_id: {df_raw["ticket_id"].duplicated().sum():,}')
print(f'Total tickets: {len(df_raw):,}, Total passengers represented: {df_raw["passenger_count"].sum():,}')

print('\n=== 2. CLEANED DATASET STATS ===')
print(f'Cleaned total records: {len(df_clean):,}')
print(f'Retained percentage: {len(df_clean)/len(df_raw)*100:.2f}%')
print(f'Total passengers in cleaned dataset: {df_clean["passenger_count"].sum():,}')

print('\n=== 3. RECONSTRUCTED SEGMENTS STATS ===')
print(f'Total reconstructed segments: {len(df_recon):,}')
print(f'Min in_vehicle_load: {df_recon["in_vehicle_load"].min()}')
print(f'Max in_vehicle_load: {df_recon["in_vehicle_load"].max()}')
print(f'Zero load count: {(df_recon["in_vehicle_load"] == 0).sum():,} ({(df_recon["in_vehicle_load"] == 0).mean()*100:.2f}%)')
cap_exceeded = (df_recon["in_vehicle_load"] >= df_recon["bus_capacity"]).sum()
print(f'Segments at/above nominal capacity: {cap_exceeded:,} ({cap_exceeded/len(df_recon)*100:.2f}%)')
crush_cap = (df_recon["in_vehicle_load"] == (df_recon["bus_capacity"]*1.5).astype(int)).sum()
print(f'Segments hitting 1.5x physical crush clamp: {crush_cap:,} ({crush_cap/len(df_recon)*100:.2f}%)')
print(f'Total boardings across all segments: {df_recon["boardings"].sum():,}')
print(f'Total alightings across all segments: {df_recon["alightings"].sum():,}')
net_imbalance = df_recon["boardings"].sum() - df_recon["alightings"].sum()
print(f'Net flow imbalance (Total boardings - Total alightings): {net_imbalance:,}')

print('\n=== 4. TRIP BOUNDARY CONDITIONS ===')
# Group by trip and check start and end load
trips = df_recon.groupby('trip_id')
trip_starts = df_recon[df_recon['stop_sequence'] == 1]
print(f'Trips starting with load == boardings: {(trip_starts["in_vehicle_load"] == trip_starts["boardings"]).sum()}/{len(trip_starts)}')
max_seq_per_trip = df_recon.groupby('trip_id')['stop_sequence'].max().reset_index()
trip_ends = pd.merge(df_recon, max_seq_per_trip, on=['trip_id', 'stop_sequence'])
print(f'Trips ending with load == 0 (conservation complete): {(trip_ends["in_vehicle_load"] == 0).sum()}/{len(trip_ends)}')
print(f'Trips ending with residual load > 0: {(trip_ends["in_vehicle_load"] > 0).sum()}/{len(trip_ends)}')
if (trip_ends["in_vehicle_load"] > 0).sum() > 0:
    print('Sample residual end loads:', trip_ends[trip_ends["in_vehicle_load"] > 0]["in_vehicle_load"].describe())
