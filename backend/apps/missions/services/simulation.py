"""
Mission simulation service.

This module provides deterministic, API-based simulation of mission scenarios.

NO WebSockets yet.
NO ROS yet.
NO real LiDAR yet.
NO Celery yet.

Simulation state is calculated on request based on:
- Mission start time
- Speed multiplier
- Use case type
- Elapsed mission time

All simulation logic is deterministic and reproducible given the same parameters.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import math
import random


def format_time(seconds: float) -> str:
    """
    Format elapsed seconds as MM:SS for timeline events.
    
    Args:
        seconds: Elapsed seconds
        
    Returns:
        Formatted time string (e.g., "02:30")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def calculate_terrain_reconstruction(
    sectors: List[Dict[str, Any]],
    agents: List[Dict[str, Any]],
    elapsed_seconds: float
) -> Dict[str, Any]:
    """
    Calculate progressive terrain reconstruction state for fog-of-war map reveal.
    
    Sectors are revealed as agents move through them. Multiple agents scanning
    the same sector increase confidence and detail level.
    
    Args:
        sectors: List of sector definitions with reveal timing and scan rules
        agents: List of active agents with their positions
        elapsed_seconds: Mission elapsed time
        
    Returns:
        Terrain reconstruction dict with overall stats and per-sector state
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
    
    This is the main entry point for simulation state calculation.
    Returns a complete dashboard state dictionary.
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
    
    # Drone A - Scout/Mapper
    drone_a_battery = max(5, 100 - (elapsed_seconds / 20))  # Drains slowly
    drone_a_signal = 72 + math.sin(elapsed_seconds / 30) * 8  # Fluctuates
    drone_a_state = 'healthy' if elapsed_seconds < 420 else 'degraded'
    
    agents.append({
        'agent_id': 'drone-a',
        'name': 'Scout Drone A',
        'role': 'Primary mapper',
        'state': drone_a_state,
        'battery_percent': int(drone_a_battery),
        'signal_strength': int(drone_a_signal),
        'location_label': 'Corridor A' if elapsed_seconds < 180 else 'Void 1',
        'position': {
            'x': 24 + (elapsed_seconds / 10),
            'y': 12 + (elapsed_seconds / 15),
            'z': 3
        },
        'sensors': ['LiDAR', 'Thermal', 'RGB'],
        'nfc_recovery_available': False
    })
    
    # Drone B - Detection drone
    drone_b_battery = max(3, 100 - (elapsed_seconds / 15))  # Drains faster
    drone_b_signal = 68 - (elapsed_seconds / 20) if elapsed_seconds < 360 else 45
    
    if elapsed_seconds < 300:
        drone_b_state = 'healthy'
        drone_b_location = 'Entrance void'
    elif elapsed_seconds < 360:
        drone_b_state = 'degraded'
        drone_b_location = 'Corridor B'
    else:
        drone_b_state = 'landed_relay'
        drone_b_location = 'Corridor B (relay)'
    
    agents.append({
        'agent_id': 'drone-b',
        'name': 'Thermal/Audio Drone',
        'role': 'Detection',
        'state': drone_b_state,
        'battery_percent': int(drone_b_battery),
        'signal_strength': int(drone_b_signal),
        'location_label': drone_b_location,
        'position': {
            'x': 18 + (elapsed_seconds / 12),
            'y': 7 + (elapsed_seconds / 18),
            'z': 1.5
        },
        'sensors': ['Thermal', 'Microphone Array', 'WiFi Scanner'],
        'nfc_recovery_available': drone_b_state == 'landed_relay'
    })
    
    # Drone C - Relay (eventually sacrificed)
    drone_c_battery = max(0, 100 - (elapsed_seconds / 18))
    drone_c_signal = 88 if elapsed_seconds < 240 else 78
    
    if elapsed_seconds < 240:
        drone_c_state = 'healthy'
        drone_c_location = 'Entry point'
    elif elapsed_seconds < 420:
        drone_c_state = 'healthy'
        drone_c_location = 'Relay position'
    else:
        drone_c_state = 'sacrificed'
        drone_c_location = 'Relay position (sacrificed)'
    
    agents.append({
        'agent_id': 'drone-c',
        'name': 'Relay Drone',
        'role': 'Communications relay',
        'state': drone_c_state,
        'battery_percent': int(drone_c_battery),
        'signal_strength': int(drone_c_signal),
        'location_label': drone_c_location,
        'position': {
            'x': 8,
            'y': 4,
            'z': 2
        },
        'sensors': [],
        'nfc_recovery_available': drone_c_state == 'sacrificed'
    })
    
    # Static relay node
    agents.append({
        'agent_id': 'relay-1',
        'name': 'Static Relay Node',
        'role': 'Base relay',
        'state': 'active',
        'battery_percent': 100,  # Powered
        'signal_strength': 95,
        'location_label': 'Base station',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Network state
    base_signal = 88 - (elapsed_seconds / 60)
    packet_loss = min(15, 2 + (elapsed_seconds / 45))
    mesh_health = max(50, 90 - (elapsed_seconds / 20))
    
    relay_chain = ['base-station', 'relay-node-1']
    if drone_c_state != 'sacrificed':
        relay_chain.append('drone-c')
    if drone_b_state == 'landed_relay':
        relay_chain.append('drone-b')
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
    
    # Environmental sensors - O₂ and CO₂ for survivor detection
    # O₂ sensor appears at 60s when thermal/audio drone activates
    if elapsed_seconds >= 60:
        o2_value = max(19.8, 20.9 - (elapsed_seconds / 800))  # Slowly decreasing in confined space
        o2_status = 'normal' if o2_value >= 19.5 else 'watch' if o2_value >= 19.0 else 'warning'
        sensors['environmental_readings'].append({
            'sensor_type': 'oxygen',
            'display_name': 'O₂',
            'value': round(o2_value, 1),
            'unit': '%',
            'status': o2_status,
            'location_label': drone_b_location,
            'confidence': 0.88,
            'detected_at': 60,
            'timestamp': format_time(elapsed_seconds)
        })
    
    # CO₂ sensor appears at 90s
    if elapsed_seconds >= 90:
        # Higher CO₂ suggests human presence or confined space buildup
        co2_value = min(1500, 420 + (elapsed_seconds * 1.8))
        co2_status = 'normal' if co2_value <= 800 else 'watch' if co2_value <= 1000 else 'warning' if co2_value <= 1200 else 'critical'
        sensors['environmental_readings'].append({
            'sensor_type': 'carbon_dioxide',
            'display_name': 'CO₂',
            'value': int(co2_value),
            'unit': 'ppm',
            'status': co2_status,
            'location_label': drone_b_location,
            'confidence': 0.82,
            'detected_at': 90,
            'timestamp': format_time(elapsed_seconds)
        })
    
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
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction
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
    
    # Drone A: Scout with LiDAR/SLAM
    drone_a_battery = max(5, 100 - (elapsed_seconds / 22))  # Slower drain
    drone_a_signal = max(35, 95 - (elapsed_seconds / 8))  # Degrades with depth
    
    if elapsed_seconds < 60:
        drone_a_state = 'healthy'
        drone_a_loc = 'Entrance Chamber'
        drone_a_pos = {'x': 15 + (elapsed_seconds * 0.3), 'y': 8, 'z': 2}
    elif elapsed_seconds < 180:
        drone_a_state = 'healthy'
        drone_a_loc = 'Main Tunnel'
        drone_a_pos = {'x': 35 + ((elapsed_seconds - 60) * 0.2), 'y': 12 + ((elapsed_seconds - 60) * 0.1), 'z': 1}
    elif elapsed_seconds < 300:
        drone_a_state = 'healthy' if drone_a_signal > 50 else 'degraded'
        drone_a_loc = 'Junction Chamber'
        drone_a_pos = {'x': 58, 'y': 25, 'z': 0}
    else:
        drone_a_state = 'degraded'
        drone_a_loc = 'Deep Squeeze'
        drone_a_pos = {'x': 62 + ((elapsed_seconds - 300) * 0.1), 'y': 28, 'z': -2}
    
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
    
    # Static base relay
    agents.append({
        'agent_id': 'base-relay',
        'name': 'Cave Entrance Relay',
        'role': 'Base station relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 95,
        'location_label': 'Entrance',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'sensors': [],
        'nfc_recovery_available': False
    })
    
    # Network state
    if elapsed_seconds < 180:
        mesh_health = max(75, 95 - (elapsed_seconds / 15))
        relay_chain = ['base-relay', 'drone-a']
        packet_loss = min(10, elapsed_seconds / 20)
    elif elapsed_seconds < 300:
        mesh_health = max(65, 85 - ((elapsed_seconds - 180) / 12))
        relay_chain = ['base-relay', 'relay-1', 'drone-a']
        packet_loss = min(15, 5 + ((elapsed_seconds - 180) / 15))
    else:
        mesh_health = max(55, 70 - ((elapsed_seconds - 300) / 10))
        relay_chain = ['base-relay', 'relay-1', 'drone-a']
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
    
    # Humidity readings increase with depth
    base_humidity = 65 + (elapsed_seconds / 15)
    environmental_readings.append({
        'sensor_type': 'humidity',
        'value': min(95, base_humidity),
        'unit': '%',
        'location': drone_a_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Temperature drops with depth
    base_temp = 18 - (elapsed_seconds / 100)
    environmental_readings.append({
        'sensor_type': 'temperature',
        'value': max(12, base_temp),
        'unit': '°C',
        'location': drone_a_loc,
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
    
    # Environmental sensors - O₂ and CO₂ for cave atmosphere monitoring
    # O₂ sensor appears at 90s when micro mapper activates
    if elapsed_seconds >= 90:
        o2_value = max(19.5, 20.9 - (elapsed_seconds / 1200))  # Slowly decreasing in cave
        o2_status = 'normal' if o2_value >= 19.5 else 'watch' if o2_value >= 19.0 else 'warning'
        environmental_readings.append({
            'sensor_type': 'oxygen',
            'display_name': 'O₂',
            'value': round(o2_value, 1),
            'unit': '%',
            'status': o2_status,
            'location_label': drone_a_loc,
            'confidence': 0.85,
            'detected_at': 90,
            'timestamp': format_time(elapsed_seconds)
        })
    
    # CO₂ sensor appears at 120s
    if elapsed_seconds >= 120:
        # Cave CO₂ can build up but typically lower than collapsed building
        co2_value = min(1200, 380 + (elapsed_seconds * 1.2))
        co2_status = 'normal' if co2_value <= 800 else 'watch' if co2_value <= 1000 else 'warning'
        environmental_readings.append({
            'sensor_type': 'carbon_dioxide',
            'display_name': 'CO₂',
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
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction
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
    
    # Amphibious Unit A: Main explorer
    amp_a_battery = max(8, 100 - (elapsed_seconds / 20))  # Faster drain underwater
    amp_a_signal = max(25, 85 - (elapsed_seconds / 6))  # Water + concrete attenuation
    
    if elapsed_seconds < 60:
        amp_a_state = 'healthy'
        amp_a_loc = 'Entry Pool (surface)'
        amp_a_depth = 0.5
        amp_a_pos = {'x': 12, 'y': 8, 'z': -0.5}
    elif elapsed_seconds < 180:
        amp_a_state = 'healthy'
        amp_a_loc = 'Submerged Corridor'
        amp_a_depth = 2.8
        amp_a_pos = {'x': 25 + ((elapsed_seconds - 60) * 0.15), 'y': 15, 'z': -2.8}
    elif elapsed_seconds < 300:
        amp_a_state = 'degraded'  # Mobility issues
        amp_a_loc = 'Deep Chamber'
        amp_a_depth = 4.2
        amp_a_pos = {'x': 42, 'y': 22, 'z': -4.2}
    else:
        amp_a_state = 'degraded'
        amp_a_loc = 'Deep Chamber'
        amp_a_depth = 4.5
        amp_a_pos = {'x': 45, 'y': 25, 'z': -4.5}
    
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
    
    # Surface relay node
    agents.append({
        'agent_id': 'surface-relay',
        'name': 'Surface Relay Station',
        'role': 'Water-to-air relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 90,
        'location_label': 'Entry platform',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'sensors': [],
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
    
    # Water depth/pressure readings
    current_depth = min(4.5, elapsed_seconds / 80)
    environmental_readings.append({
        'sensor_type': 'water_depth',
        'value': round(current_depth, 1),
        'unit': 'm',
        'location': amp_a_loc,
        'timestamp': format_time(elapsed_seconds)
    })
    
    # Water temperature
    water_temp = max(8, 14 - (elapsed_seconds / 200))
    environmental_readings.append({
        'sensor_type': 'water_temperature',
        'value': round(water_temp, 1),
        'unit': '°C',
        'location': amp_a_loc,
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
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction
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
    
    # Inspection Drone A: Primary inspector
    drone_a_battery = max(10, 100 - (elapsed_seconds / 23))
    drone_a_signal = max(50, 90 - (elapsed_seconds / 12))  # EMI interference
    
    if elapsed_seconds < 60:
        drone_a_state = 'healthy'
        drone_a_loc = 'Plant Room'
        drone_a_pos = {'x': 15, 'y': 10, 'z': 2.5}
    elif elapsed_seconds < 180:
        drone_a_state = 'healthy'
        drone_a_loc = 'Pipe Gallery'
        drone_a_pos = {'x': 32 + ((elapsed_seconds - 60) * 0.2), 'y': 18, 'z': 4}
    elif elapsed_seconds < 300:
        drone_a_state = 'degraded'  # Reflective surfaces affecting sensors
        drone_a_loc = 'Tank Interior'
        drone_a_pos = {'x': 55, 'y': 25, 'z': 6}
    else:
        drone_a_state = 'degraded'  # EMI interference
        drone_a_loc = 'Duct Section'
        drone_a_pos = {'x': 68 + ((elapsed_seconds - 300) * 0.15), 'y': 30, 'z': 8}
    
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
    
    # Thermal specialist drone
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
            'position': {'x': 75, 'y': 35, 'z': 2},
            'sensors': ['High-res Thermal', 'Infrared'],
            'nfc_recovery_available': False
        })
    
    # Base station
    agents.append({
        'agent_id': 'base-station',
        'name': 'Industrial Base Station',
        'role': 'Command and relay',
        'state': 'active',
        'battery_percent': 100,
        'signal_strength': 95,
        'location_label': 'Entry point',
        'position': {'x': 0, 'y': 0, 'z': 0},
        'sensors': [],
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
            'display_name': 'Oxygen (O₂)',
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
            'display_name': 'Carbon Dioxide (CO₂)',
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
            'display_name': 'Hydrogen (H₂)',
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
            'display_name': 'Methane (CH₄)',
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
            'unit': '°C',
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
            'description': 'Elevated temperature (+22.5°C) detected, possible leak or friction',
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
            'description': 'Abnormal heat (+38.2°C) in electrical cabinet, immediate review required',
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
            'Thermal hotspot: Pipe Joint A3 (+22.5°C)',
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
        ai_summary = 'Critical thermal hotspot detected in Control Cabinet C2 (+38.2°C). Immediate human review required. Multiple defects ranked by severity.'
        priority_findings = [
            '🔴 CRITICAL: Control Cabinet C2 thermal hotspot (+38.2°C)',
            '🟠 HIGH: Pressure leak in Duct Section',
            '🟡 MODERATE: Pipe Joint A3 thermal anomaly (+22.5°C)',
            '🟡 MODERATE: Methane elevation in Pipe Gallery',
            '🟡 MODERATE: Abnormal vibration in Pipe Gallery'
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
        'agents': agents,
        'network': network,
        'map': map_data,
        'sensors': sensors,
        'events': events,
        'ai_analysis': ai_analysis,
        'terrain_reconstruction': terrain_reconstruction
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
