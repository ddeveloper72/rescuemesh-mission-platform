# GitHub Copilot Instructions — RescueMesh Mission Platform

> Repository location: place this file at `.github/copilot-instructions.md`.
>
> Project codename: **RescueMesh Mission Platform**
>
> Preferred MVP frontend: **Astro + Tailwind CSS + TypeScript**
>
> Backend/API: **Django + Django REST Framework**
>
> Live telemetry later: **Django Channels / WebSockets**
>
> Spatial data later: **PostgreSQL + PostGIS**

---

## 1. Project purpose

Build a simulation-first mission dashboard for dangerous, GPS-denied, partially inaccessible environments such as:

- collapsed buildings;
- cave systems;
- tunnels;
- flooded or partially flooded structures;
- industrial confined spaces;
- hazardous terrain.

The platform demonstrates how autonomous agents such as drones, relay nodes, ground robots, amphibious robots, passive sensors, and AI analyst services can cooperate to:

- map unknown terrain;
- share map coverage between agents;
- relay communications through a terrain;
- search for survivors or hazards;
- simulate sensor feeds;
- simulate hardware degradation, intermittent failure, and complete failure;
- show where hardware is active, degraded, abandoned, sacrificed, recoverable, or left behind;
- generate structured prompts or command packages for AI platforms;
- produce a mission timeline and after-action report.

The MVP is a **dashboard and digital-twin simulation**, not a real drone-control system. Do not assume physical drone hardware is available.

---

## 2. Core design principle

Model the system as an **agent-based mission platform**, not as a drone-only application.

An `Agent` may be:

- a drone;
- a ground robot;
- an amphibious robot;
- a static relay node;
- a passive sensor;
- a human rescuer;
- a base station;
- an AI analyst service.

An `Asset` may be:

- a complete agent;
- a component attached to an agent;
- a dropped relay;
- a sensor package;
- a black-box recovery module;
- an NFC-readable identity/recovery module.

This keeps the architecture flexible for future robotics integration.

---

## 3. Preferred MVP architecture

Use the following shape unless the user explicitly changes direction:

```text
rescuemesh/
  .github/
    copilot-instructions.md
  frontend/
    Astro + Tailwind CSS + TypeScript
  backend/
    Django + Django REST Framework
  docs/
    architecture notes, ADRs, diagrams, use-case notes
  data/
    sample missions, use cases, hardware profiles, failure scenarios
```

Recommended runtime responsibilities:

```text
Astro frontend
  - landing page
  - use-case pages
  - static documentation pages
  - mission dashboard shell
  - interactive islands for maps, telemetry, timeline and AI panels

Django backend
  - domain models
  - API endpoints
  - mission simulation engine
  - prompt-generation service
  - mission event generator
  - data persistence

Django Channels later
  - WebSocket telemetry stream
  - mission event stream
  - simulated live dashboard updates

PostgreSQL/PostGIS later
  - mission zones
  - agent positions
  - route geometry
  - terrain sectors
  - detection locations
```

---

## 4. Frontend rules: Astro + Tailwind

Use **Astro** as the frontend shell for the MVP.

Use **Tailwind CSS** for styling.

Use **TypeScript** for interactive components.

Use Astro’s island model for interactive sections. Keep most pages static or server-rendered where possible. Hydrate only the components that require browser-side behaviour.

Good candidates for interactive islands:

- `MissionMap`;
- `TelemetryPanel`;
- `HardwareStatePanel`;
- `MissionTimeline`;
- `SensorFeedPanel`;
- `AiAnalystPanel`;
- `NetworkGraphPanel`;
- `FailureInjectionPanel`.

Avoid building the entire frontend as a heavy single-page application unless the project later becomes a full operational command centre.

### Suggested frontend structure

```text
frontend/
  src/
    pages/
      index.astro
      architecture.astro
      use-cases/
        collapsed-building.astro
        cave-rescue.astro
        flooded-structure.astro
        industrial-inspection.astro
      missions/
        demo.astro
      hardware/
        index.astro
    layouts/
      BaseLayout.astro
      DashboardLayout.astro
    components/
      common/
      usecases/
      hardware/
      dashboard/
    components/islands/
      MissionMap.tsx
      TelemetryPanel.tsx
      HardwareStatePanel.tsx
      MissionTimeline.tsx
      SensorFeedPanel.tsx
      AiAnalystPanel.tsx
      NetworkGraphPanel.tsx
      FailureInjectionPanel.tsx
    data/
      usecases.json
      hardware-profiles.json
      failure-scenarios.json
      sample-mission-events.json
    styles/
      global.css
```

