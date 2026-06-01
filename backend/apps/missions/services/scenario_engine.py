"""
Mission Scenario Engine

Data-driven simulation engine that reads mission scenarios from the database
and generates simulation state based on agent routes, waypoints, and timeline events.

Replaces hardcoded simulation logic with reusable, configurable mission scripts.
"""
from typing import Dict, List, Any, Optional
import math
from functools import lru_cache
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


@lru_cache(maxsize=32)
def load_scenario_cached(scenario_id: str) -> Dict[str, Any]:
    """
    Cached version of load_scenario.
    
    Scenarios are static during runtime - they only change when database is updated.
    This eliminates redundant database queries for the same scenario.
    
    Cache is cleared on server restart or when maxsize is exceeded.
    
    Args:
        scenario_id: Unique scenario identifier
        
    Returns:
        Dictionary with scenario, routes, waypoints, events
    """
    return load_scenario(scenario_id)


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


@lru_cache(maxsize=32)
def get_terrain_sectors_cached(site_slug: str, terrain_slug: str) -> Dict[str, TerrainSector]:
    """
    Cached version of get_terrain_sectors.
    
    Terrain geometry is static - sectors never change during runtime.
    This eliminates redundant database queries for the same terrain.
    
    Cache is cleared on server restart or when maxsize is exceeded.
    
    Performance impact: Reduces ~90 queries/minute to ~1 query on first access.
    
    Args:
        site_slug: Digital twin site identifier
        terrain_slug: Terrain map identifier
        
    Returns:
        Dictionary mapping sector_id to TerrainSector object
    """
    return get_terrain_sectors(site_slug, terrain_slug)


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


def extract_environmental_readings(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector],
    agents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extract environmental sensor readings from scenario events.
    
    Looks for sensor_reading events and formats them for display.
    """
    readings = []
    
    for event in events:
        if event.event_type == 'sensor_reading' and event.trigger_at_seconds <= elapsed_seconds:
            # Get location from sector or agent
            location_label = 'Unknown'
            if event.sector_id and event.sector_id in terrain_sectors:
                location_label = terrain_sectors[event.sector_id].label
            elif event.agent_id:
                agent = next((a for a in agents if a['agent_id'] == event.agent_id), None)
                if agent:
                    location_label = agent.get('location_label', 'Unknown')
            
            # Extract sensor data from event_data
            sensor_type = event.event_data.get('sensor_type', 'unknown')
            value = event.event_data.get('value', 0)
            unit = event.event_data.get('unit', '')
            status = event.event_data.get('status', 'normal')
            display_name = event.event_data.get('display_name', event.title)
            
            reading = {
                'sensor_type': sensor_type,
                'display_name': display_name,
                'value': value,
                'unit': unit,
                'status': status,
                'location_label': location_label,
                'confidence': int(event.event_data.get('confidence', 90)),
                'detected_at': int(event.trigger_at_seconds),
                'timestamp': format_time(event.trigger_at_seconds),
                'location': location_label
            }
            readings.append(reading)
    
    return readings


def extract_lighting_state(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    agents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract current lighting mode and state from scenario events.
    
    Returns the most recent lighting_mode_change event for each agent.
    """
    lighting_states = {}
    
    for event in events:
        if event.event_type == 'lighting_mode_change' and event.trigger_at_seconds <= elapsed_seconds:
            if event.agent_id:
                lighting_states[event.agent_id] = {
                    'agent_id': event.agent_id,
                    'current_mode': event.event_data.get('new_mode', 'low_light_rgb'),
                    'previous_mode': event.event_data.get('previous_mode', 'low_light_rgb'),
                    'light_active': event.event_data.get('light_active', False),
                    'light_intensity_percent': event.event_data.get('light_intensity_percent', 0),
                    'battery_cost_percent_per_second': event.event_data.get('battery_impact', 0),
                    'image_confidence': event.event_data.get('image_confidence', 0.5),
                    'confidence_penalty_factors': event.event_data.get('confidence_penalty_factors', {}),
                    'changed_at_seconds': event.trigger_at_seconds,
                    'reason': event.event_data.get('reason', 'operator_command'),
                }
    
    return lighting_states


