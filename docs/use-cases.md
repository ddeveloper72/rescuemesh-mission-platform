# RescueMesh Use Cases

## Overview

Each use case defines a complete mission scenario with consistent documentation structure covering objectives, terrain, agents, sensors, communications, navigation, media, failures, escalation, outputs, and AI behavior.

**Last updated:** May 30, 2026

---

## 1. Collapsed Building Search

**Priority:** Life Safety

### Mission Objective

Rapidly map unstable voids and detect signs of human presence in partially collapsed structures where traditional search methods are too dangerous or time-consuming.

Primary goals:
- Identify survivors or signs of human presence
- Map accessible voids and passages
- Assess structural hazards
- Establish relay communications network

### Terrain Characteristics

- Collapsed building with unstable voids and confined spaces
- Multiple floors, stairwells, and basement areas
- GPS denied or unreliable inside structure
- Radio attenuation through concrete and steel reinforcement
- Dark environment with dust obscuration
- Unstable structure with sharp debris
- Risk of secondary collapse

### Recommended Agents

**Scout Drone A (Survey/Mapper):**
- LiDAR for 3D mapping
- Low-light RGB camera
- Thermal camera
- IMU for position estimation
- High endurance battery

**Scout Drone B (Detection/Relay):**
- Microphone array for audio detection
- CO₂ sensor
- WiFi/Bluetooth scanner
- Relay capability
- Moderate battery with relay fallback mode

**Deep Penetration Drone C:**
- Compact design for narrow passages
- Thermal camera
- Audio sensor
- NFC black-box module for recovery
- Priority one-way streaming capability

**Static Relay Node (optional):**
- High-power radio
- Mesh networking
- Extended battery or wired power

### Sensor / Technology Packs

**Mapping Sensors:**
- LiDAR (3D terrain reconstruction)
- IMU (position estimation in GPS-denied)
- Low-light camera (visual documentation)

**Detection Sensors:**
- Thermal camera (human heat signatures)
- Microphone array (tapping, voice, knocking sounds)
- CO₂ sensor (respiration indicators)
- WiFi/Bluetooth scanner (mobile device detection)

**Health Monitoring:**
- Battery level
- Signal strength
- Component temperature
- Dust occlusion indicators

### Communications Model

**Primary:** Mesh relay networking through multi-hop agent chain

**Strategy:**
- Scout Drone A maintains line-of-sight to base or relay
- Scout Drone B extends range and provides redundancy
- Deep Penetration Drone C operates at network edge
- Tactical relay decisions when battery or signal degrade
- Agents land and become static relays when needed

**Challenges:**
- Steel reinforcement causes signal attenuation
- Concrete walls block direct radio paths
- Multi-hop latency increases with depth
- Packet loss possible at network edges

### Navigation Intelligence

**Coordinate System:** Local mission 3D grid with entry point as origin

**Compass Reliability:** Acceptable to Degraded (65-84% confidence)
- Metal reinforcement causes moderate magnetic interference
- Confidence decreases with depth and proximity to steel beams

**Key Measurements:**
- Distance from origin (2D and 3D)
- Bearing from origin (compass heading)
- Elevation relative to entry (+3m above, -4m below)
- Depth below entry point for basement voids
- Route distance through mapped passages

**Vertical Profile:**
- Upper floors: +2m to +8m above entry
- Ground floor: 0m to +2m
- Basement voids: -2m to -6m below entry

### Media Returns

**Generated/Captured Media:**
- Low-light imagery of voids and passages
- Thermal camera frames with hotspot highlighting
- Audio recordings of tapping, knocking, voice-like sounds
- Spectrograms of audio events for pattern analysis
- Last-good-frame with signal degradation effects

**Media Quality Challenges:**
- Dust occlusion degrades camera and LiDAR
- Low light requires enhanced imaging
- Audio contaminated by fan noise and echoes

### Failure Risks

**Sensor Degradation:**
- Dust occlusion → LiDAR/camera quality loss
- Impact damage → Sensor misalignment
- Thermal sensor noise from component heat

