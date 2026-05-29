"""
AI prompt API views.
"""
from rest_framework import viewsets
from .models import AIPromptTemplate
from .serializers import AIPromptTemplateSerializer


class AIPromptTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI prompt templates"""
    queryset = AIPromptTemplate.objects.filter(is_active=True)
    serializer_class = AIPromptTemplateSerializer
    filterset_fields = ['use_case', 'role', 'requires_human_review']
