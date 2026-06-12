"""
Mission simulation service.

This module provides deterministic, API-based simulation of mission scenarios.

**ARCHITECTURE DECISION: Simulation-First, No Real Hardware Yet**

NO WebSockets yet.
NO ROS yet.
NO real LiDAR yet.
NO Celery yet.
NO background processing.

**How It Works:**

Simulation state is calculated on-demand per API request based on:
1. **Mission start time** - when simulation.started_at was set
2. **Speed multiplier** - 1x, 2x, 5x, 10x real-time acceleration
3. **Use case type** - determines agent routes, events, terrain
4. **Elapsed mission time** - calculated from start time and speed multiplier
5. **Random seed** - ensures reproducibility (same time = same state)

**Data-Driven Scenarios:**

Missions are now driven by **MissionScenario** database records, not hardcoded logic.
Each scenario defines:
- Agent routes as sequences of waypoints with timing
- Timeline events (detections, failures, state changes)
- Terrain sectors with reveal and scan rules
- Sensor observations with trigger conditions

**To Modify Scenario Behavior:**
1. Edit JSON file in data/scenarios/
2. Run: `python manage.py seed_mission_scenarios --file {filename}.json --overwrite`
3. Restart Django server (to clear @lru_cache)
4. No code changes needed!

**Determinism:**

All simulation logic is deterministic and reproducible given the same parameters.
Same elapsed_seconds with same random_seed always produces same state.
This enables:
- Replay and analysis
- A/B testing of scenarios
- Debugging mission behavior
- Consistent demonstrations

**Performance:**

- Scenario data cached via @lru_cache (cleared on server restart)
- Typical state calculation: 20-50ms
- No database queries during state calculation (after initial load)
- Supports multiple concurrent clients polling different missions

**Future Evolution:**

When real-time sensor feeds and hardware integration are added:
- WebSocket endpoints for live telemetry streams
- ROS 2 bridge for real robot integration
- Celery tasks for background data processing
- Redis for real-time event buffering
- Hybrid mode: real sensor data + simulated agents
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import math
import random

from .navigation_utils import (
    calculate_distance_2d,
    calculate_distance_3d,
    calculate_bearing_degrees,
    bearing_to_cardinal,
    calculate_elevation_depth,
    calculate_vertical_profile_label,
    find_nearest_relay,
    calculate_contact_path_length,
    estimate_return_time,
    calculate_slope_and_incline,
    format_depth_elevation_label,
    calculate_compass_confidence,
)


def format_time(seconds: float) -> str:
    """
    Format elapsed seconds as HH:MM:SS (ISO 8601 time format) for timeline events.
    
    Used throughout the system to display mission elapsed time in a
    human-readable format for timelines, event logs, and operator displays.
    
    Args:
        seconds: Elapsed seconds (can be fractional, will be truncated to integer seconds)
        
    Returns:
        Formatted time string (e.g., "00:02:30", "01:15:42", "12:00:00")
        
    Examples:
        >>> format_time(90)
        "00:01:30"
        >>> format_time(3661)
        "01:01:01"
        >>> format_time(0)
        "00:00:00"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def calculate_terrain_reconstruction(
    sectors: List[Dict[str, Any]],
    agents: List[Dict[str, Any]],
    elapsed_seconds: float
) -> Dict[str, Any]:
    """
    Calculate progressive terrain reconstruction state for fog-of-war map reveal.
    
    This function implements the "fog of war" system where sectors of the map
    are progressively revealed as agents explore them. Multiple agent scans
    increase confidence and detail level.
    
    **Sector Status Progression:**
    1. `unknown`: Not yet detected (elapsed < reveal_at)
    2. `detected`: First scan completed (1 scan, 20% confidence, detail level 1)
    3. `partially_mapped`: Second scan completed (2 scans, 45% confidence, detail level 2)
    4. `mapped`: Well-mapped (3 scans, 70% confidence, detail level 3)
    5. `high_confidence`: Thoroughly mapped (4+ scans, 95% confidence, detail level 5)
    6. `hazardous`: Detected hazard in sector (overrides other statuses)
    7. `blocked`: Detected obstruction in sector (overrides other statuses)
    
    **Confidence Scoring:**
    - Confidence increases with each scan: 20% -> 45% -> 70% -> 80% -> 90% -> 95%
    - Hazard/blocked detection adds +5-10% confidence bonus
    - Multiple agents scanning same sector accelerates confidence growth
    
    **Detail Level:**
    - Level 1-5 scale indicating map quality
    - Higher detail = more accurate geometry, better texture, finer features
    - Used by frontend to adjust visual representation quality
    
    **Scan Rules:**
    Each sector has scan_rules defining when agents scan it:
    ```json
    "scan_rules": [
      {"time": 120, "agent_id": "drone-a", "scan_quality": 0.8},
      {"time": 180, "agent_id": "drone-b", "scan_quality": 0.9}
    ]
    ```
    
    Args:
        sectors: List of sector definitions with reveal_at and scan_rules
        agents: List of active agents with positions (currently not used for dynamic scan detection)
        elapsed_seconds: Mission elapsed time
        
    Returns:
        Dictionary containing:
        - overall_confidence: Average confidence across all sectors (0-100)
        - overall_detail_level: Average detail level across all sectors (0-5)
        - total_scan_count: Total number of scans performed across all sectors
        - sectors: Array of sector states with status, confidence, mapped_by, etc.
        
    Examples:
        >>> result = calculate_terrain_reconstruction(sectors, agents, 150)
        >>> result['overall_confidence']
        42
        >>> result['sectors'][0]['status']
        'partially_mapped'
    """
    sector_states = []
    total_scan_count = 0
    total_confidence = 0
    total_detail = 0
    
    for sector in sectors:
        sector_id = sector['sector_id']
        reveal_at = sector.get('reveal_at', 0)
        scan_rules = sector.get('scan_rules', [])
        
        # Determine sector status based on elapsed time and scan rules
        if elapsed_seconds < reveal_at:
            status = 'unknown'
            confidence = 0
            detail_level = 0
            mapped_by = []
            scan_count = 0
            first_detected = None
            last_updated = None
        else:
            # Sector is at least detected
            first_detected = reveal_at
            last_updated = elapsed_seconds
            
            # Count how many scans have occurred
            scan_count = 0
            mapped_by = []
            
            for rule in scan_rules:
                scan_time = rule.get('time', 0)
                agent_id = rule.get('agent_id', '')
                
                if elapsed_seconds >= scan_time:
                    scan_count += 1
                    if agent_id and agent_id not in mapped_by:
                        mapped_by.append(agent_id)
            
            # Calculate confidence and detail based on scan count
            if scan_count == 0:
                status = 'detected'
                confidence = 20
                detail_level = 1
            elif scan_count == 1:
                status = 'partially_mapped'
                confidence = 45
                detail_level = 2
            elif scan_count == 2:
                status = 'mapped'
                confidence = 70
                detail_level = 3
            elif scan_count >= 3:
                status = 'high_confidence'
                confidence = min(95, 70 + (scan_count - 2) * 10)
                detail_level = min(5, 3 + (scan_count - 2))
            
            # Check for hazardous/blocked status overrides
            if sector.get('is_hazardous') and elapsed_seconds >= sector.get('hazard_detected_at', reveal_at + 60):
                status = 'hazardous'
                confidence = min(100, confidence + 10)
            elif sector.get('is_blocked') and elapsed_seconds >= sector.get('blocked_detected_at', reveal_at + 30):
                status = 'blocked'
                confidence = min(100, confidence + 5)
        
        sector_state = {
            'sector_id': sector_id,
            'status': status,
            'confidence': confidence,
            'detail_level': detail_level,
            'mapped_by_agent_ids': mapped_by,
            'first_detected_at': first_detected,
            'last_updated_at': last_updated,
            'scan_count': scan_count
        }
        
        sector_states.append(sector_state)
        total_scan_count += scan_count
        total_confidence += confidence
        total_detail += detail_level
    
    # Calculate overall stats
    num_sectors = len(sectors) if sectors else 1
    overall_confidence = int(total_confidence / num_sectors) if num_sectors > 0 else 0
    overall_detail_level = int(total_detail / num_sectors) if num_sectors > 0 else 0
    
    return {
        'overall_confidence': overall_confidence,
        'overall_detail_level': overall_detail_level,
        'total_scan_count': total_scan_count,
        'sectors': sector_states
    }


