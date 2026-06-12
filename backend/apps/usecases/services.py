"""
Use case service helpers.

These functions keep API views thin and provide one reusable place for shaping
demo profile data for the frontend mission dashboard.
"""
from typing import Any, Dict, List, Optional


MAP_TYPES = {
    'collapsed-building-search': 'void-map',
    'cave-rescue': 'cave-map',
    'flooded-structure': 'flood-map',
    'industrial-inspection': 'industrial-map',
    'archaeological-exploration': 'cave-map',
}

OUTPUT_TYPES = {
    '3d_map': '3d-map',
    'device_scan': 'device-scan',
    'relay_map': 'relay-map',
    'ai_analysis': 'ai-analysis',
}


def build_demo_profile(use_case) -> Dict[str, Any]:
    """
    Build a UseCaseDemoProfile-shaped dictionary for the frontend.

    This intentionally produces the same camelCase fields used by
    frontend/src/types/demo.ts so static demo pages and API-backed demo pages
    can share the same components.
    """
    terrain = _get_terrain(use_case)
    agents = _build_agents(use_case)
    expected_failures = _build_expected_failures(use_case)
    expected_outputs = _build_expected_outputs(use_case)
    comms_risk = _assess_comms_risk(terrain)

    return {
        'slug': use_case.slug,
        'title': use_case.title,
        'priority': _format_priority(use_case.priority),
        'missionId': f'mission-demo-{use_case.slug[:8]}',
        'status': 'Simulated',
        'missionObjective': use_case.objective,
        'terrain': {
            'type': terrain.terrain_type if terrain else '',
            'gps': _format_gps_status(terrain.gps_status) if terrain else 'Unknown',
            'communications': terrain.communication_conditions if terrain else comms_risk,
            'lighting': terrain.lighting_conditions if terrain else '',
            'hazards': terrain.hazards if terrain else [],
        },
        'agents': agents,
        'expectedFailures': expected_failures,
        'expectedOutputs': expected_outputs,
        'simulation': {
            'mapType': MAP_TYPES.get(use_case.slug, 'void-map'),
            'environmentTags': _environment_tags(terrain, use_case.slug),
            'defaultConfidence': _default_confidence(use_case.slug),
            'communicationRisk': comms_risk,
            'batteryRisk': _battery_risk(use_case.priority),
            'sensorRisk': _sensor_risk(terrain),
            'missionDurationMinutes': _mission_duration(use_case.slug),
        },
        'timeline': _generate_sample_timeline(use_case, agents, expected_failures),
        'aiAnalyst': _build_ai_analyst(use_case),
    }


def _get_terrain(use_case):
    try:
        return use_case.terrain
    except Exception:
        return None


def _build_agents(use_case) -> List[Dict[str, Any]]:
    agents = []
    state_cycle = ['healthy', 'healthy', 'degraded', 'landed_relay']
    battery_cycle = [82, 68, 41, 91]

    for index, agent_role in enumerate(use_case.agent_roles.all(), 1):
        sensor_names = [
            sensor.display_name
            for sensor in agent_role.sensor_packages.all()
        ]

        agents.append({
            'id': f'agent-{chr(96 + index)}',
            'name': agent_role.name,
            'role': agent_role.role,
            'description': agent_role.description,
            'state': state_cycle[(index - 1) % len(state_cycle)],
            'batteryPercent': battery_cycle[(index - 1) % len(battery_cycle)],
            'locationLabel': _agent_location_label(index, agent_role.agent_type),
            'capabilities': _normalise_list(agent_role.capabilities),
            'sensors': sensor_names,
            'nfcRecoveryAvailable': agent_role.agent_type in {'relay_node', 'sensor'},
        })

    return agents


def _build_expected_failures(use_case) -> List[Dict[str, Any]]:
    failures = []
    for failure in use_case.failure_profiles.all():
        failures.append({
            'name': failure.name,
            'affectedComponent': failure.affected_component,
            'severity': failure.severity,
            'description': failure.description,
            'dashboardEffect': failure.operator_message or _summarise_effects(failure.effects),
        })
    return failures


def _build_expected_outputs(use_case) -> List[Dict[str, Any]]:
    outputs = []
    queryset = use_case.expected_outputs.all().order_by('-display_priority')
    for output in queryset:
        outputs.append({
            'name': output.name,
            'outputType': OUTPUT_TYPES.get(output.output_type, output.output_type.replace('_', '-')),
            'description': output.description,
            'confidenceRequired': output.confidence_required or output.human_review_required,
        })
    return outputs


