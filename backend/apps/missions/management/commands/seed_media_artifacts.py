"""
Seed scenario media artifact metadata.

Usage:
    python manage.py seed_media_artifacts
    python manage.py seed_media_artifacts --clear
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.missions.models_media import ScenarioMediaArtifact


class Command(BaseCommand):
    help = 'Seed scenario media artifact metadata'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing media artifacts before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing media artifacts...')
            ScenarioMediaArtifact.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        self.stdout.write('Seeding media artifacts...')
        
        with transaction.atomic():
            self.seed_collapsed_building()
            self.seed_archaeology()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully seeded {ScenarioMediaArtifact.objects.count()} media artifacts!'))

    def seed_collapsed_building(self):
        """Seed Collapsed Building media artifacts"""
        self.stdout.write('Seeding Collapsed Building media...')
        
        # RGB Camera Views
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-rgb-entry-clear',
            use_case_slug='collapsed-building-search',
            sector_id='entry',
            agent_role='mapper',
            agent_id='drone-a',
            media_type='rgb_image',
            sensor_type='rgb_camera',
            file_path='/media/collapsed-building/rgb-entry-clear.png',
            title='Entry Point - Clear View',
            description='First-person POV from rescue drone entering collapsed concrete building. Clear view of rubble, exposed rebar, and accessible entry point.',
            mission_time_seconds=30.0,
            linked_event_type='sector-explored',
            confidence=0.92,
            signal_quality=0.95,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['exposed_rebar', 'unstable_debris', 'sharp_obstacles'],
            annotation_tags=['entry point', 'structural damage', 'accessible'],
            metadata={
                'camera_mode': 'rgb',
                'light_active': True,
                'image_quality': 'high',
                'gimbal_stabilization': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-rgb-dust-corridor',
            use_case_slug='collapsed-building-search',
            sector_id='ground-corridor-east',
            agent_role='mapper',
            agent_id='drone-a',
            media_type='rgb_image',
            sensor_type='rgb_camera',
            file_path='/media/collapsed-building/rgb-dust-corridor.png',
            title='Ground Corridor - Heavy Dust',
            description='Dust-obscured corridor with heavy airborne particulate, concrete rubble, cracked walls, damaged ceiling.',
            mission_time_seconds=90.0,
            linked_event_type='sector-explored',
            confidence=0.65,
            signal_quality=0.70,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='dust',
            hazard_tags=['dust_obscuration', 'low_visibility', 'unstable_structure'],
            annotation_tags=['dust interference', 'corridor mapped', 'visibility degraded'],
            metadata={
                'camera_mode': 'rgb',
                'light_active': True,
                'dust_severity': 'high',
                'lidar_confidence_drop': 0.35
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-rgb-void-space-dark',
            use_case_slug='collapsed-building-search',
            sector_id='void-space-1',
            agent_role='mapper',
            agent_id='drone-a',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/collapsed-building/rgb-void-space-dark.png',
            title='Void Space Interior - Deep Shadow',
            description='Dark void space with broken concrete slabs, exposed metal reinforcement, narrow accessible gap.',
            mission_time_seconds=180.0,
            linked_event_type='sector-explored',
            confidence=0.72,
            signal_quality=0.68,
            human_review_required=True,
            lighting_state='low_light',
            visibility_condition='darkness',
            hazard_tags=['complete_darkness', 'confined_space', 'structural_instability'],
            annotation_tags=['void space', 'low light', 'structural damage'],
            metadata={
                'camera_mode': 'low_light',
                'light_active': False,
                'depth_estimate_m': 3.5,
                'void_classification': 'accessible'
            }
        )
        
        # Thermal Camera Views
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-thermal-void-heat-signature',
            use_case_slug='collapsed-building-search',
            sector_id='void-space-1',
            agent_role='detector',
            agent_id='drone-b',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/collapsed-building/thermal-void-heat-signature.png',
            title='Thermal Anomaly - Void Space 1',
            description='Thermal frame showing warm survivor-like heat anomaly partially obscured by debris. Cool surrounding concrete visible in false-color palette.',
            mission_time_seconds=360.0,
            linked_event_type='thermal_detection',
            confidence=0.78,
            signal_quality=0.64,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='obscured',
            hazard_tags=['heat_source_detected', 'requires_investigation'],
            annotation_tags=['thermal anomaly', 'possible human cue', 'review required', 'priority high'],
            metadata={
                'temperature_delta': 'high',
                'temperature_estimate_c': 32.5,
                'ambient_temperature_c': 18.0,
                'review_reason': 'possible human heat signature',
                'thermal_palette': 'ironbow'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-thermal-empty-corridor',
            use_case_slug='collapsed-building-search',
            sector_id='ground-corridor-east',
            agent_role='detector',
            agent_id='drone-b',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/collapsed-building/thermal-empty-corridor.png',
            title='Thermal Scan - Empty Corridor',
            description='Thermal scan of empty basement corridor, cool blue and purple false-color palette, no obvious heat source detected.',
            mission_time_seconds=120.0,
            linked_event_type='sector-explored',
            confidence=0.85,
            signal_quality=0.82,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['thermal scan', 'no anomalies', 'cold zone'],
            metadata={
                'temperature_delta': 'uniform',
                'ambient_temperature_c': 17.5,
                'thermal_palette': 'arctic'
            }
        )
        
        # LiDAR/Point Cloud Views
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-lidar-void-point-cloud',
            use_case_slug='collapsed-building-search',
            sector_id='void-space-1',
            agent_role='mapper',
            agent_id='drone-a',
            media_type='lidar_preview',
            sensor_type='lidar',
            file_path='/media/collapsed-building/lidar-void-point-cloud.png',
            title='LiDAR Point Cloud - Void Space',
            description='LiDAR point cloud visualization of collapsed building interior. Walls, corridors and debris reconstructed in blue, green and purple points, confidence-colored.',
            mission_time_seconds=180.0,
            linked_event_type='sector-explored',
            confidence=0.88,
            signal_quality=0.90,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['lidar', 'point cloud', '3d mapping', 'high confidence'],
            metadata={
                'point_count': 45820,
                'confidence_coloring': True,
                'point_density': 'high',
                'slam_confidence': 0.88
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='collapsed-lidar-sector-coverage',
            use_case_slug='collapsed-building-search',
            sector_id='ground-entry',
            agent_role='mapper',
            agent_id='drone-a',
            media_type='point_cloud_preview',
            sensor_type='lidar',
            file_path='/media/collapsed-building/lidar-sector-coverage.png',
            title='3D Reconstruction Preview',
            description='3D mesh reconstruction preview of partially mapped collapsed structure interior. Void spaces and blocked debris zones highlighted.',
            mission_time_seconds=300.0,
            linked_event_type='map_generated',
            confidence=0.82,
            signal_quality=0.85,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['3d reconstruction', 'mesh preview', 'sector coverage', 'mapping progress'],
            metadata={
                'mapped_sectors': 4,
                'total_sectors': 7,
                'coverage_percent': 57.0,
                'mesh_quality': 'medium'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Collapsed Building media (7 artifacts)'))

    def seed_archaeology(self):
        """Seed Archaeological Exploration media artifacts"""
        self.stdout.write('Seeding Archaeological Exploration media...')
        
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-low-light-access-tunnel',
            use_case_slug='archaeological-exploration',
            sector_id='access-tunnel',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/archaeology/low-light-access-tunnel.png',
            title='Access Tunnel - Non-Contact Survey',
            description='Low-light camera view of underground archaeological access tunnel. Stone walls, dust, fragile surfaces. Preservation survey mode.',
            mission_time_seconds=45.0,
            linked_event_type='sector-explored',
            confidence=0.90,
            signal_quality=0.88,
            human_review_required=True,
            lighting_state='low_light',
            visibility_condition='dust',
            hazard_tags=['fragile_surfaces', 'heritage_site', 'non_contact_required'],
            annotation_tags=['archaeological survey', 'access tunnel', 'preservation mode', 'heritage documentation'],
            metadata={
                'survey_mode': 'non_contact',
                'heritage_classification': 'ancient_structure',
                'preservation_priority': 'high',
                'cultural_sensitivity': 'maximum'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-ir-wall-inscription',
            use_case_slug='archaeological-exploration',
            sector_id='ceremonial-chamber',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='infrared_image',
            sensor_type='infrared_camera',
            file_path='/media/archaeology/ir-wall-inscription.png',
            title='IR-Enhanced Wall Inscriptions',
            description='Infrared-assisted drone view of ancient wall inscriptions inside sealed underground chamber. Fragile surfaces, non-contact documentation mode.',
            mission_time_seconds=180.0,
            linked_event_type='heritage_discovery',
            confidence=0.85,
            signal_quality=0.80,
            human_review_required=True,
            lighting_state='ir_illuminator',
            visibility_condition='clear',
            hazard_tags=['fragile_inscriptions', 'heritage_site', 'non_contact_required'],
            annotation_tags=['inscription discovery', 'IR documentation', 'heritage preservation', 'expert review required'],
            metadata={
                'inscription_type': 'wall_carving',
                'estimated_age': 'ancient',
                'preservation_state': 'fragile',
                'documentation_method': 'infrared_enhanced',
                'cultural_significance': 'high'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-lidar-chamber-point-cloud',
            use_case_slug='archaeological-exploration',
            sector_id='ceremonial-chamber',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='lidar_preview',
            sensor_type='lidar',
            file_path='/media/archaeology/lidar-chamber-point-cloud.png',
            title='Ceremonial Chamber - LiDAR Reconstruction',
            description='LiDAR point cloud reconstruction of underground ceremonial chamber. Stone columns, alcoves and low corridors in blue-green point cloud. Digital heritage survey.',
            mission_time_seconds=240.0,
            linked_event_type='map_generated',
            confidence=0.92,
            signal_quality=0.90,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=['heritage_site', 'fragile_structure'],
            annotation_tags=['lidar reconstruction', 'ceremonial chamber', 'digital heritage', '3d documentation'],
            metadata={
                'point_count': 128450,
                'chamber_volume_m3': 245.0,
                'column_count': 6,
                'alcove_count': 3,
                'heritage_classification': 'ceremonial_space',
                'documentation_quality': 'research_grade'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-sealed-chamber-climate-archive',
            use_case_slug='archaeological-exploration',
            sector_id='sealed-chamber',
            agent_role='detector',
            agent_id='heritage-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/archaeology/sealed-chamber-climate-archive.png',
            title='Sealed Chamber - Climate Archive Candidate',
            description='Drone survey image of sealed side chamber with sediment layers and fragile organic material. Archaeological climate archive candidate. Conservation priority.',
            mission_time_seconds=360.0,
            linked_event_type='heritage_discovery',
            confidence=0.88,
            signal_quality=0.85,
            human_review_required=True,
            lighting_state='low_light',
            visibility_condition='clear',
            hazard_tags=['fragile_organic_material', 'climate_archive', 'non_contact_required', 'conservation_priority'],
            annotation_tags=['climate archive', 'sealed chamber', 'organic preservation', 'expert analysis required', 'conservation critical'],
            metadata={
                'chamber_type': 'sealed_side_chamber',
                'sediment_layers_visible': True,
                'organic_material_detected': True,
                'climate_significance': 'potential drought/flood evidence',
                'preservation_mode': 'immediate',
                'conservation_action': 'non_destructive_documentation_only',
                'specialist_required': 'archaeologist + paleoclimatologist'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Archaeological Exploration media (4 artifacts)'))
