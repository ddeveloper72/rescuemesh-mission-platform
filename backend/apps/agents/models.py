"""
Agent models.
"""
from django.db import models
import uuid


class Agent(models.Model):
    """
    An agent is any autonomous or semi-autonomous entity in a mission.
    Can be a drone, ground robot, relay node, sensor, or AI service.
    """
    
    AGENT_TYPES = [
        ('drone', 'Drone'),
        ('ground_robot', 'Ground Robot'),
        ('amphibious_robot', 'Amphibious Robot'),
        ('relay_node', 'Relay Node'),
        ('sensor', 'Passive Sensor'),
        ('base_station', 'Base Station'),
        ('ai_analyst', 'AI Analyst Service'),
    ]
    
    STATE_CHOICES = [
        ('planned', 'Planned'),
        ('available', 'Available'),
        ('deployed', 'Deployed'),
        ('active', 'Active'),
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('intermittent', 'Intermittent'),
        ('failed', 'Failed'),
        ('failed_primary_power', 'Failed - Primary Power'),
        ('landed', 'Landed'),
        ('landed_relay', 'Landed as Relay'),
        ('abandoned', 'Abandoned'),
        ('sacrificed', 'Sacrificed'),
        ('lost', 'Lost'),
        ('unknown', 'Unknown'),
        ('recoverable', 'Recoverable'),
        ('recovered', 'Recovered'),
        ('nfc_readable', 'NFC Readable'),
        ('retired', 'Retired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPES)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default='available')
    
    # Current mission assignment
    current_mission = models.ForeignKey(
        'missions.Mission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agents'
    )
    
    # Specifications
    specifications = models.JSONField(default=dict)
    
    # Current status
    battery_level = models.IntegerField(null=True, blank=True)
    location = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['agent_id']
    
    def __str__(self) -> str:
        return f"{self.agent_id} - {self.name}"


class AgentStateChange(models.Model):
    """Track state changes for agents during missions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='state_changes')
    mission = models.ForeignKey('missions.Mission', on_delete=models.CASCADE, related_name='agent_state_changes')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_state = models.CharField(max_length=50)
    new_state = models.CharField(max_length=50)
    reason = models.TextField()
    confidence = models.FloatField(null=True, blank=True)
    
    location = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.agent.agent_id}: {self.previous_state} → {self.new_state}"
