"""
Mapping app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'outputs', views.ExpectedOutputTemplateViewSet, basename='output')
router.register(r'digital-twin-sites', views.DigitalTwinSiteViewSet, basename='digital-twin-site')
router.register(r'terrain-maps', views.TerrainMapViewSet, basename='terrain-map')
router.register(r'terrain-sectors', views.TerrainSectorViewSet, basename='terrain-sector')
router.register(r'terrain-paths', views.TerrainPathViewSet, basename='terrain-path')
router.register(r'waypoints', views.WaypointViewSet, basename='waypoint')
router.register(r'map-artifacts', views.MapArtifactViewSet, basename='map-artifact')

urlpatterns = [
    path('', include(router.urls)),
]
