# RescueMesh Mission Platform

**Simulation-first mission dashboard for dangerous, GPS-denied, partially inaccessible environments**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

RescueMesh is a simulation-first mission platform that demonstrates how autonomous agents (drones, ground robots, relay nodes, sensors, and AI services) cooperate to:

- Map unknown terrain in GPS-denied environments
- Search for survivors in collapsed buildings, caves, tunnels, and flooded structures
- Maintain communications through multi-hop relay networks
- Handle hardware failures gracefully
- Generate structured AI prompts for human-reviewed decision support

**This is a demonstration and training platform**, not a real-time drone control system. No physical drone hardware is required for the MVP.

## Safety and Purpose

RescueMesh is safety-focused and non-weaponised. It models autonomous mapping, sensing, communications and operator decision support for rescue, inspection, environmental and heritage exploration scenarios.

Beyond rescue and industrial inspection, RescueMesh can model archaeological and heritage exploration where fragile, inaccessible spaces must be mapped without unnecessary human entry or disturbance.

## Why Mesh Relay Communications?

In dangerous GPS-denied environments such as caves, collapsed buildings, or flooded structures, autonomous agents often lose direct contact with mission control. RescueMesh models a **mesh relay network** where agents can:

- **Relay data through nearby agents** when direct communication is blocked or degraded
- **Extend the mission reach** by deploying static relay nodes at strategic positions
- **Share mapped terrain** so one agent's discoveries help others navigate safely
- **Land and become relay nodes** when battery reserves are low or signal strength is weak
- **Continue as mission assets** even after primary failures (beacon mode, NFC-readable black box, last-known sensor data)

The platform visualises the **communication chain, agent status, map confidence, and relay network health** throughout the mission. This mesh-based approach is critical for operations where line-of-sight radio links are impossible and agents must cooperate to maintain connectivity.

## Use Cases

- **Collapsed Building Search** - Life safety operations in unstable structures
- **Cave Rescue** - Mapping and path discovery in underground systems
- **Flooded Structure** - Amphibious inspection and obstruction mapping
- **Industrial Inspection** - Confined space hazard assessment
- **Archaeological Exploration** - Non-destructive mapping of fragile heritage sites

## Key Features

### Agent-Based Architecture
Model diverse hardware types (drones, robots, sensors, relays, AI services) as cooperating agents rather than drone-only systems.

### Simulation-First
Deterministic, reproducible mission scenarios without requiring real hardware. Perfect for:
- Algorithm development
- Operator training
- Failure scenario exploration
- AI model testing

### Failure Modeling
Realistic simulation of:
- Battery degradation and drain
- Sensor failures (dust, water, impact)
- Communication loss and intermittency
- Tactical sacrifice decisions (land as relay)
- Black-box recovery scenarios

### AI Integration
Generate structured prompts for AI analysis with:
- Thermal detection analysis
- Audio pattern recognition
- WiFi/Bluetooth device scanning
- Confidence scoring
- Human review requirements

## Interoperability Philosophy

RescueMesh uses **structured, interoperable mission data** inspired by healthcare interoperability standards (HL7 FHIR, CDA), IoT standards (OGC SensorThings, W3C SOSA/SSN), and geospatial standards. Mission data is designed to be:

- **Exchangeable** - Standard formats enable data sharing across systems
- **Validated** - Schema validation ensures data consistency
- **Versioned** - API versioning supports backward compatibility
- **Explainable** - Provenance tracking shows data lineage and confidence

While RescueMesh is not a healthcare system, it applies proven interoperability principles from health data exchange to mission planning and autonomous agent coordination. This approach ensures that:

- **Sensor observations** align with semantic standards rather than ad-hoc formats
- **AI recommendations** include confidence scores, provenance metadata, and human-review flags
- **Mission reports** can integrate with emergency service workflows
- **Future emergency-to-healthcare handover** scenarios could map rescue findings into medical interoperability patterns when missions transition from search and rescue to patient care

