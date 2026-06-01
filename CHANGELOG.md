# RescueMesh Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive pan/zoom functionality for tactical maps
  - Mouse drag to pan
  - Mouse wheel to zoom
  - Touch gesture support
  - UI controls (zoom in/out, reset view)
  - Zoom range: 0.5x to 5x
- Network connection visualization between agents and relays
  - Live communication mesh topology
  - Signal strength color coding (green/yellow/red)
  - Automatic routing through active relay chains
  - Bypasses sacrificed/failed relay nodes
- Fixed viewport UI elements (compass, legend, controls)
  - North indicator stays fixed during pan/zoom
  - Legend overlay at bottom-left
  - Zoom controls at top-right
- Adaptive aspect ratio scaling for tactical maps
  - Handles extreme aspect ratios (>4:1 or <0.25:1)
  - Independent X/Y scaling for wide/tall terrains
  - Vertical centering in viewport
- Label collision detection and auto-spacing for sector labels

### Changed
- Tactical map rendering now uses SVG transform groups for pan/zoom
- Network connections only show active communication paths
- Sacrificed agents are marked visually but excluded from network routing
- Compass position adjusted to avoid overlap with zoom controls

### Fixed
- Map clustering issue with extreme aspect ratio terrains (e.g., flooded vessel)
- Map positioning now centered vertically in tactical viewport
- Network connections were invisible due to 0% opacity on sacrificed agents
- Compass/north indicator moving with pan/zoom (now fixed to viewport)
- Label overlap on closely spaced sectors

### Technical
- New module: `tactical-map-pan-zoom.ts` for interactive map controls
- Enhanced `digitalTwinMapAdapter.ts` with aspect ratio detection
- Updated `tactical-map-manager.ts` with active-only network rendering
- SVG structure reorganized: pannable content vs fixed viewport elements

### Initial Project Structure
- Initial project structure
- Astro frontend with Tailwind CSS and TypeScript
- Django backend with REST API
- Mission and agent domain models
- Sample use cases (collapsed building, cave, flooded structure, industrial)
- Hardware profile fixtures
- Failure scenario modeling
- Documentation structure with ADRs
- Demo mission dashboard
- Architecture documentation

### Frontend
- Landing page with use case cards
- Architecture page
- Collapsed building use case page
- Demo mission dashboard with simulated data
- Base and dashboard layouts
- Tailwind custom color scheme

### Backend
- Mission management app
- Agent management app
- REST API endpoints
- Django admin configuration
- SQLite database setup

### Documentation
- Architecture overview
- Use case definitions
- ADR-0001: Frontend framework selection
- ADR-0002: Simulation-first approach
- ADR-0003: Agent-based domain model
- README with quick start guide

## [0.1.0] - 2026-05-29

### Initial Release
- Project scaffolding
- Core architecture
- MVP foundation
