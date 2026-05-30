"""
Image generator for mission simulation media.

Generates synthetic still images using Pillow with mission context:
- Low-light scenes
- Underwater/murky images
- Thermal-style frames
- Industrial inspection views
- Dusty/degraded conditions
"""

import os
import random
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Base directory for generated media
GENERATED_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'media' / 'generated'


def ensure_media_dir():
    """Ensure the generated media directory exists."""
    GENERATED_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_MEDIA_DIR / 'images').mkdir(exist_ok=True)
    (GENERATED_MEDIA_DIR / 'audio').mkdir(exist_ok=True)
    (GENERATED_MEDIA_DIR / 'spectrograms').mkdir(exist_ok=True)


def get_image_path(media_id: str) -> Path:
    """Get the file path for a generated image."""
    ensure_media_dir()
    return GENERATED_MEDIA_DIR / 'images' / f'{media_id}.png'


def generate_base_noise_image(width=640, height=480, base_color=(40, 45, 50), noise_level=15):
    """Generate a noisy base image simulating sensor noise."""
    img = Image.new('RGB', (width, height), base_color)
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = base_color
            noise = random.randint(-noise_level, noise_level)
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
    
    return img


def add_gradient(img, start_color, end_color, direction='vertical'):
    """Add a gradient overlay to simulate lighting conditions."""
    width, height = img.size
    gradient = Image.new('RGB', (width, height), start_color)
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return Image.blend(img, gradient, alpha=0.3)


