"""
Mission app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'missions', views.MissionViewSet, basename='mission')
router.register(r'events', views.MissionEventViewSet, basename='mission-event')

urlpatterns = [
    path('', include(router.urls)),
]
