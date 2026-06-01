"""
Mission models for RescueMesh platform.

This module defines the core domain models for mission management,
events tracking, and simulation state.

Core Concepts:
--------------
- **Mission**: A complete operational scenario with lifecycle (planned → active → completed)
- **MissionEvent**: Timestamped events that occur during mission execution
- **MissionSimulation**: Tracks deterministic simulation state calculated on-demand

The simulation is NOT real-time background processing - it's calculated per API request
based on elapsed time, speed multiplier, and use case type. No Celery/Redis required yet.
"""
from django.db import models
from django.utils import timezone
import uuid


class Mission(models.Model):
    """
    A mission represents a complete operational scenario in dangerous terrain.
    
    Missions are simulation-first: they demonstrate how autonomous agents (drones,
    relays, sensors) cooperate to map unknown terrain, search for objectives,
    and maintain communications in GPS-denied environments.
    
    **Lifecycle States:**
    - `planned`: Mission created but not yet started
    - `active`: Mission currently executing
    - `paused`: Mission temporarily halted
    - `completed`: Mission successfully finished
    - `aborted`: Mission terminated early due to failure or operator decision
    
    **Use Case Templates:**
    Missions are based on use case templates that define terrain type, objectives,
    recommended agents, sensors, and expected hazards. Templates ensure consistency
    and enable comparison between similar missions.
    
    **Attributes:**
    - id: UUID primary key for secure identification
    - mission_id: Human-readable unique identifier (e.g., "mission-alpha-001")
    - name: Descriptive mission name
    - use_case_template: FK to UseCaseTemplate (preferred)
    - use_case_type: Legacy string field (backward compatibility)
    - status: Current mission lifecycle state
    - objective: Mission goal description
    - terrain_description: Environment characteristics
    - simulation_seed: Deterministic random seed for reproducible scenarios
    - metadata: Flexible JSON storage for mission-specific data
    """
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique mission identifier (UUID)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Human-readable mission name"
    )
    mission_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique mission identifier string (e.g., 'mission-alpha-001')"
    )
    
    # Use case relationship
    use_case_template = models.ForeignKey(
        'usecases.UseCaseTemplate',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='missions',
        help_text="Template this mission is based on (preferred over use_case_type)"
    )
    # Legacy field - kept for backward compatibility
    use_case_type = models.CharField(
        max_length=100,
        help_text="Legacy use case type string (use use_case_template instead)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        help_text="Current mission lifecycle state"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the mission was created"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the mission was started (status changed to 'active')"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the mission was completed or aborted"
    )
    
    # Mission parameters
    objective = models.TextField(
        help_text="Mission goal and success criteria"
    )
    terrain_description = models.TextField(
        blank=True,
        help_text="Environment characteristics (e.g., 'collapsed building', 'flooded tunnel')"
    )
    simulation_seed = models.IntegerField(
        null=True,
        blank=True,
        help_text="Random seed for deterministic simulation reproducibility"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible JSON storage for mission-specific configuration"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest missions first
    
    def __str__(self) -> str:
        """String representation for admin and debugging."""
        return f"{self.mission_id} - {self.name}"


class MissionEvent(models.Model):
    """
    A timestamped event that occurred during a mission.
    
    Events form the mission timeline and provide an audit trail of all significant
    occurrences: agent deployments, state changes, sensor detections, hardware failures,
    AI analysis results, and operator decisions.
    
    **Event Types:**
    - `mission_start`: Mission begins execution
    - `mission_end`: Mission completes or aborts
    - `agent_deployed`: New agent enters the field
    - `agent_state_change`: Agent transitions between states (active → failed, etc.)
    - `detection`: Sensor detects potential objective (thermal, audio, gas, etc.)
    - `failure`: Hardware degradation or complete failure
    - `telemetry`: Periodic status update from agent
    - `ai_analysis`: AI system generates analysis or recommendation
    - `operator_decision`: Human operator makes a decision
    
    **Confidence Scoring:**
    Events include an optional confidence value (0.0-1.0) indicating certainty.
    Low-confidence events (< 0.7) typically require human review.
    
    **Structured Data:**
    The `event_data` JSON field stores event-specific structured information:
    - Agent state changes: previous_state, new_state, reason
    - Detections: detection_type, location, sensor_id, metadata
    - Failures: affected_component, severity, recovery_possible
    - AI analysis: recommendations, confidence_breakdown, reasoning
    
    **Attributes:**
    - id: UUID primary key
    - mission: FK to parent Mission
    - event_type: Categorizes the event
    - timestamp: When the event occurred (mission elapsed time, not wall clock)
    - source_agent_id: Which agent generated this event (if applicable)
    - title: Short event description (shown in timeline)
    - description: Detailed event explanation
    - confidence: Optional 0.0-1.0 confidence score
    - event_data: Structured JSON data specific to event type
    """
    
    EVENT_TYPES = [
        ('mission_start', 'Mission Start'),
        ('mission_end', 'Mission End'),
        ('agent_deployed', 'Agent Deployed'),
        ('agent_state_change', 'Agent State Change'),
        ('detection', 'Detection'),
        ('failure', 'Failure'),
        ('telemetry', 'Telemetry Update'),
        ('ai_analysis', 'AI Analysis'),
        ('operator_decision', 'Operator Decision'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique event identifier"
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="Parent mission this event belongs to"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        help_text="Event category"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the event occurred (real-world time, not mission elapsed time)"
    )
    
    # Event details
    source_agent_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Agent ID that generated this event (if applicable)"
    )
    title = models.CharField(
        max_length=200,
        help_text="Short event title for timeline display"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed event explanation"
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional confidence score (0.0-1.0) for uncertain events"
    )
    
    # Structured data
    event_data = models.JSONField(
        default=dict,
        help_text="Event-specific structured data (varies by event_type)"
    )
    
    class Meta:
        ordering = ['timestamp']  # Chronological order
        indexes = [
            models.Index(fields=['mission', 'timestamp']),  # Fast mission timeline queries
            models.Index(fields=['event_type']),  # Fast event type filtering
        ]
    
    def __str__(self) -> str:
        """String representation for admin and debugging."""
        return f"{self.mission.mission_id} - {self.event_type} at {self.timestamp}"


class MissionSimulation(models.Model):
    """
    Tracks the simulation state for a mission.
    
    **IMPORTANT: This is NOT background processing or real-time simulation.**
    
    The simulation is **deterministic and calculated on-demand** per API request.
    State computation is based on:
    - Mission start time (when simulation.started_at was set)
    - Current wall-clock time (determines elapsed seconds)
    - Speed multiplier (1x, 2x, 5x, 10x real-time acceleration)
    - Use case type (determines agent routes, events, terrain)
    - Random seed (ensures reproducibility)
    
    **No WebSockets. No Celery. No Redis. No background tasks.**
    
    When the frontend polls `/api/v1/missions/{pk}/state/`, the backend:
    1. Reads the MissionSimulation record
    2. Calculates elapsed_seconds from started_at and speed_multiplier
    3. Passes elapsed_seconds to the scenario engine
    4. Returns complete dashboard state (agents, sensors, map, events)
    
    This approach is:
    - Simple to implement and debug
    - Scales well for demonstration purposes
    - Reproducible (same elapsed time = same state)
    - No coordination required between multiple processes
    
    **Future Evolution:**
    When real-time sensor feeds and hardware integration are added,
    this model will be extended with WebSocket session IDs, Celery
    task tracking, and real-time event buffering.
    
    **Lifecycle:**
    - `not_started`: Simulation created but not yet started
    - `running`: Simulation actively progressing
    - `paused`: Simulation temporarily halted (preserves accumulated_elapsed_seconds)
    - `completed`: Simulation reached end condition
    - `reset`: Simulation reset to initial state
    
    **Speed Control:**
    Speed multiplier affects how fast mission time progresses:
    - 1.0 = real-time (1 second elapsed = 1 second mission time)
    - 2.0 = 2x speed (1 second elapsed = 2 seconds mission time)
    - 10.0 = 10x speed (1 second elapsed = 10 seconds mission time)
    
    **Attributes:**
    - id: UUID primary key
    - mission: OneToOne relationship to Mission
    - status: Simulation lifecycle state
    - speed_multiplier: Time acceleration factor
    - started_at: Real-world time when simulation started
    - paused_at: Real-world time when simulation was paused
    - accumulated_elapsed_seconds: Total mission time accumulated before pause
    - random_seed: Deterministic random seed (inherited from mission or generated)
    - metadata: Flexible JSON storage for simulation-specific data
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('reset', 'Reset'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique simulation identifier"
    )
    mission = models.OneToOneField(
        Mission,
        on_delete=models.CASCADE,
        related_name='simulation',
        help_text="The mission this simulation is for"
    )
    
    # Simulation control
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        help_text="Current simulation state"
    )
    speed_multiplier = models.FloatField(
        default=1.0,
        help_text="Simulation speed: 1x, 2x, 5x, 10x real-time"
    )
    
    # Time tracking
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Real-world time when simulation started"
    )
    paused_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Real-world time when simulation was paused"
    )
    accumulated_elapsed_seconds = models.FloatField(
        default=0.0,
        help_text="Total simulated mission time accumulated before current run/pause"
    )
    
    # Simulation parameters
    random_seed = models.IntegerField(
        null=True,
        blank=True,
        help_text="Seed for reproducible simulation randomness (inherited from mission.simulation_seed)"
    )
    scenario_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Scenario-specific configuration and events (use case customization)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this simulation record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this simulation record was last modified"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest simulations first
        verbose_name = "Mission Simulation"
        verbose_name_plural = "Mission Simulations"
    
    def __str__(self) -> str:
        """String representation for admin and debugging."""
        return f"Simulation for {self.mission.mission_id} ({self.status})"
    
    def get_elapsed_seconds(self) -> float:
        """
        Calculate total elapsed mission time in seconds.
        
        This is the core calculation that drives simulation state computation.
        It combines accumulated time from previous sessions with current session time,
        applying the speed multiplier to real-world elapsed time.
        
        **Calculation Logic:**
        - If not_started or reset: return 0.0
        - If paused or completed: return accumulated_elapsed_seconds (frozen state)
        - If running: accumulated_elapsed_seconds + (real_time_since_start * speed_multiplier)
        
        **Example:**
        - Simulation runs for 100 real seconds at 2x speed: 200 elapsed mission seconds
        - Then paused with accumulated_elapsed_seconds = 200
        - Then resumed and runs for 50 more real seconds at 5x speed: 200 + (50 * 5) = 450 elapsed seconds
        
        Returns:
            float: Total simulated mission elapsed time in seconds
        """
        if self.status == 'not_started' or self.status == 'reset':
            return 0.0
        
        elapsed = self.accumulated_elapsed_seconds
        
        if self.status == 'running' and self.started_at:
            from django.utils import timezone as tz
            real_time_delta = (tz.now() - self.started_at).total_seconds()
            elapsed += real_time_delta * self.speed_multiplier
        
        return elapsed


# Import scenario models to register them with Django
from .models_scenario import (  # noqa: F401, E402
    MissionScenario,
    AgentRoute,
    RouteWaypoint,
    ScenarioEvent,
    UserMissionAction,
)

# Import media models to register them with Django
from .models_media import (  # noqa: F401, E402
    ScenarioMediaArtifact,
)
