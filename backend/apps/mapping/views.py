"""
Expected output API views.
"""
from rest_framework import viewsets
from .models import ExpectedOutputTemplate
from .serializers import ExpectedOutputTemplateSerializer


class ExpectedOutputTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for expected output templates"""
    queryset = ExpectedOutputTemplate.objects.all()
    serializer_class = ExpectedOutputTemplateSerializer
    filterset_fields = ['use_case', 'output_type', 'confidence_required', 'human_review_required']
