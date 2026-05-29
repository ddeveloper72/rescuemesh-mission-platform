"""
Agent API serializers.
"""
from rest_framework import serializers
from .models import Agent, AgentStateChange


class AgentStateChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStateChange
        fields = '__all__'


class AgentSerializer(serializers.ModelSerializer):
    state_changes = AgentStateChangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Agent
        fields = '__all__'
