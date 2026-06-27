#!/usr/bin/env python3
"""
Sandbox Demo: Generate mock WAV and test prep_audio.py functions

This script:
1. Generates a 5-second test tone using numpy.sin
2. Creates mock lyrics
3. Runs all prep_audio functions
4. Prints JSON output

"""

import os
import sys
import json
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prep_audio import process_audio


def generate_mock_wav(duration=5.0, sample_rate=22050, frequency=440.0):
    """
    Generate a 5-second test tone WAV file using numpy.sin.

    Args:
        duration: Length in seconds
        sample_rate: Sample rate in Hz
        frequency: Tone frequency in Hz (default: A4 = 440Hz)

    Returns:
        Path to generated WAV file
    """
    print(f"Generating mock WAV: {duration}s @ {sample_rate}Hz, {frequency}Hz tone")

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate sine wave
    audio = np.sin(2 * np.pi * frequency * t)

    # Add some variation to make it interesting
    # Add harmonics
    audio += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # Octave
    audio += 0.15 * np.sin(2 * np.pi * frequency * 3 * t)  # Fifth

    # Add amplitude modulation (tremolo effect)
    tremolo = 0.7 + 0.3 * np.sin(2 * np.pi * 4 * t)
    audio = audio * tremolo

    # Add beat-like impulses every 0.5 seconds
    for beat_time in np.arange(0.5, duration, 0.5):
        beat_idx = int(beat_time * sample_rate)
        if beat_idx < len(audio) - 2000:
            # Short burst
            burst_length = 1000
            burst = np.sin(2 * np.pi * 880 * np.arange(burst_length) / sample_rate)
            burst *= np.exp(-np.arange(burst_length) / 200)  # Decay envelope
            audio[beat_idx:beat_idx + burst_length] += burst * 2.0

    # Normalize to prevent clipping
    audio = audio / np.max(np.abs(audio)) * 0.8

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        wav_path = tmp.name

    sf.write(wav_path, audio, sample_rate)

    file_size = os.path.getsize(wav_path)
    print(f"✓ Generated WAV: {wav_path}")
    print(f"  Size: {file_size:,} bytes")
    print(f"  Duration: {duration}s")
    print()

    return wav_path


def generate_mock_lyrics():
    """
    Generate mock lyrics file.

    Returns:
        Path to generated lyrics TXT file
    """
    print("Generating mock lyrics...")

    lyrics_content = """0:00-0:02 Hello|world|this|is
0:02-0:04 A|test|of|the
0:04-0:05 Pipeline"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write(lyrics_content)
        lyrics_path = tmp.name

    print(f"✓ Generated lyrics: {lyrics_path}")
    print(f"  Content:\n{lyrics_content}")
    print()

    return lyrics_path


def main():
    """Run sandbox demo."""
    print("="*70)
    print("SANDBOX DEMO: prep_audio.py")
    print("="*70)
    print()

    # Generate test assets
    wav_path = generate_mock_wav(duration=5.0)
    lyrics_path = generate_mock_lyrics()

    # Output path
    output_path = os.path.join(
        Path(__file__).parent.parent,
        'outputs',
        'sandbox_demo_output.json'
    )

    print("="*70)
    print("RUNNING AUDIO PROCESSING PIPELINE")
    print("="*70)
    print()

    # Process audio
    try:
        result = process_audio(
            audio_path=wav_path,
            lyrics_path=lyrics_path,
            rhubarb_path=None,  # Use mock phonemes
            output_json=output_path
        )

        print()
        print("="*70)
        print("RESULTS (JSON OUTPUT)")
        print("="*70)
        print()
        print(json.dumps(result, indent=2))
        print()

        print("="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Audio Duration:  {result['audio']['duration']}s")
        print(f"Sample Rate:     {result['audio']['sample_rate']} Hz")
        print(f"Tempo:           {result['audio']['tempo']:.1f} BPM")
        print(f"Beats Detected:  {len(result['beats']['beat_times'])}")
        print(f"Onsets Detected: {len(result['beats']['onset_times'])}")
        print(f"Phonemes:        {len(result['phonemes'])}")
        print(f"Timed Words:     {len(result['timed_words'])}")
        print()
        print(f"Output saved to: {output_path}")
        print("="*70)
        print()

        # Validate results
        print("VALIDATION")
        print("="*70)
        assert len(result['beats']['beat_times']) > 0, "Should detect at least one beat"
        assert len(result['beats']['onset_times']) > 0, "Should detect at least one onset"
        assert len(result['phonemes']) > 0, "Should generate phonemes"
        assert len(result['timed_words']) > 0, "Should parse lyrics"
        assert result['audio']['duration'] > 4.9, "Duration should be ~5s"
        print("✓ All assertions passed!")
        print()

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary files
        print("Cleaning up temporary files...")
        for path in [wav_path, lyrics_path]:
            if os.path.exists(path):
                os.unlink(path)
                print(f"  Deleted: {path}")
        print()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
