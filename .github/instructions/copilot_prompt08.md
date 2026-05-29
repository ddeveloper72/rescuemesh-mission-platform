Please extend the RescueMesh live simulation and tactical map so the terrain is generated progressively from drone mapping data, rather than appearing as a fully known static layout.

Current direction:
The drones should not simply move over a pre-drawn map. They should start from the entry point and gradually reveal / reconstruct the terrain as they send mapping data back to mission control.

Think of this like an old-style computer game “fog of war” or map discovery model:

* unexplored terrain is hidden or dark
* first drone pass reveals a rough outline
* repeated scans increase confidence
* multiple drones mapping the same space increase detail and reliability
* hazardous sectors appear only when detected
* blocked or inaccessible areas appear only after mapping evidence is received

Do not add Three.js, Cesium, WebGL, or heavy map libraries yet. Keep the current SVG tactical map approach, but make it feel like terrain is materialising as the agents explore.

Core requirements:

1. Progressive terrain reveal
   Each use case should have sectors that reveal over simulated mission time.

A sector should have states such as:

* unknown
* detected
* partially_mapped
* mapped
* high_confidence
* hazardous
* blocked

Example:
At 00:00 only the Entry sector is visible.
At 00:30 a drone moves into the next sector and a rough outline appears.
At 01:30 LiDAR/depth scan improves the sector.
At 03:00 a second drone scans the same sector, increasing confidence.
At 05:00 a hazard marker appears after sensor confirmation.

2. Map confidence and detail level
   Add or derive per-sector confidence and detail level.

Suggested shape:

```ts
export interface TacticalSectorState {
  sectorId: string;
  status:
    | 'unknown'
    | 'detected'
    | 'partially_mapped'
    | 'mapped'
    | 'high_confidence'
    | 'hazardous'
    | 'blocked';
  confidence: number; // 0-100
  detailLevel: number; // 0-5
  mappedByAgentIds: string[];
  firstDetectedAt?: number;
  lastUpdatedAt?: number;
  scanCount: number;
}
```

3. Multi-agent mapping effect
   If two or more agents scan the same sector, the map should visibly improve.

Examples:

* Sector opacity increases
* Border becomes sharper
* Grid/point pattern becomes denser
* Confidence percentage increases
* Detail label changes from “rough scan” to “confirmed structure”
* AI analyst confidence improves

4. Use-case-specific terrain generation

Collapsed Building Search:

* Entry is known at start
* Corridor A appears after first scout movement
* Void Space 1 appears as a rough outline after LiDAR scan
* Collapsed Section appears as hazardous/blocked only after detection
* Thermal/audio markers appear later after sensor confirmation
* More than one drone scanning a void should increase confidence in accessible space detection

Cave Rescue:

* Entrance Chamber is known at start
* Main Tunnel materialises as scout drone moves forward
* Narrow Passage appears first as low-confidence terrain
* Junction Chamber appears after route confirmation
* Deep Squeeze appears only when micro mapper reaches it
* Multiple scans reduce SLAM drift and increase cave passage confidence
* Moisture/humidity may reduce detail or confidence
* Lost/NFC-readable asset marker appears only after failure event

Flooded Structure:

* Entry Pool is known at start
* Flooded Corridor appears as shallow/deep zones are measured
* Submerged Zone appears gradually from pressure/depth readings
* Sonar/depth scans reveal submerged obstacles
* Thermal anomaly above waterline appears only after sufficient scan confidence
* Electrical hazard marker appears only after environmental detection

Industrial Inspection:

* Entry Point / Plant Room known first
* Pipe Gallery, Duct Section, Control Cabinet, and Tank Interior reveal as agents inspect them
* Reflective surfaces or EMI may reduce confidence
* Thermal hotspots, gas detections, vibration anomalies, and pressure leaks appear after relevant sensor events
* Static monitoring node can continue improving detail after deployment

5. Add environmental hazardous atmosphere sensors
   Please add O₂, CO₂, and H₂ sensors to the technical/sensor pack model and simulation outputs.

