# RescueMesh Mission Platform Architecture

## Overview

The RescueMesh Mission Platform is a **simulation-first** mission dashboard designed for dangerous, GPS-denied, partially inaccessible environments. It demonstrates how autonomous agents cooperate to map unknown terrain, search for survivors, and maintain communications in challenging conditions.

## Core Philosophy

### Simulation-First

The platform does not require real drone hardware for MVP features. All mission scenarios can be simulated with deterministic or seeded randomness, allowing:

- Reproducible testing
- Failure scenario exploration
- Training and demonstration
- AI algorithm development

### Agent-Based Architecture

Rather than building a "drone control system," we model the mission as a collection of **agents** that cooperate:

- **Drones**: Survey, detection, deep penetration
- **Ground Robots**: Rugged terrain navigation
- **Relay Nodes**: Communications bridges
- **Sensors**: Passive environmental monitoring
- **AI Services**: Analysis and recommendation
- **Base Stations**: Command and coordination

This flexibility allows future integration with diverse robotics platforms.

## Technology Stack

### Frontend
- **Astro** - Static site generation with islands architecture
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type-safe interactive components
- **Vite** - Build tooling

### Backend
- **Django 5.x** - Domain models and business logic
- **Django REST Framework** - RESTful APIs
- **PostgreSQL** (future) - Relational data
- **PostGIS** (future) - Spatial queries

### Future Extensions
- **Django Channels** - WebSocket real-time telemetry
- **Three.js / CesiumJS** - 3D visualization
- **ROS 2** - Real robotics integration
- **MCAP** - Robotics log replay

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Astro Frontend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Static Pages │  │   Islands    │  │  Dashboard   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                         REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Django Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Missions   │  │    Agents    │  │  Simulation  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Telemetry   │  │ AI Prompts   │  │   Reports    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                      Database Layer
                            │
                  ┌─────────────────────┐
                  │  SQLite / PostgreSQL │
                  └─────────────────────┘
```

## Domain Model

### Core Entities

**Mission**
- Represents a complete operational scenario
- Contains objective, terrain, timeline
- Links to all agents, events, and outputs

**Agent**
- Any autonomous or semi-autonomous participant
- Has type, state, capabilities, current location
- Tracks battery, health, and role

**MissionEvent**
- Timestamped record of state changes
- Includes detections, failures, decisions
- Structured JSON data with confidence values

**AssetStateChange**
- Tracks agent state transitions
- Records reason, location, metadata
- Enables timeline replay

**TelemetryFrame** ✅ **IMPLEMENTED**
- Live agent telemetry data
- Battery percentage, signal strength
- Position tracking (x, y, z coordinates)
- Sensor health indicators

**DetectionEvent** ✅ **IMPLEMENTED**
- Thermal anomaly signatures
- Audio patterns (tapping, voice-like, knocking)
- WiFi/Bluetooth device signals
- Environmental sensor readings (O₂, CO₂, pressure, temperature)
- AI-generated confidence scores
- Human review required flags

**AIAnalysisRun** ✅ **IMPLEMENTED**
- Structured AI summaries of mission state
- Priority findings with confidence scores
- Human review requirement flagging
- Mission escalation recommendations

## Data Flow

### Mission Lifecycle

1. **Mission Setup**
   - Select use case template (collapsed building, cave, flooded, industrial)
   - Terrain and hazards auto-configured from use case
   - Agents and sensors defined in simulation scenario
   - Failure scenarios embedded in simulation logic

2. **Simulation Start** ✅ **IMPLEMENTED**
   - Deploy agents with initial positions
   - Begin deterministic event generation
   - Initialize simulation clock with speed multiplier (1x-10x)
   - Stream telemetry via HTTP polling

3. **Runtime Events** ✅ **IMPLEMENTED**
   - Agent state changes (healthy → degraded → failed → relay)
   - Detection events (thermal, audio, gas, electrical)
   - Hardware failures (battery drain, sensor degradation)
   - AI analysis summaries with confidence scoring
   - Mission escalation and relay reinforcement
   - Operator-visible timeline updates

4. **Mission Completion**
   - Timeline export capability
   - Mission report generation (planned)
   - Black-box recovery log (NFC recovery indicators present)

### Live Simulation API Flow ✅ **IMPLEMENTED**

```
Frontend → HTTP GET /api/v1/missions/{id}/state/
                ↓
