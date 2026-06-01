#!/usr/bin/env python
"""Test what the API is actually returning."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.missions.models import Mission, MissionSimulation
from apps.missions.services.simulation import calculate_mission_state

# Get the mission
mission = Mission.objects.get(id='7d9f9ad9-2144-4c89-8ef5-08bcf7c41916')
sim = MissionSimulation.objects.get(mission=mission)

print(f"Mission: {mission.name}")
print(f"Status: {sim.status}")
print(f"Elapsed: {sim.get_elapsed_seconds():.1f}s")
print()

# Test at 0 seconds (simulation not started)
print("=" * 60)
print("Testing at 0 seconds (not_started state)")
print("=" * 60)

state = calculate_mission_state(
    mission_id=mission.mission_id,
    mission_name=mission.name,
    use_case_slug='industrial-inspection',
    elapsed_seconds=0,
    speed_multiplier=sim.speed_multiplier,
    started_at=None,
    status='not_started',
    random_seed=sim.random_seed
)

print(f"\nAgents in state: {len(state.get('agents', []))}")
for agent in state.get('agents', []):
    print(f"  - {agent['agent_id']}: {agent['name']}")

print("\n" + "=" * 60)
print("Testing at 10 seconds (running state)")
print("=" * 60)

state = calculate_mission_state(
    mission_id=mission.mission_id,
    mission_name=mission.name,
    use_case_slug='industrial-inspection',
    elapsed_seconds=10,
    speed_multiplier=1.0,
    started_at=None,
    status='running',
    random_seed=sim.random_seed
)

print(f"\nAgents in state: {len(state.get('agents', []))}")
for agent in state.get('agents', []):
    print(f"  - {agent['agent_id']}: {agent['name']}")
    pos = agent.get('position', {})
    print(f"    Position: x={pos.get('x')}, y={pos.get('y')}, z={pos.get('z')}")
print(f"Visible sectors: {len(visible_sectors)}")
for sector in visible_sectors[:5]:
    print(f"  - {sector.get('id')}: {sector.get('label')} (confidence: {sector.get('confidence')})")

print(f"\nEvents: {len(state.get('events', []))}")
