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


class DigitalTwinSite(models.Model):
    """
    Digital twin site representing a real-world environment imported for
    simulation and demo purposes. Sources may include cave surveys,
    archaeological sites, industrial facilities, or synthetic environments.
    """
    
    SITE_TYPE_CHOICES = [
        ('cave', 'Cave System'),
        ('archaeology', 'Archaeological Site'),
        ('industrial', 'Industrial Facility'),
        ('synthetic', 'Synthetic Environment'),
    ]
    
    SENSITIVITY_LEVEL_CHOICES = [
        ('public_demo', 'Public Demo - Full coordinates'),
        ('reduced_precision', 'Reduced Precision - Approximate location'),
        ('restricted', 'Restricted - No location data'),
        ('synthetic_only', 'Synthetic Only - Not a real location'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    site_type = models.CharField(max_length=50, choices=SITE_TYPE_CHOICES)
    country = models.CharField(max_length=100, blank=True)
    
    description = models.TextField()
    
    # Attribution and licensing
    source_name = models.CharField(
        max_length=200,
        help_text="Name of the source dataset or survey"
    )
    source_url = models.URLField(
        blank=True,
        help_text="URL to source dataset or survey project"
    )
    source_license = models.CharField(
        max_length=200,
        help_text="License identifier (e.g., CC-BY-SA-4.0, ODbL, proprietary)"
    )
    attribution = models.TextField(
        help_text="Required attribution text"
    )
    
    # Sensitivity and privacy
    sensitivity_level = models.CharField(
        max_length=50,
        choices=SENSITIVITY_LEVEL_CHOICES,
        default='public_demo'
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about data processing or restrictions"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Digital Twin Site'
        verbose_name_plural = 'Digital Twin Sites'
    
    def __str__(self) -> str:
        return f"{self.name} ({self.site_type})"


class TerrainMap(models.Model):
    """
    A terrain map representing the spatial structure of a digital twin site.
    Uses local 3D grid coordinates for GPS-denied navigation.
    """
    
    COORDINATE_SYSTEM_CHOICES = [
        ('local_mission_3d_grid', 'Local Mission 3D Grid'),
        ('utm', 'UTM'),
        ('wgs84', 'WGS84'),
        ('arbitrary_local', 'Arbitrary Local'),
    ]
    
    SOURCE_FORMAT_CHOICES = [
        ('manual', 'Manual Entry'),
        ('therion', 'Therion Survey'),
        ('survex', 'Survex Survey'),
        ('point_cloud', 'Point Cloud Processed'),
        ('geojson', 'GeoJSON'),
        ('synthetic', 'Synthetically Generated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    digital_twin_site = models.ForeignKey(
        DigitalTwinSite,
        on_delete=models.CASCADE,
        related_name='terrain_maps'
    )
    
    slug = models.SlugField(max_length=100)
    name = models.CharField(max_length=200)
    
    coordinate_system = models.CharField(
        max_length=50,
        choices=COORDINATE_SYSTEM_CHOICES,
        default='local_mission_3d_grid'
    )
    origin_label = models.CharField(
        max_length=200,
        help_text="Description of coordinate system origin (e.g., 'Cave entrance')"
    )
    units = models.CharField(
        max_length=20,
        default='meters',
        help_text="Units for coordinates (typically meters)"
    )
    
    source_format = models.CharField(max_length=50, choices=SOURCE_FORMAT_CHOICES)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['digital_twin_site', 'name']
        verbose_name = 'Terrain Map'
        verbose_name_plural = 'Terrain Maps'
        unique_together = [['digital_twin_site', 'slug']]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.digital_twin_site.name})"


class TerrainSector(models.Model):
    """
    A discrete sector or region within a terrain map. Represents a chamber,
    passage, room, or other spatial unit.
    """
    
    SECTOR_TYPE_CHOICES = [
        ('chamber', 'Chamber'),
        ('passage', 'Passage'),
        ('junction', 'Junction'),
        ('entrance', 'Entrance'),
        ('shaft', 'Vertical Shaft'),
        ('sump', 'Water-filled Sump'),
        ('room', 'Room'),
        ('corridor', 'Corridor'),
        ('void', 'Void Space'),
        ('hazard', 'Hazard Zone'),
        # Vessel-specific sectors
        ('cargo_hold', 'Cargo Hold'),
        ('engine_room', 'Engine Room'),
        ('bridge', 'Bridge'),
        ('crew_quarters', 'Crew Quarters'),
        ('bilge', 'Bilge'),
        ('hull_breach', 'Hull Breach'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    terrain_map = models.ForeignKey(
        TerrainMap,
        on_delete=models.CASCADE,
        related_name='sectors'
    )
    
    sector_id = models.CharField(
        max_length=50,
        help_text="Sector identifier (e.g., 'C1', 'P3', 'junction-alpha')"
    )
    label = models.CharField(max_length=200)
    sector_type = models.CharField(max_length=50, choices=SECTOR_TYPE_CHOICES)
    
    # 3D position and dimensions
    x_m = models.FloatField(help_text="X coordinate in meters")
    y_m = models.FloatField(help_text="Y coordinate in meters")
    z_m = models.FloatField(help_text="Z coordinate in meters (vertical)")
    
    width_m = models.FloatField(
        null=True,
        blank=True,
        help_text="Approximate width in meters"
    )
    height_m = models.FloatField(
        null=True,
        blank=True,
        help_text="Approximate height in meters"
    )
    depth_m = models.FloatField(
        null=True,
        blank=True,
        help_text="Approximate depth in meters"
    )
    elevation_m = models.FloatField(
        null=True,
        blank=True,
        help_text="Elevation relative to reference point"
    )
    
    confidence = models.FloatField(
        default=1.0,
        help_text="Data confidence (0.0-1.0)"
    )
    
    source_ref = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reference to source data (survey station, etc.)"
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata (dimensions, features, etc.)"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['terrain_map', 'sector_id']
        verbose_name = 'Terrain Sector'
        verbose_name_plural = 'Terrain Sectors'
        unique_together = [['terrain_map', 'sector_id']]
    
    def __str__(self) -> str:
        return f"{self.sector_id}: {self.label}"


class TerrainPath(models.Model):
    """
    A path or connection between two terrain sectors. Represents traversable
    routes with distance, bearing, and risk assessment.
    """
    
    PATH_TYPE_CHOICES = [
        ('passage', 'Passage'),
        ('climb', 'Climb'),
        ('descent', 'Descent'),
        ('crawl', 'Crawl'),
        ('squeeze', 'Tight Squeeze'),
        ('swim', 'Underwater'),
        ('dive', 'Technical Dive'),
        ('traverse', 'Traverse'),
        ('ladder', 'Ladder/Fixed Aid'),
        ('open', 'Open Path'),
        # Vessel-specific paths
        ('wade', 'Wade (Shallow Water)'),
        ('sealed_passage', 'Sealed/Watertight Door'),
        ('emergency_hatch', 'Emergency Hatch'),
    ]
    
    TRAVERSAL_RISK_CHOICES = [
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('extreme', 'Extreme Risk'),
        ('impassable', 'Impassable'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    terrain_map = models.ForeignKey(
        TerrainMap,
        on_delete=models.CASCADE,
        related_name='paths'
    )
    
    from_sector = models.ForeignKey(
        TerrainSector,
        on_delete=models.CASCADE,
        related_name='outgoing_paths'
    )
    to_sector = models.ForeignKey(
        TerrainSector,
        on_delete=models.CASCADE,
        related_name='incoming_paths'
    )
    
    # Path characteristics
    distance_m = models.FloatField(help_text="Path distance in meters")
    bearing_deg = models.FloatField(
        null=True,
        blank=True,
        help_text="Compass bearing in degrees (0-360)"
    )
    vertical_change_m = models.FloatField(
        help_text="Vertical change in meters (positive=up, negative=down)"
    )
    
    path_type = models.CharField(max_length=50, choices=PATH_TYPE_CHOICES)
    traversal_risk = models.CharField(
        max_length=50,
        choices=TRAVERSAL_RISK_CHOICES,
        default='low'
    )
    
    confidence = models.FloatField(
        default=1.0,
        help_text="Data confidence (0.0-1.0)"
    )
    
    # Capabilities required for traversal
    capabilities_required = models.JSONField(
        default=list,
        help_text="Required capabilities (e.g., ['waterproof', 'vertical_mobility'])"
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata (restrictions, hazards, etc.)"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['terrain_map', 'from_sector']
        verbose_name = 'Terrain Path'
        verbose_name_plural = 'Terrain Paths'
    
    def __str__(self) -> str:
        return f"{self.from_sector.sector_id} → {self.to_sector.sector_id} ({self.distance_m}m)"


class Waypoint(models.Model):
    """
    A waypoint within a terrain map. Used for route planning and navigation.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    terrain_map = models.ForeignKey(
        TerrainMap,
        on_delete=models.CASCADE,
        related_name='waypoints'
    )
    
    waypoint_id = models.CharField(
        max_length=50,
        help_text="Waypoint identifier (e.g., 'WP1', 'nav-alpha')"
    )
    label = models.CharField(max_length=200)
    
    # 3D position
    x_m = models.FloatField(help_text="X coordinate in meters")
    y_m = models.FloatField(help_text="Y coordinate in meters")
    z_m = models.FloatField(help_text="Z coordinate in meters (vertical)")
    
    # Route information
    sequence = models.IntegerField(
        null=True,
        blank=True,
        help_text="Sequence number in a route"
    )
    route_group = models.CharField(
        max_length=100,
        blank=True,
        help_text="Route group identifier"
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata (features, notes, etc.)"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['terrain_map', 'route_group', 'sequence', 'waypoint_id']
        verbose_name = 'Waypoint'
        verbose_name_plural = 'Waypoints'
        unique_together = [['terrain_map', 'waypoint_id']]
    
    def __str__(self) -> str:
        return f"{self.waypoint_id}: {self.label}"


class MapArtifact(models.Model):
    """
    Reference to map artifacts such as survey files, point clouds, meshes,
    or images. Stores metadata and references, not large binary data.
    """
    
    ARTIFACT_TYPE_CHOICES = [
        ('survey_file', 'Survey Data File'),
        ('point_cloud', 'Point Cloud Reference'),
        ('mesh', '3D Mesh Reference'),
        ('image', 'Image/Photo'),
        ('reference_link', 'External Reference Link'),
        ('derived_json', 'Derived JSON Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    digital_twin_site = models.ForeignKey(
        DigitalTwinSite,
        on_delete=models.CASCADE,
        related_name='artifacts'
    )
    
    artifact_type = models.CharField(max_length=50, choices=ARTIFACT_TYPE_CHOICES)
    file_format = models.CharField(
        max_length=50,
        blank=True,
        help_text="File format (e.g., 'survex', 'therion', 'las', 'ply', 'geojson')"
    )
    
    local_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to file within data/ directory"
    )
    external_url = models.URLField(
        blank=True,
        help_text="URL to external resource"
    )
    
    # Attribution
    source_license = models.CharField(
        max_length=200,
        help_text="License identifier"
    )
    attribution = models.TextField(
        help_text="Required attribution text"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this artifact"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['digital_twin_site', 'artifact_type', 'created_at']
        verbose_name = 'Map Artifact'
        verbose_name_plural = 'Map Artifacts'
    
    def __str__(self) -> str:
        return f"{self.artifact_type}: {self.digital_twin_site.name}"
