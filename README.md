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
# Windows:
.venv\Scripts\activate
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

### API Endpoints

- `GET /api/v1/missions/` - List all missions
- `POST /api/v1/missions/` - Create new mission
- `GET /api/v1/missions/{id}/` - Mission details
- `POST /api/v1/missions/{id}/start/` - Start mission
- `GET /api/v1/missions/{id}/events/` - Mission events
- `GET /api/v1/agents/` - List all agents
- `POST /api/v1/agents/` - Register new agent

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

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests where appropriate
5. Update documentation
6. Submit a pull request

## Roadmap

### MVP (Current)
- [x] Astro frontend with Tailwind
- [x] Django backend with REST API
- [x] Mission and agent models
- [x] Sample use cases and fixtures
- [x] Demo mission dashboard
- [ ] Interactive islands (maps, telemetry, timeline)

### Phase 2
- [ ] WebSocket telemetry streaming
- [ ] 3D visualization (Three.js)
- [ ] AI prompt generation API
- [ ] Mission report export

### Phase 3
- [ ] PostgreSQL + PostGIS
- [ ] ROS 2 integration
- [ ] MCAP log replay
- [ ] Real hardware bridging

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