The platform models 17 conceptual resource types (Mission, Agent, Device, Sensor, Observation, EnvironmentalReading, MediaFrame, MapArtifact, TerrainSector, RelayLink, CommunicationMode, Hazard, Detection, Alert, Recommendation, MissionEvent, Provenance) to ensure consistent data representation across the mission lifecycle.

Learn more: [Interoperability Architecture](/architecture/interoperability)

## Generated Media vs Real Mission Media

RescueMesh uses a **simulation-first approach to mission media**. Instead of requiring S3/object storage during development and demos, the platform generates synthetic media on demand:

### Demo Mode (Current)
- **Generated locally** - Images, audio clips, and spectrograms created by Python code
- **Lazy generation** - Media files generated only when requested and cached in `media/generated/`
- **No external dependencies** - Uses Pillow for images and Python's wave module for audio
- **Docker-friendly** - Self-contained with writable media directory
- **Cheap and portable** - No cloud storage costs or configuration needed

### Real Operational Mode (Future)
- **S3/Object Storage** - Captured media from actual missions stored in scalable object storage
- **Database metadata** - Mission database stores references and metadata for all media
- **Same API shape** - Frontend continues to use the same endpoints regardless of source
- **Seamless transition** - Switch from generated to real media by changing backend configuration

### Supported Generated Media Types

**Images:**
- Low-light / night vision scenes
- Thermal camera frames with hotspot detection
- Underwater / murky water views
- Industrial inspection images (pipes, corrosion)
- Dusty rubble / collapsed structure scenes
- Last-good-frame with signal degradation effects

**Audio:**
- Knocking sounds (SOS patterns, regular intervals)
- Tapping audio (higher frequency, sharper)
- Voice-like placeholder audio (modulated frequencies simulating speech)
- Static / interference
- Ambient environmental sounds (cave drips, underwater, industrial hum)

**Spectrograms:**
- Visual frequency analysis of audio clips
- Time-domain representation
- Confidence and signal quality overlays

### API Endpoints

```
GET /api/v1/missions/{mission_id}/generated-media/
    Returns metadata for all generated media associated with a mission

GET /api/v1/generated-media/{media_id}/preview/
    Serves generated image preview (PNG)

GET /api/v1/generated-media/{media_id}/audio/
    Serves generated audio file (WAV)

GET /api/v1/generated-media/{media_id}/spectrogram/
    Serves spectrogram visualization (PNG)
```

### Cache Management

Generated media is cached in `media/generated/` directory:

```
media/generated/
  images/          # Generated PNG images
  audio/           # Generated WAV audio files
  spectrograms/    # Audio visualization PNGs
```

**Clear cache:**
```bash
# Remove all generated media
rm -rf media/generated/

# Regenerate on next request (lazy generation)
```

**Docker volume:**
- Mount `media/generated` as a writable volume
- Persists generated media between container restarts
- Clear volume to force regeneration

### Why Generated Media?

1. **Development speed** - No S3 setup required for demos
2. **Reproducibility** - Same media generated for same mission scenarios
3. **Cost efficiency** - No storage costs during development
4. **Offline capability** - Works without internet or cloud dependencies
5. **Testing** - Consistent test data for frontend development
6. **Portability** - Easy to package and distribute

Generated media keeps the simulation-first philosophy intact while providing realistic-looking mission artifacts for demonstrations and development.

## Demo Routes

The platform provides two types of demo experiences:

### Static Mission Profiles (`/demo/{use-case}`)
Static overview pages showing mission objectives, agent configurations, sensor packages, risk assessments, and expected outputs using local TypeScript fallback data. These pages provide:
- Mission planning information
- Hardware and sensor specifications
- Environmental hazards and constraints
- Tactical approach recommendations
- Expected detection types

Example routes:
- `/demo/collapsed-building-search`
- `/demo/cave-rescue`
- `/demo/flooded-structure`
- `/demo/industrial-inspection`