def calculate_mission_state(
    mission_id: str,
    mission_name: str,
    use_case_slug: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str,
    random_seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate complete mission state for a given elapsed time.
    
    **This is the main entry point for all simulation state calculation.**
    
    This function is called by the `/api/v1/missions/{pk}/state/` endpoint
    to generate the complete dashboard state that drives all frontend visualizations.
    
    **Routing Logic:**
    Based on use_case_slug, routes to the appropriate scenario-specific simulation:
    - 'collapsed-building-search' -> simulate_collapsed_building()
    - 'cave-rescue' -> simulate_cave_rescue()
    - 'flooded-structure' -> simulate_flooded_structure()
    - 'industrial-inspection' -> simulate_industrial_inspection()
    - 'archaeological-exploration' -> simulate_archaeological_exploration()
    - Other -> create_empty_state() (fallback)
    
    **Each scenario simulator returns consistent structure:**
    ```json
    {
      "mission_id": "mission-alpha-001",
      "mission_name": "Collapsed Building Search Alpha",
      "elapsed_seconds": 245.3,
      "status": "running",
      "agents": [...],           // Agent positions, states, battery, signal
      "sensors": {...},           // Thermal, audio, gas detections
      "map_coverage": {...},      // Terrain reconstruction progress
      "timeline_events": [...],   // Chronological event list
      "ai_analysis": {...}        // AI recommendations (if any)
    }
    ```
    
    **Determinism:**
    If random_seed is provided, sets random.seed() to ensure reproducible results.
    Same elapsed_seconds with same seed always produces identical state.
    
    Args:
        mission_id: Unique mission identifier
        mission_name: Human-readable mission name
        use_case_slug: Determines which scenario to simulate
        elapsed_seconds: Mission elapsed time (from simulation.get_elapsed_seconds())
        speed_multiplier: Current simulation speed (1x, 2x, 5x, 10x)
        started_at: Real-world time when simulation started (optional)
        status: Simulation status ('not_started', 'running', 'paused', 'completed')
        random_seed: Optional seed for reproducible randomness
        
    Returns:
        Complete dashboard state dictionary with agents, sensors, map, events, etc.
        
    Performance:
        - Cached scenario data (via @lru_cache in scenario_engine)
        - Typical execution: 20-50ms
        - No database queries during calculation (after initial scenario load)
    """
    # Use seed for reproducible randomness
    if random_seed is not None:
        random.seed(random_seed)
    
    # Route to use-case-specific simulation
    if use_case_slug == 'collapsed-building-search':
        return simulate_collapsed_building(
            mission_id, mission_name, elapsed_seconds, speed_multiplier,
            started_at, status
        )
    elif use_case_slug == 'cave-rescue':
        return simulate_cave_rescue(
            mission_id, mission_name, elapsed_seconds, speed_multiplier,
            started_at, status
        )
    elif use_case_slug == 'flooded-structure':
        return simulate_flooded_structure(
            mission_id, mission_name, elapsed_seconds, speed_multiplier,
            started_at, status
        )
    elif use_case_slug == 'industrial-inspection':
        return simulate_industrial_inspection(
            mission_id, mission_name, elapsed_seconds, speed_multiplier,
            started_at, status
        )
    elif use_case_slug == 'archaeological-exploration':
        return simulate_archaeological_exploration(
            mission_id, mission_name, elapsed_seconds, speed_multiplier,
            started_at, status
        )
    else:
        # Generic fallback
        return create_empty_state(
            mission_id, mission_name, use_case_slug, elapsed_seconds,
            speed_multiplier, started_at, status
        )


def simulate_collapsed_building(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Simulate Collapsed Building Search scenario.
    
    **NOW USING SCENARIO ENGINE** - Data-driven simulation from database scenario.
    
    **Scenario:** collapsed-building-alpha-01
    - Loaded from database via MissionScenario model
    - Agent routes defined by RouteWaypoint sequences in database
    - Timeline events defined by ScenarioEvent records in database
    - Detections (thermal, audio) triggered at specific times/locations
    
    **To Modify Scenario Behavior:**
    1. Edit `data/scenarios/collapsed_building_scenario_alpha.json`
    2. Run: `python manage.py seed_mission_scenarios --file collapsed_building_scenario_alpha.json --overwrite`
    3. Restart Django server (to clear @lru_cache)
    4. No code changes needed!
    
    **Scenario Features:**
    - 4 agents: Drone A (scout), Drone B (relay), Drone C (thermal specialist), Relay Node 1 (static)
    - Progressive map reveal as drones explore sectors
    - Thermal anomaly detection in Basement Corridor (320 seconds)
    - Audio event detection in Basement Area (350 seconds)
    - Battery degradation forcing Drone B to land as relay (420 seconds)
    - Drone C mission priority streaming before battery exhaustion (550 seconds)
    
    **Map Coverage:**
    - Entrance -> Ground Floor -> Stairwell -> Basement
    - 10+ sectors with progressive reveal based on agent exploration timing
    - Confidence increases with multiple agent scans of same sector
    
    Args:
        mission_id: Unique mission identifier
        mission_name: Human-readable mission name
        elapsed_seconds: Mission elapsed time
        speed_multiplier: Current simulation speed
        started_at: Real-world time when simulation started (optional)
        status: Simulation status
        
    Returns:
        Complete dashboard state dictionary including:
        - agents: Positions, states, battery, signal strength, roles
        - sensors: Thermal and audio detections with locations and confidence
        - map_coverage: Sector-by-sector reconstruction progress
        - timeline_events: Chronological mission event list
        - network: Communication chain topology (active relays only)
    """
    from .scenario_engine import generate_simulation_state_from_scenario
    
    try:
        # Use scenario engine to generate simulation state
        return generate_simulation_state_from_scenario(
            mission_id=mission_id,
            scenario_id='collapsed-building-alpha-01',
            elapsed_seconds=elapsed_seconds,
            speed_multiplier=speed_multiplier,
            mission_name=mission_name,
            status=status
        )
    except Exception as e:
        # Fallback to basic state if scenario engine fails
        import traceback
        print(f"[Scenario Engine Error] {e}")
        traceback.print_exc()
        
        # Return minimal valid state
        return {
            'mission': {
                'mission_id': mission_id,
                'name': mission_name,
                'use_case': 'collapsed-building-search',
                'status': status
            },
            'simulation_clock': {
                'started_at': started_at.isoformat() if started_at else None,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'speed_multiplier': speed_multiplier,
                'is_running': status == 'running'
            },
            'error': str(e),
            'agents': [],
            'sectors': [],
            'events': [],
        }


def simulate_collapsed_building_legacy(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    LEGACY: Original hardcoded collapsed building simulation.
    
    Kept for reference and fallback. Will be removed once scenario engine is stable.
    
    Timeline:
    - 0-60s: Initial deployment and entry
    - 60-180s: Primary mapping phase
    - 120s: Dust occlusion event
    - 180s: Thermal anomaly detected
    - 240s: Audio event detected
    - 300s: Drone B signal degrades
    - 360s: Drone B lands as relay
    - 420s: Mission transitions to focused search
    """
    minutes_elapsed = elapsed_seconds / 60.0
    
    # Agent states evolve over time
    agents = []
    
    # Static relay node (always present at entry)
    # Using Digital Twin coordinates: ground-entry at (0, 0, 0)
    agents.append({
        'agent_id': 'relay-1',
        'name': 'Static Relay Node',
        'role': 'Base relay',
        'state': 'active',
        'battery_percent': 100,  # Powered
        'signal_strength': 95,
        'location_label': 'Ground Level Entry',
        'sector': 'ground-entry',  # Digital Twin sector ID
        'position': {'x': 0, 'y': 0, 'z': 0},  # Digital Twin: ground-entry
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Drone A - Scout/Mapper (deploys at 30s)
    if elapsed_seconds >= 30:
        drone_a_battery = max(5, 100 - ((elapsed_seconds - 30) / 20))  # Start counting from deployment
        drone_a_signal = 72 + math.sin(elapsed_seconds / 30) * 8  # Fluctuates
        drone_a_state = 'healthy' if elapsed_seconds < 420 else 'degraded'
        
        # Position based on time since deployment (moving through building)
        # Digital Twin coords: start at (0,0,0), move through ground floor, then explore upper floors
        progress = (elapsed_seconds - 30) / 10  # 10 seconds per unit of progress
        
        if elapsed_seconds < 90:
            drone_a_loc = 'Ground Floor Lobby'
            drone_a_sector = 'ground-lobby'
            # Move from entry (0,0,0) to lobby (8,0,0)
            t = min(1.0, progress / 3)  # 30 seconds to traverse
            x = 0 + (8 * t)
            y = 0
            z = 0
        elif elapsed_seconds < 180:
            drone_a_loc = 'East Corridor'
            drone_a_sector = 'ground-corridor-east'
            # Move from lobby (8,0,0) to east corridor (18,3,0)
            t = min(1.0, (progress - 6) / 4)  # 40 seconds to traverse
            x = 8 + (10 * t)
            y = 0 + (3 * t)
            z = 0
        elif elapsed_seconds < 300:
            drone_a_loc = 'First Floor Corridor'
            drone_a_sector = 'floor-1-corridor'
            # Move to first floor (12,0,3.5)
            t = min(1.0, (progress - 15) / 5)  # 50 seconds to climb and traverse
            x = 18 - (6 * t)
            y = 3 - (3 * t)
            z = 0 + (3.5 * t)
        else:
            drone_a_loc = 'Second Floor West Corridor'
            drone_a_sector = 'floor-2-corridor-west'
            # Move to second floor (8,-5,7.0)
            t = min(1.0, (progress - 27) / 5)
            x = 12 - (4 * t)
            y = 0 - (5 * t)
            z = 3.5 + (3.5 * t)
        
        agents.append({
            'agent_id': 'drone-a',
            'name': 'Scout Drone A',
            'role': 'Primary mapper',
            'state': drone_a_state,
            'battery_percent': int(drone_a_battery),
            'signal_strength': int(drone_a_signal),
            'location_label': drone_a_loc,
            'sector': drone_a_sector,
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'sensors': ['LiDAR', 'Thermal', 'RGB'],
            'nfc_recovery_available': False
        })
    
    # Drone B - Detection drone (deploys at 60s)
    if elapsed_seconds >= 60:
        drone_b_battery = max(3, 100 - ((elapsed_seconds - 60) / 15))  # Start counting from deployment
        drone_b_signal = 68 - ((elapsed_seconds - 60) / 20) if elapsed_seconds < 360 else 45
        
        # Digital Twin coords: slower exploration path
        progress = (elapsed_seconds - 60) / 12  # 12 seconds per unit
        
        if elapsed_seconds < 300:
            drone_b_state = 'healthy'
            drone_b_location = 'Ground Floor Lobby'
            drone_b_sector = 'ground-lobby'
            # Move from entry (0,0,0) toward lobby center (8,0,0)
            t = min(1.0, progress / 5)
            x = 0 + (8 * t)
            y = 0
            z = 0.5  # Flying slightly above ground
        elif elapsed_seconds < 360:
            drone_b_state = 'degraded'
            drone_b_location = 'Basement Corridor'
            drone_b_sector = 'basement-corridor'
            # Move toward basement corridor (12,-8,-3.5)
            t = min(1.0, (progress - 20) / 3)
            x = 8 + (4 * t)
            y = 0 - (8 * t)
            z = 0.5 - (4.0 * t)
        else:
            drone_b_state = 'landed_relay'
            drone_b_location = 'Basement Corridor (relay)'
            drone_b_sector = 'basement-corridor'
            # Landed in basement corridor
            x = 12
            y = -8
            z = -3.5
        
        agents.append({
            'agent_id': 'drone-b',
            'name': 'Thermal/Audio Drone',
            'role': 'Detection',
            'state': drone_b_state,
            'battery_percent': int(drone_b_battery),
            'signal_strength': int(drone_b_signal),
            'location_label': drone_b_location,
            'sector': drone_b_sector,
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'sensors': ['Thermal', 'Microphone Array', 'WiFi Scanner'],
            'nfc_recovery_available': drone_b_state == 'landed_relay'
        })
    
    # Drone C - Relay (deploys at 90s, eventually sacrificed)
    if elapsed_seconds >= 90:
        drone_c_battery = max(0, 100 - ((elapsed_seconds - 90) / 18))
        drone_c_signal = 88 if elapsed_seconds < 240 else 78
        
        if elapsed_seconds < 240:
            drone_c_state = 'healthy'
            drone_c_location = 'East Corridor'
            drone_c_sector = 'ground-corridor-east'
            # Digital Twin: move from entry toward east corridor (18,3,0)
            progress = (elapsed_seconds - 90) / 150  # Slow deployment to relay position
            x = 0 + (18 * min(1.0, progress))
            y = 0 + (3 * min(1.0, progress))
            z = 2  # Flying at relay height
        elif elapsed_seconds < 420:
            drone_c_state = 'healthy'
            drone_c_location = 'East Corridor (relay position)'
            drone_c_sector = 'ground-corridor-east'
            # Stationary relay at east corridor
            x = 18
            y = 3
            z = 2
        else:
            drone_c_state = 'sacrificed'
            drone_c_location = 'East Corridor (sacrificed relay)'
            drone_c_sector = 'ground-corridor-east'
            # Sacrificed relay position
            x = 18
            y = 3
            z = 2
        
        agents.append({
            'agent_id': 'drone-c',
            'name': 'Relay Drone',
            'role': 'Communications relay',
            'state': drone_c_state,
            'battery_percent': int(drone_c_battery),
            'signal_strength': int(drone_c_signal),
            'location_label': drone_c_location,
            'sector': drone_c_sector,
            'position': {
                'x': x,
                'y': y,
                'z': z
            },
            'sensors': [],
            'nfc_recovery_available': drone_c_state == 'sacrificed'
        })
    
    # Network state
    base_signal = 88 - (elapsed_seconds / 60)
    packet_loss = min(15, 2 + (elapsed_seconds / 45))
    mesh_health = max(50, 90 - (elapsed_seconds / 20))
    
    relay_chain = ['relay-1']  # Static relay node always present
    # Only add drones to relay chain if they're deployed
    if elapsed_seconds >= 90:
        drone_c_agent = next((a for a in agents if a['agent_id'] == 'drone-c'), None)
        if drone_c_agent and drone_c_agent['state'] != 'sacrificed':
            relay_chain.append('drone-c')
    if elapsed_seconds >= 60:
        drone_b_agent = next((a for a in agents if a['agent_id'] == 'drone-b'), None)
        if drone_b_agent and drone_b_agent['state'] == 'landed_relay':
            relay_chain.append('drone-b')
    if elapsed_seconds >= 30:
        relay_chain.append('drone-a')
    
    network = {
        'base_signal_strength': int(base_signal),
        'mesh_health': int(mesh_health),
        'relay_chain': relay_chain,
        'packet_loss_percent': int(packet_loss)
    }
    
    # Map coverage grows over time
    coverage_percent = min(95, (elapsed_seconds / 600) * 100)
    confidence = max(0.55, 0.95 - (elapsed_seconds / 1000))
    total_points = int(5000 + (elapsed_seconds * 22))
    new_points = int(1250 if elapsed_seconds < 360 else 850)
    
    mapped_sectors = []
    if elapsed_seconds > 30:
        mapped_sectors.append('Entrance')
    if elapsed_seconds > 90:
        mapped_sectors.append('Corridor A')
    if elapsed_seconds > 150:
        mapped_sectors.append('Void 1')
    if elapsed_seconds > 240:
        mapped_sectors.append('Corridor B')
    if elapsed_seconds > 360:
        mapped_sectors.append('Void 2')
    
    blocked_sectors = []
    if elapsed_seconds > 120:
        blocked_sectors.append('Collapsed Stairwell')
    if elapsed_seconds > 300:
        blocked_sectors.append('Rubble Zone A')
    
    accessible_areas = []
    if elapsed_seconds > 150:
        accessible_areas.append({
            'label': 'Void 1',
            'confidence': 0.82,
            'risk': 'medium'
        })
    if elapsed_seconds > 360:
        accessible_areas.append({
            'label': 'Void 2',
            'confidence': 0.68,
            'risk': 'high'
        })
    
    map_data = {
        'map_type': 'void-map',
        'coverage_percent': int(coverage_percent),
        'confidence': round(confidence, 2),
        'total_points': total_points,
        'new_points_generated': new_points,
        'mapped_sectors': mapped_sectors,
        'blocked_sectors': blocked_sectors,
        'accessible_areas': accessible_areas
    }
    
    # Sensor events
    thermal_anomalies = []
    if elapsed_seconds > 180:
        thermal_anomalies.append({
            'detected_at': '03:00',
            'location': 'Void 1, Northeast corner',
            'temperature_delta': 2.4,
            'confidence': 0.58,
            'human_review_required': True,
            'status': 'under review'
        })
    
    audio_events = []
    if elapsed_seconds > 240:
        audio_events.append({
            'detected_at': '04:00',
            'location': 'Void 1',
            'type': 'voice-like signature',
            'confidence': 0.48,
            'frequency_range': '300-3000Hz',
            'human_review_required': True,
            'status': 'requires verification'
        })
    
    device_signals = []
    if elapsed_seconds > 200:
        device_signals.append({
            'detected_at': '03:20',
            'device_type': 'WiFi',
            'mac_address': '**:**:4a:2b:**:**',
            'signal_strength': -78,
            'last_seen': '3m ago'
        })
    
    sensors = {
        'thermal_anomalies': thermal_anomalies,
        'audio_events': audio_events,
        'device_signals': device_signals,
        'environmental_readings': []
    }
    
    # Timeline events
    events = []
    if elapsed_seconds > 5:
        events.append({
            'type': 'mission-start',
            'time': '00:00',
            'title': 'Mission started',
            'description': 'Collapsed Building Search mission initiated',
            'agent': None
        })
    if elapsed_seconds > 30:
        events.append({
            'type': 'agent-deployed',
            'time': '00:30',
            'title': 'Scout Drone A deployed',
            'description': 'Primary mapping initiated',
            'agent': 'drone-a'
        })
    if elapsed_seconds > 60:
        events.append({
            'type': 'agent-deployed',
            'time': '01:00',
            'title': 'Thermal/Audio Drone deployed',
            'description': 'Detection systems active',
            'agent': 'drone-b'
        })
    if elapsed_seconds > 120:
        events.append({
            'type': 'failure',
            'time': '02:00',
            'title': 'Dust occlusion detected',
            'description': 'LiDAR quality degraded due to particulate interference',
            'agent': 'drone-a',
            'severity': 'moderate'
        })
    if elapsed_seconds > 180:
        events.append({
            'type': 'detection',
            'time': '03:00',
            'title': 'Thermal anomaly detected',
            'description': 'Possible heat signature in Void 1',
            'agent': 'drone-b',
            'severity': 'medium'
        })
    if elapsed_seconds > 240:
        events.append({
            'type': 'detection',
            'time': '04:00',
            'title': 'Audio signature detected',
            'description': 'Voice-like pattern detected, confidence 48%',
            'agent': 'drone-b',
            'severity': 'high'
        })
    if elapsed_seconds > 300:
        events.append({
            'type': 'state-change',
            'time': '05:00',
            'title': 'Signal degradation',
            'description': 'Drone B signal strength dropping',
            'agent': 'drone-b',
            'severity': 'moderate'
        })
    if elapsed_seconds > 360:
        events.append({
            'type': 'state-change',
            'time': '06:00',
            'title': 'Drone B landed as relay',
            'description': 'Battery critical, landed to preserve relay function',
            'agent': 'drone-b',
            'severity': 'high'
        })
    
    # AI analysis
    if elapsed_seconds < 180:
        ai_summary = 'Initial mapping in progress. No confirmed detections yet.'
        priority_findings = []
        human_review = False
        ai_confidence = 0.64
    elif elapsed_seconds < 240:
        ai_summary = 'Thermal anomaly detected in Void 1. Investigating possible survivor presence.'
        priority_findings = ['Thermal anomaly at Void 1 (confidence 58%)']
        human_review = True
        ai_confidence = 0.58
    else:
        ai_summary = 'Multiple detection signals in Void 1. Strong recommendation for human review and possible rescue team deployment.'
        priority_findings = [
            'Thermal anomaly at Void 1 (confidence 58%)',
            'Voice-like audio signature (confidence 48%)',
            'WiFi device signal detected'
        ]
        human_review = True
        ai_confidence = 0.72
    
    ai_analysis = {
        'summary': ai_summary,
        'priority_findings': priority_findings,
        'human_review_required': human_review,
        'confidence': ai_confidence
    }
    
    # Terrain reconstruction with progressive sector reveal
    # All sectors start unknown, revealed as agents scan them
    terrain_sectors = [
        {
            'sector_id': 'entry',
            'reveal_at': 0,
            'scan_rules': [
                {'time': 0, 'agent_id': 'relay-1'},  # Base station knows entry
                {'time': 30, 'agent_id': 'drone-a'},  # Scout passes through
                {'time': 60, 'agent_id': 'drone-b'},  # Thermal/audio passes through
            ]
        },
        {
            'sector_id': 'corridor-a',
            'reveal_at': 30,
            'scan_rules': [
                {'time': 60, 'agent_id': 'drone-a'},  # Scout maps corridor
                {'time': 120, 'agent_id': 'drone-b'},  # Thermal/audio scans
                {'time': 150, 'agent_id': 'drone-c'},  # Relay positioned here
            ]
        },
        {
            'sector_id': 'corridor-b',
            'reveal_at': 90,
            'scan_rules': [
                {'time': 150, 'agent_id': 'drone-a'},  # Scout detects corridor B
                {'time': 210, 'agent_id': 'drone-b'},  # Thermal/audio scans for survivors
            ]
        },
        {
            'sector_id': 'void-1',
            'reveal_at': 120,
            'scan_rules': [
                {'time': 120, 'agent_id': 'drone-a'},  # Scout discovers void
                {'time': 180, 'agent_id': 'drone-a'},  # Scout detailed scan
                {'time': 240, 'agent_id': 'drone-a'},  # Scout deep scan
            ]
        },
        {
            'sector_id': 'collapsed',
            'reveal_at': 180,
            'scan_rules': [
                {'time': 180, 'agent_id': 'drone-a'},  # Scout detects collapsed section
            ],
            'is_blocked': True
        },
    ]
    
    terrain_reconstruction = calculate_terrain_reconstruction(
        terrain_sectors,
        agents,
        elapsed_seconds
    )
    
    # Environmental sensors - O2 and CO2 for survivor detection
    # O2 sensor appears at 60s when thermal/audio drone activates
    if elapsed_seconds >= 60:
        o2_value = max(19.8, 20.9 - (elapsed_seconds / 800))  # Slowly decreasing in confined space
        o2_status = 'normal' if o2_value >= 19.5 else 'watch' if o2_value >= 19.0 else 'warning'
        sensors['environmental_readings'].append({
            'sensor_type': 'oxygen',
            'display_name': 'O2',
            'value': round(o2_value, 1),
            'unit': '%',
            'status': o2_status,
            'location_label': drone_b_location,
            'confidence': 0.88,
            'detected_at': 60,
            'timestamp': format_time(elapsed_seconds)
        })
    
    # CO2 sensor appears at 90s
    if elapsed_seconds >= 90:
        # Higher CO2 suggests human presence or confined space buildup
        co2_value = min(1500, 420 + (elapsed_seconds * 1.8))
        co2_status = 'normal' if co2_value <= 800 else 'watch' if co2_value <= 1000 else 'warning' if co2_value <= 1200 else 'critical'
        sensors['environmental_readings'].append({
            'sensor_type': 'carbon_dioxide',
            'display_name': 'CO2',
            'value': int(co2_value),
            'unit': 'ppm',
            'status': co2_status,
            'location_label': drone_b_location,
            'confidence': 0.82,
            'detected_at': 90,
            'timestamp': format_time(elapsed_seconds)
        })
    
    # Media feeds - simulated camera/sensor returns
    media_feeds = []
    
    # Scout Drone A: Low-light RGB stills of rubble and voids
    if elapsed_seconds >= 45:
        scout_signal = next((a for a in agents if a['agent_id'] == 'drone-a'), None)
        if scout_signal:
            frame_status = 'live' if scout_signal['signal_strength'] > 70 else 'degraded' if scout_signal['signal_strength'] > 50 else 'delayed'
            frame_conf = min(95, 60 + scout_signal['signal_strength'] / 3)
            
            media_feeds.append({
                'frame_id': f'scout-rgb-{int(elapsed_seconds)}',
                'agent_id': 'drone-a',
                'agent_name': 'Scout Drone A',
                'sensor_type': 'low_light_camera',
                'frame_type': 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': scout_signal['signal_strength'],
                'confidence': int(frame_conf),
                'location_label': scout_signal['location_label'],
                'annotations': ['structural debris', 'mapping active'] if frame_status == 'live' else ['signal degraded', 'frame delayed'],
                'description': f'Low-light structural imaging from {scout_signal["location_label"]}.'
            })
    
    # Thermal/Audio Drone: Thermal frames
    if elapsed_seconds >= 75:
        thermal_agent = next((a for a in agents if a['agent_id'] == 'drone-b'), None)
        if thermal_agent:
            # After thermal anomaly detected at 180s, flag frame for human review
            if elapsed_seconds >= 180:
                frame_status = 'thermal_detection' if elapsed_seconds < 300 else 'ai_flagged'
                annotations = ['thermal anomaly detected', 'possible survivor', 'human review required']
                description = 'Thermal frame indicates warm object in Void Space 1. Human review required.'
                conf = 78
            else:
                frame_status = 'live'
                annotations = ['thermal scan active', 'baseline mapping']
                description = f'Thermal imaging of {thermal_agent["location_label"]}.'
                conf = 82
            
            media_feeds.append({
                'frame_id': f'thermal-{int(elapsed_seconds)}',
                'agent_id': 'drone-b',
                'agent_name': 'Thermal/Audio Drone',
                'sensor_type': 'thermal_camera',
                'frame_type': 'thermal',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': thermal_agent['signal_strength'],
                'confidence': conf,
                'location_label': thermal_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Dust occlusion degrades image quality after 120s
    if elapsed_seconds >= 120:
        scout_agent = next((a for a in agents if a['agent_id'] == 'drone-a'), None)
        if scout_agent and scout_agent['state'] == 'degraded':
            media_feeds.append({
                'frame_id': f'scout-degraded-{int(elapsed_seconds)}',
                'agent_id': 'drone-a',
                'agent_name': 'Scout Drone A',
                'sensor_type': 'low_light_camera',
                'frame_type': 'still',
                'status': 'degraded',
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': scout_agent['signal_strength'],
                'confidence': 42,
                'location_label': scout_agent['location_label'],
                'annotations': ['dust occlusion', 'reduced visibility', 'sensor degraded'],
                'description': 'Image quality degraded due to particulate interference.'
            })
    
    # If thermal/audio drone becomes relay, show last good frame
    if elapsed_seconds >= 360:
        relay_agent = next((a for a in agents if a['agent_id'] == 'drone-b' and a['state'] == 'landed_relay'), None)
        if relay_agent:
            media_feeds.append({
                'frame_id': 'thermal-last-good',
                'agent_id': 'drone-b',
                'agent_name': 'Thermal/Audio Drone',
                'sensor_type': 'thermal_camera',
                'frame_type': 'last_good_frame',
                'status': 'last_good_frame',
                'mission_time': format_time(360),
                'signal_quality': 45,
                'confidence': 65,
                'location_label': 'Corridor B (relay)',
                'annotations': ['last good frame', 'drone now relay mode'],
                'description': 'Last thermal frame before drone entered relay mode.'
            })
    
    # Audio detections - connect to generated media system
    audio_detections = []
    
    # Audio detection at 240s - tapping pattern detected
    if elapsed_seconds >= 240:
        thermal_agent = next((a for a in agents if a['agent_id'] == 'drone-b'), None)
        if thermal_agent:
            detection_status = 'human_review_required' if elapsed_seconds < 300 else 'confirmed'
            audio_detections.append({
                'id': f'{mission_id}-tapping-audio-001',
                'agent_id': 'drone-b',
                'agent_name': 'Thermal/Audio Drone',
                'sensor_type': 'microphone',
                'audio_type': 'tapping',
                'status': detection_status,
                'mission_time': format_time(240),
                'signal_quality': 58,
                'confidence': 82,
                'location_label': 'Void Space 2',
                'annotations': ['rhythmic pattern', 'possible human signal', 'low bandwidth'],
                'description': 'Rhythmic tapping detected. Pattern suggests intentional signal.',
                'audio_url': f'/api/v1/generated-media/{mission_id}-tapping-audio-001/audio/',
                'spectrogram_url': f'/api/v1/generated-media/{mission_id}-tapping-audio-001/spectrogram/'
            })
    
    # Additional audio detection at 360s - possible voice
    if elapsed_seconds >= 360:
        audio_detections.append({
            'id': f'{mission_id}-voice-audio-001',
            'agent_id': 'drone-b',
            'agent_name': 'Thermal/Audio Drone',
            'sensor_type': 'microphone',
            'audio_type': 'voice_like',
            'status': 'analyzing',
            'mission_time': format_time(360),
            'signal_quality': 42,
            'confidence': 68,
            'location_label': 'Void Space 2',
            'annotations': ['voice-like audio', 'possible human cue', 'comms degraded'],
            'description': 'Voice-like audio pattern detected. Quality degraded due to signal loss.',
                'audio_url': f'/api/v1/generated-media/{mission_id}-voice-audio-001/audio/',
                'spectrogram_url': f'/api/v1/generated-media/{mission_id}-voice-audio-001/spectrogram/'
            })
    
    # === MISSION DISTANCE INTELLIGENCE: 3D NAVIGATION MODEL ===
    # Define mission origin (entry point / base station)
    # Digital Twin coordinates: ground-entry at (0, 0, 0)
    origin_position = {'x': 0, 'y': 0, 'z': 0}
    
    # Navigation model for GPS-denied environments
    # Uses local 3D coordinate system with mission north reference
    compass_confidence, compass_reliability, compass_reason = calculate_compass_confidence(
        environment_type='collapsed_building',
        distance_from_origin_m=0,  # Will be calculated per agent
        has_metal_nearby=True,  # Steel reinforcement in building
        has_electrical_interference=False
    )
    
    navigation_model = {
        'coordinate_system': 'local_mission_3d_grid',
        'origin_sector_id': 'entry',
        'origin_label': 'Entry / Base Station',
        'origin_position': origin_position,
        'units': 'metres',
        'horizontal_units': 'metres',
        'vertical_units': 'metres',
        'svg_unit_to_metres': 0.25,  # 1 SVG unit = 0.25 metres
        'grid_square_metres': 5,
        'z_reference': 'origin_relative',
        'z_positive_direction': 'up',
        'depth_positive_direction': 'down',
        'north_reference': 'mission_north',
        'bearing_reference': 'magnetic_simulated',
        'magnetic_declination_deg': 0,
        'bearing_confidence': round(compass_confidence, 2),
        'bearing_reliability': compass_reliability,
        'bearing_reliability_reason': compass_reason
    }
    
    # Define detailed sector positions with 3D coordinates
    # Using Digital Twin collapsed building sectors
    # Start with base sector definitions
    sectors_base = [
        {
            'sector_id': 'ground-entry',
            'label': 'Ground Level Entry',
            'centroid': {'x': 0, 'y': 0, 'z': 0},
            'type': 'accessible',
            'exploration_start': 0  # Always visible from start
        },
        {
            'sector_id': 'ground-lobby',
            'label': 'Ground Floor Lobby',
            'centroid': {'x': 8, 'y': 0, 'z': 0},
            'type': 'accessible',
            'exploration_start': 30  # Drone A enters at 30s
        },
        {
            'sector_id': 'ground-corridor-east',
            'label': 'East Corridor',
            'centroid': {'x': 18, 'y': 3, 'z': 0},
            'type': 'accessible',
            'exploration_start': 90  # Drone A/C reach around 90s
        },
        {
            'sector_id': 'basement-corridor',
            'label': 'Basement Corridor',
            'centroid': {'x': 12, 'y': -8, 'z': -3.5},  # 3.5m below entry
            'type': 'accessible',
            'exploration_start': 300  # Drone B descends at 300s
        },
        {
            'sector_id': 'basement-storage',
            'label': 'Basement Storage',
            'centroid': {'x': 18, 'y': -10, 'z': -3.5},  # 3.5m below entry
            'type': 'accessible',
            'exploration_start': 420  # Not explored yet in this demo
        },
        {
            'sector_id': 'floor-1-corridor',
            'label': 'First Floor Corridor',
            'centroid': {'x': 12, 'y': 0, 'z': 3.5},  # 3.5m above entry
            'type': 'accessible',
            'exploration_start': 180  # Drone A ascends at 180s
        },
        {
            'sector_id': 'floor-2-corridor-west',
            'label': 'Second Floor West Corridor',
            'centroid': {'x': 8, 'y': -5, 'z': 7.0},  # 7m above entry
            'type': 'accessible',
            'exploration_start': 300  # Drone A reaches at 300s
        }
    ]
    
    # Calculate sector confidence based on exploration progress
    sectors_detailed = []
    for sector_base in sectors_base:
        sector = sector_base.copy()
        
        # Calculate confidence based on elapsed time since exploration started
        if elapsed_seconds >= sector_base['exploration_start']:
            time_explored = elapsed_seconds - sector_base['exploration_start']
            # Confidence builds up over 30 seconds of exploration
            confidence = min(1.0, 0.3 + (time_explored / 30) * 0.7)
        else:
            # Not yet explored - zero confidence
            confidence = 0.0
        
        sector['confidence'] = round(confidence, 2)
        sectors_detailed.append(sector)
    
    # Calculate distance, bearing, and elevation for each sector
    for sector in sectors_detailed:
        centroid = sector['centroid']
        
        # 2D and 3D distances from origin
        distance_2d = calculate_distance_2d(origin_position, centroid)
        distance_3d = calculate_distance_3d(origin_position, centroid)
        
        # Bearing from origin
        bearing_deg = calculate_bearing_degrees(origin_position, centroid)
        bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        
        # Elevation and depth
        elevation_m, depth_m = calculate_elevation_depth(centroid['z'])
        vertical_label = calculate_vertical_profile_label(centroid['z'], context='building')
        depth_elevation_label = format_depth_elevation_label(centroid['z'], use_arrows=True)
        
        # Add calculated fields to sector
        sector.update({
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_offset_from_origin_m': round(elevation_m, 1),
            'straight_line_2d_distance_from_origin_m': round(distance_2d, 1),
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1),
            'bearing_from_origin_cardinal': bearing_cardinal,
            'vertical_profile_label': vertical_label,
            'depth_elevation_label': depth_elevation_label
        })
    
    # Define path segments with 3D distance and slope
    # These represent traversable routes between sectors (Digital Twin building paths)
    path_segments = [
        {
            'from_sector_id': 'ground-entry',
            'to_sector_id': 'ground-lobby',
            'from_position': {'x': 0, 'y': 0, 'z': 0},
            'to_position': {'x': 8, 'y': 0, 'z': 0}
        },
        {
            'from_sector_id': 'ground-lobby',
            'to_sector_id': 'ground-corridor-east',
            'from_position': {'x': 8, 'y': 0, 'z': 0},
            'to_position': {'x': 18, 'y': 3, 'z': 0}
        },
        {
            'from_sector_id': 'ground-lobby',
            'to_sector_id': 'basement-corridor',
            'from_position': {'x': 8, 'y': 0, 'z': 0},
            'to_position': {'x': 12, 'y': -8, 'z': -3.5}
        },
        {
            'from_sector_id': 'ground-corridor-east',
            'to_sector_id': 'floor-1-corridor',
            'from_position': {'x': 18, 'y': 3, 'z': 0},
            'to_position': {'x': 12, 'y': 0, 'z': 3.5}
        }
    ]
    
    # Calculate 3D path metrics
    for path in path_segments:
        from_pos = path['from_position']
        to_pos = path['to_position']
        
        # Horizontal and vertical components
        horizontal_distance = calculate_distance_2d(from_pos, to_pos)
        vertical_change = to_pos['z'] - from_pos['z']
        
        # 3D segment distance
        segment_3d_distance = calculate_distance_3d(from_pos, to_pos)
        
        # Slope and incline
        slope_percent, incline_label = calculate_slope_and_incline(horizontal_distance, vertical_change)
        
        # Bearing
        bearing_deg = calculate_bearing_degrees(from_pos, to_pos)
        bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        
        # Traversal risk based on slope
        if abs(slope_percent) > 40:
            traversal_risk = 'high'
        elif abs(slope_percent) > 20:
            traversal_risk = 'medium'
        else:
            traversal_risk = 'low'
        
        # Add calculated fields
        path.update({
            'horizontal_distance_m': round(horizontal_distance, 1),
            'vertical_change_m': round(vertical_change, 1),
            'segment_3d_distance_m': round(segment_3d_distance, 1),
            'segment_bearing_deg': round(bearing_deg, 1),
            'segment_bearing_cardinal': bearing_cardinal,
            'slope_percent': round(slope_percent, 1),
            'incline_label': incline_label,
            'traversal_risk': traversal_risk,
            'status': 'traversable',
            'traversable_by_capabilities': ['drone', 'small_robot']
        })
    
    # Enhance agents with distance, bearing, and elevation data
    relay_agents = [a for a in agents if 'relay' in a['state'].lower() or a['agent_id'] == 'relay-1']
    
    for agent in agents:
        agent_pos = agent.get('position', origin_position)
        
        # Distance from origin
        distance_2d = calculate_distance_2d(origin_position, agent_pos)
        distance_3d = calculate_distance_3d(origin_position, agent_pos)
        
        # Bearing from origin
        if distance_2d > 1:  # Only meaningful if agent has moved
            bearing_deg = calculate_bearing_degrees(origin_position, agent_pos)
            bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        else:
            bearing_deg = 0
            bearing_cardinal = 'N'
        
        # Elevation and depth
        elevation_m, depth_m = calculate_elevation_depth(agent_pos.get('z', 0))
        vertical_label = calculate_vertical_profile_label(agent_pos.get('z', 0), context='building')
        depth_elevation_label = format_depth_elevation_label(agent_pos.get('z', 0), use_arrows=True)
        
        # Heading (simulated - in real system would come from IMU/compass)
        # For now, assume heading matches bearing if agent is moving
        heading_deg = bearing_deg if agent['state'] in ['healthy', 'degraded'] else None
        
        # Nearest relay
        nearest_relay_info = find_nearest_relay(agent_pos, relay_agents, use_3d=True)
        
        # Contact path length through mesh
        contact_path_length = calculate_contact_path_length(
            agent_pos,
            relay_agents[1:] if len(relay_agents) > 1 else [],  # Exclude base relay from chain
            origin_position,
            use_3d=True
        )
        
        # Estimated return time (assume 2 m/s average speed)
        return_route_distance = distance_3d  # Simplified - would use actual route in real system
        estimated_return_time = estimate_return_time(return_route_distance, average_speed_m_per_s=2.0)
        
        # Route distance from origin (for route profile positioning)
        # This is the cumulative distance along the route path
        # For now using 2D distance as approximation - real system would track actual path
        route_distance_from_origin_m = distance_2d
        
        # Add navigation intelligence fields
        agent['navigation'] = {
            'distance_from_origin_m': round(distance_2d, 1),
            'route_distance_from_origin_m': round(route_distance_from_origin_m, 1),
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1) if distance_2d > 1 else None,
            'bearing_from_origin_cardinal': bearing_cardinal if distance_2d > 1 else None,
            'heading_deg': round(heading_deg, 1) if heading_deg is not None else None,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_offset_from_origin_m': round(elevation_m, 1),
            'vertical_profile_label': vertical_label,
            'depth_elevation_label': depth_elevation_label,
            'estimated_return_route_distance_m': round(return_route_distance, 1),
            'estimated_return_time_seconds': round(estimated_return_time, 0),
            'nearest_relay': nearest_relay_info,
            'contact_path_length_m': round(contact_path_length, 1)
        }
    
    # Enhance audio detections with 3D position data
    for detection in audio_detections:
        # Get position based on location label (Digital Twin coordinates)
        # In real system, this would come from agent position at detection time
        if 'Void Space 2' in detection['location_label']:
            detection_pos = {'x': 18, 'y': -10, 'z': -3.5}  # basement-storage
        elif 'Void Space 1' in detection['location_label']:
            detection_pos = {'x': 12, 'y': -8, 'z': -3.5}  # basement-corridor
        else:
            detection_pos = {'x': 8, 'y': 0, 'z': 0}  # ground-lobby
        
        # Calculate distance and bearing
        distance_2d = calculate_distance_2d(origin_position, detection_pos)
        distance_3d = calculate_distance_3d(origin_position, detection_pos)
        bearing_deg = calculate_bearing_degrees(origin_position, detection_pos)
        bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        
        # Elevation and depth
        elevation_m, depth_m = calculate_elevation_depth(detection_pos['z'])
        vertical_label = calculate_vertical_profile_label(detection_pos['z'], context='building')
        depth_elevation_label = format_depth_elevation_label(detection_pos['z'], use_arrows=True)
        
        # Contact path length (how far signal travels through mesh)
        contact_path_length = calculate_contact_path_length(
            detection_pos,
            relay_agents[1:] if len(relay_agents) > 1 else [],
            origin_position,
            use_3d=True
        )
        
        # Comms risk based on contact path length and depth
        if contact_path_length > 80 or depth_m > 5:
            comms_risk = 'high'
        elif contact_path_length > 50 or depth_m > 3:
            comms_risk = 'medium'
        else:
            comms_risk = 'low'
        
        # Add navigation fields
        detection['position'] = detection_pos
        detection['navigation'] = {
            'route_distance_from_origin_m': round(distance_2d, 1),  # Simplified - would use route in real system
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1),
            'bearing_from_origin_cardinal': bearing_cardinal,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_context_label': vertical_label,
            'depth_elevation_label': depth_elevation_label,
            'contact_path_length_m': round(contact_path_length, 1),
            'comms_risk': comms_risk
        }
    
    # Build complete state
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': 'collapsed-building-search',
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'navigation_model': navigation_model,
        'sectors': sectors_detailed,
        'paths': path_segments,
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction,
        'media_feeds': media_feeds,
        'audio_detections': audio_detections
    }


def calculate_mission_escalation_cave_rescue(
    elapsed_seconds: float,
    mesh_health: float,
    packet_loss: float,
    audio_events: list
) -> Dict[str, Any]:
    """
    Calculate mission escalation state for cave rescue.
    
    Escalates when:
    - High-priority detection exists (voice-like audio, tapping)
    - Communications chain is degrading
    """
    # No escalation before any detections
    if elapsed_seconds < 420:
        return {
            'active': False,
            'severity': 'none',
            'reason': None,
            'area_of_interest': None,
            'contact_continuity_risk': 'stable',
            'recommended_actions': []
        }
    
    # Determine detection priority
    has_voice_detection = elapsed_seconds >= 480
    has_tapping_detection = elapsed_seconds >= 420
    
    # Determine comms health
    comms_degraded = mesh_health < 70 or packet_loss > 15
    comms_critical = mesh_health < 60 or packet_loss > 20
    
    # Calculate contact continuity risk
    if comms_critical:
        contact_risk = 'critical'
    elif comms_degraded:
        contact_risk = 'high'
    elif mesh_health < 80:
        contact_risk = 'watch'
    else:
        contact_risk = 'stable'
    
    # Escalation logic
    if has_voice_detection and comms_degraded:
        severity = 'critical' if comms_critical else 'urgent'
        reason = 'Voice-like audio detected in Deep Squeeze with degrading communications.'
        area_of_interest = 'deep-squeeze'
        
        recommended_actions = [
            'Deploy additional relay drone to Junction Chamber',
            'Preserve comms path from Main Tunnel to Junction Chamber',
            'Hold wider exploration until signal is stabilized',
            'Prepare ground team for physical approach if contact is lost'
        ]
        
        if comms_critical:
            recommended_actions.insert(0, 'IMMEDIATE: Reinforce relay chain before contact is lost')
        
        return {
            'active': True,
            'severity': severity,
            'reason': reason,
            'area_of_interest': area_of_interest,
            'contact_continuity_risk': contact_risk,
            'recommended_actions': recommended_actions
        }
    
    elif has_tapping_detection and comms_degraded:
        severity = 'urgent' if comms_critical else 'warning'
        reason = 'Tapping sounds detected in Deep Squeeze. Communications to the area of interest are degrading.'
        area_of_interest = 'deep-squeeze'
        
        recommended_actions = [
            'Deploy additional relay-capable asset to Junction Chamber',
            'Monitor signal strength to Deep Squeeze',
            'Maintain comms corridor before advancing further',
            'Consider static relay placement at stable junction point'
        ]
        
        return {
            'active': True,
            'severity': severity,
            'reason': reason,
            'area_of_interest': area_of_interest,
            'contact_continuity_risk': contact_risk,
            'recommended_actions': recommended_actions
        }
    
    # No escalation if detections exist but comms are stable
    return {
        'active': False,
        'severity': 'none',
        'reason': None,
        'area_of_interest': None,
        'contact_continuity_risk': contact_risk,
        'recommended_actions': []
    }


def simulate_cave_rescue(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Simulate Cave Rescue scenario.
    
    **NOW USING SCENARIO ENGINE** - Data-driven simulation from database scenario.
    
    Scenario: cave-rescue-alpha-01
    - Loaded from database via MissionScenario model
    - Uses Migovec Primadona Digital Twin coordinates
    - Agent routes through entrance, passage, junction, chambers
    
    To modify scenario behavior:
    1. Edit data/scenarios/cave_rescue_scenario_alpha.json
    2. Run: python manage.py seed_mission_scenarios --file cave_rescue_scenario_alpha.json --overwrite
    3. No code changes needed
    """
    from .scenario_engine import generate_simulation_state_from_scenario
    
    try:
        # Use scenario engine to generate simulation state
        return generate_simulation_state_from_scenario(
            mission_id=mission_id,
            scenario_id='cave-rescue-alpha-01',
            elapsed_seconds=elapsed_seconds,
            speed_multiplier=speed_multiplier,
            mission_name=mission_name,
            status=status
        )
    except Exception as e:
        # Fallback to minimal state if scenario engine fails
        import traceback
        print(f"[Scenario Engine Error] {e}")
        traceback.print_exc()
        
        return {
            'mission': {
                'mission_id': mission_id,
                'name': mission_name,
                'use_case': 'cave-rescue',
                'status': status
            },
            'simulation_clock': {
                'started_at': started_at.isoformat() if started_at else None,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'speed_multiplier': speed_multiplier,
                'is_running': status == 'running'
            },
            'error': str(e),
            'agents': [],
            'sectors': [],
            'events': [],
        }


def simulate_cave_rescue_legacy(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    LEGACY: Original hardcoded cave rescue simulation.
    
    Kept for reference and fallback. Will be removed once scenario engine is stable.
    
    Models cave passage mapping, GPS denial, rock attenuation, relay chain.
    Timeline includes narrow passage navigation, SLAM drift, humidity readings.
    """
    # Timeline phases for Cave Rescue
    # 0-60s: Initial deployment and entrance mapping
    # 60-180s: Main tunnel exploration
    # 180-300s: Junction mapping and relay placement
    # 300-420s: Deep passage exploration with SLAM drift
    # 420s+: Audio detection and focused search
    
    # Agent states
    agents = []
    
    # Base station relay (always present at entrance)
    agents.append({
        'agent_id': 'base-station',
        'name': 'Cave Entrance Relay',
        'role': 'Base station relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 95,
        'location_label': 'Entrance',
        'position': {'x': 120, 'y': 240, 'z': 0},  # Entrance Chamber position
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Drone A: Scout with LiDAR/SLAM (deploys at 30s)
    if elapsed_seconds >= 30:
        drone_a_battery = max(5, 100 - ((elapsed_seconds - 30) / 22))  # Start from deployment
        drone_a_signal = max(35, 95 - ((elapsed_seconds - 30) / 8))  # Degrades with depth
        
        if elapsed_seconds < 60:
            drone_a_state = 'healthy'
            drone_a_loc = 'Entrance Chamber'
            drone_a_pos = {'x': 120 + ((elapsed_seconds - 30) * 0.3), 'y': 240, 'z': 2}
        elif elapsed_seconds < 180:
            drone_a_state = 'healthy'
            drone_a_loc = 'Main Tunnel'
            drone_a_pos = {'x': 200 + ((elapsed_seconds - 60) * 0.8), 'y': 240, 'z': 1}
        elif elapsed_seconds < 300:
            drone_a_state = 'healthy' if drone_a_signal > 50 else 'degraded'
            drone_a_loc = 'Junction Chamber'
            drone_a_pos = {'x': 600, 'y': 230, 'z': 0}
        else:
            drone_a_state = 'degraded'
            drone_a_loc = 'Deep Squeeze'
            drone_a_pos = {'x': 720, 'y': 240, 'z': -2}
        
        agents.append({
            'agent_id': 'drone-a',
            'name': 'Cave Scout Drone',
            'role': 'SLAM mapper',
            'state': drone_a_state,
            'battery_percent': int(drone_a_battery),
            'signal_strength': int(drone_a_signal),
            'location_label': drone_a_loc,
            'position': drone_a_pos,
            'sensors': ['LiDAR', 'IMU', 'RGB Camera'],
            'nfc_recovery_available': False
        })
    
    # Drone B: Micro mapper (may fail in narrow passage)
    if elapsed_seconds >= 90:
        if elapsed_seconds < 240:
            drone_b_battery = max(10, 100 - ((elapsed_seconds - 90) / 18))
            drone_b_signal = max(40, 80 - ((elapsed_seconds - 90) / 7))
            drone_b_state = 'healthy'
            drone_b_loc = 'Narrow Passage'
            drone_b_pos = {'x': 42 + ((elapsed_seconds - 90) * 0.15), 'y': 18, 'z': 0.5}
            nfc_available = False
        else:
            # Micro mapper lost in narrow passage
            drone_b_battery = 8
            drone_b_signal = 0
            drone_b_state = 'lost'
            drone_b_loc = 'Narrow Passage (last known)'
            drone_b_pos = {'x': 48, 'y': 20, 'z': 0.3}
            nfc_available = True
        
        agents.append({
            'agent_id': 'drone-b',
            'name': 'Micro Mapper',
            'role': 'Narrow passage scout',
            'state': drone_b_state,
            'battery_percent': int(drone_b_battery),
            'signal_strength': int(drone_b_signal),
            'location_label': drone_b_loc,
            'position': drone_b_pos,
            'sensors': ['Mini Camera', 'IMU'],
            'nfc_recovery_available': nfc_available
        })
    
    # Relay Drone: Lands at junction when needed
    if elapsed_seconds >= 180:
        if elapsed_seconds < 300:
            relay_battery = max(60, 100 - ((elapsed_seconds - 180) / 30))
            relay_state = 'healthy'
        else:
            relay_battery = max(20, 80 - ((elapsed_seconds - 300) / 40))
            relay_state = 'landed_relay'
        
        agents.append({
            'agent_id': 'relay-1',
            'name': 'Junction Relay Drone',
            'role': 'Communications relay',
            'state': relay_state,
            'battery_percent': int(relay_battery),
            'signal_strength': 85 if relay_state == 'landed_relay' else 75,
            'location_label': 'Junction Chamber',
            'position': {'x': 58, 'y': 25, 'z': 1.5},
            'sensors': [],
            'nfc_recovery_available': False
        })
    
    # Network state
    if elapsed_seconds < 180:
        mesh_health = max(75, 95 - (elapsed_seconds / 15))
        relay_chain = ['base-station', 'drone-a']
        packet_loss = min(10, elapsed_seconds / 20)
    elif elapsed_seconds < 300:
        mesh_health = max(65, 85 - ((elapsed_seconds - 180) / 12))
        relay_chain = ['base-station', 'relay-1', 'drone-a']
        packet_loss = min(15, 5 + ((elapsed_seconds - 180) / 15))
    else:
        mesh_health = max(55, 70 - ((elapsed_seconds - 300) / 10))
        relay_chain = ['base-station', 'relay-1', 'drone-a']
        packet_loss = min(25, 10 + ((elapsed_seconds - 300) / 12))
    
    network = {
        'base_signal_strength': int(max(50, 90 - (elapsed_seconds / 10))),
        'mesh_health': int(mesh_health),
        'relay_chain': relay_chain,
        'packet_loss_percent': int(packet_loss)
    }
    
    # Map state
    coverage = min(75, (elapsed_seconds / 6))
    confidence_base = 0.92 - (elapsed_seconds / 2000)  # SLAM drift
    
    mapped_sectors = []
    if elapsed_seconds >= 30:
        mapped_sectors.append('Entrance Chamber')
    if elapsed_seconds >= 90:
        mapped_sectors.append('Main Tunnel')
    if elapsed_seconds >= 180:
        mapped_sectors.append('Narrow Passage')
    if elapsed_seconds >= 240:
        mapped_sectors.append('Junction Chamber')
    if elapsed_seconds >= 360:
        mapped_sectors.append('Deep Squeeze')
    
    map_data = {
        'map_type': 'cave-passage-map',
        'coverage_percent': int(coverage),
        'confidence': max(0.72, confidence_base),
        'total_points': int(3000 + (elapsed_seconds * 25)),
        'new_points_generated': 800,
        'mapped_sectors': mapped_sectors,
        'blocked_sectors': ['Collapsed Section A'] if elapsed_seconds > 150 else [],
        'accessible_areas': [
            {'label': 'Main Tunnel', 'confidence': 0.88, 'risk': 'low'},
            {'label': 'Narrow Passage', 'confidence': 0.75, 'risk': 'medium'},
            {'label': 'Deep Squeeze', 'confidence': 0.62, 'risk': 'high'}
        ] if elapsed_seconds > 300 else []
    }
    
    # Sensor data
    thermal_anomalies = []
    audio_events = []
    device_signals = []
    environmental_readings = []
    
    # Determine current location for sensors (use drone_a location if deployed, otherwise entrance)
    if elapsed_seconds >= 30:
        current_sensor_location = next((a for a in agents if a['agent_id'] == 'drone-a'), None)
        sensor_loc = current_sensor_location['location_label'] if current_sensor_location else 'Entrance Chamber'
    else:
        sensor_loc = 'Entrance Chamber'
    
    # Humidity readings increase with depth
    base_humidity = 65 + (elapsed_seconds / 15)
    environmental_readings.append({
        'sensor_type': 'humidity',
        'value': min(95, base_humidity),
        'unit': '%',
        'location': sensor_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Temperature drops with depth
    base_temp = 18 - (elapsed_seconds / 100)
    environmental_readings.append({
        'sensor_type': 'temperature',
        'value': max(12, base_temp),
        'unit': 'degC',
        'location': sensor_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Audio events
    if elapsed_seconds >= 420:
        audio_events.append({
            'detected_at': format_time(420),
            'location': 'Deep Squeeze',
            'type': 'tapping-sound',
            'confidence': 0.71,
            'frequency_range': '200-800 Hz',
            'human_review_required': True,
            'status': 'investigating'
        })
    
    if elapsed_seconds >= 480:
        audio_events.append({
            'detected_at': format_time(480),
            'location': 'Deep Squeeze',
            'type': 'voice-like',
            'confidence': 0.64,
            'frequency_range': '300-3000 Hz',
            'human_review_required': True,
            'status': 'priority'
        })
    
    sensors = {
        'thermal_anomalies': thermal_anomalies,
        'audio_events': audio_events,
        'device_signals': device_signals,
        'environmental_readings': environmental_readings
    }
    
    # Mission events
    events = []
    
    if elapsed_seconds >= 0:
        events.append({
            'type': 'mission-start',
            'time': format_time(0),
            'title': 'Cave rescue mission started',
            'description': 'GPS-denied cave mapping and search initiated',
            'agent': None
        })
    
    if elapsed_seconds >= 30:
        events.append({
            'type': 'deployment',
            'time': format_time(30),
            'title': 'Cave Scout Drone deployed',
            'description': 'SLAM mapping active in Entrance Chamber',
            'agent': 'drone-a'
        })
    
    if elapsed_seconds >= 90:
        events.append({
            'type': 'deployment',
            'time': format_time(90),
            'title': 'Micro Mapper deployed',
            'description': 'Narrow passage exploration initiated',
            'agent': 'drone-b'
        })
    
    if elapsed_seconds >= 180:
        events.append({
            'type': 'relay-deployment',
            'time': format_time(180),
            'title': 'Junction relay deployed',
            'description': 'Communications relay positioned at Junction Chamber',
            'agent': 'relay-1',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 240:
        events.append({
            'type': 'asset-lost',
            'time': format_time(240),
            'title': 'Micro Mapper lost in narrow passage',
            'description': 'Last known position recorded, NFC recovery tag available',
            'agent': 'drone-b',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 300:
        events.append({
            'type': 'navigation-degraded',
            'time': format_time(300),
            'title': 'SLAM confidence degraded',
            'description': 'Position drift detected in deep passages, relay support active',
            'agent': 'drone-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 300:
        events.append({
            'type': 'relay-landed',
            'time': format_time(300),
            'title': 'Relay drone landed at junction',
            'description': 'Static relay mode active to maintain communications chain',
            'agent': 'relay-1',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 420:
        events.append({
            'type': 'detection',
            'time': format_time(420),
            'title': 'Audio event: tapping sound',
            'description': 'Rhythmic tapping detected in Deep Squeeze area',
            'agent': 'drone-a',
            'severity': 'high'
        })
    
    if elapsed_seconds >= 480:
        events.append({
            'type': 'detection',
            'time': format_time(480),
            'title': 'Audio event: voice-like signature',
            'description': 'Voice-like audio pattern detected, human review required',
            'agent': 'drone-a',
            'severity': 'critical'
        })
    
    # AI analysis
    if elapsed_seconds < 180:
        ai_summary = 'Cave passage mapping in progress. GPS-denied navigation active. No detections yet.'
        priority_findings = []
        human_review = False
        ai_confidence = 0.68
    elif elapsed_seconds < 300:
        ai_summary = 'Main tunnel and junction mapped. SLAM navigation stable. Micro mapper exploring narrow passage.'
        priority_findings = ['Junction relay deployed', 'Narrow passage accessible']
        human_review = False
        ai_confidence = 0.74
    elif elapsed_seconds < 420:
        ai_summary = 'Deep passage exploration active. SLAM drift detected. Relay chain maintaining communications. Micro mapper lost in narrow passage.'
        priority_findings = ['SLAM confidence degraded', 'Micro mapper NFC tag available', 'Deep Squeeze accessible']
        human_review = True
        ai_confidence = 0.66
    else:
        ai_summary = 'Audio signatures detected in Deep Squeeze. Possible survivor presence. Human review required for voice-like patterns.'
        priority_findings = [
            'Voice-like audio detected (confidence: 64%)',
            'Tapping sound detected (confidence: 71%)',
            'Deep Squeeze location identified',
            'SLAM drift may affect position accuracy'
        ]
        human_review = True
        ai_confidence = 0.72
    
    # Terrain reconstruction with progressive sector reveal
    # Critical: All agents start from entrance-chamber per claude_prompt09.md
    # No agent should spawn directly in Narrow Passage or Deep Squeeze
    terrain_sectors = [
        {
            'sector_id': 'entrance-chamber',
            'reveal_at': 0,
            'scan_rules': [
                {'time': 0, 'agent_id': 'base-station'},  # Base station knows entrance
                {'time': 30, 'agent_id': 'drone-a'},  # Scout starts here
                {'time': 90, 'agent_id': 'drone-b'},  # Micro mapper starts here
                {'time': 180, 'agent_id': 'relay-1'},  # Relay starts here
            ]
        },
        {
            'sector_id': 'main-tunnel',
            'reveal_at': 60,
            'scan_rules': [
                {'time': 60, 'agent_id': 'drone-a'},  # Scout discovers and maps main tunnel
                {'time': 120, 'agent_id': 'drone-b'},  # Micro mapper follows mapped route
                {'time': 180, 'agent_id': 'relay-1'},  # Relay travels through
            ]
        },
        {
            'sector_id': 'narrow-passage',
            'reveal_at': 120,
            'scan_rules': [
                {'time': 120, 'agent_id': 'drone-a'},  # Scout detects narrow passage
                {'time': 180, 'agent_id': 'drone-b'},  # Micro mapper explores (narrow_passage_navigation capability)
            ]
        },
        {
            'sector_id': 'junction-chamber',
            'reveal_at': 180,
            'scan_rules': [
                {'time': 180, 'agent_id': 'drone-a'},  # Scout discovers junction
                {'time': 210, 'agent_id': 'relay-1'},  # Relay positioned here
                {'time': 240, 'agent_id': 'drone-a'},  # Scout continues mapping
            ]
        },
        {
            'sector_id': 'deep-squeeze',
            'reveal_at': 300,
            'scan_rules': [
                {'time': 300, 'agent_id': 'drone-a'},  # Scout enters deep passage
                {'time': 360, 'agent_id': 'drone-a'},  # Scout deep scan
                {'time': 420, 'agent_id': 'drone-a'},  # Scout detection scan
            ]
        },
    ]
    
    terrain_reconstruction = calculate_terrain_reconstruction(
        terrain_sectors,
        agents,
        elapsed_seconds
    )
    
    # Environmental sensors - O2 and CO2 for cave atmosphere monitoring
    # O2 sensor appears at 90s when micro mapper activates
    if elapsed_seconds >= 90:
        o2_value = max(19.5, 20.9 - (elapsed_seconds / 1200))  # Slowly decreasing in cave
        o2_status = 'normal' if o2_value >= 19.5 else 'watch' if o2_value >= 19.0 else 'warning'
        environmental_readings.append({
            'sensor_type': 'oxygen',
            'display_name': 'O2',
            'value': round(o2_value, 1),
            'unit': '%',
            'status': o2_status,
            'location_label': drone_a_loc,
            'confidence': 0.85,
            'detected_at': 90,
            'timestamp': format_time(elapsed_seconds)
        })
    
    # CO2 sensor appears at 120s
    if elapsed_seconds >= 120:
        # Cave CO2 can build up but typically lower than collapsed building
        co2_value = min(1200, 380 + (elapsed_seconds * 1.2))
        co2_status = 'normal' if co2_value <= 800 else 'watch' if co2_value <= 1000 else 'warning'
        environmental_readings.append({
            'sensor_type': 'carbon_dioxide',
            'display_name': 'CO2',
            'value': int(co2_value),
            'unit': 'ppm',
            'status': co2_status,
            'location_label': drone_a_loc,
            'confidence': 0.78,
            'detected_at': 120,
            'timestamp': format_time(elapsed_seconds)
        })
    
    ai_analysis = {
        'summary': ai_summary,
        'priority_findings': priority_findings,
        'human_review_required': human_review,
        'confidence': ai_confidence
    }
    
    # Media feeds - simulated camera returns from cave exploration
    media_feeds = []
    
    # Cave Scout Drone: Low-light cave passage frames
    if elapsed_seconds >= 45:
        scout_agent = next((a for a in agents if a['agent_id'] == 'drone-a'), None)
        if scout_agent:
            frame_status = 'live' if scout_agent['signal_strength'] > 60 else 'degraded' if scout_agent['signal_strength'] > 40 else 'delayed'
            frame_conf = min(88, 55 + scout_agent['signal_strength'] / 2.5)
            
            # Moisture/humidity may degrade visibility
            if elapsed_seconds >= 180:
                annotations = ['low-light imaging', 'high humidity', 'moisture on lens']
                description = f'Cave passage imaging affected by moisture. Location: {scout_agent["location_label"]}.'
                frame_conf = max(45, frame_conf - 20)
            else:
                annotations = ['low-light imaging', 'passage mapping']
                description = f'Low-light cave passage imaging from {scout_agent["location_label"]}.'
            
            media_feeds.append({
                'frame_id': f'cave-scout-{int(elapsed_seconds)}',
                'agent_id': 'drone-a',
                'agent_name': 'Cave Scout Drone',
                'sensor_type': 'low_light_camera',
                'frame_type': 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': scout_agent['signal_strength'],
                'confidence': int(frame_conf),
                'location_label': scout_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Micro Mapper: Close-up stills from Narrow Passage
    if elapsed_seconds >= 105 and elapsed_seconds < 240:
        micro_agent = next((a for a in agents if a['agent_id'] == 'drone-b'), None)
        if micro_agent:
            media_feeds.append({
                'frame_id': f'micro-mapper-{int(elapsed_seconds)}',
                'agent_id': 'drone-b',
                'agent_name': 'Micro Mapper',
                'sensor_type': 'inspection_camera',
                'frame_type': 'still',
                'status': 'live',
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': micro_agent['signal_strength'],
                'confidence': 76,
                'location_label': micro_agent['location_label'],
                'annotations': ['narrow passage', 'close-up imaging', 'tight squeeze navigation'],
                'description': f'Close-up imaging from narrow passage. Agent: {micro_agent["name"]}.'
            })
    
    # Micro Mapper: Last good frame before failure
    if elapsed_seconds >= 240:
        # Micro mapper lost - show last good frame
        media_feeds.append({
            'frame_id': 'micro-mapper-last-good',
            'agent_id': 'drone-b',
            'agent_name': 'Micro Mapper',
            'sensor_type': 'inspection_camera',
            'frame_type': 'last_good_frame',
            'status': 'last_good_frame',
            'mission_time': format_time(240),
            'signal_quality': 0,
            'confidence': 68,
            'location_label': 'Narrow Passage (last known)',
            'annotations': ['last good frame', 'agent lost', 'NFC recovery available'],
            'description': 'Last frame before signal loss in narrow passage. NFC recovery tag available.'
        })
    
    # Audio event paired with scout frame
    if elapsed_seconds >= 420:
        scout_agent = next((a for a in agents if a['agent_id'] == 'drone-a'), None)
        if scout_agent:
            frame_status = 'ai_flagged' if elapsed_seconds >= 480 else 'human_review_required'
            annotations_base = ['audio event detected', 'deep squeeze location']
            
            if elapsed_seconds >= 480:
                annotations = annotations_base + ['voice-like signature', 'priority review']
                description = 'Frame captured during voice-like audio event. Human review required.'
                conf = 64
            else:
                annotations = annotations_base + ['tapping sound detected']
                description = 'Frame captured during tapping audio event. Investigating.'
                conf = 71
            
            media_feeds.append({
                'frame_id': f'audio-event-frame-{int(elapsed_seconds)}',
                'agent_id': 'drone-a',
                'agent_name': 'Cave Scout Drone',
                'sensor_type': 'low_light_camera',
                'frame_type': 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': scout_agent['signal_strength'],
                'confidence': conf,
                'location_label': 'Deep Squeeze',
                'annotations': annotations,
                'description': description
            })
    
    # Navigation model for GPS-denied cave environment
    # Uses local 3D coordinate system with mission north reference
    origin_position = {'x': 120, 'y': 240, 'z': 0}  # Entrance Chamber
    
    # Calculate per-agent navigation intelligence
    # Add distance, bearing, and depth/elevation labels to each agent
    for agent in agents:
        agent_pos = agent.get('position', origin_position)
        
        # 2D and 3D distances from origin
        distance_2d = calculate_distance_2d(origin_position, agent_pos)
        distance_3d = calculate_distance_3d(origin_position, agent_pos)
        
        # Bearing from origin (only if agent has moved significantly)
        if distance_2d > 1.0:
            bearing_deg = calculate_bearing_degrees(origin_position, agent_pos)
            bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        else:
            bearing_deg = 0
            bearing_cardinal = 'N'
        
        # Elevation and depth
        elevation_m, depth_m = calculate_elevation_depth(agent_pos.get('z', 0))
        vertical_label = calculate_vertical_profile_label(agent_pos.get('z', 0), context='cave')
        depth_elevation_label = format_depth_elevation_label(agent_pos.get('z', 0), use_arrows=True)
        
        # Add navigation intelligence fields
        agent['navigation'] = {
            'distance_from_origin_m': round(distance_2d, 1),
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1) if distance_2d > 1 else None,
            'bearing_from_origin_cardinal': bearing_cardinal if distance_2d > 1 else None,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_offset_from_origin_m': round(elevation_m, 1),
            'vertical_profile_label': vertical_label,
            'depth_elevation_label': depth_elevation_label
        }
    compass_confidence, compass_reliability, compass_reason = calculate_compass_confidence(
        environment_type='cave',
        distance_from_origin_m=0,
        has_metal_nearby=False,  # Natural cave system
        has_electrical_interference=False
    )
    
    navigation_model = {
        'coordinate_system': 'local_mission_3d_grid',
        'origin_sector_id': 'entrance',
        'origin_label': 'Cave Entrance',
        'origin_position': origin_position,
        'units': 'metres',
        'horizontal_units': 'metres',
        'vertical_units': 'metres',
        'svg_unit_to_metres': 0.25,
        'grid_square_metres': 5,
        'z_reference': 'origin_relative',
        'z_positive_direction': 'up',
        'depth_positive_direction': 'down',
        'north_reference': 'mission_north',
        'bearing_reference': 'magnetic_simulated',
        'magnetic_declination_deg': 0,
        'bearing_confidence': round(compass_confidence, 2),
        'bearing_reliability': compass_reliability,
        'bearing_reliability_reason': compass_reason
    }
    
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': 'cave-rescue',
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'navigation_model': navigation_model,
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction,
        'media_feeds': media_feeds,
        'mission_escalation': calculate_mission_escalation_cave_rescue(
            elapsed_seconds, mesh_health, packet_loss, audio_events
        )
    }


def simulate_flooded_structure(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Simulate Flooded Structure scenario.
    
    **NOW USING SCENARIO ENGINE** - Data-driven simulation from database scenario.
    
    Scenario: flooded-structure-alpha-01
    - Loaded from database via MissionScenario model
    - Uses Liberty Cargo Vessel Digital Twin coordinates
    - ROV routes through hull breach, corridors, cargo holds, engine room
    
    To modify scenario behavior:
    1. Edit data/scenarios/flooded_structure_scenario_alpha.json
    2. Run: python manage.py seed_mission_scenarios --file flooded_structure_scenario_alpha.json --overwrite
    3. No code changes needed
    """
    from .scenario_engine import generate_simulation_state_from_scenario
    
    try:
        # Use scenario engine to generate simulation state
        return generate_simulation_state_from_scenario(
            mission_id=mission_id,
            scenario_id='flooded-structure-alpha-01',
            elapsed_seconds=elapsed_seconds,
            speed_multiplier=speed_multiplier,
            mission_name=mission_name,
            status=status
        )
    except Exception as e:
        # Fallback to minimal state if scenario engine fails
        import traceback
        print(f"[Scenario Engine Error] {e}")
        traceback.print_exc()
        
        return {
            'mission': {
                'mission_id': mission_id,
                'name': mission_name,
                'use_case': 'flooded-structure',
                'status': status
            },
            'simulation_clock': {
                'started_at': started_at.isoformat() if started_at else None,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'speed_multiplier': speed_multiplier,
                'is_running': status == 'running'
            },
            'error': str(e),
            'agents': [],
            'sectors': [],
            'events': [],
        }


def simulate_flooded_structure_legacy(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    LEGACY: Original hardcoded flooded structure simulation.
    
    Kept for reference and fallback. Will be removed once scenario engine is stable.
    
    Models amphibious inspection, water depth mapping, submerged obstructions.
    Timeline includes signal degradation through water, environmental hazards.
    """
    # Timeline phases for Flooded Structure
    # 0-60s: Surface deployment and initial sonar scan
    # 60-180s: Shallow water exploration
    # 180-300s: Deep water obstruction mapping
    # 300-420s: Environmental hazard detection
    # 420s+: Above-waterline thermal detection
    
    # Agent states
    agents = []
    
    # Surface relay node (always present at entry)
    agents.append({
        'agent_id': 'surface-relay',
        'name': 'Surface Relay Station',
        'role': 'Water-to-air relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 90,
        'location_label': 'Entry platform',
        'position': {'x': 125, 'y': 90, 'z': 0},  # Entry Pool position
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Amphibious Unit A: Main explorer (deploys at 30s)
    if elapsed_seconds >= 30:
        amp_a_battery = max(8, 100 - ((elapsed_seconds - 30) / 20))  # Start from deployment
        amp_a_signal = max(25, 85 - ((elapsed_seconds - 30) / 6))  # Water + concrete attenuation
        
        if elapsed_seconds < 60:
            amp_a_state = 'healthy'
            amp_a_loc = 'Entry Pool (surface)'
            amp_a_depth = 0.5
            amp_a_pos = {'x': 125, 'y': 90, 'z': -0.5}
        elif elapsed_seconds < 180:
            amp_a_state = 'healthy'
            amp_a_loc = 'Flooded Corridor'
            amp_a_depth = 2.8
            amp_a_pos = {'x': 320, 'y': 125, 'z': -2.8}
        elif elapsed_seconds < 300:
            amp_a_state = 'degraded'  # Mobility issues
            amp_a_loc = 'Plant Room'
            amp_a_depth = 3.5
            amp_a_pos = {'x': 515, 'y': 125, 'z': -3.5}
        else:
            amp_a_state = 'degraded'
            amp_a_loc = 'Submerged Zone'
            amp_a_depth = 4.5
            amp_a_pos = {'x': 405, 'y': 310, 'z': -4.5}
        
        agents.append({
            'agent_id': 'amp-unit-a',
            'name': 'Amphibious Explorer',
            'role': 'Underwater mapping',
            'state': amp_a_state,
            'battery_percent': int(amp_a_battery),
            'signal_strength': int(amp_a_signal),
            'location_label': f'{amp_a_loc} (depth: {amp_a_depth}m)',
            'position': amp_a_pos,
            'sensors': ['Sonar', 'Pressure', 'Water Quality', 'Camera'],
            'nfc_recovery_available': False
        })
    
    # Drone B: Above-waterline thermal scout
    if elapsed_seconds >= 120:
        drone_b_battery = max(15, 100 - ((elapsed_seconds - 120) / 25))
        drone_b_signal = max(45, 75 - ((elapsed_seconds - 120) / 10))
        drone_b_state = 'healthy'
        
        if elapsed_seconds < 300:
            drone_b_loc = 'Above waterline - upper floor'
        else:
            drone_b_loc = 'Elevated dry area'
        
        agents.append({
            'agent_id': 'drone-b',
            'name': 'Aerial Thermal Scout',
            'role': 'Above-waterline detection',
            'state': drone_b_state,
            'battery_percent': int(drone_b_battery),
            'signal_strength': int(drone_b_signal),
            'location_label': drone_b_loc,
            'position': {'x': 30, 'y': 20, 'z': 3.5},
            'sensors': ['Thermal', 'RGB Camera'],
            'nfc_recovery_available': False
        })
    
    # Environmental sensor package
    if elapsed_seconds >= 180:
        agents.append({
            'agent_id': 'env-sensor-1',
            'name': 'Water Quality Sensor',
            'role': 'Environmental monitoring',
            'state': 'active',
            'battery_percent': 95,
            'signal_strength': 60,
            'location_label': 'Submerged Corridor',
            'position': {'x': 28, 'y': 16, 'z': -2.5},
            'sensors': ['pH', 'Conductivity', 'Temperature', 'Pressure'],
            'nfc_recovery_available': False
        })
    
    # Network state - heavily degraded by water and concrete
    if elapsed_seconds < 180:
        mesh_health = max(60, 85 - (elapsed_seconds / 10))
        packet_loss = min(20, elapsed_seconds / 10)
    elif elapsed_seconds < 300:
        mesh_health = max(45, 70 - ((elapsed_seconds - 180) / 8))
        packet_loss = min(35, 10 + ((elapsed_seconds - 180) / 6))
    else:
        mesh_health = max(35, 55 - ((elapsed_seconds - 300) / 10))
        packet_loss = min(45, 20 + ((elapsed_seconds - 300) / 8))
    
    relay_chain = ['surface-relay', 'amp-unit-a']
    if len(agents) > 2:
        relay_chain.insert(1, 'drone-b')
    
    network = {
        'base_signal_strength': int(max(40, 85 - (elapsed_seconds / 8))),
        'mesh_health': int(mesh_health),
        'relay_chain': relay_chain,
        'packet_loss_percent': int(packet_loss)
    }
    
    # Map state
    coverage = min(65, (elapsed_seconds / 8))
    confidence = max(0.68, 0.88 - (elapsed_seconds / 1500))
    
    mapped_sectors = []
    if elapsed_seconds >= 30:
        mapped_sectors.append('Entry Pool')
    if elapsed_seconds >= 90:
        mapped_sectors.append('Submerged Corridor')
    if elapsed_seconds >= 180:
        mapped_sectors.append('Shallow Room A')
    if elapsed_seconds >= 240:
        mapped_sectors.append('Deep Chamber')
    if elapsed_seconds >= 360:
        mapped_sectors.append('Elevated Dry Area')
    
    blocked_sectors = []
    if elapsed_seconds >= 150:
        blocked_sectors.append('Collapsed East Wing')
    if elapsed_seconds >= 270:
        blocked_sectors.append('Sealed Stairwell')
    
    map_data = {
        'map_type': 'flood-depth-map',
        'coverage_percent': int(coverage),
        'confidence': confidence,
        'total_points': int(2500 + (elapsed_seconds * 18)),
        'new_points_generated': 600,
        'mapped_sectors': mapped_sectors,
        'blocked_sectors': blocked_sectors,
        'accessible_areas': [
            {'label': 'Submerged Corridor', 'confidence': 0.82, 'risk': 'medium'},
            {'label': 'Deep Chamber', 'confidence': 0.71, 'risk': 'high'},
            {'label': 'Elevated Dry Area', 'confidence': 0.76, 'risk': 'low'}
        ] if elapsed_seconds > 240 else []
    }
    
    # Sensor data
    thermal_anomalies = []
    audio_events = []
    device_signals = []
    environmental_readings = []
    
    # Determine current location for sensors (use amp unit location if deployed, otherwise entry)
    if elapsed_seconds >= 30:
        amp_unit = next((a for a in agents if a['agent_id'] == 'amp-unit-a'), None)
        if amp_unit:
            # Extract location without depth suffix
            amp_loc = amp_unit['location_label'].split(' (depth:')[0] if '(depth:' in amp_unit['location_label'] else amp_unit['location_label']
        else:
            amp_loc = 'Entry Pool (surface)'
    else:
        amp_loc = 'Entry Pool (surface)'
    
    # Water depth/pressure readings
    current_depth = min(4.5, elapsed_seconds / 80)
    environmental_readings.append({
        'sensor_type': 'water_depth',
        'value': round(current_depth, 1),
        'unit': 'm',
        'location': amp_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Water temperature
    water_temp = max(8, 14 - (elapsed_seconds / 200))
    environmental_readings.append({
        'sensor_type': 'water_temperature',
        'value': round(water_temp, 1),
        'unit': 'degC',
        'location': amp_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Contamination warning
    if elapsed_seconds >= 300:
        environmental_readings.append({
            'sensor_type': 'water_quality',
            'value': 6.2,
            'unit': 'pH',
            'location': 'Deep Chamber',
            'timestamp': format_time(300)
        })
    
    # Electrical hazard risk
    if elapsed_seconds >= 330:
        environmental_readings.append({
            'sensor_type': 'electrical_risk',
            'value': 1,  # Boolean-like
            'unit': 'alert',
            'location': 'Deep Chamber',
            'timestamp': format_time(330)
        })
    
    # Thermal anomaly above waterline
    if elapsed_seconds >= 420:
        thermal_anomalies.append({
            'detected_at': format_time(420),
            'location': 'Elevated dry area',
            'temperature_delta': 8.5,
            'confidence': 0.78,
            'human_review_required': True,
            'status': 'investigating'
        })
    
    sensors = {
        'thermal_anomalies': thermal_anomalies,
        'audio_events': audio_events,
        'device_signals': device_signals,
        'environmental_readings': environmental_readings
    }
    
    # Mission events
    events = []
    
    if elapsed_seconds >= 0:
        events.append({
            'type': 'mission-start',
            'time': format_time(0),
            'title': 'Flooded structure inspection started',
            'description': 'Amphibious mapping and hazard detection initiated',
            'agent': None
        })
    
    if elapsed_seconds >= 30:
        events.append({
            'type': 'deployment',
            'time': format_time(30),
            'title': 'Amphibious unit deployed',
            'description': 'Surface sonar scan initiated',
            'agent': 'amp-unit-a'
        })
    
    if elapsed_seconds >= 120:
        events.append({
            'type': 'deployment',
            'time': format_time(120),
            'title': 'Aerial thermal scout deployed',
            'description': 'Above-waterline detection active',
            'agent': 'drone-b'
        })
    
    if elapsed_seconds >= 180:
        events.append({
            'type': 'sensor-deployed',
            'time': format_time(180),
            'title': 'Environmental sensor deployed',
            'description': 'Water quality monitoring active in Submerged Corridor',
            'agent': 'env-sensor-1'
        })
    
    if elapsed_seconds >= 240:
        events.append({
            'type': 'obstruction-detected',
            'time': format_time(240),
            'title': 'Submerged obstruction detected',
            'description': 'Large debris blocking Deep Chamber passage',
            'agent': 'amp-unit-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 300:
        events.append({
            'type': 'hazard-alert',
            'time': format_time(300),
            'title': 'Water quality alert',
            'description': 'Abnormal pH detected, possible contamination',
            'agent': 'env-sensor-1',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 330:
        events.append({
            'type': 'hazard-alert',
            'time': format_time(330),
            'title': 'Electrical hazard risk',
            'description': 'Submerged electrical equipment detected in Deep Chamber',
            'agent': 'amp-unit-a',
            'severity': 'high'
        })
    
    if elapsed_seconds >= 360:
        events.append({
            'type': 'mobility-degraded',
            'time': format_time(360),
            'title': 'Amphibious unit mobility degraded',
            'description': 'Buoyancy control and propulsion efficiency reduced',
            'agent': 'amp-unit-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 420:
        events.append({
            'type': 'detection',
            'time': format_time(420),
            'title': 'Thermal anomaly detected above waterline',
            'description': 'Elevated temperature signature in dry elevated area',
            'agent': 'drone-b',
            'severity': 'high'
        })
    
    # AI analysis
    if elapsed_seconds < 180:
        ai_summary = 'Flooded structure mapping in progress. Surface and shallow water zones accessible. No hazards detected yet.'
        priority_findings = []
        human_review = False
        ai_confidence = 0.71
    elif elapsed_seconds < 300:
        ai_summary = 'Deep water exploration active. Submerged obstructions mapped. Environmental sensor deployed.'
        priority_findings = ['Submerged obstruction detected', 'Environmental monitoring active']
        human_review = False
        ai_confidence = 0.75
    elif elapsed_seconds < 420:
        ai_summary = 'Multiple hazards detected: contaminated water, electrical risk, mobility degradation. Deep Chamber presents high risk.'
        priority_findings = [
            'Electrical hazard in Deep Chamber',
            'Water quality contamination detected',
            'Amphibious unit mobility degraded',
            'Submerged obstruction blocking passage'
        ]
        human_review = True
        ai_confidence = 0.68
    else:
        ai_summary = 'Thermal anomaly detected above waterline. Possible survivor or heat source in elevated dry area. Environmental hazards mapped in submerged zones.'
        priority_findings = [
            'Thermal anomaly above waterline (confidence: 78%)',
            'Elevated dry area accessible',
            'Electrical hazard zone identified',
            'Contaminated water in Deep Chamber'
        ]
        human_review = True
        ai_confidence = 0.73
    
    # Terrain reconstruction with progressive sector reveal
    # All agents start from entry-pool (surface)
    terrain_sectors = [
        {
            'sector_id': 'entry-pool',
            'reveal_at': 0,
            'scan_rules': [
                {'time': 0, 'agent_id': 'surface-relay'},  # Surface relay knows entry
                {'time': 30, 'agent_id': 'amp-unit-a'},  # Amphibious unit starts here
                {'time': 120, 'agent_id': 'drone-b'},  # Aerial scout starts here
            ]
        },
        {
            'sector_id': 'flooded-corridor',
            'reveal_at': 60,
            'scan_rules': [
                {'time': 60, 'agent_id': 'amp-unit-a'},  # Amphibious unit discovers corridor
                {'time': 120, 'agent_id': 'amp-unit-a'},  # Amphibious unit maps corridor
            ]
        },
        {
            'sector_id': 'plant-room',
            'reveal_at': 120,
            'scan_rules': [
                {'time': 120, 'agent_id': 'amp-unit-a'},  # Amphibious unit discovers plant room
                {'time': 240, 'agent_id': 'drone-b'},  # Aerial scout scans from above
            ]
        },
        {
            'sector_id': 'submerged-zone',
            'reveal_at': 180,
            'scan_rules': [
                {'time': 180, 'agent_id': 'amp-unit-a'},  # Amphibious unit deep dive
                {'time': 240, 'agent_id': 'env-sensor-1'},  # Water quality sensor deployed
            ],
            'is_hazardous': True,
            'hazard_detected_at': 240
        },
    ]
    
    terrain_reconstruction = calculate_terrain_reconstruction(
        terrain_sectors,
        agents,
        elapsed_seconds
    )
    
    ai_analysis = {
        'summary': ai_summary,
        'priority_findings': priority_findings,
        'human_review_required': human_review,
        'confidence': ai_confidence
    }
    
    # Media feeds - simulated underwater/amphibious imaging
    media_feeds = []
    
    # Amphibious Unit: Underwater/waterline camera
    if elapsed_seconds >= 45:
        amp_agent = next((a for a in agents if a['agent_id'] == 'amp-unit-a'), None)
        if amp_agent:
            # Water turbidity degrades frame confidence
            depth = amp_agent['location_label'].split('(depth:')[1].split('m)')[0].strip() if '(depth:' in amp_agent['location_label'] else '0.5'
            depth_val = float(depth)
            
            if depth_val > 2.5:
                frame_status = 'degraded'
                annotations = ['underwater imaging', 'high turbidity', 'low visibility']
                description = f'Underwater imaging severely degraded by turbidity at {depth_val}m depth.'
                conf = max(35, 75 - int(depth_val * 8))
            elif depth_val > 1.0:
                frame_status = 'degraded'
                annotations = ['underwater imaging', 'moderate turbidity']
                description = f'Underwater imaging at {depth_val}m depth. Moderate turbidity.'
                conf = max(50, 80 - int(depth_val * 5))
            else:
                frame_status = 'live'
                annotations = ['waterline imaging', 'surface conditions']
                description = f'Surface/waterline imaging. Depth: {depth_val}m.'
                conf = 82
            
            media_feeds.append({
                'frame_id': f'amp-underwater-{int(elapsed_seconds)}',
                'agent_id': 'amp-unit-a',
                'agent_name': 'Amphibious Explorer',
                'sensor_type': 'underwater_camera',
                'frame_type': 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': amp_agent['signal_strength'],
                'confidence': conf,
                'location_label': amp_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Aerial Scout: Above-waterline thermal detection
    if elapsed_seconds >= 135:
        aerial_agent = next((a for a in agents if a['agent_id'] == 'drone-b'), None)
        if aerial_agent:
            # Thermal anomaly above waterline creates flagged frame
            if elapsed_seconds >= 240:
                frame_status = 'ai_flagged'
                annotations = ['thermal anomaly', 'above waterline', 'electrical hazard possible']
                description = 'Thermal anomaly detected above waterline. Possible electrical hazard.'
                conf = 74
            else:
                frame_status = 'live'
                annotations = ['above waterline', 'thermal scan']
                description = 'Thermal imaging of elevated dry areas.'
                conf = 81
            
            media_feeds.append({
                'frame_id': f'aerial-thermal-{int(elapsed_seconds)}',
                'agent_id': 'drone-b',
                'agent_name': 'Aerial Thermal Scout',
                'sensor_type': 'thermal_camera',
                'frame_type': 'thermal' if elapsed_seconds >= 240 else 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': aerial_agent['signal_strength'],
                'confidence': conf,
                'location_label': aerial_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Submerged obstruction AI-annotated frame
    if elapsed_seconds >= 180:
        amp_agent = next((a for a in agents if a['agent_id'] == 'amp-unit-a'), None)
        if amp_agent:
            media_feeds.append({
                'frame_id': f'obstruction-detected-{int(elapsed_seconds)}',
                'agent_id': 'amp-unit-a',
                'agent_name': 'Amphibious Explorer',
                'sensor_type': 'underwater_camera',
                'frame_type': 'still',
                'status': 'ai_flagged',
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': amp_agent['signal_strength'],
                'confidence': 68,
                'location_label': 'Flooded Corridor',
                'annotations': ['submerged obstruction', 'AI detected', 'navigation hazard'],
                'description': 'AI-detected submerged obstruction blocking corridor passage.'
            })
    
    # Environmental sensor at 195s (already in timeline)
    if elapsed_seconds >= 195:
        media_feeds.append({
            'frame_id': 'env-sensor-frame',
            'agent_id': 'env-sensor-1',
            'agent_name': 'Water Quality Sensor',
            'sensor_type': 'hazard_camera',
            'frame_type': 'still',
            'status': 'live',
            'mission_time': format_time(elapsed_seconds),
            'signal_quality': 60,
            'confidence': 85,
            'location_label': 'Flooded Corridor',
            'annotations': ['water quality monitoring', 'pH sensor active'],
            'description': 'Environmental sensor package monitoring water conditions.'
        })
    
    # Navigation model for flooded structure environment
    # Uses local 3D coordinate system with water depth references
    origin_position = {'x': 125, 'y': 90, 'z': 0}  # Entry Pool surface
    
    # Calculate per-agent navigation intelligence
    # Add distance, bearing, and depth/elevation labels to each agent
    for agent in agents:
        agent_pos = agent.get('position', origin_position)
        
        # 2D and 3D distances from origin
        distance_2d = calculate_distance_2d(origin_position, agent_pos)
        distance_3d = calculate_distance_3d(origin_position, agent_pos)
        
        # Bearing from origin (only if agent has moved significantly)
        if distance_2d > 1.0:
            bearing_deg = calculate_bearing_degrees(origin_position, agent_pos)
            bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        else:
            bearing_deg = 0
            bearing_cardinal = 'N'
        
        # Elevation and depth (water depth context)
        elevation_m, depth_m = calculate_elevation_depth(agent_pos.get('z', 0))
        vertical_label = calculate_vertical_profile_label(agent_pos.get('z', 0), context='water')
        depth_elevation_label = format_depth_elevation_label(agent_pos.get('z', 0), use_arrows=True)
        
        # Add navigation intelligence fields
        agent['navigation'] = {
            'distance_from_origin_m': round(distance_2d, 1),
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1) if distance_2d > 1 else None,
            'bearing_from_origin_cardinal': bearing_cardinal if distance_2d > 1 else None,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_offset_from_origin_m': round(elevation_m, 1),
            'vertical_profile_label': vertical_label,
            'depth_elevation_label': depth_elevation_label
        }
    compass_confidence, compass_reliability, compass_reason = calculate_compass_confidence(
        environment_type='flooded_building',
        distance_from_origin_m=0,
        has_metal_nearby=True,  # Metal structures in building
        has_electrical_interference=False
    )
    
    navigation_model = {
        'coordinate_system': 'local_mission_3d_grid',
        'origin_sector_id': 'entry_pool',
        'origin_label': 'Entry Pool (Surface)',
        'origin_position': origin_position,
        'units': 'metres',
        'horizontal_units': 'metres',
        'vertical_units': 'metres',
        'svg_unit_to_metres': 0.25,
        'grid_square_metres': 5,
        'z_reference': 'water_surface',
        'z_positive_direction': 'up',
        'depth_positive_direction': 'down',
        'north_reference': 'mission_north',
        'bearing_reference': 'magnetic_simulated',
        'magnetic_declination_deg': 0,
        'bearing_confidence': round(compass_confidence, 2),
        'bearing_reliability': compass_reliability,
        'bearing_reliability_reason': compass_reason
    }
    
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': 'flooded-structure',
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'navigation_model': navigation_model,
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction,
        'media_feeds': media_feeds
    }


def simulate_industrial_inspection(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Simulate Industrial Inspection scenario.
    
    **NOW USING SCENARIO ENGINE** - Data-driven simulation from database scenario.
    
    Scenario: industrial-inspection-alpha-01
    - Loaded from database via MissionScenario model
    - Uses Industrial Confined Space Digital Twin coordinates
    - Drone routes through access shaft, utility corridors, equipment rooms
    
    To modify scenario behavior:
    1. Edit data/scenarios/industrial_inspection_scenario_alpha.json
    2. Run: python manage.py seed_mission_scenarios --file industrial_inspection_scenario_alpha.json --overwrite
    3. No code changes needed
    """
    from .scenario_engine import generate_simulation_state_from_scenario
    
    try:
        # Use scenario engine to generate simulation state
        return generate_simulation_state_from_scenario(
            mission_id=mission_id,
            scenario_id='industrial-inspection-alpha-01',
            elapsed_seconds=elapsed_seconds,
            speed_multiplier=speed_multiplier,
            mission_name=mission_name,
            status=status
        )
    except Exception as e:
        # Fallback to minimal state if scenario engine fails
        import traceback
        print(f"[Scenario Engine Error] {e}")
        traceback.print_exc()
        
        return {
            'mission': {
                'mission_id': mission_id,
                'name': mission_name,
                'use_case': 'industrial-inspection',
                'status': status
            },
            'simulation_clock': {
                'started_at': started_at.isoformat() if started_at else None,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'speed_multiplier': speed_multiplier,
                'is_running': status == 'running'
            },
            'error': str(e),
            'agents': [],
            'sectors': [],
            'events': [],
        }


def simulate_industrial_inspection_legacy(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    LEGACY: Original hardcoded industrial inspection simulation.
    
    Kept for reference and fallback. Will be removed once scenario engine is stable.
    
    Models confined space inspection, thermal hotspots, gas detection, defect identification.
    Timeline includes equipment inspection, hazard detection, structural integrity checks.
    """
    # Timeline phases for Industrial Inspection
    # 0-60s: Initial deployment and Plant Room scan
    # 60-180s: Pipe Gallery inspection
    # 180-300s: Tank Interior inspection with reflective surfaces
    # 300-420s: Duct Section inspection with EMI
    # 420s+: Control Cabinet inspection and defect summary
    
    # Agent states
    agents = []
    
    # Base station (always present at entry)
    agents.append({
        'agent_id': 'base-station',
        'name': 'Industrial Base Station',
        'role': 'Command and relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 95,
        'location_label': 'Entry point',
        'position': {'x': 110, 'y': 90, 'z': 0},  # Entry Point sector position
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Inspection Drone A: Primary inspector (deploys at 30s)
    if elapsed_seconds >= 30:
        drone_a_battery = max(10, 100 - ((elapsed_seconds - 30) / 23))
        drone_a_signal = max(50, 90 - ((elapsed_seconds - 30) / 12))  # EMI interference
        
        if elapsed_seconds < 60:
            drone_a_state = 'healthy'
            drone_a_loc = 'Entry Point'
            drone_a_pos = {'x': 110, 'y': 90, 'z': 2.5}
        elif elapsed_seconds < 120:
            drone_a_state = 'healthy'
            drone_a_loc = 'Plant Room'
            drone_a_pos = {'x': 140, 'y': 210, 'z': 2.5}
        elif elapsed_seconds < 180:
            drone_a_state = 'healthy'
            drone_a_loc = 'Pipe Gallery'
            drone_a_pos = {'x': 350, 'y': 210, 'z': 4}
        elif elapsed_seconds < 300:
            drone_a_state = 'degraded'  # Reflective surfaces affecting sensors
            drone_a_loc = 'Tank Interior'
            drone_a_pos = {'x': 350, 'y': 345, 'z': 6}
        else:
            drone_a_state = 'degraded'  # EMI interference
            drone_a_loc = 'Duct Section'
            drone_a_pos = {'x': 545, 'y': 210, 'z': 8}
        
        agents.append({
            'agent_id': 'inspection-drone-a',
            'name': 'Industrial Inspector',
            'role': 'Asset inspection',
            'state': drone_a_state,
            'battery_percent': int(drone_a_battery),
            'signal_strength': int(drone_a_signal),
            'location_label': drone_a_loc,
            'position': drone_a_pos,
            'sensors': ['Thermal', 'RGB Camera', 'Vibration', 'Gas Sensor'],
            'nfc_recovery_available': False
        })
    
    # Static monitoring node
    if elapsed_seconds >= 120:
        agents.append({
            'agent_id': 'monitor-node-1',
            'name': 'Plant Room Monitor',
            'role': 'Continuous gas/temperature monitoring',
            'state': 'active',
            'battery_percent': 98,
            'signal_strength': 85,
            'location_label': 'Plant Room',
            'position': {'x': 18, 'y': 12, 'z': 3},
            'sensors': ['CO2', 'Methane', 'Temperature', 'Humidity'],
            'nfc_recovery_available': False
        })
    
    # Thermal specialist drone (deploys at 240s)
    if elapsed_seconds >= 240:
        drone_b_battery = max(20, 100 - ((elapsed_seconds - 240) / 20))
        agents.append({
            'agent_id': 'thermal-drone-b',
            'name': 'Thermal Specialist',
            'role': 'Hotspot detection',
            'state': 'healthy',
            'battery_percent': int(drone_b_battery),
            'signal_strength': 78,
            'location_label': 'Control Cabinet area',
            'position': {'x': 695, 'y': 210, 'z': 2},
            'sensors': ['High-res Thermal', 'Infrared'],
            'nfc_recovery_available': False
        })
    
    # Network state - EMI and metal structures cause interference
    if elapsed_seconds < 180:
        mesh_health = max(70, 92 - (elapsed_seconds / 15))
        packet_loss = min(8, elapsed_seconds / 25)
    elif elapsed_seconds < 300:
        mesh_health = max(60, 80 - ((elapsed_seconds - 180) / 12))
        packet_loss = min(15, 5 + ((elapsed_seconds - 180) / 20))
    else:
        mesh_health = max(50, 70 - ((elapsed_seconds - 300) / 10))
        packet_loss = min(22, 10 + ((elapsed_seconds - 300) / 15))
    
    relay_chain = ['base-station', 'inspection-drone-a']
    if len(agents) > 2 and 'monitor-node-1' in [a['agent_id'] for a in agents]:
        relay_chain.insert(1, 'monitor-node-1')
    
    network = {
        'base_signal_strength': int(max(55, 92 - (elapsed_seconds / 10))),
        'mesh_health': int(mesh_health),
        'relay_chain': relay_chain,
        'packet_loss_percent': int(packet_loss)
    }
    
    # Map state
    coverage = min(70, (elapsed_seconds / 7))
    confidence = max(0.74, 0.91 - (elapsed_seconds / 1800))
    
    inspected_zones = []
    if elapsed_seconds >= 30:
        inspected_zones.append('Plant Room')
    if elapsed_seconds >= 90:
        inspected_zones.append('Pipe Gallery')
    if elapsed_seconds >= 180:
        inspected_zones.append('Tank Interior')
    if elapsed_seconds >= 300:
        inspected_zones.append('Duct Section')
    if elapsed_seconds >= 420:
        inspected_zones.append('Control Cabinet')
    
    map_data = {
        'map_type': '3d-industrial-asset-map',
        'coverage_percent': int(coverage),
        'confidence': confidence,
        'total_points': int(4000 + (elapsed_seconds * 30)),
        'new_points_generated': 1000,
        'mapped_sectors': inspected_zones,
        'blocked_sectors': ['Sealed Equipment Room'] if elapsed_seconds > 200 else [],
        'accessible_areas': [
            {'label': 'Pipe Gallery', 'confidence': 0.88, 'risk': 'low'},
            {'label': 'Tank Interior', 'confidence': 0.76, 'risk': 'medium'},
            {'label': 'Duct Section', 'confidence': 0.71, 'risk': 'medium'},
            {'label': 'Control Cabinet', 'confidence': 0.82, 'risk': 'low'}
        ] if elapsed_seconds > 300 else []
    }
    
    # Sensor data
    thermal_anomalies = []
    audio_events = []
    device_signals = []
    environmental_readings = []
    
    # Oxygen concentration (normal range 20.9%)
    if elapsed_seconds >= 30:
        o2_value = max(19.2, 20.9 - (elapsed_seconds / 600))  # Gradual O2 depletion in confined space
        o2_status = 'normal'
        if o2_value < 19.5:
            o2_status = 'watch'
        if o2_value < 19.0:
            o2_status = 'warning'
        
        environmental_readings.append({
            'sensor_type': 'oxygen',
            'display_name': 'Oxygen (O2)',
            'value': round(o2_value, 1),
            'unit': '%',
            'status': o2_status,
            'location_label': drone_a_loc,
            'confidence': 92,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(elapsed_seconds),
            'location': drone_a_loc
        })
    
    # CO2 levels (normal <1000 ppm)
    if elapsed_seconds >= 60:
        co2_value = min(1200, 400 + (elapsed_seconds * 2))
        co2_status = 'normal'
        if co2_value > 800:
            co2_status = 'watch'
        if co2_value > 1000:
            co2_status = 'warning'
        
        environmental_readings.append({
            'sensor_type': 'carbon_dioxide',
            'display_name': 'Carbon Dioxide (CO2)',
            'value': int(co2_value),
            'unit': 'ppm',
            'status': co2_status,
            'location_label': drone_a_loc,
            'confidence': 88,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(elapsed_seconds),
            'location': drone_a_loc
        })
    
    # Hydrogen detection (explosive risk)
    if elapsed_seconds >= 240:
        h2_value = 50 if elapsed_seconds < 450 else 120
        h2_status = 'normal' if h2_value < 100 else 'watch'
        
        environmental_readings.append({
            'sensor_type': 'hydrogen',
            'display_name': 'Hydrogen (H2)',
            'value': int(h2_value),
            'unit': 'ppm',
            'status': h2_status,
            'location_label': 'Pipe Gallery',
            'confidence': 84,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(elapsed_seconds),
            'location': 'Pipe Gallery'
        })
    
    # Methane detection (industrial/explosive risk)
    if elapsed_seconds >= 180:
        ch4_value = 120 if elapsed_seconds < 300 else 180
        ch4_status = 'watch' if ch4_value < 150 else 'warning'
        
        environmental_readings.append({
            'sensor_type': 'methane',
            'display_name': 'Methane (CH4)',
            'value': int(ch4_value),
            'unit': 'ppm',
            'status': ch4_status,
            'location_label': 'Pipe Gallery',
            'confidence': 86,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(180),
            'location': 'Pipe Gallery'
        })
    
    # Temperature readings
    if elapsed_seconds >= 150:
        environmental_readings.append({
            'sensor_type': 'temperature',
            'display_name': 'Temperature',
            'value': 28.5 + (elapsed_seconds / 60),
            'unit': 'degC',
            'status': 'normal' if elapsed_seconds < 300 else 'watch',
            'location_label': drone_a_loc,
            'confidence': 95,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(elapsed_seconds),
            'location': drone_a_loc
        })
    
    # Humidity readings
    if elapsed_seconds >= 90:
        environmental_readings.append({
            'sensor_type': 'humidity',
            'display_name': 'Humidity',
            'value': 65 + (elapsed_seconds / 120),
            'unit': '%',
            'status': 'normal',
            'location_label': drone_a_loc,
            'confidence': 91,
            'detected_at': int(elapsed_seconds),
            'timestamp': format_time(elapsed_seconds),
            'location': drone_a_loc
        })
    
    # Temperature hotspots
    if elapsed_seconds >= 150:
        thermal_anomalies.append({
            'detected_at': format_time(150),
            'location': 'Pipe Joint A3',
            'temperature_delta': 22.5,
            'confidence': 0.84,
            'human_review_required': True,
            'status': 'investigating'
        })
    
    if elapsed_seconds >= 270:
        thermal_anomalies.append({
            'detected_at': format_time(270),
            'location': 'Tank Interior Wall',
            'temperature_delta': 15.8,
            'confidence': 0.76,
            'human_review_required': False,
            'status': 'normal-operating-range'
        })
    
    if elapsed_seconds >= 450:
        thermal_anomalies.append({
            'detected_at': format_time(450),
            'location': 'Control Cabinet C2',
            'temperature_delta': 38.2,
            'confidence': 0.91,
            'human_review_required': True,
            'status': 'critical'
        })
    
    # Vibration/audio events
    if elapsed_seconds >= 210:
        audio_events.append({
            'detected_at': format_time(210),
            'location': 'Pipe Gallery',
            'type': 'abnormal-vibration',
            'confidence': 0.79,
            'frequency_range': '40-120 Hz',
            'human_review_required': True,
            'status': 'investigating'
        })
    
    if elapsed_seconds >= 390:
        audio_events.append({
            'detected_at': format_time(390),
            'location': 'Duct Section',
            'type': 'pressure-leak',
            'confidence': 0.82,
            'frequency_range': '2000-8000 Hz',
            'human_review_required': True,
            'status': 'defect-confirmed'
        })
    
    sensors = {
        'thermal_anomalies': thermal_anomalies,
        'audio_events': audio_events,
        'device_signals': device_signals,
        'environmental_readings': environmental_readings
    }
    
    # Mission events
    events = []
    
    if elapsed_seconds >= 0:
        events.append({
            'type': 'mission-start',
            'time': format_time(0),
            'title': 'Industrial inspection started',
            'description': 'Confined space asset inspection and hazard detection initiated',
            'agent': None
        })
    
    if elapsed_seconds >= 30:
        events.append({
            'type': 'deployment',
            'time': format_time(30),
            'title': 'Industrial inspector deployed',
            'description': 'Plant Room inspection initiated',
            'agent': 'inspection-drone-a'
        })
    
    if elapsed_seconds >= 120:
        events.append({
            'type': 'sensor-deployed',
            'time': format_time(120),
            'title': 'Monitoring node deployed',
            'description': 'Continuous gas and temperature monitoring active',
            'agent': 'monitor-node-1'
        })
    
    if elapsed_seconds >= 150:
        events.append({
            'type': 'defect-detected',
            'time': format_time(150),
            'title': 'Thermal hotspot: Pipe Joint A3',
            'description': 'Elevated temperature (+22.5degC) detected, possible leak or friction',
            'agent': 'inspection-drone-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 180:
        events.append({
            'type': 'hazard-alert',
            'time': format_time(180),
            'title': 'Gas detection: Methane',
            'description': 'Elevated methane levels (120 ppm) in Pipe Gallery',
            'agent': 'monitor-node-1',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 210:
        events.append({
            'type': 'defect-detected',
            'time': format_time(210),
            'title': 'Abnormal vibration detected',
            'description': 'Pipe Gallery showing unusual vibration signature',
            'agent': 'inspection-drone-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 240:
        events.append({
            'type': 'deployment',
            'time': format_time(240),
            'title': 'Thermal specialist deployed',
            'description': 'High-resolution thermal imaging active',
            'agent': 'thermal-drone-b'
        })
    
    if elapsed_seconds >= 300:
        events.append({
            'type': 'sensor-degraded',
            'time': format_time(300),
            'title': 'EMI interference detected',
            'description': 'Electromagnetic interference reducing sensor confidence in Duct Section',
            'agent': 'inspection-drone-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 330:
        events.append({
            'type': 'sensor-degraded',
            'time': format_time(330),
            'title': 'Reflective surface interference',
            'description': 'Tank Interior reflective surfaces affecting visual sensors',
            'agent': 'inspection-drone-a',
            'severity': 'moderate'
        })
    
    if elapsed_seconds >= 390:
        events.append({
            'type': 'defect-detected',
            'time': format_time(390),
            'title': 'Pressure leak detected',
            'description': 'High-frequency audio signature indicates leak in Duct Section',
            'agent': 'inspection-drone-a',
            'severity': 'high'
        })
    
    if elapsed_seconds >= 450:
        events.append({
            'type': 'defect-detected',
            'time': format_time(450),
            'title': 'Critical thermal hotspot: Control Cabinet C2',
            'description': 'Abnormal heat (+38.2degC) in electrical cabinet, immediate review required',
            'agent': 'thermal-drone-b',
            'severity': 'critical'
        })
    
    # AI analysis with defect ranking
    if elapsed_seconds < 150:
        ai_summary = 'Industrial asset inspection in progress. Plant Room and Pipe Gallery scanned. No defects detected yet.'
        priority_findings = []
        human_review = False
        ai_confidence = 0.76
    elif elapsed_seconds < 300:
        ai_summary = 'Multiple defects detected: thermal hotspot at Pipe Joint A3, methane elevation, abnormal vibration. Pipe Gallery requires attention.'
        priority_findings = [
            'Thermal hotspot: Pipe Joint A3 (+22.5degC)',
            'Methane detected in Pipe Gallery (120 ppm)',
            'Abnormal vibration signature'
        ]
        human_review = True
        ai_confidence = 0.79
    elif elapsed_seconds < 450:
        ai_summary = 'Inspection progressing with sensor challenges. EMI and reflective surfaces affecting confidence. Additional defects mapped in Duct Section.'
        priority_findings = [
            'Pressure leak in Duct Section (confidence: 82%)',
            'Thermal hotspot: Pipe Joint A3',
            'Methane elevation in Pipe Gallery',
            'Sensor confidence reduced by EMI and reflections'
        ]
        human_review = True
        ai_confidence = 0.74
    else:
        ai_summary = 'Critical thermal hotspot detected in Control Cabinet C2 (+38.2degC). Immediate human review required. Multiple defects ranked by severity.'
        priority_findings = [
            'CRITICAL: CRITICAL: Control Cabinet C2 thermal hotspot (+38.2degC)',
            'HIGH: HIGH: Pressure leak in Duct Section',
            'MODERATE: MODERATE: Pipe Joint A3 thermal anomaly (+22.5degC)',
            'MODERATE: MODERATE: Methane elevation in Pipe Gallery',
            'MODERATE: MODERATE: Abnormal vibration in Pipe Gallery'
        ]
        human_review = True
        ai_confidence = 0.81
    
    ai_analysis = {
        'summary': ai_summary,
        'priority_findings': priority_findings,
        'human_review_required': human_review,
        'confidence': ai_confidence
    }
    
    # Terrain reconstruction - progressive sector reveal with multi-agent scans
    terrain_sectors = [
        {
            'sector_id': 'entry',
            'reveal_at': 0,
            'scan_rules': [
                {'time': 0, 'agent_id': 'base-station'},
            ]
        },
        {
            'sector_id': 'plant-room',
            'reveal_at': 30,
            'scan_rules': [
                {'time': 30, 'agent_id': 'inspection-drone-a'},
                {'time': 120, 'agent_id': 'monitor-node-1'},
            ]
        },
        {
            'sector_id': 'pipe-gallery',
            'reveal_at': 60,
            'scan_rules': [
                {'time': 60, 'agent_id': 'inspection-drone-a'},
                {'time': 270, 'agent_id': 'thermal-drone-b'},
            ]
        },
        {
            'sector_id': 'tank-interior',
            'reveal_at': 180,
            'scan_rules': [
                {'time': 180, 'agent_id': 'inspection-drone-a'},
            ]
        },
        {
            'sector_id': 'duct-section',
            'reveal_at': 300,
            'scan_rules': [
                {'time': 300, 'agent_id': 'inspection-drone-a'},
                {'time': 330, 'agent_id': 'thermal-drone-b'},
            ]
        },
        {
            'sector_id': 'control-cabinet',
            'reveal_at': 420,
            'scan_rules': [
                {'time': 420, 'agent_id': 'inspection-drone-a'},
                {'time': 450, 'agent_id': 'thermal-drone-b'},
            ],
            'is_hazardous': True,
            'hazard_detected_at': 450
        },
    ]
    
    terrain_reconstruction = calculate_terrain_reconstruction(
        terrain_sectors, agents, elapsed_seconds
    )
    
    # Media feeds - simulated inspection camera returns
    media_feeds = []
    
    # Inspector Drone: Close-up inspection frames
    if elapsed_seconds >= 45:
        inspector_agent = next((a for a in agents if a['agent_id'] == 'inspection-drone-a'), None)
        if inspector_agent:
            # Reflective surfaces degrade confidence after 360s
            if elapsed_seconds >= 360:
                frame_status = 'degraded'
                annotations = ['inspection imaging', 'reflective surface', 'confidence reduced']
                description = 'Inspection frame degraded by reflective surface interference.'
                conf = 56
            else:
                frame_status = 'live'
                annotations = ['close-up inspection', 'structural assessment']
                description = f'Close-up inspection of {inspector_agent["location_label"]}.'
                conf = 88
            
            media_feeds.append({
                'frame_id': f'inspector-rgb-{int(elapsed_seconds)}',
                'agent_id': 'inspection-drone-a',
                'agent_name': 'Inspector Drone',
                'sensor_type': 'inspection_camera',
                'frame_type': 'still',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': inspector_agent['signal_strength'],
                'confidence': conf,
                'location_label': inspector_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Thermal Specialist: Thermal hotspot frames
    if elapsed_seconds >= 165:
        thermal_agent = next((a for a in agents if a['agent_id'] == 'thermal-specialist'), None)
        if thermal_agent:
            # Pipe Joint A3 thermal anomaly detected at 165s
            if elapsed_seconds >= 165 and elapsed_seconds < 480:
                frame_status = 'ai_flagged'
                annotations = ['thermal anomaly', 'Pipe Joint A3', '+22.5degC above baseline']
                description = 'Thermal anomaly detected at Pipe Joint A3. Elevated temperature.'
                conf = 79
            # Control Cabinet C2 critical hotspot at 480s
            elif elapsed_seconds >= 480:
                frame_status = 'human_review_required'
                annotations = ['CRITICAL thermal hotspot', 'Control Cabinet C2', '+38.2degC', 'immediate review']
                description = 'CRITICAL: Severe thermal hotspot in Control Cabinet C2. Immediate action required.'
                conf = 81
            else:
                frame_status = 'live'
                annotations = ['thermal scan', 'baseline monitoring']
                description = 'Thermal imaging of industrial equipment.'
                conf = 84
            
            media_feeds.append({
                'frame_id': f'thermal-{int(elapsed_seconds)}',
                'agent_id': 'thermal-specialist',
                'agent_name': 'Thermal Specialist',
                'sensor_type': 'thermal_camera',
                'frame_type': 'thermal',
                'status': frame_status,
                'mission_time': format_time(elapsed_seconds),
                'signal_quality': thermal_agent['signal_strength'],
                'confidence': conf,
                'location_label': thermal_agent['location_label'],
                'annotations': annotations,
                'description': description
            })
    
    # Pressure leak annotated frame (Duct Section at 390s)
    if elapsed_seconds >= 390:
        inspector_agent = next((a for a in agents if a['agent_id'] == 'inspection-drone-a'), None)
        if inspector_agent:
            media_feeds.append({
                'frame_id': 'pressure-leak-frame',
                'agent_id': 'inspection-drone-a',
                'agent_name': 'Inspector Drone',
                'sensor_type': 'inspection_camera',
                'frame_type': 'still',
                'status': 'ai_flagged',
                'mission_time': format_time(390),
                'signal_quality': inspector_agent['signal_strength'],
                'confidence': 82,
                'location_label': 'Duct Section',
                'annotations': ['pressure leak detected', 'AI annotated', 'structural concern'],
                'description': 'AI-detected pressure leak in duct section. Close-up inspection frame.'
            })
    
    # Corrosion defect frame (if present in timeline)
    if elapsed_seconds >= 270:
        inspector_agent = next((a for a in agents if a['agent_id'] == 'inspection-drone-a'), None)
        if inspector_agent and 'Pipe Gallery' in inspector_agent['location_label']:
            media_feeds.append({
                'frame_id': 'corrosion-frame',
                'agent_id': 'inspection-drone-a',
                'agent_name': 'Inspector Drone',
                'sensor_type': 'inspection_camera',
                'frame_type': 'still',
                'status': 'ai_flagged',
                'mission_time': format_time(270),
                'signal_quality': inspector_agent['signal_strength'],
                'confidence': 76,
                'location_label': 'Pipe Gallery',
                'annotations': ['surface corrosion', 'maintenance required', 'AI detected'],
                'description': 'Surface corrosion detected on pipe surface. Maintenance attention required.'
            })
    
    # Navigation model for industrial inspection environment
    # Uses local 3D coordinate system for confined space navigation
    origin_position = {'x': 110, 'y': 90, 'z': 0}  # Entry Point
    
    # Calculate per-agent navigation intelligence
    # Add distance, bearing, and depth/elevation labels to each agent
    for agent in agents:
        agent_pos = agent.get('position', origin_position)
        
        # 2D and 3D distances from origin
        distance_2d = calculate_distance_2d(origin_position, agent_pos)
        distance_3d = calculate_distance_3d(origin_position, agent_pos)
        
        # Bearing from origin (only if agent has moved significantly)
        if distance_2d > 1.0:
            bearing_deg = calculate_bearing_degrees(origin_position, agent_pos)
            bearing_cardinal = bearing_to_cardinal(bearing_deg, points=16)
        else:
            bearing_deg = 0
            bearing_cardinal = 'N'
        
        # Elevation and depth
        elevation_m, depth_m = calculate_elevation_depth(agent_pos.get('z', 0))
        vertical_label = calculate_vertical_profile_label(agent_pos.get('z', 0), context='industrial')
        depth_elevation_label = format_depth_elevation_label(agent_pos.get('z', 0), use_arrows=True)
        
        # Add navigation intelligence fields
        agent['navigation'] = {
            'distance_from_origin_m': round(distance_2d, 1),
            'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
            'bearing_from_origin_deg': round(bearing_deg, 1) if distance_2d > 1 else None,
            'bearing_from_origin_cardinal': bearing_cardinal if distance_2d > 1 else None,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
            'vertical_offset_from_origin_m': round(elevation_m, 1),
            'vertical_profile_label': vertical_label,
            'depth_elevation_label': depth_elevation_label
        }
    compass_confidence, compass_reliability, compass_reason = calculate_compass_confidence(
        environment_type='industrial_facility',
        distance_from_origin_m=0,
        has_metal_nearby=True,  # Metal pipes, tanks, equipment
        has_electrical_interference=True  # Active electrical equipment
    )
    
    navigation_model = {
        'coordinate_system': 'local_mission_3d_grid',
        'origin_sector_id': 'entry',
        'origin_label': 'Entry Point',
        'origin_position': origin_position,
        'units': 'metres',
        'horizontal_units': 'metres',
        'vertical_units': 'metres',
        'svg_unit_to_metres': 0.25,
        'grid_square_metres': 5,
        'z_reference': 'origin_relative',
        'z_positive_direction': 'up',
        'depth_positive_direction': 'down',
        'north_reference': 'mission_north',
        'bearing_reference': 'magnetic_simulated',
        'magnetic_declination_deg': 0,
        'bearing_confidence': round(compass_confidence, 2),
        'bearing_reliability': compass_reliability,
        'bearing_reliability_reason': compass_reason
    }
    
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': 'industrial-inspection',
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'navigation_model': navigation_model,
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction,
        'media_feeds': media_feeds
    }


def create_placeholder_state(
    mission_id: str,
    mission_name: str,
    use_case: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str,
    placeholder_message: str
) -> Dict[str, Any]:
    """
    Create a basic placeholder state for use cases not yet fully implemented.
    """
    base_battery = max(10, 100 - (elapsed_seconds / 25))
    
    agents = [
        {
            'agent_id': 'agent-1',
            'name': 'Primary Agent',
            'role': 'Scout',
            'state': 'healthy',
            'battery_percent': int(base_battery),
            'signal_strength': 75,
            'location_label': 'Active area',
            'position': {'x': 10, 'y': 10, 'z': 2},
            'sensors': ['Camera', 'Sensors'],
            'nfc_recovery_available': False
        }
    ]
    
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': use_case,
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'agents': agents,
        'network': {
            'base_signal_strength': 80,
            'mesh_health': 75,
            'relay_chain': ['base-station', 'agent-1'],
            'packet_loss_percent': 5
        },
        'map': {
            'map_type': 'basic-map',
            'coverage_percent': int(min(90, (elapsed_seconds / 400) * 100)),
            'confidence': 0.70,
            'total_points': int(3000 + (elapsed_seconds * 10)),
            'new_points_generated': 500,
            'mapped_sectors': ['Area 1'],
            'blocked_sectors': [],
            'accessible_areas': []
        },
        'sensors': {
            'thermal_anomalies': [],
            'audio_events': [],
            'device_signals': [],
            'environmental_readings': []
        },
        'events': [
            {
                'type': 'mission-start',
                'time': '00:00',
                'title': 'Mission started',
                'description': placeholder_message,
                'agent': None
            }
        ],
        'ai_analysis': {
            'summary': f'{placeholder_message}. Mission in progress.',
            'priority_findings': [],
            'human_review_required': False,
            'confidence': 0.65
        }
    }


def simulate_archaeological_exploration(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Simulate Archaeological Exploration scenario.
    
    **NOW USING SCENARIO ENGINE** - Data-driven simulation from database scenario.
    
    Scenario: archaeological-exploration-alpha-01
    - Loaded from database via MissionScenario model
    - Uses Underground Heritage Chamber Digital Twin coordinates
    - Drone routes through access tunnel, antechamber, ceremonial chambers, alcoves
    
    To modify scenario behavior:
    1. Edit data/scenarios/archaeological_exploration_scenario_alpha.json
    2. Run: python manage.py seed_mission_scenarios --file archaeological_exploration_scenario_alpha.json --overwrite
    3. No code changes needed
    """
    from .scenario_engine import generate_simulation_state_from_scenario
    
    try:
        # Use scenario engine to generate simulation state
        return generate_simulation_state_from_scenario(
            mission_id=mission_id,
            scenario_id='archaeological-exploration-alpha-01',
            elapsed_seconds=elapsed_seconds,
            speed_multiplier=speed_multiplier,
            mission_name=mission_name,
            status=status
        )
    except Exception as e:
        # Fallback to minimal state if scenario engine fails
        import traceback
        print(f"[Scenario Engine Error] {e}")
        traceback.print_exc()
        
        return {
            'mission': {
                'mission_id': mission_id,
                'name': mission_name,
                'use_case': 'archaeological-exploration',
                'status': status
            },
            'simulation_clock': {
                'started_at': started_at.isoformat() if started_at else None,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'speed_multiplier': speed_multiplier,
                'is_running': status == 'running'
            },
            'error': str(e),
            'agents': [],
            'sectors': [],
            'events': [],
        }


def simulate_archaeological_exploration_legacy(
    mission_id: str,
    mission_name: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    LEGACY: Original hardcoded archaeological exploration simulation.
    
    Kept for reference and fallback. Will be removed once scenario engine is stable.
    
    Non-destructive heritage site mapping with progressive chamber discovery,
    fragile surface detection, environmental monitoring, and preservation-focused
    decision making.
    
    Timeline:
    - 0-60s: Entry preparation and relay deployment
    - 60-120s: Micro scout enters first chamber
    - 120-180s: First chamber rough mapping complete
    - 180-240s: LiDAR drone enters for high-fidelity scan
    - 240-300s: Possible artefact candidate detected
    - 300-360s: Low-light imaging begins
    - 360-420s: Narrow passage navigation challenge
    - 420-480s: Second chamber discovered
    - 480-540s: Environmental readings show humidity concern
    - 540+: Progressive refinement and cataloguing
    """
    minutes_elapsed = elapsed_seconds / 60.0
    
    # Agent states evolve over time
    agents = []
    
    # Static Relay/Environmental Node (deployed at entry, always present)
    agents.append({
        'agent_id': 'env-node-1',
        'name': 'Entry Environmental Node',
        'role': 'Relay and environmental monitoring',
        'state': 'active',
        'battery_percent': 100,  # Long-life battery
        'signal_strength': 98,
        'location_label': 'Entry Chamber',
        'position': {'x': 50, 'y': 200, 'z': 0},
        'sensors': ['Temperature', 'Humidity', 'O2', 'CO2', 'Dust Monitor'],
        'nfc_recovery_available': False
    })
    
    # Micro Scout Drone (enters at 60s)
    if elapsed_seconds >= 60:
        scout_battery = max(8, 100 - ((elapsed_seconds - 60) / 25))
        scout_signal = max(45, 88 - ((elapsed_seconds - 60) / 15))
        
        if elapsed_seconds < 360:
            scout_state = 'healthy'
            scout_location = 'First Chamber'
        elif elapsed_seconds < 450:
            scout_state = 'degraded'
            scout_location = 'Narrow Passage'
        else:
            scout_state = 'stranded'
            scout_location = 'Narrow Passage (stranded)'
        
        agents.append({
            'agent_id': 'micro-scout',
            'name': 'Micro Scout Drone',
            'role': 'Initial exploration',
            'state': scout_state,
            'battery_percent': int(scout_battery),
            'signal_strength': int(scout_signal),
            'location_label': scout_location,
            'position': {
                'x': 50 + ((elapsed_seconds - 60) / 8),
                'y': 200,
                'z': 1.2
            },
            'sensors': ['Low-light Camera', 'Obstacle Avoidance'],
            'nfc_recovery_available': scout_state == 'stranded'
        })
    
    # LiDAR Mapping Drone (enters at 180s for detailed scan)
    if elapsed_seconds >= 180:
        lidar_battery = max(12, 100 - ((elapsed_seconds - 180) / 22))
        lidar_signal = max(55, 85 - ((elapsed_seconds - 180) / 18))
        lidar_state = 'healthy' if elapsed_seconds < 540 else 'degraded'
        
        if elapsed_seconds < 300:
            lidar_location = 'First Chamber'
        elif elapsed_seconds < 480:
            lidar_location = 'Transition Passage'
        else:
            lidar_location = 'Second Chamber'
        
        agents.append({
            'agent_id': 'lidar-mapper',
            'name': 'LiDAR Mapping Drone',
            'role': 'High-fidelity 3D reconstruction',
            'state': lidar_state,
            'battery_percent': int(lidar_battery),
            'signal_strength': int(lidar_signal),
            'location_label': lidar_location,
            'position': {
                'x': 50 + ((elapsed_seconds - 180) / 10),
                'y': 200,
                'z': 2
            },
            'sensors': ['LiDAR', 'RGB Camera', 'Depth Sensor'],
            'nfc_recovery_available': False
        })
    
    # Low-Light Imaging Drone (enters at 300s for documentation)
    if elapsed_seconds >= 300:
        imaging_battery = max(15, 100 - ((elapsed_seconds - 300) / 20))
        imaging_signal = max(60, 82 - ((elapsed_seconds - 300) / 16))
        imaging_state = 'healthy'
        
        if elapsed_seconds < 420:
            imaging_location = 'First Chamber'
        else:
            imaging_location = 'Second Chamber'
        
        agents.append({
            'agent_id': 'imaging-drone',
            'name': 'Low-Light Imaging Drone',
            'role': 'Visual documentation',
            'state': imaging_state,
            'battery_percent': int(imaging_battery),
            'signal_strength': int(imaging_signal),
            'location_label': imaging_location,
            'position': {
                'x': 50 + ((elapsed_seconds - 300) / 9),
                'y': 200,
                'z': 1.8
            },
            'sensors': ['Low-light Camera', 'Infrared', 'Night Vision'],
            'nfc_recovery_available': False
        })
    
    # Network state - rock/soil attenuation increases over time
    if elapsed_seconds < 180:
        mesh_health = max(75, 95 - (elapsed_seconds / 12))
        packet_loss = min(8, elapsed_seconds / 30)
    elif elapsed_seconds < 420:
        mesh_health = max(60, 82 - ((elapsed_seconds - 180) / 15))
        packet_loss = min(15, 5 + ((elapsed_seconds - 180) / 25))
    else:
        mesh_health = max(50, 68 - ((elapsed_seconds - 420) / 20))
        packet_loss = min(22, 12 + ((elapsed_seconds - 420) / 30))
    
    relay_chain = ['env-node-1']
    if elapsed_seconds >= 180:
        relay_chain.append('lidar-mapper')
    if elapsed_seconds >= 60 and elapsed_seconds < 450:
        relay_chain.append('micro-scout')
    
    network = {
        'base_signal_strength': int(max(50, 94 - (elapsed_seconds / 15))),
        'mesh_health': int(mesh_health),
        'relay_chain': relay_chain,
        'packet_loss_percent': int(packet_loss)
    }
    
    # Progressive chamber map revelation
    coverage = min(85, (elapsed_seconds / 8))
    confidence = max(0.68, 0.92 - (elapsed_seconds / 1500))
    
    discovered_chambers = []
    if elapsed_seconds >= 90:
        discovered_chambers.append('Entry Chamber')
    if elapsed_seconds >= 180:
        discovered_chambers.append('First Chamber')
    if elapsed_seconds >= 300:
        discovered_chambers.append('Transition Passage')
    if elapsed_seconds >= 480:
        discovered_chambers.append('Second Chamber')
    
    fragile_zones = []
    if elapsed_seconds >= 240:
        fragile_zones.append('First Chamber - East Wall (possible wall art)')
    if elapsed_seconds >= 420:
        fragile_zones.append('Transition Passage - Floor (unstable surface)')
    if elapsed_seconds >= 540:
        fragile_zones.append('Second Chamber - Ceiling (loose material)')
    
    map_data = {
        'map_type': 'progressive-chamber-map',
        'coverage_percent': int(coverage),
        'confidence': round(confidence, 2),
        'total_points': int(3500 + (elapsed_seconds * 18)),
        'new_points_generated': 800,
        'mapped_sectors': discovered_chambers,
        'blocked_sectors': [],
        'fragile_zones': fragile_zones,
        'accessible_areas': [
            {
                'label': 'Entry Chamber',
                'confidence': 0.95,
                'risk': 'low'
            }
        ] + ([{
            'label': 'First Chamber',
            'confidence': 0.88,
            'risk': 'low'
        }] if elapsed_seconds >= 240 else []) + ([{
            'label': 'Second Chamber',
            'confidence': 0.72,
            'risk': 'medium'
        }] if elapsed_seconds >= 540 else [])
    }
    
    # Environmental readings
    environmental_readings = []
    if elapsed_seconds >= 30:
        environmental_readings.append({
            'sensor_type': 'temperature',
            'value': round(14.2 + (elapsed_seconds / 500), 1),
            'unit': 'degC',
            'location': 'Entry Chamber',
            'status': 'normal'
        })
        environmental_readings.append({
            'sensor_type': 'humidity',
            'value': min(85, int(62 + (elapsed_seconds / 15))),
            'unit': '%',
            'location': 'Entry Chamber',
            'status': 'watch' if elapsed_seconds > 480 else 'normal'
        })
        environmental_readings.append({
            'sensor_type': 'oxygen',
            'value': round(20.8 - (elapsed_seconds / 2000), 1),
            'unit': '%',
            'location': 'Entry Chamber',
            'status': 'normal'
        })
        environmental_readings.append({
            'sensor_type': 'carbon_dioxide',
            'value': min(800, int(420 + (elapsed_seconds / 3))),
            'unit': 'ppm',
            'location': 'Entry Chamber',
            'status': 'normal'
        })
    
    # Artefact candidate markers (review only)
    artefact_candidates = []
    if elapsed_seconds >= 240:
        artefact_candidates.append({
            'detected_at': '04:00',
            'location': 'First Chamber, East Wall',
            'type': 'possible wall marking or art',
            'confidence': 0.62,
            'human_review_required': True,
            'status': 'review only - not definitive'
        })
    if elapsed_seconds >= 420:
        artefact_candidates.append({
            'detected_at': '07:00',
            'location': 'Transition Passage, Floor',
            'type': 'possible ceramic fragment',
            'confidence': 0.45,
            'human_review_required': True,
            'status': 'review only - requires expert verification'
        })
    
    # Image catalogue
    captured_images = []
    if elapsed_seconds >= 120:
        captured_images.append({
            'image_id': 'img-001',
            'captured_at': '02:00',
            'location': 'First Chamber - Overview',
            'type': 'low-light',
            'quality': 'good'
        })
    if elapsed_seconds >= 300:
        captured_images.append({
            'image_id': 'img-002',
            'captured_at': '05:00',
            'location': 'First Chamber - East Wall detail',
            'type': 'infrared',
            'quality': 'excellent'
        })
    if elapsed_seconds >= 480:
        captured_images.append({
            'image_id': 'img-003',
            'captured_at': '08:00',
            'location': 'Second Chamber - Entry view',
            'type': 'low-light',
            'quality': 'fair'
        })
    
    sensors = {
        'artefact_candidates': artefact_candidates,
        'environmental_readings': environmental_readings,
        'captured_images': captured_images,
        'thermal_anomalies': [],
        'audio_events': [],
        'device_signals': []
    }
    
    # Timeline events
    events = []
    if elapsed_seconds > 5:
        events.append({
            'type': 'mission-start',
            'time': '00:00',
            'title': 'Archaeological Exploration mission started',
            'description': 'Non-destructive heritage site mapping initiated',
            'agent': None
        })
    if elapsed_seconds > 30:
        events.append({
            'type': 'agent-deployed',
            'time': '00:30',
            'title': 'Entry Environmental Node deployed',
            'description': 'Relay and environmental monitoring active',
            'agent': 'env-node-1'
        })
    if elapsed_seconds > 60:
        events.append({
            'type': 'agent-deployed',
            'time': '01:00',
            'title': 'Micro Scout Drone entered first chamber',
            'description': 'Initial low-speed exploration underway',
            'agent': 'micro-scout'
        })
    if elapsed_seconds > 120:
        events.append({
            'type': 'mapping-progress',
            'time': '02:00',
            'title': 'First chamber rough outline complete',
            'description': 'Initial chamber geometry mapped, confidence 65%',
            'agent': 'micro-scout'
        })
    if elapsed_seconds > 180:
        events.append({
            'type': 'agent-deployed',
            'time': '03:00',
            'title': 'LiDAR Mapping Drone entered',
            'description': 'High-fidelity 3D reconstruction beginning',
            'agent': 'lidar-mapper'
        })
    if elapsed_seconds > 240:
        events.append({
            'type': 'detection',
            'time': '04:00',
            'title': 'Possible artefact candidate detected',
            'description': 'East wall marking flagged for expert review (not definitive)',
            'agent': 'imaging-drone',
            'severity': 'info'
        })
    if elapsed_seconds > 300:
        events.append({
            'type': 'agent-deployed',
            'time': '05:00',
            'title': 'Low-Light Imaging Drone active',
            'description': 'Visual documentation and photography underway',
            'agent': 'imaging-drone'
        })
    if elapsed_seconds > 360:
        events.append({
            'type': 'warning',
            'time': '06:00',
            'title': 'Narrow passage navigation challenge',
            'description': 'Micro scout experiencing confined space difficulty',
            'agent': 'micro-scout',
            'severity': 'moderate'
        })
    if elapsed_seconds > 420:
        events.append({
            'type': 'discovery',
            'time': '07:00',
            'title': 'Second chamber discovered',
            'description': 'New chamber accessed via narrow passage',
            'agent': 'lidar-mapper'
        })
    if elapsed_seconds > 450:
        events.append({
            'type': 'state-change',
            'time': '07:30',
            'title': 'Micro scout stranded in narrow passage',
            'description': 'Agent left in place with NFC recovery available',
            'agent': 'micro-scout',
            'severity': 'info'
        })
    if elapsed_seconds > 480:
        events.append({
            'type': 'warning',
            'time': '08:00',
            'title': 'Humidity levels rising',
            'description': 'Environmental monitoring shows moisture increase to 78%',
            'agent': 'env-node-1',
            'severity': 'moderate'
        })
    
    # AI analysis - preservation focused
    if elapsed_seconds < 180:
        ai_summary = 'Initial chamber entry in progress. No artefact candidates yet. Environmental conditions normal.'
        priority_findings = []
        human_review = False
        ai_confidence = 0.72
    elif elapsed_seconds < 300:
        ai_summary = 'First chamber mapping shows promising features. Possible wall markings detected on east surface. Recommend expert archaeological review before further entry.'
        priority_findings = [
            'Possible wall marking at east wall (confidence 62%, review only)'
        ]
        human_review = True
        ai_confidence = 0.68
    else:
        ai_summary = 'Multiple chambers documented with progressive refinement. Artefact candidates flagged for expert review (not definitive identification). Humidity increasing in deeper sections - monitor before human entry. Micro scout stranded but NFC-readable for data recovery.'
        priority_findings = [
            'Possible wall marking at First Chamber east wall (confidence 62%)',
            'Possible ceramic fragment at Transition Passage floor (confidence 45%)',
            'Humidity rising to 78% - monitor environmental conditions',
            'Fragile zones identified - restricted access recommended'
        ]
        human_review = True
        ai_confidence = 0.75
    
    ai_analysis = {
        'summary': ai_summary,
        'priority_findings': priority_findings,
        'human_review_required': human_review,
        'confidence': ai_confidence
    }
    
    # Media feeds placeholder
    media_feeds = []
    if elapsed_seconds >= 120:
        media_feeds.append({
            'feed_id': 'scout-cam-1',
            'agent_id': 'micro-scout',
            'sensor_type': 'low_light',
            'label': 'Micro Scout - Low Light',
            'status': 'active' if elapsed_seconds < 450 else 'stranded',
            'last_frame_time': format_mission_time(elapsed_seconds - 5),
            'quality': 'fair'
        })
    if elapsed_seconds >= 300:
        media_feeds.append({
            'feed_id': 'imaging-cam-1',
            'agent_id': 'imaging-drone',
            'sensor_type': 'low_light',
            'label': 'Imaging Drone - Low Light',
            'status': 'active',
            'last_frame_time': format_mission_time(elapsed_seconds - 2),
            'quality': 'excellent'
        })
    
    return {
        'mission_id': mission_id,
        'mission_name': mission_name,
        'use_case_slug': 'archaeological-exploration',
        'elapsed_seconds': elapsed_seconds,
        'speed_multiplier': speed_multiplier,
        'started_at': started_at.isoformat() if started_at else None,
        'status': status,
        'clock': {
            'elapsed_time': format_mission_time(elapsed_seconds),
            'speed': f'{speed_multiplier}x'
        },
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'media_feeds': media_feeds
    }


def create_empty_state(
    mission_id: str,
    mission_name: str,
    use_case: str,
    elapsed_seconds: float,
    speed_multiplier: float,
    started_at: Optional[datetime],
    status: str
) -> Dict[str, Any]:
    """
    Create an empty state structure for unknown use cases.
    """
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': use_case,
            'status': status
        },
        'simulation_clock': {
            'started_at': started_at.isoformat() if started_at else None,
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running'
        },
        'agents': [],
        'network': {
            'base_signal_strength': 0,
            'mesh_health': 0,
            'relay_chain': [],
            'packet_loss_percent': 100
        },
        'map': {
            'map_type': 'unknown',
            'coverage_percent': 0,
            'confidence': 0.0,
            'total_points': 0,
            'new_points_generated': 0,
            'mapped_sectors': [],
            'blocked_sectors': [],
            'accessible_areas': []
        },
        'sensors': {
            'thermal_anomalies': [],
            'audio_events': [],
            'device_signals': [],
            'environmental_readings': []
        },
        'events': [],
        'ai_analysis': {
            'summary': 'No simulation available for this use case.',
            'priority_findings': [],
            'human_review_required': False,
            'confidence': 0.0
        }
    }
