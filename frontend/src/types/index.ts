/**
 * TransitSense AI TypeScript Type Definitions
 */

export interface Coordinates {
  lat: number;
  lon: number;
  name?: string;
}

export interface StopItem {
  stop_id: string;
  stop_name: string;
  stop_lat: number;
  stop_lon: number;
  zone_id?: string;
  is_metro_hub?: boolean;
  serviced_routes?: string[];
}

export interface RouteItem {
  route_id: string;
  route_short_name: string;
  route_long_name: string;
  route_type: number;
  is_ac: boolean;
  bus_capacity: number;
}

export interface CrowdAssessment {
  crowd_tier: number;
  crowd_label: string;
  color_code: string;
  mean_occupancy_ratio: number;
  seating_probability: number;
  comfort_description: string;
}

export interface IntermediateStopItem {
  stop_sequence: number;
  stop_id: string;
  stop_name: string;
  predicted_load: number;
  occupancy_ratio: number;
  crowd_tier: number;
  crowd_label: string;
}

export interface TransitLeg {
  leg_type: 'TRANSIT';
  mode: 'BUS';
  route_id: string;
  route_short_name: string;
  route_long_name: string;
  is_ac: boolean;
  from_stop_id: string;
  from_stop_name: string;
  to_stop_id: string;
  to_stop_name: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops_count: number;
  crowd_assessment: CrowdAssessment;
  intermediate_stops: IntermediateStopItem[];
  polyline: {
    type: string;
    coordinates: [number, number][];
  };
}

export interface WalkLeg {
  leg_type: 'WALK';
  duration_minutes: number;
  distance_meters: number;
  from_name: string;
  to_name: string;
  instruction: string;
}

export interface ItinerarySummary {
  total_duration_minutes: number;
  total_walking_minutes: number;
  total_walking_meters: number;
  transfers_count: number;
  estimated_fare_inr: number;
  overall_crowd_tier: number;
  overall_crowd_label: string;
  seating_probability: number;
  comfort_tradeoff?: string;
}

export interface ItineraryPlan {
  plan_id: string;
  tag: string;
  title: string;
  summary: ItinerarySummary;
  legs: (TransitLeg | WalkLeg)[];
}

export interface JourneyPlanResponse {
  status: string;
  query: Record<string, any>;
  recommended_plan_id: string;
  plans: ItineraryPlan[];
  execution_time_ms: number;
}

export interface RouteComparisonItem {
  route_id: string;
  route_short_name: string;
  route_long_name: string;
  is_ac: boolean;
  bus_capacity: number;
  departure_time: string;
  estimated_travel_minutes: number;
  predicted_load: number;
  occupancy_ratio: number;
  crowd_tier: number;
  crowd_label: string;
  seating_probability: number;
  fare_inr: number;
  comfort_advantage: string;
}

export interface RouteComparisonResponse {
  query_corridor: string;
  departure_time: string;
  recommended_route_id: string;
  routes: RouteComparisonItem[];
}

export interface NetworkOverviewStats {
  total_active_routes: number;
  total_bus_stops: number;
  october_transactions_analyzed: number;
  fleet_vehicles_tracked: number;
  peak_morning_rush: string;
  peak_evening_rush: string;
  active_ml_model: string;
  model_mae: number;
  model_wape_pct: number;
}