### Live Django Simulations (`/demo/live/{use-case}`)
Interactive simulation pages connected to the Django API showing real-time mission state changes via HTTP polling. These pages provide:
- Live agent telemetry (battery, signal, location)
- Mission event timeline
- Map coverage and confidence updates
- Sensor detection events
- Hardware failure scenarios
- AI analyst summaries
- Simulation controls (start, pause, reset, speed)

Example routes:
- `/demo/live/collapsed-building-search`
- `/demo/live/cave-rescue`
- `/demo/live/flooded-structure`
- `/demo/live/industrial-inspection`

The live simulations use **deterministic state calculation** - each mission progresses the same way for a given elapsed time, making scenarios reproducible. No WebSockets or real-time infrastructure required yet.

## Technology Stack

### Frontend
- **Astro** - Static site generation with islands architecture
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type-safe interactive components

### Backend
- **Django 5.x** - Domain models and business logic
- **Django REST Framework** - RESTful APIs
- **SQLite** - Development database (PostgreSQL for production)

### Future Extensions
- **Django Channels** - WebSocket real-time telemetry
- **Three.js / CesiumJS** - 3D visualization
- **ROS 2** - Real robotics integration
- **MCAP** - Robotics log replay

## Project Structure

```
rescuemesh/
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
├── frontend/              # Astro + Tailwind + TypeScript
│   ├── src/
│   │   ├── pages/        # Static pages and routes
│   │   ├── layouts/      # Page layouts
│   │   ├── components/   # Reusable components
│   │   ├── styles/       # Global styles
│   │   └── data/         # JSON fixtures
│   └── package.json
├── backend/              # Django + DRF
│   ├── apps/
│   │   ├── missions/     # Mission management
│   │   ├── agents/       # Agent models
│   │   ├── telemetry/    # Telemetry data
│   │   ├── ai_prompts/   # AI prompt generation
│   │   └── reports/      # Mission reports
│   ├── config/           # Django settings
│   ├── manage.py
│   └── requirements.txt
├── docs/                 # Architecture docs and ADRs
├── data/                 # Sample fixtures and scenarios
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ / npm
- Git

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (Command Prompt):
.venv\Scripts\activate.bat
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:4321`

### Visit the Demo

1. Open `http://localhost:4321` in your browser
2. Navigate to **Use Cases** → **Collapsed Building Search**
3. Click **Launch Demo** to see the simulated mission dashboard

## Digital Twin Seed Data

RescueMesh supports pre-populating the database with simplified digital twin map data derived from public/open cave survey and archaeological/heritage datasets. This provides realistic mission terrain without requiring access to physical environments.

**Live tactical maps now render terrain from Django Digital Twin data where available, with automatic fallback to local layouts for use cases without seeded terrain.**

### What are Digital Twins?

Digital twins are simplified 3D representations of real-world environments stored as:
- **Terrain sectors** - Chambers, passages, junctions, shafts (with bounding boxes and metadata)
- **Paths** - Connections between sectors with distance, bearing, vertical change, and traversal risk
- **Waypoints** - Navigation points along mission routes

**Why not full point clouds?**  
Full LiDAR/photogrammetry point clouds are multi-gigabyte files unsuitable for SQL storage. Instead, we store simplified structure with references to external point cloud files when needed.

### Source Datasets

Demo data is inspired by:

1. **Migovec Resurvey Project** - Cave survey data from Slovenia (Therion/Survex formats)
   - https://github.com/tr1813/migresurvey
   - Collected by ICCC and JSPDT, 1974-2019

2. **CAVERS Dataset** - Cave SLAM data with RGB-D, LiDAR, thermal sensors (MIT License)
   - https://github.com/spaceuma/cavers/
   - DOI: https://doi.org/10.5281/zenodo.19367714

3. **Open Heritage 3D** - Cultural heritage 3D documentation
   - https://openheritage3d.org/
   - Founded by CyArk, Historic Environment Scotland, USF Libraries

