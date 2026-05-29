"""
AI prompt serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import AIPromptTemplate


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    use_case_slug = serializers.CharField(source='use_case.slug', read_only=True)
    use_case_title = serializers.CharField(source='use_case.title', read_only=True)
    
    class Meta:
        model = AIPromptTemplate
        fields = [
            'id', 'use_case', 'use_case_slug', 'use_case_title',
            'name', 'role', 'description', 'prompt_text', 'system_prompt',
            'input_types', 'output_schema', 'temperature', 'max_tokens',
            'requires_human_review', 'is_active', 'created_at', 'updated_at'
        ]
