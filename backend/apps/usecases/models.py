"""
Use case template models for RescueMesh platform.

These models define reusable mission scenario templates that can be instantiated
into actual mission runs. Each use case (collapsed building, cave rescue, etc.)
is defined here with its terrain, agents, sensors, and failure profiles.
"""
from django.db import models
from django.utils import timezone
import uuid


class UseCaseTemplate(models.Model):
    """
    A reusable mission scenario template.
    Examples: collapsed-building-search, cave-rescue, flooded-structure, industrial-inspection
    """
    
    PRIORITY_CHOICES = [
        ('life_safety', 'Life Safety'),
        ('navigation_safety', 'Navigation Safety'),
        ('infrastructure_safety', 'Infrastructure Safety'),
        ('operational_efficiency', 'Operational Efficiency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    summary = models.TextField()
    objective = models.TextField()
    
    # Status
    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['slug']
        verbose_name = 'Use Case Template'
        verbose_name_plural = 'Use Case Templates'
    
    def __str__(self) -> str:
        return f"{self.title} ({self.slug})"


class TerrainProfile(models.Model):
    """
    Terrain characteristics for a use case that affect simulation behavior.
    """
    
    GPS_STATUS_CHOICES = [
        ('denied', 'GPS Denied'),
        ('degraded', 'GPS Degraded'),
        ('intermittent', 'GPS Intermittent'),
        ('available', 'GPS Available'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_case = models.OneToOneField(
        UseCaseTemplate,
        on_delete=models.CASCADE,
        related_name='terrain'
    )
    
    terrain_type = models.CharField(max_length=200)
    gps_status = models.CharField(max_length=50, choices=GPS_STATUS_CHOICES)
    communication_conditions = models.TextField()
    lighting_conditions = models.TextField()
    
    # Environmental factors
    hazards = models.JSONField(default=list, help_text="List of environmental hazards")
    accessibility = models.TextField(blank=True)
    
    # Simulation parameters
    simulation_complexity = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('extreme', 'Extreme')],
        default='medium'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Terrain Profile'
        verbose_name_plural = 'Terrain Profiles'
    
    def __str__(self) -> str:
        return f"Terrain: {self.use_case.title}"


class AgentRoleTemplate(models.Model):
    """
    Template for an agent role within a use case.
    Defines what types of agents (Scout Drone, Relay Drone, etc.) are recommended.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    use_case = models.ForeignKey(
        UseCaseTemplate,
        on_delete=models.CASCADE,
        related_name='agent_roles'
    )
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="Primary role: scout, relay, mapper, etc.")
    description = models.TextField()
    default_quantity = models.PositiveIntegerField(default=1)
    
    # Agent specifications
    agent_type = models.CharField(
        max_length=50,
        choices=[
            ('drone', 'Drone'),
            ('ground_robot', 'Ground Robot'),
            ('amphibious_robot', 'Amphibious Robot'),
            ('relay_node', 'Relay Node'),
            ('sensor', 'Passive Sensor'),
        ]
    )
    
    capabilities = models.JSONField(
        default=list,
        help_text="List of capabilities: mapping, relay, thermal_sensing, etc."
    )
    
    specifications = models.JSONField(
        default=dict,
        help_text="Hardware specs: battery_capacity, max_speed, sensor_range, etc."
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['use_case', 'name']
        verbose_name = 'Agent Role Template'
        verbose_name_plural = 'Agent Role Templates'
    
    def __str__(self) -> str:
        return f"{self.name} ({self.use_case.slug})"
