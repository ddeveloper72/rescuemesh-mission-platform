"""
Spectrogram generator for audio visualization.

Generates visual representations of audio clips as spectrograms using Pillow.
Provides a simplified spectrogram visualization without requiring matplotlib or scipy.
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# Base directory for generated media
GENERATED_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'media' / 'generated'


def ensure_media_dir():
    """Ensure the generated media directory exists."""
    GENERATED_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_MEDIA_DIR / 'spectrograms').mkdir(exist_ok=True)


def get_spectrogram_path(media_id: str) -> Path:
    """Get the file path for a generated spectrogram."""
    ensure_media_dir()
    return GENERATED_MEDIA_DIR / 'spectrograms' / f'{media_id}_spec.png'


def generate_spectrogram_visualization(media_id, audio_type, width=640, height=240, **kwargs):
    """
    Generate a simplified spectrogram visualization.
    
    This creates a stylized representation that looks like a spectrogram
    without requiring actual FFT analysis.
    """
    # Create black background
    img = Image.new('RGB', (width, height), (10, 10, 15))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Draw frequency axis labels
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except:
        font = ImageFont.load_default()
    
    # Frequency labels (vertical axis)
    for i, freq in enumerate(['8k', '4k', '2k', '1k', '500', '250', '125']):
        y = int(i * height / 7)
        draw.text((5, y), freq, fill=(100, 100, 100), font=font)
    
    # Time axis
    draw.line([(50, height - 20), (width - 10, height - 20)], fill=(80, 80, 80))
    draw.text((10, height - 18), '0s', fill=(100, 100, 100), font=font)
    draw.text((width - 30, height - 18), f'{int(width/100)}s', fill=(100, 100, 100), font=font)
    
    # Generate spectrogram pattern based on audio type
    start_x = 50
    end_x = width - 10
    start_y = 10
    end_y = height - 30
    
    if audio_type == 'knocking':
        # Sharp vertical impulses
        num_knocks = kwargs.get('num_knocks', 3)
        knock_spacing = (end_x - start_x) / (num_knocks + 1)
        
        for i in range(num_knocks):
            x = int(start_x + knock_spacing * (i + 1))
            
            # Draw impulse across multiple frequencies
            for freq_y in range(start_y, end_y, 2):
                intensity = random.randint(150, 255) if freq_y < end_y * 0.6 else random.randint(50, 150)
                color = (intensity, intensity // 2, 0)  # Orange-red
                draw.rectangle([(x - 2, freq_y), (x + 2, freq_y + 2)], fill=color)
    
    elif audio_type == 'tapping':
        # Thinner, sharper impulses at higher frequencies
        num_taps = kwargs.get('num_taps', 5)
        tap_spacing = (end_x - start_x) / (num_taps + 1)
        
        for i in range(num_taps):
            x = int(start_x + tap_spacing * (i + 1))
            
            # Higher frequency focus
            for freq_y in range(start_y, end_y // 2, 2):
                intensity = random.randint(150, 255)
                color = (intensity, intensity, intensity // 2)  # Yellow-white
                draw.rectangle([(x - 1, freq_y), (x + 1, freq_y + 2)], fill=color)
    
    elif audio_type == 'voice_like':
        # Complex horizontal bands with variations (formants)
        num_segments = random.randint(3, 6)
        segment_width = (end_x - start_x) / num_segments
        
        for seg in range(num_segments):
            seg_start = int(start_x + seg * segment_width)
            seg_end = int(seg_start + segment_width)
            
            # Fundamental frequency band (low)
            base_y = random.randint(end_y - 80, end_y - 40)
            for x in range(seg_start, seg_end, 2):
                for y_offset in range(-10, 10):
                    y = base_y + y_offset
                    if start_y < y < end_y:
                        intensity = random.randint(100, 200)
                        draw.point((x, y), fill=(intensity, intensity // 2, intensity // 3))
            
            # Formant bands (higher frequencies)
            for formant in range(2):
                formant_y = random.randint(start_y + 40, end_y - 100)
                for x in range(seg_start, seg_end, 2):
                    for y_offset in range(-5, 5):
                        y = formant_y + y_offset
                        if start_y < y < end_y:
                            intensity = random.randint(80, 150)
                            draw.point((x, y), fill=(intensity, intensity // 2, intensity // 4))
    
    elif audio_type == 'static':
        # Random noise across all frequencies
        intensity_level = kwargs.get('intensity', 'medium')
        base_intensity = {'low': 50, 'medium': 100, 'high': 150}.get(intensity_level, 100)
        
        for x in range(start_x, end_x, 2):
            for y in range(start_y, end_y, 2):
                if random.random() > 0.3:  # 70% fill
                    intensity = random.randint(base_intensity - 30, base_intensity + 30)
                    draw.point((x, y), fill=(intensity, intensity, intensity))
    
    elif audio_type == 'ambient':
        # Low-frequency continuous bands
        environment = kwargs.get('environment', 'cave')
        
        if environment == 'cave':
            # Low rumble + sparse drip sounds
            for x in range(start_x, end_x):
                # Low frequency rumble
                for y in range(end_y - 40, end_y):
                    intensity = random.randint(60, 120)
                    draw.point((x, y), fill=(intensity // 2, intensity // 2, intensity))
                
                # Occasional drip (high frequency impulse)
                if random.random() > 0.98:
                    drip_y = random.randint(start_y, start_y + 50)
                    for dy in range(10):
                        draw.point((x, drip_y + dy), fill=(150, 150, 200))
        
        elif environment == 'underwater':
            # Muffled, low frequencies only
            for x in range(start_x, end_x):
                for y in range(end_y - 60, end_y):
                    if random.random() > 0.2:
                        intensity = random.randint(40, 100)
                        draw.point((x, y), fill=(intensity // 3, intensity // 2, intensity))
        
        elif environment == 'industrial':
            # Strong harmonic bands (machinery)
            for harmonic in range(4):
                harmonic_y = end_y - 80 - (harmonic * 30)
                for x in range(start_x, end_x):
                    intensity = random.randint(80, 150) - (harmonic * 20)
                    for y_offset in range(-3, 3):
                        y = harmonic_y + y_offset + random.randint(-2, 2)
                        if start_y < y < end_y:
                            draw.point((x, y), fill=(intensity, intensity // 2, 0))
    
    else:
        # Default: simple tone
        tone_y = end_y // 2
        for x in range(start_x, end_x):
            for y_offset in range(-5, 5):
                y = tone_y + y_offset
                intensity = 150
                draw.point((x, y), fill=(intensity, intensity, intensity))
    
    # Add title
    try:
        title_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = font
    
    title = f"Audio Spectrogram: {audio_type.replace('_', ' ').title()}"
    draw.text((width // 2 - 100, 5), title, fill=(200, 200, 200), font=title_font)
    
    return img


def generate_and_save_spectrogram(media_id, audio_type, **kwargs):
    """Generate and save spectrogram if it doesn't already exist."""
    path = get_spectrogram_path(media_id)
    
    if path.exists():
        return path
    
    img = generate_spectrogram_visualization(media_id, audio_type, **kwargs)
    img.save(path, 'PNG')
    
    return path
