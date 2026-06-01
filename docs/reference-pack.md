# RescueMesh Technology Reference Pack

**Purpose:** Document the external concepts, standards, and technologies that inform RescueMesh design and architecture.

RescueMesh is a **simulation-first integration** of established ideas from robotics, rescue technology, sensor standards, geospatial/digital twin systems, underwater communication, low-light sensing, and mission-data interoperability.

This reference pack shows **where RescueMesh draws inspiration** and **what future integration paths exist**, while making clear what is implemented now versus what is modelled or planned.

---

## Status Definitions

Throughout this document, technologies are categorized as:

- **✅ Implemented:** Currently working in the RescueMesh codebase
- **🎭 Simulated:** Modelled in simulation but not connected to real hardware
- **🔮 Future Candidate:** Identified for potential future integration
- **📚 Background/Inspiration:** Informs design thinking but not directly integrated

---

## 1. Robotics and Future Hardware Integration

### ROS 2 (Robot Operating System 2)

**Status:** 🔮 Future Candidate

**What It Is:**
- Industry-standard middleware for robotics communication
- Topics (pub/sub), Services (request/response), Actions (long-running tasks with feedback)
- Message definitions with typed schemas
- Used by academic research, commercial robotics, autonomous systems

**How RescueMesh Uses It:**
- RescueMesh does **not** currently use ROS 2
- Mission event architecture is **inspired by** ROS 2 topics and action feedback patterns
- Future integration: RescueMesh could consume ROS 2 topics for real drone telemetry or publish simulated mission state as ROS 2 messages for robotics testing

**Reference:**
- Official documentation: https://docs.ros.org/en/humble/

---

### Gazebo Simulation

**Status:** 🔮 Future Candidate

**What It Is:**
- Open-source 3D robotics simulator
- Physics-based simulation (gravity, inertia, collision)
- Sensor simulation (LiDAR, cameras, IMU)
- Plugin-based extensibility

**How RescueMesh Uses It:**
- RescueMesh does **not** currently use Gazebo
- Current simulation is **lightweight mission-logic** in Django
- Future integration: Gazebo could provide realistic drone physics, sensor noise, SLAM mapping for a hybrid digital-twin/robotics simulator

**Reference:**
- Gazebo: https://gazebosim.org/

---

### PX4 and ArduPilot

**Status:** 📚 Background/Inspiration

**What They Are:**
- **PX4:** Open-source flight control software for drones and autonomous vehicles
- **ArduPilot:** Open-source autopilot firmware supporting multirotors, fixed-wing, rovers

**How RescueMesh Uses Them:**
- RescueMesh does **not** control real drones
- Battery models, flight-time estimation, and waypoint navigation are **inspired by** autopilot mission planning concepts
- Future integration: A real-world RescueMesh deployment could use PX4/ArduPilot drones with telemetry streamed into the mission platform

**Reference:**
- PX4: https://px4.io/
- ArduPilot: https://ardupilot.org/

---

### MCAP (Robotics Log Format)

**Status:** 🔮 Future Candidate

**What It Is:**
- Modern container format for robotics logs and sensor data
- Supports ROS 2, Protobuf, JSON schemas
- Developed by Foxglove for efficient time-series data storage and replay

**How RescueMesh Uses It:**
- RescueMesh does **not** currently export MCAP
- Mission events and agent telemetry are stored in Django models
- Future integration: Export mission runs as MCAP files for analysis in Foxglove Studio or robotics workflows

**Reference:**
- MCAP: https://mcap.dev/
- Foxglove: https://docs.foxglove.dev/

---

## 2. Sensor and Interoperability Standards

### OGC SensorThings API

**Status:** 📚 Background/Inspiration

**What It Is:**
- Open Geospatial Consortium (OGC) standard for IoT sensor data interoperability
- RESTful API with JSON responses
- Entities: Thing, Datastream, Observation, ObservedProperty, Sensor, Location

