Cave Rescue

Priority: Life Safety / Navigation Safety

Mission Objective

Map complex underground cave passages, identify safe routes, detect signs of trapped persons, and maintain communication links in GPS-denied, dark, humid, and irregular terrain.

Terrain Characteristics

• Type: Natural cave system with tunnels, chambers, vertical shafts, narrow squeezes, uneven floors, water pools, and loose rock
• GPS: Fully denied underground
• Communications: Severe attenuation through rock; line-of-sight radio often unreliable
• Lighting: Complete darkness except drone-mounted illumination
• Hazards: Tight passages, falling rock, moisture, water, mud, unstable footing, low oxygen pockets, disorientation risk

Recommended Agents
Scout Drone — Drone A

Primary exploration and route-mapping agent for initial entry into unknown cave passages.

• LiDAR or depth sensor for 3D passage mapping
• Low-light RGB camera
• Thermal camera
• Obstacle avoidance
• High-efficiency battery profile

Relay Drone — Drone B

Maintains the communication chain between the cave entrance and deeper agents.

• Mesh radio
• Signal-strength monitoring
• Autonomous landing mode
• Low-power relay mode
• NFC black-box module

Micro Mapper — Drone C

Small form-factor drone for narrow passages, side chambers, and tight squeezes.

• Compact protected frame
• Short-range LiDAR/depth sensor
• Audio sensor
• Temperature and humidity sensor
• Disposable / one-way mission mode

Ground Sensor Node

Static environmental and communications support node placed at key junctions.

• Mesh repeater
• Temperature and humidity sensor
• Air quality sensor
• Passive audio monitoring
• Long-life battery

Expected Failures
Rock Attenuation

Radio signals become weak or unavailable after bends, chambers, or deep rock sections.

Moisture Degradation

Humidity, dripping water, or condensation may reduce sensor quality and increase electrical risk.

Navigation Drift

SLAM confidence may decrease in repetitive or feature-poor tunnel sections.

Confined-Space Collision

Narrow passages increase the likelihood of propeller strikes or protective cage contact.

Tactical Relay Decision

A drone may land at a cave junction and become a static relay to preserve the communication path.

Expected Outputs

• 3D Cave Passage Map: Point cloud or tunnel mesh showing chambers, shafts, obstructions, and traversable routes
• Route Safety Estimate: Confidence-ranked routes for rescue teams
• Thermal Anomalies: Heat signatures that may indicate humans, animals, or warm airflow
• Audio Events: Voice-like sounds, movement, water flow, falling rock, or tapping patterns
• Environmental Readings: Temperature, humidity, air quality, and possible low-oxygen risk indicators
• Relay Map: Communication chain from cave entrance to deep exploration agents
• Lost Asset Markers: Last known locations of landed, failed, or abandoned drones/nodes
• AI Analysis: Suggested route priorities and human-review alerts

Flooded Structure

Priority: Life Safety / Environmental Hazard Assessment

Mission Objective

Survey partially flooded buildings, tunnels, basements, underground car parks, culverts, or industrial spaces where water, debris, poor visibility, and electrical hazards make human access unsafe.

Terrain Characteristics

• Type: Flooded or partially submerged built environment
• GPS: Denied indoors or underground
• Communications: Radio degraded by concrete, metal, and water; underwater communications extremely limited
• Lighting: Dark, reflective, and visually confusing due to water surfaces
• Hazards: Deep water, floating debris, submerged obstacles, contamination, electrical risk, unstable surfaces, trapped persons

Recommended Agents
Surface Scout Drone — Drone A

Aerial survey agent for dry or partially flooded upper spaces.

• RGB camera
• Thermal camera
• LiDAR/depth sensor
• Spotlight
• Water-resistant frame

Amphibious Micro Agent — Drone B

Hybrid or amphibious unit for shallow flooded areas, water-surface inspection, and low-clearance spaces.

• Water-resistant or waterproof housing
• Buoyancy support
• Short-range sonar or depth sensor
• Temperature sensor
• NFC black-box module

Environmental Sensor Node

Static sensor node deployed near water entry points or hazard zones.

• Water level sensor
• Temperature sensor
• Pressure sensor
• Air quality sensor
• Contamination indicator placeholder

Relay Node

Maintains communication between exterior command and interior agents.

