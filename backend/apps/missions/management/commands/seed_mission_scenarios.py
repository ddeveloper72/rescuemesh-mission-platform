"""
Import mission scenarios from JSON files.

Usage:
    python manage.py seed_mission_scenarios --file collapsed_building_scenario.json
    python manage.py seed_mission_scenarios --all  # Import all from data/scenarios/
"""
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from apps.missions.models_scenario import (
    MissionScenario,
    AgentRoute,
    RouteWaypoint,
    ScenarioEvent,
)


class Command(BaseCommand):
    help = 'Import mission scenarios from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='JSON file to import (relative to data/scenarios/)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Import all JSON files from data/scenarios/',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing scenarios with same scenario_id',
        )

    def handle(self, *args, **options):
        # Get project root directory (parent of backend/)
        project_root = Path(settings.BASE_DIR).parent
        base_dir = project_root / 'data' / 'scenarios'
        
        if not base_dir.exists():
            raise CommandError(f'Scenarios directory not found: {base_dir}')
        
        files_to_import = []
        
        if options['all']:
            # Import all JSON files
            for filepath in base_dir.glob('*.json'):
                files_to_import.append(filepath)
        elif options['file']:
            # Import specific file
            filepath = base_dir / options['file']
            if not filepath.exists():
                raise CommandError(f'File not found: {filepath}')
            files_to_import.append(filepath)
        else:
            raise CommandError('Must specify --file or --all')
        
        if not files_to_import:
            self.stdout.write(self.style.WARNING('No JSON files found'))
            return
        
        for filepath in files_to_import:
            self.import_scenario_file(filepath, options['overwrite'])

    @transaction.atomic
    def import_scenario_file(self, filepath, overwrite=False):
        """Import a single scenario JSON file."""
        self.stdout.write(f'\nImporting: {filepath}')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if scenario already exists
        scenario_id = data['scenario_id']
        existing_scenario = MissionScenario.objects.filter(scenario_id=scenario_id).first()
        
        if existing_scenario:
            if not overwrite:
                self.stdout.write(self.style.WARNING(
                    f'  Scenario "{scenario_id}" already exists. Use --overwrite to replace.'
                ))
                return
            else:
                self.stdout.write(self.style.WARNING(f'  Deleting existing scenario: {scenario_id}'))
                existing_scenario.delete()
        
        # Create scenario
        scenario = MissionScenario.objects.create(
            scenario_id=data['scenario_id'],
            name=data['name'],
            use_case=data['use_case'],
            digital_twin_site_slug=data.get('digital_twin_site_slug'),
            digital_twin_terrain_slug=data.get('digital_twin_terrain_slug'),
            estimated_duration_seconds=data.get('estimated_duration_seconds', 600),
            origin_sector_id=data.get('origin_sector_id', ''),
            allow_agent_deployment=data.get('allow_agent_deployment', False),
            allow_agent_redirect=data.get('allow_agent_redirect', False),
            allow_agent_recall=data.get('allow_agent_recall', False),
            description=data.get('description', ''),
            metadata=data.get('metadata', {}),
        )
        
        self.stdout.write(self.style.SUCCESS(f'  Created scenario: {scenario.name}'))
        
        # Create agent routes
        routes_created = 0
        for route_data in data.get('agent_routes', []):
            route = AgentRoute.objects.create(
                scenario=scenario,
                agent_id=route_data['agent_id'],
                agent_name=route_data['agent_name'],
                agent_role=route_data['agent_role'],
                deploy_at_seconds=route_data.get('deploy_at_seconds', 0),
                sensors=route_data.get('sensors', []),
                average_speed_m_per_s=route_data.get('average_speed_m_per_s', 2.0),
                battery_drain_rate_percent_per_second=route_data.get('battery_drain_rate_percent_per_second', 0.05),
                behavior=route_data.get('behavior', 'patrol'),
                metadata=route_data.get('metadata', {}),
            )
            
            # Create waypoints for this route
            waypoints_created = 0
            for wp_data in route_data.get('waypoints', []):
                RouteWaypoint.objects.create(
                    route=route,
                    sequence_order=wp_data['sequence_order'],
                    sector_id=wp_data['sector_id'],
                    override_x_m=wp_data.get('override_x_m'),
                    override_y_m=wp_data.get('override_y_m'),
                    override_z_m=wp_data.get('override_z_m'),
                    pause_duration_seconds=wp_data.get('pause_duration_seconds', 0),
                    action=wp_data.get('action', 'explore'),
                    metadata=wp_data.get('metadata', {}),
                )
                waypoints_created += 1
            
            routes_created += 1
            self.stdout.write(f'    Route: {route.agent_name} ({waypoints_created} waypoints)')
        
        # Create scenario events
        events_created = 0
        for event_data in data.get('events', []):
            ScenarioEvent.objects.create(
                scenario=scenario,
                trigger_at_seconds=event_data['trigger_at_seconds'],
                event_type=event_data['event_type'],
                agent_id=event_data.get('agent_id'),
                sector_id=event_data.get('sector_id'),
                title=event_data['title'],
                description=event_data.get('description', ''),
                severity=event_data.get('severity', 'info'),
                event_data=event_data.get('event_data', {}),
                requires_user_action=event_data.get('requires_user_action', False),
                user_action_type=event_data.get('user_action_type', ''),
                metadata=event_data.get('metadata', {}),
            )
            events_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'  Imported: {routes_created} routes, {events_created} events'
        ))
