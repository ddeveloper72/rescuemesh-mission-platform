"""
Views for generated mission media API.

Provides endpoints for accessing generated synthetic media:
- List mission media metadata
- Serve generated image previews
- Serve generated audio files
- Serve spectrograms
"""

from django.http import FileResponse, JsonResponse, HttpResponseNotFound
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pathlib import Path

from .generators.image_generator import generate_and_save_image, get_image_path
from .generators.audio_generator import generate_and_save_audio, get_audio_path
from .generators.spectrogram_generator import generate_and_save_spectrogram, get_spectrogram_path


def get_mission_generated_media_metadata(mission_id, use_case):
    """
    Get metadata for all generated media for a mission.
    
    This returns structured metadata without generating the actual files yet (lazy generation).
    """
    metadata = []
    
    # Different media based on use case
    if use_case == 'collapsed-building-search':
        metadata.extend([
            {
                "id": f"{mission_id}-dusty-rubble-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "low_light_camera",
                "agent_id": "scout-drone",
                "agent_name": "Scout Drone",
                "sector_id": "void-space-1",
                "location_label": "Void Space 1",
                "mission_time_seconds": 180,
                "status": "review_recommended",
                "confidence": 68,
                "signal_quality": 72,
                "description": "Low-light image showing dusty void space with possible structural hazards.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-dusty-rubble-001/preview/",
                "annotations": ["dust occlusion", "low visibility", "structural debris"]
            },
            {
                "id": f"{mission_id}-thermal-anomaly-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "thermal",
                "agent_id": "thermal-drone",
                "agent_name": "Thermal Scanner",
                "sector_id": "void-space-2",
                "location_label": "Void Space 2",
                "mission_time_seconds": 300,
                "status": "human_review_required",
                "confidence": 74,
                "signal_quality": 65,
                "description": "Thermal signature detected in confined space. Possible heat source.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-thermal-anomaly-001/preview/",
                "annotations": ["thermal anomaly", "heat signature", "investigation required"]
            },
            {
                "id": f"{mission_id}-tapping-audio-001",
                "generated": True,
                "media_type": "audio",
                "sensor_type": "microphone",
                "agent_id": "audio-sensor-1",
                "agent_name": "Audio Sensor Alpha",
                "sector_id": "void-space-2",
                "location_label": "Void Space 2",
                "mission_time_seconds": 360,
                "status": "human_review_required",
                "confidence": 82,
                "signal_quality": 58,
                "description": "Rhythmic tapping detected. Pattern suggests intentional signal.",
                "audio_url": f"/api/v1/generated-media/{mission_id}-tapping-audio-001/audio/",
                "spectrogram_url": f"/api/v1/generated-media/{mission_id}-tapping-audio-001/spectrogram/",
                "annotations": ["rhythmic pattern", "possible human signal", "low bandwidth"]
            }
        ])
    
    elif use_case == 'cave-rescue':
        metadata.extend([
            {
                "id": f"{mission_id}-cave-tunnel-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "low_light_camera",
                "agent_id": "scout",
                "agent_name": "Cave Scout Drone",
                "sector_id": "main-tunnel",
                "location_label": "Main Tunnel",
                "mission_time_seconds": 120,
                "status": "normal",
                "confidence": 85,
                "signal_quality": 78,
                "description": "Low-light cave tunnel mapping image.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-cave-tunnel-001/preview/",
                "annotations": ["tunnel mapped", "clear passage"]
            },
            {
                "id": f"{mission_id}-voice-audio-001",
                "generated": True,
                "media_type": "audio",
                "sensor_type": "audio_sensor",
                "agent_id": "scout",
                "agent_name": "Cave Scout Drone",
                "sector_id": "deep-squeeze",
                "location_label": "Deep Squeeze",
                "mission_time_seconds": 420,
                "status": "human_review_required",
                "confidence": 74,
                "signal_quality": 38,
                "description": "Voice-like audio pattern detected in low-bandwidth cave sector.",
                "audio_url": f"/api/v1/generated-media/{mission_id}-voice-audio-001/audio/",
                "spectrogram_url": f"/api/v1/generated-media/{mission_id}-voice-audio-001/spectrogram/",
                "annotations": ["voice-like audio", "possible human cue", "comms degraded"]
            },
            {
                "id": f"{mission_id}-last-frame-micro",
                "generated": True,
                "media_type": "image",
                "sensor_type": "camera",
                "agent_id": "micro",
                "agent_name": "Micro Mapper",
                "sector_id": "narrow-passage",
                "location_label": "Narrow Passage",
                "mission_time_seconds": 240,
                "status": "signal_lost",
                "confidence": 45,
                "signal_quality": 12,
                "description": "Last good frame before signal loss. Heavy degradation.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-last-frame-micro/preview/",
                "annotations": ["signal lost", "last known position", "NFC recovery available"]
            }
        ])
    
    elif use_case == 'flooded-structure':
        metadata.extend([
            {
                "id": f"{mission_id}-underwater-murky-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "underwater_camera",
                "agent_id": "amphibious",
                "agent_name": "Amphibious Explorer",
                "sector_id": "flooded-corridor",
                "location_label": "Flooded Corridor",
                "mission_time_seconds": 180,
                "status": "review_recommended",
                "confidence": 62,
                "signal_quality": 55,
                "description": "Underwater image with poor visibility due to particulate matter.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-underwater-murky-001/preview/",
                "annotations": ["murky water", "low visibility", "obstruction ahead"]
            }
        ])
    
    elif use_case == 'industrial-inspection':
        metadata.extend([
            {
                "id": f"{mission_id}-thermal-hotspot-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "thermal",
                "agent_id": "thermal-inspector",
                "agent_name": "Thermal Inspector",
                "sector_id": "equipment-bay",
                "location_label": "Equipment Bay",
                "mission_time_seconds": 240,
                "status": "human_review_required",
                "confidence": 88,
                "signal_quality": 92,
                "description": "Thermal hotspot detected on equipment surface. Possible overheating.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-thermal-hotspot-001/preview/",
                "annotations": ["thermal hotspot", "equipment overheating", "safety concern"]
            },
            {
                "id": f"{mission_id}-pipe-corrosion-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "visual_camera",
                "agent_id": "visual-inspector",
                "agent_name": "Visual Inspector",
                "sector_id": "pipe-corridor",
                "location_label": "Pipe Corridor",
                "mission_time_seconds": 300,
                "status": "review_recommended",
                "confidence": 76,
                "signal_quality": 88,
                "description": "Visible corrosion on pipe surface. Structural assessment recommended.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-pipe-corrosion-001/preview/",
                "annotations": ["corrosion detected", "structural integrity concern"]
            }
        ])
    
    elif use_case == 'archaeological-exploration':
        metadata.extend([
            {
                "id": f"{mission_id}-chamber-low-light-001",
                "generated": True,
                "media_type": "image",
                "sensor_type": "low_light_camera",
                "agent_id": "imaging-drone",
                "agent_name": "Low-Light Imaging Drone",
                "sector_id": "first-chamber",
                "location_label": "First Chamber",
                "mission_time_seconds": 360,
                "status": "documentation",
                "confidence": 82,
                "signal_quality": 74,
                "description": "Low-light documentation of chamber interior. Minimal disturbance approach.",
                "preview_url": f"/api/v1/generated-media/{mission_id}-chamber-low-light-001/preview/",
                "annotations": ["non-destructive documentation", "fragile environment"]
            }
        ])
    
    return metadata


