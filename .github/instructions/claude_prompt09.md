Please improve the RescueMesh tactical map simulation so that drone movement is visually realistic and causally consistent.

Current issue:
In the Cave Rescue scenario, one drone starts at the entry point and maps the main tunnel, but a later drone appears directly in the Narrow Passage. This breaks the realism of the mission. All mobile drones should originate from the entry point, base station, or a previously visible staging point. They should visibly travel into the terrain from the start, not appear inside unmapped or unreachable areas.

Core realism rule:
A drone may not appear in a sector unless it has a visible route from the entry point or from a previously deployed parent asset such as a relay node, base station, or carrier agent.

Please implement route continuity and exploration causality.

Requirements:

1. All mobile agents start from the entry/base sector

For each use case:

* Collapsed Building Search: Entry
* Cave Rescue: Entrance Chamber
* Flooded Structure: Entry Pool
* Industrial Inspection: Entry Point

Every mobile drone should have a route beginning at that entry sector.

Static assets may appear only if:

* they are deployed by a mobile agent that travelled there, or
* they are part of the initial base setup at the entry point.

2. No teleporting agents

If a drone is shown in Narrow Passage, Deep Squeeze, Void Space, Duct Section, Control Cabinet, Submerged Zone, or any non-entry location, the user should be able to visually understand how it got there.

Use one of these approaches:

* animate the drone along a route from entry to current sector, or
* show a route trail from entry to the current sector, or
* show a deployment event explaining which agent carried/deployed it.

Do not spawn a mobile drone directly in a deep sector.

3. Route timeline model

Update the route definitions so every agent has a full route from the entry point.

Example Cave Rescue route logic:

Scout Drone:
00:00 Entrance Chamber
00:30 Main Tunnel
02:00 Narrow Passage
04:00 Junction Chamber
06:00 Deep Squeeze

Relay Drone:
00:00 Entrance Chamber
01:00 Main Tunnel
02:30 Stop at Main Tunnel/Junction and switch to relay mode

Micro Mapper:
00:00 Entrance Chamber
01:30 Main Tunnel
03:00 Narrow Passage
05:00 Deep Squeeze
06:30 Failure/NFC-readable state if the scenario requires it

The Micro Mapper must be seen travelling through Entrance Chamber and Main Tunnel before reaching Narrow Passage or Deep Squeeze.

4. Terrain reveal and route dependency

A drone should not route through a sector until that sector is at least detected or partially mapped.

Suggested logic:

* First scout may enter unknown terrain and reveal it.
* Later drones can use the scout’s mapped route.
* A drone can follow a known path faster or with higher confidence after another drone maps it.
* The UI should show that later drones benefit from previous mapping.

5. Hazard-aware behaviour

If a hazard has already been mapped by another drone, later drones should not blindly enter it.

Later drones should either:

* navigate around the hazard if an alternate route exists,
* stop before the hazard and scan it,
* deploy a relay/sensor near the hazard,
* proceed cautiously with reduced speed/confidence,
* enter only if their role/capability allows it,
* or “punch through” / overcome the obstacle if the scenario explicitly gives them that capability.

Examples:

* A scout detects a narrow unstable passage.
* The micro mapper can proceed because it is small and designed for narrow passages.
* The larger relay drone should stop before the narrow passage and become a relay.
* If a blocked section exists, no drone should pass through it unless it has a capability such as “obstacle penetration”, “debris gap navigation”, “amphibious traversal”, or “confined-space micro frame”.

6. Agent capability checks

Add or use existing capabilities to determine whether an agent can proceed through a hazard.

Example capabilities:

* narrow_passage_navigation
* low_clearance_navigation
* amphibious_traversal
* thermal_search
* relay_deployment
* hazardous_atmosphere_monitoring
* debris_gap_navigation
* confined_space_micro_frame
* obstacle_penetration_placeholder
* sacrificial_probe_mode