Django simulation.py service layer
                ↓
Calculate state based on elapsed time
                ↓
Generate navigation model, telemetry, detections, events, AI analysis
                ↓
JSON response → Frontend tactical map, panels, timeline
```

The simulation uses **deterministic state calculation** - each mission progresses identically for a given elapsed time, making scenarios reproducible without database state storage (MVP approach).

### Mission State Response Structure ✅ **IMPLEMENTED**

The `/api/v1/missions/{id}/state/` endpoint returns comprehensive mission state:

```json
{
  "mission": { mission metadata },
  "simulation_clock": { time, speed, status },
  "navigation_model": { coordinate system, compass reliability },
  "agents": [ array of agents with telemetry and 3D positioning ],
  "network": { mesh health, relay chains, packet loss },
  "map": { coverage, confidence, mapped sectors },
  "sensors": { thermal, audio, environmental readings },
  "events": [ chronological mission event timeline ],
  "ai_analysis": { summary, priority findings, confidence },
  "terrain_reconstruction": { sector reveal, scan tracking },
  "media_feeds": [ generated media links ],
  "mission_escalation": { escalation level, relay reinforcement },
  "audio_detections": [ audio event cards ]
}
```

See [API Documentation](../README.md#api-documentation) for complete field descriptions.

## State Management

### Agent States

Agents progress through well-defined states:

```
planned → available → deployed → active → healthy
                                        ↓
                              degraded → intermittent
                                        ↓
                            failed / landed_relay
                                        ↓
                    abandoned / recoverable / recovered
```

### Mission States

```
planned → active → paused
               ↓
        completed / aborted