• Mesh radio
• High-position deployment mode
• Battery or tethered power
• Low-power survival mode

Expected Failures
Water Damage

Sensors, motors, or electronics may degrade or fail due to splashing, immersion, or condensation.

Reflection and Refraction Errors

LiDAR, camera, or depth readings may become unreliable near reflective water surfaces.

Signal Loss

Radio communications may degrade rapidly through concrete, metal, and water-filled spaces.

Buoyancy or Mobility Failure

Amphibious agents may become trapped by debris, tangled material, or narrow submerged gaps.

Tactical Abandonment Decision

An amphibious unit may be left in place as a water-level monitor, beacon, or passive sensor if recovery is unsafe.

Expected Outputs

• Flood Extent Map: Map layer showing dry, shallow, deep, and inaccessible zones
• Depth / Pressure Readings: Approximate water depth and pressure changes by location
• Thermal Anomalies: Possible human presence above waterline or behind obstructions
• Submerged Obstruction Map: Sonar/depth-based estimate of underwater hazards
• Environmental Alerts: Temperature, air quality, possible contamination, and electrical-risk notes
• Asset Placement Map: Locations of relay nodes, amphibious agents, failed units, and static sensors
• Access Route Suggestions: Safe or unsafe route estimates for rescuers
• AI Analysis: Prioritised areas for human review, rescue entry, or further robotic inspection

Industrial Inspection

Priority: Infrastructure Safety / Hazard Prevention

Mission Objective

Inspect dangerous, confined, or hard-to-access industrial environments such as tanks, ducts, silos, utility tunnels, plant rooms, chimneys, warehouses, and processing facilities without exposing personnel to unnecessary risk.

Terrain Characteristics

• Type: Industrial interior, confined space, plant room, tank, pipe gallery, ducting, or service tunnel
• GPS: Denied indoors or inside metal structures
• Communications: Interference from metal, machinery, concrete, and electromagnetic noise
• Lighting: Variable; may include dark spaces, glare, reflective surfaces, or steam/dust
• Hazards: Heat, gas, chemicals, moving machinery, confined-space entry risks, sharp metal, poor ventilation, electrical equipment

Recommended Agents
Inspection Drone — Drone A

Primary visual and geometric inspection agent.

• RGB camera
• LiDAR or depth sensor
• Thermal camera
• Protective cage
• Stable hover mode

Environmental Drone — Drone B

Specialised agent for environmental and hazard detection.

• Temperature sensor
• Gas sensor placeholder
• Humidity sensor
• Pressure sensor
• Audio/vibration sensor

Close-Range Detail Drone — Drone C

Small drone for detailed inspection of pipes, ducts, cracks, corrosion points, and equipment surfaces.

• Macro/close-range camera
• Compact frame
• LED lighting
• NFC black-box module
• Short-duration precision flight mode

Static Monitoring Node

Deployable node left behind for temporary monitoring of hazardous or unstable conditions.

• Temperature sensor
• Gas/air quality sensor placeholder
• Vibration/acoustic sensor
• Mesh relay
• Long-life battery

Expected Failures
Electromagnetic Interference

Industrial equipment may interfere with compass, radio, or sensor readings.

Reflective Surface Confusion

Metal surfaces, tanks, glass, or water may reduce LiDAR/camera confidence.

Heat or Gas Exposure

High temperatures, fumes, or poor air quality may degrade hardware or trigger early retreat.

Confined-Space Collision

Narrow spaces, cables, beams, and pipework increase collision risk.

Static Monitoring Decision

An agent or sensor node may be left in place to monitor vibration, temperature, or gas levels after the main inspection pass.

Expected Outputs

• 3D Asset Map: Point cloud or model of tanks, ducts, machinery, pipework, and access spaces
• Defect Indicators: Possible corrosion, cracks, obstructions, leaks, deformation, or abnormal heat
• Thermal Map: Heat signatures around motors, panels, pipes, machinery, or confined spaces
• Environmental Readings: Temperature, humidity, pressure, air quality, and gas-risk placeholders
• Audio / Vibration Events: Unusual mechanical sounds, vibration patterns, or impact events
• Inspection Confidence Score: Confidence level for each inspected zone or asset
• Static Sensor Placement Map: Nodes left behind for continued monitoring
• AI Analysis: Prioritised defect list, recommended human review points, and follow-up inspection actions