### Tailwind conventions

- Prefer Tailwind utility classes for layout and responsive design.
- Extract repeated patterns into Astro or TypeScript components.
- Do not use inline `style="..."` attributes unless absolutely unavoidable.
- Keep theme tokens and repeated design decisions centralised.
- Use semantic component names, not visual-only names.
- Maintain accessible contrast, focus states, keyboard navigation, and readable typography.

---

## 5. Backend rules: Django + DRF

Use Django for the domain model and REST API.

Use Django REST Framework for APIs.

Keep backend logic domain-oriented and testable. Avoid placing important business logic directly inside views.

Suggested Django apps:

```text
backend/
  apps/
    accounts/
    missions/
    usecases/
    agents/
    assets/
    sensors/
    telemetry/
    mapping/
    faults/
    ai_prompts/
    ai_results/
    reports/
```

Recommended domain objects:

```text
Mission
UseCaseTemplate
MissionScenario
Agent
HardwareAsset
HardwareComponent
SensorPackage
TelemetryFrame
MissionEvent
MapArtifact
DetectionEvent
FailureProfile
FaultInjectionEvent
AssetStateChange
AIAnalysisRun
OperatorDecision
MissionReport
```

API design:

- Use clear REST endpoints for mission setup, mission events, hardware inventory, simulated telemetry, and generated AI prompts.
- Version APIs when the schema becomes non-trivial, for example `/api/v1/...`.
- Return JSON with stable keys.
- Include IDs, timestamps, source agent IDs, confidence values, and schema versions in mission event payloads.
- Keep simulation data deterministic when a seed is provided.

---

## 6. Simulation-first rule

Do not require real drone hardware for MVP features.

Build the platform so it can simulate:

- mission start and stop;
- agent movement;
- battery drain;
- signal strength and dropouts;
- map coverage;
- sensor readings;
- detection events;
- hardware degradation;
- intermittent failure;
- complete failure;
- left-behind relay nodes or drones;
- AI analysis results;
- operator decisions.

Simulation should be reproducible. Prefer seeded scenarios stored as JSON fixtures or database records.

Example simulation event:

```json
{
  "event_type": "asset_state_change",
  "mission_id": "mission-demo-001",
  "agent_id": "drone-b",
  "timestamp": "2026-05-29T12:14:30Z",
  "previous_state": "active",
  "new_state": "landed_relay",
  "reason": "battery below return threshold and relay value is high",
  "confidence": 0.91
}
```

---

## 7. Use-case themes

Each use case should define:

- mission objective;
- terrain type;
- expected hazards;
- recommended agents;
- recommended sensors;
- communications assumptions;
- failure risks;
- performance expectations;
- expected outputs;
- AI prompt templates;
- report sections.

Example use cases:

```text
Collapsed Building Search
  - priority: life safety
  - sensors: LiDAR, thermal, microphone array, CO2, WiFi/Bluetooth scan
  - risks: dust, unstable voids, communication loss, battery drain
  - outputs: void map, thermal anomalies, voice-like audio, survivor probability

Cave Rescue
  - priority: mapping and path discovery
  - sensors: LiDAR, IMU, temperature, humidity, audio
  - risks: GPS denial, radio attenuation, narrow passages, water
  - outputs: tunnel map, safe route estimate, relay placement map

Flooded Structure
  - priority: amphibious inspection and obstruction mapping
  - sensors: pressure, sonar, temperature, camera, water-quality sensors
  - risks: water ingress, corrosion, low visibility, buoyancy problems
  - outputs: water-depth model, obstruction map, recoverable asset list
```

---

## 8. Hardware state model

Every agent and important component should have a state.

Recommended states:

```text
planned
available
deployed
active
healthy
degraded
intermittent
failed
failed_primary_power
landed
landed_relay
abandoned
sacrificed
lost
unknown
recoverable
recovered
nfc_readable
powered_download_available
external_power_needed
resurrection_attempted
resurrection_successful
resurrection_failed
black_box_recovered
retired
```

State changes must be recorded as mission events.

Track:

- timestamp;
- location estimate;
- agent ID;
- component ID where applicable;
- previous state;
- new state;
- reason;
- confidence;
- operator-visible message;
- whether recovery is recommended;
- whether a black-box snapshot is available.

---

## 9. Hardware degradation and fault injection

The demo must support intentional failure modelling.

Failure types:

```text
battery_capacity_loss
accelerated_battery_drain
motor_degradation
imu_drift
lidar_noise
camera_failure
thermal_sensor_noise
microphone_noise
radio_packet_loss
radio_total_loss
gps_denied
slam_drift
water_ingress
dust_occlusion
heat_damage
impact_damage
storage_corruption
ai_uncertainty
```

Failure severity:

```text
minor
moderate
severe
critical
complete
```

Failure mode:

```text
time_based
event_based
sector_based
random_seeded
operator_triggered
scripted_demo
```

Example failure profile:

```json
{
  "name": "Dust degraded LiDAR",
  "trigger": "enter_sector",
  "sector": "collapsed_corridor_2",
  "affected_component": "lidar",
  "severity": "moderate",
  "effect": {
    "noise_multiplier": 2.4,
    "map_confidence_drop": 0.35,
    "range_reduction": 0.5
  },
  "operator_message": "LiDAR return quality degraded due to dust or particulate interference."
}
```

The dashboard should explain the consequence of failures. Do not merely show red/green status.

---

## 10. Left-behind hardware and terrain placement

The platform must show where hardware is located or left within the terrain.

Hardware markers may include:

```text
active_drone
landed_relay_drone
dropped_relay_node
passive_audio_sensor
environmental_sensor
lost_drone
last_known_location
black_box_recovery_point
recovered_hardware
unsafe_unrecoverable_hardware
```

Each marker should have a detail card containing:

- asset name;
- asset type;
- mission role;
- current state;
- last known location;
- battery or power state;
- signal role;
- sensor payload;
- reason left in terrain;
- whether the asset is still useful;
- whether recovery is recommended;
- whether NFC/black-box readout is available.

---

## 11. NFC black-box and powered recovery model

Some drones or assets may include NFC or dynamic NFC capability.

Treat NFC as a **near-field recovery and service interface**, not as the main mission communications channel.

Supported concepts:

```text
nfc_identity_tag
nfc_black_box_log
last_state_snapshot
powered_download_state
external_power_recovery
service_tap
field_resurrection_attempt
post_failure_evidence_recovery
```

Use cases:

- A powered-down drone can expose a small identity and last-state record.
- A recovery technician or recovery robot can tap the asset to identify it.
- A limited black-box snapshot can be read after primary power failure.
- An external near-field power source or connector may wake a diagnostic/download state.
- The asset may attempt a limited resurrection, such as enabling a low-power beacon, not full flight.

Do not imply NFC can meaningfully recharge a drone for flight. Model meaningful recharge separately using docking, battery swap, wired connector, or dedicated wireless power hardware.

Example last-state snapshot:

```json
{
  "asset_id": "drone-c",
  "mission_id": "mission-demo-001",
  "last_state": "failed_primary_power",
  "last_known_sector": "void-space-3",
  "last_known_position": { "x": 18.2, "y": 7.4, "z": -2.1 },
  "battery_at_failure": 3,
  "failure_reason": "unexpected battery collapse after thermal payload surge",
  "black_box_available": true,
  "map_fragment_available": true,
  "priority_observation": "voice-like audio event detected 11 seconds before failure",
  "recovery_hint": "NFC readout available; external power required for full data download"
}
```

---

## 12. Mission consequence rules

The simulator should model decisions caused by mission conditions.

Examples:

```text
IF battery < return_threshold
AND map_priority is high
AND survivor_probability is low
THEN return_to_base.

IF battery < return_threshold
AND comms_chain is weak
AND relay_value is high
THEN land_and_become_relay.

IF survivor_probability > threshold
AND return_impossible
THEN continue_one_way_priority_streaming.

IF lidar_confidence drops
THEN slow_speed_and_request_second_pass.

IF comms_lost
THEN continue_local_mapping_for_configured_duration_then_return_to_last_relay.
```

AI-generated recommendations must be explainable and shown as recommendations, not automatic real-world commands.

---

## 13. Sensor and signal model

The platform should simulate or ingest diverse sensor and signal types.

Supported sensor categories:

