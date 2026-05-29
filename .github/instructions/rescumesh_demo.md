Please refactor the RescueMesh Astro demo so that all four use cases share the same reusable demo engine and dashboard layout.

The four use cases are:

1. collapsed-building-search
2. cave-rescue
3. flooded-structure
4. industrial-inspection

Do not create four separate hardcoded demo pages with duplicated logic. Instead, create a data-driven demo architecture where each use case provides parameters and the shared demo components render the correct mission profile, agents, sensors, failures, outputs, timeline events, and map placeholders.

Current frontend stack:

* Astro
* Tailwind CSS
* TypeScript
* No inline CSS
* Prefer reusable components
* Keep the UI dark, technical, mission-control style
* Keep the existing navigation and layout style

Goal:
Create a reusable demo system where Astro uses the same demo template for each use case, but the displayed data and simulated mission behaviour change according to the selected use case profile.

Required pages:

* /demo/collapsed-building-search
* /demo/cave-rescue
* /demo/flooded-structure
* /demo/industrial-inspection

Each page should use the same Astro page template or dynamic route if appropriate.

Create or update a TypeScript data model similar to this:

```ts
export interface UseCaseDemoProfile {
  slug: string;
  title: string;
  priority: string;
  missionId: string;
  status: 'Simulated' | 'Planned' | 'Active' | 'Completed';

  missionObjective: string;

  terrain: {
    type: string;
    gps: string;
    communications: string;
    lighting: string;
    hazards: string[];
  };

  agents: DemoAgent[];

  expectedFailures: DemoFailure[];

  expectedOutputs: DemoOutput[];

  simulation: {
    mapType: 'void-map' | 'cave-map' | 'flood-map' | 'industrial-map';
    environmentTags: string[];
    defaultConfidence: number;
    communicationRisk: 'low' | 'medium' | 'high' | 'severe';
    batteryRisk: 'low' | 'medium' | 'high';
    sensorRisk: 'low' | 'medium' | 'high';
    missionDurationMinutes: number;
  };

  timeline: DemoTimelineEvent[];

  aiAnalyst: {
    role: string;
    promptSummary: string;
    expectedFindings: string[];
    humanReviewRequired: boolean;
  };
}

export interface DemoAgent {
  id: string;
  name: string;
  role: string;
  description: string;
  state:
    | 'healthy'
    | 'degraded'
    | 'intermittent'
    | 'failed'
    | 'landed_relay'
    | 'abandoned'
    | 'sacrificed'
    | 'nfc_readable'
    | 'black_box_recovered';
  batteryPercent: number;
  locationLabel: string;
  capabilities: string[];
  sensors: string[];
  nfcRecoveryAvailable?: boolean;
}

export interface DemoFailure {
  name: string;
  affectedComponent: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  dashboardEffect: string;
}

export interface DemoOutput {
  name: string;
  outputType:
    | '3d-map'
    | 'thermal'
    | 'audio'
    | 'environmental'
    | 'device-scan'
    | 'relay-map'
    | 'ai-analysis'
    | 'report';
  description: string;
  confidenceRequired: boolean;
}

export interface DemoTimelineEvent {
  time: string;
  title: string;
  description: string;
  assetId?: string;
  eventType:
    | 'mission-start'
    | 'mapping'
    | 'relay'
    | 'sensor-detection'
    | 'failure'
    | 'ai-analysis'
    | 'operator-review'
    | 'mission-end';
  confidence?: number;
}
```

Create a data file such as:

```text
src/data/useCaseDemoProfiles.ts
```

This file should export all four use case profiles as structured TypeScript data.

Create reusable dashboard components such as:

```text
src/components/demo/DemoDashboard.astro
src/components/demo/MissionHeader.astro
src/components/demo/MissionMapPanel.astro
src/components/demo/AgentStatusPanel.astro
src/components/demo/TelemetryPanel.astro
src/components/demo/SensorOutputsPanel.astro
src/components/demo/TimelinePanel.astro
src/components/demo/AiAnalystPanel.astro
src/components/demo/MissionReportPanel.astro
```