4. **Maritime/Vessel Datasets** - For flooded structure scenarios
   - **NOAA Wrecks and Obstructions Database** - Shipwreck locations and vessel data (Public domain)
     - https://nauticalcharts.noaa.gov/data/wrecks-and-obstructions.html
   - **Integrated Marine Observing System (IMOS)** - ~30TB ocean measurements (Open access)
     - https://imos.aodn.org.au/
   - **BODC - British Oceanographic Data Centre** - ~22K marine data variables
     - https://www.bodc.ac.uk/data/
   - **Oil and Gas Authority Open Data (UK)** - 12,500 offshore wellbores (Open Government License)
     - https://data-ogauthority.opendata.arcgis.com/
   - **Liberty Ship Specifications** - Historical WWII cargo vessel class (Public domain)
     - https://en.wikipedia.org/wiki/Liberty_ship

5. **Industrial Facility Datasets** - For confined space and hazardous environment scenarios
   - **Swiss Apartment Models** - 42,207 apartments with 242,257 rooms (Open access)
     - https://zenodo.org/record/7070952
   - **3D Semantic City Models** - Building and facility 3D models (Varies by dataset)
     - https://github.com/OloOcki/awesome-citygml
   - **Homeland Infrastructure Foundation-Level Data (HIFLD)** - Critical infrastructure (Public domain)
     - https://hifld-geoplatform.opendata.arcgis.com/
   - **BuildData - Canadian Construction Data API** - Building and construction data (API terms)
     - https://builddata.ca/
   - **OSHA Confined Space Standards** - Safety and access standards (Public domain)
     - https://www.osha.gov/confined-spaces

### Running the Seed Command

```bash
# Seed all digital twin samples
python manage.py seed_digital_twins

# Clear existing data first
python manage.py seed_digital_twins --clear

# Import specific file
python manage.py seed_digital_twins --file migovec_sample.json
```

**Docker Usage:**
```bash
docker exec -it rescuemesh-backend python manage.py seed_digital_twins
```

### Sample Data Included

The platform includes three demonstration digital twins:

1. **`migovec_sample.json`** - Simplified cave system structure
   - 7 sectors (entrance, passages, chambers, shaft)
   - 6 paths with distance/bearing/risk data
   - 6 waypoints for route planning
   - Based on public cave survey patterns (synthetic demo)

2. **`archaeology_sample.json`** - Underground heritage site
   - 8 sectors (ceremonial chambers, artifact alcoves, burial chamber)
   - 7 paths with heritage conservation constraints
   - 7 waypoints for non-destructive documentation
   - Inspired by heritage 3D documentation best practices (synthetic demo)

3. **`flooded_vessel_sample.json`** - Flooded cargo vessel structure
   - 9 sectors (cargo holds, engine room, bridge, crew quarters, hull breach)
   - 9 paths including wade, swim, dive, sealed passages
   - 9 waypoints for amphibious robot navigation
   - Inspired by Liberty ship general specifications (synthetic demo)

4. **`industrial_facility_sample.json`** - Industrial processing facility
   - 9 sectors (utility corridors, equipment rooms, pipe corridors, tank chamber, confined space, hazard zone)
   - 9 paths with confined space entry procedures
   - 9 waypoints for hazardous environment inspection
   - Inspired by industrial spatial patterns and OSHA confined space standards (synthetic demo)

### Attribution and Sensitivity

All digital twin data includes:
- **Source name and URL**
- **License information**
- **Required attribution text**
- **Sensitivity level**: `public_demo`, `reduced_precision`, `restricted`, or `synthetic_only`

**Important:** Sample data is synthetic for demonstration purposes. No actual sensitive cave locations or archaeological sites are exposed.

### Live Tactical Map Integration

The frontend tactical maps now support three rendering modes:

1. **Django Digital Twin** - Terrain loaded from database via REST API
   - Automatic coordinate scaling from metres to SVG
   - Sector type-based visual styling
   - Metadata display (depth, elevation, hazards)
   - Source attribution badge shown on map
   
2. **Local Fallback** - Hardcoded TypeScript layouts for use cases without Digital Twin data
   - Used for Collapsed Building Search (no seeded terrain yet)
   - Badge indicates "Local Fallback" mode
   
