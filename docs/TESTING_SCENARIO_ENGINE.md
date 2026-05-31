# Mission Scenario Engine - Testing Checklist

## Prerequisites
1. Start Django backend server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Start Astro frontend (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

## Test Criteria
For each use case, verify:
- ✅ **Progressive Sector Revelation**: Sectors only appear as agents explore them
- ✅ **Agent Positioning**: Agents appear at correct locations (not off-map)
- ✅ **Route Profile**: Side view panel shows agent depth/elevation correctly
- ✅ **Starting Position**: All agents start at designated origin point
- ✅ **No Premature Loading**: Map doesn't reveal full terrain before exploration

---

## Test 1: Collapsed Building Search

**URL**: http://localhost:4321/demo/live/collapsed-building-search/

### At Mission Start (0:00)
- [ ] Only "Ground Level Entry" sector visible
- [ ] Static Relay Node at origin (0, 0, 0)
- [ ] No drones visible yet (they deploy at 0:10, 0:30, 0:90)
- [ ] Route Profile shows only relay node at ground level

### At 1:00 minute
- [ ] Scout Drone A visible moving into East Corridor
- [ ] Scout position approximately (18, 3, 0)
- [ ] Only 2-3 sectors visible (entry + currently exploring)
- [ ] Route Profile shows scout at ground level

### At 3:00 minutes
- [ ] 3-4 agents active
- [ ] Agents spread across multiple floors
- [ ] Route Profile shows vertical distribution (-3.5m to +7m range)
- [ ] Only explored sectors visible (~25-30% map coverage)

### At 5:00 minutes
- [ ] "Voice-like Audio Detected" event triggered
- [ ] Thermal/Audio Drone in basement area (negative Z)
- [ ] Route Profile shows depth indicator for basement agent
- [ ] Map coverage ~30-40%

---

## Test 2: Cave Rescue

**URL**: http://localhost:4321/demo/live/cave-rescue/

### At Mission Start (0:00)
- [ ] Only "Entrance Chamber" sector visible
- [ ] Cave Entrance Relay at origin (0, 0, 0)
- [ ] No scouts visible yet
- [ ] Route Profile shows entrance at 0m

### At 1:00 minute
- [ ] Scout Drone in "Main Passage - Section 1"
- [ ] Scout position approximately (15, -8, -5)
- [ ] Only 2 sectors visible (entrance + passage)
- [ ] Route Profile shows descent to -5m

### At 3:00 minutes
- [ ] Junction Alpha reached at (28, -12, -12)
- [ ] Relay drone deploying to junction
- [ ] Route Profile shows progressive descent
- [ ] Micro Mapper may have lost signal

### At 5:00 minutes
- [ ] Scout in Chamber One at (35, -8, -15)
- [ ] Route Profile shows deepest point around -15m
- [ ] Junction relay visible at -12m
- [ ] Map coverage ~40-50%

---

## Test 3: Flooded Structure Inspection

**URL**: http://localhost:4321/demo/live/flooded-structure/

### At Mission Start (0:00)
- [ ] Only "Hull Breach Entry Point" visible
- [ ] Surface Command Station at (0, 0, 0)
- [ ] No ROVs visible yet
- [ ] Route Profile shows waterline at 0m

### At 1:00 minute
- [ ] Primary ROV exploring main corridor
- [ ] ROV position around (8, 0, 0) near waterline
- [ ] Only 2 sectors visible
- [ ] Route Profile shows ROV at/near waterline

### At 3:00 minutes
- [ ] Primary ROV descending to engine room
- [ ] ROV approaching depth -4.5m
- [ ] Micro ROV searching for air pockets
- [ ] Route Profile shows underwater depth progression

### At 5:00 minutes
- [ ] Air pocket detected in crew quarters (+2m elevation)
- [ ] Surface Buoy Relay floating at waterline
- [ ] Route Profile shows depth range from -4.5m to +2m
- [ ] Map coverage ~30-35%

---

## Test 4: Industrial Confined Space Inspection

**URL**: http://localhost:4321/demo/live/industrial-inspection/

### At Mission Start (0:00)
- [ ] Only "Vertical Access Shaft" visible
- [ ] Surface Command Post at (0, 0, 0)
- [ ] No inspection drones yet
- [ ] Route Profile shows ground level

### At 1:00 minute
- [ ] Inspection Drone descended to utility corridor
- [ ] Drone at depth -8m in "Main Utility Corridor"
- [ ] Only 2-3 sectors visible
- [ ] Route Profile shows -8m depth marker

### At 3:00 minutes
- [ ] Drone inspecting equipment room
- [ ] Gas sensor deployed to hazard zone
- [ ] Route Profile shows consistent -8m depth (level floor)
- [ ] Elevated temperature warning may appear

### At 5:00 minutes
- [ ] H2S detection alert in hazard zone
- [ ] Drone in pipe corridor or equipment room
- [ ] Route Profile stable at -8m to -8.5m
- [ ] Map coverage ~30-40%

---

## Test 5: Archaeological Exploration

**URL**: http://localhost:4321/demo/live/archaeological-exploration/

### At Mission Start (0:00)
- [ ] Only "Modern Access Tunnel" visible
- [ ] Surface Coordination at (0, 0, 0)
- [ ] No survey drones yet
- [ ] Route Profile shows entrance level

### At 1:00 minute
- [ ] Heritage Survey Drone in antechamber
- [ ] Drone position approximately (12, 2, -2)
- [ ] Only 2 sectors visible
- [ ] Route Profile shows slight descent to -2m

### At 3:00 minutes
- [ ] Survey Drone in Main Ceremonial Chamber
- [ ] Drone at (20, 4, -3.5)
- [ ] Photogrammetry scan in progress
- [ ] Route Profile shows -3.5m depth

### At 5:00 minutes
- [ ] Wall inscriptions detected
- [ ] Micro Scanner investigating artifacts
- [ ] Route Profile shows agents at -3m to -5m range
- [ ] Map coverage ~35-45%

---

## Common Issues to Check

### Coordinate System Issues
- [ ] No agents appearing at coordinates like (120, 240) or (350, 210)
- [ ] All agents should be within terrain bounds:
  - Collapsed Building: 0-22m x, -12 to +8m y
  - Cave: 0-60m x, -12 to +8m y
  - Vessel: 0-90m x, -10 to +10m y
  - Industrial: 0-50m x, -12 to +10m y
  - Archaeological: 0-55m x, -5 to +15m y

### Progressive Exploration
- [ ] Map should start nearly empty
- [ ] Sectors reveal as agents move through them
- [ ] Sector confidence increases over time (starts at 0%, builds to 85-100%)
- [ ] No "instant full map reveal" on mission start

### Route Profile Issues
- [ ] Side view should update as mission progresses
- [ ] Vertical position markers should match agent depth/elevation
- [ ] No agents appearing off the chart (e.g., at -1000m or +5000m)
- [ ] Chart scales appropriately to terrain vertical range

### Audio/Detection Modals
- [ ] Detection markers appear on tactical map
- [ ] Clicking detection marker opens modal with details
- [ ] Audio detections appear in Audio Detections panel
- [ ] Recommended actions are clickable and functional

---

## Success Criteria

✅ **All 5 use cases pass progressive exploration check**  
✅ **All agents start at correct origin coordinates**  
✅ **Route Profile displays agents at correct depths**  
✅ **No off-map agent rendering**  
✅ **Sectors reveal gradually, not all at once**  

---

## Test Execution Log

### Collapsed Building Search
- Tested at: _____________
- Status: ⬜ PASS / ⬜ FAIL
- Notes: _______________________________________________

### Cave Rescue
- Tested at: _____________
- Status: ⬜ PASS / ⬜ FAIL
- Notes: _______________________________________________

### Flooded Structure
- Tested at: _____________
- Status: ⬜ PASS / ⬜ FAIL
- Notes: _______________________________________________

### Industrial Inspection
- Tested at: _____________
- Status: ⬜ PASS / ⬜ FAIL
- Notes: _______________________________________________

### Archaeological Exploration
- Tested at: _____________
- Status: ⬜ PASS / ⬜ FAIL
- Notes: _______________________________________________

---

## Quick Verification Commands

To verify scenario data is loaded:
```bash
# Check scenarios in database
python manage.py shell -c "from apps.missions.models_scenario import MissionScenario; print(f'{MissionScenario.objects.count()} scenarios loaded')"

# Test specific scenario
python manage.py test_scenario_engine --scenario collapsed-building-alpha-01 --time 180
python manage.py test_scenario_engine --scenario cave-rescue-alpha-01 --time 180
python manage.py test_scenario_engine --scenario flooded-structure-alpha-01 --time 180
python manage.py test_scenario_engine --scenario industrial-inspection-alpha-01 --time 180
python manage.py test_scenario_engine --scenario archaeological-exploration-alpha-01 --time 180
```

To verify Digital Twin terrain data:
```bash
# Check collapsed building sectors
python manage.py shell -c "from apps.mapping.models import TerrainMap; tm = TerrainMap.objects.get(slug='collapsed-building-sample'); print(f'{tm.sectors.count()} sectors')"

# Check cave sectors
python manage.py shell -c "from apps.mapping.models import TerrainMap; tm = TerrainMap.objects.get(slug='primadona-entrance-zone'); print(f'{tm.sectors.count()} sectors')"
```
