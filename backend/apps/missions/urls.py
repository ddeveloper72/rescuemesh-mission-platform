"""
Mission app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register with empty prefix since we're already under /missions/ from config/urls.py
router.register(r'', views.MissionViewSet, basename='mission')
router.register(r'events', views.MissionEventViewSet, basename='mission-event')

urlpatterns = [
    path('', include(router.urls)),
]
