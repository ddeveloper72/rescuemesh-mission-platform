"""
Media artifact metadata models for mission scenarios.

Supports static demo media, generated media, and future real operational media.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ScenarioMediaArtifact(models.Model):
    """
    Media artifact metadata for mission scenarios.
    
    Links media files (images, audio, video, point clouds) to specific
    mission events, sectors, agents, and timestamps.
    
    Supports:
    - Static demo assets (stored in frontend/public/media/)
    - Generated/synthetic media (Python-generated)
    - Future real operational media (object storage URLs)
    """
    
    # Media type choices
    MEDIA_TYPE_CHOICES = [
        ('rgb_image', 'RGB Image'),
        ('low_light_image', 'Low-Light Image'),
        ('infrared_image', 'Infrared Image'),
        ('thermal_image', 'Thermal Image'),
        ('lidar_preview', 'LiDAR Preview'),
        ('point_cloud_preview', 'Point Cloud Preview'),
        ('spectrogram', 'Spectrogram'),
        ('audio_clip', 'Audio Clip'),
        ('video_placeholder', 'Video Placeholder'),
    ]
    
    # Sensor type choices
    SENSOR_TYPE_CHOICES = [
        ('rgb_camera', 'RGB Camera'),
        ('low_light_camera', 'Low-Light Camera'),
        ('infrared_camera', 'Infrared Camera'),
        ('thermal_camera', 'Thermal Camera'),
        ('lidar', 'LiDAR'),
        ('audio_sensor', 'Audio Sensor'),
        ('seismic_sensor', 'Seismic Sensor'),
        ('hydrophone', 'Hydrophone'),
        ('inspection_camera', 'Inspection Camera'),
    ]
    
    # Lighting state choices
    LIGHTING_STATE_CHOICES = [
        ('natural', 'Natural Light'),
        ('low_light', 'Low Light'),
        ('spotlight', 'Spotlight Active'),
        ('ir_illuminator', 'IR Illuminator Active'),
        ('thermal_mode', 'Thermal Mode'),
        ('complete_darkness', 'Complete Darkness'),
    ]
    
    # Visibility condition choices
    VISIBILITY_CONDITION_CHOICES = [
        ('clear', 'Clear'),
        ('dust', 'Dust/Particulate'),
        ('smoke', 'Smoke'),
        ('water', 'Water/Moisture'),
        ('darkness', 'Darkness'),
        ('obscured', 'Obscured'),
        ('degraded', 'Degraded'),
    ]
    
    # Primary identifiers
    slug = models.SlugField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Stable slug for lookups (e.g., collapsed-thermal-void-heat-signature)'
    )
    
    # Scenario/mission context
    use_case_slug = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Use case this media belongs to (e.g., collapsed-building-search)'
    )
    mission_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text='Optional mission ID if media is mission-specific'
    )
    site_slug = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional digital twin site slug'
    )
    terrain_map_slug = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional terrain map slug'
    )
    
    # Location context
    sector_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        help_text='Sector ID where media was captured'
    )
    waypoint_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional waypoint ID'
    )
    
    # Agent context
    agent_role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Agent role (e.g., mapper, detector, relay)'
    )
    agent_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        help_text='Specific agent ID (e.g., drone-a)'
    )
    
    # Media classification
    media_type = models.CharField(
        max_length=30,
        choices=MEDIA_TYPE_CHOICES,
        db_index=True,
        help_text='Type of media artifact'
    )
    sensor_type = models.CharField(
        max_length=30,
        choices=SENSOR_TYPE_CHOICES,
        help_text='Sensor that captured this media'
    )
    
    # File paths
    file_path = models.CharField(
        max_length=500,
        help_text='Relative path to media file (e.g., /media/collapsed-building/thermal-void-heat-signature.png)'
    )
    thumbnail_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Optional thumbnail path'
    )
    
    # Metadata
    title = models.CharField(
        max_length=200,
        help_text='Human-readable title'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of what the media shows'
    )
    
    # Timing
    mission_time_seconds = models.FloatField(
        validators=[MinValueValidator(0)],
        db_index=True,
        help_text='Mission elapsed time when media was captured'
    )
    display_after_event = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional event slug to trigger display'
    )
    linked_event_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        help_text='Event type this media is linked to (e.g., thermal_detection)'
    )
    
    # Quality metrics
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.75,
        help_text='Confidence score (0.0-1.0)'
    )
    signal_quality = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text='Signal quality score (0.0-1.0)'
    )
    
    # Review flags
    human_review_required = models.BooleanField(
        default=False,
        help_text='Whether this media requires human review'
    )
    
    # Environmental context
    lighting_state = models.CharField(
        max_length=30,
        choices=LIGHTING_STATE_CHOICES,
        blank=True,
        null=True,
        help_text='Lighting condition when captured'
    )
    visibility_condition = models.CharField(
        max_length=30,
        choices=VISIBILITY_CONDITION_CHOICES,
        blank=True,
        null=True,
        help_text='Visibility condition'
    )
    
    # JSON fields for flexible metadata
    hazard_tags = models.JSONField(
        default=list,
        blank=True,
        help_text='List of hazard tags (e.g., ["unstable_structure", "sharp_debris"])'
    )
    annotation_tags = models.JSONField(
        default=list,
        blank=True,
        help_text='List of annotation tags (e.g., ["thermal anomaly", "review required"])'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional flexible metadata as JSON'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scenario_media_artifact'
        ordering = ['use_case_slug', 'mission_time_seconds', 'created_at']
        indexes = [
            models.Index(fields=['use_case_slug', 'mission_time_seconds']),
            models.Index(fields=['sector_id', 'mission_time_seconds']),
            models.Index(fields=['agent_id', 'mission_time_seconds']),
            models.Index(fields=['linked_event_type', 'mission_time_seconds']),
        ]
        verbose_name = 'Scenario Media Artifact'
        verbose_name_plural = 'Scenario Media Artifacts'
    
    def __str__(self):
        return f"{self.slug} ({self.media_type} at {self.mission_time_seconds}s)"
    
    def get_display_time(self):
        """Return formatted mission time as MM:SS."""
        minutes = int(self.mission_time_seconds // 60)
        seconds = int(self.mission_time_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def to_api_dict(self):
        """Convert to API response dictionary."""
        return {
            'id': self.slug,
            'media_type': self.media_type,
            'sensor_type': self.sensor_type,
            'title': self.title,
            'description': self.description,
            'media_url': self.file_path,
            'thumbnail_url': self.thumbnail_path,
            'sector_id': self.sector_id,
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'mission_time_seconds': self.mission_time_seconds,
            'mission_time_display': self.get_display_time(),
            'linked_event_type': self.linked_event_type,
            'confidence': self.confidence,
            'signal_quality': self.signal_quality,
            'human_review_required': self.human_review_required,
            'lighting_state': self.lighting_state,
            'visibility_condition': self.visibility_condition,
            'hazard_tags': self.hazard_tags,
            'annotation_tags': self.annotation_tags,
            'metadata': self.metadata,
        }