**Power Management:**
- Battery drain accelerated by hovering and obstacle avoidance
- Aggressive power consumption in cold environments
- Insufficient battery for return journey

**Communications:**
- Radio packet loss → Intermittent communications
- Total signal loss in deep basement voids
- Relay chain break if intermediate agent fails

**Tactical Decisions:**
- Agent lands as relay when battery < threshold
- One-way priority streaming when return impossible
- Sacrifice decisions for critical detections

### Escalation Triggers

**Elevated Escalation:**
- Battery levels below 40% across multiple agents
- Network mesh health drops below 60%
- Medium-confidence detection requires investigation

**Critical Escalation:**
- Multiple agent failures
- High-confidence survivor detection (thermal + audio + CO₂)
- Network at risk of complete failure
- Structural collapse warning

**Actions on Escalation:**
- Deploy relay reinforcement
- Recall agents from non-critical sectors
- Increase human operator review frequency
- Prepare recovery team for entry

### Expected Outputs

**Mapping Products:**
- 3D void map with point cloud data
- Accessible vs. blocked sector classification
- Structural hazard markers
- Recommended access routes for rescuers

**Detection Products:**
- Thermal anomaly locations with confidence scores
- Audio event timeline (tapping, voice-like, knocking)
- WiFi/Bluetooth device signals with locations
- CO₂ concentration map

**Operational Products:**
- Relay topology map showing mesh network
- Agent status and battery projections
- Failed/left-behind asset recovery map
- Mission timeline and event log

**AI Analysis:**
- Ranked detection list for human review
- Survivor probability by location
- Recommended next waypoints
- Hazard warnings for human entry

### AI Analyst Behaviour

**Analysis Tasks:**
- Fuse thermal, audio, CO₂, and WiFi/Bluetooth data
- Rank detections by confidence and urgency
- Identify patterns suggesting human presence
- Highlight hazards blocking rescuer access

**Output Requirements:**
- Confidence scores for all detections (0.0-1.0)
- Human review required flag for critical findings
- Explainable recommendations with supporting evidence
- Alternate hypotheses for ambiguous signals

**Constraints:**
- Do not make definitive "survivor confirmed" claims
- Present findings as "possible human presence" with confidence
- Recommend human expert review for all medium+ confidence detections
- Warn when data quality is degraded (dust, signal loss)


---

## 2. Cave Rescue

**Priority:** Mapping and Path Discovery

### Mission Objective

Map unknown cave systems to locate lost or injured persons and identify safe access routes for rescue teams.

Primary goals:
- Create 3D tunnel map for navigation
- Locate persons requiring assistance
- Identify safe routes and hazards
- Establish relay communications through rock

### Terrain Characteristics

- Natural or abandoned mine tunnels
- GPS completely denied
- Radio attenuation through solid rock
- Narrow passages and vertical drops (squeezes, chimneys)
- Water hazards (underground streams, pools)
- Complete darkness
- High humidity
- Temperature variations
- Cave formations (stalactites, stalagmites)

### Recommended Agents

**Survey Drone A (Primary Mapper):**
- LiDAR for tunnel mapping
- IMU for dead reckoning
- Low-light camera
- Temperature and humidity sensors
- Extended battery

**Ground Crawler (Rough Terrain):**
- Designed for uneven rocky surfaces
- Thermal camera
- Audio sensors
- All-terrain mobility

**Static Relay Nodes (Multiple):**
- High-power radio for rock penetration
- Mesh networking
- Long-life battery
- Waterproof casing

**Detection Drone B (Audio/Thermal):**
- Microphone array
- Thermal camera
- Compact design for narrow passages

### Sensor / Technology Packs

**Mapping Sensors:**
- LiDAR (tunnel geometry)
- IMU (dead reckoning navigation)
- Low-light camera
- Distance measurement

**Environmental Sensors:**
- Temperature
- Humidity
- O₂ level
- CO₂ level
- Atmospheric pressure

