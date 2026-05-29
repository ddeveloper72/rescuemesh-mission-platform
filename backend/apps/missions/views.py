"""
Mission API views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Mission, MissionEvent
from .serializers import MissionSerializer, MissionEventSerializer, MissionCreateSerializer


class MissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing missions.
    """
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MissionCreateSerializer
        return MissionSerializer
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get all events for a mission."""
        mission = self.get_object()
        events = mission.events.all()
        serializer = MissionEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a mission."""
        mission = self.get_object()
        if mission.status != 'planned':
            return Response(
                {'error': 'Mission can only be started from planned status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mission.status = 'active'
        from django.utils import timezone
        mission.started_at = timezone.now()
        mission.save()
        
        # Create mission start event
        MissionEvent.objects.create(
            mission=mission,
            event_type='mission_start',
            title='Mission Started',
            description=f'Mission {mission.mission_id} started'
        )
        
        return Response(MissionSerializer(mission).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a mission."""
        mission = self.get_object()
        mission.status = 'completed'
        from django.utils import timezone
        mission.completed_at = timezone.now()
        mission.save()
        
        # Create mission end event
        MissionEvent.objects.create(
            mission=mission,
            event_type='mission_end',
            title='Mission Completed',
            description=f'Mission {mission.mission_id} completed'
        )
        
        return Response(MissionSerializer(mission).data)


class MissionEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mission events.
    """
    queryset = MissionEvent.objects.all()
    serializer_class = MissionEventSerializer
    filterset_fields = ['mission', 'event_type']
