# TODO: Dynamic Data Integration

**Status:** In Progress  
**Owner:** Development Team  
**Created:** 2026-05-29

## Overview

This document tracks the plan for integrating realistic, dynamic mission data from the Django API into the RescueMesh frontend. The goal is to replace static/demo data with live, changing data that simulates real mission conditions.

## Completed Items

1. **API Client Infrastructure** (2026-05-29)
   - Created `frontend/src/lib/api.ts` with graceful error handling
   - Implemented `APIResult` pattern for non-throwing fetch functions
   - Added typed interfaces for all Django models
   - Created helper functions: `getUseCases()`, `getSensors()`, `getFailures()`, `getOutputs()`, `getAgentRoles()`

2. **Agent Roles Endpoint** (2026-05-29)
   - Fixed routing conflict in `backend/apps/usecases/urls.py`
   - Moved `TerrainProfileViewSet` and `AgentRoleTemplateViewSet` to top-level endpoints
   - Created `/api/v1/agent-role-templates/` and `/api/v1/terrain-profiles/`
   - Updated hardware page to fetch agent roles from Django

3. **Hardware Catalogue Page** (2026-05-29)
   - Created `/hardware` route with complete catalogue
   - Fetches sensors, failures, and agent roles from Django API
   - Graceful fallback to static data if API unavailable
   - Shows detailed warning banner indicating which endpoints failed

4. **Demo Pages API Integration** (2026-05-29)
   - Updated all 5 demo pages to use new API client
   - Implemented `APIResult` handling pattern
   - Proper error handling and 404 redirects

## In Progress 🚧

### Phase 1: Realistic Mission Simulation Data

**Goal:** Enable the demo pages to show realistic, changing mission data that simulates actual drone operations.

**Key Features to Implement:**
- [ ] **Real-time Void Map Generation** - LiDAR-generated 3D void space reconstruction
  - Show accessible areas, obstructions, and structural hazards
  - Update map progressively as drones explore
  - Use time-based or event-based simulation

- [ ] **Mission Timeline Generator** - Django service to generate realistic mission events
  - Agent deployment events
  - Movement/navigation waypoints
  - Detection events (thermal anomalies, audio signatures, device scans)
  - Hardware degradation events
  - Communication relay handoffs
  - Battery depletion and landing decisions
  - Recovery/sacrifice decisions

- [ ] **Sensor Feed Simulation** - Generate realistic sensor data streams
  - LiDAR point cloud fragments
  - Thermal image metadata
  - Audio detection events
  - WiFi/Bluetooth scan results
  - Environmental sensor readings (CO2, temperature, humidity)

- [ ] **Agent State Management** - Track and update agent states over mission time
  - Position tracking
  - Battery level progression
  - Hardware health degradation
  - Communication link quality
  - Active/degraded/failed/landed_relay state transitions

**Technical Approach (Research with ChatGPT):**
- Mission simulation engine in Django
- Procedural generation of realistic events
- Time-based or event-based progression
- Seed-based reproducibility for demos
- WebSocket integration for live updates (later phase)

### Phase 2: Interactive Data Loading States

**Goal:** Improve UX during API calls with proper loading states and skeleton screens.

**Tasks:**
- [ ] Add loading spinners for API requests
- [ ] Create skeleton screens for empty/loading states
- [ ] Add "Loading..." overlays for dashboard panels
- [ ] Implement progressive loading (show cached data while fetching updates)
- [ ] Add retry buttons for failed API requests

### Phase 3: WebSocket Integration (Django Channels)

**Goal:** Enable real-time mission updates without page refresh.

**Tasks:**
- [ ] Set up Django Channels
- [ ] Create WebSocket consumer for mission events
- [ ] Add frontend WebSocket client
- [ ] Update dashboard components to listen for live events
- [ ] Implement graceful degradation if WebSocket unavailable

### Phase 4: Mission CRUD Operations

