"""
Expected output serializers for RescueMesh API.
"""
from rest_framework import serializers
from .models import ExpectedOutputTemplate


class ExpectedOutputTemplateSerializer(serializers.ModelSerializer):
    use_case_slug = serializers.CharField(source='use_case.slug', read_only=True)
    use_case_title = serializers.CharField(source='use_case.title', read_only=True)
    
    class Meta:
        model = ExpectedOutputTemplate
        fields = [
            'id', 'use_case', 'use_case_slug', 'use_case_title',
            'name', 'output_type', 'description', 'confidence_required',
            'human_review_required', 'display_priority', 'icon_name',
            'output_schema', 'created_at', 'updated_at'
        ]
