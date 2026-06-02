"""
UUID validation utilities for missions.

Prevents stale UUID issues by validating mission identifiers at multiple layers.
"""
from uuid import UUID
from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_uuid_format(value: str) -> bool:
    """
    Validate that a string is a properly formatted UUID.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    try:
        UUID(value, version=4)
        return True
    except (ValueError, AttributeError):
        return False


def validate_mission_uuid(uuid_str: str, raise_exception: bool = True) -> Optional[str]:
    """
    Validate mission UUID format and provide clear error messages.
    
    Args:
        uuid_str: UUID string to validate
        raise_exception: If True, raises ValidationError on invalid UUID
        
    Returns:
        Normalized UUID string if valid, None if invalid and raise_exception=False
        
    Raises:
        ValidationError: If UUID is invalid and raise_exception=True
    """
    if not uuid_str:
        if raise_exception:
            raise ValidationError("Mission UUID is required")
        return None
    
    if not validate_uuid_format(uuid_str):
        if raise_exception:
            raise ValidationError(
                f"Invalid UUID format: '{uuid_str}'. "
                "Expected format: xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
            )
        return None
    
    return str(UUID(uuid_str))  # Normalize format


class MissionUUIDField(serializers.UUIDField):
    """
    Enhanced UUID field with better error messages for mission endpoints.
    """
    
    def to_internal_value(self, data):
        """Override to provide better error messages."""
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            raise serializers.ValidationError(
                f"Invalid mission UUID: '{data}'. "
                "This may indicate a stale UUID from a previous database. "
                "Try rebuilding the frontend with: docker compose build --no-cache frontend"
            )


def check_mission_exists(mission_pk: str) -> Dict[str, Any]:
    """
    Check if a mission exists and return diagnostic information.
    
    Args:
        mission_pk: Mission UUID or slug to check
        
    Returns:
        Dictionary with existence status and suggestions
    """
    from apps.missions.models import Mission
    
    result = {
        'exists': False,
        'uuid': mission_pk,
        'valid_format': validate_uuid_format(mission_pk),
        'suggestions': []
    }
    
    # Check if mission exists
    try:
        mission = Mission.objects.get(pk=mission_pk)
        result['exists'] = True
        result['mission_name'] = mission.name
        result['scenario'] = mission.scenario.name if mission.scenario else None
        return result
    except Mission.DoesNotExist:
        pass
    
    # Provide helpful suggestions
    if result['valid_format']:
        result['suggestions'].append(
            "UUID format is valid but mission not found in database. "
            "This may indicate:"
        )
        result['suggestions'].append("  1. Database was recreated (run: docker compose build --no-cache frontend)")
        result['suggestions'].append("  2. Mission was deleted")
        result['suggestions'].append("  3. Wrong environment (dev vs production)")
        
        # Find similar missions
        all_missions = Mission.objects.all().values('pk', 'name', 'scenario__name')
        if all_missions.exists():
            result['suggestions'].append("")
            result['suggestions'].append("Available missions:")
            for m in all_missions[:5]:
                result['suggestions'].append(f"  - {m['pk']} ({m['name']} - {m['scenario__name']})")
    else:
        result['suggestions'].append("Invalid UUID format")
    
    return result