**How RescueMesh Uses It:**
- RescueMesh does **not** implement OGC SensorThings
- Mission API design is **inspired by** resource-oriented REST principles
- Future integration: Expose agent telemetry and sensor observations as SensorThings-compatible endpoints for interoperability with GIS platforms

**Reference:**
- OGC SensorThings: https://www.ogc.org/standards/sensorthings

---

### W3C SSN/SOSA (Semantic Sensor Network Ontology)

**Status:** 📚 Background/Inspiration

**What It Is:**
- W3C ontology for describing sensors, observations, samples, and actuators
- Provides semantic interoperability across sensor systems
- Used in research, smart cities, environmental monitoring

**How RescueMesh Uses It:**
- RescueMesh does **not** use SSN/SOSA ontologies
- Sensor confidence modeling, observation timestamps, and detection events are **conceptually aligned** with SOSA observation patterns
- Future integration: Mission data could be exported as RDF/JSON-LD with SSN/SOSA semantics for research datasets

**Reference:**
- W3C SSN/SOSA: https://www.w3.org/TR/vocab-ssn/

---

### Django Models and Django REST Framework

**Status:** ✅ Implemented

**What They Are:**
- **Django:** Python web framework with ORM, migrations, admin interface
- **Django REST Framework (DRF):** Toolkit for building RESTful APIs with serializers, viewsets, authentication

**How RescueMesh Uses Them:**
- Django powers the backend API and domain model
- DRF serializers expose mission state, agents, telemetry, events as JSON
- Mission state endpoint: `/api/v1/missions/{mission_pk}/state/`
- Structured, versioned API design inspired by REST best practices

**Reference:**
- Django: https://www.djangoproject.com/
- DRF: https://www.django-rest-framework.org/

---

## 3. Digital Twins and 3D Mapping

### Open Heritage 3D

**Status:** 📚 Background/Inspiration

**What It Is:**
- Initiative to create 3D digital twins of cultural heritage sites
- Uses photogrammetry, LiDAR, and 3D scanning
- Preserves historical sites digitally for research and accessibility

**How RescueMesh Uses It:**
- RescueMesh does **not** scan real heritage sites
- Digital twin concept: pre-built terrain sectors, waypoints, paths represent mission environment
- Future integration: Import real 3D scans of disaster sites, tunnels, or confined spaces for mission planning

**Reference:**
- CyArk / Open Heritage: https://www.cyark.org/

---

### Cesium 3D Tiles

**Status:** 🔮 Future Candidate

**What It Is:**
- Open standard for streaming massive 3D geospatial datasets
- Optimized for visualization of point clouds, meshes, buildings
- Used by Cesium for geospatial rendering in web browsers

**How RescueMesh Uses It:**
- Current tactical maps use **lightweight SVG** with sectors and waypoints
- Future integration: Replace SVG maps with Cesium 3D Tiles for realistic point-cloud visualization of scanned environments
- Use case: Visualize LiDAR-scanned collapsed building interior in mission dashboard

**Reference:**
- 3D Tiles: https://cesium.com/why-cesium/3d-tiles/
- CesiumJS: https://cesium.com/platform/cesiumjs/

---

### GeoJSON and 3D Coordinate Compatibility

**Status:** ✅ Implemented (Conceptually)

**What It Is:**
- **GeoJSON:** Standard format for geographic features (points, lines, polygons)
- Supports `[longitude, latitude, elevation]` coordinates

**How RescueMesh Uses It:**
- Django digital twins store sectors with `x, y, width, height`
- Mission coordinate model uses local mission coordinates, not global GPS
- Future integration: Export mission geometry as GeoJSON for interoperability with mapping tools

**Reference:**
- GeoJSON Spec: https://geojson.org/

---

### Local Mission Coordinate Model

**Status:** ✅ Implemented

**What It Is:**
- RescueMesh uses a **local coordinate system** for each mission
- Origin (0, 0) represents mission entry or reference point
- Coordinates in meters or mission-defined units
- Suitable for GPS-denied or confined-space missions