**Detection Sensors:**
- Thermal camera (human heat signatures)
- Microphone array (calls for help)
- Gas sensors (safety assessment)

### Communications Model

**Primary:** Static relay chain through cave system

**Strategy:**
- Deploy static relay nodes at key junctions
- Relay spacing based on rock composition and thickness
- Multi-hop mesh through relay chain
- Store-and-forward capability (future)
- High-power transmission to penetrate rock

**Challenges:**
- Rock composition affects radio propagation
- Deep caves require many relay hops
- Water in passages increases attenuation
- Vertical drops create line-of-sight challenges

### Navigation Intelligence

**Coordinate System:** Local mission 3D grid with cave entrance as origin

**Compass Reliability:** Degraded to Unreliable (45-65% confidence)
- Rock composition and mineral deposits cause magnetic interference
- Iron ore and metal-rich rock severely degrade compass
- Confidence decreases rapidly with depth

**Key Measurements:**
- Distance from entrance (actual tunnel path)
- Bearing from entrance (when compass reliable)
- Depth below entrance (vertical descent)
- Tunnel slope and incline
- Distance to nearest relay node

**Vertical Profile:**
- Entry chamber: 0m reference
- Descending passages: -5m, -15m, -28m depths
- Deep chambers: -40m+ below entrance

### Media Returns

**Generated/Captured Media:**
- Low-light tunnel imagery
- Thermal camera frames in chambers
- Audio recordings of ambient cave sounds
- Tunnel geometry visualization
- Path profile diagrams

**Media Quality Challenges:**
- Complete darkness requires illumination or low-light sensors
- High humidity causes condensation on lenses
- Narrow passages limit camera field of view

### Failure Risks

**Navigation Challenges:**
- GPS completely denied
- Compass unreliable due to rock interference
- Dead reckoning drift over long distances
- Narrow squeeze passages may block larger agents

**Communications:**
- Radio total loss in deep sections without relays
- Rock thickness exceeds signal penetration
- Relay node failure breaks communication chain

**Environmental:**
- Water damage to electronics
- High humidity sensor degradation
- Battery performance affected by temperature

**Operational:**
- Agent stranded in tight passage
- Insufficient battery for return journey
- Loss of orientation without IMU

### Escalation Triggers

**Elevated Escalation:**
- Relay chain weakening
- Agent approaching narrow passage with low confidence
- Environmental sensor warnings (low O₂, high CO₂)

**Critical Escalation:**
- Communication chain broken
- Agent stranded beyond safe return distance
- High-confidence human detection (thermal + audio)
- Environmental hazard detected (gas, flooding)

**Actions on Escalation:**
- Deploy additional relay nodes
- Recall agents from speculative exploration
- Human review of all navigation decisions
- Prepare rescue team for physical entry

### Expected Outputs

**Mapping Products:**
- 3D tunnel map with passage geometry
- Vertical profile showing descent
- Junction map with branch options
- Squeeze and restriction markers
- Water hazard locations

**Safety Products:**
- Safe route recommendations
- Hazard warnings (vertical drops, water, unstable rock)
- Relay node placement map
- O₂ and CO₂ readings by location

**Detection Products:**
- Thermal anomaly locations
- Audio event timeline
- Human presence probability map

**Operational Products:**
- Relay chain topology
- Agent battery projections
- Return path distance estimates
- Recovery plan for stranded agents

### AI Analyst Behaviour

**Analysis Tasks:**
- Analyze tunnel geometry for safe human passage
- Identify passages likely vs. unlikely to contain persons
- Recommend relay deployment locations
- Assess environmental safety (O₂, CO₂, temperature)

**Output Requirements:**
- Confidence scores for route safety
- Clear warnings for hazards (drops, squeezes, water)
- Recommended search priorities
- Environmental safety assessment

**Constraints:**
- Conservative recommendations for human entry
- Flag passages requiring specialized caving equipment
- Warn when agent data quality is degraded
- Recommend additional sensing for ambiguous areas