def _build_ai_analyst(use_case) -> Dict[str, Any]:
    first_prompt = use_case.ai_prompts.filter(is_active=True).first()
    if not first_prompt:
        return {
            'role': 'Mission Review Assistant',
            'promptSummary': 'Review mission data, sensor outputs, and confidence flags for human decision support.',
            'expectedFindings': [],
            'humanReviewRequired': True,
        }

    return {
        'role': first_prompt.role,
        'promptSummary': first_prompt.description,
        'expectedFindings': _expected_findings_from_outputs(use_case),
        'humanReviewRequired': first_prompt.requires_human_review,
    }


def _generate_sample_timeline(
    use_case,
    agents: List[Dict[str, Any]],
    failures: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    primary_agent_id = agents[0]['id'] if agents else None
    timeline = [
        {
            'time': '00:00',
            'eventType': 'mission-start',
            'title': 'Mission Started',
            'description': f'{use_case.title} mission initiated',
        },
        {
            'time': '02:30',
            'eventType': 'mapping',
            'title': 'Primary Mapping',
            'description': 'Initial terrain mapping and sensor checks underway',
            'assetId': primary_agent_id,
            'confidence': 0.85,
        },
    ]

    if failures:
        timeline.append({
            'time': '06:00',
            'eventType': 'failure',
            'title': failures[0]['name'],
            'description': failures[0]['description'],
            'assetId': primary_agent_id,
        })

    timeline.extend([
        {
            'time': '10:30',
            'eventType': 'sensor-detection',
            'title': 'Priority Sensor Review',
            'description': 'Sensor output flagged for operator review',
            'assetId': primary_agent_id,
            'confidence': 0.68,
        },
        {
            'time': '14:20',
            'eventType': 'ai-analysis',
            'title': 'AI Review Summary',
            'description': 'AI analyst prepares confidence-ranked findings',
            'confidence': 0.74,
        },
        {
            'time': '18:00',
            'eventType': 'mission-end',
            'title': 'Mission Profile Complete',
            'description': 'Demo profile summary ready for review',
        },
    ])
    return timeline


def _format_priority(priority: str) -> str:
    return priority.replace('_', ' ').title() if priority else 'Operational Review'


def _format_gps_status(gps_status: str) -> str:
    return gps_status.replace('_', ' ').title() if gps_status else 'Unknown'


def _assess_comms_risk(terrain) -> str:
    if not terrain:
        return 'medium'
    if terrain.gps_status == 'denied':
        return 'severe'
    if terrain.gps_status in {'degraded', 'intermittent'}:
        return 'high'
    return 'medium'


def _battery_risk(priority: str) -> str:
    return 'high' if priority == 'life_safety' else 'medium'


def _sensor_risk(terrain) -> str:
    if terrain and terrain.simulation_complexity in {'high', 'extreme'}:
        return 'high'
    return 'medium'


def _default_confidence(slug: str) -> float:
    return {
        'archaeological-exploration': 0.85,
        'industrial-inspection': 0.77,
        'collapsed-building-search': 0.72,
        'flooded-structure': 0.64,
        'cave-rescue': 0.68,
    }.get(slug, 0.75)


def _mission_duration(slug: str) -> int:
    return {
        'archaeological-exploration': 16,
        'industrial-inspection': 20,
        'collapsed-building-search': 18,
        'flooded-structure': 15,
        'cave-rescue': 22,
    }.get(slug, 18)


def _environment_tags(terrain, slug: str) -> List[str]:
    if terrain and terrain.hazards:
        return [str(tag).lower().replace(' ', '-') for tag in terrain.hazards[:5]]
    return slug.split('-')


def _agent_location_label(index: int, agent_type: str) -> str:
    if agent_type == 'relay_node':
        return 'Entry relay position'
    if index == 1:
        return 'Primary survey sector'
    return f'Sector {index}'


def _normalise_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return [str(key) for key, enabled in value.items() if enabled]
    if value:
        return [str(value)]
    return []


def _summarise_effects(effects: Optional[Dict[str, Any]]) -> str:
    if not effects:
        return 'Dashboard confidence and operator attention adjusted.'
    return '; '.join(f'{key}: {value}' for key, value in effects.items())


def _expected_findings_from_outputs(use_case) -> List[str]:
    findings = []
    for output in use_case.expected_outputs.all().order_by('-display_priority')[:4]:
        findings.append(f'{output.name}: {output.description}')
    return findings
