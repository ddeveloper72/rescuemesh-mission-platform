"""
Test scenario engine by generating simulation state at various time points.

Usage:
    python manage.py test_scenario_engine
    python manage.py test_scenario_engine --scenario collapsed-building-alpha-01 --time 120
"""
from django.core.management.base import BaseCommand
from apps.missions.services.scenario_engine import generate_simulation_state_from_scenario


class Command(BaseCommand):
    help = 'Test scenario engine by generating simulation state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            default='collapsed-building-alpha-01',
            help='Scenario ID to test',
        )
        parser.add_argument(
            '--time',
            type=float,
            default=60.0,
            help='Elapsed seconds to simulate',
        )

    def handle(self, *args, **options):
        scenario_id = options['scenario']
        elapsed_seconds = options['time']
        
        self.stdout.write(f'\n=== Testing Scenario Engine ===')
        self.stdout.write(f'Scenario: {scenario_id}')
        self.stdout.write(f'Time: {elapsed_seconds}s\n')
        
        try:
            # Generate simulation state
            state = generate_simulation_state_from_scenario(
                mission_id='test-mission-001',
                scenario_id=scenario_id,
                elapsed_seconds=elapsed_seconds,
                speed_multiplier=1.0,
                mission_name='Test Mission',
                status='running'
            )
            
            # Display results
            self.stdout.write(self.style.SUCCESS(f'✓ Scenario loaded successfully'))
            
            self.stdout.write(f'\nMission:')
            self.stdout.write(f'  - ID: {state["mission"]["mission_id"]}')
            self.stdout.write(f'  - Name: {state["mission"]["name"]}')
            self.stdout.write(f'  - Use Case: {state["mission"]["use_case"]}')
            self.stdout.write(f'  - Status: {state["mission"]["status"]}')
            
            self.stdout.write(f'\nSimulation Clock:')
            self.stdout.write(f'  - Elapsed: {state["simulation_clock"]["elapsed_seconds"]}s')
            self.stdout.write(f'  - Running: {state["simulation_clock"]["is_running"]}')
            
            self.stdout.write(f'\nAgents: {len(state["agents"])} active')
            for agent in state["agents"]:
                self.stdout.write(f'  - {agent["name"]} ({agent["role"]}):')
                self.stdout.write(f'      State: {agent["state"]}')
                self.stdout.write(f'      Battery: {agent["battery_percent"]}%')
                self.stdout.write(f'      Location: {agent["location_label"]}')
                self.stdout.write(f'      Position: ({agent["position"]["x"]:.1f}, {agent["position"]["y"]:.1f}, {agent["position"]["z"]:.1f})')
            
            self.stdout.write(f'\nSectors: {len(state["sectors"])} total')
            explored = [s for s in state["sectors"] if s["confidence"] > 0]
            self.stdout.write(f'  - Explored: {len(explored)}')
            for sector in explored:
                self.stdout.write(f'      {sector["label"]}: {sector["confidence"]*100:.0f}% confidence')
            
            self.stdout.write(f'\nEvents: {len(state["events"])} triggered')
            for event in state["events"]:
                self.stdout.write(f'  - [{event["timestamp"]}] {event["title"]}')
            
            self.stdout.write(f'\nMap Coverage: {state["map"]["coverage_percent"]:.1f}%')
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Test completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Test failed: {e}'))
            import traceback
            traceback.print_exc()
