"""
Mission API serializers.
"""
from rest_framework import serializers
from .models import Mission, MissionEvent


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
