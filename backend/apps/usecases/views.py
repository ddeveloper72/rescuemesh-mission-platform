"""
Use case API views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UseCaseTemplate, TerrainProfile, AgentRoleTemplate
from .serializers import (
    UseCaseTemplateListSerializer,
    UseCaseTemplateDetailSerializer,
    TerrainProfileSerializer,
    AgentRoleTemplateSerializer,
    DemoProfileSerializer
)


class UseCaseTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for use case templates.
    Read-only since these are managed via Django admin.
    """
    queryset = UseCaseTemplate.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UseCaseTemplateListSerializer
        return UseCaseTemplateDetailSerializer
    
    @action(detail=True, methods=['get'])
    def demo_profile(self, request, slug=None):
        """
        Get complete demo profile for a use case.
        Returns data in the format expected by the frontend demo dashboard.
        """
        use_case = self.get_object()
        terrain = use_case.terrain
        
        # Build agents list from agent role templates
        agents = []
        for i, agent_role in enumerate(use_case.agent_roles.all(), 1):
            agent_data = {
                'id': f'agent-{chr(96 + i)}',  # agent-a, agent-b, etc.
                'name': agent_role.name,
                'type': agent_role.agent_type,
                'role': agent_role.role,
                'state': 'healthy',  # Default state for demo
                'battery': 100,
                'location': {'x': 0, 'y': 0, 'z': 0},
                'capabilities': agent_role.capabilities,
                'sensors': [
                    {
                        'type': sensor.sensor_type,
                        'name': sensor.display_name,
                        'status': 'operational'
                    }
                    for sensor in agent_role.sensor_packages.all()
                ],
                'specifications': agent_role.specifications
            }
            agents.append(agent_data)
        
        # Build expected failures list
        expected_failures = [
            {
                'name': failure.name,
                'affectedComponent': failure.affected_component,
                'severity': failure.severity,
                'triggerType': failure.trigger_type,
                'description': failure.description,
                'effects': failure.effects,
                'operatorMessage': failure.operator_message
            }
            for failure in use_case.failure_profiles.all()
        ]
        
        # Build expected outputs list
        expected_outputs = [
            {
                'name': output.name,
                'type': output.output_type,
                'description': output.description,
                'confidenceRequired': output.confidence_required,
                'humanReviewRequired': output.human_review_required,
                'priority': output.display_priority
            }
            for output in use_case.expected_outputs.all().order_by('-display_priority')
        ]
        
        # Build simulation params
        simulation_params = {
            'mapType': self._get_map_type(use_case.slug),
            'environmentTags': terrain.hazards if terrain else [],
            'riskAssessment': {
                'communications': self._assess_comms_risk(terrain),
                'battery': 'High',  # Default
                'sensors': 'Medium'  # Default
            },
            'duration': '15-20 minutes',
            'missionConfidence': 0.75
        }
        
        # Build timeline (sample - would be generated from simulation)
        timeline = self._generate_sample_timeline(use_case, agents)
        
        # Build AI analyst info
        ai_analyst = {}
        first_prompt = use_case.ai_prompts.filter(is_active=True).first()
        if first_prompt:
            ai_analyst = {
                'role': first_prompt.role,
                'promptSummary': first_prompt.description,
                'findings': [],
                'humanReviewRequired': first_prompt.requires_human_review
            }
        
        # Build response
        profile_data = {
            'slug': use_case.slug,
            'title': use_case.title,
            'priority': use_case.priority,
            'objective': use_case.objective,
            'terrain': {
                'type': terrain.terrain_type if terrain else '',
                'gpsStatus': terrain.gps_status if terrain else 'unknown',
                'lighting': terrain.lighting_conditions if terrain else '',
                'hazards': terrain.hazards if terrain else [],
                'accessibility': terrain.accessibility if terrain else ''
            },
            'agents': agents,
            'expectedFailures': expected_failures,
            'expectedOutputs': expected_outputs,
            'simulationParams': simulation_params,
            'timeline': timeline,
            'aiAnalyst': ai_analyst
        }
        
        serializer = DemoProfileSerializer(profile_data)
        return Response(serializer.data)
    
    def _get_map_type(self, slug):
        """Determine map type from use case slug"""
        map_types = {
            'collapsed-building-search': 'void-map',
            'cave-rescue': 'cave-map',
            'flooded-structure': 'flood-map',
            'industrial-inspection': 'industrial-map'
        }
        return map_types.get(slug, 'void-map')
    
    def _assess_comms_risk(self, terrain):
        """Assess communications risk from terrain"""
        if not terrain:
            return 'Medium'
        if terrain.gps_status == 'denied':
            return 'Critical'
        elif terrain.gps_status == 'degraded':
            return 'High'
        return 'Medium'
    
    def _generate_sample_timeline(self, use_case, agents):
        """Generate sample timeline events"""
        return [
            {
                'time': '00:00',
                'type': 'mission-start',
                'title': 'Mission Started',
                'description': f'{use_case.title} mission initiated',
                'agent': None
            },
            {
                'time': '02:30',
                'type': 'mapping',
                'title': 'Primary mapping in progress',
                'description': 'Initial sector mapping underway',
                'agent': agents[0]['id'] if agents else None,
                'confidence': 0.85
            }
        ]


class TerrainProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for terrain profiles"""
    queryset = TerrainProfile.objects.all()
    serializer_class = TerrainProfileSerializer


class AgentRoleTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for agent role templates"""
    queryset = AgentRoleTemplate.objects.all()
    serializer_class = AgentRoleTemplateSerializer
    filterset_fields = ['use_case', 'agent_type']
