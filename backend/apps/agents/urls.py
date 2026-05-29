"""
Agent app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'agents', views.AgentViewSet, basename='agent')
router.register(r'state-changes', views.AgentStateChangeViewSet, basename='agent-state-change')

urlpatterns = [
    path('', include(router.urls)),
]