3. **Hybrid Mode** - Digital Twin terrain + live mission state overlay
   - Agent positions and movements
   - Detection markers
   - Relay network links
   - Escalation markers

**Frontend Integration Modules:**
- `frontend/src/lib/api.ts` - Digital Twin API client functions
- `frontend/src/lib/tactical-map/digitalTwinMapAdapter.ts` - Coordinate transformation
- `frontend/src/lib/tactical-map/digitalTwinMapLoader.ts` - Async loader with caching
- `frontend/src/lib/tactical-map/useCaseTerrainBindings.ts` - Use case → site mappings

### Plan View and Route Profile

RescueMesh provides two complementary views to help operators understand mission progress:

1. **Plan View (Tactical Map)** - Top-down horizontal view
   - Shows where agents, sectors, and detections are located spatially
   - X/Y positioning in metres from local origin
   - Sector boundaries, paths, and relay networks
   - Real-time agent movement and status

2. **Route Profile (Side View)** - Vertical profile along route distance
   - X-axis: Route distance from entry point (metres)
   - Y-axis: Elevation/depth relative to origin (metres)
   - Shows how far agents have travelled into the mission
   - Visualizes vertical hazards (steep descents, depth below surface)
   - Displays relay gaps and return distance
   - Summary statistics: farthest agent, max depth, return risk, contact continuity

**Why both views?**
- The tactical map alone doesn't show how deep/high agents are or how far they've travelled
- The route profile makes it obvious when agents are 500 m, 1 km, or 2 km into a cave
- Together they provide complete situational awareness for mission control

**Use Case Examples:**
- Cave Rescue: Shows cave depth progression and distance from entrance
- Flooded Structure: Visualizes waterline and submerged zones
- Industrial Inspection: Shows platform levels and elevation changes
- Archaeological Exploration: Displays chamber depths and vertical access routes

**Route Profile Features:**
- Interactive tooltips on hover (agent position, sector details)
- Color-coded risk segments (high-risk descents, relay-supported areas)
- Reference line at entry level (z=0)
- Automatic scaling based on terrain data
- Summary panel: farthest distance, max depth, return risk, contact status

### API Endpoints

```
GET /api/v1/mapping/digital-twin-sites/
GET /api/v1/mapping/terrain-maps/
GET /api/v1/mapping/terrain-sectors/
GET /api/v1/mapping/terrain-paths/
GET /api/v1/mapping/waypoints/
```

### Learn More

See [docs/digital-twin-seed-data.md](docs/digital-twin-seed-data.md) for:
- Detailed data model documentation
- How to add new digital twin sources
- Point cloud processing guidance
- Future format support (Therion, Survex, LAS/LAZ, E57, GeoJSON, 3D Tiles)
- Licensing and sensitivity rules

## Development

### Frontend Development
- Pages: Add new `.astro` files to `frontend/src/pages/`
- Components: Create reusable components in `frontend/src/components/`
- Interactive Islands: Add React/TypeScript islands to `frontend/src/components/islands/`
- Styling: Use Tailwind utility classes (no inline styles)

### Backend Development
- Models: Add domain models to app-specific `models.py` files
- APIs: Create viewsets in `views.py` and serializers in `serializers.py`
- URLs: Register routes in app `urls.py` and main `config/urls.py`
- Migrations: Run `python manage.py makemigrations` after model changes

## API Documentation

### Live Simulation API

The live simulation API provides real-time mission state via HTTP polling (future: WebSockets).

#### Get Mission State

```http
GET /api/v1/missions/{mission_id}/state/
```

Returns complete mission state including agents, network, map, sensors, events, AI analysis, and terrain reconstruction.

**Response Structure:**