**Goal:** Allow users to create, configure, and control missions from the frontend.

**Tasks:**
- [ ] Create mission form (use case selection, agent configuration)
- [ ] Add mission control panel (start/pause/stop simulation)
- [ ] Implement mission parameter adjustment (speed, duration, failure injection)
- [ ] Add mission saving and loading
- [ ] Create mission history/replay feature

### Phase 5: Advanced Visualizations

**Goal:** Add richer visual representations of mission data.

**Tasks:**
- [ ] 3D void map visualization (Three.js or CesiumJS)
- [ ] Point cloud viewer for LiDAR data
- [ ] Network topology graph showing relay chains
- [ ] Heatmap overlays for thermal/detection data
- [ ] Agent path visualization on 2D/3D map

## Django Data Model Enhancements Needed

### New Models to Create

1. **MissionSimulation**
   - mission (ForeignKey to Mission)
   - simulation_speed (float, default 1.0)
   - current_mission_time (float, seconds)
   - simulation_state (choices: paused, running, completed)
   - random_seed (int, for reproducible demos)

2. **MissionEvent**
   - mission (ForeignKey)
   - event_type (choices: agent_deployed, detection, state_change, comms_event, etc.)
   - mission_time (float, seconds)
   - agent (ForeignKey, nullable)
   - event_data (JSON)
   - confidence (float, 0-1)
   - human_review_required (bool)

3. **AgentTelemetry**
   - agent (ForeignKey)
   - mission_time (float)
   - position (JSON: {x, y, z})
   - battery_percent (float)
   - state (choices: same as hardware states)
   - signal_strength (float)
   - active_sensor_readings (JSON)

4. **VoidMapFragment**
   - mission (ForeignKey)
   - agent (ForeignKey)
   - captured_at (timestamp)
   - geometry (JSON or PostGIS geometry)
   - coverage_area (JSON)
   - hazard_markers (JSON array)

5. **DetectionEvent**
   - mission (ForeignKey)
   - agent (ForeignKey)
   - detection_type (choices: thermal, audio, wifi, gas, etc.)
   - location (JSON: {x, y, z})
   - confidence (float)
   - raw_data (JSON)
   - interpreted_value (string)
   - operator_reviewed (bool)
   - ai_recommendation (text)

### API Endpoints to Create

- `POST /api/v1/missions/` - Create new mission
- `GET /api/v1/missions/{id}/` - Mission detail
- `POST /api/v1/missions/{id}/start/` - Start simulation
- `POST /api/v1/missions/{id}/pause/` - Pause simulation
- `POST /api/v1/missions/{id}/stop/` - Stop simulation
- `GET /api/v1/missions/{id}/events/` - List mission events (paginated, filtered by time)
- `GET /api/v1/missions/{id}/telemetry/` - Current agent telemetry
- `GET /api/v1/missions/{id}/void-map/` - Current void map state
- `GET /api/v1/missions/{id}/detections/` - Detection events (filtered by type, confidence)
- `WS /ws/missions/{id}/` - WebSocket for live updates (Django Channels)

## Frontend Components Needing Enhancement

### Demo Dashboard Components

**Components in `frontend/src/components/demo/`:**
- [ ] `MissionOverviewPanel.astro` - Add live mission state updates
- [ ] `AgentStatusPanel.astro` - Add live agent telemetry
- [ ] `TelemetryPanel.astro` - Connect to live telemetry stream
- [ ] `MissionMapPanel.astro` - Add void map visualization
- [ ] `SensorOutputsPanel.astro` - Show live sensor readings
- [ ] `DetectionsPanel.astro` - Stream detection events
- [ ] `AiAnalystPanel.astro` - Live AI analysis updates
- [ ] `TimelinePanel.astro` - Live timeline updates
- [ ] `FailureStatePanel.astro` - Real-time failure tracking
- [ ] `MissionReportPanel.astro` - Dynamic report generation

### New Components to Create

