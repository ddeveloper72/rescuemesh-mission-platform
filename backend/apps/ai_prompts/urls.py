"""
AI Prompts app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.AIPromptTemplateViewSet, basename='prompt')

urlpatterns = [
    path('', include(router.urls)),
]