```json
{
  "mission": {
    "mission_id": "uuid",
    "name": "Mission Name",
    "use_case": "collapsed-building-search",
    "status": "running"
  },
  "simulation_clock": {
    "started_at": "2026-05-30T14:23:45Z",
    "elapsed_seconds": 245.0,
    "speed_multiplier": 10.0,
    "is_running": true
  },
  "navigation_model": {
    "coordinate_system": "local_mission_3d_grid",
    "origin_sector_id": "entry",
    "origin_label": "Entry Point",
    "origin_position": { "x": 100, "y": 240, "z": 0 },
    "units": "metres",
    "bearing_reference": "magnetic_simulated",
    "bearing_confidence": 0.75,
    "bearing_reliability": "acceptable",
    "bearing_reliability_reason": "Metal reinforcement causes moderate interference"
  },
  "agents": [
    {
      "agent_id": "drone-a",
      "name": "Scout Drone A",
      "role": "Primary mapper",
      "state": "healthy",
      "battery_percent": 85,
      "signal_strength": 72,
      "location_label": "Void Space 1",
      "position": { "x": 115.5, "y": 240, "z": 3.0 },
      "sensors": ["LiDAR", "Low-light Camera", "IMU"],
      "nfc_recovery_available": false,
      "navigation": {
        "distance_from_origin_m": 15.6,
        "straight_line_3d_distance_from_origin_m": 15.8,
        "bearing_from_origin_deg": 90.0,
        "bearing_from_origin_cardinal": "E",
        "elevation_m": 3.0,
        "depth_m": 0.0,
        "vertical_profile_label": "+3.0 m above entry (upper floor/void)",
        "depth_elevation_label": "↑3.0m"
      }
    }
  ],
  "network": {
    "base_signal_strength": 85,
    "mesh_health": 78,
    "relay_chain": ["base-station", "drone-a", "drone-b"],
    "packet_loss_percent": 5
  },
  "map": {
    "map_type": "collapsed-building-map",
    "coverage_percent": 45,
    "confidence": 0.88,
    "total_points": 125000,
    "new_points_generated": 8500,
    "mapped_sectors": ["Entry", "Corridor A", "Void Space 1"],
    "blocked_sectors": ["Collapsed Corridor B"],
    "accessible_areas": [...]
  },
  "sensors": {
    "thermal_anomalies": [...],
    "audio_events": [...],
    "device_signals": [...],
    "environmental_readings": [...]
  },
  "events": [
    {
      "type": "deployment",
      "time": "00:00:30",
      "title": "Scout Drone A deployed",
      "description": "Primary mapper initiated SLAM",
      "agent": "drone-a"
    }
  ],
  "ai_analysis": {
    "summary": "Mission progressing normally...",
    "priority_findings": ["Thermal anomaly detected..."],
    "human_review_required": true,
    "confidence": 0.78
  },
  "terrain_reconstruction": {
    "sectors": [...],
    "scan_coverage_percent": 45,
    "multi_agent_overlaps": 3
  },
  "media_feeds": [...],
  "mission_escalation": {
    "escalation_level": "normal",
    "relay_reinforcement": null
  },
  "audio_detections": [...]
}
```

#### Start/Pause/Reset Mission

```http
POST /api/v1/missions/{mission_id}/start/
POST /api/v1/missions/{mission_id}/pause/
POST /api/v1/missions/{mission_id}/reset/
```

#### Generated Media API

```http
GET /api/v1/missions/{mission_id}/generated-media/
GET /api/v1/generated-media/{media_id}/preview/
GET /api/v1/generated-media/{media_id}/audio/
GET /api/v1/generated-media/{media_id}/spectrogram/
```

### Mission State Fields

#### Navigation Model
Provides GPS-denied 3D positioning reference:
- **coordinate_system**: Local mission 3D grid
- **origin_position**: Entry point coordinates
- **bearing_reference**: Magnetic or mission north
- **bearing_confidence**: 0-1 scale
- **bearing_reliability**: good/acceptable/degraded/unreliable

#### Agent Navigation Data
Each agent includes positioning data:
- **position**: Absolute x, y, z coordinates
- **distance_from_origin_m**: 2D horizontal distance
- **straight_line_3d_distance_from_origin_m**: True 3D distance
- **bearing_from_origin_deg**: Compass bearing (0-360°)
- **bearing_from_origin_cardinal**: N, NE, E, SE, S, SW, W, NW
- **elevation_m**: Vertical offset from origin
- **depth_m**: Depth below origin (positive value)
- **depth_elevation_label**: Display label (e.g., "↓2.5m", "↑3.0m")

