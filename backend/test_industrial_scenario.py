#!/usr/bin/env python
"""Test industrial inspection scenario engine output."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.missions.services.scenario_engine import generate_simulation_state_from_scenario

# Test at 20 seconds (should have all 3 agents deployed now)
print("=" * 60)
print("TESTING INDUSTRIAL INSPECTION AT 20 SECONDS")
print("=" * 60)

try:
    state = generate_simulation_state_from_scenario(
        mission_id='test-mission',
        scenario_id='industrial-inspection-alpha-01',
        elapsed_seconds=20,
        speed_multiplier=1.0,
        mission_name='Test Industrial Inspection',
        status='running'
    )
    
    print(f"\n✓ Scenario engine executed successfully")
    print(f"\nAgents: {len(state.get('agents', []))}")
    for agent in state.get('agents', []):
        print(f"  - {agent['agent_id']}: {agent['name']}")
        print(f"    State: {agent['state']}")
        print(f"    Battery: {agent['battery_percent']}%")
        pos = agent.get('position', {})
        print(f"    Position: ({pos.get('x')}, {pos.get('y')}, {pos.get('z')})")
    
    print(f"\nSectors visible: {len([s for s in state.get('sectors', []) if s.get('confidence', 0) > 0])}")
    print(f"Events: {len(state.get('events', []))}")
    
    # Check if agents exist but aren't being returned
    if len(state.get('agents', [])) == 0:
        print("\n❌ ERROR: No agents in state!")
        print("\nFull state keys:", list(state.keys()))
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
