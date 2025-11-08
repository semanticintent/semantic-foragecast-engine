#!/usr/bin/env python3
"""
Create sample assets for testing the video pipeline.

Generates:
- song.wav: 30-second test audio with varying tones
- fox.png: Simple placeholder image for mascot

Author: Claude (Anthropic)
Version: 1.0
"""

import os
import numpy as np
import soundfile as sf

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("WARNING: PIL not installed. Install with: pip install pillow")
    Image = None


def create_sample_audio():
    """Create a 30-second sample audio file with musical variation."""
    print("Generating sample audio (song.wav)...")

    duration = 30.0  # seconds
    sample_rate = 22050  # Hz

    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Create a musical progression (simple chord changes)
    # Using different frequencies to simulate chord changes
    audio = np.zeros_like(t)

    # Chord progression: I - IV - V - I (in C major)
    chords = [
        (0, 8, [261.63, 329.63, 392.00]),    # C major (C-E-G)
        (8, 16, [349.23, 440.00, 523.25]),   # F major (F-A-C)
        (16, 24, [392.00, 493.88, 587.33]),  # G major (G-B-D)
        (24, 30, [261.63, 329.63, 392.00]),  # C major (C-E-G)
    ]

    for start, end, frequencies in chords:
        mask = (t >= start) & (t < end)
        chord_audio = np.zeros_like(t)

        for freq in frequencies:
            chord_audio += np.sin(2 * np.pi * freq * t) / len(frequencies)

        audio[mask] = chord_audio[mask]

    # Add rhythm (beats every 0.5 seconds)
    beat_interval = 0.5
    for beat_time in np.arange(0, duration, beat_interval):
        beat_idx = int(beat_time * sample_rate)
        if beat_idx < len(audio) - 2000:
            # Percussive hit
            burst_length = 2000
            decay = np.exp(-np.arange(burst_length) / 300)
            burst = np.sin(2 * np.pi * 200 * np.arange(burst_length) / sample_rate) * decay
            audio[beat_idx:beat_idx + burst_length] += burst * 0.5

    # Add bass line
    bass_freq = 65.41  # C2
    bass = np.sin(2 * np.pi * bass_freq * t) * 0.3
    audio += bass

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.7

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'song.wav')
    sf.write(output_path, audio, sample_rate)

    file_size = os.path.getsize(output_path)
    print(f"✓ Created: {output_path}")
    print(f"  Duration: {duration}s, Size: {file_size:,} bytes")


def create_sample_image():
    """Create a simple placeholder image for the mascot."""
    if Image is None:
        print("Skipping image generation (PIL not installed)")
        return

    print("Generating sample mascot image (fox.png)...")

    # Create 512x512 image
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color=(255, 200, 100))  # Orange background

    draw = ImageDraw.Draw(img)

    # Draw a simple fox face
    # Ears
    draw.polygon([(150, 100), (200, 50), (220, 150)], fill=(255, 140, 0))  # Left ear
    draw.polygon([(362, 100), (312, 50), (292, 150)], fill=(255, 140, 0))  # Right ear

    # Face
    draw.ellipse([150, 150, 362, 400], fill=(255, 160, 60))  # Main face

    # Eyes
    draw.ellipse([190, 220, 230, 270], fill=(255, 255, 255))  # Left eye white
    draw.ellipse([200, 235, 220, 260], fill=(0, 0, 0))        # Left eye pupil

    draw.ellipse([282, 220, 322, 270], fill=(255, 255, 255))  # Right eye white
    draw.ellipse([292, 235, 312, 260], fill=(0, 0, 0))        # Right eye pupil

    # Snout
    draw.ellipse([220, 280, 292, 330], fill=(255, 220, 180))

    # Nose
    draw.ellipse([240, 300, 272, 320], fill=(0, 0, 0))

    # Mouth
    draw.arc([210, 310, 302, 350], start=0, end=180, fill=(0, 0, 0), width=3)

    # Add text
    try:
        draw.text((150, 420), "SAMPLE FOX", fill=(0, 0, 0))
    except:
        pass  # Font might not be available

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'fox.png')
    img.save(output_path)

    file_size = os.path.getsize(output_path)
    print(f"✓ Created: {output_path}")
    print(f"  Size: {width}x{height}, {file_size:,} bytes")


def main():
    print("=" * 70)
    print("CREATING SAMPLE ASSETS")
    print("=" * 70)
    print()

    create_sample_audio()
    print()
    create_sample_image()

    print()
    print("=" * 70)
    print("✓ Sample assets created successfully")
    print("=" * 70)
    print()
    print("Files created:")
    print("  - assets/song.wav (30s audio)")
    print("  - assets/fox.png (512x512 image)")
    print("  - assets/lyrics.txt (already exists)")
    print()


if __name__ == '__main__':
    main()