#### Terrain Reconstruction
Progressive sector reveal based on agent scanning:
- **sectors**: List of terrain sectors with reveal timestamps
- **scan_rules**: Which agents scanned which sectors and when
- **multi_agent_overlaps**: Count of sectors scanned by multiple agents

#### Mission Escalation
Tracks mission criticality and relay reinforcement:
- **escalation_level**: normal/elevated/critical
- **relay_reinforcement**: Details if additional relays deployed
- **trigger_reason**: Why escalation occurred
- **recommended_actions**: Operator guidance

### API Endpoints

- `GET /api/v1/missions/` - List all missions
- `POST /api/v1/missions/` - Create new mission
- `GET /api/v1/missions/{id}/` - Mission details
- `GET /api/v1/missions/{id}/state/` - **Live simulation state**
- `POST /api/v1/missions/{id}/start/` - Start mission
- `POST /api/v1/missions/{id}/pause/` - Pause mission
- `POST /api/v1/missions/{id}/reset/` - Reset mission
- `GET /api/v1/missions/{id}/events/` - Mission events
- `GET /api/v1/missions/{id}/generated-media/` - Media metadata
- `GET /api/v1/agents/` - List all agents
- `POST /api/v1/agents/` - Register new agent
- `GET /api/v1/generated-media/{id}/preview/` - Image preview
- `GET /api/v1/generated-media/{id}/audio/` - Audio file
- `GET /api/v1/generated-media/{id}/spectrogram/` - Spectrogram

## Documentation

- [Architecture](docs/architecture.md) - System design and data flow
- [Use Cases](docs/use-cases.md) - Mission scenarios and templates
- [ADR-0001](docs/decisions/ADR-0001-frontend-astro-tailwind.md) - Frontend framework decision
- [ADR-0002](docs/decisions/ADR-0002-simulation-first.md) - Simulation-first approach
- [ADR-0003](docs/decisions/ADR-0003-agent-based-model.md) - Agent-based domain model

## Sample Data

Sample data fixtures are available in the `data/` directory:

- `usecases.json` - Use case templates
- `hardware-profiles.json` - Agent hardware specifications
- `failure-scenarios.json` - Failure injection profiles
- `sample-mission-events.json` - Demo mission timeline

## Safety and Security

**Important**: This is a **simulation and decision-support dashboard**, not a real-time control system.

The platform:
- Does NOT provide unsafe autonomous control
- Does NOT bypass aviation regulations
- Does NOT weaponize drones
- Does NOT enable covert surveillance

For real-world deployment:
- Human operator review required
- Aviation compliance mandatory
- Emergency service governance
- Privacy review required
- Safety testing required

## Technology Reference Pack

RescueMesh is informed by established robotics, geospatial, sensor, rescue, and communications technologies while remaining a lightweight simulation-first demonstrator. The platform draws inspiration from industry standards and proven approaches including ROS 2 (Robot Operating System), OGC SensorThings API, Cesium 3D Tiles, underwater acoustic/optical communications, thermal imaging, and mesh networking protocols.

The **[Technology Reference Pack](docs/reference-pack.md)** documents:
- What technologies influence RescueMesh design
- Which are currently implemented vs simulated vs future candidates
- How RescueMesh relates to robotics, sensor standards, and geospatial systems
- Safety boundaries and ethical considerations
- Future integration paths for real hardware and standards-based interoperability

This reference helps contributors understand the broader context of mission platform development and shows how RescueMesh could integrate with real autonomous systems when proper governance, safety testing, and operational protocols are in place.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests where appropriate
5. Update documentation
6. Submit a pull request

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the complete development roadmap.

### Currently Implemented ✅

