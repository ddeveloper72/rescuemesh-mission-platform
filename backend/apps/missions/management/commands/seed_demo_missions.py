"""
Create demo missions with fixed UUIDs for live simulation pages.

This ensures the frontend can reliably connect to mission instances.
"""
from django.core.management.base import BaseCommand
from apps.missions.models import Mission
import uuid


class Command(BaseCommand):
    help = 'Create or update demo missions with fixed UUIDs for frontend'

    def handle(self, *args, **options):
        demo_missions = [
            {
                'id': 'c5d0ffd4-2fc8-4b45-841d-88ec93f27e8e',
                'name': 'Collapsed Building Search - Demo',
                'mission_id': 'demo-collapsed-building-001',
                'use_case_type': 'collapsed-building-search',
                'objective': 'Live demo mission for collapsed building search scenario',
            },
            {
                'id': '7a3e9b2c-1d4f-4e6a-8c5b-9f1e3a7d2b4c',
                'name': 'Cave Rescue - Demo',
                'mission_id': 'demo-cave-rescue-001',
                'use_case_type': 'cave-rescue',
                'objective': 'Live demo mission for cave rescue scenario',
            },
            {
                'id': '5f8c2a1b-3e7d-4a9c-8b6f-1e4d7a2c9b5e',
                'name': 'Flooded Structure - Demo',
                'mission_id': 'demo-flooded-structure-001',
                'use_case_type': 'flooded-structure-inspection',
                'objective': 'Live demo mission for flooded structure inspection scenario',
            },
            {
                'id': '8d1f6c3b-2e5a-4b7c-9d3f-6e2a8c1b4d7f',
                'name': 'Industrial Inspection - Demo',
                'mission_id': 'demo-industrial-inspection-001',
                'use_case_type': 'industrial-inspection',
                'objective': 'Live demo mission for industrial confined space inspection scenario',
            },
            {
                'id': '2b4d7f1e-6c9a-4e3b-8f5d-1c7a3e9b2d6f',
                'name': 'Archaeological Exploration - Demo',
                'mission_id': 'demo-archaeological-exploration-001',
                'use_case_type': 'archaeological-exploration',
                'objective': 'Live demo mission for archaeological underground exploration scenario',
            },
        ]

        for mission_data in demo_missions:
            mission_id = uuid.UUID(mission_data['id'])
            mission, created = Mission.objects.update_or_create(
                id=mission_id,
                defaults={
                    'name': mission_data['name'],
                    'mission_id': mission_data['mission_id'],
                    'use_case_type': mission_data['use_case_type'],
                    'objective': mission_data['objective'],
                    'status': 'planned',
                    'simulation_seed': 42,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created mission: {mission.name} ({mission.id})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Updated mission: {mission.name} ({mission.id})'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(demo_missions)} demo missions ready'))