```text
3d_mapping
lidar
visual_rgb
infrared
thermal
audio_voice
audio_ambient
ultraviolet
pressure
temperature
humidity
gas_co2
gas_general
wifi_scan
bluetooth_scan
em_signal
sonar
imu
battery
radio_quality
```

Each observation should include:

- source agent;
- source sensor;
- timestamp;
- location estimate;
- raw value or artifact reference;
- interpreted value where applicable;
- confidence;
- quality flags;
- mission relevance.

---

## 14. AI prompt orchestration

The app should generate structured prompts or command packages for AI platforms.

AI prompt outputs must be structured and reproducible.

Separate AI roles:

```text
mission_planner
sensor_analyst
map_analyst
audio_analyst
thermal_analyst
operator_assistant
report_writer
```

Example generated prompt package:

```json
{
  "mission_type": "collapsed_building_search",
  "priority": "life_safety",
  "agent_role": "thermal_audio_analyst",
  "inputs": [
    "thermal_frames",
    "audio_segments",
    "wifi_bluetooth_scan",
    "3d_void_map"
  ],
  "questions": [
    "Identify possible human presence.",
    "Rank detections by confidence.",
    "Highlight hazards blocking rescuer access.",
    "Suggest the next drone waypoint for human review."
  ],
  "output_schema": {
    "detections": [],
    "confidence": "0-1",
    "recommended_action": "string",
    "human_review_required": true
  }
}
```

Do not build unsafe autonomous command execution. AI recommendations should remain human-reviewed in the MVP.

---

## 15. Confidence model

Avoid presenting simulated outputs as certain.

Use confidence fields for:

- map coverage;
- route safety;
- signal chain reliability;
- thermal detections;
- audio detections;
- WiFi/Bluetooth detections;
- sensor health;
- AI recommendations;
- survivor probability;
- asset recovery feasibility.

Example:

```json
{
  "event_type": "detection",
  "detection_type": "voice_like_audio",
  "confidence": 0.58,
  "human_review_required": true,
  "operator_message": "Voice-like audio signature detected, but confidence is moderate due to fan noise and intermittent signal loss."
}
```

---

## 16. Dashboard requirements

The dashboard should include:

- mission overview;
- use-case theme;
- map/terrain preview;
- agent list;
- hardware inventory;
- hardware state panel;
- network/relay graph;
- sensor feed summary;
- detection panel;
- AI analyst panel;
- fault injection panel;
- timeline replay;
- after-action report export.

For the MVP, use sample data where live feeds are not available.

Do not overbuild real-time infrastructure before the static/demo experience is strong.

---

## 17. 3D mapping and visualisation guidance

For the MVP, a simplified 2D/2.5D/3D representation is acceptable.

Start simple:

- grid map;
- sector map;
- tunnel graph;
- building floorplan approximation;
- fake point-cloud preview;
- simple 3D scene with markers.

Potential future technologies:

- Three.js for custom browser 3D;
- CesiumJS for 3D geospatial/tiles;
- Potree-style point cloud viewing;
- 3D Tiles for streamable 3D datasets;
- MCAP/ROS bag replay for robotics logs.

Do not invent a complex 3D engine during the first iteration.

---

## 18. Security and safety boundaries

This project is a simulation and decision-support dashboard.

Do not generate code that:

- provides unsafe autonomous control of real drones;
- bypasses aviation rules;
- weaponises drones;
- enables covert surveillance;
- targets people without consent;
- hides logging or accountability;
- treats AI output as a final life-safety decision.

For real-world deployment, assume human operator review, aviation compliance, emergency service governance, privacy review, and safety testing are required.

---

## 19. Coding conventions

General:

- Use clear, readable code.
- Prefer small components and small functions.
- Use meaningful names.
- Avoid premature abstraction.
- Add comments where intent is not obvious.
- Use type hints in Python.
- Use TypeScript types/interfaces for frontend data structures.
- Keep secrets out of the repository.
- Use environment variables for configuration.
- Include sample `.env.example` files where helpful.
- Write tests for important domain logic.

Python/Django:

- Keep business rules in services or domain modules, not directly in views.
- Use serializers for API validation.
- Use model choices/enums for controlled state values.
- Add migrations when models change.
- Prefer explicit timestamps and UUIDs for mission data.

Astro/TypeScript:

- Keep page files clean.
- Extract repeated UI into components.
- Keep interactive islands focused.
- Avoid large global client state until needed.
- Use typed fixtures for demo data.

