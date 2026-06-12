"""
Django management command to seed initial use case templates.

Usage:
    python manage.py seed_usecases
    python manage.py seed_usecases --clear  # Clear existing data first
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.usecases.models import UseCaseTemplate, TerrainProfile, AgentRoleTemplate
from apps.sensors.models import SensorPackageTemplate
from apps.faults.models import FailureProfile
from apps.mapping.models import ExpectedOutputTemplate
from apps.ai_prompts.models import AIPromptTemplate


class Command(BaseCommand):
    help = 'Seed initial use case templates with all related data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing use case templates before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing use case templates...')
            UseCaseTemplate.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        self.stdout.write('Seeding use case templates...')
        
        with transaction.atomic():
            self.seed_collapsed_building()
            self.seed_cave_rescue()
            self.seed_flooded_structure()
            self.seed_industrial_inspection()
            self.seed_archaeological_exploration()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded all use case templates!'))

    def seed_collapsed_building(self):
        """Seed Collapsed Building Search use case"""
        self.stdout.write('Seeding Collapsed Building Search...')
        
        use_case = UseCaseTemplate.objects.create(
            slug='collapsed-building-search',
            title='Collapsed Building Search',
            priority='life_safety',
            summary='Search for survivors in structurally compromised buildings using autonomous mapping and multi-sensor detection.',
            objective='Deploy autonomous agents to map void spaces, detect thermal signatures, identify audio anomalies, and scan for electronic device signals within collapsed structures where human entry is too dangerous or physically impossible.',
            is_active=True,
            is_demo=True
        )
        
        # Terrain Profile
        TerrainProfile.objects.create(
            use_case=use_case,
            terrain_type='Collapsed multi-story structure with unstable voids',
            gps_status='denied',
            communication_conditions='Severe signal attenuation through concrete and rebar. Line-of-sight relay required.',
            lighting_conditions='Complete darkness in interior voids',
            hazards=['Unstable debris', 'Dust obscuration', 'Sharp obstacles', 'Void collapse risk', 'Electrical hazards'],
            accessibility='Inaccessible to human rescuers without structural stabilization',
            simulation_complexity='high'
        )
        
        # Agent Roles
        scout = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Scout Drone A',
            role='primary_mapping',
            description='Primary mapping drone with LiDAR and thermal sensors',
            default_quantity=1,
            agent_type='drone',
            capabilities=['3d_mapping', 'thermal_sensing', 'navigation'],
            specifications={'battery_capacity': 100, 'max_speed': 3.0, 'sensor_range': 10.0}
        )
        
        relay = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Relay Drone',
            role='communications_relay',
            description='Communications relay with ability to land and serve as static node',
            default_quantity=1,
            agent_type='drone',
            capabilities=['relay', 'navigation', 'sacrifice_landing'],
            specifications={'battery_capacity': 100, 'max_speed': 2.5}
        )
        
        thermal = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Thermal/Audio Drone',
            role='detection',
            description='Specialized detection drone with thermal camera and microphone array',
            default_quantity=1,
            agent_type='drone',
            capabilities=['thermal_sensing', 'audio_detection', 'device_scanning'],
            specifications={'battery_capacity': 100, 'max_speed': 2.0}
        )
        
        static = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Static Relay Node',
            role='base_relay',
            description='Entry-point communications relay',
            default_quantity=1,
            agent_type='relay_node',
            capabilities=['relay'],
            specifications={'powered': True}
        )
        
        # Sensors
        SensorPackageTemplate.objects.create(
            agent_role=scout,
            sensor_type='lidar',
            display_name='LiDAR Scanner',
            description='3D environment mapping',
            data_format='point_cloud',
            expected_output='3D void map with structural features',
            specifications={'range': 10.0, 'resolution': 0.05, 'frequency': 10},
            failure_modes=['dust_occlusion', 'range_degradation']
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=thermal,
            sensor_type='thermal',
            display_name='Thermal Camera',
            description='Heat signature detection',
            data_format='image',
            expected_output='Thermal anomalies indicating possible human presence',
            specifications={'resolution': '320x240', 'range': 50.0, 'sensitivity': 0.05},
            failure_modes=['dust_interference', 'calibration_drift']
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=thermal,
            sensor_type='microphone_array',
            display_name='Microphone Array',
            description='Voice and audio detection',
            data_format='audio',
            expected_output='Voice-like audio events',
            specifications={'channels': 4, 'frequency_range': '20-20000Hz', 'snr': 60},
            failure_modes=['ambient_noise', 'fan_noise']
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=thermal,
            sensor_type='wifi_scanner',
            display_name='WiFi/Bluetooth Scanner',
            description='Electronic device detection',
            data_format='json',
            expected_output='Device MAC addresses and signal strength',
            specifications={'scan_radius': 30.0},
            failure_modes=['signal_attenuation']
        )
        
        # Failure Profiles
        FailureProfile.objects.create(
            use_case=use_case,
            name='Dust Occlusion',
            description='Airborne dust degrades LiDAR returns',
            affected_component='lidar',
            severity='medium',
            trigger_type='sector_based',
            trigger_conditions={'sector': 'collapsed_corridor_2'},
            effects={'map_confidence_drop': 0.35, 'sensor_noise_multiplier': 2.4},
            operator_message='LiDAR quality degraded due to dust particulates',
            is_recoverable=False
        )
        
        FailureProfile.objects.create(
            use_case=use_case,
            name='Battery Degradation',
            description='Unexpected battery capacity loss',
            affected_component='battery',
            severity='high',
            trigger_type='time_based',
            trigger_conditions={'elapsed_minutes': 12},
            effects={'battery_drain_multiplier': 3.0, 'forces_landing': True},
            operator_message='Battery experiencing accelerated drain',
            is_recoverable=False
        )
        
        FailureProfile.objects.create(
            use_case=use_case,
            name='Communications Intermittent',
            description='Signal loss through heavy structure',
            affected_component='radio',
            severity='high',
            trigger_type='sector_based',
            trigger_conditions={'sector': 'deep_void'},
            effects={'packet_loss': 0.7, 'requires_relay': True},
            operator_message='Communications degraded, relay required',
            is_recoverable=True,
            recovery_actions=['deploy_relay', 'move_closer']
        )
        
        # Expected Outputs
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='3D Void Map',
            output_type='3d_map',
            description='Complete 3D reconstruction of accessible void spaces',
            confidence_required=True,
            human_review_required=False,
            display_priority=10,
            icon_name='map',
            output_schema={'format': 'point_cloud', 'confidence_per_sector': True}
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Thermal Anomalies',
            output_type='thermal',
            description='Heat signatures consistent with human presence',
            confidence_required=True,
            human_review_required=True,
            display_priority=9,
            icon_name='thermal',
            output_schema={'detections': [], 'confidence': 'float'}
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Audio Events',
            output_type='audio',
            description='Voice-like audio signatures',
            confidence_required=True,
            human_review_required=True,
            display_priority=8,
            icon_name='audio',
            output_schema={'events': [], 'confidence': 'float'}
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Device Scan Results',
            output_type='device_scan',
            description='WiFi and Bluetooth device detections',
            confidence_required=False,
            human_review_required=True,
            display_priority=7,
            icon_name='wifi',
            output_schema={'devices': [], 'signal_strength': 'float'}
        )
        
        # AI Prompt
        AIPromptTemplate.objects.create(
            use_case=use_case,
            name='Thermal/Audio Analyst',
            role='thermal_analyst',
            description='Analyze thermal and audio data for survivor detection',
            prompt_text='''Analyze the following sensor data from a collapsed building search mission:

Thermal Data: {thermal_frames}
Audio Data: {audio_segments}
Device Scan: {wifi_bluetooth_results}
3D Map Context: {void_map_summary}

Tasks:
1. Identify possible human presence indicators
2. Rank detections by confidence
3. Highlight any hazards blocking access
4. Suggest next investigation priorities

Output Format: JSON with detections array, confidence scores, and recommended actions.''',
            system_prompt='You are an expert search and rescue analyst. Prioritize life safety. Be conservative with confidence scores.',
            input_types=['thermal_frames', 'audio_segments', 'wifi_bluetooth_scan', '3d_void_map'],
            output_schema={'detections': [], 'confidence': 'float', 'recommended_action': 'string'},
            temperature=0.3,
            max_tokens=1000,
            requires_human_review=True,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS('  Collapsed Building Search'))

    def seed_cave_rescue(self):
        """Seed Cave Rescue use case"""
        self.stdout.write('Seeding Cave Rescue...')
        
        use_case = UseCaseTemplate.objects.create(
            slug='cave-rescue',
            title='Cave Rescue',
            priority='life_safety',
            summary='Map complex underground cave systems and establish communication relay network for rescue operations.',
            objective='Deploy autonomous mapping agents to explore and map cave passages, establish relay communications through GPS-denied underground environments, and locate missing persons or hazards.',
            is_active=True,
            is_demo=True
        )
        
        TerrainProfile.objects.create(
            use_case=use_case,
            terrain_type='Underground cave system with narrow passages',
            gps_status='denied',
            communication_conditions='Complete GPS denial. Radio signals attenuate rapidly. Multi-hop relay required.',
            lighting_conditions='Complete darkness',
            hazards=['Rock fall', 'Water pools', 'Narrow passages', 'Low oxygen pockets', 'Unstable formations'],
            accessibility='Extremely limited human access beyond entry chambers',
            simulation_complexity='extreme'
        )
        
        scout = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Cave Scout Drone',
            role='primary_mapping',
            description='Compact mapping drone for confined spaces',
            default_quantity=2,
            agent_type='drone',
            capabilities=['3d_mapping', 'navigation', 'tight_space_flight'],
            specifications={'battery_capacity': 80, 'max_speed': 2.0, 'size': 'compact'}
        )
        
        relay = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Relay Drone',
            role='communications_relay',
            description='Sacrificial relay node for underground communications',
            default_quantity=2,
            agent_type='drone',
            capabilities=['relay', 'sacrifice_landing'],
            specifications={'battery_capacity': 120, 'relay_range': 50.0}
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=scout,
            sensor_type='lidar',
            display_name='Cave LiDAR',
            description='High-precision cave passage mapping',
            data_format='point_cloud',
            specifications={'range': 15.0, 'resolution': 0.02},
            failure_modes=['moisture_interference', 'range_degradation']
        )
        
        FailureProfile.objects.create(
            use_case=use_case,
            name='Navigation Drift',
            description='IMU drift without GPS correction',
            affected_component='imu',
            severity='medium',
            trigger_type='time_based',
            trigger_conditions={'elapsed_minutes': 8},
            effects={'position_uncertainty': 2.0, 'map_confidence_drop': 0.25},
            operator_message='Navigation uncertainty increasing due to GPS denial',
            is_recoverable=False
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Cave Passage Map',
            output_type='3d_map',
            description='3D map of traversable cave passages',
            confidence_required=True,
            human_review_required=False,
            display_priority=10,
            icon_name='map'
        )
        
        AIPromptTemplate.objects.create(
            use_case=use_case,
            name='Cave Route Planner',
            role='route_planner',
            description='Plan safe access routes through cave system',
            prompt_text='Analyze cave passage map and suggest safe access routes for human rescuers.',
            input_types=['cave_map', 'hazard_locations'],
            output_schema={'routes': [], 'safety_rating': 'string'},
            temperature=0.2,
            max_tokens=800,
            requires_human_review=True
        )
        
        self.stdout.write(self.style.SUCCESS('  Cave Rescue'))

    def seed_flooded_structure(self):
        """Seed Flooded Structure use case"""
        self.stdout.write('Seeding Flooded Structure...')
        
        use_case = UseCaseTemplate.objects.create(
            slug='flooded-structure',
            title='Flooded Structure',
            priority='infrastructure_safety',
            summary='Deploy amphibious agents to inspect and map partially or fully flooded structures.',
            objective='Use amphibious micro-agents to navigate flooded spaces, map underwater and surface obstacles, assess structural damage, and identify hazards in environments inaccessible to standard aerial or ground robots.',
            is_active=True,
            is_demo=True
        )
        
        TerrainProfile.objects.create(
            use_case=use_case,
            terrain_type='Partially flooded building or tunnel system',
            gps_status='intermittent',
            communication_conditions='Radio signals blocked underwater. Surface relay required.',
            lighting_conditions='Low visibility underwater',
            hazards=['Submerged debris', 'Current flow', 'Water quality', 'Electrical hazards', 'Unstable structures'],
            accessibility='Inaccessible to non-amphibious platforms',
            simulation_complexity='high'
        )
        
        amphibious = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Amphibious Micro Agent',
            role='amphibious_mapper',
            description='Can operate above and below water surface',
            default_quantity=2,
            agent_type='amphibious_robot',
            capabilities=['underwater_navigation', 'surface_navigation', 'sonar_mapping'],
            specifications={'battery_capacity': 90, 'max_depth': 5.0}
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=amphibious,
            sensor_type='sonar',
            display_name='Forward Sonar',
            description='Underwater obstacle detection',
            data_format='json',
            specifications={'range': 8.0, 'frequency': '200kHz'}
        )
        
        FailureProfile.objects.create(
            use_case=use_case,
            name='Water Ingress',
            description='Seal failure causing water intrusion',
            affected_component='general',
            severity='critical',
            trigger_type='random_seeded',
            effects={'immediate_failure': True},
            operator_message='Critical seal failure detected',
            is_recoverable=False
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Flood Extent Map',
            output_type='3d_map',
            description='Map of flooded and accessible areas',
            confidence_required=True,
            display_priority=10,
            icon_name='water'
        )
        
        AIPromptTemplate.objects.create(
            use_case=use_case,
            name='Structural Risk Analyst',
            role='risk_assessor',
            description='Assess structural integrity from sensor data',
            prompt_text='Analyze sonar and visual data to identify structural damage and access risks.',
            input_types=['sonar_data', 'visual_images', 'water_quality'],
            output_schema={'risk_level': 'string', 'hazards': []},
            temperature=0.3,
            max_tokens=1000,
            requires_human_review=True
        )
        
        self.stdout.write(self.style.SUCCESS('  Flooded Structure'))

    def seed_industrial_inspection(self):
        """Seed Industrial Inspection use case"""
        self.stdout.write('Seeding Industrial Inspection...')
        
        use_case = UseCaseTemplate.objects.create(
            slug='industrial-inspection',
            title='Industrial Confined Space Inspection',
            priority='operational_efficiency',
            summary='Inspect hazardous industrial confined spaces using autonomous agents with environmental monitoring.',
            objective='Deploy sensor-equipped agents into industrial confined spaces (tanks, pipes, shafts) to perform visual inspection, gas detection, structural assessment, and equipment monitoring without requiring human entry.',
            is_active=True,
            is_demo=True
        )
        
        TerrainProfile.objects.create(
            use_case=use_case,
            terrain_type='Industrial confined space with potential atmospheric hazards',
            gps_status='denied',
            communication_conditions='Metal structures cause signal attenuation',
            lighting_conditions='Dark or poorly lit',
            hazards=['Toxic gases', 'Low oxygen', 'High heat', 'Moving equipment', 'Corrosive materials'],
            accessibility='Requires permit and safety protocols for human entry',
            simulation_complexity='medium'
        )
        
        inspector = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Industrial Inspector Drone',
            role='inspection',
            description='Equipped with visual and environmental sensors',
            default_quantity=2,
            agent_type='drone',
            capabilities=['visual_inspection', 'gas_detection', 'thermal_inspection'],
            specifications={'battery_capacity': 100, 'max_speed': 2.0}
        )
        
        static_sensor = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Static Environmental Sensor',
            role='monitoring',
            description='Dropped sensor package for continuous monitoring',
            default_quantity=2,
            agent_type='sensor',
            capabilities=['gas_detection', 'temperature_monitoring'],
            specifications={'battery_capacity': 1000, 'powered': False}
        )
        
        SensorPackageTemplate.objects.create(
            agent_role=inspector,
            sensor_type='gas_sensor',
            display_name='Multi-Gas Detector',
            description='Detects toxic and combustible gases',
            data_format='scalar',
            specifications={'gases': ['CO', 'CO2', 'CH4', 'H2S']},
            failure_modes=['sensor_poisoning', 'calibration_drift']
        )
        
        FailureProfile.objects.create(
            use_case=use_case,
            name='Heat Degradation',
            description='Electronics degraded by high ambient temperature',
            affected_component='general',
            severity='medium',
            trigger_type='sector_based',
            trigger_conditions={'sector': 'high_temp_zone'},
            effects={'sensor_reliability': 0.6, 'battery_drain_multiplier': 1.5},
            operator_message='High temperature affecting system performance',
            is_recoverable=True
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Visual Inspection Report',
            output_type='report',
            description='Visual condition assessment with annotations',
            confidence_required=False,
            display_priority=10,
            icon_name='camera'
        )
        
        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Environmental Data',
            output_type='environmental',
            description='Gas concentration and temperature readings',
            confidence_required=True,
            display_priority=9,
            icon_name='gauge'
        )
        
        AIPromptTemplate.objects.create(
            use_case=use_case,
            name='Equipment Condition Analyst',
            role='sensor_analyst',
            description='Analyze visual and sensor data for equipment condition',
            prompt_text='Review inspection images and environmental data to assess equipment condition and identify maintenance needs.',
            input_types=['visual_images', 'gas_readings', 'thermal_data'],
            output_schema={'condition_rating': 'string', 'maintenance_recommendations': []},
            temperature=0.4,
            max_tokens=1200,
            requires_human_review=True
        )

        self.stdout.write(self.style.SUCCESS('  Industrial Confined Space Inspection'))

    def seed_archaeological_exploration(self):
        """Seed Archaeological Exploration use case"""
        self.stdout.write('Seeding Archaeological Exploration...')

        use_case = UseCaseTemplate.objects.create(
            slug='archaeological-exploration',
            title='Archaeological Exploration',
            priority='navigation_safety',
            summary='Map and document fragile underground heritage spaces without unnecessary human entry or disturbance.',
            objective='Deploy low-disturbance autonomous agents to map fragile chambers, monitor environmental conditions, preserve communication links, and flag possible artefact or conservation review areas for qualified human experts.',
            is_active=True,
            is_demo=True
        )

        TerrainProfile.objects.create(
            use_case=use_case,
            terrain_type='Fragile underground chamber complex with restricted access passages',
            gps_status='denied',
            communication_conditions='GPS denied underground. Curved passages and stone mass require relay positioning.',
            lighting_conditions='Dark with strict low-disturbance artificial lighting',
            hazards=['Low oxygen zones', 'Unstable passages', 'Dust-sensitive surfaces', 'Conservation constraints'],
            accessibility='Human access restricted to protect fragile site fabric and artefacts',
            simulation_complexity='high'
        )

        scout = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Heritage Scout A',
            role='primary_mapping',
            description='Low-disturbance LiDAR and low-light mapping agent',
            default_quantity=1,
            agent_type='drone',
            capabilities=['3d_mapping', 'low_light_navigation', 'no_contact_survey'],
            specifications={'battery_capacity': 90, 'max_speed': 1.2, 'disturbance_mode': 'low'}
        )

        inspector = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Micro Inspector B',
            role='narrow_passage_survey',
            description='Compact close-range imaging agent for side passages and restricted voids',
            default_quantity=1,
            agent_type='ground_robot',
            capabilities=['compact_navigation', 'close_range_imaging', 'artefact_candidate_marking'],
            specifications={'battery_capacity': 70, 'max_speed': 0.6, 'size': 'micro'}
        )

        relay = AgentRoleTemplate.objects.create(
            use_case=use_case,
            name='Relay Node ARCH-01',
            role='communications_relay',
            description='Static relay and environmental monitor for the entry chamber',
            default_quantity=1,
            agent_type='relay_node',
            capabilities=['relay', 'environmental_monitoring', 'long_duration_beacon'],
            specifications={'battery_capacity': 180, 'relay_range': 45.0}
        )

        SensorPackageTemplate.objects.create(
            agent_role=scout,
            sensor_type='lidar',
            display_name='Heritage LiDAR',
            description='Low-disturbance chamber geometry mapping',
            data_format='point_cloud',
            expected_output='3D chamber geometry and route profile',
            specifications={'range': 12.0, 'resolution': 0.02, 'scan_mode': 'low_disturbance'},
            failure_modes=['dust_disturbance_limit', 'feature_poor_geometry']
        )

        SensorPackageTemplate.objects.create(
            agent_role=inspector,
            sensor_type='camera',
            display_name='Close-Range Conservation Camera',
            description='Review-only imaging for candidate artefacts and fragile surfaces',
            data_format='image',
            expected_output='Candidate review images for human experts',
            specifications={'resolution': '4k', 'lighting': 'low_heat_led'},
            failure_modes=['low_light_noise', 'surface_glare']
        )

        SensorPackageTemplate.objects.create(
            agent_role=relay,
            sensor_type='environmental',
            display_name='Chamber Environment Monitor',
            description='Temperature, humidity, oxygen, and CO2 monitoring',
            data_format='json',
            expected_output='Environmental readings for conservation review',
            specifications={'readings': ['temperature', 'humidity', 'oxygen', 'co2']},
            failure_modes=['sensor_drift']
        )

        FailureProfile.objects.create(
            use_case=use_case,
            name='Dust-Sensitive Zone',
            description='Agent speed must be reduced near fragile deposits to avoid disturbance',
            affected_component='navigation',
            severity='medium',
            trigger_type='sector_based',
            trigger_conditions={'sector': 'decorated_wall_zone'},
            effects={'mapping_rate_multiplier': 0.5, 'requires_low_disturbance_mode': True},
            operator_message='Conservation-safe mode enabled near dust-sensitive surface',
            is_recoverable=True,
            recovery_actions=['reduce_speed', 'increase_standoff_distance']
        )

        FailureProfile.objects.create(
            use_case=use_case,
            name='Narrow Passage Signal Loss',
            description='Curved passage geometry increases packet loss for the micro inspector',
            affected_component='radio',
            severity='high',
            trigger_type='sector_based',
            trigger_conditions={'sector': 'north_alcove'},
            effects={'packet_loss': 0.45, 'requires_relay': True},
            operator_message='Relay hold required before continuing side-passage survey',
            is_recoverable=True,
            recovery_actions=['hold_position', 'deploy_relay']
        )

        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='3D Chamber Geometry',
            output_type='3d_map',
            description='Detailed 3D point cloud of chamber geometry and access routes',
            confidence_required=True,
            human_review_required=False,
            display_priority=10,
            icon_name='map'
        )

        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Artefact Candidate Log',
            output_type='ai_analysis',
            description='Review-only list of possible artefacts, inscriptions, or decorated surfaces',
            confidence_required=True,
            human_review_required=True,
            display_priority=9,
            icon_name='sparkles'
        )

        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Environmental Readings',
            output_type='environmental',
            description='Temperature, humidity, oxygen, and CO2 trends around sensitive areas',
            confidence_required=False,
            human_review_required=True,
            display_priority=8,
            icon_name='gauge'
        )

        ExpectedOutputTemplate.objects.create(
            use_case=use_case,
            name='Conservation Route Notes',
            output_type='report',
            description='Suggested low-disturbance inspection route for human experts',
            confidence_required=True,
            human_review_required=True,
            display_priority=7,
            icon_name='route'
        )

        AIPromptTemplate.objects.create(
            use_case=use_case,
            name='Heritage Documentation Assistant',
            role='heritage_documentation',
            description='Analyze geometry, environmental readings, and visual candidates while preserving expert archaeological interpretation.',
            prompt_text='Review heritage survey data and identify areas requiring archaeologist or conservation expert review. Do not make definitive artefact claims.',
            system_prompt='You support non-destructive heritage documentation. Flag candidates for expert review and avoid definitive archaeological identification.',
            input_types=['chamber_geometry', 'environmental_readings', 'candidate_images'],
            output_schema={'review_candidates': [], 'conservation_notes': [], 'confidence': 'float'},
            temperature=0.2,
            max_tokens=1000,
            requires_human_review=True,
            is_active=True
        )

        self.stdout.write(self.style.SUCCESS('  Archaeological Exploration'))
        
