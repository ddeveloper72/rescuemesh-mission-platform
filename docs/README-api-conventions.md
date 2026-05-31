# RescueMesh API Conventions & Data Standards

**Version:** 1.0  
**Last Updated:** June 1, 2026  
**Status:** Living Document

---

## Overview

RescueMesh follows robotics and GIS industry standards for telemetry, spatial data, and mission state representation. This document defines coordinate systems, units, data formats, and conventions used throughout the platform.

**Design Philosophy:**
- **Robotics-first:** Compatible with ROS 2, MAVLink, and drone telemetry standards
- **GIS-compatible:** Integrates with PostGIS, GeoJSON, and spatial databases
- **Human-readable:** JSON payloads are clear and self-documenting
- **Future-proof:** Designed for real hardware integration and MCAP log replay

---

## Coordinate Systems

### Local Mission Frame (Primary)

RescueMesh uses a **local 3D Cartesian coordinate system** anchored to the mission origin point.

```
Origin: Mission entry point (e.g., cave entrance, building entrance)
- X axis: East (meters)
- Y axis: North (meters)
- Z axis: Up (meters)
  - Positive Z = elevation (above origin)
  - Negative Z = depth (below origin)
  - Z = 0 at origin reference plane
```

**Why Local Frame?**
- GPS-denied environments (caves, buildings, tunnels) have no GPS reference
- Eliminates coordinate transformation overhead during real-time mission
- Matches SLAM (Simultaneous Localization and Mapping) output from drones
- Compatible with ROS `odom` and `map` frames

**Example:**
```json
{
  "position": {
    "x": 45.6,    // 45.6 meters east of origin
    "y": -4.1,    // 4.1 meters south of origin
    "z": -18.0    // 18 meters below origin (depth)
  }
}
```

### Geographic Coordinates (Future)

When real-world GPS data is available:
- **Standard:** WGS84 (EPSG:4326)
- **Format:** GeoJSON Point geometry
- **Coordinate order:** `[longitude, latitude, altitude]`

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [13.7167, 46.3333, 1820.5]  // lon, lat, alt (WGS84)
  },
  "properties": {
    "agent_id": "drone-a"
  }
}
```

---

## Units & Standards

### Distance
- **Unit:** Meters (m)
- **Standard:** SI units
- **Precision:** 0.1m typical, 0.01m for high-precision mapping

### Angles & Bearing
- **Unit:** Degrees (°)
- **Range:** 0° to 360°
- **Reference:** **True North** (not magnetic north)
- **Convention:** Clockwise from North
  - 0° = North
  - 90° = East
  - 180° = South
  - 270° = West
- **Cardinal conversion:**
  ```
  N   = 337.5° - 22.5°
  NE  = 22.5° - 67.5°
  E   = 67.5° - 112.5°
  SE  = 112.5° - 157.5°
  S   = 157.5° - 202.5°
  SW  = 202.5° - 247.5°
  W   = 247.5° - 292.5°
  NW  = 292.5° - 337.5°
  ```

### Time
- **Format:** ISO 8601 timestamps
- **Timezone:** UTC (no local time)
- **Example:** `2026-05-31T23:05:32.925Z`
- **Elapsed Time:** Seconds (float) from mission start

### Battery
- **Unit:** Percentage (%)
- **Range:** 0-100
- **Precision:** Integer (whole percent)

### Signal Strength
- **Unit:** Percentage (%)
- **Range:** 0-100 (0 = no signal, 100 = perfect)
- **Precision:** Integer
- **Note:** Simplified model; real systems may use dBm/RSSI

### Speed
- **Unit:** Meters per second (m/s)
- **Alternative:** Kilometers per hour (km/h) for user display

### Temperature
- **Unit:** Celsius (°C)
- **Alternative:** Kelvin (K) for scientific sensors

---

## Data Formats

### Agent Telemetry

Standard agent telemetry payload:

```json
{
  "agent_id": "drone-a",
  "timestamp": "2026-05-31T23:05:32.925Z",
  "position": {
    "x": 45.6,          // meters, local frame
    "y": -4.1,          // meters, local frame
    "z": -18.0,         // meters, local frame (negative = depth)
    "location": "Chamber Tight Squeeze"  // human-readable label
  },
  "navigation": {
    "bearing_deg": 84.9,              // degrees, true north reference
    "bearing_cardinal": "E",          // N/NE/E/SE/S/SW/W/NW
    "distance_from_origin_m": 47.3,   // straight-line 3D distance
    "elevation_m": null,              // positive altitude above origin
    "depth_m": 18.0                   // positive depth below origin
  },
  "status": {
    "state": "healthy",               // healthy|degraded|intermittent|failed|landed_relay|sacrificed
    "battery_percent": 39,            // 0-100
    "signal_strength": 85             // 0-100
  },
  "sensors": ["LiDAR", "RGB Camera", "IMU", "SLAM"]
}
```

### Terrain Sector

Spatial sector geometry with confidence:

```json
{
  "sector_id": "chamber-1",
  "label": "Chamber One",
  "centroid": {
    "x": 42.0,
    "y": -8.5,
    "z": -15.0
  },
  "bounds": {
    "width_m": 12.0,
    "height_m": 8.0,
    "depth_m": 3.5
  },
  "type": "accessible",  // accessible|blocked|void|water|hazard
  "confidence": 0.85,    // 0.0 (unexplored) to 1.0 (fully mapped)
  "explored_at": "2026-05-31T23:04:15Z"
}
```

### Sensor Detection

Detection event with position and confidence:

```json
{
  "detection_id": "audio-001",
  "detection_type": "voice_like_audio",
  "timestamp": "2026-05-31T23:06:42Z",
  "position": {
    "x": 52.3,
    "y": -12.8,
    "z": -22.0
  },
  "sector_id": "chamber-2",
  "confidence": 0.68,
  "severity": "high",
  "source_agent": "drone-a",
  "source_sensor": "microphone_array",
  "metadata": {
    "frequency_range_hz": [200, 3400],
    "duration_seconds": 2.3,
    "signal_to_noise_ratio": 4.2
  },
  "requires_human_review": true
}
```

---

## API Versioning

### Current Version: `/api/v1/`

All API endpoints are versioned to allow schema evolution:

```
/api/v1/missions/{mission_id}/state/
/api/v1/terrain/{site_slug}/{terrain_slug}/sectors/
/api/v1/scenarios/{scenario_id}/
```

### Version Policy

- **Backward compatible changes:** Same version (add optional fields)
- **Breaking changes:** New version (`/api/v2/`)
- **Deprecation period:** 6 months minimum before removal
- **Version header:** `Accept: application/vnd.rescuemesh.v1+json`

---

## Schema Validation (Future)

### JSON Schema

All API responses will include JSON Schema validation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentTelemetry",
  "type": "object",
  "required": ["agent_id", "timestamp", "position", "status"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "position": {
      "type": "object",
      "required": ["x", "y", "z"],
      "properties": {
        "x": {"type": "number", "description": "X coordinate in meters (local frame)"},
        "y": {"type": "number", "description": "Y coordinate in meters (local frame)"},
        "z": {"type": "number", "description": "Z coordinate in meters (positive=up)"}
      }
    }
  }
}
```

