"""
Sensor package API views.
"""
from rest_framework import viewsets
from .models import SensorPackageTemplate
from .serializers import SensorPackageTemplateSerializer


class SensorPackageTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sensor package templates"""
    queryset = SensorPackageTemplate.objects.all()
    serializer_class = SensorPackageTemplateSerializer
    filterset_fields = ['agent_role__use_case', 'sensor_type', 'data_format']
