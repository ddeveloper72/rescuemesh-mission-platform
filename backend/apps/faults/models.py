"""
Failure profile models for RescueMesh platform.

These models define failure scenarios that can occur during mission simulations,
including hardware degradation, sensor failures, and communication issues.
"""
from django.db import models
from django.utils import timezone
import uuid


class FailureProfile(models.Model):
    """
    Template for a failure scenario within a use case.
    Defines what can go wrong and how it affects the simulation.
    """
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    TRIGGER_TYPE_CHOICES = [
        ('time_based', 'Time Based'),
        ('event_based', 'Event Based'),
        ('sector_based', 'Sector Based'),
        ('battery_threshold', 'Battery Threshold'),
        ('random_seeded', 'Random Seeded'),
        ('operator_triggered', 'Operator Triggered'),
        ('scripted_demo', 'Scripted Demo'),
    ]
    
    COMPONENT_TYPE_CHOICES = [
        ('battery', 'Battery'),
        ('motor', 'Motor'),
        ('lidar', 'LiDAR'),
        ('camera', 'Camera'),
        ('thermal_sensor', 'Thermal Sensor'),
        ('microphone', 'Microphone'),
        ('radio', 'Radio'),
        ('gps', 'GPS'),
        ('imu', 'IMU'),
        ('slam_system', 'SLAM System'),
        ('storage', 'Storage'),
        ('propulsion', 'Propulsion'),
        ('general', 'General System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_case = models.ForeignKey(
        'usecases.UseCaseTemplate',
        on_delete=models.CASCADE,
        related_name='failure_profiles'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    affected_component = models.CharField(max_length=100, choices=COMPONENT_TYPE_CHOICES)
    severity = models.CharField(max_length=50, choices=SEVERITY_CHOICES)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPE_CHOICES)
    
    # Trigger conditions
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="Conditions that cause this failure: time, sector, battery_level, etc."
    )
    
    # Effects on simulation
    effects = models.JSONField(
        default=dict,
        help_text="Effects: map_confidence_drop, sensor_noise_multiplier, speed_reduction, etc."
    )
    
    # Dashboard messaging
    operator_message = models.TextField(
        help_text="Message shown to operator when this failure occurs"
    )
    
    # Recovery options
    is_recoverable = models.BooleanField(default=False)
    recovery_actions = models.JSONField(
        default=list,
        help_text="Possible recovery actions"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['use_case', 'severity', 'name']
        verbose_name = 'Failure Profile'
        verbose_name_plural = 'Failure Profiles'
    
    def __str__(self) -> str:
        return f"{self.name} - {self.severity} ({self.use_case.slug})"
