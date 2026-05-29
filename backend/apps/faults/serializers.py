"""
Failure profile serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import FailureProfile


class FailureProfileSerializer(serializers.ModelSerializer):
    use_case_slug = serializers.CharField(source='use_case.slug', read_only=True)
    use_case_title = serializers.CharField(source='use_case.title', read_only=True)
    
    class Meta:
        model = FailureProfile
        fields = [
            'id', 'use_case', 'use_case_slug', 'use_case_title',
            'name', 'description', 'affected_component', 'severity',
            'trigger_type', 'trigger_conditions', 'effects', 'operator_message',
            'is_recoverable', 'recovery_actions', 'created_at', 'updated_at'
        ]