**Core Platform:**
- [x] Astro frontend with Tailwind CSS and TypeScript
- [x] Django backend with REST API
- [x] Mission and agent domain models
- [x] Live simulation state calculation
- [x] HTTP polling for real-time updates

**Mission Features:**
- [x] Four use case scenarios (collapsed building, cave, flooded structure, industrial)
- [x] Interactive tactical maps with SVG rendering
- [x] Agent markers with click-to-view details
- [x] Progressive sector reveal
- [x] Route-based agent positioning
- [x] Detection markers (thermal, audio, gas)

**Agent Intelligence:**
- [x] 3D positioning data (x, y, z coordinates)
- [x] Distance and bearing calculations
- [x] Compass rose with environment-specific reliability
- [x] Depth/elevation labels
- [x] Per-agent navigation intelligence
- [x] Clickable agents with survey data modal

**Telemetry & Monitoring:**
- [x] Battery and signal strength tracking
- [x] Agent state management (17+ states)
- [x] Network mesh health monitoring
- [x] Relay chain visualization
- [x] Hardware failure modeling

**Detection & Analysis:**
- [x] Thermal anomaly detection
- [x] Audio event detection (tapping, voice-like)
- [x] Environmental sensor readings
- [x] WiFi/Bluetooth device scanning
- [x] AI analysis summaries with confidence scores
- [x] Mission event timeline

**Media & Data:**
- [x] Generated media system (images, audio, spectrograms)
- [x] Media feed panels
- [x] Audio detections panel with clickable cards
- [x] Distance & Link Budget panel
- [x] Terrain reconstruction display

**Mission Management:**
- [x] Simulation controls (start, pause, reset, speed control)
- [x] Mission escalation modeling
- [x] Relay reinforcement logic
- [x] Time formatting (ISO 8601 HH:MM:SS)

### Next: Simulation Improvements 🚧

**Enhanced Visualization:**
- [ ] 3D terrain visualization (Three.js/CesiumJS)
- [ ] Point cloud rendering for LiDAR data
- [ ] Path trail animation
- [ ] Vertical profile charts
- [ ] Heat map overlays

**Advanced Simulation:**
- [ ] Configurable failure scenarios
- [ ] Custom mission builder UI
- [ ] Multi-mission coordination
- [ ] Historical mission replay
- [ ] Export mission reports (PDF/JSON)

**Data Management:**
- [ ] PostgreSQL migration for production
- [ ] PostGIS spatial queries
- [ ] Mission data persistence
- [ ] Agent telemetry history logging
- [ ] Search and filter missions

### Future: Real-Time & Robotics Extensions 🔮

**Real-Time Infrastructure:**
- [ ] Django Channels for WebSocket streaming
- [ ] Live telemetry push notifications
- [ ] Real-time map updates
- [ ] Operator collaboration features

**Physical Integration:**
- [ ] ROS 2 bridge for real robotics
- [ ] MCAP log import and replay
- [ ] PX4/ArduPilot autopilot simulation
- [ ] Gazebo physics simulation bridge
- [ ] Real drone control interfaces (research/safety-approved contexts only)

**Advanced Features:**
- [ ] Machine learning model integration
- [ ] Autonomous path planning
- [ ] SLAM algorithm testing
- [ ] Multi-agent coordination algorithms
- [ ] Cloud deployment (AWS/Azure/GCP)

**Storage & Media:**
- [ ] S3/Object storage for real mission media
- [ ] Video stream integration
- [ ] Large-scale point cloud storage
- [ ] Distributed mission data archives

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Inspired by real-world search and rescue operations
- Built with open-source technologies
- Designed for safety-first mission planning

## Contact

For questions, suggestions, or collaboration:
- [About me](https://ddeveloper72.github.io/)
- [LinkedIn](https://www.linkedin.com/in/duncanfalconer/)
- [GitHub](https://github.com/ddeveloper72)
- [GitHub Issues](https://github.com/ddeveloper72/rescuemesh-mission-platform/issues)
- [Documentation](docs/)

---

**RescueMesh Mission Platform** - Simulation-first dashboard for GPS-denied environments
