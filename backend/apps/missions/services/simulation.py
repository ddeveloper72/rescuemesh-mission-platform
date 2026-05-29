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
        'ai_analysis': ai_analysis
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
    
    TODO: Implement detailed cave rescue simulation logic.
    TODO: Model narrow passages, relay chain building, path discovery.
    TODO: Model GPS denial, radio attenuation, water hazards.
    """
    # Placeholder implementation
    return create_placeholder_state(
        mission_id, mission_name, 'cave-rescue', elapsed_seconds,
        speed_multiplier, started_at, status,
        placeholder_message='Cave rescue simulation - basic mapping and relay'
    )


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
    
    TODO: Implement amphibious agent simulation.
    TODO: Model water depth, sonar mapping, buoyancy control.
    TODO: Model corrosion risk, water quality sensors.
    """
    # Placeholder implementation
    return create_placeholder_state(
        mission_id, mission_name, 'flooded-structure', elapsed_seconds,
        speed_multiplier, started_at, status,
        placeholder_message='Flooded structure simulation - amphibious inspection'
    )


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
    
    TODO: Implement gas detection simulation.
    TODO: Model confined space hazards, ventilation status.
    TODO: Model equipment inspection, structural integrity checks.
    """
    # Placeholder implementation
    return create_placeholder_state(
        mission_id, mission_name, 'industrial-inspection', elapsed_seconds,
        speed_multiplier, started_at, status,
        placeholder_message='Industrial inspection simulation - hazard detection'
    )


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
