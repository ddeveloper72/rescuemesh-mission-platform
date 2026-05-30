# Mission State Schema Documentation

This document provides comprehensive documentation for all data structures in the RescueMesh Mission Platform live simulation API.

**API Endpoint:** `GET /api/v1/missions/{mission_id}/state/`

**Last updated:** May 30, 2026

---

## MissionState

Top-level mission state object containing all simulation data.

```typescript
interface MissionState {
  mission: Mission;
  simulation_clock: SimulationClock;
  navigation_model: NavigationModel;
  agents: AgentState[];
  network: NetworkState;
  map: MapState;
  sensors: SensorState;
  events: MissionEvent[];
  ai_analysis: AIAnalysis;
  terrain_reconstruction: TerrainReconstruction;
  media_feeds: MediaFeed[];
  mission_escalation: MissionEscalation;
  audio_detections: AudioDetection[];
  distance_and_link_budget?: DistanceAndLinkBudget;
}
```

---

## Mission

Basic mission metadata.

```typescript
interface Mission {
  mission_id: string;           // UUID
  name: string;                 // Human-readable mission name
  use_case: string;             // "collapsed-building-search" | "cave-rescue" | "flooded-structure" | "industrial-inspection"
  status: string;               // "planned" | "running" | "paused" | "completed" | "aborted"
  created_at?: string;          // ISO 8601 timestamp
  description?: string;         // Mission description
}
```

---

## SimulationClock

Tracks simulation time and speed.

```typescript
interface SimulationClock {
  started_at: string;           // ISO 8601 timestamp when simulation started
  elapsed_seconds: number;      // Total elapsed simulation time
  elapsed_time_display: string; // Formatted as "HH:MM:SS"
  speed_multiplier: number;     // Simulation speed (1.0 = real-time, 10.0 = 10x speed)
  is_running: boolean;          // Whether simulation is currently running
  paused_at?: string;           // ISO 8601 timestamp if paused
}
```

---

## NavigationModel

GPS-denied navigation reference system.

```typescript
interface NavigationModel {
  coordinate_system: string;              // "local_mission_3d_grid"
  origin_sector_id: string;               // Reference sector ID (usually "entry")
  origin_label: string;                   // Human-readable origin label
  origin_position: Position3D;            // Origin coordinates { x, y, z }
  units: string;                          // "metres"
  bearing_reference: string;              // "magnetic_simulated" | "mission_north"
  bearing_confidence: number;             // 0.0 - 1.0
  bearing_reliability: string;            // "good" | "acceptable" | "degraded" | "unreliable"
  bearing_reliability_reason: string;     // Explanation of reliability level
  compass_confidence_factors?: {
    metal_interference: boolean;
    electrical_interference: boolean;
    distance_from_origin_m: number;
    environment_type: string;
  };
}
```

### Position3D

```typescript
interface Position3D {
  x: number;  // Metres along local X axis (east/west)
  y: number;  // Metres along local Y axis (north/south)
  z: number;  // Metres along local Z axis (vertical, 0 = origin level)
}
```

---

## AgentState

Complete state for a single agent.

```typescript
interface AgentState {
  agent_id: string;                           // Unique agent identifier
  name: string;                               // Human-readable name
  type: string;                               // "drone" | "ground_robot" | "relay_node" | "sensor" | "ai_service"
  role: string;                               // Mission role description
  state: AgentStateEnum;                      // Current operational state
  battery_percent: number;                    // 0-100
  signal_strength: number;                    // 0-100
  location_label: string;                     // Human-readable location
  position: Position3D;                       // Current 3D position
  sensors: string[];                          // List of sensor types
  payload_description?: string;               // Additional payload details
  nfc_recovery_available: boolean;            // Whether NFC black-box recovery is possible
  last_state_change?: string;                 // ISO 8601 timestamp of last state change
  state_reason?: string;                      // Explanation for current state
  navigation: AgentNavigation;                // Navigation intelligence data
}
```

### AgentStateEnum

```typescript
type AgentStateEnum =
  | "planned"
  | "available"
  | "deployed"
  | "active"
  | "healthy"
  | "degraded"
  | "intermittent"
  | "failed"
  | "failed_primary_power"
  | "landed"
  | "landed_relay"
  | "abandoned"
  | "sacrificed"
  | "lost"
  | "unknown"
  | "recoverable"
  | "recovered"
  | "nfc_readable"
  | "powered_download_available"
  | "retired";
```

### AgentNavigation

```typescript
interface AgentNavigation {
  distance_from_origin_m: number;                     // 2D horizontal distance
  straight_line_3d_distance_from_origin_m: number;    // True 3D distance ignoring obstacles
  bearing_from_origin_deg: number;                    // 0-360 degrees
  bearing_from_origin_cardinal: string;               // "N" | "NNE" | "NE" | "ENE" | "E" | ...
  elevation_m: number;                                // Vertical offset from origin (can be negative)
  depth_m: number;                                    // Positive value for depth below origin
  vertical_profile_label: string;                     // E.g., "+3.0 m above entry (upper floor/void)"
  depth_elevation_label: string;                      // E.g., "↑3.0m" or "↓2.5m"
  route_distance_m?: number;                          // Actual path distance (future)
  estimated_return_distance_m?: number;               // Estimated return path (future)
  nearest_relay?: {
    relay_id: string;
    distance_m: number;
    bearing_deg: number;
  };
  contact_path_length_m?: number;                     // Total distance through relay mesh (future)
}
```