**How It Works:**
- Sectors defined as `(x, y, width, height)` rectangles
- Waypoints defined as `(x, y, time, sectorId, label)`
- Depth/elevation labels like `"-3.5m"` or `"+8.0m"` attached to sectors
- No global GPS required

**Why:**
- Collapsed buildings, caves, tunnels, underwater structures lack reliable GPS
- Local coordinates enable SLAM-like mapping simulation

---

## 4. Mesh, Relay and Communications

### MeshStatic vs MeshCore

**Status:** ✅ MeshStatic Implemented, 🔮 MeshCore Future Candidate

**MeshStatic (Current Implementation):**
- **What:** Static relay placement with known agent paths
- **How:** Django defines relay positions and communication chains
- **Rendering:** SVG network connections show active relay chains
- **Signal strength:** Color-coded lines (green/yellow/red)
- **Topology:** Routes around sacrificed/failed relay nodes

**MeshCore (Future Dynamic Networking):**
- **What:** Real-time ad-hoc mesh networking
- **How:** Agents dynamically form and re-form network topology based on signal strength and node availability
- **Protocols:** Inspired by MANETs (Mobile Ad-Hoc Networks), ZigBee mesh, LoRa mesh
- **Use case:** Autonomous relay placement, self-healing networks

**Why Separate:**
- MeshStatic is sufficient for simulation-first demos with known terrain
- MeshCore requires real-time routing algorithms and hardware integration

---

### WebRTC (Web Real-Time Communication)

**Status:** 🔮 Future Candidate

**What It Is:**
- Browser-based protocol for peer-to-peer audio, video, and data streaming
- Low-latency, encrypted, NAT-traversal support
- Used for video calls, live streaming, collaborative tools

**How RescueMesh Could Use It:**
- **Not currently implemented**
- Future integration: Stream live video from simulated or real cameras to mission dashboard
- Voice/data channels for operator-to-agent communication
- Real-time sensor data streaming (alternative to HTTP polling)

**Reference:**
- WebRTC: https://webrtc.org/

---

### NFC (Near Field Communication)

**Status:** 🎭 Simulated

**What It Is:**
- Very short-range wireless communication (typically < 10 cm)
- Used for contactless payments, tap-to-pair devices, access badges
- **Dynamic NFC tags** can be powered by reader field and respond with data or accept limited power transfer

**How RescueMesh Uses It:**
- Simulated as **black-box recovery** and **service tap** mechanism
- Scenario: Failed drone lands in terrain, operator or recovery robot taps with NFC to read:
  - Last known position
  - Mission state snapshot
  - Battery failure reason
  - Map fragment
  - Priority observations
- **Not for long-range tracking** — NFC is touch-range only
- **Not for meaningful recharge** — insufficient power for drone flight, but may enable diagnostic mode

**Reference:**
- NFC Forum: https://nfc-forum.org/
- ST Dynamic NFC Tags: https://www.st.com/en/nfc/st25-dynamic-nfc-tags.html
- NXP NTAG I2C Plus: https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf

---

### UHF RFID / EPC Gen2

**Status:** 📚 Background/Inspiration

**What It Is:**
- Long-range radio frequency identification (up to 10+ meters)
- Used for supply chain tracking, toll collection, asset management
- Tags are typically passive (powered by reader signal)

**How RescueMesh Could Use It:**
- **Not currently implemented**
- Future use case: Tag equipment, relay nodes, or supply caches with RFID
- Recovery robot or operator scans area to locate tagged assets
- Closer to **toll-tag-style detection** than precise positioning

**Why Not NFC:**
- NFC requires very close proximity (cm)
- RFID can detect tags at distance (meters)

**Reference:**
- EPC Gen2 RFID: https://www.gs1.org/standards/epc-rfid

---

## 5. Underwater / Submersible Communications

### Underwater Acoustic Modems

**Status:** 🎭 Simulated (Conceptually)

