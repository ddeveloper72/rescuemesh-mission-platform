"""
Mission API serializers.
"""
from rest_framework import serializers
from .models import Mission, MissionEvent, MissionSimulation


class MissionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionEvent
        fields = '__all__'


class MissionSerializer(serializers.ModelSerializer):
    events = MissionEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Mission
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['name', 'mission_id', 'use_case_type', 'objective', 'terrain_description', 'simulation_seed', 'metadata']


class MissionSimulationSerializer(serializers.ModelSerializer):
    """Serializer for MissionSimulation model."""
    elapsed_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = MissionSimulation
        fields = [
            'id', 'mission', 'status', 'speed_multiplier',
            'started_at', 'paused_at', 'accumulated_elapsed_seconds',
            'elapsed_seconds', 'random_seed', 'scenario_config',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'elapsed_seconds']
    
    def get_elapsed_seconds(self, obj):
        """Get the current elapsed mission time."""
        return obj.get_elapsed_seconds()


class SpeedControlSerializer(serializers.Serializer):
    """Serializer for speed control requests."""
    speed_multiplier = serializers.FloatField(min_value=0.5, max_value=20.0)
    
    def validate_speed_multiplier(self, value):
        """Validate that speed is one of the allowed values."""
        allowed_speeds = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
        if value not in allowed_speeds:
            raise serializers.ValidationError(
                f'Speed multiplier must be one of: {allowed_speeds}'
            )
        return value