def add_annotations(img, annotations, confidence=None, signal_quality=None):
    """Add text annotations to image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Try to use a basic font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    draw.text((10, 10), timestamp, fill=(200, 200, 200), font=small_font)
    
    # Confidence and signal quality badges
    y_offset = 10
    if confidence is not None:
        conf_text = f'Confidence: {confidence}%'
        conf_color = (100, 200, 100) if confidence > 70 else (200, 200, 100) if confidence > 50 else (200, 100, 100)
        draw.text((width - 150, y_offset), conf_text, fill=conf_color, font=small_font)
        y_offset += 20
    
    if signal_quality is not None:
        sig_text = f'Signal: {signal_quality}%'
        sig_color = (100, 200, 100) if signal_quality > 70 else (200, 200, 100) if signal_quality > 50 else (200, 100, 100)
        draw.text((width - 150, y_offset), sig_text, fill=sig_color, font=small_font)
    
    # Annotations at bottom
    if annotations:
        y_pos = height - 30
        for annotation in annotations[:2]:  # Limit to 2 annotations
            draw.rectangle([(10, y_pos - 5), (len(annotation) * 8 + 20, y_pos + 20)], 
                          fill=(0, 0, 0), outline=(255, 165, 0))
            draw.text((15, y_pos), annotation, fill=(255, 165, 0), font=font)
            y_pos -= 30


def generate_low_light_image(media_id, sector_label, annotations=None, confidence=None, signal_quality=None):
    """Generate a low-light/dark scene image."""
    img = generate_base_noise_image(base_color=(20, 22, 25), noise_level=25)
    
    # Add some faint light sources
    draw = ImageDraw.Draw(img, 'RGBA')
    width, height = img.size
    
    # Simulated light source
    light_x = random.randint(width // 4, 3 * width // 4)
    light_y = random.randint(height // 4, height // 2)
    for radius in range(80, 0, -10):
        alpha = int(30 * (1 - radius / 80))
        draw.ellipse(
            [(light_x - radius, light_y - radius), (light_x + radius, light_y + radius)],
            fill=(120, 110, 80, alpha)
        )
    
    # Add some random bright spots (dust particles in light)
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse([(x, y), (x + size, y + size)], fill=(brightness, brightness, brightness - 20))
    
    add_annotations(img, annotations or [], confidence, signal_quality)
    
    return img


def generate_thermal_image(media_id, sector_label, annotations=None, confidence=None, signal_quality=None, hotspot=False):
    """Generate a thermal camera style image."""
    img = generate_base_noise_image(base_color=(20, 10, 40), noise_level=20)
    
    # Apply thermal color gradient
    img = add_gradient(img, (20, 10, 60), (60, 20, 80), 'vertical')
    
    draw = ImageDraw.Draw(img, 'RGBA')
    width, height = img.size
    
    # Add thermal hotspot if requested
    if hotspot or random.random() > 0.5:
        hot_x = random.randint(width // 3, 2 * width // 3)
        hot_y = random.randint(height // 3, 2 * height // 3)
        
        # Create hotspot gradient
        for radius in range(60, 0, -5):
            ratio = 1 - (radius / 60)
            alpha = int(150 * ratio)
            # Transition from purple to red to yellow
            if ratio < 0.5:
                color = (int(100 + 155 * ratio * 2), int(10 + 40 * ratio * 2), 80 - int(80 * ratio * 2), alpha)
            else:
                adjusted_ratio = (ratio - 0.5) * 2
                color = (255, int(50 + 205 * adjusted_ratio), int(10 - 10 * adjusted_ratio), alpha)
            
            draw.ellipse(
                [(hot_x - radius, hot_y - radius), (hot_x + radius, hot_y + radius)],
                fill=color
            )
        
        # Draw crosshair on hotspot
        draw.line([(hot_x - 20, hot_y), (hot_x + 20, hot_y)], fill=(255, 255, 0), width=2)
        draw.line([(hot_x, hot_y - 20), (hot_x, hot_y + 20)], fill=(255, 255, 0), width=2)
    
    add_annotations(img, annotations or [], confidence, signal_quality)
    
    return img


def generate_underwater_image(media_id, sector_label, annotations=None, confidence=None, signal_quality=None):
    """Generate an underwater/murky image."""
    img = generate_base_noise_image(base_color=(10, 35, 45), noise_level=30)
    
    # Add blue-green tint
    img = add_gradient(img, (5, 30, 40), (15, 45, 55), 'vertical')
    
    # Apply blur for murkiness
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    draw = ImageDraw.Draw(img, 'RGBA')
    width, height = img.size
    
    # Add floating particles
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 6)
        alpha = random.randint(100, 200)
        draw.ellipse([(x, y), (x + size, y + size)], fill=(200, 200, 190, alpha))
    
    # Add light rays from above
    for i in range(3):
        x_start = random.randint(0, width)
        for y in range(0, height, 5):
            alpha = int(20 * (1 - y / height))
            width_ray = int(10 + y / 20)
            x_offset = random.randint(-5, 5)
            draw.line([(x_start + x_offset, y), (x_start + x_offset, y + 5)], 
                     fill=(150, 180, 200, alpha), width=width_ray)
    
    add_annotations(img, annotations or [], confidence, signal_quality)
    
    return img


def generate_industrial_image(media_id, sector_label, annotations=None, confidence=None, signal_quality=None):
    """Generate an industrial inspection image (pipes, metal surfaces)."""
    img = generate_base_noise_image(base_color=(60, 55, 50), noise_level=15)
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Draw some pipe-like structures
    for i in range(3):
        y_pos = random.randint(height // 4, 3 * height // 4)
        pipe_height = random.randint(30, 50)
        draw.rectangle(
            [(0, y_pos), (width, y_pos + pipe_height)],
            fill=(80, 75, 70),
            outline=(100, 95, 90)
        )
        
        # Add rust/corrosion spots
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, width)
            spot_y = y_pos + random.randint(0, pipe_height)
            spot_size = random.randint(5, 15)
            draw.ellipse(
                [(x, spot_y), (x + spot_size, spot_y + spot_size)],
                fill=(120, 60, 30)
            )
    
    add_annotations(img, annotations or [], confidence, signal_quality)
    
    return img


def generate_dusty_rubble_image(media_id, sector_label, annotations=None, confidence=None, signal_quality=None):
    """Generate a dusty rubble/collapsed structure image."""
    img = generate_base_noise_image(base_color=(45, 40, 35), noise_level=25)
    
    # Apply slight blur for dust
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    
    draw = ImageDraw.Draw(img, 'RGBA')
    width, height = img.size
    
    # Add dust particles
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 4)
        alpha = random.randint(50, 150)
        brightness = random.randint(150, 220)
        draw.ellipse([(x, y), (x + size, y + size)], 
                    fill=(brightness, brightness - 10, brightness - 20, alpha))
    
    # Add some angular rubble shapes
    for _ in range(5):
        points = []
        base_x = random.randint(0, width)
        base_y = random.randint(height // 2, height)
        for _ in range(random.randint(3, 5)):
            points.append((
                base_x + random.randint(-50, 50),
                base_y + random.randint(-40, 10)
            ))
        if len(points) >= 3:
            shade = random.randint(30, 70)
            draw.polygon(points, fill=(shade, shade - 5, shade - 10))
    
    add_annotations(img, annotations or [], confidence, signal_quality)
    
    return img


def generate_last_good_frame(media_id, sector_label, sensor_type='camera'):
    """Generate a 'last good frame' with signal degradation effects."""
    # Start with a base image type based on sensor
    if sensor_type == 'thermal':
        img = generate_thermal_image(media_id, sector_label)
    elif sensor_type == 'underwater':
        img = generate_underwater_image(media_id, sector_label)
    else:
        img = generate_low_light_image(media_id, sector_label)
    
    # Add severe degradation effects
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    
    # Add scan lines / corruption
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    for y in range(0, height, random.randint(10, 30)):
        if random.random() > 0.5:
            draw.rectangle([(0, y), (width, y + random.randint(2, 5))], fill=(0, 0, 0))
    
    # Add "SIGNAL LOST" overlay
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "SIGNAL LOST"
    draw.text((width // 2 - 80, height // 2 - 20), text, fill=(255, 50, 50), font=font)
    draw.text((10, height - 30), "Last good frame", fill=(255, 50, 50), font=font)
    
    return img


def generate_image(media_id, media_type, sector_label, sensor_type='camera', 
                  annotations=None, confidence=None, signal_quality=None, **kwargs):
    """
    Generate an image based on media type and context.
    
    Args:
        media_id: Unique identifier for the media
        media_type: Type of image (low_light, thermal, underwater, industrial, dusty_rubble, last_frame)
        sector_label: Mission sector label
        sensor_type: Type of sensor capturing the image
        annotations: List of text annotations
        confidence: Confidence percentage (0-100)
        signal_quality: Signal quality percentage (0-100)
    
    Returns:
        PIL Image object
    """
    if media_type == 'thermal':
        return generate_thermal_image(media_id, sector_label, annotations, confidence, signal_quality, 
                                     hotspot=kwargs.get('hotspot', False))
    elif media_type == 'underwater':
        return generate_underwater_image(media_id, sector_label, annotations, confidence, signal_quality)
    elif media_type == 'industrial':
        return generate_industrial_image(media_id, sector_label, annotations, confidence, signal_quality)
    elif media_type == 'dusty_rubble':
        return generate_dusty_rubble_image(media_id, sector_label, annotations, confidence, signal_quality)
    elif media_type == 'last_frame':
        return generate_last_good_frame(media_id, sector_label, sensor_type)
    else:  # default to low_light
        return generate_low_light_image(media_id, sector_label, annotations, confidence, signal_quality)


def save_generated_image(media_id, img):
    """Save generated image to disk."""
    path = get_image_path(media_id)
    img.save(path, 'PNG')
    return path


def generate_and_save_image(media_id, media_type, sector_label, sensor_type='camera',
                            annotations=None, confidence=None, signal_quality=None, **kwargs):
    """Generate and save an image if it doesn't already exist."""
    path = get_image_path(media_id)
    
    if path.exists():
        return path
    
    img = generate_image(media_id, media_type, sector_label, sensor_type, 
                        annotations, confidence, signal_quality, **kwargs)
    return save_generated_image(media_id, img)
