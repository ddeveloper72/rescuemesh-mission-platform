"""
Agent API views.
"""
from rest_framework import viewsets
from .models import Agent, AgentStateChange
from .serializers import AgentSerializer, AgentStateChangeSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agents."""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    filterset_fields = ['agent_type', 'state', 'current_mission']


class AgentStateChangeViewSet(viewsets.ModelViewSet):
    """ViewSet for agent state changes."""
    queryset = AgentStateChange.objects.all()
    serializer_class = AgentStateChangeSerializer
    filterset_fields = ['agent', 'mission']
