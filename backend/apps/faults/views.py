"""
Failure profile API views.
"""
from rest_framework import viewsets
from .models import FailureProfile
from .serializers import FailureProfileSerializer


class FailureProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for failure profiles"""
    queryset = FailureProfile.objects.all()
    serializer_class = FailureProfileSerializer
    filterset_fields = ['use_case', 'severity', 'affected_component', 'trigger_type']
