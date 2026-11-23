/**
 * TransitSense AI API Client
 */

import { 
  RouteItem, 
  StopItem, 
  JourneyPlanResponse, 
  RouteComparisonResponse, 
  NetworkOverviewStats 
} from '../types';

const BASE_URL = '/api/v1';

export async function fetchRoutes(): Promise<RouteItem[]> {
  const res = await fetch(`${BASE_URL}/routes`);
  if (!res.ok) throw new Error('Failed to fetch routes');
  return res.json();
}

export async function searchStops(query: string, limit = 20): Promise<StopItem[]> {
  const res = await fetch(`${BASE_URL}/stops/search?query=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error('Failed to search stops');
  return res.json();
}

export async function planJourney(payload: {
  origin: { lat: number; lon: number; name?: string };
  destination: { lat: number; lon: number; name?: string };
  departure_time: string;
  preference: string;
  max_walk_meters?: number;
  max_transfers?: number;
}): Promise<JourneyPlanResponse> {
  const res = await fetch(`${BASE_URL}/journey/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to compute journey plan');
  }
  return res.json();
}

export async function compareRoutes(routeIds: string, departureTime: string): Promise<RouteComparisonResponse> {
  const res = await fetch(`${BASE_URL}/routes/compare?route_ids=${encodeURIComponent(routeIds)}&departure_time=${encodeURIComponent(departureTime)}`);
  if (!res.ok) throw new Error('Failed to compare routes');
  return res.json();
}

export async function fetchCrowdForecast(routeId: string, departureTime: string) {
  const res = await fetch(`${BASE_URL}/routes/${routeId}/crowd-forecast?departure_time=${encodeURIComponent(departureTime)}`);
  if (!res.ok) throw new Error('Failed to fetch crowd forecast');
  return res.json();
}

export async function fetchNetworkHeatmap(hour: number, isWeekend: boolean) {
  const res = await fetch(`${BASE_URL}/crowd/network-heatmap?hour=${hour}&is_weekend=${isWeekend}`);
  if (!res.ok) throw new Error('Failed to fetch network heatmap');
  return res.json();
}

export async function fetchDashboardAnalytics(): Promise<NetworkOverviewStats> {
  const res = await fetch(`${BASE_URL}/analytics/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}
