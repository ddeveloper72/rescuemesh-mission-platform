Please improve the Tactical Map SVG animation so the drones visibly start from the entry point and autonomously search outward through the terrain.

Current issue:
The tactical map renders sectors and agents, but the agents appear already placed in their final positions. The demo should show the mission unfolding: agents begin at the entry point, move outward, map sectors progressively, and leave relay/static assets behind where appropriate.

Do not add Three.js, Cesium, WebGL, or a heavy mapping library yet. Keep the tactical map lightweight using SVG, TypeScript, and Tailwind.

Goals:

1. Agents should start from the entry point.
2. Agents should move along visible search paths over simulated mission time.
3. Sectors should be revealed progressively as the mission clock advances.
4. Relay assets should remain behind when deployed.
5. Hazard/detection markers should appear only after the relevant event time.
6. Movement should look autonomous and purposeful, not random.
7. The map should update using the existing Django mission state and polling.
8. Do not break the existing API shape unless a small additive field is needed.

Implementation guidance:

Add a use-case-specific route/path model in tactical-map-manager.ts.

Each use case should define:

* entry sector
* ordered sectors
* paths between sectors
* reveal time for each sector
* agent route waypoints
* relay deployment point
* detection marker timings
* failure marker timings

Suggested TypeScript shape:

```ts
export interface TacticalWaypoint {
  time: number; // simulated elapsed seconds
  x: number;
  y: number;
  sectorId: string;
  label?: string;
}

export interface TacticalAgentRoute {
  agentId: string;
  startsAt: number;
  route: TacticalWaypoint[];
  leavesAssetBehind?: {
    time: number;
    assetId: string;
    label: string;
    x: number;
    y: number;
    state: 'relay' | 'static_sensor' | 'failed' | 'nfc_readable' | 'sacrificed';
  };
}

export interface TacticalSector {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  sectorType: 'entry' | 'corridor' | 'void' | 'blocked' | 'cave' | 'water' | 'industrial' | 'hazard';
  revealAt: number;
  confidenceAtReveal?: number;
}

export interface TacticalPath {
  fromSectorId: string;
  toSectorId: string;
  revealAt: number;
  risk?: 'low' | 'medium' | 'high' | 'critical';
}
```

The current mission state already has elapsed time. Use this to interpolate agent position between waypoints.

Example behaviour for Collapsed Building Search:

* At 00:00 all mobile drones start at Entry.
* At 00:30 Scout Drone moves from Entry to Corridor A.
* At 01:30 Corridor A is revealed.
* At 02:30 Scout Drone reaches Void Space 1.
* At 03:00 map coverage increases and Void Space 1 appears.
* At 03:30 Thermal/Audio Drone follows from Entry to Corridor A.
* At 04:00 Relay Drone stops near Entry/Corridor A and becomes a relay.
* At 05:00 Collapsed Section appears as blocked/hazard.
* At 06:00 thermal marker appears in Void Space 1.
* At 07:00 audio marker appears deeper in the structure.
* If an agent state becomes degraded/failed/sacrificed, stop movement and show last known position.

Example behaviour for Cave Rescue:

* All drones start at Entrance Chamber.
* Scout Drone moves into Main Tunnel.
* Relay Drone stops at Entrance Chamber or Main Tunnel junction.
* Narrow Passage appears only after scout reaches it.
* Micro mapper enters Deep Squeeze later.
* If micro mapper fails or becomes NFC-readable, leave a marker at Deep Squeeze.
* Audio/tapping marker appears only after the event time.

Example behaviour for Flooded Structure:

* Agents start at Entry Pool.
* Amphibious agent moves into Flooded Corridor.
* Flood zones reveal progressively: shallow, deep, submerged.
* Environmental sensor remains near Entry Pool or Plant Room.
* Electrical hazard appears only after the simulated event time.
* Thermal anomaly appears above waterline later in the mission.

Example behaviour for Industrial Inspection:

* Agents start at Entry Point.
* Industrial Inspector moves to Plant Room, then Pipe Gallery, then Duct Section.
* Plant Room Monitor remains in Plant Room as a static node.
* Thermal Specialist moves to Control Cabinet after thermal event.
* Thermal hotspot markers appear only after relevant event times.
* Gas detection appears in Pipe Gallery only after methane event.
* Pressure leak marker appears in Duct Section only after pressure leak event.

Animation requirements:

* Use smooth SVG transitions or CSS transitions for agent marker movement.
* Show a faint path trail behind each moving agent.
* Show mapped/revealed sectors with stronger opacity.
* Show unrevealed sectors faintly, hidden, or labelled “Unknown” until reveal time.
* Show scan pulse around active agents.
* Show relay chain lines when relay nodes are active.
* Show detection markers with clear icons:

  * thermal: 🔥
  * audio: 🔊
  * gas: ☁
  * water/electrical hazard: ⚡
  * failed/NFC-readable asset: ⬢ or NFC label
* Add a small map status line:
  “Autonomous search expanding from entry point”
  “Sector reveal based on simulated mission time”
  “Agent positions interpolated from mission route”

Important:
The map should not simply place agents based on static coordinates. Agent positions should be calculated from:

* mission elapsed time
* use case route definition
* agent state
* mission events

If the API already returns elapsed time, use it.
If the API does not return enough timing information, derive it from mission_state.simulation_clock.elapsed_seconds.

If an agent is failed, sacrificed, abandoned, or nfc_readable:

* stop it at the route position matching the failure time
* show a persistent asset marker
* include tooltip text explaining why it stopped

Please keep the UI responsive and readable. The tactical map should still work on laptop screens.

After implementation, report:

* files changed
* route/path model added
* how positions are interpolated
* which use cases have animated routes
* how sector reveal timing works
* any limitations