- [ ] `MissionControlPanel.astro` - Start/pause/stop controls
- [ ] `MissionConfigForm.astro` - Configure new missions
- [ ] `VoidMapViewer.astro` - 3D void space visualization
- [ ] `NetworkTopologyGraph.astro` - Agent relay network
- [ ] `LoadingSpinner.astro` - Reusable loading indicator
- [ ] `SkeletonCard.astro` - Loading skeleton for cards
- [ ] `ErrorBanner.astro` - Reusable error display

## Research Topics (ChatGPT Collaboration)

The user is researching with ChatGPT:
1. How to generate realistic void maps from collapsed structures
2. LiDAR-generated 3D void space reconstruction
3. Showing accessible areas, obstructions, and structural hazards
4. Progressive map updates as agents explore
5. Realistic sensor data generation
6. Mission event simulation strategies

**Action Items After ChatGPT Research:**
- Document the implementation approach
- Create ADR for mission simulation architecture
- Define data schemas for void maps and sensor readings
- Plan Django model structure for geometric data
- Evaluate whether to use PostGIS or JSON for spatial data

## Testing Strategy

### Unit Tests Needed
- [ ] Mission simulation engine tests
- [ ] Event generation logic tests
- [ ] Agent state transition tests
- [ ] Telemetry data validation tests

### Integration Tests Needed
- [ ] Full mission simulation end-to-end test
- [ ] WebSocket connection and data flow test
- [ ] API endpoint integration tests
- [ ] Frontend component rendering with live data

### Demo Scenarios to Create
- [ ] Collapsed Building: Progressive void mapping demo
- [ ] Cave Rescue: Communication relay chain demo
- [ ] Flooded Structure: Amphibious agent demo
- [ ] Industrial Inspection: Gas detection and hazard mapping demo

## Dependencies and Prerequisites

### Python Packages to Add
- [ ] `django-channels` - WebSocket support
- [ ] `channels-redis` - Channel layer backend
- [ ] `numpy` - Geometric calculations
- [ ] `shapely` - Geometry operations (if using JSON geometry)
- [ ] `psycopg2-binary` - PostgreSQL adapter (for production)

### Frontend Packages to Add
- [ ] `three` - 3D visualization (if needed)
- [ ] `@cesium/engine` - Geospatial 3D (if needed)
- [ ] `d3` - Network graphs and visualizations
- [ ] WebSocket client library (native or library)

## Performance Considerations

- Mission events should be paginated (limit to last N events)
- Void map data should be incrementally loaded
- Telemetry updates should be throttled (e.g., 1Hz, not every frame)
- WebSocket messages should be compressed
- Frontend should cache and deduplicate events
- Use Redis for WebSocket channel layer in production

## Security Considerations

- Mission creation should require authentication (future)
- WebSocket connections should be authenticated
- Sensitive mission data should be access-controlled
- Rate limiting on simulation control endpoints
- Validate all simulation parameters

## Documentation Updates Needed

- [ ] Update architecture.md with simulation engine design
- [ ] Create ADR for WebSocket integration
- [ ] Document void map data format
- [ ] Create API documentation for new endpoints
- [ ] Add developer guide for creating mission scenarios

## Related Documents

- [Architecture Documentation](./architecture.md)
- [Use Cases](./use-cases.md)
- [ADR-0002: Simulation First](./decisions/ADR-0002-simulation-first.md)
- [Demo System Instructions](./.github/instructions/rescumesh_demo.md)
- [Django Instructions](./.github/instructions/django_instructions.md)

## Notes

- Keep simulation deterministic for reproducible demos (use seeds)
- Maintain graceful degradation if Django offline
- Support both live and historical mission replay
- Design for eventual integration with real drone hardware (ROS 2)
- Consider future integration with Foxglove for robotics visualization
- Plan for MCAP log export for mission data

---

**Last Updated:** 2026-05-29  
**Status:** Active Development
