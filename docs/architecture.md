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

**TelemetryFrame** (future)
- Real-time sensor readings
- Position, battery, signal strength
- Sensor-specific payloads

**DetectionEvent** (future)
- Thermal signatures
- Audio patterns
- WiFi/Bluetooth signals
- AI-generated confidence

**AIAnalysisRun** (future)
- Structured prompt generation
- AI recommendations
- Human review required flag

## Data Flow

### Mission Lifecycle

1. **Mission Setup**
   - Select use case template
   - Define terrain and hazards
   - Configure agents and sensors
   - Set failure scenarios

2. **Simulation Start**
   - Deploy agents
   - Begin event generation
   - Stream telemetry

3. **Runtime Events**
   - Agent state changes
   - Detections
   - Failures
   - AI analyses
   - Operator decisions

4. **Mission Completion**
   - Timeline export
   - Report generation
   - Black-box recovery log

### API Flow

```
Frontend Request → Django View → Serializer → Model
                                    ↓
                               Database
                                    ↓
Model → Serializer → JSON Response → Frontend
```

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

### 3D Coordinate System

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

### Compass Bearing System

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

### Navigation Data Model

**For Each Sector:**
- 3D centroid position (x, y, z)
- Distance from origin (2D and 3D)
- Bearing from origin with cardinal direction
- Elevation or depth label ("4 m below entry", "+3 m above entry")
- Vertical profile description

**For Each Path Segment:**
- Horizontal distance
- Vertical change (gain or loss)
- 3D segment distance  
- Slope percentage and incline classification
- Traversal risk based on slope
- Bearing along segment

**For Each Agent:**
- Current 3D position
- Distance from origin
- Bearing from origin
- Current heading (if moving)
- Depth or elevation
- Route distance travelled
- Estimated return distance and time
- Nearest relay (distance and bearing)
- Contact path length through relay mesh
- Communications risk

**For Each Detection:**
- 3D position
- Distance from origin (route distance and straight-line)
- Bearing from origin
- Depth or elevation context
- Contact path length to base through relays
- Communications risk assessment

### Use Case Examples

**Collapsed Building Search:**
- Model floors, stairwells, basement voids
- Upper/lower floor detection
- "Void Space 2: 63 m route, 074° ENE, ↓ 4 m below entry"

**Cave Rescue:**
- Descending tunnels and chambers
- Depth below entrance critical for planning
- "Deep Squeeze: 112 m route, 078° ENE, ↓ 11 m below entrance"

**Flooded Structure:**
- Water depth and submerged elevation
- Surface relay vs. underwater drone positions
- "Submerged zone: 3.5 m depth, contact path 45 m"

**Industrial Inspection:**
- Elevated platforms, ducts, basements
- "Pipe Gallery: 28 m route, +6 m above plant floor"

### Frontend Visualization

**Tactical Map:**
- Compass rose indicator (top-right corner)
- Color-coded by bearing reliability
- Depth/elevation chips on agent markers (↓ 4 m, ↑ 3 m)
- Tooltips with full 3D position data

**Distance & Link Budget Panel:**
- Agent distance, bearing, and elevation
- Nearest relay with bearing
- Return route distance and estimated time
- Contact path length through mesh
- Communications risk indicators

**Vertical Profile Display:**
- Simple SVG elevation chart (future feature)
- Shows route distance vs. depth/elevation
- Marks relays, hazards, detections

### Future Compatibility

This local 3D coordinate system is designed for future integration with:
- **GeoJSON-style 3D positions** - Altitude as third coordinate
- **PostGIS spatial queries** - For database-backed spatial analysis
- **ROS path/pose data** - Standard robotics coordinate frames
- **Bathymetric/depth mapping** - For underwater and flooded missions

The system remains **deterministic and simulation-first**, with no external dependencies on GPS, cloud services, or mapping APIs in the MVP.

## Communication Modes

The platform models diverse communication strategies for different mission types:

### Emergency Response Scenarios
- Real-time mesh relay networks
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
