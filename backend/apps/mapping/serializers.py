"""
Expected output serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import (
    ExpectedOutputTemplate,
    DigitalTwinSite,
    TerrainMap,
    TerrainSector,
    TerrainPath,
    Waypoint,
    MapArtifact,
)


class ExpectedOutputTemplateSerializer(serializers.ModelSerializer):
    use_case_slug = serializers.CharField(source='use_case.slug', read_only=True)
    use_case_title = serializers.CharField(source='use_case.title', read_only=True)
    
    class Meta:
        model = ExpectedOutputTemplate
        fields = [
            'id', 'use_case', 'use_case_slug', 'use_case_title',
            'name', 'output_type', 'description', 'confidence_required',
            'human_review_required', 'display_priority', 'icon_name',
            'output_schema', 'created_at', 'updated_at'
        ]


class DigitalTwinSiteSerializer(serializers.ModelSerializer):
    """Serializer for digital twin site information."""
    
    class Meta:
        model = DigitalTwinSite
        fields = [
            'id', 'slug', 'name', 'site_type', 'country', 'description',
            'source_name', 'source_url', 'source_license', 'attribution',
            'sensitivity_level', 'notes', 'created_at', 'updated_at'
        ]


class TerrainMapSerializer(serializers.ModelSerializer):
    """Serializer for terrain map information."""
    
    digital_twin_site_slug = serializers.CharField(source='digital_twin_site.slug', read_only=True)
    digital_twin_site_name = serializers.CharField(source='digital_twin_site.name', read_only=True)
    sector_count = serializers.SerializerMethodField()
    waypoint_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TerrainMap
        fields = [
            'id', 'digital_twin_site', 'digital_twin_site_slug', 'digital_twin_site_name',
            'slug', 'name', 'coordinate_system', 'origin_label', 'units',
            'source_format', 'sector_count', 'waypoint_count',
            'created_at', 'updated_at'
        ]
    
    def get_sector_count(self, obj):
        return obj.sectors.count()
    
    def get_waypoint_count(self, obj):
        return obj.waypoints.count()


class TerrainSectorSerializer(serializers.ModelSerializer):
    """Serializer for terrain sectors."""
    
    terrain_map_slug = serializers.CharField(source='terrain_map.slug', read_only=True)
    
    class Meta:
        model = TerrainSector
        fields = [
            'id', 'terrain_map', 'terrain_map_slug', 'sector_id', 'label',
            'sector_type', 'x_m', 'y_m', 'z_m', 'width_m', 'height_m',
            'depth_m', 'elevation_m', 'confidence', 'source_ref', 'metadata',
            'created_at', 'updated_at'
        ]


class TerrainPathSerializer(serializers.ModelSerializer):
    """Serializer for terrain paths between sectors."""
    
    from_sector_id = serializers.CharField(source='from_sector.sector_id', read_only=True)
    from_sector_label = serializers.CharField(source='from_sector.label', read_only=True)
    to_sector_id = serializers.CharField(source='to_sector.sector_id', read_only=True)
    to_sector_label = serializers.CharField(source='to_sector.label', read_only=True)
    
    class Meta:
        model = TerrainPath
        fields = [
            'id', 'terrain_map', 'from_sector', 'from_sector_id', 'from_sector_label',
            'to_sector', 'to_sector_id', 'to_sector_label', 'distance_m',
            'bearing_deg', 'vertical_change_m', 'path_type', 'traversal_risk',
            'confidence', 'capabilities_required', 'metadata',
            'created_at', 'updated_at'
        ]


class WaypointSerializer(serializers.ModelSerializer):
    """Serializer for waypoints."""
    
    terrain_map_slug = serializers.CharField(source='terrain_map.slug', read_only=True)
    
    class Meta:
        model = Waypoint
        fields = [
            'id', 'terrain_map', 'terrain_map_slug', 'waypoint_id', 'label',
            'x_m', 'y_m', 'z_m', 'sequence', 'route_group', 'metadata',
            'created_at', 'updated_at'
        ]


class MapArtifactSerializer(serializers.ModelSerializer):
    """Serializer for map artifacts."""
    
    digital_twin_site_slug = serializers.CharField(source='digital_twin_site.slug', read_only=True)
    digital_twin_site_name = serializers.CharField(source='digital_twin_site.name', read_only=True)
    
    class Meta:
        model = MapArtifact
        fields = [
            'id', 'digital_twin_site', 'digital_twin_site_slug', 'digital_twin_site_name',
            'artifact_type', 'file_format', 'local_path', 'external_url',
            'source_license', 'attribution', 'notes',
            'created_at', 'updated_at'
        ]
