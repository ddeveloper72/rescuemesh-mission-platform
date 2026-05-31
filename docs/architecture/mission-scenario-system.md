# Mission Scenario System Architecture

## Problem Statement

The current `simulation.py` is **3,925 lines** and growing exponentially:
- ❌ Hardcoded exploration timing per use case
- ❌ Hardcoded agent movement paths (complex if/else chains)  
- ❌ Hardcoded failure scenarios
- ❌ No user interaction support
- ❌ Not leveraging Digital Twin data effectively
- ❌ Will become unmaintainable with 5+ use cases

## Solution: Data-Driven Mission Scenarios

### New Database Models

```
MissionScenario
├── AgentRoute (many)
│   └── RouteWaypoint (many)
└── ScenarioEvent (many)

UserMissionAction (per mission instance)
```

### Key Concepts

#### 1. **Mission Scenarios** (Reusable Templates)
- Defines agent routes, timeline events, failures
- Links to Digital Twin terrain
- Can be replayed, modified, tested
- Stored in JSON files → imported to database

#### 2. **Agent Routes** (Pre-planned Paths)
- Sequence of waypoints through Digital Twin sectors
- Deploy timing, speed, sensors, battery drain
- Behavior: patrol, static, return-to-base, one-way

#### 3. **Scenario Events** (Timeline)
- Sector exploration milestones
- Detections (thermal, audio, signal)
- Failures (battery, sensor, comms)
- Escalations requiring user action

#### 4. **User Actions** (Live Overrides)
- Deploy new agent
- Redirect agent to new target
- Recall agent to base
- Acknowledge events
- Manual control

### Architecture Benefits

✅ **Scalability**: Add new use cases without code changes  
✅ **Reusability**: Same scenario can run multiple missions  
✅ **Testability**: Scenarios are data, easy to modify/test  
✅ **User Interaction**: Built-in support for user commands  
✅ **Maintainability**: Simulation engine reads data, not hardcoded  
✅ **Digital Twin Integration**: Routes reference sectors directly  

## Migration Plan

### Phase 1: Database Schema ✅ DONE
- [x] Create `models_scenario.py` with new models
- [x] Create `seed_mission_scenarios.py` management command
- [x] Create sample scenario JSON for collapsed building
- [ ] Run migrations to create database tables

### Phase 2: Simulation Engine Rewrite
- [ ] Create `scenario_engine.py` service
  - Load scenario from database
  - Calculate agent positions based on routes + elapsed time
  - Trigger events at specified times
  - Apply user actions/overrides
- [ ] Update `simulation.py` to use scenario engine
- [ ] Test with collapsed building scenario

### Phase 3: User Interaction API
- [ ] Add API endpoints:
  - `POST /api/missions/{id}/actions/deploy-agent/`
  - `POST /api/missions/{id}/actions/redirect-agent/`
  - `POST /api/missions/{id}/actions/recall-agent/`
  - `GET /api/missions/{id}/actions/` (list user actions)
- [ ] Frontend components:
  - Agent deployment modal (click map to place)
  - Agent redirect control (select agent, click new target)
  - Agent recall button
  - Action confirmation dialogs

### Phase 4: Frontend User Controls
- [ ] Add tactical map controls:
  - Right-click menu on map → "Deploy Agent Here"
  - Right-click agent → "Redirect to...", "Recall", "Manual Control"
  - Action confirmation modals
- [ ] Add mission control panel:
  - Active agents list with controls
  - Available agents for deployment
  - Action history
  - Mission override controls

### Phase 5: Migrate Other Use Cases
- [ ] Create scenario JSON for cave rescue
- [ ] Create scenario JSON for flooded structure
- [ ] Create scenario JSON for industrial inspection
- [ ] Create scenario JSON for archaeological exploration
- [ ] Test all scenarios
- [ ] Remove old hardcoded logic from `simulation.py`

## Sample Scenario Structure