def extract_seismic_detections(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector]
) -> List[Dict[str, Any]]:
    """
    Extract seismic/acoustic ground sensor detections from scenario events.
    
    Returns list of seismic sensor nodes and their detections.
    """
    sensors = {}
    detections = []
    
    for event in events:
        if event.trigger_at_seconds > elapsed_seconds:
            continue
        
        if event.event_type == 'seismic_sensor_deployed':
            sensor_id = event.event_data.get('sensor_id', f"seismic-{event.id}")
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            sensors[sensor_id] = {
                'sensor_id': sensor_id,
                'state': 'listening',
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'sector_id': event.sector_id,
                'position': {
                    'x_m': sector.x_m if sector else 0,
                    'y_m': sector.y_m if sector else 0,
                    'z_m': sector.z_m if sector else 0,
                },
                'deployed_at_seconds': event.trigger_at_seconds,
                'background_noise_level': event.event_data.get('background_noise_level', 0.35),
                'detection_threshold': event.event_data.get('detection_threshold', 0.50),
                'detections': [],
            }
        
        elif event.event_type == 'seismic_detection':
            sensor_id = event.event_data.get('sensor_id', 'seismic-unknown')
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            detection = {
                'id': f"seismic-det-{event.id}",
                'sensor_id': sensor_id,
                'detected_at_seconds': event.trigger_at_seconds,
                'timestamp': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'type': event.event_data.get('type', 'unknown'),
                'confidence': event.event_data.get('confidence', 0.5),
                'pattern': event.event_data.get('pattern', ''),
                'frequency_hz': event.event_data.get('frequency_hz', 0),
                'human_cue_probability': event.event_data.get('human_cue_probability', 0),
                'classification': event.event_data.get('classification', 'unknown'),
                'requires_human_review': event.event_data.get('requires_human_review', False),
                'description': event.description or event.title,
            }
            detections.append(detection)
            
            # Add to sensor's detection list if sensor exists
            if sensor_id in sensors:
                sensors[sensor_id]['detections'].append(detection)
    
    return {
        'sensors': list(sensors.values()),
        'detections': detections,
    }


def extract_hydrophone_detections(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector]
) -> List[Dict[str, Any]]:
    """
    Extract hydrophone/water acoustic detections from scenario events.
    
    Returns list of hydrophone sensors and their detections.
    """
    hydrophones = {}
    detections = []
    
    for event in events:
        if event.trigger_at_seconds > elapsed_seconds:
            continue
        
        if event.event_type == 'hydrophone_deployed':
            sensor_id = event.event_data.get('sensor_id', f"hydrophone-{event.id}")
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            hydrophones[sensor_id] = {
                'sensor_id': sensor_id,
                'state': event.event_data.get('state', 'deployed_submerged'),
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'sector_id': event.sector_id,
                'position': {
                    'x_m': sector.x_m if sector else 0,
                    'y_m': sector.y_m if sector else 0,
                    'z_m': sector.z_m if sector else 0,
                },
                'water_depth_m': event.event_data.get('water_depth_m', 0),
                'deployed_at_seconds': event.trigger_at_seconds,
                'turbulence_level': event.event_data.get('turbulence_level', 0.3),
                'detections': [],
            }
        
        elif event.event_type == 'hydrophone_detection':
            sensor_id = event.event_data.get('sensor_id', 'hydrophone-unknown')
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            detection = {
                'id': f"hydrophone-det-{event.id}",
                'sensor_id': sensor_id,
                'detected_at_seconds': event.trigger_at_seconds,
                'timestamp': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'detection_type': event.event_data.get('detection_type', 'unknown'),
                'confidence': event.event_data.get('confidence', 0.5),
                'frequency_range': event.event_data.get('frequency_range', 'Unknown'),
                'flow_direction': event.event_data.get('flow_direction', ''),
                'intensity': event.event_data.get('intensity', 'moderate'),
                'classification': event.event_data.get('classification', 'unknown'),
                'description': event.description or event.title,
            }
            detections.append(detection)
            
            # Add to hydrophone's detection list if hydrophone exists
            if sensor_id in hydrophones:
                hydrophones[sensor_id]['detections'].append(detection)
    
    return {
        'hydrophones': list(hydrophones.values()),
        'detections': detections,
    }