**What They Are:**
- Underwater communication using sound waves
- Longer range (hundreds of meters to kilometers)
- Lower bandwidth (typically kbps)
- Subject to multipath, noise, Doppler effects

**How RescueMesh Models Them:**
- Flooded structure scenario includes amphibious agents
- Communication challenges simulated through signal strength degradation
- Future integration: Model acoustic-specific propagation, latency, packet loss

**Trade-offs:**
- ✅ Long range
- ❌ Low bandwidth
- ❌ High latency
- ❌ Susceptible to ambient noise (ship engines, waves)

**Reference:**
- Underwater acoustic communication research (IEEE, academic papers)

---

### Underwater Optical Communications

**Status:** 🔮 Future Candidate

**What They Are:**
- High-bandwidth underwater communication using light (laser or LED)
- Very short range (meters to tens of meters)
- Requires line-of-sight
- High data rates (Mbps to Gbps)

**How RescueMesh Could Model Them:**
- **Not currently implemented**
- Future use case: Amphibious robots use optical bursts for high-speed map fragment transfer or video streaming
- Only works in clear water with line-of-sight

**Trade-offs:**
- ✅ High bandwidth
- ✅ Low latency
- ❌ Very short range
- ❌ Requires clear water and alignment

**Reference:**
- Research on underwater optical wireless communication (UOWC)

---

### Hybrid Acoustic/Optical Concepts

**Status:** 📚 Background/Inspiration

**What It Is:**
- Conceptual approach: Use acoustic for long-range coordination and discovery, optical for high-bandwidth data bursts when agents are close

**How RescueMesh Could Model It:**
- **Not currently implemented**
- Future scenario: Amphibious agents use acoustic to locate each other, switch to optical when within range for map synchronization

**Use Case:**
- Acoustic: "I'm in sector D, battery 60%, found hotspot"
- Optical (when close): Transfer 10 MB of sonar scan data in seconds

---

## 6. Rescue Sensing and Low-Light Operations

### Thermal Search-and-Rescue Imaging

**Status:** 🎭 Simulated

**What It Is:**
- Infrared cameras detect heat signatures from humans, animals, fires
- Used by firefighters, search-and-rescue teams, law enforcement
- Effective in darkness, smoke, obscured environments

**How RescueMesh Uses It:**
- **Capability pack:** Agents can carry thermal sensors
- Simulated detection events: `"Thermal anomaly detected, confidence 0.68"`
- Dashboard shows thermal detection overlays

**Reference:**
- FLIR thermal cameras: https://www.flir.com/

---

### Night Vision / Image Intensification

**Status:** 🎭 Simulated

**What It Is:**
- Amplifies available light (moonlight, starlight, infrared)
- Different technology from thermal imaging
- Used for low-light navigation and observation

**How RescueMesh Uses It:**
- **Capability pack:** Separate from thermal
- Enables mission operation in complete darkness
- Modelled as sensor availability, not actual image processing

**Difference from Thermal:**
- Night vision: amplifies light, sees reflected photons
- Thermal: detects heat radiation, works in total darkness without light

**Reference:**
- Night vision technology overview (military/civilian use)

---

### Seismic/Acoustic Life Detectors

**Status:** 🎭 Simulated

**What They Are:**
- Sensors that detect vibrations, breathing sounds, heartbeats, movement
- Used in earthquake rescue, collapsed building search
- Can detect trapped persons under rubble

**How RescueMesh Uses Them:**
- **Capability pack:** Agents can carry seismic/acoustic sensors
- Simulated detection: `"Voice-like audio detected, confidence 0.58"`
- Mission priority: If acoustic signature detected, drone may sacrifice itself to stream priority data

**Reference:**
- DHS SAVER Program: https://www.dhs.gov/science-and-technology/saver (search and rescue technology)

---

### Hydrophones

**Status:** 🎭 Simulated

**What They Are:**
- Underwater microphones for detecting sound in water
- Used for marine biology, submarine detection, underwater communication