---

## 3. Flooded Structure

**Priority:** Amphibious Inspection and Obstruction Mapping

### Mission Objective

Inspect partially flooded buildings or underground structures to map obstructions, assess water depth, and identify safe/unsafe zones.

Primary goals:
- Map water depth and submerged obstacles
- Identify accessible dry sections
- Locate stranded assets or equipment
- Assess structural integrity underwater

### Terrain Characteristics

- Partially submerged building or tunnel system
- Standing or slowly flowing water
- Submerged debris and obstructions
- Visibility degradation underwater
- Corrosion risk to electronics
- Buoyancy control challenges
- Possible contamination (sewage, chemicals)

### Recommended Agents

**Amphibious Drone A (Primary Scout):**
- Surface and underwater capability
- Pressure sensor for depth
- Sonar for underwater mapping
- Waterproof camera
- Buoyancy control system

**Surface Relay Drone:**
- Remains at water surface
- High-power radio for surface-to-underwater relay
- GPS (if above ground with satellite visibility)
- Extended battery

**Ground Robot (Dry Sections):**
- Operates in accessible dry areas
- LiDAR mapping
- Thermal camera
- Relay capability

### Sensor / Technology Packs

**Underwater Sensors:**
- Pressure sensor (depth measurement)
- Sonar (obstacle detection, mapping)
- Water quality sensors (pH, temperature, conductivity)
- Waterproof camera with lighting

**Surface/Dry Sensors:**
- LiDAR (above-water mapping)
- GPS (outdoor sections)
- Thermal camera
- Standard RGB camera

**Environmental Monitoring:**
- Water temperature
- Contamination indicators
- Structural integrity sensors

### Communications Model

**Primary:** Hybrid mesh with surface relay and underwater acoustic

**Strategy:**
- Surface relay drone maintains base station contact
- Underwater agents communicate via acoustic or surface breaks
- Amphibious drones surface periodically for data burst
- Ground robots provide relay in accessible dry sections

**Challenges:**
- Water severely attenuates radio signals
- Acoustic underwater communication is low bandwidth
- Submerged metal and concrete block signals
- Contaminated water increases attenuation

### Navigation Intelligence

**Coordinate System:** Local mission 3D grid with entry point as origin

**Compass Reliability:** Good to Acceptable (75-90% confidence above water, degraded underwater)
- Compass reliable on surface and dry sections
- Underwater compass affected by building metal and water currents
- GPS available outdoors (if not blocked by structure)

**Key Measurements:**
- Distance from entry (surface travel + underwater)
- Water depth below surface (positive depth value)
- Elevation above/below entry point
- Submerged obstacle proximity

**Vertical Profile:**
- Above water: +2m to +5m (upper floors, elevated platforms)
- Water surface: 0m reference
- Shallow submersion: -1m to -3m depth
- Deep submersion: -3m to -10m+ depth

### Media Returns

**Generated/Captured Media:**
- Murky underwater imagery
- Sonar mapping visualizations
- Surface-level photography
- Water depth contour maps
- Last-good-frame before submersion

**Media Quality Challenges:**
- Very low visibility underwater
- Particulate matter obscures cameras
- Lighting required for underwater photography
- Sonar provides geometric data but not visual detail

### Failure Risks

**Water-Related Failures:**
- Water ingress → Electronics failure
- Corrosion → Component degradation
- Buoyancy control loss → Sinking or uncontrolled floating
- Current drift → Loss of position

**Communications:**
- Radio failure underwater
- Acoustic communication limited range and bandwidth
- Surface relay drone must remain operational

**Operational:**
- Battery drain from buoyancy control
- Low visibility navigation challenges
- Agent stranded underwater beyond safe return

### Escalation Triggers

**Elevated Escalation:**
- Water ingress warning on any agent
- Buoyancy control degradation
- Surface relay signal weakening

