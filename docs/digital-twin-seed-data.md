# Digital Twin Seed Data

## Overview

RescueMesh Mission Platform supports pre-populating the database with simplified digital twin map data derived from public/open cave survey and archaeological/heritage datasets. This feature enables realistic mission simulations without requiring access to physical hardware or conducting actual surveys.

**Purpose:** Provide demo and training scenarios based on real-world survey patterns while respecting sensitivity and licensing requirements.

---

## Key Principles

1. **Simulation-First:** Digital twins are for demonstration and training, not for exposing sensitive locations
2. **Simplified Data:** Store sectors, paths, and waypoints, not large point clouds or raw sensor data
3. **Attribution-Aware:** Preserve source licenses and attribution for all imported data
4. **Sensitivity-Conscious:** Support multiple sensitivity levels to protect sensitive locations
5. **Lightweight:** Keep database footprint small and Docker-friendly

---

## Data Model

### Core Models

#### DigitalTwinSite
Represents a real-world environment imported for simulation purposes.

**Key Fields:**
- `slug`: URL-friendly identifier
- `name`: Human-readable site name
- `site_type`: `cave`, `archaeology`, `industrial`, `synthetic`
- `country`: Geographic location (if publicly shareable)
- `description`: Site overview
- `source_name`: Name of source dataset or survey project
- `source_url`: URL to source dataset
- `source_license`: License identifier (e.g., CC-BY-SA-4.0, MIT, ODbL)
- `attribution`: Required attribution text
- `sensitivity_level`:
  - `public_demo`: Full coordinates (publicly available data)
  - `reduced_precision`: Approximate location only
  - `restricted`: No location data
  - `synthetic_only`: Not a real location
- `notes`: Additional processing notes or restrictions

#### TerrainMap
Spatial structure of a digital twin site using local 3D grid coordinates.

**Key Fields:**
- `digital_twin_site`: Parent site
- `slug`: Map identifier
- `name`: Map name
- `coordinate_system`: Usually `local_mission_3d_grid` for GPS-denied environments
- `origin_label`: Description of coordinate origin (e.g., "Cave entrance")
- `units`: Typically "meters"
- `source_format`: `manual`, `therion`, `survex`, `point_cloud`, `geojson`, `synthetic`

#### TerrainSector
Discrete region within a terrain map (chamber, passage, junction, etc.).

**Key Fields:**
- `sector_id`: Identifier (e.g., "C1", "passage-alpha")
- `label`: Human-readable name
- `sector_type`: `chamber`, `passage`, `junction`, `entrance`, `shaft`, `sump`, `room`, `corridor`, `void`, `hazard`
- `x_m`, `y_m`, `z_m`: 3D position in meters
- `width_m`, `height_m`, `depth_m`: Approximate dimensions
- `elevation_m`: Elevation relative to reference
- `confidence`: Data confidence (0.0-1.0)
- `source_ref`: Reference to source survey data
- `metadata`: JSON with additional features

#### TerrainPath
Connection between two sectors with distance, bearing, and risk assessment.

**Key Fields:**
- `from_sector`, `to_sector`: Connected sectors
- `distance_m`: Path distance
- `bearing_deg`: Compass bearing (0-360)
- `vertical_change_m`: Elevation change (positive=up, negative=down)
- `path_type`: `passage`, `climb`, `descent`, `crawl`, `squeeze`, `swim`, `dive`, `traverse`, `ladder`, `open`
- `traversal_risk`: `low`, `moderate`, `high`, `extreme`, `impassable`
- `confidence`: Data confidence
- `capabilities_required`: JSON array (e.g., ["waterproof", "vertical_mobility"])
- `metadata`: JSON with additional path characteristics

#### Waypoint
Navigation waypoint within a terrain map.

**Key Fields:**
- `waypoint_id`: Identifier
- `label`: Description
- `x_m`, `y_m`, `z_m`: 3D position
- `sequence`: Order in route
- `route_group`: Route identifier
- `metadata`: JSON with additional waypoint info

