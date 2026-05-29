Excellent work on the dynamic mission simulation layer.

Next, please extend the deterministic simulation engine so that Cave Rescue, Flooded Structure, and Industrial Inspection are no longer placeholder/static simulations.

Do not change the API response shape. Reuse the same MissionState structure already implemented for collapsed-building-search.

Do not add WebSockets, Celery, ROS, or real LiDAR yet. Keep the system deterministic and HTTP polling-based.

For each use case, implement use-case-specific dynamic behaviour.

Cave Rescue simulation should include:
- cave passage map coverage increasing over time
- mapped sectors such as Entrance Chamber, Narrow Passage, Main Tunnel, Junction Chamber, Deep Squeeze
- SLAM/navigation confidence that may drift over time
- communication degradation caused by rock attenuation
- relay drone landing at a cave junction when signal becomes weak
- humidity/moisture environmental readings
- possible audio event such as tapping, voice-like sound, water flow, or falling rock
- lost or NFC-readable asset marker if a micro mapper fails or enters one-way mode
- AI analyst summary that changes as map coverage and detections increase

Flooded Structure simulation should include:
- flood map coverage increasing over time
- water depth or pressure readings changing by sector
- submerged obstruction detection
- signal degradation through concrete, metal, and water
- amphibious agent battery and mobility degradation
- environmental alerts such as contamination placeholder, low temperature, electrical hazard risk, or unsafe water depth
- possible thermal anomaly above waterline
- asset placement markers for relay node, environmental sensor, and amphibious unit
- AI analyst summary that changes as flood extent and hazard confidence increase

Industrial Inspection simulation should include:
- 3D industrial asset map coverage increasing over time
- inspected zones such as Plant Room, Pipe Gallery, Tank Interior, Duct Section, Control Cabinet
- thermal hotspot detection
- gas/air quality placeholder alert
- vibration or abnormal audio event
- reflective surface or electromagnetic interference reducing sensor confidence
- static monitoring node deployment
- defect indicators such as corrosion, obstruction, leak risk, deformation, or abnormal heat
- AI analyst summary that ranks defects and recommends human review points

Also update the Astro UI so TODO text is hidden or replaced when live Django simulation data is available.

The demo pages should clearly show whether they are using:
- live Django simulation data
or
- local static fallback data

Please add a small visual indicator such as:
“Data source: Django simulation”
or
“Data source: local fallback”

Please ensure:
- /demo/live works
- /demo/collapsed-building-search works
- /demo/cave-rescue works
- /demo/flooded-structure works
- /demo/industrial-inspection works

If /demo/live is only for collapsed-building-search, either:
1. make /demo/live redirect to the collapsed building live demo, or
2. rename/clarify it as /demo/live/collapsed-building-search, or
3. allow /demo/live?use_case=cave-rescue style selection.

After implementation, provide:
- files changed
- simulation behaviours added for each use case
- API endpoints tested
- frontend routes tested
- screenshots or console outputs if available
- remaining TODOs