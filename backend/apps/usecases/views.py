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
from .services import build_demo_profile


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
        profile_data = build_demo_profile(use_case)
        serializer = DemoProfileSerializer(profile_data)
        return Response(serializer.data)


class TerrainProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for terrain profiles"""
    queryset = TerrainProfile.objects.all()
    serializer_class = TerrainProfileSerializer


class AgentRoleTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for agent role templates"""
    queryset = AgentRoleTemplate.objects.all()
    serializer_class = AgentRoleTemplateSerializer
    filterset_fields = ['use_case', 'agent_type']
