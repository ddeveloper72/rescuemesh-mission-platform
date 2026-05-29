"""
Mapping and expected output models for RescueMesh platform.

These models define the expected outputs from missions, such as maps,
detection events, and analysis results.
"""
from django.db import models
from django.utils import timezone
import uuid


class ExpectedOutputTemplate(models.Model):
    """
    Template for an expected output from a use case mission.
    Examples: 3D Void Map, Thermal Anomalies, Audio Events, Relay Map
    """
    
    OUTPUT_TYPE_CHOICES = [
        ('3d_map', '3D Map'),
        ('thermal', 'Thermal Analysis'),
        ('audio', 'Audio Analysis'),
        ('environmental', 'Environmental Data'),
        ('device_scan', 'Device Scan Results'),
        ('relay_map', 'Relay Network Map'),
        ('route_map', 'Route Map'),
        ('ai_analysis', 'AI Analysis'),
        ('report', 'Mission Report'),
        ('detection_list', 'Detection List'),
        ('hazard_map', 'Hazard Map'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_case = models.ForeignKey(
        'usecases.UseCaseTemplate',
        on_delete=models.CASCADE,
        related_name='expected_outputs'
    )
    
    name = models.CharField(max_length=100)
    output_type = models.CharField(max_length=50, choices=OUTPUT_TYPE_CHOICES)
    description = models.TextField()
    
    # Output requirements
    confidence_required = models.BooleanField(
        default=True,
        help_text="Whether this output requires confidence scoring"
    )
    
    human_review_required = models.BooleanField(
        default=False,
        help_text="Whether this output requires human review before action"
    )
    
    # Display configuration
    display_priority = models.IntegerField(
        default=0,
        help_text="Display order on dashboard (higher = more important)"
    )
    
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon identifier for UI display"
    )
    
    # Output schema
    output_schema = models.JSONField(
        default=dict,
        help_text="Expected structure of this output type"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['use_case', '-display_priority', 'name']
        verbose_name = 'Expected Output Template'
        verbose_name_plural = 'Expected Output Templates'
    
    def __str__(self) -> str:
        return f"{self.name} ({self.use_case.slug})"