The shared demo dashboard should accept a `UseCaseDemoProfile` object as a prop.

The Mission Map panel does not need to implement a real 3D map yet. For now, render a high-quality placeholder that changes depending on `simulation.mapType`.

Examples:

* collapsed-building-search should show a collapsed structure / void map placeholder
* cave-rescue should show a cave passage / tunnel network placeholder
* flooded-structure should show flood zones / submerged areas placeholder
* industrial-inspection should show tanks / pipes / plant-room placeholder

The placeholder should include:

* asset markers
* left-behind hardware markers
* relay chain indicators
* confidence label
* map type label
* simulated status indicator

The Agent Status panel should display:

* agent name
* role
* current state
* battery percentage
* location label
* sensors
* NFC recovery availability if true

The Failure panel or telemetry area should show:

* expected failures for the use case
* affected component
* severity
* dashboard effect

The Timeline panel should render the use-case-specific timeline events.

The AI Analyst panel should render:

* AI analyst role
* prompt summary
* expected findings
* whether human review is required

The Mission Report panel should summarise:

* mission objective
* mapped outputs
* detected risks
* failed/degraded assets
* left-behind assets
* recommended human review points

For the four use cases, use these scenario differences:

Collapsed Building Search:

* Map type: void-map
* Priority: Life Safety
* Main risks: dust occlusion, radio packet loss, battery drain, structural collapse
* Outputs: 3D void map, thermal anomalies, audio events, device scan, relay map, access routes, AI analysis
* Agents: survey drone, detection drone, deep penetration drone, relay node

Cave Rescue:

* Map type: cave-map
* Priority: Life Safety / Navigation Safety
* Main risks: rock attenuation, moisture degradation, SLAM drift, confined-space collision, relay loss
* Outputs: 3D cave passage map, route safety estimate, thermal anomalies, audio events, environmental readings, relay map, lost asset markers, AI analysis
* Agents: scout drone, relay drone, micro mapper, ground sensor node

Flooded Structure:

* Map type: flood-map
* Priority: Life Safety / Environmental Hazard Assessment
* Main risks: water damage, reflection/refraction errors, radio signal loss, buoyancy or mobility failure, electrical risk
* Outputs: flood extent map, depth/pressure readings, thermal anomalies, submerged obstruction map, environmental alerts, asset placement map, access route suggestions, AI analysis
* Agents: surface scout drone, amphibious micro agent, environmental sensor node, relay node

Industrial Inspection:

* Map type: industrial-map
* Priority: Infrastructure Safety / Hazard Prevention
* Main risks: electromagnetic interference, reflective surface confusion, heat/gas exposure, confined-space collision, static monitoring requirement
* Outputs: 3D asset map, defect indicators, thermal map, environmental readings, audio/vibration events, inspection confidence score, static sensor placement map, AI analysis
* Agents: inspection drone, environmental drone, close-range detail drone, static monitoring node

Implementation requirements:

1. Keep the existing RescueMesh visual identity.
2. Avoid duplicated page logic.
3. Use TypeScript types for all data.
4. Avoid inline CSS.
5. Use Tailwind utility classes and reusable components.
6. Keep components small and readable.
7. Ensure all four demo routes work.
8. Add navigation links from the main Demo page to each use case demo.
9. Use accessible semantic HTML where practical.
10. Do not connect to Django yet. This is still a frontend simulation using local TypeScript data.
11. Leave comments or TODOs showing where future Django API data will replace local demo data.
12. Make sure the project builds successfully.

Important architectural direction:
The Astro frontend should treat the local TypeScript data as a temporary stand-in for future Django database-backed mission templates. Later, Django will provide UseCaseTemplate, TerrainProfile, AgentRoleTemplate, SensorPackageTemplate, FailureProfile, ExpectedOutputTemplate, Mission, MissionAsset, and MissionEvent data through an API. For now, keep the local data shape close to what the future API will return.

After implementing, provide:

* a summary of files created or changed
* any assumptions made
* how to run the project
* any TODOs for the later Django integration
