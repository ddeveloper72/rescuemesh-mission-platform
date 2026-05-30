"""
Audio generator for mission simulation media.

Generates synthetic audio clips using Python's wave module:
- Knocking/tapping sounds
- Voice-like placeholder audio
- Static/noise
- Ambient cave/water sounds
"""

import wave
import struct
import math
import random
from pathlib import Path


# Base directory for generated media
GENERATED_MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'media' / 'generated'


def ensure_media_dir():
    """Ensure the generated media directory exists."""
    GENERATED_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_MEDIA_DIR / 'audio').mkdir(exist_ok=True)


def get_audio_path(media_id: str) -> Path:
    """Get the file path for a generated audio file."""
    ensure_media_dir()
    return GENERATED_MEDIA_DIR / 'audio' / f'{media_id}.wav'


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generate a sine wave."""
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        samples.append(sample)
    
    return samples


def generate_noise(duration, sample_rate=44100, amplitude=0.3):
    """Generate white noise."""
    num_samples = int(duration * sample_rate)
    samples = []
    
    for _ in range(num_samples):
        sample = amplitude * random.uniform(-1, 1)
        samples.append(sample)
    
    return samples


def apply_envelope(samples, attack=0.01, decay=0.05, sustain_level=0.7, release=0.1, sample_rate=44100):
    """Apply ADSR envelope to samples."""
    total_samples = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    if sustain_samples < 0:
        sustain_samples = 0
    
    enveloped = []
    
    for i, sample in enumerate(samples):
        envelope = 1.0
        
        if i < attack_samples:
            # Attack phase
            envelope = i / attack_samples
        elif i < attack_samples + decay_samples:
            # Decay phase
            progress = (i - attack_samples) / decay_samples
            envelope = 1.0 - (1.0 - sustain_level) * progress
        elif i < attack_samples + decay_samples + sustain_samples:
            # Sustain phase
            envelope = sustain_level
        else:
            # Release phase
            release_progress = (i - attack_samples - decay_samples - sustain_samples) / release_samples
            envelope = sustain_level * (1.0 - release_progress)
        
        enveloped.append(sample * envelope)
    
    return enveloped


def samples_to_wav_data(samples, sample_rate=44100):
    """Convert floating-point samples to WAV format."""
    wav_data = []
    for sample in samples:
        # Clamp to [-1, 1]
        sample = max(-1.0, min(1.0, sample))
        # Convert to 16-bit integer
        int_sample = int(sample * 32767)
        wav_data.append(struct.pack('<h', int_sample))
    
    return b''.join(wav_data)


def write_wav_file(path, wav_data, sample_rate=44100):
    """Write WAV data to file."""
    with wave.open(str(path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wav_data)


def generate_knocking_audio(media_id, num_knocks=3, interval=0.5):
    """Generate knocking sound (sharp impulses)."""
    sample_rate = 44100
    samples = []
    
    for i in range(num_knocks):
        # Generate a short impulse with multiple frequencies
        knock_duration = 0.05
        knock_samples = []
        
        # Combine multiple frequencies for richer knock sound
        for freq in [150, 200, 250, 350]:
            amplitude = 0.2 / (freq / 150)  # Lower amplitude for higher frequencies
            wave_samples = generate_sine_wave(freq, knock_duration, sample_rate, amplitude)
            if not knock_samples:
                knock_samples = wave_samples
            else:
                knock_samples = [a + b for a, b in zip(knock_samples, wave_samples)]
        
        # Apply sharp envelope
        knock_samples = apply_envelope(knock_samples, attack=0.001, decay=0.02, 
                                      sustain_level=0.3, release=0.03, sample_rate=sample_rate)
        
        samples.extend(knock_samples)
        
        # Add silence between knocks
        if i < num_knocks - 1:
            silence_duration = interval
            samples.extend([0.0] * int(silence_duration * sample_rate))
    
    # Add some ambient noise
    noise = generate_noise(len(samples) / sample_rate, sample_rate, amplitude=0.05)
    samples = [s + n for s, n in zip(samples, noise)]
    
    return samples


def generate_tapping_audio(media_id, num_taps=5, tempo='regular'):
    """Generate tapping sound (lighter than knocking)."""
    sample_rate = 44100
    samples = []
    
    # Determine intervals
    if tempo == 'regular':
        intervals = [0.4] * num_taps
    elif tempo == 'sos':
        # SOS pattern: 3 short, 3 long, 3 short
        intervals = [0.3, 0.3, 0.3, 0.6, 0.6, 0.6, 0.3, 0.3, 0.3]
        num_taps = len(intervals)
    else:
        intervals = [random.uniform(0.3, 0.7) for _ in range(num_taps)]
    
    for i in range(num_taps):
        # Generate a very short impulse
        tap_duration = 0.03
        tap_samples = []
        
        # Higher frequencies for tap
        for freq in [800, 1200, 1600]:
            amplitude = 0.15 / (freq / 800)
            wave_samples = generate_sine_wave(freq, tap_duration, sample_rate, amplitude)
            if not tap_samples:
                tap_samples = wave_samples
            else:
                tap_samples = [a + b for a, b in zip(tap_samples, wave_samples)]
        
        # Very sharp envelope
        tap_samples = apply_envelope(tap_samples, attack=0.001, decay=0.01, 
                                    sustain_level=0.2, release=0.02, sample_rate=sample_rate)
        
        samples.extend(tap_samples)
        
        # Add silence
        if i < num_taps - 1:
            silence_duration = intervals[i] if i < len(intervals) else 0.4
            samples.extend([0.0] * int(silence_duration * sample_rate))
    
    # Add ambient noise
    noise = generate_noise(len(samples) / sample_rate, sample_rate, amplitude=0.03)
    samples = [s + n for s, n in zip(samples, noise)]
    
    return samples


def generate_voice_like_audio(media_id, duration=2.0):
    """Generate voice-like placeholder audio (modulated noise and tones)."""
    sample_rate = 44100
    samples = []
    
    # Generate multiple frequency bands to simulate voice
    num_segments = random.randint(3, 6)
    segment_duration = duration / num_segments
    
    for _ in range(num_segments):
        # Random fundamental frequency in voice range
        fundamental = random.uniform(100, 300)
        
        segment_samples = []
        
        # Add fundamental and harmonics
        for harmonic in [1, 2, 3, 4]:
            freq = fundamental * harmonic
            amplitude = 0.15 / harmonic
            wave = generate_sine_wave(freq, segment_duration, sample_rate, amplitude)
            if not segment_samples:
                segment_samples = wave
            else:
                segment_samples = [a + b for a, b in zip(segment_samples, wave)]
        
        # Add some noise for "breathiness"
        noise = generate_noise(segment_duration, sample_rate, amplitude=0.1)
        segment_samples = [s + n for s, n in zip(segment_samples, noise)]
        
        # Apply envelope to simulate syllables
        segment_samples = apply_envelope(segment_samples, attack=0.05, decay=0.1,
                                        sustain_level=0.6, release=0.05, sample_rate=sample_rate)
        
        samples.extend(segment_samples)
        
        # Small pause between segments
        if _ < num_segments - 1:
            samples.extend([0.0] * int(0.1 * sample_rate))
    
    return samples


def generate_static_audio(media_id, duration=1.0, intensity='medium'):
    """Generate static/interference audio."""
    sample_rate = 44100
    
    amplitude = {
        'low': 0.2,
        'medium': 0.4,
        'high': 0.6
    }.get(intensity, 0.4)
    
    samples = generate_noise(duration, sample_rate, amplitude)
    
    # Add some low-frequency rumble
    rumble = generate_sine_wave(60, duration, sample_rate, amplitude * 0.3)
    samples = [s + r for s, r in zip(samples, rumble)]
    
    return samples


def generate_ambient_audio(media_id, duration=3.0, environment='cave'):
    """Generate ambient environmental audio."""
    sample_rate = 44100
    samples = []
    
    if environment == 'cave':
        # Low rumble + dripping sounds
        base_noise = generate_noise(duration, sample_rate, amplitude=0.05)
        rumble = generate_sine_wave(40, duration, sample_rate, amplitude=0.1)
        samples = [n + r for n, r in zip(base_noise, rumble)]
        
        # Add occasional drips
        num_drips = random.randint(2, 5)
        drip_times = sorted([random.uniform(0, duration) for _ in range(num_drips)])
        
        for drip_time in drip_times:
            drip_start = int(drip_time * sample_rate)
            drip_samples = generate_sine_wave(2000, 0.1, sample_rate, amplitude=0.15)
            drip_samples = apply_envelope(drip_samples, attack=0.001, decay=0.05,
                                         sustain_level=0, release=0.05, sample_rate=sample_rate)
            
            # Mix in the drip
            for i, drip_sample in enumerate(drip_samples):
                if drip_start + i < len(samples):
                    samples[drip_start + i] += drip_sample
    
    elif environment == 'underwater':
        # Muffled low frequencies
        base_noise = generate_noise(duration, sample_rate, amplitude=0.08)
        low_freq = generate_sine_wave(30, duration, sample_rate, amplitude=0.15)
        samples = [n + l for n, l in zip(base_noise, low_freq)]
    
    elif environment == 'industrial':
        # Machinery hum
        hum = generate_sine_wave(50, duration, sample_rate, amplitude=0.2)
        noise = generate_noise(duration, sample_rate, amplitude=0.1)
        samples = [h + n for h, n in zip(hum, noise)]
    
    else:
        # Generic ambient
        samples = generate_noise(duration, sample_rate, amplitude=0.06)
    
    return samples


def generate_audio(media_id, audio_type, **kwargs):
    """
    Generate audio based on type and context.
    
    Args:
        media_id: Unique identifier for the audio
        audio_type: Type of audio (knocking, tapping, voice_like, static, ambient)
        **kwargs: Additional parameters specific to audio type
    
    Returns:
        List of audio samples
    """
    if audio_type == 'knocking':
        return generate_knocking_audio(media_id, 
                                       num_knocks=kwargs.get('num_knocks', 3),
                                       interval=kwargs.get('interval', 0.5))
    elif audio_type == 'tapping':
        return generate_tapping_audio(media_id,
                                      num_taps=kwargs.get('num_taps', 5),
                                      tempo=kwargs.get('tempo', 'regular'))
    elif audio_type == 'voice_like':
        return generate_voice_like_audio(media_id, duration=kwargs.get('duration', 2.0))
    elif audio_type == 'static':
        return generate_static_audio(media_id, 
                                     duration=kwargs.get('duration', 1.0),
                                     intensity=kwargs.get('intensity', 'medium'))
    elif audio_type == 'ambient':
        return generate_ambient_audio(media_id,
                                      duration=kwargs.get('duration', 3.0),
                                      environment=kwargs.get('environment', 'cave'))
    else:
        # Default to simple tone
        return generate_sine_wave(440, 1.0)


def generate_and_save_audio(media_id, audio_type, sample_rate=44100, **kwargs):
    """Generate and save audio if it doesn't already exist."""
    path = get_audio_path(media_id)
    
    if path.exists():
        return path
    
    samples = generate_audio(media_id, audio_type, **kwargs)
    wav_data = samples_to_wav_data(samples, sample_rate)
    write_wav_file(path, wav_data, sample_rate)
    
    return path