---

## NetworkState

Communication network health and topology.

```typescript
interface NetworkState {
  base_signal_strength: number;       // 0-100, signal at base station
  mesh_health: number;                // 0-100, overall network health
  relay_chain: string[];              // Array of agent IDs forming relay path
  packet_loss_percent: number;        // 0-100, estimated packet loss
  active_relays?: number;             // Count of agents in relay mode
  max_hop_count?: number;             // Maximum hops from base to furthest agent
}
```

---

## MapState

Terrain mapping progress and confidence.

```typescript
interface MapState {
  map_type: string;                   // Use case specific map type
  coverage_percent: number;           // 0-100, percentage of terrain mapped
  confidence: number;                 // 0.0-1.0, map quality confidence
  total_points: number;               // Total LiDAR points (simulated)
  new_points_generated: number;       // New points this update
  mapped_sectors: string[];           // List of fully mapped sector names
  blocked_sectors: string[];          // Sectors identified as inaccessible
  accessible_areas: TerrainSector[];  // Accessible terrain sectors
}
```

---

## SensorState

Aggregated sensor readings from all agents.

```typescript
interface SensorState {
  thermal_anomalies: ThermalAnomaly[];
  audio_events: AudioEvent[];
  device_signals: DeviceSignal[];
  environmental_readings: EnvironmentalReading[];
}
```

### ThermalAnomaly

```typescript
interface ThermalAnomaly {
  id: string;
  agent_id: string;
  timestamp: string;                  // ISO 8601
  position: Position3D;
  temperature_celsius: number;
  confidence: number;                 // 0.0-1.0
  description: string;
}
```

### AudioEvent

```typescript
interface AudioEvent {
  id: string;
  agent_id: string;
  timestamp: string;                  // ISO 8601
  position: Position3D;
  event_type: string;                 // "tapping" | "voice-like" | "knocking" | "ambient"
  frequency_range: string;
  confidence: number;                 // 0.0-1.0
  description: string;
  media_id?: string;                  // Link to generated audio media
}
```

### DeviceSignal

```typescript
interface DeviceSignal {
  id: string;
  agent_id: string;
  timestamp: string;                  // ISO 8601
  position: Position3D;
  signal_type: string;                // "wifi" | "bluetooth" | "cellular"
  device_identifier: string;
  signal_strength: number;            // RSSI or equivalent
  confidence: number;                 // 0.0-1.0
}
```

---

## EnvironmentalReading

Environmental sensor data point.

```typescript
interface EnvironmentalReading {
  id: string;
  agent_id: string;
  timestamp: string;                  // ISO 8601
  position: Position3D;
  sensor_type: string;                // "temperature" | "humidity" | "pressure" | "o2" | "co2" | "methane" | "co"
  value: number;
  unit: string;                       // "celsius" | "percent" | "hPa" | "ppm" | "percent_o2"
  threshold_status?: string;          // "normal" | "warning" | "critical"
  description?: string;
}
```

---

## MissionEvent

Timestamped mission event for timeline.

```typescript
interface MissionEvent {
  id: string;
  type: string;                       // "deployment" | "detection" | "failure" | "state_change" | "escalation"
  time: string;                       // Formatted elapsed time "HH:MM:SS"
  timestamp: string;                  // ISO 8601 absolute timestamp
  title: string;                      // Event title
  description: string;                // Event description
  agent?: string;                     // Associated agent ID
  severity?: string;                  // "info" | "warning" | "critical"
  location_label?: string;
  position?: Position3D;
}
```

---

## AIAnalysis

AI-generated mission analysis.

```typescript
interface AIAnalysis {
  summary: string;                    // Natural language mission summary
  priority_findings: string[];        // Array of priority observations
  human_review_required: boolean;     // Whether human review is needed
  confidence: number;                 // 0.0-1.0, overall analysis confidence
  generated_at?: string;              // ISO 8601 timestamp
  model_version?: string;             // AI model identifier
  recommendations?: string[];         // Tactical recommendations
}
```

---

## TerrainReconstruction

Progressive terrain reveal and scanning data.

```typescript
interface TerrainReconstruction {
  sectors: TerrainSector[];
  scan_coverage_percent: number;      // 0-100
  multi_agent_overlaps: number;       // Count of sectors scanned by multiple agents
  scan_rules?: ScanRule[];            // Which agents scanned which sectors
}
```

### TerrainSector

```typescript
interface TerrainSector {
  sector_id: string;
  sector_name: string;
  centroid: Position3D;
  revealed: boolean;                  // Whether sector is visible on map
  scanned_by?: string;                // Agent ID that scanned this sector
  scan_timestamp?: string;            // ISO 8601 timestamp of scan
  sector_type?: string;               // "accessible" | "blocked" | "void" | "water" | "hazard"
  confidence?: number;                // 0.0-1.0, map confidence for this sector
}
```