**Critical Escalation:**
- Agent completely submerged without surfacing capability
- Contamination detected (chemical, sewage)
- Structural collapse underwater
- Multiple agent failures

**Actions on Escalation:**
- Recall underwater agents to surface
- Deploy backup surface relay
- Prepare recovery team with diving equipment
- Assess contamination risk for human entry

### Expected Outputs

**Mapping Products:**
- Water depth contour map
- Submerged obstruction map
- Accessible vs. flooded zone classification
- 3D structure map (above and below water)

**Safety Products:**
- Safe passage routes (avoiding deep water)
- Structural integrity assessment
- Contamination warnings
- Current flow indicators

**Asset Products:**
- Recoverable asset locations (equipment, valuables)
- Stranded asset recovery plan
- Underwater vs. accessible asset classification

**Operational Products:**
- Relay topology map
- Agent battery and buoyancy status
- Water level change monitoring
- Mission timeline

### AI Analyst Behaviour

**Analysis Tasks:**
- Identify safe vs. hazardous zones for human entry
- Recommend dry access routes
- Assess water quality and contamination risk
- Prioritize asset recovery by accessibility

**Output Requirements:**
- Water depth confidence scoring
- Obstruction detection with confidence
- Contamination risk assessment
- Recommended diving vs. ground access paths

**Constraints:**
- Conservative water safety recommendations
- Flag contamination risk prominently
- Warn when underwater visibility degraded
- Recommend specialized diving equipment when needed


---

## 4. Industrial Confined Space Inspection

**Priority:** Hazardous Material Assessment and Structural Inspection

### Mission Objective

Inspect industrial facilities with hazardous materials, confined spaces, or extreme conditions without exposing human personnel to risks.

Primary goals:
- Assess atmosphere safety (toxic gases, O₂ levels)
- Map confined space geometry
- Identify structural damage or corrosion
- Detect radiation or chemical hazards

### Terrain Characteristics

- Confined spaces with limited access points
- Potentially toxic or explosive atmosphere
- Heat or radiation hazards
- Complex pipe gallery geometry
- Electromagnetic interference from heavy machinery
- Elevated platforms and basement areas
- Sharp edges and protrusions
- Poor lighting

### Recommended Agents

**Micro Inspection Drone A:**
- Compact design for tight spaces
- Gas sensors (CO, CO₂, H₂S, CH₄, O₂)
- Thermal camera
- High-intensity lighting
- Chemical-resistant materials

**Radiation Scout Drone (if applicable):**
- Radiation detector
- Dosimeter
- Shielded electronics
- Remote operation capability

**Ground Robot (Elevated Platforms):**
- Stair/ladder climbing capability
- LiDAR mapping
- Gas sensors
- Relay capability

**Static Relay Node:**
- High-power radio (to penetrate metal)
- Extended battery
- Heat-resistant casing

### Sensor / Technology Packs

**Safety Sensors:**
- Gas sensors: CO, CO₂, H₂S, CH₄, O₂, VOCs
- Radiation detector (Geiger counter, dosimeter)
- Temperature sensors (extreme heat warning)
- Pressure sensors

**Inspection Sensors:**
- Thermal camera (heat anomalies, hot pipes)
- RGB camera with high-intensity lighting
- Corrosion detection imaging
- Structural integrity sensors

**Navigation:**
- LiDAR (confined space mapping)
- IMU (orientation in complex geometry)
- Obstacle avoidance sensors

### Communications Model

**Primary:** Mesh relay with electromagnetic interference mitigation

**Strategy:**
- Static relay nodes placed outside confined spaces
- Agents operate at network edge with burst communication
- Store mission data locally with periodic upload
- High-power transmission to penetrate metal structures

**Challenges:**
- Heavy machinery causes electromagnetic interference
- Metal pipes and tanks block radio signals
- Complex geometry creates multi-path reflections
- High-temperature areas may require relay positioning outside hot zones

### Navigation Intelligence

**Coordinate System:** Local mission 3D grid with facility entry as origin

