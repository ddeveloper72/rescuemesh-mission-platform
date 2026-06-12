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
            self.seed_cave_rescue()
            self.seed_industrial_inspection()
            self.seed_flooded_structure()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {ScenarioMediaArtifact.objects.count()} media artifacts'))

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
        
        self.stdout.write(self.style.SUCCESS('  Collapsed Building media (7 artifacts)'))

    def seed_archaeology(self):
        """Seed Archaeological Exploration media artifacts"""
        self.stdout.write('Seeding Archaeological Exploration media...')
        
        # RGB Inspection Views
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-rgb-access-tunnel',
            use_case_slug='archaeological-exploration',
            sector_id='access-tunnel',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/archaeology/rgb-access-tunnel.png',
            title='Access Tunnel - Non-Contact Survey',
            description='Low-light camera view of underground archaeological access tunnel. Stone walls, ancient construction, preservation survey mode.',
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
            slug='archaeology-rgb-chamber-entrance',
            use_case_slug='archaeological-exploration',
            sector_id='chamber-entrance',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/archaeology/rgb-chamber-entrance.png',
            title='Chamber Entrance Discovery',
            description='RGB documentation of ceremonial chamber entrance with architectural features and inscriptions visible.',
            mission_time_seconds=120.0,
            linked_event_type='heritage_discovery',
            confidence=0.88,
            signal_quality=0.85,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['fragile_features', 'heritage_site'],
            annotation_tags=['chamber entrance', 'architectural features', 'inscriptions visible', 'cultural significance'],
            metadata={
                'entrance_type': 'ceremonial',
                'architectural_style': 'ancient',
                'inscription_present': True,
                'cultural_significance': 'high'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-rgb-artifact-alcove',
            use_case_slug='archaeological-exploration',
            sector_id='artifact-alcove',
            agent_role='detector',
            agent_id='heritage-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/archaeology/rgb-artifact-alcove.png',
            title='Artifact Alcove - Non-Contact Documentation',
            description='Non-destructive documentation of artifact alcove showing ceramic fragments and organic material. Conservation priority.',
            mission_time_seconds=300.0,
            linked_event_type='heritage_discovery',
            confidence=0.85,
            signal_quality=0.82,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['fragile_artifacts', 'organic_material', 'heritage_site', 'non_contact_required'],
            annotation_tags=['artifact alcove', 'ceramic fragments', 'organic material', 'conservation critical', 'expert analysis required'],
            metadata={
                'artifact_types': ['ceramic_fragments', 'organic_material'],
                'preservation_state': 'fragile',
                'conservation_priority': 'immediate',
                'contact_forbidden': True,
                'specialist_required': 'archaeologist + conservator'
            }
        )
        
        # Infrared Inspection Views
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-ir-wall-inscription',
            use_case_slug='archaeological-exploration',
            sector_id='ceremonial-chamber',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='infrared_image',
            sensor_type='infrared_camera',
            file_path='/media/archaeology/ir-wall-inscription-new.png',
            title='IR-Enhanced Wall Inscriptions',
            description='Infrared-assisted documentation revealing previously invisible wall inscriptions and surface details. Non-contact heritage preservation.',
            mission_time_seconds=180.0,
            linked_event_type='heritage_discovery',
            confidence=0.85,
            signal_quality=0.80,
            human_review_required=True,
            lighting_state='ir_illuminator',
            visibility_condition='clear',
            hazard_tags=['fragile_inscriptions', 'heritage_site', 'non_contact_required'],
            annotation_tags=['inscription discovery', 'IR documentation', 'heritage preservation', 'expert review required', 'cultural text'],
            metadata={
                'inscription_type': 'wall_carving',
                'estimated_age': 'ancient',
                'preservation_state': 'fragile',
                'documentation_method': 'infrared_enhanced',
                'cultural_significance': 'high',
                'translation_required': True
            }
        )
        
        # LiDAR Spatial Mapping Visuals
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-lidar-chamber-reconstruction',
            use_case_slug='archaeological-exploration',
            sector_id='ceremonial-chamber',
            agent_role='mapper',
            agent_id='heritage-drone-1',
            media_type='lidar_preview',
            sensor_type='lidar',
            file_path='/media/archaeology/lidar-chamber-reconstruction.png',
            title='Ceremonial Chamber - 3D Reconstruction',
            description='High-resolution LiDAR point cloud reconstruction of ceremonial chamber. Stone columns, alcoves, and architectural features digitally preserved.',
            mission_time_seconds=240.0,
            linked_event_type='map_generated',
            confidence=0.92,
            signal_quality=0.90,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=['heritage_site', 'fragile_structure'],
            annotation_tags=['lidar reconstruction', 'ceremonial chamber', 'digital heritage', '3d documentation', 'architectural analysis'],
            metadata={
                'point_count': 128450,
                'chamber_volume_m3': 245.0,
                'column_count': 6,
                'alcove_count': 3,
                'heritage_classification': 'ceremonial_space',
                'documentation_quality': 'research_grade',
                'digital_preservation': True
            }
        )
        
        # Environmental Sensor Dashboard
        ScenarioMediaArtifact.objects.create(
            slug='archaeology-env-sensor-dashboard',
            use_case_slug='archaeological-exploration',
            sector_id='sealed-chamber',
            agent_role='detector',
            agent_id='sensor-package-1',
            media_type='spectrogram',
            sensor_type='environmental_sensor',
            file_path='/media/archaeology/env-sensor-dashboard.png',
            title='Environmental Sensor Dashboard',
            description='Comprehensive environmental monitoring dashboard showing temperature, humidity, CO2, O2 levels in sealed chamber. Climate archive preservation data.',
            mission_time_seconds=360.0,
            linked_event_type='environmental_monitoring',
            confidence=0.95,
            signal_quality=0.92,
            human_review_required=True,
            lighting_state='none',
            visibility_condition='not_applicable',
            hazard_tags=['low_oxygen', 'high_co2', 'climate_sensitive'],
            annotation_tags=['environmental monitoring', 'climate data', 'sealed chamber', 'preservation critical', 'sensor dashboard'],
            metadata={
                'temperature_c': 14.5,
                'humidity_percent': 82.0,
                'co2_ppm': 1850,
                'o2_percent': 18.2,
                'chamber_type': 'sealed',
                'climate_stability': 'high',
                'preservation_conditions': 'excellent',
                'climate_archive_candidate': True,
                'paleoclimate_significance': 'high'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  Archaeological Exploration media (6 artifacts)'))

    def seed_cave_rescue(self):
        """Seed Cave Rescue media artifacts"""
        self.stdout.write('Seeding Cave Rescue media...')
        
        # RGB Low-light Camera Views
        ScenarioMediaArtifact.objects.create(
            slug='cave-rgb-narrow-passage',
            use_case_slug='cave-rescue',
            sector_id='narrow-passage-1',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/cave-rescue/rgb-narrow-passage.png',
            title='Narrow Passage - Low Light',
            description='Low-light view of narrow cave passage with tight rock walls, mineral deposits, and limited maneuvering space.',
            mission_time_seconds=60.0,
            linked_event_type='sector-explored',
            confidence=0.75,
            signal_quality=0.70,
            human_review_required=False,
            lighting_state='low_light',
            visibility_condition='darkness',
            hazard_tags=['narrow_passage', 'confined_space', 'navigation_difficulty'],
            annotation_tags=['cave passage', 'low light', 'tight space', 'navigation challenge'],
            metadata={
                'passage_width_m': 0.8,
                'camera_mode': 'low_light',
                'light_active': True,
                'navigation_difficulty': 'high'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-rgb-main-tunnel',
            use_case_slug='cave-rescue',
            sector_id='main-tunnel',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/cave-rescue/rgb-main-tunnel.png',
            title='Main Tunnel - Stable Route',
            description='Low-light camera view of main cave tunnel showing stable rock formations and accessible passage.',
            mission_time_seconds=120.0,
            linked_event_type='sector-explored',
            confidence=0.88,
            signal_quality=0.85,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['main tunnel', 'stable formation', 'accessible route', 'primary passage'],
            metadata={
                'passage_width_m': 2.5,
                'ceiling_height_m': 3.0,
                'route_stability': 'high',
                'recommended_route': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-rgb-junction',
            use_case_slug='cave-rescue',
            sector_id='junction-point',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/cave-rescue/rgb-junction.png',
            title='Junction Point - Path Decision',
            description='Three-way junction in cave system requiring path selection. Low-light visibility of multiple passages.',
            mission_time_seconds=180.0,
            linked_event_type='sector-explored',
            confidence=0.82,
            signal_quality=0.78,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['path_decision_required', 'multiple_routes'],
            annotation_tags=['junction', 'navigation decision', 'multiple passages', 'route planning'],
            metadata={
                'passage_count': 3,
                'decision_point': True,
                'slam_confidence': 0.82,
                'recommended_path': 'left_passage'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-rgb-vertical-drop',
            use_case_slug='cave-rescue',
            sector_id='vertical-drop',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='low_light_image',
            sensor_type='low_light_camera',
            file_path='/media/cave-rescue/rgb-vertical-drop.png',
            title='Vertical Drop - Hazard Alert',
            description='Significant vertical drop in cave passage. Hazardous terrain requiring alternative routing or specialized equipment.',
            mission_time_seconds=240.0,
            linked_event_type='hazard_detected',
            confidence=0.90,
            signal_quality=0.85,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['vertical_drop', 'fall_hazard', 'route_blocked', 'specialized_equipment_required'],
            annotation_tags=['vertical drop', 'hazard alert', 'route blocked', 'safety critical'],
            metadata={
                'drop_height_m': 8.5,
                'safety_risk': 'critical',
                'passage_type': 'vertical_shaft',
                'alternative_route_required': True
            }
        )
        
        # Infrared/Night Vision Views
        ScenarioMediaArtifact.objects.create(
            slug='cave-ir-passage-scan',
            use_case_slug='cave-rescue',
            sector_id='side-passage-2',
            agent_role='detector',
            agent_id='cave-drone-2',
            media_type='infrared_image',
            sensor_type='infrared_camera',
            file_path='/media/cave-rescue/ir-passage-scan.png',
            title='IR Passage Scan',
            description='Infrared scan of cave passage revealing temperature variations and moisture patterns.',
            mission_time_seconds=150.0,
            linked_event_type='sector-explored',
            confidence=0.80,
            signal_quality=0.75,
            human_review_required=False,
            lighting_state='ir_illuminator',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['infrared scan', 'temperature mapping', 'moisture detection'],
            metadata={
                'temperature_range_c': [10.5, 14.2],
                'moisture_detected': True,
                'thermal_mode': 'passive_ir'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-ir-thermal-anomaly',
            use_case_slug='cave-rescue',
            sector_id='deep-chamber',
            agent_role='detector',
            agent_id='cave-drone-2',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/cave-rescue/ir-thermal-anomaly.png',
            title='Thermal Anomaly Detected',
            description='Infrared detection of warm thermal signature in deep cave chamber. Possible human presence.',
            mission_time_seconds=420.0,
            linked_event_type='thermal_detection',
            confidence=0.72,
            signal_quality=0.68,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='obscured',
            hazard_tags=['requires_investigation'],
            annotation_tags=['thermal anomaly', 'possible human', 'priority investigation', 'rescue target'],
            metadata={
                'temperature_estimate_c': 29.5,
                'ambient_temperature_c': 12.0,
                'anomaly_type': 'warm_signature',
                'investigation_priority': 'high'
            }
        )
        
        # LiDAR Mapping Visuals
        ScenarioMediaArtifact.objects.create(
            slug='cave-lidar-cave-system',
            use_case_slug='cave-rescue',
            sector_id='mapped-area',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='lidar_preview',
            sensor_type='lidar',
            file_path='/media/cave-rescue/lidar-cave-system.png',
            title='Cave System LiDAR Map',
            description='LiDAR point cloud visualization of cave tunnel system showing passage geometry and branching routes.',
            mission_time_seconds=300.0,
            linked_event_type='map_generated',
            confidence=0.85,
            signal_quality=0.88,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['lidar map', 'cave system', 'passage network', '3d reconstruction'],
            metadata={
                'point_count': 92340,
                'mapped_length_m': 145.0,
                'passage_count': 7,
                'slam_confidence': 0.85
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-lidar-passage-geometry',
            use_case_slug='cave-rescue',
            sector_id='narrow-passage-1',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='lidar_preview',
            sensor_type='lidar',
            file_path='/media/cave-rescue/lidar-passage-geometry.png',
            title='Passage Geometry Analysis',
            description='Detailed LiDAR geometry analysis of narrow cave passage showing dimensions and clearances.',
            mission_time_seconds=90.0,
            linked_event_type='sector-explored',
            confidence=0.92,
            signal_quality=0.90,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['geometry analysis', 'passage dimensions', 'clearance data', 'navigation planning'],
            metadata={
                'min_width_m': 0.75,
                'max_width_m': 1.2,
                'height_m': 1.8,
                'clearance_suitable': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-lidar-junction-map',
            use_case_slug='cave-rescue',
            sector_id='junction-point',
            agent_role='mapper',
            agent_id='cave-drone-1',
            media_type='point_cloud_preview',
            sensor_type='lidar',
            file_path='/media/cave-rescue/lidar-junction-map.png',
            title='Junction Point 3D Map',
            description='3D LiDAR reconstruction of cave junction showing three passage options with geometry data.',
            mission_time_seconds=195.0,
            linked_event_type='map_generated',
            confidence=0.88,
            signal_quality=0.85,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['junction map', '3d reconstruction', 'route options', 'decision support'],
            metadata={
                'junction_type': 'three_way',
                'passage_angles_deg': [15, 90, 245],
                'recommended_route': 'passage_1_left',
                'decision_confidence': 0.78
            }
        )
        
        # Acoustic/Seismic/Talkback Visuals
        ScenarioMediaArtifact.objects.create(
            slug='cave-acoustic-echo-analysis',
            use_case_slug='cave-rescue',
            sector_id='deep-chamber',
            agent_role='detector',
            agent_id='relay-node-2',
            media_type='spectrogram',
            sensor_type='audio_sensor',
            file_path='/media/cave-rescue/acoustic-echo-analysis.png',
            title='Acoustic Echo Analysis',
            description='Acoustic analysis showing echo patterns and potential audio responses from deep cave chambers.',
            mission_time_seconds=360.0,
            linked_event_type='audio_detection',
            confidence=0.65,
            signal_quality=0.60,
            human_review_required=True,
            lighting_state='none',
            visibility_condition='not_applicable',
            hazard_tags=[],
            annotation_tags=['acoustic analysis', 'echo mapping', 'audio response', 'detection uncertain'],
            metadata={
                'echo_delay_ms': 450,
                'frequency_range_hz': [200, 4000],
                'audio_type': 'echo_analysis',
                'response_confidence': 0.65
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-acoustic-talkback-active',
            use_case_slug='cave-rescue',
            sector_id='deep-chamber',
            agent_role='detector',
            agent_id='relay-node-2',
            media_type='spectrogram',
            sensor_type='audio_sensor',
            file_path='/media/cave-rescue/acoustic-talkback-active.png',
            title='Talkback System Active',
            description='Audio talkback system operational. Voice message transmitted to deep cave sections, listening for response.',
            mission_time_seconds=390.0,
            linked_event_type='talkback_active',
            confidence=0.75,
            signal_quality=0.70,
            human_review_required=True,
            lighting_state='none',
            visibility_condition='not_applicable',
            hazard_tags=[],
            annotation_tags=['talkback', 'voice transmission', 'response monitoring', 'rescue communication'],
            metadata={
                'transmission_power': 'high',
                'listening_mode': 'active',
                'response_window_s': 30,
                'audio_quality': 'clear'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-seismic-vibration-map',
            use_case_slug='cave-rescue',
            sector_id='unstable-area',
            agent_role='detector',
            agent_id='sensor-package-1',
            media_type='spectrogram',
            sensor_type='seismic_sensor',
            file_path='/media/cave-rescue/seismic-vibration-map.png',
            title='Seismic Vibration Mapping',
            description='Seismic sensor data showing vibration patterns and structural stability indicators in cave system.',
            mission_time_seconds=270.0,
            linked_event_type='hazard_detected',
            confidence=0.80,
            signal_quality=0.78,
            human_review_required=True,
            lighting_state='none',
            visibility_condition='not_applicable',
            hazard_tags=['unstable_area', 'vibration_detected', 'structural_concern'],
            annotation_tags=['seismic analysis', 'vibration mapping', 'stability assessment', 'safety monitoring'],
            metadata={
                'vibration_frequency_hz': 12.5,
                'amplitude': 'low',
                'stability_rating': 'moderate',
                'caution_advised': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='cave-acoustic-response-detected',
            use_case_slug='cave-rescue',
            sector_id='deep-chamber',
            agent_role='detector',
            agent_id='relay-node-2',
            media_type='spectrogram',
            sensor_type='audio_sensor',
            file_path='/media/cave-rescue/acoustic-response-detected.png',
            title='Acoustic Response Detected',
            description='Possible human audio response detected following talkback transmission. Voice-like pattern in deep chamber.',
            mission_time_seconds=425.0,
            linked_event_type='audio_detection',
            confidence=0.68,
            signal_quality=0.62,
            human_review_required=True,
            lighting_state='none',
            visibility_condition='not_applicable',
            hazard_tags=['requires_investigation'],
            annotation_tags=['audio response', 'possible human', 'voice-like pattern', 'priority investigation', 'rescue target'],
            metadata={
                'response_type': 'voice_like',
                'frequency_pattern': 'human_compatible',
                'signal_to_noise_ratio': 0.62,
                'investigation_priority': 'high',
                'expert_analysis_required': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  Cave Rescue media (13 artifacts)'))

    def seed_industrial_inspection(self):
        """Seed Industrial Inspection media artifacts"""
        self.stdout.write('Seeding Industrial Inspection media...')
        
        # RGB Inspection Views
        ScenarioMediaArtifact.objects.create(
            slug='industrial-rgb-machinery-corridor',
            use_case_slug='industrial-inspection',
            sector_id='machinery-corridor',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/industrial-inspection/rgb-machinery-corridor.png',
            title='Machinery Corridor Inspection',
            description='RGB inspection view of industrial machinery corridor showing equipment status and access routes.',
            mission_time_seconds=45.0,
            linked_event_type='sector-explored',
            confidence=0.90,
            signal_quality=0.92,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['machinery', 'moving_parts_possible'],
            annotation_tags=['machinery corridor', 'equipment visible', 'access route', 'inspection complete'],
            metadata={
                'corridor_width_m': 3.5,
                'equipment_count': 12,
                'accessibility': 'good',
                'inspection_type': 'visual'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='industrial-rgb-control-room',
            use_case_slug='industrial-inspection',
            sector_id='control-room',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/industrial-inspection/rgb-control-room.png',
            title='Control Room Assessment',
            description='Control room visual assessment showing panel status, equipment condition, and environmental state.',
            mission_time_seconds=120.0,
            linked_event_type='sector-explored',
            confidence=0.88,
            signal_quality=0.90,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['control room', 'equipment assessment', 'panel inspection', 'operational status'],
            metadata={
                'panel_count': 8,
                'equipment_status': 'powered_down',
                'environmental_condition': 'stable',
                'review_focus': 'equipment_condition'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='industrial-rgb-structural-damage',
            use_case_slug='industrial-inspection',
            sector_id='south-wall',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='rgb_image',
            sensor_type='inspection_camera',
            file_path='/media/industrial-inspection/rgb-structural-damage.png',
            title='Structural Damage Detected',
            description='Visual documentation of structural damage to facility wall. Cracks, deformation, and potential integrity compromise.',
            mission_time_seconds=240.0,
            linked_event_type='hazard_detected',
            confidence=0.85,
            signal_quality=0.88,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['structural_damage', 'integrity_compromise', 'safety_concern'],
            annotation_tags=['structural damage', 'wall cracks', 'deformation', 'engineer review required'],
            metadata={
                'damage_type': 'structural_cracks',
                'severity': 'moderate',
                'crack_length_m': 2.8,
                'structural_engineer_required': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='industrial-rgb-confined-space',
            use_case_slug='industrial-inspection',
            sector_id='confined-space-1',
            agent_role='inspector',
            agent_id='inspection-drone-2',
            media_type='low_light_image',
            sensor_type='inspection_camera',
            file_path='/media/industrial-inspection/rgb-confined-space.png',
            title='Confined Space Entry',
            description='Low-light inspection of confined industrial space. Limited ventilation, narrow access, equipment inspection.',
            mission_time_seconds=180.0,
            linked_event_type='sector-explored',
            confidence=0.75,
            signal_quality=0.70,
            human_review_required=True,
            lighting_state='low_light',
            visibility_condition='darkness',
            hazard_tags=['confined_space', 'limited_ventilation', 'narrow_access'],
            annotation_tags=['confined space', 'equipment visible', 'ventilation concern', 'safety critical'],
            metadata={
                'space_volume_m3': 8.5,
                'access_width_m': 0.6,
                'ventilation': 'poor',
                'gas_sensor_required': True
            }
        )
        
        # Thermal Views
        ScenarioMediaArtifact.objects.create(
            slug='industrial-thermal-hotspot-equipment',
            use_case_slug='industrial-inspection',
            sector_id='machinery-corridor',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/industrial-inspection/thermal-hotspot-equipment.png',
            title='Equipment Thermal Hotspot',
            description='Thermal imaging revealing elevated temperature in industrial equipment. Possible electrical fault or mechanical friction.',
            mission_time_seconds=90.0,
            linked_event_type='thermal_detection',
            confidence=0.82,
            signal_quality=0.80,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=['thermal_hotspot', 'equipment_fault', 'fire_risk'],
            annotation_tags=['thermal anomaly', 'equipment fault', 'elevated temperature', 'maintenance required'],
            metadata={
                'hotspot_temperature_c': 78.5,
                'ambient_temperature_c': 24.0,
                'equipment_type': 'motor_housing',
                'fault_type': 'thermal_elevation',
                'maintenance_priority': 'high'
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='industrial-thermal-pipe-leak',
            use_case_slug='industrial-inspection',
            sector_id='pipe-corridor',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/industrial-inspection/thermal-pipe-leak.png',
            title='Thermal Signature - Pipe Leak',
            description='Thermal imaging detecting temperature anomaly indicating possible pipe leak or steam release.',
            mission_time_seconds=210.0,
            linked_event_type='hazard_detected',
            confidence=0.88,
            signal_quality=0.85,
            human_review_required=True,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=['pipe_leak', 'steam_release', 'pressure_loss'],
            annotation_tags=['pipe leak', 'thermal signature', 'steam visible', 'repair required'],
            metadata={
                'leak_temperature_c': 110.5,
                'ambient_temperature_c': 24.0,
                'leak_type': 'steam_release',
                'pipe_section': 'south_corridor_main',
                'isolation_required': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='industrial-thermal-heat-distribution',
            use_case_slug='industrial-inspection',
            sector_id='main-facility',
            agent_role='inspector',
            agent_id='inspection-drone-1',
            media_type='thermal_image',
            sensor_type='thermal_camera',
            file_path='/media/industrial-inspection/thermal-heat-distribution.png',
            title='Facility Heat Distribution Map',
            description='Thermal overview of industrial facility showing heat distribution patterns across equipment and zones.',
            mission_time_seconds=360.0,
            linked_event_type='map_generated',
            confidence=0.90,
            signal_quality=0.88,
            human_review_required=False,
            lighting_state='thermal_mode',
            visibility_condition='clear',
            hazard_tags=[],
            annotation_tags=['heat distribution', 'facility overview', 'thermal mapping', 'baseline data'],
            metadata={
                'temperature_range_c': [18.0, 85.0],
                'hot_zones': 3,
                'cold_zones': 2,
                'thermal_map_type': 'facility_wide',
                'baseline_established': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  Industrial Inspection media (7 artifacts)'))

    def seed_flooded_structure(self):
        """Seed Flooded Structure media artifacts"""
        self.stdout.write('Seeding Flooded Structure media...')
        
        # RGB Surface Views
        ScenarioMediaArtifact.objects.create(
            slug='flooded-rgb-surface-entry',
            use_case_slug='flooded-structure',
            sector_id='surface-entry',
            agent_role='surface-scout',
            agent_id='amphibious-drone-1',
            media_type='rgb_image',
            sensor_type='rgb_camera',
            file_path='/media/flooded-structure/rgb-surface-entry.png',
            title='Surface Entry Point',
            description='RGB view of flooded structure surface entry point showing water level, debris, and access conditions.',
            mission_time_seconds=30.0,
            linked_event_type='sector-explored',
            confidence=0.92,
            signal_quality=0.95,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['water_hazard', 'submersion_required'],
            annotation_tags=['surface entry', 'water level', 'access point', 'deployment zone'],
            metadata={
                'water_depth_m': 1.8,
                'water_clarity': 'moderate',
                'surface_condition': 'calm',
                'entry_feasible': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='flooded-rgb-surface-debris',
            use_case_slug='flooded-structure',
            sector_id='surface-zone',
            agent_role='surface-scout',
            agent_id='amphibious-drone-1',
            media_type='rgb_image',
            sensor_type='rgb_camera',
            file_path='/media/flooded-structure/rgb-surface-debris.png',
            title='Surface Debris Field',
            description='Surface debris and floating objects visible on water. Navigation hazards and obstruction mapping.',
            mission_time_seconds=90.0,
            linked_event_type='hazard_detected',
            confidence=0.85,
            signal_quality=0.88,
            human_review_required=False,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['floating_debris', 'navigation_hazard', 'entanglement_risk'],
            annotation_tags=['surface debris', 'floating objects', 'navigation hazard', 'route planning'],
            metadata={
                'debris_density': 'moderate',
                'debris_types': ['wood', 'plastic', 'vegetation'],
                'entanglement_risk': 'low',
                'clear_path_available': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='flooded-rgb-surface-dock',
            use_case_slug='flooded-structure',
            sector_id='surface-structure',
            agent_role='surface-scout',
            agent_id='amphibious-drone-1',
            media_type='rgb_image',
            sensor_type='rgb_camera',
            file_path='/media/flooded-structure/rgb-surface-dock.png',
            title='Submerged Dock Structure',
            description='Partially submerged dock or pier structure visible at surface. Structural assessment and navigation reference.',
            mission_time_seconds=150.0,
            linked_event_type='sector-explored',
            confidence=0.88,
            signal_quality=0.90,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='clear',
            hazard_tags=['submerged_structure', 'collision_hazard'],
            annotation_tags=['submerged dock', 'structural reference', 'navigation landmark', 'partial submersion'],
            metadata={
                'structure_type': 'dock',
                'submersion_depth_m': 0.5,
                'structural_integrity': 'unknown',
                'collision_risk': 'moderate'
            }
        )
        
        # Underwater Murky Views
        ScenarioMediaArtifact.objects.create(
            slug='flooded-underwater-murky-corridor',
            use_case_slug='flooded-structure',
            sector_id='underwater-corridor-1',
            agent_role='underwater-inspector',
            agent_id='underwater-rov-1',
            media_type='low_light_image',
            sensor_type='underwater_camera',
            file_path='/media/flooded-structure/underwater-murky-corridor.png',
            title='Underwater Corridor - Low Visibility',
            description='Murky underwater view of flooded corridor. Limited visibility, particulate matter, low-light conditions.',
            mission_time_seconds=240.0,
            linked_event_type='sector-explored',
            confidence=0.65,
            signal_quality=0.60,
            human_review_required=True,
            lighting_state='low_light',
            visibility_condition='murky',
            hazard_tags=['low_visibility', 'murky_water', 'navigation_difficulty'],
            annotation_tags=['underwater', 'murky conditions', 'low visibility', 'corridor mapped'],
            metadata={
                'visibility_distance_m': 1.2,
                'water_turbidity': 'high',
                'particulate_density': 'heavy',
                'sonar_assist_required': True
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='flooded-underwater-obstruction',
            use_case_slug='flooded-structure',
            sector_id='underwater-corridor-2',
            agent_role='underwater-inspector',
            agent_id='underwater-rov-1',
            media_type='low_light_image',
            sensor_type='underwater_camera',
            file_path='/media/flooded-structure/underwater-obstruction.png',
            title='Underwater Obstruction Detected',
            description='Large obstruction blocking underwater passage. Debris or structural collapse requiring route adjustment.',
            mission_time_seconds=330.0,
            linked_event_type='hazard_detected',
            confidence=0.78,
            signal_quality=0.72,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='murky',
            hazard_tags=['obstruction', 'blocked_passage', 'route_adjustment_required'],
            annotation_tags=['underwater obstruction', 'blocked route', 'debris field', 'navigation blocked'],
            metadata={
                'obstruction_type': 'structural_collapse',
                'passage_blocked': True,
                'alternative_route_required': True,
                'clearance_feasible': False
            }
        )
        
        ScenarioMediaArtifact.objects.create(
            slug='flooded-underwater-debris-field',
            use_case_slug='flooded-structure',
            sector_id='underwater-zone-3',
            agent_role='underwater-inspector',
            agent_id='underwater-rov-1',
            media_type='low_light_image',
            sensor_type='underwater_camera',
            file_path='/media/flooded-structure/underwater-debris-field.png',
            title='Underwater Debris Field',
            description='Dense underwater debris field with multiple objects and structural fragments. Complex navigation environment.',
            mission_time_seconds=420.0,
            linked_event_type='sector-explored',
            confidence=0.70,
            signal_quality=0.68,
            human_review_required=True,
            lighting_state='visible_spotlight',
            visibility_condition='murky',
            hazard_tags=['debris_field', 'entanglement_risk', 'navigation_complex'],
            annotation_tags=['debris field', 'multiple objects', 'complex terrain', 'careful navigation required'],
            metadata={
                'debris_density': 'high',
                'object_count': 'numerous',
                'entanglement_risk': 'high',
                'navigation_difficulty': 'severe',
                'sonar_mapping_recommended': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  Flooded Structure media (6 artifacts)'))