### ScanRule

```typescript
interface ScanRule {
  agent_id: string;
  sector_id: string;
  reveal_time_seconds: number;        // Elapsed time when sector revealed
}
```

---

## MediaFeed

Reference to generated or captured media.

```typescript
interface MediaFeed {
  media_id: string;
  agent_id: string;
  media_type: string;                 // "image" | "audio" | "spectrogram"
  captured_at: string;                // ISO 8601 timestamp
  location_label: string;
  position: Position3D;
  preview_url: string;                // URL to preview/thumbnail
  full_url?: string;                  // URL to full resolution
  description: string;
  confidence?: number;                // 0.0-1.0, quality/relevance confidence
  status?: string;                    // "generating" | "ready" | "error"
}
```

---

## AudioDetection

Audio detection event with media reference.

```typescript
interface AudioDetection {
  id: string;
  agent_id: string;
  time: string;                       // Formatted elapsed time "HH:MM:SS"
  timestamp: string;                  // ISO 8601 absolute timestamp
  event_type: string;                 // "tapping" | "voice-like" | "knocking"
  frequency_range: string;
  confidence: number;                 // 0.0-1.0
  location_label: string;
  position: Position3D;
  distance_from_origin_m: number;
  bearing_from_origin_deg: number;
  bearing_cardinal: string;
  media_id?: string;                  // Generated audio media reference
  spectrogram_id?: string;            // Generated spectrogram media reference
}
```

---

## MissionEscalation

Mission escalation state and relay reinforcement.

```typescript
interface MissionEscalation {
  escalation_level: string;           // "normal" | "elevated" | "critical"
  relay_reinforcement: RelayReinforcement | null;
  trigger_reason?: string;            // Why escalation occurred
  escalated_at?: string;              // ISO 8601 timestamp
  recommended_actions?: string[];     // Operator guidance
}
```

### RelayReinforcement

```typescript
interface RelayReinforcement {
  deployed_at: string;                // Formatted elapsed time "HH:MM:SS"
  timestamp: string;                  // ISO 8601 absolute timestamp
  reason: string;                     // Why reinforcement deployed
  action: string;                     // What action was taken
  affected_agents?: string[];         // Agent IDs affected
  recommended_actions?: string[];     // Follow-up recommendations
}
```

---

## DistanceAndLinkBudget

Distance tracking and communications budget (future enhancement).

```typescript
interface DistanceAndLinkBudget {
  agents: AgentLinkBudget[];
  weakest_link?: {
    from_agent: string;
    to_agent: string;
    signal_strength: number;
    risk_level: string;               // "low" | "medium" | "high" | "critical"
  };
}
```

### AgentLinkBudget

```typescript
interface AgentLinkBudget {
  agent_id: string;
  distance_from_base_m: number;
  contact_path_length_m: number;      // Total distance through relay chain
  hop_count: number;                  // Number of relay hops
  estimated_return_time_seconds: number;
  link_quality: number;               // 0.0-1.0
  risk_assessment: string;            // "acceptable" | "marginal" | "critical"
}
```

---

## CommunicationMode

Communication strategy for mission type.

```typescript
interface CommunicationMode {
  mode: string;                       // "mesh_relay" | "static_relay" | "tethered" | "store_forward" | "nfc_recovery"
  description: string;
  suitable_for: string[];             // Mission types this mode suits
  latency_profile: string;            // "real-time" | "near-real-time" | "delayed" | "post-mission"
  bandwidth_profile: string;          // "low" | "medium" | "high"
}
```

---

## Usage Examples

### Fetching Mission State

```typescript
const response = await fetch(`/api/v1/missions/${missionId}/state/`);
const state: MissionState = await response.json();

// Access agents
state.agents.forEach(agent => {
  console.log(`${agent.name} at ${agent.position.x}, ${agent.position.y}, ${agent.position.z}`);
  console.log(`Battery: ${agent.battery_percent}%, Signal: ${agent.signal_strength}%`);
  console.log(`Distance from origin: ${agent.navigation.distance_from_origin_m}m`);
});

// Check mission escalation
if (state.mission_escalation.escalation_level !== "normal") {
  console.warn(`Mission escalated to ${state.mission_escalation.escalation_level}`);
  console.warn(`Reason: ${state.mission_escalation.trigger_reason}`);
}

// Map coverage
console.log(`Map coverage: ${state.map.coverage_percent}%`);
console.log(`Mapped sectors: ${state.map.mapped_sectors.join(", ")}`);
```

---

## Schema Versioning

**Current Version:** 1.0.0 (May 2026)

**Backward Compatibility:**
- Optional fields marked with `?` in TypeScript interfaces
- New fields added with default values
- Deprecated fields maintained for 2 minor versions
- Breaking changes reserved for major version increments

**Validation:**
- All timestamps in ISO 8601 format
- Confidence values between 0.0 and 1.0
- Percentages between 0 and 100
- Positions in metres relative to origin

---

## See Also

- [Architecture Documentation](architecture.md)
- [API Documentation](../README.md#api-documentation)
- [Use Cases](use-cases.md)
- [Next Work Items](next-work-items.md)