**Compass Reliability:** Degraded to Unreliable (40-60% confidence)
- Electromagnetic interference from machinery
- Metal pipe galleries cause severe magnetic distortion
- Electrical systems create variable interference

**Key Measurements:**
- Distance from entry (route through facility)
- Bearing from entry (when compass usable)
- Elevation (basement, ground floor, elevated platform)
- Clearance to overhead pipes and obstacles

**Vertical Profile:**
- Elevated platforms: +4m to +12m above ground
- Ground floor: 0m to +2m reference
- Basements and tunnels: -2m to -8m below ground

### Media Returns

**Generated/Captured Media:**
- Industrial facility imagery (pipes, valves, gauges)
- Thermal hotspot maps
- Corrosion damage photographs
- Gas sensor heatmaps
- Radiation level contour maps

**Media Quality Challenges:**
- Poor lighting requires onboard illumination
- Heat shimmer affects thermal imaging
- Dust and particulates obscure cameras
- Reflective metal surfaces create imaging challenges

### Failure Risks

**Environmental Hazards:**
- Toxic atmosphere → Sensor contamination or failure
- Heat damage → Electronics failure or battery degradation
- Radiation → Electronics upset or permanent damage
- Corrosive chemicals → Material degradation

**Electromagnetic Interference:**
- EM interference → Communications loss
- High-power machinery → Control system interference
- Variable interference → Intermittent failures

**Operational:**
- Disorientation in complex pipe galleries
- Battery drain in extreme temperatures
- Agent stuck in tight passage

### Escalation Triggers

**Elevated Escalation:**
- Gas concentration approaching hazardous levels
- Elevated radiation detected
- Multiple agents experiencing interference
- Heat levels approaching safe operating limits

**Critical Escalation:**
- Explosive gas mixture detected (LEL warnings)
- Radiation exceeds safe dose rate
- Structural collapse risk identified
- Agent failure in hazardous zone

**Actions on Escalation:**
- Immediate recall of agents from hazard zone
- Alert facility safety team
- Recommend evacuation if explosive risk
- Prepare specialized recovery procedures

### Expected Outputs

**Safety Products:**
- Gas concentration map by zone
- Radiation level contour map
- Temperature hazard map
- Safe entry route recommendations

**Structural Products:**
- Facility geometry map
- Corrosion and damage locations
- Structural integrity assessment
- Equipment condition report

**Operational Products:**
- PPE recommendations for human entry
- Required safety equipment list
- Hazard priority rankings
- Agent operational limits by zone

**Regulatory Products:**
- Atmospheric monitoring data
- Radiation survey results
- Confined space entry documentation
- Hazard assessment report

### AI Analyst Behaviour

**Analysis Tasks:**
- Identify immediate safety hazards (explosive gas, high radiation)
- Assess structural integrity and corrosion severity
- Recommend appropriate PPE for human entry
- Prioritize repair and inspection areas

**Output Requirements:**
- Clear hazard severity classifications (safe, caution, danger, prohibited)
- Gas concentration confidence scores
- Radiation dose rate measurements with uncertainty
- Conservative recommendations for human entry

**Constraints:**
- Prioritize safety over mission completion
- Flag any atmosphere approaching explosive limits
- Recommend specialized equipment when needed (SCBA, radiation suits)
- Warn when sensor readings are degraded or unreliable
- Require human expert review for all critical safety decisions

---

## 5. Archaeological Exploration

**Priority:** Heritage Preservation and Non-Destructive Survey

### Mission Objective

Use autonomous or semi-autonomous agents to progressively map fragile or inaccessible heritage environments while minimizing human entry and physical disturbance.

Primary goals:
- Create high-fidelity 3D maps of chambers and passages
- Document visual features with minimal disturbance
- Identify areas requiring expert review
- Establish environmental baseline (temperature, humidity, air quality)

### Terrain Characteristics

