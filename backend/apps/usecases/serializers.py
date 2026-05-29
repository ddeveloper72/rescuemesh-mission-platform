"""
Use case serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import UseCaseTemplate, TerrainProfile, AgentRoleTemplate
from apps.sensors.models import SensorPackageTemplate
from apps.faults.models import FailureProfile
from apps.mapping.models import ExpectedOutputTemplate
from apps.ai_prompts.models import AIPromptTemplate


class TerrainProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerrainProfile
        fields = [
            'id', 'terrain_type', 'gps_status', 'communication_conditions',
            'lighting_conditions', 'hazards', 'accessibility', 'simulation_complexity',
            'created_at', 'updated_at'
        ]


class SensorPackageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorPackageTemplate
        fields = [
            'id', 'sensor_type', 'display_name', 'description',
            'data_format', 'expected_output', 'specifications', 'failure_modes',
            'created_at', 'updated_at'
        ]


class AgentRoleTemplateSerializer(serializers.ModelSerializer):
    sensor_packages = SensorPackageTemplateSerializer(many=True, read_only=True)
    
    class Meta:
        model = AgentRoleTemplate
        fields = [
            'id', 'name', 'role', 'description', 'default_quantity',
            'agent_type', 'capabilities', 'specifications', 'sensor_packages',
            'created_at', 'updated_at'
        ]


class FailureProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureProfile
        fields = [
            'id', 'name', 'description', 'affected_component', 'severity',
            'trigger_type', 'trigger_conditions', 'effects', 'operator_message',
            'is_recoverable', 'recovery_actions', 'created_at', 'updated_at'
        ]


class ExpectedOutputTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedOutputTemplate
        fields = [
            'id', 'name', 'output_type', 'description', 'confidence_required',
            'human_review_required', 'display_priority', 'icon_name',
            'output_schema', 'created_at', 'updated_at'
        ]


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPromptTemplate
        fields = [
            'id', 'name', 'role', 'description', 'prompt_text', 'system_prompt',
            'input_types', 'output_schema', 'temperature', 'max_tokens',
            'requires_human_review', 'is_active', 'created_at', 'updated_at'
        ]


class UseCaseTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    
    class Meta:
        model = UseCaseTemplate
        fields = [
            'id', 'slug', 'title', 'priority', 'summary',
            'is_active', 'is_demo', 'created_at'
        ]


class UseCaseTemplateDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all related data"""
    terrain = TerrainProfileSerializer(read_only=True)
    agent_roles = AgentRoleTemplateSerializer(many=True, read_only=True)
    failure_profiles = FailureProfileSerializer(many=True, read_only=True)
    expected_outputs = ExpectedOutputTemplateSerializer(many=True, read_only=True)
    ai_prompts = AIPromptTemplateSerializer(many=True, read_only=True)
    
    class Meta:
        model = UseCaseTemplate
        fields = [
            'id', 'slug', 'title', 'priority', 'summary', 'objective',
            'is_active', 'is_demo', 'created_at', 'updated_at',
            'terrain', 'agent_roles', 'failure_profiles',
            'expected_outputs', 'ai_prompts'
        ]


class DemoProfileSerializer(serializers.Serializer):
    """
    Serializer for demo profile matching frontend TypeScript UseCaseDemoProfile interface.
    This aggregates all use case data into the format expected by the demo dashboard.
    """
    slug = serializers.CharField()
    title = serializers.CharField()
    priority = serializers.CharField()
    missionId = serializers.CharField()
    status = serializers.CharField()
    missionObjective = serializers.CharField()
    terrain = serializers.DictField()
    agents = serializers.ListField()
    expectedFailures = serializers.ListField()
    expectedOutputs = serializers.ListField()
    simulation = serializers.DictField()
    timeline = serializers.ListField()
    aiAnalyst = serializers.DictField()