def extract_talkback_events(
    events: List[ScenarioEvent],
    elapsed_seconds: float,
    terrain_sectors: Dict[str, TerrainSector],
    agents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract talkback/survivor communication events from scenario.
    
    Returns talkback messages sent and responses received.
    """
    talkback_messages = []
    talkback_responses = []
    talkback_capability = {
        'talkback_available': False,
        'speaker_available': False,
        'microphone_available': False,
        'available_agents': [],
    }
    
    # Check which agents have talkback capability
    for agent in agents:
        if agent.get('state') in ['active', 'deployed', 'landed_relay']:
            sensors = agent.get('sensors', [])
            has_speaker = any('speaker' in s.lower() or 'talkback' in s.lower() for s in sensors)
            has_mic = any('microphone' in s.lower() or 'mic' in s.lower() for s in sensors)
            
            if has_speaker or has_mic:
                talkback_capability['talkback_available'] = True
                talkback_capability['speaker_available'] = talkback_capability['speaker_available'] or has_speaker
                talkback_capability['microphone_available'] = talkback_capability['microphone_available'] or has_mic
                talkback_capability['available_agents'].append({
                    'agent_id': agent['agent_id'],
                    'name': agent['name'],
                    'has_speaker': has_speaker,
                    'has_microphone': has_mic,
                })
    
    # Extract messages and responses from events
    for event in events:
        if event.trigger_at_seconds > elapsed_seconds:
            continue
        
        if event.event_type == 'talkback_message_sent':
            agent = next((a for a in agents if a['agent_id'] == event.agent_id), None)
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            message = {
                'id': f"talkback-msg-{event.id}",
                'agent_id': event.agent_id,
                'agent_name': agent['name'] if agent else event.agent_id,
                'sent_at_seconds': event.trigger_at_seconds,
                'timestamp': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'message': event.event_data.get('message', event.title),
                'audio_link_quality': event.event_data.get('audio_link_quality', 0.5),
                'delivery_status': event.event_data.get('delivery_status', 'delivered'),
                'response_expected': event.event_data.get('response_expected', True),
                'response_window_seconds': event.event_data.get('response_window_seconds', 30),
            }
            talkback_messages.append(message)
        
        elif event.event_type == 'talkback_response_detected':
            sector = terrain_sectors.get(event.sector_id) if event.sector_id else None
            
            response = {
                'id': f"talkback-resp-{event.id}",
                'detected_at_seconds': event.trigger_at_seconds,
                'timestamp': format_time(event.trigger_at_seconds),
                'location': sector.label if sector else event.sector_id or 'Unknown',
                'original_message_at': event.event_data.get('original_message_at', 0),
                'response_type': event.event_data.get('response_type', 'unknown'),
                'tap_count': event.event_data.get('tap_count', 0),
                'confidence': event.event_data.get('confidence', 0.5),
                'requires_human_review': event.event_data.get('requires_human_review', True),
                'transcript': event.event_data.get('transcript', event.description or event.title),
                'description': event.description or event.title,
            }
            talkback_responses.append(response)
    
    return {
        'capability': talkback_capability,
        'messages': talkback_messages,
        'responses': talkback_responses,
    }


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
    # Load scenario (cached - static data)
    scenario_data = load_scenario_cached(scenario_id)
    scenario = scenario_data['scenario']
    routes = scenario_data['routes']
    events = scenario_data['events']
    
    # Load Digital Twin terrain (cached - static geometry)
    terrain_sectors = get_terrain_sectors_cached(
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
        
        # Calculate signal strength based on agent state and role
        if agent_state == 'sacrificed':
            # Sacrificed agents have no active radio transmission
            # Only NFC black-box recovery available
            signal_strength = 0
        elif agent_state == 'degraded':
            # Degraded agents have weakened signal
            signal_strength = 50
        elif route.agent_role == 'relay':
            # Relay nodes maintain strong signal as their primary function
            signal_strength = 95
        else:
            # Healthy mapper/scout agents
            signal_strength = 85
        
        # Get current sector
        sector_id = get_agent_sector_id(agent_position, terrain_sectors)
        current_sector = terrain_sectors.get(sector_id)
        location_label = current_sector.label if current_sector else 'Unknown'
        
        # Calculate navigation data for agent
        origin_position = {'x': 0, 'y': 0, 'z': 0}
        distance_3d = calculate_distance_3d(agent_position, origin_position)
        bearing = calculate_bearing_degrees(origin_position, agent_position)
        elevation_m, depth_m = calculate_elevation_depth(agent_position['z'])
        
        # Build agent dict
        agent = {
            'agent_id': route.agent_id,
            'name': route.agent_name,
            'role': route.agent_role,
            'state': agent_state,
            'battery_percent': int(agent_position['battery_percent']),
            'signal_strength': signal_strength,
            'location_label': location_label,
            'sector': sector_id,
            'position': {
                'x': agent_position['x'],
                'y': agent_position['y'],
                'z': agent_position['z'],
            },
            'navigation': {
                'straight_line_3d_distance_from_origin_m': round(distance_3d, 1),
                'bearing_from_origin_deg': round(bearing, 1) if bearing is not None else None,
                'bearing_from_origin_cardinal': bearing_to_cardinal(bearing) if bearing is not None else None,
                'elevation_m': round(elevation_m, 1) if elevation_m != 0 else None,
                'depth_m': round(depth_m, 1) if depth_m != 0 else None,
                'vertical_offset_from_origin_m': round(agent_position['z'], 1),
                'depth_elevation_label': format_depth_elevation_label(agent_position['z']),
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
    environmental_readings = extract_environmental_readings(events, elapsed_seconds, terrain_sectors, agents)
    
    # Extract capability pack data
    lighting_states = extract_lighting_state(events, elapsed_seconds, agents)
    seismic_data = extract_seismic_detections(events, elapsed_seconds, terrain_sectors)
    hydrophone_data = extract_hydrophone_detections(events, elapsed_seconds, terrain_sectors)
    talkback_data = extract_talkback_events(events, elapsed_seconds, terrain_sectors, agents)
    
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
            'mesh_health': 85,  # Simplified - could calculate from agent signal strengths
            'packet_loss_percent': 5,  # Simplified - low loss in cave with relays
            'base_signal_strength': 78,  # Simplified - degraded in cave environment
            'total_nodes': len(agents),
            'relay_nodes': sum(1 for a in agents if a['role'] == 'relay' or a['state'] == 'landed_relay'),
            'active_nodes': sum(1 for a in agents if a['state'] not in ['sacrificed', 'failed']),
            'relay_chain': [a['name'] for a in agents if a['role'] == 'relay' or a['state'] == 'landed_relay'],
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
            'environmental_readings': environmental_readings,
        },
        'lighting': lighting_states,
        'seismic': seismic_data,
        'hydrophone': hydrophone_data,
        'talkback': talkback_data,
        'events': timeline_events,
        'audio_detections': audio_events_data,  # Same data, different format expected by some components
        'ai_analysis': {
            'summary': 'Mission in progress - analyzing sensor data...' if len(agents) > 0 else 'No active agents',
            'confidence': 0.75 if len(audio_events_data) > 0 else 0.0,
        },
    }


def format_time(seconds: float) -> str:
    """Format elapsed seconds as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
