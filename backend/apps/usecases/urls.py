"""
Use case app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.UseCaseTemplateViewSet, basename='usecase')
router.register(r'terrain', views.TerrainProfileViewSet, basename='terrain')
router.register(r'agent-roles', views.AgentRoleTemplateViewSet, basename='agent-role')

urlpatterns = [
    path('', include(router.urls)),
]