- Fragile underground chambers and tombs
- Cave systems with historical or archaeological significance
- Buried passageways and ancient tunnels
- Wells, ruins, and sealed chambers
- GPS completely denied
- Complete darkness
- Dust, moisture, unstable surfaces
- Preservation-sensitive artifacts and wall surfaces
- Fragile ancient architecture

### Recommended Agents

**Micro Scout Drone:**
- Compact frame for narrow ancient passages
- Low-speed navigation for minimal air disturbance
- Advanced obstacle avoidance
- Low-light camera
- NFC black-box recovery module

**LiDAR Mapping Drone:**
- High-fidelity LiDAR/depth mapping
- RGB still camera (high resolution)
- Multiple-pass refinement capability
- Shared map contribution
- High-confidence reconstruction

**Low-Light Imaging Drone:**
- Specialized low-light camera
- Infrared/night vision sensor pack
- Still-image capture mode
- Minimal air disturbance design (low prop wash)
- Visual documentation capability

**Static Relay / Environmental Node:**
- Mesh relay capability
- Temperature sensor
- Humidity sensor
- O₂ sensor
- CO₂ sensor
- Dust/particulate monitoring
- Long-life battery for extended deployment

### Sensor / Technology Packs

**High-Fidelity Mapping:**
- LiDAR/depth mapping (millimeter accuracy)
- Photogrammetry-capable RGB cameras
- Structured light scanning (future)
- Multi-pass alignment algorithms

**Visual Documentation:**
- Low-light cameras
- Infrared/night vision
- High-resolution still cameras
- Minimal lighting to reduce heat and light exposure

**Environmental Monitoring:**
- Temperature sensors (baseline and monitoring)
- Humidity sensors (preservation conditions)
- O₂ sensors (safety for potential human entry)
- CO₂ sensors (air circulation assessment)
- Dust/particulate monitors

**Navigation:**
- LiDAR-based obstacle avoidance
- IMU for dead reckoning
- Fragile surface proximity warnings

### Communications Model

**Primary:** Mesh relay networks with static nodes

**Strategy:**
- Deploy static relay nodes at chamber entrances
- Low-power mesh networking to minimize interference
- Store-and-forward capability for deep exploration (future)
- Tethered/fiber data connections for extended missions (future)
- NFC black-box recovery for failed agents

**Challenges:**
- Rock and ancient masonry attenuate signals
- Preservation requirements limit transmit power
- Narrow passages require careful relay placement
- Multi-hop latency acceptable for non-emergency mission

### Navigation Intelligence

**Coordinate System:** Local mission 3D grid with site entrance as origin

**Compass Reliability:** Variable (45-85% confidence depending on rock composition)
- Natural caves: Moderate interference from mineral deposits
- Ancient structures: Variable interference from building materials
- Tombs and chambers: Good to acceptable compass performance

**Key Measurements:**
- Distance from entrance (actual passage path)
- Bearing from entrance (when compass reliable)
- Depth below surface (critical for planning access)
- Chamber dimensions and geometry
- Fragile zone proximity warnings

**Vertical Profile:**
- Surface entry: 0m reference
- Descending passages: -2m, -5m, -10m depths
- Deep chambers: -15m+ below surface

### Media Returns

**Generated/Captured Media:**
- High-resolution chamber imagery
- LiDAR point clouds (millimeter accuracy)
- Low-light wall surface documentation
- Environmental condition time-series data
- Chamber geometry visualizations

**Media Quality:**
- Minimal lighting to protect surfaces
- Low-light and infrared imaging preferred
- High-resolution stills over video (reduces disturbance)
- Environmental data logged continuously

**Preservation Constraints:**
- Minimize light exposure to ancient surfaces
- Reduce air disturbance (prop wash) near artifacts
- No physical contact with surfaces
- Document before any intervention

### Failure Risks

**Sensor Degradation:**
- Dust occlusion affecting LiDAR and cameras
- High humidity causing condensation on lenses
- Low-light image quality degradation

**Navigation Challenges:**
- Narrow ancient passages (built for human, not drone dimensions)
- Fragile surface proximity warnings
- Disorientation in complex tomb layouts

