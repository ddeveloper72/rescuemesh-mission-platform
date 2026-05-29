"""
Sensor package serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import SensorPackageTemplate


class SensorPackageTemplateSerializer(serializers.ModelSerializer):
    agent_role_name = serializers.CharField(source='agent_role.name', read_only=True)
    use_case_slug = serializers.CharField(source='agent_role.use_case.slug', read_only=True)
    
    class Meta:
        model = SensorPackageTemplate
        fields = [
            'id', 'agent_role', 'agent_role_name', 'use_case_slug',
            'sensor_type', 'display_name', 'description',
            'data_format', 'expected_output', 'specifications', 'failure_modes',
            'created_at', 'updated_at'
        ]