If a sector has a hazard, the route planner should check whether the agent has an appropriate capability.

If no capability exists:

* the agent stops before the hazard,
* records the hazard,
* sends the data back,
* and either waits, reroutes, or becomes a relay/static sensor.

7. Visual hazard response

Show the user what the drone is doing when it reaches a hazard.

Examples:

* “Avoiding mapped hazard”
* “Holding before unstable passage”
* “Proceeding: micro-frame capable”
* “Deploying relay before signal-loss zone”
* “Scanning blocked route”
* “Sacrificial probe mode active”
* “Obstacle penetration attempt”
* “Path rejected: insufficient capability”

This can appear as:

* tooltip text,
* a small status label near the agent,
* a timeline event,
* or a dashboard alert.

8. Known-path advantage

If one drone has already mapped a sector, later drones should move through it more confidently.

Visual behaviours:

* known path line becomes brighter
* later drone movement is smoother/faster
* confidence increases
* sector detail improves
* repeated scan count increments
* map detail level improves

This supports the concept that drones share mapped terrain and can navigate areas mapped by another drone.

9. Route trail and provenance

Each sector should track which agents mapped it.

When hovering or clicking a sector, show:

* first detected by
* mapped by
* scan count
* confidence
* known hazards
* last updated time

For example:
“Main Tunnel — mapped by Cave Scout Drone, Relay Drone. Scan count: 4. Confidence: 82%.”

10. Backend mission state

If needed, extend the Django simulation state additively. Do not break the existing API.

Useful additions could include:

```json
"route_planning": {
  "entry_sector_id": "entrance-chamber",
  "known_paths": [
    {
      "from": "entrance-chamber",
      "to": "main-tunnel",
      "status": "mapped",
      "confidence": 82
    }
  ],
  "agent_routes": [
    {
      "agent_id": "cave-scout-drone",
      "origin_sector_id": "entrance-chamber",
      "current_sector_id": "main-tunnel",
      "target_sector_id": "narrow-passage",
      "route_status": "moving",
      "decision": "Following newly mapped tunnel route"
    }
  ]
}
```

Also consider adding per-agent fields such as:

```json
"navigation_status": {
  "origin_sector_id": "entrance-chamber",
  "current_sector_id": "main-tunnel",
  "target_sector_id": "narrow-passage",
  "path_confidence": 76,
  "decision": "Proceeding through known route",
  "blocked_by_hazard": false,
  "capability_used": "narrow_passage_navigation"
}
```

11. Frontend route calculation

If the backend does not provide full route_planning data yet, calculate it in `tactical-map-manager.ts` using:

* elapsed simulation time
* agent route definitions
* sector reveal times
* hazard reveal times
* agent capabilities
* agent state

But keep the design ready to accept backend route planning later.

12. Acceptance criteria

Please test the Cave Rescue live simulation specifically.

At no point should:

* a mobile drone appear directly in the Narrow Passage,
* a mobile drone appear directly in Deep Squeeze,
* a relay appear deep inside the cave without travelling there,
* an agent pass through a known hazard without a visible decision or capability explanation.

The user should visually see:

* drones starting from Entrance Chamber,
* scout mapping Main Tunnel,
* later drones following the mapped route,
* relay stopping where appropriate,
* micro mapper proceeding through Narrow Passage because it has the right capability,
* Deep Squeeze appearing only after the route is discovered,
* any lost/NFC-readable asset remaining at its last reachable location.

Please apply the same principle to all use cases:

* Collapsed Building Search: all drones start at Entry and move through corridors/voids.
* Flooded Structure: all agents start at Entry Pool and move through flooded zones only if capable.
* Industrial Inspection: all agents start at Entry Point and move through plant-room zones based on role and hazard capability.

Do not add Three.js, Cesium, WebSockets, Celery, ROS, or real LiDAR yet. Keep the current SVG tactical map and HTTP polling architecture.
