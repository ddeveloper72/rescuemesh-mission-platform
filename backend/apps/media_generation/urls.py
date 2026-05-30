"""
URLs for generated media API endpoints.
"""

from django.urls import path
from . import views

app_name = 'media_generation'

urlpatterns = [
    # Mission media list
    path('missions/<str:mission_id>/generated-media/',
         views.mission_generated_media_list,
         name='mission-generated-media-list'),
    
    # Individual media endpoints
    path('generated-media/<str:media_id>/preview/',
         views.generated_media_preview,
         name='generated-media-preview'),
    
    path('generated-media/<str:media_id>/audio/',
         views.generated_media_audio,
         name='generated-media-audio'),
    
    path('generated-media/<str:media_id>/spectrogram/',
         views.generated_media_spectrogram,
         name='generated-media-spectrogram'),
]
