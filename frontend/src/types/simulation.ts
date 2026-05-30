/**
 * TypeScript interfaces for mission simulation state.
 * 
 * These match the Django API response structure from:
 * GET /api/v1/missions/{pk}/state/
 */

export interface MissionSimulationState {
  mission: MissionInfo;
  simulation_clock: SimulationClock;
  agents: Agent[];
  network: NetworkState;
  map: MapState;
  sensors: SensorData;
  events: MissionEvent[];
  ai_analysis: AIAnalysis;
  terrain_reconstruction?: TerrainReconstruction;
  media_feeds?: MediaFrame[];
  mission_escalation?: MissionEscalation;
}

export interface MissionInfo {
  mission_id: string;
  name: string;
  use_case: string;
  status: string;
}

export interface SimulationClock {
  started_at: string | null;
  elapsed_seconds: number;
  speed_multiplier: number;
  is_running: boolean;
}

export interface Agent {
  agent_id: string;
  name: string;
  role: string;
  state: AgentState;
  battery_percent: number;
  signal_strength: number;
  location_label: string;
  position: Position;
  sensors: string[];
  nfc_recovery_available: boolean;
}

export type AgentState =
  | 'planned'
  | 'available'
  | 'deployed'
  | 'active'
  | 'healthy'
  | 'degraded'
  | 'intermittent'
  | 'failed'
  | 'failed_primary_power'
  | 'landed'
  | 'landed_relay'
  | 'abandoned'
  | 'sacrificed'
  | 'lost'
  | 'unknown'
  | 'recoverable'
  | 'recovered'
  | 'nfc_readable'
  | 'powered_download_available'
  | 'external_power_needed'
  | 'resurrection_attempted'
  | 'resurrection_successful'
  | 'resurrection_failed'
  | 'black_box_recovered'
  | 'retired';

export interface Position {
  x: number;
  y: number;
  z: number;
}

export interface NetworkState {
  base_signal_strength: number;
  mesh_health: number;
  relay_chain: string[];
  packet_loss_percent: number;
}

export interface MapState {
  map_type: string;
  coverage_percent: number;
  confidence: number;
  total_points: number;
  new_points_generated: number;
  mapped_sectors: string[];
  blocked_sectors: string[];
  accessible_areas: AccessibleArea[];
}

export interface AccessibleArea {
  label: string;
  confidence: number;
  risk: 'low' | 'medium' | 'high' | 'critical';
}

export interface SensorData {
  thermal_anomalies: ThermalAnomaly[];
  audio_events: AudioEvent[];
  device_signals: DeviceSignal[];
  environmental_readings: EnvironmentalReading[];
}

export interface ThermalAnomaly {
  detected_at: string;
  location: string;
  temperature_delta: number;
  confidence: number;
  human_review_required: boolean;
  status: string;
}

export interface AudioEvent {
  detected_at: string;
  location: string;
  type: string;
  confidence: number;
  frequency_range?: string;
  human_review_required: boolean;
  status: string;
}

export interface DeviceSignal {
  detected_at: string;
  device_type: string;
  mac_address: string;
  signal_strength: number;
  last_seen: string;
}

export interface EnvironmentalReading {
  sensor_type:
    | 'temperature'
    | 'humidity'
    | 'pressure'
    | 'oxygen'
    | 'carbon_dioxide'
    | 'hydrogen'
    | 'methane'
    | 'air_quality'
    | 'water_depth'
    | 'contamination'
    | string;
  display_name: string;
  value: number;
  unit: string;
  status: 'normal' | 'watch' | 'warning' | 'critical';
  location_label: string;
  confidence: number;
  detected_at: number;
  timestamp?: string;
  location?: string;
}

export interface MissionEvent {
  type: string;
  time: string;
  title: string;
  description: string;
  agent: string | null;
  severity?: 'low' | 'moderate' | 'medium' | 'high' | 'critical';
}

export interface AIAnalysis {
  summary: string;
  priority_findings: string[];
  human_review_required: boolean;
  confidence: number;
}

export interface MissionEscalation {
  active: boolean;
  severity: 'none' | 'advisory' | 'warning' | 'urgent' | 'critical';
  reason: string | null;
  area_of_interest: string | null;
  contact_continuity_risk: 'stable' | 'watch' | 'high' | 'critical';
  recommended_actions: string[];
}

/**
 * Terrain reconstruction types for progressive map reveal
 */

export interface TerrainReconstruction {
  overall_confidence: number;
  overall_detail_level: number;
  total_scan_count: number;
  sectors: TacticalSectorState[];
}

export interface TacticalSectorState {
  sector_id: string;
  status:
    | 'unknown'
    | 'detected'
    | 'partially_mapped'
    | 'mapped'
    | 'high_confidence'
    | 'hazardous'
    | 'blocked';
  confidence: number; // 0-100
  detail_level: number; // 0-5
  mapped_by_agent_ids: string[];
  first_detected_at?: number;
  last_updated_at?: number;
  scan_count: number;
}

/**
 * Control request/response types
 */

export interface SpeedControlRequest {
  speed_multiplier: number;
}

export interface SpeedControlResponse {
  speed_multiplier: number;
  message: string;
  elapsed_seconds: number;
}

export interface SimulationControlResponse {
  status: string;
  message: string;
  elapsed_seconds: number;
}

/**
 * Media feed types for simulated image/video returns
 */

export interface MediaFrame {
  frame_id: string;
  agent_id: string;
  agent_name: string;
  sensor_type:
    | 'rgb_camera'
    | 'low_light_camera'
    | 'thermal_camera'
    | 'inspection_camera'
    | 'underwater_camera'
    | 'hazard_camera';
  frame_type: 'still' | 'video_placeholder' | 'thermal' | 'last_good_frame';
  status:
    | 'live'
    | 'delayed'
    | 'degraded'
    | 'lost'
    | 'last_good_frame'
    | 'thermal_detection'
    | 'ai_flagged'
    | 'human_review_required';
  mission_time: string;
  signal_quality: number;
  confidence: number;
  location_label: string;
  annotations: string[];
  description: string;
}
