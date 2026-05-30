"""
Mission navigation utilities for distance and bearing calculations.

Provides local mission coordinate-based navigation for GPS-denied environments.
Uses a simple 2D/3D Euclidean coordinate system with configurable origin.

This module supports:
- Straight-line distance calculations
- Route distance calculations (sum of path segments)
- Bearing calculations (compass heading in degrees)
- Cardinal direction conversion
- Contact path length through relay mesh

Future compatibility:
- Can be extended for GeoJSON/PostGIS integration
- Compatible with ROS path/waypoint data structures
- Supports 3D coordinates for vertical positioning
"""

import math
from typing import Dict, List, Tuple, Optional, Any


# Cardinal direction labels (16-point compass)
CARDINAL_16 = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW'
]


def calculate_distance_2d(point_a: Dict[str, float], point_b: Dict[str, float]) -> float:
    """
    Calculate straight-line (Euclidean) distance between two points in 2D.
    
    Args:
        point_a: Dictionary with 'x' and 'y' keys (in metres)
        point_b: Dictionary with 'x' and 'y' keys (in metres)
        
    Returns:
        Distance in metres
    """
    dx = point_b['x'] - point_a['x']
    dy = point_b['y'] - point_a['y']
    return math.sqrt(dx * dx + dy * dy)


