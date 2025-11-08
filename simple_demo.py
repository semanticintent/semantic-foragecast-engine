#!/usr/bin/env python3
"""
Simple Demo Asset Generator

Creates demo assets and runs Phase 1 preprocessing to demonstrate
the Semantic Foragecast Engine capabilities.

Author: Claude (Anthropic)
Version: 1.0
"""

import os
import sys
import json
import numpy as np

def create_demo_audio(output_path: str, duration: float = 10.0):
    """Create demo audio with beats."""
    print("\nCreating demo audio...")

    try:
        import soundfile as sf
    except ImportError:
        from scipy.io import wavfile
        sf = None

    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create upbeat melody
    freqs = [440, 554, 659, 880]  # A4, C#5, E5, A5
    audio = np.zeros_like(t)

    for i, freq in enumerate(freqs * 3):
        start = i * duration / 12
        end = (i + 1) * duration / 12
        mask = (t >= start) & (t < end)
        audio[mask] += 0.3 * np.sin(2 * np.pi * freq * t[mask])

    # Add beat impulses every 0.5s (120 BPM)
    for beat_time in np.arange(0, duration, 0.5):
        beat_idx = int(beat_time * sample_rate)
        if beat_idx < len(audio) - 2000:
            envelope = np.exp(-np.linspace(0, 5, 2000))
            burst = envelope * np.sin(2 * np.pi * 200 * np.linspace(0, 0.1, 2000))
            audio[beat_idx:beat_idx + 2000] += burst * 1.5

    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.9

    if sf:
        sf.write(output_path, audio, sample_rate)
    else:
        wavfile.write(output_path, sample_rate, (audio * 32767).astype(np.int16))

    print(f"✓ Created: {output_path}")
    print(f"  Duration: {duration}s @ {sample_rate} Hz")
    return output_path


