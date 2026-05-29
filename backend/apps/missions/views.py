"""
Mission API views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Mission, MissionEvent, MissionSimulation
from .serializers import (
    MissionSerializer, MissionEventSerializer, MissionCreateSerializer,
    MissionSimulationSerializer, SpeedControlSerializer
)
from .services.simulation import calculate_mission_state


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
        mission.save()
        
        # Create mission end event
        MissionEvent.objects.create(
            mission=mission,
            event_type='mission_end',
            title='Mission Completed',
            description=f'Mission {mission.mission_id} completed'
        )
        
        return Response(MissionSerializer(mission).data)    
    @action(detail=True, methods=['get'], url_path='state')
    def simulation_state(self, request, pk=None):
        """
        Get the current mission simulation state.
        
        GET /api/v1/missions/{pk}/state/
        
        This calculates the complete dashboard state on-demand based on:
        - Mission start time
        - Speed multiplier
        - Use case type
        - Elapsed time
        
        Returns a complete dashboard state including agents, sensors,
        map coverage, events, and AI analysis.
        """
        mission = self.get_object()
        
        # Get or create simulation
        simulation, created = MissionSimulation.objects.get_or_create(
            mission=mission,
            defaults={
                'random_seed': mission.simulation_seed,
                'speed_multiplier': 1.0,
                'status': 'not_started'
            }
        )
        
        # Get use case slug from use_case_template or fall back to use_case_type
        if mission.use_case_template:
            use_case_slug = mission.use_case_template.slug
        else:
            use_case_slug = mission.use_case_type
        
        # Calculate current state
        state = calculate_mission_state(
            mission_id=mission.mission_id,
            mission_name=mission.name,
            use_case_slug=use_case_slug,
            elapsed_seconds=simulation.get_elapsed_seconds(),
            speed_multiplier=simulation.speed_multiplier,
            started_at=simulation.started_at,
            status=simulation.status,
            random_seed=simulation.random_seed
        )
        
        return Response(state)
    
    @action(detail=True, methods=['post'], url_path='start-sim')
    def start_simulation(self, request, pk=None):
        """
        Start the mission simulation.
        
        POST /api/v1/missions/{pk}/start-sim/
        """
        mission = self.get_object()
        
        # Get or create simulation
        simulation, created = MissionSimulation.objects.get_or_create(
            mission=mission,
            defaults={
                'random_seed': mission.simulation_seed,
                'speed_multiplier': 1.0,
                'status': 'not_started'
            }
        )
        
        if simulation.status == 'running':
            return Response(
                {'error': 'Simulation is already running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start or resume
        simulation.status = 'running'
        simulation.started_at = timezone.now()
        simulation.save()
        
        return Response({
            'status': 'running',
            'message': 'Simulation started',
            'elapsed_seconds': simulation.get_elapsed_seconds()
        })
    
    @action(detail=True, methods=['post'], url_path='pause-sim')
    def pause_simulation(self, request, pk=None):
        """
        Pause the mission simulation.
        
        POST /api/v1/missions/{pk}/pause-sim/
        """
        mission = self.get_object()
        
        try:
            simulation = mission.simulation
        except MissionSimulation.DoesNotExist:
            return Response(
                {'error': 'No simulation exists for this mission'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if simulation.status != 'running':
            return Response(
                {'error': 'Simulation is not running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accumulate elapsed time before pausing
        simulation.accumulated_elapsed_seconds = simulation.get_elapsed_seconds()
        simulation.status = 'paused'
        simulation.paused_at = timezone.now()
        simulation.save()
        
        return Response({
            'status': 'paused',
            'message': 'Simulation paused',
            'elapsed_seconds': simulation.get_elapsed_seconds()
        })
    
    @action(detail=True, methods=['post'], url_path='reset-sim')
    def reset_simulation(self, request, pk=None):
        """
        Reset the mission simulation to initial state.
        
        POST /api/v1/missions/{pk}/reset-sim/
        """
        mission = self.get_object()
        
        try:
            simulation = mission.simulation
        except MissionSimulation.DoesNotExist:
            return Response(
                {'error': 'No simulation exists for this mission'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        simulation.status = 'not_started'
        simulation.started_at = None
        simulation.paused_at = None
        simulation.accumulated_elapsed_seconds = 0.0
        simulation.save()
        
        return Response({
            'status': 'not_started',
            'message': 'Simulation reset',
            'elapsed_seconds': 0.0
        })
    
    @action(detail=True, methods=['post'], url_path='speed-sim')
    def set_simulation_speed(self, request, pk=None):
        """
        Set simulation speed multiplier.
        
        POST /api/v1/missions/{pk}/speed-sim/
        
        Body:
        {
            "speed_multiplier": 5.0
        }
        
        Allowed values: 0.5, 1.0, 2.0, 5.0, 10.0, 20.0
        """
        mission = self.get_object()
        
        try:
            simulation = mission.simulation
        except MissionSimulation.DoesNotExist:
            return Response(
                {'error': 'No simulation exists for this mission'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SpeedControlSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If running, accumulate time before changing speed
        if simulation.status == 'running':
            simulation.accumulated_elapsed_seconds = simulation.get_elapsed_seconds()
            simulation.started_at = timezone.now()
        
        simulation.speed_multiplier = serializer.validated_data['speed_multiplier']
        simulation.save()
        
        return Response({
            'speed_multiplier': simulation.speed_multiplier,
            'message': f'Speed set to {simulation.speed_multiplier}x',
            'elapsed_seconds': simulation.get_elapsed_seconds()
        })

class MissionEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mission events.
    """
    queryset = MissionEvent.objects.all()
    serializer_class = MissionEventSerializer
    filterset_fields = ['mission', 'event_type']



class MissionSimulationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mission simulations.
    
    Provides deterministic, API-based simulation control without
    WebSockets, Celery, or background tasks.
    """
    queryset = MissionSimulation.objects.all()
    serializer_class = MissionSimulationSerializer
    
    @action(detail=True, methods=['get'])
    def state(self, request, pk=None):
        """
        Get the current mission state.
        
        This calculates the complete dashboard state on-demand based on:
        - Mission start time
        - Speed multiplier
        - Use case type
        - Elapsed time
        
        Returns a complete dashboard state including agents, sensors,
        map coverage, events, and AI analysis.
        """
        simulation = self.get_object()
        mission = simulation.mission
        
        # Get use case slug from use_case_template or fall back to use_case_type
        if mission.use_case_template:
            use_case_slug = mission.use_case_template.slug
        else:
            use_case_slug = mission.use_case_type
        
        # Calculate current state
        state = calculate_mission_state(
            mission_id=mission.mission_id,
            mission_name=mission.name,
            use_case_slug=use_case_slug,
            elapsed_seconds=simulation.get_elapsed_seconds(),
            speed_multiplier=simulation.speed_multiplier,
            started_at=simulation.started_at,
            status=simulation.status,
            random_seed=simulation.random_seed
        )
        
        return Response(state)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start the simulation.
        
        POST /api/v1/missions/{mission_id}/simulation/start/
        """
        simulation = self.get_object()
        
        if simulation.status == 'running':
            return Response(
                {'error': 'Simulation is already running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start or resume
        simulation.status = 'running'
        simulation.started_at = timezone.now()
        simulation.save()
        
        return Response({
            'status': 'running',
            'message': 'Simulation started',
            'simulation': MissionSimulationSerializer(simulation).data
        })
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        Pause the simulation.
        
        POST /api/v1/missions/{mission_id}/simulation/pause/
        """
        simulation = self.get_object()
        
        if simulation.status != 'running':
            return Response(
                {'error': 'Simulation is not running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accumulate elapsed time before pausing
        simulation.accumulated_elapsed_seconds = simulation.get_elapsed_seconds()
        simulation.status = 'paused'
        simulation.paused_at = timezone.now()
        simulation.save()
        
        return Response({
            'status': 'paused',
            'message': 'Simulation paused',
            'simulation': MissionSimulationSerializer(simulation).data
        })
    
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """
        Reset the simulation to initial state.
        
        POST /api/v1/missions/{mission_id}/simulation/reset/
        """
        simulation = self.get_object()
        
        simulation.status = 'not_started'
        simulation.started_at = None
        simulation.paused_at = None
        simulation.accumulated_elapsed_seconds = 0.0
        simulation.save()
        
        return Response({
            'status': 'not_started',
            'message': 'Simulation reset',
            'simulation': MissionSimulationSerializer(simulation).data
        })
    
    @action(detail=True, methods=['post'])
    def speed(self, request, pk=None):
        """
        Set simulation speed multiplier.
        
        POST /api/v1/missions/{mission_id}/simulation/speed/
        
        Body:
        {
            "speed_multiplier": 5.0
        }
        
        Allowed values: 0.5, 1.0, 2.0, 5.0, 10.0, 20.0
        """
        simulation = self.get_object()
        serializer = SpeedControlSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If running, accumulate time before changing speed
        if simulation.status == 'running':
            simulation.accumulated_elapsed_seconds = simulation.get_elapsed_seconds()
            simulation.started_at = timezone.now()
        
        simulation.speed_multiplier = serializer.validated_data['speed_multiplier']
        simulation.save()
        
        return Response({
            'speed_multiplier': simulation.speed_multiplier,
            'message': f'Speed set to {simulation.speed_multiplier}x',
            'simulation': MissionSimulationSerializer(simulation).data
        })