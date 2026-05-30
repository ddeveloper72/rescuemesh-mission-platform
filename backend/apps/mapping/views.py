"""
Expected output API views.
"""
from rest_framework import viewsets
from .models import (
    ExpectedOutputTemplate,
    DigitalTwinSite,
    TerrainMap,
    TerrainSector,
    TerrainPath,
    Waypoint,
    MapArtifact,
)
from .serializers import (
    ExpectedOutputTemplateSerializer,
    DigitalTwinSiteSerializer,
    TerrainMapSerializer,
    TerrainSectorSerializer,
    TerrainPathSerializer,
    WaypointSerializer,
    MapArtifactSerializer,
)


class ExpectedOutputTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for expected output templates"""
    queryset = ExpectedOutputTemplate.objects.all()
    serializer_class = ExpectedOutputTemplateSerializer
    filterset_fields = ['use_case', 'output_type', 'confidence_required', 'human_review_required']


class DigitalTwinSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for digital twin sites (read-only)"""
    queryset = DigitalTwinSite.objects.all()
    serializer_class = DigitalTwinSiteSerializer
    lookup_field = 'slug'
    filterset_fields = ['site_type', 'country', 'sensitivity_level']


class TerrainMapViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for terrain maps (read-only)"""
    queryset = TerrainMap.objects.select_related('digital_twin_site').all()
    serializer_class = TerrainMapSerializer
    lookup_field = 'slug'
    filterset_fields = ['digital_twin_site', 'coordinate_system', 'source_format']


class TerrainSectorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for terrain sectors (read-only)"""
    queryset = TerrainSector.objects.select_related('terrain_map').all()
    serializer_class = TerrainSectorSerializer
    filterset_fields = ['terrain_map', 'sector_type']


class TerrainPathViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for terrain paths (read-only)"""
    queryset = TerrainPath.objects.select_related(
        'terrain_map', 'from_sector', 'to_sector'
    ).all()
    serializer_class = TerrainPathSerializer
    filterset_fields = ['terrain_map', 'path_type', 'traversal_risk']


class WaypointViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for waypoints (read-only)"""
    queryset = Waypoint.objects.select_related('terrain_map').all()
    serializer_class = WaypointSerializer
    filterset_fields = ['terrain_map', 'route_group']


class MapArtifactViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for map artifacts (read-only)"""
    queryset = MapArtifact.objects.select_related('digital_twin_site').all()
    serializer_class = MapArtifactSerializer
    filterset_fields = ['digital_twin_site', 'artifact_type', 'file_format']
