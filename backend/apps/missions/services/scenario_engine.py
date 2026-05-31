"""
Mission Scenario Engine

Data-driven simulation engine that reads mission scenarios from the database
and generates simulation state based on agent routes, waypoints, and timeline events.

Replaces hardcoded simulation logic with reusable, configurable mission scripts.
"""
from typing import Dict, List, Any, Optional
import math
from django.core.cache import cache

from apps.missions.models_scenario import (
    MissionScenario,
    AgentRoute,
    RouteWaypoint,
    ScenarioEvent,
    UserMissionAction,
)
from apps.mapping.models import TerrainSector, TerrainPath
from .navigation_utils import (
    calculate_distance_2d,
    calculate_distance_3d,
    calculate_bearing_degrees,
    bearing_to_cardinal,
    calculate_elevation_depth,
    calculate_vertical_profile_label,
    format_depth_elevation_label,
)


def load_scenario(scenario_id: str) -> Dict[str, Any]:
    """
    Load scenario from database with all related data.
    
    Args:
        scenario_id: Unique scenario identifier
        
    Returns:
        Dictionary with scenario, routes, waypoints, events
    """
    try:
        scenario = MissionScenario.objects.prefetch_related(
            'agent_routes__waypoints',
            'events'
        ).get(scenario_id=scenario_id)
        
        return {
            'scenario': scenario,
            'routes': list(scenario.agent_routes.all()),
            'events': list(scenario.events.all()),
        }
    except MissionScenario.DoesNotExist:
        raise ValueError(f'Scenario not found: {scenario_id}')


def get_terrain_sectors(site_slug: str, terrain_slug: str) -> Dict[str, TerrainSector]:
    """
    Load terrain sectors from Digital Twin.
    
    Returns:
        Dictionary mapping sector_id to TerrainSector object
    """
    sectors = TerrainSector.objects.filter(
        terrain_map__slug=terrain_slug,
        terrain_map__digital_twin_site__slug=site_slug
    ).select_related('terrain_map__digital_twin_site')
    
    return {sector.sector_id: sector for sector in sectors}


def calculate_agent_position(
    route: AgentRoute,
    waypoints: List[RouteWaypoint],
    terrain_sectors: Dict[str, TerrainSector],
    elapsed_seconds: float
) -> Optional[Dict[str, Any]]:
    """
    Calculate agent's current position based on route and elapsed time.
    
    Args:
        route: AgentRoute object
        waypoints: List of RouteWaypoint objects (ordered)
        terrain_sectors: Dictionary of sector_id -> TerrainSector
        elapsed_seconds: Mission elapsed time in seconds
        
    Returns:
        Position dict or None if agent not yet deployed
    """
    # Check if agent is deployed yet
    if elapsed_seconds < route.deploy_at_seconds:
        return None
    
    # Time agent has been active
    time_on_route = elapsed_seconds - route.deploy_at_seconds
    
    # If no waypoints, return None
    if not waypoints:
        return None
    
    # Calculate cumulative time to reach each waypoint
    waypoint_times = []
    cumulative_time = 0.0
    
    for i, waypoint in enumerate(waypoints):
        # Travel time from previous waypoint
        if i > 0:
            prev_waypoint = waypoints[i - 1]
            distance = calculate_waypoint_distance(
                prev_waypoint,
                waypoint,
                terrain_sectors
            )
            travel_time = distance / route.average_speed_m_per_s if route.average_speed_m_per_s > 0 else 0
            cumulative_time += travel_time
        
        waypoint_times.append({
            'waypoint': waypoint,
            'arrival_time': cumulative_time,
            'departure_time': cumulative_time + waypoint.pause_duration_seconds
        })
        
        cumulative_time += waypoint.pause_duration_seconds
    
    # Find current waypoint
    current_waypoint_index = 0
    is_moving = False
    progress = 0.0
    
    for i, wpt_time in enumerate(waypoint_times):
        if time_on_route < wpt_time['departure_time']:
            current_waypoint_index = i
            
            # Check if moving toward this waypoint or paused at it
            if time_on_route < wpt_time['arrival_time']:
                # Moving toward this waypoint
                is_moving = True
                if i > 0:
                    prev_departure = waypoint_times[i - 1]['departure_time']
                    travel_duration = wpt_time['arrival_time'] - prev_departure
                    time_traveling = time_on_route - prev_departure
                    progress = time_traveling / travel_duration if travel_duration > 0 else 0.0
            else:
                # Paused at waypoint
                is_moving = False
                progress = 1.0
            
            break
    else:
        # Agent has completed all waypoints
        current_waypoint_index = len(waypoints) - 1
        is_moving = False
        progress = 1.0
    
    # Get position
    current_waypoint = waypoints[current_waypoint_index]
    
    if is_moving and current_waypoint_index > 0:
        # Interpolate between previous and current waypoint
        prev_waypoint = waypoints[current_waypoint_index - 1]
        position = interpolate_waypoint_position(
            prev_waypoint,
            current_waypoint,
            terrain_sectors,
            progress
        )
    else:
        # At waypoint
        position = get_waypoint_position(current_waypoint, terrain_sectors)
    
    # Calculate battery drain
    battery_percent = 100.0 - (time_on_route * route.battery_drain_rate_percent_per_second)
    battery_percent = max(0.0, battery_percent)
    
    return {
        **position,
        'current_waypoint_index': current_waypoint_index,
        'is_moving': is_moving,
        'progress_to_next': progress,
        'battery_percent': battery_percent,
        'time_on_route': time_on_route,
    }