**How RescueMesh Uses Them:**
- **Capability pack:** Flooded structure scenario includes hydrophone sensors
- Detects underwater acoustic signals, structural sounds, water flow

**Reference:**
- Ocean Instruments hydrophones: https://www.oceaninstruments.com/

---

## 7. Safety and Ethical Boundaries

RescueMesh is a **simulation and decision-support platform**, not a real-time autonomous control system.

### Core Principles:

1. **Simulation-First**
   - Does not require real hardware to demonstrate concepts
   - Reproducible scenarios with seeded data
   - Safe for experimentation and training

2. **Non-Weaponised**
   - Never generate code for weapon control
   - Never enable covert surveillance without consent
   - Never target people maliciously

3. **Not Real-Time Drone Control**
   - Does not provide unsafe autonomous control
   - AI recommendations require human review
   - No direct flight command execution in demo

4. **No Unauthorised Device Control**
   - Does not hijack drones or sensors
   - Integration assumes authorised, governed deployment
   - Respects aviation law and emergency service protocols

5. **Talkback Is Simulated or Authorised Only**
   - Simulated survivor communication is demo-only
   - Real-world talkback would require proper rescue communication equipment and legal authority

6. **Real-World Deployment Requires Governance**
   - Aviation compliance
   - Emergency service approval
   - Privacy review
   - Safety testing
   - Operator training
   - Legal and ethical oversight

### Why These Boundaries Matter:

- RescueMesh demonstrates **what could be done** with proper governance
- It does **not** claim to be a ready-to-fly system
- Any transition from demo to real-world use must include:
  - Legal review
  - Safety certification
  - Privacy assessment
  - Operational protocols
  - Emergency stop mechanisms
  - Human oversight requirements

**Real-world rescue missions involve life-or-death decisions. This platform is for planning, training, and research — not autonomous life-safety operations without human oversight.**

---

## 8. How to Use This Reference Pack

### When Adding a New Feature:

1. **Identify the Reference Category**
   - Which section does this feature relate to?
   - Robotics? Sensors? Communications? Digital Twins?

2. **Declare Implementation Status**
   - ✅ Implemented
   - 🎭 Simulated
   - 🔮 Future Candidate
   - 📚 Background/Inspiration

3. **Link to Official Documentation**
   - Prefer standards bodies (OGC, W3C, ISO)
   - Prefer official project documentation (ROS 2, PX4)
   - Use reputable technical sources

4. **Explain What RescueMesh Does vs What It Could Do**
   - Be honest about what's real vs simulated
   - Avoid claiming features not yet implemented
   - Show the path from demo to real integration

### When Updating This Document:

- **Keep it current** — update status as features move from planned → simulated → implemented
- **Add new references** — as new standards or technologies emerge
- **Remove obsolete references** — if a standard is deprecated or superseded
- **Balance depth and readability** — this is a reference pack, not a textbook

### When Reviewing Pull Requests:

- **Check status claims** — don't merge code that claims integration without proof
- **Verify references** — ensure external links are valid and accurate
- **Require documentation updates** — if PR adds a feature, update this document

### When Explaining RescueMesh to Others:

- **Start with "simulation-first"**
- **Explain what's real, what's modelled, what's planned**
- **Use this reference pack to show thought went into design**
- **Emphasize safety boundaries**

---

## Conclusion

RescueMesh is a **lightweight, simulation-first demonstrator** informed by real-world robotics, sensor standards, geospatial systems, and rescue technologies.

This reference pack exists to:

- **Show our influences** — we're not reinventing the wheel
- **Plan for the future** — integration paths are documented
- **Maintain honesty** — clear about what's real vs simulated
- **Enable learning** — useful for contributors and evaluators

By documenting these references, we make RescueMesh easier to understand, extend, and integrate with real systems when appropriate governance and safety measures are in place.

**RescueMesh demonstrates concepts. Real missions save lives. The gap between them requires care, testing, and responsibility.**