def calculate_distance_3d(point_a: Dict[str, float], point_b: Dict[str, float]) -> float:
    """
    Calculate straight-line (Euclidean) distance between two points in 3D.
    
    Args:
        point_a: Dictionary with 'x', 'y', and 'z' keys (in metres)
        point_b: Dictionary with 'x', 'y', and 'z' keys (in metres)
        
    Returns:
        Distance in metres
    """
    dx = point_b['x'] - point_a['x']
    dy = point_b['y'] - point_a['y']
    dz = point_b.get('z', 0) - point_a.get('z', 0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def calculate_bearing_degrees(from_point: Dict[str, float], to_point: Dict[str, float]) -> float:
    """
    Calculate compass bearing from one point to another.
    
    Uses mission coordinate system where:
    - Y-axis points north (smaller Y = more north)
    - X-axis points east (larger X = more east)
    - 0° = North
    - 90° = East
    - 180° = South
    - 270° = West
    
    Args:
        from_point: Starting point with 'x' and 'y' keys
        to_point: Destination point with 'x' and 'y' keys
        
    Returns:
        Bearing in degrees (0-359)
    """
    dx = to_point['x'] - from_point['x']
    dy = to_point['y'] - from_point['y']
    
    # Calculate angle from positive X-axis (East)
    # atan2 returns angle in radians from -π to +π
    angle_radians = math.atan2(dx, -dy)  # Negative dy because SVG Y increases downward
    
    # Convert to degrees
    angle_degrees = math.degrees(angle_radians)
    
    # Normalize to 0-359
    bearing = angle_degrees % 360
    
    return bearing


def bearing_to_cardinal(bearing_degrees: float, points: int = 16) -> str:
    """
    Convert bearing in degrees to cardinal direction.
    
    Args:
        bearing_degrees: Bearing in degrees (0-359)
        points: Number of compass points (8 or 16)
        
    Returns:
        Cardinal direction string (e.g., 'NNE', 'E', 'SSW')
    """
    if points == 8:
        cardinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(bearing_degrees / 45) % 8
        return cardinals[index]
    else:  # 16-point compass
        index = round(bearing_degrees / 22.5) % 16
        return CARDINAL_16[index]


def calculate_route_distance(
    waypoints: List[Dict[str, float]],
    use_3d: bool = False
) -> float:
    """
    Calculate total route distance by summing path segments.
    
    Args:
        waypoints: List of points with 'x', 'y', and optionally 'z' keys
        use_3d: Whether to include Z-axis in distance calculation
        
    Returns:
        Total route distance in metres
    """
    if len(waypoints) < 2:
        return 0.0
    
    total_distance = 0.0
    distance_func = calculate_distance_3d if use_3d else calculate_distance_2d
    
    for i in range(len(waypoints) - 1):
        segment_distance = distance_func(waypoints[i], waypoints[i + 1])
        total_distance += segment_distance
    
    return total_distance


def calculate_path_segments(
    waypoints: List[Dict[str, Any]],
    use_3d: bool = False
) -> List[Dict[str, Any]]:
    """
    Calculate distance and bearing for each path segment.
    
    Args:
        waypoints: List of waypoint dictionaries with 'x', 'y', optional 'z'
        use_3d: Whether to use 3D distance calculation
        
    Returns:
        List of segment dictionaries with distance and bearing
    """
    if len(waypoints) < 2:
        return []
    
    segments = []
    distance_func = calculate_distance_3d if use_3d else calculate_distance_2d
    
    for i in range(len(waypoints) - 1):
        from_wp = waypoints[i]
        to_wp = waypoints[i + 1]
        
        distance = distance_func(from_wp, to_wp)
        bearing = calculate_bearing_degrees(from_wp, to_wp)
        cardinal = bearing_to_cardinal(bearing)
        
        segment = {
            'from': from_wp.get('label', f'Waypoint {i}'),
            'to': to_wp.get('label', f'Waypoint {i + 1}'),
            'distance_m': round(distance, 1),
            'bearing_deg': round(bearing, 1),
            'bearing_cardinal': cardinal,
        }
        
        segments.append(segment)
    
    return segments


def find_nearest_relay(
    position: Dict[str, float],
    relays: List[Dict[str, Any]],
    use_3d: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Find the nearest relay to a given position.
    
    Args:
        position: Current position with 'x', 'y', optional 'z'
        relays: List of relay dictionaries with position data
        use_3d: Whether to use 3D distance calculation
        
    Returns:
        Dictionary with nearest relay info, or None if no relays
    """
    if not relays:
        return None
    
    distance_func = calculate_distance_3d if use_3d else calculate_distance_2d
    nearest_relay = None
    nearest_distance = float('inf')
    
    for relay in relays:
        relay_pos = relay.get('position', {})
        if not relay_pos:
            continue
        
        distance = distance_func(position, relay_pos)
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_relay = relay
    
    if nearest_relay:
        relay_pos = nearest_relay.get('position', {})
        bearing = calculate_bearing_degrees(position, relay_pos)
        
        return {
            'relay_id': nearest_relay.get('agent_id'),
            'relay_name': nearest_relay.get('name'),
            'distance_m': round(nearest_distance, 1),
            'bearing_deg': round(bearing, 1),
            'bearing_cardinal': bearing_to_cardinal(bearing),
        }
    
    return None


def calculate_contact_path_length(
    agent_position: Dict[str, float],
    relay_chain: List[Dict[str, Any]],
    base_position: Dict[str, float],
    use_3d: bool = False
) -> float:
    """
    Calculate total contact path length through relay mesh to base.
    
    This represents the actual communication path, not straight-line distance.
    
    Args:
        agent_position: Agent's current position
        relay_chain: Ordered list of relays from agent to base
        base_position: Base station position
        use_3d: Whether to use 3D distance calculation
        
    Returns:
        Total contact path length in metres
    """
    if not relay_chain:
        # Direct to base
        distance_func = calculate_distance_3d if use_3d else calculate_distance_2d
        return distance_func(agent_position, base_position)
    
    # Build complete path: agent -> relays -> base
    path_points = [agent_position]
    for relay in relay_chain:
        relay_pos = relay.get('position', {})
        if relay_pos:
            path_points.append(relay_pos)
    path_points.append(base_position)
    
    return calculate_route_distance(path_points, use_3d)


def estimate_return_time(
    route_distance_m: float,
    average_speed_m_per_s: float,
    safety_margin: float = 1.2
) -> float:
    """
    Estimate return time based on route distance and agent speed.
    
    Args:
        route_distance_m: Route distance to travel in metres
        average_speed_m_per_s: Agent's average speed in metres per second
        safety_margin: Safety multiplier for conservative estimates (default 1.2 = 20% margin)
        
    Returns:
        Estimated return time in seconds
    """
    if average_speed_m_per_s <= 0:
        return float('inf')
    
    base_time = route_distance_m / average_speed_m_per_s
    return base_time * safety_margin


def calculate_compass_confidence(
    environment_type: str,
    distance_from_origin_m: float,
    has_metal_nearby: bool = False,
    has_electrical_interference: bool = False
) -> Tuple[float, str, str]:
    """
    Calculate compass reliability based on environment conditions.
    
    Magnetometers can be affected by:
    - Steel reinforcement / metal structures
    - Electrical interference
    - Rock composition (caves)
    - Water (flooded structures)
    - Confined spaces
    
    Args:
        environment_type: Type of environment ('collapsed_building', 'cave', 'flooded', 'industrial')
        distance_from_origin_m: Distance from entry/base
        has_metal_nearby: Whether metal structures are nearby
        has_electrical_interference: Whether electrical interference is present
        
    Returns:
        Tuple of (confidence 0-1, reliability label, reason string)
    """
    confidence = 1.0
    reliability = 'good'
    reasons = []
    
    # Base degradation by environment type
    if environment_type == 'collapsed_building':
        confidence -= 0.15
        reasons.append('reinforced concrete')
        if has_metal_nearby:
            confidence -= 0.20
            reasons.append('steel debris')
    elif environment_type == 'cave':
        confidence -= 0.10
        reasons.append('rock composition')
        if distance_from_origin_m > 50:
            confidence -= 0.05
            reasons.append('depth')
    elif environment_type == 'flooded':
        confidence -= 0.12
        reasons.append('water')
        if has_metal_nearby:
            confidence -= 0.15
            reasons.append('submerged metal')
    elif environment_type == 'industrial':
        confidence -= 0.20
        reasons.append('metal structures')
        if has_electrical_interference:
            confidence -= 0.25
            reasons.append('electromagnetic interference')
    
    # Clamp confidence
    confidence = max(0.10, min(1.0, confidence))
    
    # Determine reliability label
    if confidence >= 0.85:
        reliability = 'good'
    elif confidence >= 0.65:
        reliability = 'acceptable'
    elif confidence >= 0.45:
        reliability = 'degraded'
    else:
        reliability = 'unreliable'
    
    reason_str = ' / '.join(reasons) if reasons else 'nominal'
    
    return confidence, reliability, reason_str