def calculate_waypoint_distance(
    waypoint1: RouteWaypoint,
    waypoint2: RouteWaypoint,
    terrain_sectors: Dict[str, TerrainSector]
) -> float:
    """Calculate 2D distance between two waypoints."""
    pos1 = get_waypoint_position(waypoint1, terrain_sectors)
    pos2 = get_waypoint_position(waypoint2, terrain_sectors)
    
    return calculate_distance_2d(pos1, pos2)


def get_waypoint_position(
    waypoint: RouteWaypoint,
    terrain_sectors: Dict[str, TerrainSector]
) -> Dict[str, float]:
    """
    Get position of a waypoint.
    
    Uses override position if specified, otherwise sector centroid.
    """
    if waypoint.override_x_m is not None:
        return {
            'x': waypoint.override_x_m,
            'y': waypoint.override_y_m or 0.0,
            'z': waypoint.override_z_m or 0.0,
        }
    
    # Use sector centroid
    sector = terrain_sectors.get(waypoint.sector_id)
    if sector:
        # Position agent at center of sector, not at origin
        center_x = sector.x_m + (sector.width_m / 2.0 if sector.width_m else 0.0)
        center_y = sector.y_m + (sector.height_m / 2.0 if sector.height_m else 0.0)
        # Z uses sector's base z_m (for now, could add vertical centering later)
        return {
            'x': center_x,
            'y': center_y,
            'z': sector.z_m,
        }
    
    # Fallback to origin
    return {'x': 0.0, 'y': 0.0, 'z': 0.0}


def interpolate_waypoint_position(
    waypoint1: RouteWaypoint,
    waypoint2: RouteWaypoint,
    terrain_sectors: Dict[str, TerrainSector],
    progress: float
) -> Dict[str, float]:
    """Interpolate position between two waypoints."""
    pos1 = get_waypoint_position(waypoint1, terrain_sectors)
    pos2 = get_waypoint_position(waypoint2, terrain_sectors)
    
    progress = max(0.0, min(1.0, progress))
    
    return {
        'x': pos1['x'] + (pos2['x'] - pos1['x']) * progress,
        'y': pos1['y'] + (pos2['y'] - pos1['y']) * progress,
        'z': pos1['z'] + (pos2['z'] - pos1['z']) * progress,
    }


