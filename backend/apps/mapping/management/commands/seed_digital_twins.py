"""
Management command to seed digital twin data from JSON files.

Usage:
    python manage.py seed_digital_twins
    python manage.py seed_digital_twins --clear  # Clear existing data first
"""
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.mapping.models import (
    DigitalTwinSite,
    TerrainMap,
    TerrainSector,
    TerrainPath,
    Waypoint,
)


class Command(BaseCommand):
    help = 'Seed digital twin data from JSON files in data/processed/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing digital twin data before seeding',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Specific JSON file to import (relative to data/processed/)',
        )

    def handle(self, *args, **options):
        # Determine project root
        project_root = Path(__file__).resolve().parents[5]
        data_dir = project_root / 'data' / 'processed'

        if not data_dir.exists():
            self.stdout.write(
                self.style.ERROR(
                    f'Data directory not found: {data_dir}'
                )
            )
            return

        # Optionally clear existing data
        if options['clear']:
            self.stdout.write('Clearing existing digital twin data...')
            with transaction.atomic():
                Waypoint.objects.all().delete()
                TerrainPath.objects.all().delete()
                TerrainSector.objects.all().delete()
                TerrainMap.objects.all().delete()
                DigitalTwinSite.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Determine which files to process
        if options['file']:
            json_files = [data_dir / options['file']]
        else:
            json_files = list(data_dir.glob('*.json'))

        if not json_files:
            self.stdout.write(
                self.style.WARNING(
                    f'No JSON files found in {data_dir}'
                )
            )
            return

        # Process each JSON file
        for json_file in json_files:
            self.stdout.write(f'\nProcessing {json_file.name}...')
            try:
                self.import_digital_twin(json_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {json_file.name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error importing {json_file.name}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted seeding {len(json_files)} digital twin(s)'
            )
        )

    @transaction.atomic
    def import_digital_twin(self, json_file_path):
        """Import a single digital twin from JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Create DigitalTwinSite
        site_data = data['site']
        site, created = DigitalTwinSite.objects.update_or_create(
            slug=site_data['slug'],
            defaults={
                'name': site_data['name'],
                'site_type': site_data['site_type'],
                'country': site_data.get('country', ''),
                'description': site_data['description'],
                'source_name': site_data['source_name'],
                'source_url': site_data.get('source_url', ''),
                'source_license': site_data['source_license'],
                'attribution': site_data['attribution'],
                'sensitivity_level': site_data['sensitivity_level'],
                'notes': site_data.get('notes', ''),
            }
        )
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  {action} site: {site.name}')

        # Create TerrainMap
        map_data = data['terrain_map']
        terrain_map, created = TerrainMap.objects.update_or_create(
            digital_twin_site=site,
            slug=map_data['slug'],
            defaults={
                'name': map_data['name'],
                'coordinate_system': map_data['coordinate_system'],
                'origin_label': map_data['origin_label'],
                'units': map_data['units'],
                'source_format': map_data['source_format'],
            }
        )
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  {action} terrain map: {terrain_map.name}')

        # Create TerrainSectors
        sectors_by_id = {}
        for sector_data in data.get('sectors', []):
            sector, created = TerrainSector.objects.update_or_create(
                terrain_map=terrain_map,
                sector_id=sector_data['sector_id'],
                defaults={
                    'label': sector_data['label'],
                    'sector_type': sector_data['sector_type'],
                    'x_m': sector_data['x_m'],
                    'y_m': sector_data['y_m'],
                    'z_m': sector_data['z_m'],
                    'width_m': sector_data.get('width_m'),
                    'height_m': sector_data.get('height_m'),
                    'depth_m': sector_data.get('depth_m'),
                    'elevation_m': sector_data.get('elevation_m'),
                    'confidence': sector_data.get('confidence', 1.0),
                    'source_ref': sector_data.get('source_ref', ''),
                    'metadata': sector_data.get('metadata', {}),
                }
            )
            sectors_by_id[sector_data['sector_id']] = sector
            
        self.stdout.write(f'  Created/updated {len(sectors_by_id)} sectors')

        # Create TerrainPaths
        path_count = 0
        for path_data in data.get('paths', []):
            from_sector = sectors_by_id.get(path_data['from_sector'])
            to_sector = sectors_by_id.get(path_data['to_sector'])
            
            if not from_sector or not to_sector:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping path: sector not found '
                        f'({path_data["from_sector"]} -> {path_data["to_sector"]})'
                    )
                )
                continue

            TerrainPath.objects.update_or_create(
                terrain_map=terrain_map,
                from_sector=from_sector,
                to_sector=to_sector,
                defaults={
                    'distance_m': path_data['distance_m'],
                    'bearing_deg': path_data.get('bearing_deg'),
                    'vertical_change_m': path_data['vertical_change_m'],
                    'path_type': path_data['path_type'],
                    'traversal_risk': path_data['traversal_risk'],
                    'confidence': path_data.get('confidence', 1.0),
                    'capabilities_required': path_data.get('capabilities_required', []),
                    'metadata': path_data.get('metadata', {}),
                }
            )
            path_count += 1
            
        self.stdout.write(f'  Created/updated {path_count} paths')

        # Create Waypoints
        waypoint_count = 0
        for waypoint_data in data.get('waypoints', []):
            Waypoint.objects.update_or_create(
                terrain_map=terrain_map,
                waypoint_id=waypoint_data['waypoint_id'],
                defaults={
                    'label': waypoint_data['label'],
                    'x_m': waypoint_data['x_m'],
                    'y_m': waypoint_data['y_m'],
                    'z_m': waypoint_data['z_m'],
                    'sequence': waypoint_data.get('sequence'),
                    'route_group': waypoint_data.get('route_group', ''),
                    'metadata': waypoint_data.get('metadata', {}),
                }
            )
            waypoint_count += 1
            
        self.stdout.write(f'  Created/updated {waypoint_count} waypoints')