def create_demo_image(output_path: str):
    """Create demo mascot image."""
    print("\nCreating demo mascot...")

    from PIL import Image, ImageDraw

    img = Image.new('RGB', (1024, 1024), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Draw colorful fox mascot
    # Head
    draw.ellipse([200, 200, 824, 824], fill=(255, 140, 0), outline=(0, 0, 0), width=5)

    # Ears
    draw.polygon([300, 200, 200, 100, 400, 160], fill=(255, 140, 0), outline=(0, 0, 0))
    draw.polygon([724, 200, 824, 100, 624, 160], fill=(255, 140, 0), outline=(0, 0, 0))

    # Inner ears
    draw.polygon([320, 190, 250, 140, 370, 180], fill=(255, 200, 150))
    draw.polygon([704, 190, 774, 140, 654, 180], fill=(255, 200, 150))

    # Eyes
    draw.ellipse([360, 400, 460, 540], fill=(0, 0, 0))
    draw.ellipse([564, 400, 664, 540], fill=(0, 0, 0))

    # Eye highlights
    draw.ellipse([390, 420, 430, 470], fill=(255, 255, 255))
    draw.ellipse([594, 420, 634, 470], fill=(255, 255, 255))

    # Nose
    draw.polygon([512, 560, 462, 620, 562, 620], fill=(0, 0, 0))

    # Mouth (smile)
    draw.arc([400, 560, 624, 700], 0, 180, fill=(0, 0, 0), width=5)

    img.save(output_path)

    print(f"✓ Created: {output_path}")
    print(f"  Resolution: 1024x1024")
    return output_path


def create_demo_lyrics(output_path: str):
    """Create demo lyrics."""
    print("\nCreating demo lyrics...")

    lyrics = """0:00-0:03 Welcome|to|Semantic|Foragecast
0:03-0:06 AI-powered|video|generation
0:06-0:10 Watch|the|magic|happen"""

    with open(output_path, 'w') as f:
        f.write(lyrics)

    print(f"✓ Created: {output_path}")
    return output_path


def run_preprocessing_demo(audio_path: str, lyrics_path: str):
    """Run Phase 1 preprocessing and show results."""
    print("\n" + "="*70)
    print("Running Phase 1: Audio Preprocessing")
    print("="*70)

    from prep_audio import AudioPreprocessor, PhonemeExtractor, LyricsParser

    # Audio preprocessing
    print("\n1. Audio Analysis...")
    processor = AudioPreprocessor(sample_rate=22050)
    y, sr = processor.load_audio(audio_path)
    beat_data = processor.detect_beats(y, sr)

    duration = len(y) / sr
    print(f"   Duration: {duration:.2f}s")
    print(f"   Tempo: {beat_data['tempo']:.1f} BPM")
    print(f"   Beats: {len(beat_data['beat_times'])}")
    print(f"   Onsets: {len(beat_data['onset_times'])}")

    # Phoneme extraction
    print("\n2. Phoneme Extraction...")
    extractor = PhonemeExtractor(rhubarb_path=None)
    phonemes = extractor.extract_phonemes(audio_path)
    print(f"   Phonemes: {len(phonemes)}")
    print(f"   First 5: {[p['phoneme'] for p in phonemes[:5]]}")

    # Lyrics parsing
    print("\n3. Lyrics Parsing...")
    lyrics = LyricsParser.parse_lyrics(lyrics_path)
    print(f"   Words: {len(lyrics)}")
    print(f"   First 5: {[w['word'] for w in lyrics[:5]]}")

    # Create prep data JSON
    prep_data = {
        'audio': {
            'duration': duration,
            'sample_rate': sr,
            'tempo': beat_data['tempo'],
            'beat_times': beat_data['beat_times'].tolist() if hasattr(beat_data['beat_times'], 'tolist') else beat_data['beat_times'],
            'onset_times': beat_data['onset_times'].tolist() if hasattr(beat_data['onset_times'], 'tolist') else beat_data['onset_times']
        },
        'phonemes': phonemes,
        'lyrics': lyrics
    }

    return prep_data


def main():
    print("="*70)
    print("Semantic Foragecast Engine - Simple Demo")
    print("="*70)

    # Create output directory
    output_dir = "demo_reel"
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Create assets
    print("\n" + "="*70)
    print("STEP 1: Creating Demo Assets")
    print("="*70)

    audio_path = create_demo_audio(
        os.path.join(assets_dir, "demo_song.wav"),
        duration=10.0
    )

    image_path = create_demo_image(
        os.path.join(assets_dir, "demo_fox.png")
    )

    lyrics_path = create_demo_lyrics(
        os.path.join(assets_dir, "demo_lyrics.txt")
    )

    # Run preprocessing
    try:
        prep_data = run_preprocessing_demo(audio_path, lyrics_path)

        # Save prep data
        prep_json_path = os.path.join(output_dir, "prep_data.json")
        with open(prep_json_path, 'w') as f:
            json.dump(prep_data, f, indent=2)

        print(f"\n✓ Saved prep data: {prep_json_path}")

    except Exception as e:
        print(f"\n⚠ Preprocessing failed: {e}")

    # Summary
    print("\n" + "="*70)
    print("✅ Demo Assets Created Successfully!")
    print("="*70)
    print(f"\nOutput directory: {output_dir}/")
    print("\nGenerated files:")
    print(f"  • {audio_path}")
    print(f"  • {image_path}")
    print(f"  • {lyrics_path}")
    print(f"  • {output_dir}/prep_data.json")

    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("\n1. View the generated assets in the demo_reel/ directory")
    print("\n2. Run the full pipeline with Blender:")
    print("   $ python main.py --config config.yaml")
    print("\n3. For video export, install FFmpeg:")
    print("   $ sudo apt-get install ffmpeg  # Linux")
    print("   $ brew install ffmpeg          # macOS")
    print("\n4. Generate a complete demo reel:")
    print("   $ python create_demo_reel.py")
    print("\nNote: This demo shows Phase 1 (preprocessing) only.")
    print("Full rendering requires Blender installation.")
    print("="*70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
