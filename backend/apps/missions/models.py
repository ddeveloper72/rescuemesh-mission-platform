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