def get_agent_sector_id(
    position: Dict[str, float],
    terrain_sectors: Dict[str, TerrainSector]
) -> str:
    """Find which sector the agent is currently in based on position."""
    # Find closest sector by distance
    min_distance = float('inf')
    closest_sector_id = ''
    
    for sector_id, sector in terrain_sectors.items():
        sector_pos = {'x': sector.x_m, 'y': sector.y_m, 'z': sector.z_m}
        distance = calculate_distance_3d(position, sector_pos)
        
        if distance < min_distance:
            min_distance = distance
            closest_sector_id = sector_id
    
    return closest_sector_id


def get_active_events(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    last_check_seconds: float = 0
) -> List[ScenarioEvent]:
    """
    Get events that should trigger between last_check and current time.
    
    Returns:
        List of ScenarioEvent objects that should fire
    """
    active_events = []
    
    for event in events:
        if last_check_seconds < event.trigger_at_seconds <= elapsed_seconds:
            active_events.append(event)
    
    return active_events


def extract_thermal_detections(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector],
    agents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extract thermal detection events that have been triggered.
    Detections persist even after detecting agent fails.
    
    Returns:
        List of thermal anomaly detection records
    """
    detections = []
    
    for event in events:
        # Only process triggered detection events
        if event.trigger_at_seconds > elapsed_seconds:
            continue
            
        # Check for thermal detection events
        if event.event_type in ('detection-thermal', 'detection') and 'thermal' in event.title.lower():
            # Get agent name
            agent_name = event.agent_id or 'Unknown'
            agent_obj = next((a for a in agents if a['agent_id'] == event.agent_id), None)
            if agent_obj:
                agent_name = agent_obj['name']
            
            # Get position from sector
            position = None
            sector = None
            if event.sector_id and event.sector_id in terrain_sectors:
                sector = terrain_sectors[event.sector_id]
                position = {
                    'x_m': sector.x_m + (sector.width_m / 2),
                    'y_m': sector.y_m + (sector.height_m / 2),
                    'z_m': sector.z_m,
                }
            
            # Extract temperature from event_data if available
            temperature_delta = event.event_data.get('temperature_delta', 0)
            if not temperature_delta:
                # Try to extract from description
                import re
                temp_match = re.search(r'(\d+\.?\d*)\s*[°\u00b0]?[Cc]', event.description or '')
                if temp_match:
                    temperature_delta = float(temp_match.group(1))
            
            detection = {
                'id': f"thermal-{event.id}",
                'agent_id': event.agent_id,
                'agent_name': agent_name,
                'detected_at': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else (event.sector_id or 'Unknown'),
                'temperature_delta': temperature_delta,
                'confidence': float(event.event_data.get('confidence', 0.75)),
                'human_review_required': event.requires_user_action,
                'status': event.severity,
                'description': event.description or event.title,
                'position': position,
                'timestamp_seconds': event.trigger_at_seconds,
            }
            detections.append(detection)
    
    return detections


def extract_audio_detections(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector],
    agents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extract audio detection events that have been triggered.
    Detections persist even after detecting agent fails.
    
    Returns:
        List of audio detection records
    """
    detections = []
    
    for event in events:
        # Only process triggered detection events
        if event.trigger_at_seconds > elapsed_seconds:
            continue
            
        # Check for audio detection events
        if event.event_type in ('detection-audio', 'detection') and 'audio' in event.title.lower():
            # Get agent name
            agent_name = event.agent_id or 'Unknown'
            agent_obj = next((a for a in agents if a['agent_id'] == event.agent_id), None)
            if agent_obj:
                agent_name = agent_obj['name']
            
            # Get position from sector
            position = None
            sector = None
            if event.sector_id and event.sector_id in terrain_sectors:
                sector = terrain_sectors[event.sector_id]
                position = {
                    'x_m': sector.x_m + (sector.width_m / 2),
                    'y_m': sector.y_m + (sector.height_m / 2),
                    'z_m': sector.z_m,
                }
            
            # Determine audio type from title/description
            audio_type = 'voice_like'
            title_lower = event.title.lower()
            if 'tapping' in title_lower or 'knock' in title_lower:
                audio_type = 'tapping'
            elif 'voice' in title_lower:
                audio_type = 'voice_like'
            
            detection = {
                'id': f"audio-{event.id}",
                'agent_id': event.agent_id,
                'agent_name': agent_name,
                'detected_at': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else (event.sector_id or 'Unknown'),
                'type': audio_type,
                'confidence': float(event.event_data.get('confidence', 0.65)),
                'frequency_range': event.event_data.get('frequency_range', 'Unknown'),
                'human_review_required': event.requires_user_action,
                'status': 'detected' if not event.requires_user_action else 'human_review_required',
                'description': event.description or event.title,
                'position': position,
                'timestamp_seconds': event.trigger_at_seconds,
            }
            detections.append(detection)
    
    return detections