#### MapArtifact
Reference to external map artifacts (survey files, point clouds, images).

**Key Fields:**
- `digital_twin_site`: Parent site
- `artifact_type`: `survey_file`, `point_cloud`, `mesh`, `image`, `reference_link`, `derived_json`
- `file_format`: Format identifier (e.g., "survex", "therion", "las", "ply", "geojson")
- `local_path`: Path to file in `data/` directory
- `external_url`: URL to external resource
- `source_license`: License identifier
- `attribution`: Required attribution

---

## Source Dataset Candidates

### 1. Migovec Resurvey Project
**URL:** https://github.com/tr1813/migresurvey  
**License:** Public survey data (check repository for specific license)  
**Data Type:** Cave survey data (Survex/Therion formats)  
**Coverage:** Tolminski Migovec cave system, Slovenia  
**Collected By:** Imperial College Caving Club (ICCC) and Jamarska Sekcija Planinskega Drustva Tolmin (JSPDT), 1974-2019

**Suitable For:**
- Route graph generation
- Sector/passage structure
- Path connections
- Waypoint extraction
- Vertical terrain modeling

**Data Formats:**
- Therion (`.th`, `.th2`, `.thconfig`)
- Survex (`.svx`)
- 3D models (`.3d`, `.lox`)
- PDF/SVG maps

### 2. CAVERS Dataset
**URL:** https://github.com/spaceuma/cavers/  
**DOI:** https://doi.org/10.5281/zenodo.19367714  
**License:** MIT License  
**Data Type:** Cave SLAM dataset with multimodal sensors  
**Coverage:** Cueva de la Victoria, Spain

**Suitable For:**
- Sensor realism (RGB-D, LiDAR, thermal, IMU)
- Ground truth pose data
- Waypoint/trajectory examples
- SLAM validation scenarios

**Data Formats:**
- ROS2 rosbags (mcap format)
- RGB-D imagery
- 3D LiDAR scans
- Near-IR thermal camera data
- IMU and ground truth pose

### 3. Open Heritage 3D
**URL:** https://openheritage3d.org/  
**Registry:** https://www.re3data.org/repository/r3d100013317  
**License:** Varies by dataset (check per-dataset licensing)  
**Data Type:** Cultural heritage 3D documentation  
**Coverage:** Global archaeological and heritage sites

**Suitable For:**
- Archaeological site structure
- Heritage preservation scenarios
- Non-destructive survey simulations
- Cultural sensitivity training

**Data Formats:**
- LiDAR point clouds
- Photogrammetry models
- Laser scan data
- 3D meshes

**Founding Members:**
- CyArk
- Historic Environment Scotland
- University of South Florida Libraries

---

## Why Raw Point Clouds Are Not Stored in SQL

**Database Performance:**
- Point clouds contain millions to billions of points
- SQL databases are optimized for structured relational data, not massive geometry
- Query performance degrades with large BLOB storage

**Storage Efficiency:**
- Point clouds are multi-gigabyte to multi-terabyte in size
- Database backups become unwieldy
- Replication and migration become slow and expensive

**Better Alternatives:**
- **File System:** Store `.las`, `.laz`, `.ply`, `.e57`, `.pcd` files in `data/` or object storage
- **Specialized Formats:** Use streamable formats like 3D Tiles or Potree for web viewing
- **Database References:** Store metadata and file paths/URLs in SQL, not raw geometry

**What We Store Instead:**
- Simplified sectors (bounding boxes with metadata)
- Path graphs (distance, bearing, risk)
- Waypoints (x, y, z coordinates)
- References to external point cloud files

---

## How Simplified Sectors/Paths/Waypoints Are Generated

### From Cave Survey Data (Therion/Survex)

1. **Parse Survey Centreline:**
   - Extract survey stations (x, y, z coordinates)
   - Calculate distances and bearings between stations
   - Identify passage types from survey metadata

2. **Identify Sectors:**
   - Group stations into chambers, passages, junctions based on spatial clustering
   - Calculate bounding box dimensions
   - Extract elevation changes