**Communications:**
- Signal loss in deep chambers without relays
- Rock composition variability affects range

**Agent Recovery:**
- Agent stranded in tight passage
- NFC recovery available if powered down
- Preservation priority: Remove failed agent if safe, document if not

### Escalation Triggers

**Elevated Escalation:**
- Agent approaching fragile artifact or surface
- Environmental readings outside acceptable range
- Navigation confidence drops in complex passages

**Critical Escalation:**
- Risk of physical contact with artifact or wall
- Agent failure in chamber with no recovery path
- Environmental damage detected (temperature spike, humidity change)

**Actions on Escalation:**
- Immediate halt of agent near fragile areas
- Human expert review before proceeding
- Environmental monitoring increase
- Document situation before any recovery attempts

### Expected Outputs

**Mapping Products:**
- High-fidelity 3D chamber reconstruction (millimeter accuracy)
- Progressive chamber map with gradual sector reveal
- Fragile-zone markers and no-fly zones
- Access route confidence map
- Multi-agent scan overlap regions (higher confidence)

**Visual Documentation:**
- Image catalog organized by chamber and feature
- Low-light visual documentation of walls, ceilings, floors
- Artifact candidate markers (review only, not definitive)
- Visual condition assessment imagery

**Environmental Products:**
- Temperature baseline by chamber
- Humidity profiles
- Air quality readings (O₂, CO₂)
- Dust/particulate levels
- Environmental stability assessment

**Operational Products:**
- Relay chain topology map
- Safe human access route recommendations
- Areas requiring specialized equipment
- Human review priority list

### AI Analyst Behaviour

**Analysis Tasks:**
- Identify areas of archaeological interest requiring expert review
- Flag possible artifact candidates as "review only" (not definitive identification)
- Assess environmental conditions for preservation
- Recommend chambers safe for careful human entry
- Warn where confidence is low or data quality degraded

**Output Requirements:**
- "Possible feature" language, not definitive artifact identification
- Confidence scores for all observations
- Human expert review required flag for all significant findings
- Conservative recommendations for physical access

**Preservation Principles:**
- Recommend non-invasive sensing over physical inspection
- Flag areas where agent presence may cause disturbance
- Prioritize remote documentation over direct access
- Suggest additional non-destructive scanning before human entry

**Constraints:**
- Do NOT make definitive archaeological identifications (leave to human experts)
- Present findings as "possible artifact" or "feature of interest"
- Recommend expert review for all medium+ confidence observations
- Warn prominently when agent risks disturbing fragile surfaces
- Conservative bias: When uncertain, recommend caution and expert consultation

---

## Use Case Template

When creating new use cases, include all sections for consistency:

### Required Sections

1. **Mission Objective** - Clear goals and priorities
2. **Terrain Characteristics** - Environment description and challenges
3. **Recommended Agents** - Hardware types and configurations
4. **Sensor / Technology Packs** - Required sensor suites
5. **Communications Model** - Networking strategy and challenges
6. **Navigation Intelligence** - Coordinate system, compass reliability, key measurements
7. **Media Returns** - Expected media types and quality considerations
8. **Failure Risks** - Anticipated failure modes and consequences
9. **Escalation Triggers** - Conditions requiring elevated or critical response
10. **Expected Outputs** - Deliverable products organized by category
11. **AI Analyst Behaviour** - Analysis tasks, output requirements, and constraints

### Tone Guidelines

- **Safety-focused** - Prioritize human safety in all recommendations
- **Simulation-first** - Remember this is demonstration/training, not real-time control
- **Non-weaponized** - No military applications, focus on rescue/inspection/heritage
- **Interoperability-aware** - Consider data standards and exchange formats
- **Preservation-conscious** - For heritage use cases, emphasize non-destructive methods

---

**Document Version:** 2.0  
**Last Updated:** May 30, 2026  
**Status:** Active - Use cases match current implementation