def generate_simulation_state_from_scenario(
    mission_id: str,
    scenario_id: str,
    elapsed_seconds: float,
    speed_multiplier: float = 1.0,
    mission_name: str = "Mission Demo",
    status: str = "running"
) -> Dict[str, Any]:
    """
    Generate complete simulation state from scenario.
    
    Main entry point for scenario-driven simulation.
    
    Args:
        mission_id: Unique mission instance ID
        scenario_id: Scenario template ID to use
        elapsed_seconds: Mission elapsed time
        speed_multiplier: Time speed multiplier
        mission_name: Mission display name
        status: Mission status
        
    Returns:
        Complete simulation state matching simulation.py format
    """
    # Load scenario
    scenario_data = load_scenario(scenario_id)
    scenario = scenario_data['scenario']
    routes = scenario_data['routes']
    events = scenario_data['events']
    
    # Load Digital Twin terrain
    terrain_sectors = get_terrain_sectors(
        scenario.digital_twin_site_slug,
        scenario.digital_twin_terrain_slug
    )
    
    # Origin position (from scenario or first sector)
    origin_sector = terrain_sectors.get(scenario.origin_sector_id)
    if origin_sector:
        origin_position = {'x': origin_sector.x_m, 'y': origin_sector.y_m, 'z': origin_sector.z_m}
    else:
        origin_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    
    # Generate agents from routes
    agents = []
    for route in routes:
        waypoints = list(route.waypoints.all().order_by('sequence_order'))
        
        agent_position = calculate_agent_position(
            route,
            waypoints,
            terrain_sectors,
            elapsed_seconds
        )
        
        if agent_position is None:
            # Agent not yet deployed
            continue
        
        # Determine agent state based on battery and waypoints
        if agent_position['battery_percent'] <= 0:
            agent_state = 'sacrificed'
        elif agent_position['battery_percent'] < 20:
            agent_state = 'degraded'
        else:
            agent_state = 'healthy'
        
        # Get current sector
        sector_id = get_agent_sector_id(agent_position, terrain_sectors)
        current_sector = terrain_sectors.get(sector_id)
        location_label = current_sector.label if current_sector else 'Unknown'
        
        # Build agent dict
        agent = {
            'agent_id': route.agent_id,
            'name': route.agent_name,
            'role': route.agent_role,
            'state': agent_state,
            'battery_percent': int(agent_position['battery_percent']),
            'signal_strength': 85,  # Simplified for now
            'location_label': location_label,
            'sector': sector_id,
            'position': {
                'x': agent_position['x'],
                'y': agent_position['y'],
                'z': agent_position['z'],
            },
            'sensors': route.sensors,
            'nfc_recovery_available': agent_state == 'sacrificed',
        }
        
        agents.append(agent)
    
    # Build sectors list with confidence
    sectors_detailed = []
    currently_occupied_sector_ids = set(agent['sector'] for agent in agents)
    
    # Build cumulative set of ALL sectors visited during mission (not just current)
    explored_sector_ids = set()
    for route in scenario.agent_routes.all():
        if elapsed_seconds < route.deploy_at_seconds:
            continue  # Agent not deployed yet
            
        time_on_route = elapsed_seconds - route.deploy_at_seconds
        waypoints = list(route.waypoints.all().order_by('sequence_order'))
        
        # Add all waypoint sectors that agent has reached
        cumulative_time = 0.0
        for i, waypoint in enumerate(waypoints):
            # Add travel time from previous waypoint
            if i > 0:
                prev_waypoint = waypoints[i - 1]
                distance = calculate_waypoint_distance(prev_waypoint, waypoint, terrain_sectors)
                travel_time = distance / route.average_speed_m_per_s if route.average_speed_m_per_s > 0 else 0
                cumulative_time += travel_time
            
            # Check if agent has reached this waypoint
            if time_on_route >= cumulative_time:
                explored_sector_ids.add(waypoint.sector_id)
            
            cumulative_time += waypoint.pause_duration_seconds
            
            # If agent hasn't reached departure time, stop
            if time_on_route < cumulative_time:
                break
    
    for sector_id, sector in terrain_sectors.items():
        # Calculate confidence based on exploration
        if sector_id in currently_occupied_sector_ids:
            confidence = 0.85  # Currently being explored
        elif sector_id in explored_sector_ids:
            confidence = 1.0  # Previously explored (fully mapped)
        elif sector_id == scenario.origin_sector_id:
            confidence = 1.0  # Origin always known
        else:
            confidence = 0.0  # Not yet explored
        
        elevation_m, depth_m = calculate_elevation_depth(sector.z_m)
        
        sector_dict = {
            'sector_id': sector_id,
            'label': sector.label,
            'centroid': {'x': sector.x_m, 'y': sector.y_m, 'z': sector.z_m},
            'type': sector.sector_type,
            'confidence': confidence,
            'elevation_m': round(elevation_m, 1),
            'depth_m': round(depth_m, 1),
        }
        
        sectors_detailed.append(sector_dict)
    
    # Get active events for timeline
    timeline_events = []
    active_scenario_events = get_active_events(events, elapsed_seconds)
    
    for event in active_scenario_events:
        timeline_events.append({
            'event_type': event.event_type,
            'timestamp': format_time(event.trigger_at_seconds),
            'title': event.title,
            'description': event.description,
            'severity': event.severity,
            'agent_id': event.agent_id or '',
            'sector_id': event.sector_id or '',
            'requires_user_action': event.requires_user_action,
            'event_data': event.event_data,
        })
    
    # Extract sensor detections from triggered events
    thermal_anomalies = extract_thermal_detections(events, elapsed_seconds, terrain_sectors, agents)
    audio_events_data = extract_audio_detections(events, elapsed_seconds, terrain_sectors, agents)
    
    # Build complete simulation state
    return {
        'mission': {
            'mission_id': mission_id,
            'name': mission_name,
            'use_case': scenario.use_case,
            'status': status,
        },
        'simulation_clock': {
            'started_at': None,  # Would come from Mission model
            'elapsed_seconds': round(elapsed_seconds, 1),
            'speed_multiplier': speed_multiplier,
            'is_running': status == 'running',
        },
        'navigation_model': {
            'origin_position': origin_position,
            'coordinate_system': 'local_mission_3d_grid',
        },
        'sectors': sectors_detailed,
        'paths': [],  # TODO: Load from Digital Twin
        'agents': agents,
        'network': {
            'mesh_health': 85,  # Simplified
            'total_nodes': len(agents),
            'relay_nodes': sum(1 for a in agents if a['role'] == 'relay'),
        },
        'map': {
            'coverage_percent': round(len(explored_sector_ids) / len(terrain_sectors) * 100, 1) if terrain_sectors else 0,
            'confidence': 0.75,  # Simplified
            'total_points': len(explored_sector_ids) * 1000,  # Approximate point count
        },
        'sensors': {
            'thermal_anomalies': thermal_anomalies,
            'audio_events': audio_events_data,
            'gas_readings': [],  # TODO: Extract from scenario events
        },
        'events': timeline_events,
        'audio_detections': audio_events_data,  # Same data, different format expected by some components
        'ai_analysis': {},  # TODO: Build from scenario
    }


def format_time(seconds: float) -> str:
    """Format elapsed seconds as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