3. **Generate Paths:**
   - Connect sectors based on survey shot data
   - Calculate distances from station-to-station shots
   - Infer traversal risk from passage dimensions and metadata

4. **Create Waypoints:**
   - Use key survey stations as waypoints
   - Sequence waypoints along logical routes
   - Preserve metadata about station features

### From SLAM/Point Cloud Data

1. **Trajectory Analysis:**
   - Extract robot/drone pose history
   - Simplify trajectory into waypoints at key positions
   - Calculate distances and bearings between waypoints

2. **Spatial Segmentation:**
   - Cluster point cloud into spatial regions
   - Define sector bounding boxes from region extents
   - Calculate connectivity between regions

3. **Obstacle Detection:**
   - Identify narrow passages, vertical changes, hazards
   - Map to traversal risk levels
   - Define capability requirements

### Manual/Synthetic Generation

1. **Reference Maps:**
   - Study published maps, diagrams, or descriptions
   - Extract sector locations and dimensions
   - Estimate distances and bearings

2. **Demonstration Scenarios:**
   - Create realistic synthetic structures
   - Design mission-appropriate challenges
   - Ensure compatibility with agent capabilities

---

## Running the Seed Command

### Basic Usage

```bash
# Seed all JSON files in data/processed/
python manage.py seed_digital_twins

# Clear existing data before seeding
python manage.py seed_digital_twins --clear

# Import a specific file
python manage.py seed_digital_twins --file migovec_sample.json
```

### Docker Usage

```bash
# After starting Docker containers
docker exec -it rescuemesh-backend python manage.py seed_digital_twins
```

### Expected Output

```
Processing migovec_sample.json...
  Created site: Migovec Primadona (Simplified Demo Extract)
  Created terrain map: Primadona Entrance Zone (Demo)
  Created/updated 7 sectors
  Created/updated 6 paths
  Created/updated 6 waypoints
Successfully imported migovec_sample.json

Processing archaeology_sample.json...
  Created site: Archaeological Underground Chamber (Heritage Demo)
  Created terrain map: Underground Chamber Complex (Heritage Demo)
  Created/updated 8 sectors
  Created/updated 7 paths
  Created/updated 7 waypoints
Successfully imported archaeology_sample.json

Completed seeding 2 digital twin(s)
```

---

## Adding New Digital Twin Sources

### Step 1: Obtain Source Data

1. **Verify License:** Ensure data is openly licensed or permission granted
2. **Check Sensitivity:** Confirm no sensitive location data exposure
3. **Download Data:** Obtain survey files, point clouds, or documentation

### Step 2: Process Data

1. **Extract Structure:**
   - Parse survey files or point clouds
   - Identify sectors, paths, waypoints
   - Calculate distances, bearings, elevations

2. **Simplify Geometry:**
   - Reduce to essential structure
   - Create bounding boxes for sectors
   - Generate path graph

3. **Preserve Attribution:**
   - Record source name, URL, license
   - Write required attribution text
   - Document any processing steps

### Step 3: Create JSON File

Create a JSON file in `data/processed/` following this structure:

```json
{
  "site": {
    "slug": "unique-site-slug",
    "name": "Site Name",
    "site_type": "cave|archaeology|industrial|synthetic",
    "country": "Country Name",
    "description": "Description...",
    "source_name": "Source Dataset Name",
    "source_url": "https://source.url",
    "source_license": "License ID",
    "attribution": "Required attribution text",
    "sensitivity_level": "public_demo|reduced_precision|restricted|synthetic_only",
    "notes": "Processing notes"
  },
  "terrain_map": {
    "slug": "map-slug",
    "name": "Map Name",
    "coordinate_system": "local_mission_3d_grid",
    "origin_label": "Origin description",
    "units": "meters",
    "source_format": "manual|therion|survex|point_cloud|geojson|synthetic"
  },
  "sectors": [
    {
      "sector_id": "sector-1",
      "label": "Sector Name",
      "sector_type": "chamber|passage|junction|entrance|shaft|...",
      "x_m": 0.0,
      "y_m": 0.0,
      "z_m": 0.0,
      "width_m": 10.0,
      "height_m": 5.0,
      "depth_m": 8.0,
      "elevation_m": 0.0,
      "confidence": 0.9,
      "source_ref": "reference",
      "metadata": {}
    }
  ],
  "paths": [
    {
      "from_sector": "sector-1",
      "to_sector": "sector-2",
      "distance_m": 15.0,
      "bearing_deg": 90.0,
      "vertical_change_m": -5.0,
      "path_type": "passage|climb|descent|...",
      "traversal_risk": "low|moderate|high|extreme|impassable",
      "confidence": 0.9,
      "capabilities_required": ["capability1", "capability2"],
      "metadata": {}
    }
  ],
  "waypoints": [
    {
      "waypoint_id": "wp-1",
      "label": "Waypoint Name",
      "x_m": 0.0,
      "y_m": 0.0,
      "z_m": 0.0,
      "sequence": 1,
      "route_group": "route-name",
      "metadata": {}
    }
  ]
}
```

### Step 4: Import

```bash
python manage.py seed_digital_twins --file your_new_file.json
```

### Step 5: Verify

1. Check Django admin: `/admin/mapping/`
2. Query API endpoints
3. Test mission simulation with new terrain

---

## Licensing and Sensitivity Rules

### License Requirements

**Must Store:**
- Source dataset name
- Source URL (if available)
- License identifier (e.g., "CC-BY-SA-4.0", "MIT", "ODbL")
- Full attribution text as required by license

**Must Respect:**
- Non-commercial clauses (if present)
- Share-alike requirements
- Attribution display requirements
- Modification restrictions

### Sensitivity Levels

#### `public_demo`
- **Use:** Publicly available datasets with full coordinates
- **Example:** Published cave surveys with public entrance locations
- **Restrictions:** None beyond license requirements

#### `reduced_precision`
- **Use:** Real datasets with approximate locations only
- **Example:** "Cave system in Slovenia" without specific GPS coordinates
- **Restrictions:** Do not expose precise entrance coordinates

#### `restricted`
- **Use:** Real datasets with no location data
- **Example:** Survey structure only, labeled "Location withheld"
- **Restrictions:** Do not include country, region, or identifiable features

#### `synthetic_only`
- **Use:** Demonstration data not based on real sites
- **Example:** "Simulated cave system for training purposes"
- **Restrictions:** Clearly mark as synthetic in all documentation

### Prohibited Actions

- ❌ Exposing sensitive cave entrance coordinates
- ❌ Publishing location data for endangered species habitats
- ❌ Sharing heritage site locations vulnerable to looting
- ❌ Violating indigenous cultural restrictions
- ❌ Ignoring license attribution requirements
- ❌ Using restricted or copyrighted data without permission

---

## Future Format Support

### Planned Support

#### Cave Survey Formats
- **Therion** (`.th`, `.th2`, `.thconfig`): Full parser for centreline and scrap data
- **Survex** (`.svx`, `.3d`): Import survey stations and shots
- **Compass** (`.dat`, `.plt`): Cave survey standard format

#### Point Cloud Formats
- **LAS/LAZ**: ASPRS LiDAR format (compressed and uncompressed)
- **E57**: ASTM 3D imaging data exchange
- **PLY**: Polygon file format (point clouds and meshes)
- **PCD**: Point Cloud Data format (ROS/PCL)
- **XYZ/ASCII**: Simple text-based point cloud format

#### Geospatial Formats
- **GeoJSON**: Geographic features with coordinate reference systems
- **KML/KMZ**: Google Earth format for cave entrance locations
- **Shapefiles**: GIS vector data for site boundaries

#### 3D Model Formats
- **3D Tiles**: Streamable 3D geospatial format (for web viewers)
- **COLLADA** (`.dae`): 3D asset exchange
- **OBJ/MTL**: Simple 3D mesh format
- **GLTF/GLB**: Modern 3D transmission format

