We now need to move the RescueMesh demo from static frontend data to dynamic simulated mission data from the Django API.

The current Astro dashboard uses static data for the four use cases. That was fine for the first UI prototype, but now we need Django to provide changing simulated data so the dashboard feels alive.

Please implement this carefully in phases. Do not remove the existing static fallback data yet.

Goal:
Create a Django-backed mission simulation state API that the Astro frontend can poll to update the dashboard.

Use cases:

1. collapsed-building-search
2. cave-rescue
3. flooded-structure
4. industrial-inspection

The first dynamic target should be Collapsed Building Search, but the design must support the other use cases.

Required behaviour:

* mission elapsed time changes
* support accelerated simulation time: 1x, 2x, 5x, 10x
* agent battery levels decrease over time
* agent signal strength changes over time
* agent states can change: healthy, degraded, intermittent, failed, landed_relay, abandoned, sacrificed, nfc_readable
* mission timeline events appear as the simulation progresses
* map coverage increases over time
* confidence values change over time
* expected failure events can be triggered
* AI analyst findings update as new evidence appears

Please add a mission state endpoint similar to:

GET /api/v1/missions/{mission_id}/state/

The response should include a complete current dashboard state:

```json
{
  "mission": {
    "mission_id": "mission-demo-001",
    "name": "Collapsed Building Search - Demo",
    "use_case": "collapsed-building-search",
    "status": "running"
  },
  "simulation_clock": {
    "started_at": "2026-05-29T12:00:00Z",
    "elapsed_seconds": 120,
    "speed_multiplier": 5,
    "is_running": true
  },
  "agents": [
    {
      "agent_id": "drone-a",
      "name": "Survey Drone",
      "role": "Primary mapper",
      "state": "healthy",
      "battery_percent": 84,
      "signal_strength": 72,
      "location_label": "Entrance void",
      "position": {
        "x": 24,
        "y": 12,
        "z": 3
      },
      "sensors": ["LiDAR", "Thermal", "RGB"],
      "nfc_recovery_available": false
    }
  ],
  "network": {
    "base_signal_strength": 88,
    "mesh_health": 76,
    "relay_chain": [
      "base-station",
      "relay-node-1",
      "drone-a"
    ],
    "packet_loss_percent": 8
  },
  "map": {
    "map_type": "void-map",
    "coverage_percent": 42,
    "confidence": 0.71,
    "total_points": 18400,
    "new_points_generated": 1250,
    "mapped_sectors": ["Entrance", "Corridor A", "Void 1"],
    "blocked_sectors": ["Collapsed Stairwell"],
    "accessible_areas": [
      {
        "label": "Void 1",
        "confidence": 0.82,
        "risk": "medium"
      }
    ]
  },
  "sensors": {
    "thermal_anomalies": [],
    "audio_events": [],
    "device_signals": [],
    "environmental_readings": []
  },
  "events": [],
  "ai_analysis": {
    "summary": "Mapping in progress. No confirmed survivor detection yet.",
    "priority_findings": [],
    "human_review_required": false,
    "confidence": 0.64
  }
}
```

Also add control endpoints if practical:

POST /api/v1/missions/{mission_id}/start/
POST /api/v1/missions/{mission_id}/pause/
POST /api/v1/missions/{mission_id}/reset/
POST /api/v1/missions/{mission_id}/speed/

The speed endpoint should accept:

```json
{
  "speed_multiplier": 5
}
```

For now, this can be a deterministic simulation based on elapsed time. It does not need Celery, Redis, WebSockets, or real background tasks yet.

Important design:

* The simulation state can be calculated on request using mission start time, speed multiplier, use case type, and scenario rules.
* Keep it simple and reliable.
* Avoid over-engineering.
* Do not connect to real drone systems.
* Do not require ROS yet.
* Do not require WebSockets yet.

Please create a simulation service module, for example:

missions/services/simulation.py

It should contain use case-specific simulation functions.

For collapsed-building-search, simulate:

* growing void map coverage
* increasing point count
* battery drain
* fluctuating signal strength
* dust occlusion event
* radio packet loss
* thermal anomaly after a certain elapsed time
* audio event after a later elapsed time
* drone landing as relay if signal is weak and battery drops
* AI analyst summary changing as evidence appears

For cave-rescue, flooded-structure, and industrial-inspection, add basic placeholder simulation logic using the same response shape, with TODO comments for future refinement.

Frontend changes:

* Update the Astro demo dashboard so it can fetch mission state from Django.
* Poll the state endpoint every 1–2 seconds while the demo is running.
* Use local static data as fallback if Django is unavailable.
* Add visible simulation controls:

  * Start
  * Pause
  * Reset
  * Speed selector: 1x, 2x, 5x, 10x
* Update the UI dynamically:

  * mission clock
  * battery bars
  * signal strength
  * agent states
  * map coverage
  * map confidence
  * timeline events
  * AI analyst summary

The Mission Map panel should remain a visual placeholder for now, but it should react to live state:

* show coverage percentage
* show point count
* show mapped sectors
* show blocked sectors
* show accessible areas
* show asset markers based on agent positions
* show warnings when confidence drops

Architecture requirements:

* Keep Astro + Tailwind + TypeScript.
* No inline CSS.
* Keep components reusable.
* Keep API logic inside src/lib/api.ts or similar.
* Add TypeScript interfaces for MissionState and related objects.
* Do not remove the existing static fallback data.
* Add clear TODO comments where future WebSockets, real LiDAR data, or ROS integration could be added.

After implementation, report:

* Django files created/changed
* Astro files created/changed
* API endpoints added
* how to start the Django backend
* how to start the Astro frontend
* how to test the dynamic mission state
* which parts are still simulated/static
* recommended next step
