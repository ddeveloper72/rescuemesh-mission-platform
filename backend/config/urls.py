"""
URL configuration for RescueMesh Mission Platform.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Import health check views
from apps.missions.views_health import health_check, readiness_check

# Create a router for API endpoints
router = routers.DefaultRouter()

# Register viewsets that need to be at top level to avoid route conflicts
from apps.usecases import views as usecase_views
router.register(r'terrain-profiles', usecase_views.TerrainProfileViewSet, basename='terrain-profile')
router.register(r'agent-role-templates', usecase_views.AgentRoleTemplateViewSet, basename='agent-role-template')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        # Health check endpoints
        path('health/', health_check, name='health-check'),
        path('ready/', readiness_check, name='readiness-check'),
        # API routes
        path('', include(router.urls)),
        path('missions/', include('apps.missions.urls')),
        path('agents/', include('apps.agents.urls')),
        path('usecases/', include('apps.usecases.urls')),
        path('sensors/', include('apps.sensors.urls')),
        path('failures/', include('apps.faults.urls')),
        path('mapping/', include('apps.mapping.urls')),
        path('prompts/', include('apps.ai_prompts.urls')),
        path('telemetry/', include('apps.telemetry.urls')),
        path('', include('apps.media_generation.urls')),
    ])),
]