### OpenAPI/Swagger

API documentation available at `/api/docs/` (future):
- Interactive API explorer
- Request/response examples
- Schema definitions
- Authentication requirements

---

## Integration Standards

### ROS 2 Compatibility

RescueMesh data maps to ROS 2 message types:

| RescueMesh Field | ROS 2 Message Type | Notes |
|------------------|-------------------|-------|
| `position` | `geometry_msgs/Point` | Direct mapping |
| `pose` | `geometry_msgs/PoseStamped` | Add orientation |
| `telemetry` | `sensor_msgs/NavSatFix` | For GPS data |
| `map` | `nav_msgs/OccupancyGrid` | For 2D grid maps |
| `pointcloud` | `sensor_msgs/PointCloud2` | For LiDAR data |

**Future:** ROS 2 bridge node for real drone integration

### MCAP Log Format

Mission replay logs will use **MCAP** (Foxglove format):
- Standard for robotics data logging
- Time-indexed message streams
- Supports ROS, JSON, Protobuf
- Playback in Foxglove Studio

### PostGIS Integration

Terrain geometry stored as PostGIS spatial types:

```sql
CREATE TABLE terrain_sectors (
  id SERIAL PRIMARY KEY,
  sector_id VARCHAR(50) UNIQUE,
  geometry GEOMETRY(PolygonZ, 0),  -- Local 3D frame, SRID 0
  centroid GEOMETRY(PointZ, 0),
  confidence FLOAT,
  explored_at TIMESTAMPTZ
);

-- Spatial query: Find sectors within 10m of position
SELECT sector_id 
FROM terrain_sectors 
WHERE ST_DWithin(centroid, ST_MakePoint(45.6, -4.1, -18.0), 10.0);
```

### GeoJSON Export

Missions can export to GeoJSON for external GIS tools:

```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {
      "name": "urn:ogc:def:crs:EPSG::4326"
    }
  },
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [13.7167, 46.3333, 1820.5]
      },
      "properties": {
        "agent_id": "drone-a",
        "timestamp": "2026-05-31T23:05:32Z",
        "battery_percent": 39
      }
    }
  ]
}
```

---

## Field Naming Conventions

### Style Guide

