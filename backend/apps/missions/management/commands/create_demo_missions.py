"""
Management command to create demo missions for simulation testing.
"""
from django.core.management.base import BaseCommand
from apps.missions.models import Mission, MissionSimulation
from apps.usecases.models import UseCaseTemplate
from django.utils import timezone
import uuid


class Command(BaseCommand):
    help = 'Create demo missions with simulations for all use cases'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo missions...')
        
        use_cases = UseCaseTemplate.objects.filter(is_demo=True)
        
        for use_case in use_cases:
            # Create mission
            mission_id = f"demo-{use_case.slug}"
            
            # Check if already exists
            if Mission.objects.filter(mission_id=mission_id).exists():
                self.stdout.write(
                    self.style.WARNING(f'Mission {mission_id} already exists, skipping.')
                )
                continue
            
            mission = Mission.objects.create(
                mission_id=mission_id,
                name=f"{use_case.title} - Demo",
                use_case_template=use_case,
                use_case_type=use_case.slug,
                status='planned',
                objective=use_case.objective,
                terrain_description=f"Demo simulation for {use_case.title}",
                simulation_seed=42,  # Reproducible seed
                metadata={
                    'is_demo': True,
                    'created_by': 'seed_command'
                }
            )
            
            # Create simulation
            simulation = MissionSimulation.objects.create(
                mission=mission,
                status='not_started',
                speed_multiplier=1.0,
                random_seed=42,
                scenario_config={
                    'use_case': use_case.slug,
                    'is_demo': True
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created mission: {mission.mission_id} (PK: {mission.pk})'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'  Simulation PK: {simulation.pk}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('\nDemo missions created successfully!'))
        self.stdout.write('\nYou can now access them at:')
        
        for use_case in use_cases:
            mission_id = f"demo-{use_case.slug}"
            try:
                mission = Mission.objects.get(mission_id=mission_id)
                self.stdout.write(f'  - {mission.name}: /demo/{use_case.slug}')
                self.stdout.write(f'    API: /api/v1/missions/{mission.pk}/state/')
            except Mission.DoesNotExist:
                pass