#### Heritage Formats
- **Open Heritage 3D API**: Direct integration with OHA platform
- **Potree Format**: Web-optimized point cloud streaming
- **SketchFab API**: Access to published heritage 3D models

### Integration Roadmap

**Phase 1 (Current):** Manual JSON import with simplified structure  
**Phase 2:** Therion/Survex parser for cave survey data  
**Phase 3:** Point cloud processing with spatial clustering  
**Phase 4:** GeoJSON and geospatial format support  
**Phase 5:** 3D Tiles streaming for web visualization  
**Phase 6:** Open Heritage 3D API integration

---

## API Endpoints

### Read-Only Endpoints

```
GET /api/v1/mapping/digital-twin-sites/
GET /api/v1/mapping/digital-twin-sites/{slug}/
GET /api/v1/mapping/terrain-maps/
GET /api/v1/mapping/terrain-maps/{slug}/
GET /api/v1/mapping/terrain-sectors/
GET /api/v1/mapping/terrain-sectors/{id}/
GET /api/v1/mapping/terrain-paths/
GET /api/v1/mapping/terrain-paths/{id}/
GET /api/v1/mapping/waypoints/
GET /api/v1/mapping/waypoints/{id}/
GET /api/v1/mapping/map-artifacts/
GET /api/v1/mapping/map-artifacts/{id}/
```

### Query Parameters

```
# Filter by site
GET /api/v1/mapping/terrain-maps/?digital_twin_site={site_id}

# Filter by map
GET /api/v1/mapping/terrain-sectors/?terrain_map={map_id}

# Filter by sector type
GET /api/v1/mapping/terrain-sectors/?sector_type=chamber

# Filter by path risk
GET /api/v1/mapping/terrain-paths/?traversal_risk=high

# Filter by route group
GET /api/v1/mapping/waypoints/?route_group=primary-route
```

---

## References

- **Migovec Resurvey Project:** https://github.com/tr1813/migresurvey
- **CAVERS Dataset:** https://github.com/spaceuma/cavers/ | https://doi.org/10.5281/zenodo.19367714
- **Open Heritage 3D:** https://openheritage3d.org/
- **Therion Documentation:** https://therion.speleo.sk/
- **Survex Documentation:** https://survex.com/
- **3D Tiles Specification:** https://cesium.com/why-cesium/3d-tiles/
- **Potree Point Cloud Viewer:** https://github.com/potree/potree
- **LAS Specification (ASPRS):** https://www.asprs.org/divisions-committees/lidar-division/laser-las-file-format-exchange-activities
- **E57 Format (ASTM):** https://www.libe57.org/

---

## Troubleshooting

### "Data directory not found"
**Cause:** `data/processed/` directory does not exist  
**Solution:** `mkdir -p data/processed` and add JSON files

### "No JSON files found"
**Cause:** No `.json` files in `data/processed/`  
**Solution:** Create or copy sample JSON files to that directory

### "Error importing: ... not found"
**Cause:** Missing required fields in JSON  
**Solution:** Check JSON structure matches expected schema

### "Skipping path: sector not found"
**Cause:** Path references non-existent sector  
**Solution:** Ensure `from_sector` and `to_sector` match existing `sector_id` values

### Migration conflicts
**Cause:** Models changed without migrations  
**Solution:** `python manage.py makemigrations mapping` then `python manage.py migrate`

---

## Next Steps

1. **Import Sample Data:**
   ```bash
   python manage.py seed_digital_twins
   ```

2. **Verify in Admin:**
   - Visit `/admin/mapping/digitaltwinsite/`
   - Check imported sites, maps, sectors, paths, waypoints

3. **Test API:**
   ```bash
   curl http://localhost:8000/api/v1/mapping/digital-twin-sites/
   ```

4. **Create Missions:**
   - Use terrain maps as basis for mission scenarios
   - Configure agents to navigate waypoints
   - Test path traversal logic

5. **Add New Sources:**
   - Follow "Adding New Digital Twin Sources" section
   - Process real survey data
   - Maintain attribution and licensing
