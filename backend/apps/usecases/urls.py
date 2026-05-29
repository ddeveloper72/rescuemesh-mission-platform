"""
Use case app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Only register UseCaseTemplateViewSet here with empty prefix
# Terrain and AgentRole viewsets are registered in config/urls.py to avoid route conflicts
router = DefaultRouter()
router.register(r'', views.UseCaseTemplateViewSet, basename='usecase')

urlpatterns = [
    path('', include(router.urls)),
]