Styling:

- Use Tailwind utility classes.
- Extract repeated visual patterns into components.
- Avoid inline styles.
- Maintain accessible focus states.
- Support responsive layouts.

---

## 20. Documentation rules

Maintain project documentation as the implementation evolves.

Recommended docs:

```text
docs/
  architecture.md
  use-cases.md
  data-model.md
  failure-model.md
  ai-prompt-model.md
  nfc-recovery-model.md
  mission-simulation.md
  external-references.md
  decisions/
    ADR-0001-frontend-astro-tailwind.md
    ADR-0002-simulation-first.md
    ADR-0003-agent-based-model.md
```

Update docs when major decisions change.

Maintain a `CHANGELOG.md` or development journal if the repository uses one.

---

## 21. Recommended free/open-source resources and dependencies

Frontend:

- Astro
- Tailwind CSS
- TypeScript
- Vite
- Three.js, if custom 3D visualisation is needed
- CesiumJS, if geospatial/3D tiles are needed later

Backend:

- Python
- Django
- Django REST Framework
- Django Channels, later for WebSockets
- PostgreSQL
- PostGIS, later for spatial queries
- Redis, later for Channels/Celery
- Celery, later for background simulation tasks

Robotics/future integration:

- ROS 2
- Gazebo simulation
- PX4 or ArduPilot for open-source autopilot study
- Foxglove for robotics visualisation and log review
- MCAP for robotics/sensor logs

Data/visualisation:

- GeoJSON for simple geometry
- JSON fixtures for MVP scenarios
- LAS/LAZ/PLY/PCD/3D Tiles later for point clouds and 3D map artifacts

---

## 22. External references

Use official documentation when available.

Core references:

- GitHub Copilot custom instructions: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- VS Code custom instructions: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
- Astro documentation: https://docs.astro.build/
- Astro islands architecture: https://docs.astro.build/en/concepts/islands/
- Tailwind with Astro: https://tailwindcss.com/docs/installation/framework-guides/astro
- Astro Tailwind note: https://docs.astro.build/en/guides/integrations-guide/tailwind/
- Django: https://www.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django Channels: https://channels.readthedocs.io/
- PostgreSQL: https://www.postgresql.org/
- PostGIS: https://postgis.net/
- ROS 2 documentation: https://docs.ros.org/
- Gazebo: https://gazebosim.org/
- PX4: https://px4.io/
- ArduPilot: https://ardupilot.org/
- Foxglove docs: https://docs.foxglove.dev/
- MCAP: https://mcap.dev/
- Cesium 3D Tiles: https://cesium.com/why-cesium/3d-tiles/
- Three.js: https://threejs.org/
- NFC Forum: https://nfc-forum.org/
- ST dynamic NFC tags: https://www.st.com/en/nfc/st25-dynamic-nfc-tags.html
- NXP NTAG I2C Plus: https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf
- Wireless Power Consortium Qi: https://www.wirelesspowerconsortium.com/standards/qi-wireless-charging/

---

## 23. MVP target

Build the first demo around **Collapsed Building Search**.

MVP flow:

```text
1. User opens RescueMesh landing page.
2. User selects Collapsed Building Search.
3. App shows mission objective, suggested agents, sensors and performance expectations.
4. User starts a simulated mission.
5. Dashboard shows three drones and one relay node.
6. Map coverage expands over time.
7. Drone B develops intermittent communications.
8. Drone B lands and becomes a relay.
9. Drone C detects a thermal/audio anomaly.
10. Drone C suffers battery degradation and enters one-way priority streaming mode.
11. A failed asset remains in the terrain with NFC/black-box recovery available.
12. AI analyst panel ranks possible survivor location and asks for human review.
13. Timeline replay shows the mission story.
14. App exports or displays a mission report.
```

Prioritise a compelling, understandable demo over deep technical completeness.

---

## 24. Tone for generated code and project work

When assisting with this repository, GitHub Copilot should:

- preserve the simulation-first architecture;
- keep the frontend Astro/Tailwind-first unless instructed otherwise;
- avoid inline CSS;
- prefer free/open-source dependencies;
- ask only necessary clarifying questions;
- update documentation when adding important concepts;
- avoid over-engineering;
- make the demo visually clear and easy to explain;
- keep safety, explainability, and human review central.