```

## Failure Modeling

The platform simulates realistic failures:

### Failure Types
- Battery capacity loss
- Sensor degradation
- Communication loss
- Component failure
- Environmental damage

### Failure Triggers
- Time-based
- Sector-based
- Event-based
- Operator-triggered

### Consequences
- Reduced capability
- Tactical decisions (land as relay)
- Mission abort
- Black-box recovery

## Mission Distance Intelligence

RescueMesh uses **local 3D mission coordinates** for GPS-denied environments, providing operators with critical navigation intelligence for complex terrain where GPS is unavailable or unreliable.

### 3D Coordinate System ✅ **IMPLEMENTED**

The platform uses a **local mission origin** (typically the entry point or base station) as the reference point for all measurements:

**Coordinate Axes:**
- **x**: Local east/west or map horizontal axis (metres)
- **y**: Local north/south or map vertical axis (metres)  
- **z**: Vertical offset from origin (metres)
  - z = 0 at mission origin/entry point
  - Positive z = above the origin
  - Negative z = below the origin

**Derived Measurements:**
- **elevation_m**: Vertical offset relative to origin (positive or negative)
- **depth_m**: Positive value for positions below origin (abs(z) when z < 0)
- **route_distance_m**: Actual path distance through terrain (sum of segments)
- **straight_line_distance_m**: Direct Euclidean distance ignoring obstacles

### Compass Bearing System ✅ **IMPLEMENTED**

The platform calculates **compass bearings** for direction-finding in GPS-denied spaces:

**Bearing Convention:**
- 0° = North
- 90° = East
- 180° = South
- 270° = West

**Cardinal Directions:** 16-point compass rose (N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW)

**Compass Reliability:** Bearings include environment-aware confidence scores:
- **Good (85-100%)**: Open areas, minimal interference
- **Acceptable (65-84%)**: Moderate metal/concrete presence
- **Degraded (45-64%)**: Heavy metal structures, EMI
- **Unreliable (<45%)**: Severe interference, deep underground

Compass confidence degrades based on:
- Steel reinforcement in collapsed buildings
- Rock composition in caves
- Submerged metal in flooded structures
- Electromagnetic interference in industrial sites

### Navigation Data Model ✅ **IMPLEMENTED**

**For Each Agent:**
- Current 3D position (absolute x, y, z)
- Distance from origin (2D horizontal and 3D straight-line)
- Bearing from origin (degrees and cardinal direction)
- Current heading (if moving)
- Depth or elevation relative to origin
- Route distance travelled
- Estimated return distance and time (planned)
- Vertical profile label ("↓4m", "↑3m")

**Implementation:**
All agent navigation data calculated in `backend/apps/missions/services/simulation.py` using utilities from `backend/apps/missions/services/navigation_utils.py`.

### Frontend Visualization ✅ **IMPLEMENTED**

**Tactical Map:**
- Compass rose indicator (top-right corner)
- Color-coded by bearing reliability
- Depth/elevation chips on agent markers (↓ 4 m, ↑ 3 m)
- Clickable agents with full positioning modal
- SVG-based rendering with route-based interpolation

**Distance & Link Budget Panel:**
- Agent distance, bearing, and elevation display
- Nearest relay with bearing (planned)
- Contact path length through mesh (planned)
- Communications risk indicators

**Agent Detail Modal:**
- Operational Status section (battery, signal)
- 3D Positioning section with absolute and relative coordinates
- Payload and Sensors listing
- Survey Data Export (JSON format for external mapping tools)

## Terrain Reconstruction ✅ **IMPLEMENTED**

The platform models **progressive terrain discovery** as agents explore unknown environments.

### Sector-Based Terrain Model

Each use case defines a set of **terrain sectors** that represent physical spaces:

**Collapsed Building:**
- Entry, Corridor A/B, Void Space 1/2/3, Basement Sector, etc.

**Cave System:**
- Entrance Chamber, Main Passage, Junction, Squeeze, Deep Chamber, etc.

**Flooded Structure:**
- Entry Pool, Submerged Corridor, Underwater Junction, Deep Zone, etc.

**Industrial Facility:**
- Entry Gate, Main Floor, Elevated Walkway, Pipe Gallery, Basement, etc.

### Progressive Reveal Mechanism

Sectors are initially hidden and **revealed as agents scan them**:

```python
# Backend logic (simplified)
if elapsed_seconds >= sector_reveal_time:
    sector["revealed"] = True
    sector["scanned_by"] = agent_id
    sector["scan_timestamp"] = current_time
```

**Multi-Agent Scans:**
When multiple agents scan the same sector:
- Sector confidence increases
- Map quality improves
- Overlap count tracked for terrain_reconstruction

**Implementation Location:**
- `backend/apps/missions/services/simulation.py` - sector reveal logic
- `frontend/src/lib/tactical-map-manager.ts` - SVG sector rendering

### Scan Coverage Calculation

```python
scan_coverage_percent = (revealed_sectors / total_sectors) * 100
```

Displayed in the Mission Overview panel and map metadata.

## Mission Escalation & Relay Reinforcement ✅ **IMPLEMENTED**

The platform models **tactical mission escalation** when challenges intensify.

### Escalation Levels

**Normal:**
- All agents healthy or degraded
- Communications stable
- No critical detections

**Elevated:**
- Agent failures occurring
- Network mesh weakening
- Medium-confidence detections require investigation

**Critical:**
- Multiple agent failures
- Communications at risk
- High-confidence survivor detection
- Immediate human review required

### Relay Reinforcement

When network mesh health drops below threshold:

```python
if network_mesh_health < 60 and not relay_reinforcement_deployed:
    mission_escalation["escalation_level"] = "elevated"
    mission_escalation["relay_reinforcement"] = {
        "deployed_at": current_time,
        "reason": "Network mesh health dropped to {health}%",
        "action": "Additional relay node deployed",
        "recommended_actions": [
            "Monitor relay network stability",
            "Consider agent recall if mesh continues to degrade"
        ]
    }
