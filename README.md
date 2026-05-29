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

## Use Cases

- 🏢 **Collapsed Building Search** - Life safety operations in unstable structures
- 🕳️ **Cave Rescue** - Mapping and path discovery in underground systems
- 🌊 **Flooded Structure** - Amphibious inspection and obstruction mapping
- 🏭 **Industrial Inspection** - Confined space hazard assessment

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
- ❌ Does NOT provide unsafe autonomous control
- ❌ Does NOT bypass aviation regulations
- ❌ Does NOT weaponize drones
- ❌ Does NOT enable covert surveillance

For real-world deployment:
- ✅ Human operator review required
- ✅ Aviation compliance mandatory
- ✅ Emergency service governance
- ✅ Privacy review required
- ✅ Safety testing required

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
- ✅ Astro frontend with Tailwind
- ✅ Django backend with REST API
- ✅ Mission and agent models
- ✅ Sample use cases and fixtures
- ✅ Demo mission dashboard
- ⬜ Interactive islands (maps, telemetry, timeline)

### Phase 2
- ⬜ WebSocket telemetry streaming
- ⬜ 3D visualization (Three.js)
- ⬜ AI prompt generation API
- ⬜ Mission report export

### Phase 3
- ⬜ PostgreSQL + PostGIS
- ⬜ ROS 2 integration
- ⬜ MCAP log replay
- ⬜ Real hardware bridging

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Inspired by real-world search and rescue operations
- Built with open-source technologies
- Designed for safety-first mission planning

## Contact

For questions, suggestions, or collaboration:
- [LinkedIn](https://www.linkedin.com/in/duncanfalconer/)
- [GitHub](https://github.com/ddeveloper72)
- [GitHub Issues](https://github.com/ddeveloper72/rescuemesh-mission-platform/issues)
- [Documentation](docs/)

---

**RescueMesh Mission Platform** - Simulation-first dashboard for GPS-denied environments
