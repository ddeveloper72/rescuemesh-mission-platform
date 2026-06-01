"""
Mission API views.

This module provides REST API endpoints for mission management, simulation control,
and mission state retrieval.

**Key Endpoints:**
- GET /api/v1/missions/ - List all missions
- POST /api/v1/missions/ - Create a new mission
- GET /api/v1/missions/{pk}/ - Get mission details
- POST /api/v1/missions/{pk}/start/ - Start a mission
- POST /api/v1/missions/{pk}/complete/ - Complete a mission
- GET /api/v1/missions/{pk}/events/ - Get mission events timeline
- GET /api/v1/missions/{pk}/state/ - Get current simulation state (MOST IMPORTANT)
- POST /api/v1/missions/{pk}/start-sim/ - Start simulation
- POST /api/v1/missions/{pk}/pause-sim/ - Pause simulation
- POST /api/v1/missions/{pk}/reset-sim/ - Reset simulation
- POST /api/v1/missions/{pk}/set-speed/ - Set simulation speed multiplier

**Frontend Integration:**
The dashboard polls `/api/v1/missions/{pk}/state/` every 2 seconds to get:
- Agent positions and states
- Sensor data (detections, observations)
- Map coverage progress
- Timeline events
- AI analysis results

**Simulation Architecture:**
This is a deterministic, on-demand simulation. No WebSockets, no Celery,
no background tasks. State is computed per request based on elapsed time.
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
    ViewSet for managing missions and simulations.
    
    Provides CRUD operations for missions plus specialized actions for
    simulation control and state retrieval.
    
    **Simulation Control Actions:**
    - `simulation_state()`: GET current dashboard state (polled by frontend)
    - `start_simulation()`: POST to start/resume simulation
    - `pause_simulation()`: POST to pause simulation
    - `reset_simulation()`: POST to reset to initial state
    - `set_simulation_speed()`: POST to change speed multiplier
    
    **Mission Lifecycle Actions:**
    - `start()`: Mark mission as active (different from start_simulation)
    - `complete()`: Mark mission as completed
    - `events()`: Get mission events timeline
    
    **Authorization:**
    Currently no authentication required (MVP). Future versions will add
    role-based access control for mission operators vs viewers.
    """
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    
    def get_serializer_class(self):
        """Use MissionCreateSerializer for POST, MissionSerializer for GET."""
        if self.action == 'create':
            return MissionCreateSerializer
        return MissionSerializer
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """
        Get all events for a mission in chronological order.
        
        **Endpoint:** GET /api/v1/missions/{pk}/events/
        
        Returns the complete mission timeline as an array of timestamped events.
        Events include agent deployments, state changes, detections, failures,
        and operator decisions.
        
        **Response:**
        ```json
        [
          {
            "id": "uuid",
            "event_type": "agent_deployed",
            "timestamp": "2026-06-01T14:30:00Z",
            "title": "Drone A Deployed",
            "description": "Scout drone entered collapsed building",
            "confidence": null,
            "event_data": {...}
          },
          ...
        ]
        ```
        """
        mission = self.get_object()
        events = mission.events.all()
        serializer = MissionEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a mission (marks as active, distinct from starting simulation).
        
        **Endpoint:** POST /api/v1/missions/{pk}/start/
        
        Changes mission status from 'planned' to 'active' and records the start time.
        Creates a 'mission_start' event in the timeline.
        
        **Note:** This is mission lifecycle management, not simulation control.
        Use `/start-sim/` to start the simulation itself.
        
        **Errors:**
        - 400 if mission is not in 'planned' status
        """
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
        """
        Complete a mission (marks as completed).
        
        **Endpoint:** POST /api/v1/missions/{pk}/complete/
        
        Changes mission status to 'completed' and records completion time.
        Creates a 'mission_end' event in the timeline.
        
        Use this when the mission has achieved its objectives or
        reached a natural conclusion.
        """
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
        
        **Endpoint:** GET /api/v1/missions/{pk}/state/
        
        **This is the most important endpoint in the entire API.**
        
        The frontend dashboard polls this endpoint every 2 seconds to get
        the complete mission state. The response drives all visualizations:
        - Tactical map (agent positions, sectors, network connections)
        - Telemetry panel (battery, signal, sensor status)
        - Timeline panel (events, detections)
        - Sensor outputs panel (thermal, audio, etc.)
        
        **Deterministic Calculation:**
        State is computed on-demand based on:
        1. Mission start time (simulation.started_at)
        2. Current wall-clock time
        3. Speed multiplier (1x, 2x, 5x, 10x)
        4. Use case type (determines scenario, agents, routes)
        5. Random seed (ensures reproducibility)
        
        No background processing. No WebSockets. No Celery.
        Same elapsed_seconds always returns same state.
        
        **Response Structure:**
        ```json
        {
          "mission_id": "mission-alpha-001",
          "mission_name": "Collapsed Building Search Alpha",
          "elapsed_seconds": 245.3,
          "status": "running",
          "agents": [...],
          "sensors": {...},
          "map_coverage": {...},
          "timeline_events": [...],
          "ai_analysis": {...}
        }
        ```
        
        **Performance:**
        - Cached scenario data (via @lru_cache)
        - Typical response time: 20-50ms
        - Supports multiple concurrent clients polling different missions
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
        
        # Calculate current state - this is where the magic happens
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
        Start or resume the mission simulation.
        
        **Endpoint:** POST /api/v1/missions/{pk}/start-sim/
        
        Changes simulation status to 'running' and records the start time.
        If the simulation was previously paused, it resumes from the accumulated
        elapsed time.
        
        **Behavior:**
        - First start: Sets started_at to current time, begins from 0 seconds
        - Resume from pause: Sets new started_at, continues from accumulated_elapsed_seconds
        - Already running: Returns error (idempotency check)
        
        **Response:**
        ```json
        {
          "status": "running",
          "message": "Simulation started",
          "elapsed_seconds": 0.0
        }
        ```
        
        **Errors:**
        - 400 if simulation is already running
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
        
        **Endpoint:** POST /api/v1/missions/{pk}/pause-sim/
        
        Freezes the simulation at its current elapsed time. The accumulated_elapsed_seconds
        field is updated to preserve the current mission time, so that when the simulation
        is resumed, it continues from exactly where it left off.
        
        **Use Cases:**
        - Operator needs to analyze current state without mission progressing
        - Demo/presentation pause for discussion
        - Waiting for additional agents to be added before continuing
        
        **Behavior:**
        1. Calculates current elapsed_seconds (including time since started_at)
        2. Stores in accumulated_elapsed_seconds (freezes the state)
        3. Sets status to 'paused'
        4. Records paused_at timestamp
        
        **Response:**
        ```json
        {
          "status": "paused",
          "message": "Simulation paused",
          "elapsed_seconds": 245.3
        }
        ```
        
        **Errors:**
        - 404 if no simulation exists
        - 400 if simulation is not running
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
        
        # Accumulate elapsed time before pausing - this is critical!
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
        
        **Endpoint:** POST /api/v1/missions/{pk}/reset-sim/
        
        Clears all simulation progress and returns to time zero. This allows
        the same mission to be replayed from the beginning.
        
        **Behavior:**
        1. Sets status to 'reset'
        2. Clears started_at, paused_at timestamps
        3. Resets accumulated_elapsed_seconds to 0.0
        4. Next call to /state/ will show mission at t=0
        
        **Use Cases:**
        - Replay mission scenario from the beginning
        - Demo/presentation restart
        - Testing reproducibility with same seed
        
        **Response:**
        ```json
        {
          "status": "reset",
          "message": "Simulation reset to initial state",
          "elapsed_seconds": 0.0
        }
        ```
        
        **Errors:**
        - 404 if no simulation exists
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
    
    @action(detail=True, methods=['get'], url_path='media')
    def get_media_artifacts(self, request, pk=None):
        """
        Get media artifacts for this mission's use case.
        
        **Endpoint:** GET /api/v1/missions/{pk}/media/
        
        Returns media artifacts (images, audio, point clouds) that are relevant
        to this mission's use case, optionally filtered by mission time.
        
        **Query Parameters:**
        - `max_time`: Maximum mission time in seconds (optional)
        - `min_time`: Minimum mission time in seconds (optional, default: 0)
        - `media_type`: Filter by media type (optional)
        - `sector_id`: Filter by sector (optional)
        - `linked_event`: Filter by linked event type (optional)
        
        **Response:**
        ```json
        {
          "media_artifacts": [
            {
              "id": "collapsed-thermal-void-heat-signature",
              "media_type": "thermal_image",
              "sensor_type": "thermal_camera",
              "title": "Thermal anomaly in Void Space 1",
              "description": "Thermal frame showing warm anomaly...",
              "media_url": "/media/collapsed-building/thermal-void-heat-signature.png",
              "thumbnail_url": "/media/collapsed-building/thermal-void-heat-signature-thumb.png",
              "sector_id": "void-space-1",
              "agent_id": "drone-b",
              "mission_time_seconds": 360,
              "mission_time_display": "06:00",
              "confidence": 0.78,
              "human_review_required": true,
              "annotation_tags": ["thermal anomaly", "review required"]
            }
          ],
          "count": 1
        }
        ```
        """
        from apps.missions.models_media import ScenarioMediaArtifact
        
        mission = self.get_object()
        
        # Start with all media for this use case
        media = ScenarioMediaArtifact.objects.filter(
            use_case_slug=mission.use_case_type
        )
        
        # Apply time filters
        max_time = request.query_params.get('max_time')
        if max_time is not None:
            media = media.filter(mission_time_seconds__lte=float(max_time))
        
        min_time = request.query_params.get('min_time', 0)
        if min_time:
            media = media.filter(mission_time_seconds__gte=float(min_time))
        
        # Apply optional filters
        media_type = request.query_params.get('media_type')
        if media_type:
            media = media.filter(media_type=media_type)
        
        sector_id = request.query_params.get('sector_id')
        if sector_id:
            media = media.filter(sector_id=sector_id)
        
        linked_event = request.query_params.get('linked_event')
        if linked_event:
            media = media.filter(linked_event_type=linked_event)
        
        # Convert to API format
        media_list = [artifact.to_api_dict() for artifact in media]
        
        return Response({
            'media_artifacts': media_list,
            'count': len(media_list)
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