- **JSON keys:** `snake_case` (Python/Django convention)
- **Units in field names:** Always suffix (`elevation_m`, `bearing_deg`, `duration_seconds`)
- **Booleans:** Prefix with `is_`, `has_`, `requires_`
- **Timestamps:** Suffix with `_at` (`created_at`, `explored_at`)
- **IDs:** Suffix with `_id` (`agent_id`, `sector_id`, `mission_id`)

### Examples

✅ **Good:**
```json
{
  "distance_from_origin_m": 47.3,
  "bearing_deg": 84.9,
  "battery_percent": 39,
  "is_running": true,
  "explored_at": "2026-05-31T23:04:15Z"
}
```

❌ **Avoid:**
```json
{
  "distance": 47.3,          // No unit!
  "bearingDegrees": 84.9,    // camelCase inconsistent
  "battery": 39,             // Ambiguous unit
  "running": true,           // Not clearly boolean
  "explored": "2026-05-31"   // No _at suffix
}
```

---

## State & Enumeration Values

### Agent States

```
planned            - Agent defined but not yet deployed
available          - Agent ready for deployment
deployed           - Agent actively deployed
active             - Agent executing mission
healthy            - Agent operating normally
degraded           - Agent performance reduced (battery, sensors, etc.)
intermittent       - Agent experiencing connection issues
failed             - Agent critically failed
failed_primary_power - Battery depleted
landed             - Agent has landed (intentional)
landed_relay       - Agent landed to serve as relay node
abandoned          - Agent left behind (not recoverable)
sacrificed         - Agent intentionally left for mission value
lost               - Agent location/status unknown
unknown            - Status cannot be determined
recoverable        - Failed agent that can be retrieved
recovered          - Agent successfully retrieved
nfc_readable       - Agent accessible via NFC/black-box
powered_download_available - Agent can provide data with external power
retired            - Agent removed from service
```

### Sector Types

```
accessible  - Navigable space
blocked     - Impassable obstacle
void        - Empty space (air, open chamber)
water       - Flooded or submerged
hazard      - Dangerous area (unstable, toxic, extreme temperature)
```

### Detection Severity

```
info       - Informational observation
low        - Minor interest
moderate   - Noteworthy finding
high       - Significant detection
critical   - Urgent attention required
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "SECTOR_NOT_FOUND",
    "message": "Sector 'chamber-99' does not exist in terrain 'primadona-entrance-zone'",
    "status": 404,
    "timestamp": "2026-05-31T23:10:15Z",
    "request_id": "req-7f3a9b2c",
    "details": {
      "sector_id": "chamber-99",
      "terrain_slug": "primadona-entrance-zone"
    }
  }
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation failed
- `500 Internal Server Error` - Server fault
- `503 Service Unavailable` - Temporary outage

---

## Future Standards Integration

### Planned Additions

1. **Protocol Buffers** - Binary serialization for performance-critical paths
2. **gRPC** - Streaming telemetry for real-time scenarios
3. **MQTT** - Lightweight pub/sub for IoT sensor integration
4. **MAVLink** - Direct drone protocol support
5. **UAVCAN** - CAN bus standard for drone components
6. **KML/KMZ** - Export for Google Earth visualization

---

## References

### Robotics Standards
- [ROS 2 Documentation](https://docs.ros.org/)
- [geometry_msgs](http://docs.ros.org/en/noetic/api/geometry_msgs/html/index-msg.html)
- [sensor_msgs](http://docs.ros.org/en/noetic/api/sensor_msgs/html/index-msg.html)
- [MCAP Format](https://mcap.dev/)
- [Foxglove Studio](https://docs.foxglove.dev/)

### GIS Standards
- [GeoJSON RFC 7946](https://tools.ietf.org/html/rfc7946)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [EPSG Geodetic Parameters](https://epsg.org/)
- [WGS84 (EPSG:4326)](https://epsg.io/4326)

### Web Standards
- [ISO 8601 Date/Time](https://en.wikipedia.org/wiki/ISO_8601)
- [JSON Schema](https://json-schema.org/)
- [OpenAPI Specification](https://swagger.io/specification/)

### Drone Protocols
- [MAVLink](https://mavlink.io/)
- [UAVCAN](https://uavcan.org/)
- [PX4 Autopilot](https://docs.px4.io/)
- [ArduPilot](https://ardupilot.org/)

---

## Changelog

### Version 1.0 (June 1, 2026)
- Initial documentation
- Defined local mission coordinate system
- Established unit conventions (meters, degrees true north, UTC)
- Documented agent telemetry format
- Added integration standards (ROS 2, PostGIS, GeoJSON)
- Defined API versioning policy

---

## Contributing

This is a living document. When adding new data types or changing conventions:

1. Update this document FIRST
2. Implement changes in code
3. Update API tests
4. Add entry to Changelog section
5. Increment version if breaking change

**Questions?** Open an issue or discussion in the RescueMesh repository.
