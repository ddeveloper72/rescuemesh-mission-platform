"""
AI prompt template models for RescueMesh platform.

These models define AI prompt templates for different analytical roles
in mission simulations.
"""
from django.db import models
from django.utils import timezone
import uuid


class AIPromptTemplate(models.Model):
    """
    Template for AI prompts used in mission analysis.
    Defines prompts for different AI roles: sensor analyst, mission planner, etc.
    """
    
    AI_ROLE_CHOICES = [
        ('mission_planner', 'Mission Planner'),
        ('sensor_analyst', 'Sensor Analyst'),
        ('map_analyst', 'Map Analyst'),
        ('audio_analyst', 'Audio Analyst'),
        ('thermal_analyst', 'Thermal Analyst'),
        ('operator_assistant', 'Operator Assistant'),
        ('report_writer', 'Report Writer'),
        ('risk_assessor', 'Risk Assessor'),
        ('route_planner', 'Route Planner'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_case = models.ForeignKey(
        'usecases.UseCaseTemplate',
        on_delete=models.CASCADE,
        related_name='ai_prompts'
    )
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=AI_ROLE_CHOICES)
    description = models.TextField(blank=True)
    
    # Prompt content
    prompt_text = models.TextField(
        help_text="The actual prompt text with placeholders for dynamic data"
    )
    
    system_prompt = models.TextField(
        blank=True,
        help_text="System-level instructions for the AI"
    )
    
    # Input/Output configuration
    input_types = models.JSONField(
        default=list,
        help_text="List of input types: thermal_frames, audio_segments, map_data, etc."
    )
    
    output_schema = models.JSONField(
        default=dict,
        help_text="Expected structure of AI response"
    )
    
    # Prompt parameters
    temperature = models.FloatField(
        default=0.7,
        help_text="AI temperature setting (0.0-1.0)"
    )
    
    max_tokens = models.IntegerField(
        default=1000,
        help_text="Maximum tokens for AI response"
    )
    
    # Configuration
    requires_human_review = models.BooleanField(
        default=True,
        help_text="Whether AI output requires human review"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['use_case', 'role', 'name']
        verbose_name = 'AI Prompt Template'
        verbose_name_plural = 'AI Prompt Templates'
    
    def __str__(self) -> str:
        return f"{self.name} - {self.role} ({self.use_case.slug})"
