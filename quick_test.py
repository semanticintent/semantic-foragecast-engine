#!/usr/bin/env python3
"""
Quick Test Script - Full Pipeline
Tests complete automation with low-resolution fast rendering.

This script:
1. Optionally generates lyrics using Whisper (or uses existing)
2. Runs Phase 1 (audio prep)
3. Runs Phase 2 (Blender rendering)
4. Runs Phase 3 (video export)
5. Reports timing and output location

Usage:
    # Use existing lyrics.txt
    python quick_test.py

    # Auto-generate lyrics with Whisper
    python quick_test.py --auto-lyrics

    # Use custom config
    python quick_test.py --config config_quick_test.yaml

    # Skip lyrics generation
    python quick_test.py --no-lyrics
"""

import argparse
import os
import sys
import time
import subprocess
from pathlib import Path


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print error message."""
    print(f"✗ ERROR: {message}")


def check_file_exists(path, description):
    """Check if required file exists."""
    if not os.path.exists(path):
        print_error(f"{description} not found: {path}")
        return False
    print_success(f"{description} found: {path}")
    return True


def run_command(cmd, description, timeout=600):
    """
    Run a command and report results.

    Args:
        cmd: Command list for subprocess
        description: Human-readable description
        timeout: Timeout in seconds (default 10 minutes)

    Returns:
        True if successful, False otherwise
    """
    print(f"\n▶ {description}...")
    print(f"  Command: {' '.join(cmd)}")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print_success(f"Completed in {elapsed:.1f}s")
            if result.stdout:
                # Show last few lines of output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 5:
                    print("  Output (last 5 lines):")
                    for line in lines[-5:]:
                        print(f"    {line}")
            return True
        else:
            print_error(f"Failed (exit code {result.returncode})")
            if result.stderr:
                print("  Error output:")
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_error(f"Timeout after {timeout}s")
        return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Quick test of full pipeline with low-res rendering'
    )
    parser.add_argument(
        '--config',
        default='config_quick_test.yaml',
        help='Config file to use (default: config_quick_test.yaml)'
    )
    parser.add_argument(
        '--auto-lyrics',
        action='store_true',
        help='Auto-generate lyrics using Whisper'
    )
    parser.add_argument(
        '--no-lyrics',
        action='store_true',
        help='Skip lyrics (test without lyrics display)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug visualization mode'
    )

    args = parser.parse_args()

    print_header("QUICK TEST - FULL PIPELINE")

    overall_start = time.time()

    # Check prerequisites
    print("Checking prerequisites...")

    if not check_file_exists(args.config, "Config file"):
        return 1

    if not check_file_exists("assets/song.wav", "Audio file"):
        return 1

    if not check_file_exists("assets/fox.png", "Mascot image"):
        return 1

    # Step 0: Optional - Auto-generate lyrics
    if args.auto_lyrics:
        print_header("STEP 0: AUTO-GENERATE LYRICS")

        # Check if Whisper is available
        try:
            import whisper
            whisper_available = True
        except ImportError:
            whisper_available = False

        if not whisper_available:
            print_error("Whisper not installed")
            print("\nInstall with: pip install openai-whisper")
            print("Or run without --auto-lyrics to use manual lyrics")
            return 1

        # Run Whisper
        if not run_command(
            [
                sys.executable,
                'auto_lyrics_whisper.py',
                'assets/song.wav',
                '--output', 'assets/lyrics.txt',
                '--model', 'tiny',  # Fastest model for quick test
                '--words-per-phrase', '4'
            ],
            "Generating lyrics with Whisper (tiny model)",
            timeout=300  # 5 minutes max
        ):
            print("\nWARNING: Lyrics generation failed")
            print("Continuing without automated lyrics...")

    # Check lyrics file (unless --no-lyrics)
    if not args.no_lyrics:
        if not check_file_exists("assets/lyrics.txt", "Lyrics file"):
            print("\nWARNING: No lyrics file found")
            print("Run with --auto-lyrics to generate, or --no-lyrics to skip")
            print("Continuing without lyrics...")

    # Step 1: Phase 1 - Audio Prep
    print_header("STEP 1: AUDIO PREPROCESSING")

    if not run_command(
        [sys.executable, 'main.py', '--config', args.config, '--phase', '1'],
        "Running Phase 1 (Audio Prep)",
        timeout=120  # 2 minutes
    ):
        print_error("Phase 1 failed")
        return 1

    # Step 2: Phase 2 - Blender Rendering
    print_header("STEP 2: BLENDER RENDERING")

    print("⚠ NOTE: This may take 5-15 minutes depending on your hardware")
    print("  Low resolution (360p) helps, but rendering still takes time")
    print("  Progress will be shown below...\n")

    if not run_command(
        [sys.executable, 'main.py', '--config', args.config, '--phase', '2'],
        "Running Phase 2 (Blender Animation)",
        timeout=1800  # 30 minutes max (generous timeout)
    ):
        print_error("Phase 2 failed")
        return 1

    # Step 3: Phase 3 - Video Export
    print_header("STEP 3: VIDEO EXPORT")

    if not run_command(
        [sys.executable, 'main.py', '--config', args.config, '--phase', '3'],
        "Running Phase 3 (FFmpeg Export)",
        timeout=300  # 5 minutes
    ):
        print_error("Phase 3 failed")
        return 1

    # Success!
    overall_elapsed = time.time() - overall_start

    print_header("SUCCESS!")

    print(f"✓ Full pipeline completed in {overall_elapsed/60:.1f} minutes")
    print(f"\nOutput video: outputs/quick_test/quick_test.mp4")
    print(f"Resolution: 640x360 (360p)")
    print(f"Quality: Medium (for quick testing)")

    # Check output size
    output_path = "outputs/quick_test/quick_test.mp4"
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"File size: {size_mb:.2f} MB")

        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("\n1. Watch the video:")
        print(f"   {output_path}")
        print("\n2. Check positioning and timing:")
        print("   - Is mascot visible?")
        print("   - Are lyrics appearing in front?")
        print("   - Is lip sync working?")
        print("\n3. If satisfied, render at higher quality:")
        print("   python main.py --config config.yaml")
        print("\n4. Enable debug mode to see positioning markers:")
        print("   python quick_test.py --debug")
    else:
        print_error(f"Output file not found: {output_path}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