@api_view(['GET'])
def mission_generated_media_list(request, mission_id):
    """
    List all generated media metadata for a mission.
    
    GET /api/v1/missions/{mission_id}/generated-media/
    """
    # Determine use case from mission_id or query param
    use_case = request.query_params.get('use_case', 'collapsed-building-search')
    
    metadata = get_mission_generated_media_metadata(mission_id, use_case)
    
    return Response({
        "mission_id": mission_id,
        "use_case": use_case,
        "generated_media_count": len(metadata),
        "media": metadata
    })


@api_view(['GET'])
def generated_media_preview(request, media_id):
    """
    Serve generated image preview (lazy generation).
    
    GET /api/v1/generated-media/{media_id}/preview/
    """
    # Parse media_id to determine what to generate
    # Format: {mission_id}-{media_type}-{sequence}
    
    # Determine image type from media_id
    if 'dusty-rubble' in media_id:
        media_type = 'dusty_rubble'
        annotations = ["dust occlusion", "low visibility"]
        confidence = 68
        signal_quality = 72
    elif 'thermal' in media_id:
        media_type = 'thermal'
        annotations = ["thermal anomaly"]
        confidence = 74
        signal_quality = 65
    elif 'cave-tunnel' in media_id:
        media_type = 'low_light'
        annotations = ["tunnel mapped"]
        confidence = 85
        signal_quality = 78
    elif 'last-frame' in media_id:
        media_type = 'last_frame'
        annotations = ["signal lost"]
        confidence = 45
        signal_quality = 12
    elif 'underwater' in media_id:
        media_type = 'underwater'
        annotations = ["murky water"]
        confidence = 62
        signal_quality = 55
    elif 'pipe-corrosion' in media_id or 'hotspot' in media_id:
        media_type = 'industrial' if 'pipe' in media_id else 'thermal'
        annotations = ["inspection finding"]
        confidence = 76
        signal_quality = 88
    elif 'chamber' in media_id:
        media_type = 'low_light'
        annotations = ["non-destructive documentation"]
        confidence = 82
        signal_quality = 74
    else:
        media_type = 'low_light'
        annotations = []
        confidence = 70
        signal_quality = 70
    
    # Generate and save image (lazy - only if not cached)
    path = generate_and_save_image(
        media_id=media_id,
        media_type=media_type,
        sector_label="Mission Sector",
        sensor_type='camera',
        annotations=annotations,
        confidence=confidence,
        signal_quality=signal_quality,
        hotspot='hotspot' in media_id
    )
    
    if not path.exists():
        return HttpResponseNotFound("Media generation failed")
    
    return FileResponse(open(path, 'rb'), content_type='image/png')


