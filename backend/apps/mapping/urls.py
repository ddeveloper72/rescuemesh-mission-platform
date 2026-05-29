"""
Mapping app URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'outputs', views.ExpectedOutputTemplateViewSet, basename='output')

urlpatterns = [
    path('', include(router.urls)),
]
