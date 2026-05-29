"""
URL configuration for RescueMesh Mission Platform.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Create a router for API endpoints
router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('', include(router.urls)),
        path('missions/', include('apps.missions.urls')),
        path('agents/', include('apps.agents.urls')),
        path('usecases/', include('apps.usecases.urls')),
        path('sensors/', include('apps.sensors.urls')),
        path('failures/', include('apps.faults.urls')),
        path('outputs/', include('apps.mapping.urls')),
        path('prompts/', include('apps.ai_prompts.urls')),
        path('telemetry/', include('apps.telemetry.urls')),
    ])),
]