```json
{
  "scenario_id": "collapsed-building-alpha-01",
  "name": "Collapsed Building Alpha - Standard Search",
  "use_case": "collapsed-building-search",
  "digital_twin_site_slug": "urban-collapse-alpha-demo",
  "digital_twin_terrain_slug": "alpha-building-structure",
  "allow_agent_deployment": true,
  "allow_agent_redirect": true,
  
  "agent_routes": [
    {
      "agent_id": "drone-a",
      "agent_name": "Scout Drone A",
      "deploy_at_seconds": 30,
      "sensors": ["LiDAR", "Thermal"],
      "waypoints": [
        {"sequence_order": 0, "sector_id": "ground-entry"},
        {"sequence_order": 1, "sector_id": "ground-lobby", "pause_duration_seconds": 15},
        {"sequence_order": 2, "sector_id": "floor-1-corridor"}
      ]
    }
  ],
  
  "events": [
    {
      "trigger_at_seconds": 240,
      "event_type": "detection-audio",
      "sector_id": "basement-corridor",
      "title": "Voice-like Audio Detected",
      "requires_user_action": true
    }
  ]
}
```

## Simulation Engine Changes

### Current (Hardcoded):
```python
# Complex if/else for every agent
if elapsed_seconds < 90:
    drone_a_loc = 'Ground Floor Lobby'
    x = 0 + (8 * t)
elif elapsed_seconds < 180:
    drone_a_loc = 'East Corridor'
    x = 8 + (10 * t)
# ... 50+ more lines per agent
```

### New (Data-Driven):
```python
def calculate_agent_position(route, waypoints, elapsed_seconds, user_actions):
    """Calculate agent position based on route and elapsed time."""
    
    # Get current waypoint based on time
    current_waypoint = get_current_waypoint(route, waypoints, elapsed_seconds)
    
    # Check for user overrides
    redirect = get_user_redirect(route.agent_id, user_actions)
    if redirect:
        return redirect.target_position
    
    # Calculate position between waypoints
    return interpolate_position(current_waypoint, next_waypoint, progress)
```

## User Interaction Flow

### Example: Deploy New Agent

1. **User clicks map location** → Modal opens
2. **User selects agent type** (mapper, detector, relay)
3. **User confirms deployment** → POST `/api/missions/{id}/actions/deploy-agent/`
4. **Backend creates `UserMissionAction`** with status='pending'
5. **Simulation engine reads actions** on next poll
6. **New agent appears** at target location with calculated route
7. **Action status** updates to 'executed' → 'completed'

### Example: Redirect Agent

1. **User right-clicks active agent** → Context menu
2. **User selects "Redirect to..."** → Map in targeting mode
3. **User clicks new target** → Confirmation modal
4. **User confirms** → POST `/api/missions/{id}/actions/redirect-agent/`
5. **Simulation engine** recalculates route from current position to new target
6. **Agent path updates** on tactical map
7. **Route Profile updates** with new trajectory

## Benefits Recap

### For Development
- Add new scenarios without touching simulation code
- Test scenarios independently
- Version control mission scripts
- Share scenarios between developers

### For Users
- Deploy agents dynamically during mission
- Redirect agents based on detections
- Recall agents before battery depletion
- More realistic tactical decision-making

### For System
- Simulation logic shrinks from 3,925 lines to ~500 lines
- Data-driven, not code-driven
- Leverages Digital Twin infrastructure
- Supports future AI mission planning

## Next Steps

1. **Run migrations** to create database tables
2. **Import sample scenario**: `python manage.py seed_mission_scenarios --file collapsed_building_scenario_alpha.json`
3. **Build scenario engine** service
4. **Update simulation.py** to use scenario engine
5. **Test** with collapsed building mission
6. **Add user action API** endpoints
7. **Build frontend controls** for user interaction

## Files Created

- `backend/apps/missions/models_scenario.py` - Database models
- `backend/apps/missions/management/commands/seed_mission_scenarios.py` - Import command
- `data/scenarios/collapsed_building_scenario_alpha.json` - Sample scenario
- `docs/architecture/mission-scenario-system.md` - This document

---

**Status**: Phase 1 complete (database schema designed)  
**Next**: Create and run migrations, then build scenario engine