```

**Implementation:**
- `backend/apps/missions/services/simulation.py` - escalation logic
- Frontend AI Analysis Panel displays escalation status and recommendations

## MeshCore vs MeshStatic ✅ **IMPLEMENTED DISTINCTION**

The platform distinguishes between **real-time mesh networking (MeshCore)** and **static mesh visualization (MeshStatic)**.

### MeshStatic (Current MVP Implementation)

**Static mesh visualization** for demonstration and training:
- **Predefined relay chains** calculated in simulation
- **Deterministic network health** based on elapsed time
- **No runtime topology changes** (chains predetermined)
- **Visualization only** - no actual network protocols
- **HTTP polling** for state updates (not real mesh packets)

**Purpose:**
- Algorithm demonstration
- Operator training
- Failure scenario exploration
- AI model development

**Implementation:**
Frontend displays relay chains from backend JSON without runtime mesh protocols.

### MeshCore (Future Real-Time Extension)

**Real mesh networking** for physical hardware integration:
- **Dynamic topology** with runtime route discovery
- **Actual mesh protocols** (e.g., Batman-adv, 802.11s, LoRa mesh)
- **Real packet routing** through agent radios
- **Link quality monitoring** from physical signal strength
- **Automatic rerouting** on agent failure
- **WebSocket streaming** of live telemetry

**Future Integration:**
- ROS 2 bridge for real robotics
- MAVLink or similar protocols
- Physical radio hardware
- Safety-approved control systems

**Current Status:** MeshCore features are **planned for 2028+** pending robotics integration and safety validation.

## Communication Modes

The platform models diverse communication strategies for different mission types:

### Emergency Response Scenarios
- Real-time mesh relay networks (MeshStatic simulation)
- Dynamic relay node deployment
- Critical telemetry streaming
- Low-latency command links

### Non-Emergency Exploration
For non-emergency exploration scenarios such as archaeological surveys and heritage site documentation, agents may use:

- **Mesh Relay Networks** - Multi-hop communication through agent chains
- **Static Relay Nodes** - Fixed communication bridges in mapped terrain
- **Tethered/Fibre Data Options** - (Future) High-bandwidth wired connections for extended operations
- **Store-and-Forward Media** - (Future) Delayed data transfer for deep penetration missions
- **NFC Black-Box Recovery** - Near-field recovery of mission logs from failed or powered-down assets

The platform remains **simulation-first** and **non-destructive** across all communication modes, prioritizing preservation and safety in heritage environments.

## Security Boundaries

This is a **simulation and decision-support dashboard**, not a real-time control system.

The platform:
- Does NOT provide unsafe autonomous control
- Does NOT bypass aviation regulations
- Does NOT weaponize drones
- Does NOT enable covert surveillance

For real-world deployment:
- Human operator review required
- Aviation compliance mandatory
- Emergency service governance
- Privacy review
- Safety testing

## Performance Considerations

### MVP Scope
- Static pages where possible
- Interactive islands for dynamic content
- JSON fixtures for demo data
- SQLite for development

### Future Optimization
- WebSocket streaming
- Database indexing
- Geospatial queries
- Point cloud streaming
- Log replay

## Extensibility

The architecture supports:
- New agent types
- Additional sensors
- Custom use cases
- Integration with real hardware
- ROS 2 bridge
- Multi-mission coordination

## References

- [Django Documentation](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Astro Documentation](https://docs.astro.build/)
- [Tailwind CSS](https://tailwindcss.com/)
- [ROS 2](https://docs.ros.org/)
- [MCAP](https://mcap.dev/)
