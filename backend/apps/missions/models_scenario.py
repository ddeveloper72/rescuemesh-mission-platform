"""
Mission Scenario Models

Database-driven mission scripting system that defines:
- Pre-planned agent routes
- Timeline events (sector exploration, failures, detections)
- Failure scenarios
- Points of interest
- User interaction opportunities

This replaces hardcoded simulation logic with reusable, data-driven scenarios.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator


class MissionScenario(models.Model):
    """
    Reusable mission scenario template.
    
    Defines the mission script: agent routes, timeline events, failures, etc.
    Can be linked to multiple missions for replay/testing.
    """
    scenario_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    use_case = models.CharField(max_length=50, choices=[
        ('collapsed-building-search', 'Collapsed Building Search'),
        ('cave-rescue', 'Cave Rescue'),
        ('flooded-structure', 'Flooded Structure'),
        ('industrial-inspection', 'Industrial Inspection'),
        ('archaeological-exploration', 'Archaeological Exploration'),
    ])
    
    # Link to Digital Twin site/terrain
    digital_twin_site_slug = models.CharField(max_length=100, blank=True, null=True)
    digital_twin_terrain_slug = models.CharField(max_length=100, blank=True, null=True)
    
    # Mission parameters
    estimated_duration_seconds = models.IntegerField(default=600)
    origin_sector_id = models.CharField(max_length=100, help_text="Starting sector ID from Digital Twin")
    
    # User interaction settings
    allow_agent_deployment = models.BooleanField(default=False)
    allow_agent_redirect = models.BooleanField(default=False)
    allow_agent_recall = models.BooleanField(default=False)
    
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mission_scenarios'
        ordering = ['scenario_id']
    
    def __str__(self):
        return f"{self.name} ({self.scenario_id})"


class AgentRoute(models.Model):
    """
    Pre-planned route for an agent within a scenario.
    
    Defines the agent's path through the terrain using waypoints.
    """
    scenario = models.ForeignKey(MissionScenario, on_delete=models.CASCADE, related_name='agent_routes')
    agent_id = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    agent_role = models.CharField(max_length=100, choices=[
        ('mapper', 'Mapper'),
        ('detector', 'Detector'),
        ('relay', 'Relay'),
        ('specialist', 'Specialist'),
    ])
    
    # Timing
    deploy_at_seconds = models.FloatField(default=0, validators=[MinValueValidator(0)])
    
    # Agent specs
    sensors = models.JSONField(default=list, help_text="List of sensor types")
    average_speed_m_per_s = models.FloatField(default=2.0)
    battery_drain_rate_percent_per_second = models.FloatField(default=0.05)
    
    # Route behavior
    behavior = models.CharField(max_length=50, choices=[
        ('patrol', 'Patrol waypoints in sequence'),
        ('static', 'Deploy and remain stationary'),
        ('return-to-base', 'Return to origin after completing route'),
        ('one-way', 'Continue until battery depleted'),
    ], default='patrol')
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'agent_routes'
        ordering = ['scenario', 'deploy_at_seconds', 'agent_id']
        unique_together = [['scenario', 'agent_id']]
    
    def __str__(self):
        return f"{self.agent_name} ({self.scenario.name})"


class RouteWaypoint(models.Model):
    """
    Waypoint along an agent's route.
    
    References a sector from the Digital Twin terrain.
    """
    route = models.ForeignKey(AgentRoute, on_delete=models.CASCADE, related_name='waypoints')
    sequence_order = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Reference to Digital Twin sector
    sector_id = models.CharField(max_length=100, help_text="Sector ID from Digital Twin")
    
    # Optional: specific position within sector (if not using sector centroid)
    override_x_m = models.FloatField(blank=True, null=True)
    override_y_m = models.FloatField(blank=True, null=True)
    override_z_m = models.FloatField(blank=True, null=True)
    
    # Actions at this waypoint
    pause_duration_seconds = models.FloatField(default=0, validators=[MinValueValidator(0)])
    action = models.CharField(max_length=50, choices=[
        ('explore', 'Explore sector'),
        ('scan', 'Detailed scan'),
        ('deploy-relay', 'Become relay node'),
        ('wait', 'Wait for other agents'),
        ('checkpoint', 'Continue immediately'),
    ], default='explore')
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'route_waypoints'
        ordering = ['route', 'sequence_order']
        unique_together = [['route', 'sequence_order']]
    
    def __str__(self):
        return f"{self.route.agent_name} waypoint {self.sequence_order}: {self.sector_id}"


class ScenarioEvent(models.Model):
    """
    Timeline event within a mission scenario.
    
    Events include: sector exploration, detections, failures, escalations, etc.
    """
    scenario = models.ForeignKey(MissionScenario, on_delete=models.CASCADE, related_name='events')
    
    # Timing
    trigger_at_seconds = models.FloatField(validators=[MinValueValidator(0)])
    
    # Event type and data
    event_type = models.CharField(max_length=50, choices=[
        ('sector-explored', 'Sector exploration complete'),
        ('detection-thermal', 'Thermal detection'),
        ('detection-audio', 'Audio detection'),
        ('detection-signal', 'Signal detection'),
        ('failure-battery', 'Battery failure'),
        ('failure-sensor', 'Sensor failure'),
        ('failure-communications', 'Communications failure'),
        ('agent-landed-relay', 'Agent becomes relay'),
        ('agent-sacrificed', 'Agent sacrificed'),
        ('escalation', 'Mission escalation'),
        ('user-prompt', 'Prompt user for action'),
    ])
    
    # Related entities
    agent_id = models.CharField(max_length=100, blank=True, null=True)
    sector_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Event details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=[
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('success', 'Success'),
    ], default='info')
    
    # Event-specific data
    event_data = models.JSONField(default=dict, help_text="Event-specific parameters")
    
    # User interaction
    requires_user_action = models.BooleanField(default=False)
    user_action_type = models.CharField(max_length=50, blank=True, choices=[
        ('acknowledge', 'Acknowledge'),
        ('deploy-agent', 'Deploy new agent'),
        ('redirect-agent', 'Redirect agent'),
        ('abort-mission', 'Abort mission'),
        ('custom', 'Custom action'),
    ])
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'scenario_events'
        ordering = ['scenario', 'trigger_at_seconds']
    
    def __str__(self):
        return f"{self.scenario.name} @ {self.trigger_at_seconds}s: {self.title}"


class UserMissionAction(models.Model):
    """
    User actions during a live mission.
    
    Records user decisions and overrides to the pre-planned scenario.
    """
    mission_id = models.CharField(max_length=100, db_index=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    mission_time_seconds = models.FloatField(help_text="Mission elapsed time when action was taken")
    
    # Action details
    action_type = models.CharField(max_length=50, choices=[
        ('deploy-agent', 'Deploy new agent'),
        ('redirect-agent', 'Redirect agent to new location'),
        ('recall-agent', 'Recall agent to base'),
        ('abort-mission', 'Abort mission'),
        ('acknowledge-event', 'Acknowledge event'),
        ('manual-control', 'Manual control override'),
    ])
    
    # Related entities
    agent_id = models.CharField(max_length=100, blank=True, null=True)
    target_sector_id = models.CharField(max_length=100, blank=True, null=True)
    target_x_m = models.FloatField(blank=True, null=True)
    target_y_m = models.FloatField(blank=True, null=True)
    target_z_m = models.FloatField(blank=True, null=True)
    
    # Action parameters
    action_data = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('executed', 'Executed'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_mission_actions'
        ordering = ['mission_id', 'created_at']
    
    def __str__(self):
        return f"{self.mission_id}: {self.action_type} @ {self.mission_time_seconds}s"
