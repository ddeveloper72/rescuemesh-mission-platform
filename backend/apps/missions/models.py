"""
Mission models for RescueMesh platform.
"""
from django.db import models
from django.utils import timezone
import uuid


class Mission(models.Model):
    """A mission represents a complete operational scenario."""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    mission_id = models.CharField(max_length=100, unique=True)
    
    # Use case relationship
    use_case_template = models.ForeignKey(
        'usecases.UseCaseTemplate',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='missions',
        help_text="Template this mission is based on"
    )
    # Legacy field - kept for backward compatibility
    use_case_type = models.CharField(max_length=100)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Mission parameters
    objective = models.TextField()
    terrain_description = models.TextField(blank=True)
    simulation_seed = models.IntegerField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.mission_id} - {self.name}"


class MissionEvent(models.Model):
    """
    A timestamped event that occurred during a mission.
    Events include state changes, detections, failures, and operator actions.
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
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Event details
    source_agent_id = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    # Structured data
    event_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['mission', 'timestamp']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self) -> str:
        return f"{self.mission.mission_id} - {self.event_type} at {self.timestamp}"


class MissionSimulation(models.Model):
    """
    Tracks the simulation state for a mission.
    
    This is a deterministic simulation calculated on request based on:
    - Mission start time
    - Speed multiplier
    - Use case type
    - Elapsed time
    
    No background tasks, Celery, Redis, or WebSockets required yet.
    State is computed on-demand in the simulation service.
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('reset', 'Reset'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.OneToOneField(
        Mission,
        on_delete=models.CASCADE,
        related_name='simulation',
        help_text="The mission this simulation is for"
    )
    
    # Simulation control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
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
        help_text="Seed for reproducible simulation randomness"
    )
    scenario_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Scenario-specific configuration and events"
    )
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Simulation for {self.mission.mission_id} ({self.status})"
    
    def get_elapsed_seconds(self) -> float:
        """
        Calculate total elapsed mission time in seconds.
        
        This accounts for:
        - Time accumulated before current session
        - Time elapsed in current session (if running)
        - Speed multiplier
        
        Returns simulated mission time, not real-world time.
        """
        if self.status == 'not_started' or self.status == 'reset':
            return 0.0
        
        elapsed = self.accumulated_elapsed_seconds
        
        if self.status == 'running' and self.started_at:
            from django.utils import timezone as tz
            real_time_delta = (tz.now() - self.started_at).total_seconds()
            elapsed += real_time_delta * self.speed_multiplier
        
        return elapsed