@api_view(['GET'])
def generated_media_audio(request, media_id):
    """
    Serve generated audio file (lazy generation).
    
    GET /api/v1/generated-media/{media_id}/audio/
    """
    # Determine audio type from media_id
    if 'tapping' in media_id:
        audio_type = 'tapping'
        kwargs = {'num_taps': 5, 'tempo': 'regular'}
    elif 'knocking' in media_id:
        audio_type = 'knocking'
        kwargs = {'num_knocks': 3, 'interval': 0.5}
    elif 'voice' in media_id:
        audio_type = 'voice_like'
        kwargs = {'duration': 2.0}
    else:
        audio_type = 'ambient'
        kwargs = {'environment': 'cave', 'duration': 3.0}
    
    # Generate and save audio (lazy)
    path = generate_and_save_audio(
        media_id=media_id,
        audio_type=audio_type,
        **kwargs
    )
    
    if not path.exists():
        return HttpResponseNotFound("Audio generation failed")
    
    return FileResponse(open(path, 'rb'), content_type='audio/wav')


@api_view(['GET'])
def generated_media_spectrogram(request, media_id):
    """
    Serve generated spectrogram image (lazy generation).
    
    GET /api/v1/generated-media/{media_id}/spectrogram/
    """
    # Determine audio type from media_id
    if 'tapping' in media_id:
        audio_type = 'tapping'
        kwargs = {'num_taps': 5}
    elif 'knocking' in media_id:
        audio_type = 'knocking'
        kwargs = {'num_knocks': 3}
    elif 'voice' in media_id:
        audio_type = 'voice_like'
        kwargs = {}
    else:
        audio_type = 'ambient'
        kwargs = {'environment': 'cave'}
    
    # Generate and save spectrogram (lazy)
    path = generate_and_save_spectrogram(
        media_id=media_id,
        audio_type=audio_type,
        **kwargs
    )
    
    if not path.exists():
        return HttpResponseNotFound("Spectrogram generation failed")
    
    return FileResponse(open(path, 'rb'), content_type='image/png')
