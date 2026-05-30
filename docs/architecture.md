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