These are critical for hazardous or explosive atmosphere detection.

Add these sensor types where appropriate:

* O₂ sensor / oxygen concentration
* CO₂ sensor / carbon dioxide concentration
* H₂ sensor / hydrogen concentration
* Optional placeholder for CH₄ / methane where industrial or cave/flood environments need it

These should appear in:

* sensor package templates
* agent capability displays
* environmental sensor outputs
* AI analysis where abnormal readings occur
* mission report if hazardous atmosphere is detected

Use case guidance:
Collapsed Building Search:

* CO₂ may indicate trapped human presence or poor ventilation
* O₂ may indicate oxygen-deficient voids
* H₂ can be included as a hazardous atmosphere / explosive risk placeholder

Cave Rescue:

* O₂ depletion and CO₂ buildup are important environmental risks
* H₂ can be included as a hazardous gas placeholder
* Humidity/moisture may affect sensor confidence

Flooded Structure:

* O₂ / CO₂ readings may indicate poor air pockets or trapped spaces
* H₂ can indicate explosive or battery-related risk placeholder
* Contamination / water condition remains separate

Industrial Inspection:

* O₂, CO₂, H₂, CH₄, temperature, pressure, and vibration are all relevant
* H₂ should trigger explosive atmosphere concern if above threshold
* Low O₂ should trigger confined-space warning
* High CO₂ should trigger ventilation / human safety warning

6. Suggested environmental reading shape

```ts
export interface EnvironmentalReading {
  sensorType:
    | 'temperature'
    | 'humidity'
    | 'pressure'
    | 'oxygen'
    | 'carbon_dioxide'
    | 'hydrogen'
    | 'methane'
    | 'air_quality'
    | 'water_depth'
    | 'contamination';
  displayName: string;
  value: number;
  unit: string;
  status: 'normal' | 'watch' | 'warning' | 'critical';
  locationLabel: string;
  confidence: number;
  detectedAt: number;
}
```

7. Visual behaviour for generated terrain
   Please update the Tactical Map visual behaviour:

* Unknown sectors should be invisible, very faint, or labelled “Unknown”.
* Detected sectors should appear as a faint outline.
* Partially mapped sectors should appear with low opacity.
* Mapped sectors should appear with stronger fill and border.
* High-confidence sectors should show a stronger border or scan pattern.
* Hazardous/blocked sectors should show warning styling.
* Add a small per-sector confidence label where space allows.
* Add subtle scan pulses from active agents.
* Add a “terrain reconstruction” status line, for example:
  “Terrain generated from simulated LiDAR/depth/sonar returns”
  “Confidence increases with repeated or multi-agent scans”

8. Backend simulation changes
   If necessary, extend the Django mission state response additively to include terrain reconstruction state.

Do not break the existing API.

Suggested additive field:

```json
"terrain_reconstruction": {
  "overall_confidence": 72,
  "overall_detail_level": 3,
  "total_scan_count": 14,
  "sectors": [
    {
      "sector_id": "void-space-1",
      "status": "mapped",
      "confidence": 78,
      "detail_level": 3,
      "mapped_by_agent_ids": ["scout-drone-a", "thermal-audio-drone"],
      "scan_count": 4
    }
  ]
}
```

9. Frontend integration
   Update the Astro/TypeScript mission state types to support terrain reconstruction.

The TacticalMap should prefer live `terrain_reconstruction` data when available.
If not available, it should fall back to route timing and local map definitions.

10. Important constraints

* Do not add WebSockets yet.
* Do not add Celery yet.
* Do not add real LiDAR yet.
* Do not add Three.js/Cesium yet.
* Keep the SVG tactical map lightweight.
* Keep HTTP polling.
* Preserve existing live simulation routes.
* Do not remove local fallback data.
* Use clear TODO comments for future true point-cloud / 3D terrain rendering.

After implementation, report:

* Django files changed
* Astro/TypeScript files changed
* new fields added to mission state
* how terrain reveal works
* how scan count/detail/confidence are calculated
* which sensors were added to each use case
* any remaining limitations
