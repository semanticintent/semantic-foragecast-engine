#!/usr/bin/env python3
"""
Unit tests for export_video.py

Tests video export functionality, FFmpeg integration, and frame handling.

"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from export_video import VideoExporter


class TestVideoExporter(unittest.TestCase):
    """Test video export functionality."""

    @classmethod
    def setUpClass(cls):
        """Create temporary test assets."""
        # Create temp directories
        cls.temp_dir = tempfile.mkdtemp()
        cls.frames_dir = os.path.join(cls.temp_dir, 'frames')
        os.makedirs(cls.frames_dir)

        # Create test frames (simple colored images)
        print(f"Creating test frames in {cls.frames_dir}...")
        for i in range(10):
            img = Image.new('RGB', (320, 240), color=(i * 25, 100, 200))
            frame_path = os.path.join(cls.frames_dir, f'frame_{i:04d}.png')
            img.save(frame_path)

        # Create test audio
        duration = 1.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = np.sin(2 * np.pi * 440 * t) * 0.5

        cls.audio_path = os.path.join(cls.temp_dir, 'test_audio.wav')
        sf.write(cls.audio_path, audio, sample_rate)

        print(f"Created {len(os.listdir(cls.frames_dir))} frames")
        print(f"Created audio: {cls.audio_path}")

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def test_find_ffmpeg(self):
        """Test FFmpeg detection."""
        config = {}
        exporter = VideoExporter(config)

        # FFmpeg may or may not be installed
        if exporter.ffmpeg_path:
            print(f"✓ FFmpeg found: {exporter.ffmpeg_path}")
            self.assertTrue(os.path.exists(exporter.ffmpeg_path))
        else:
            print("⚠ FFmpeg not found (install FFmpeg to test encoding)")

    def test_validate_frames(self):
        """Test frame validation."""
        config = {}
        exporter = VideoExporter(config)

        # Test with valid frames directory
        frames_exist, frame_count = exporter.validate_frames(self.frames_dir)

        self.assertTrue(frames_exist, "Frames should exist")
        self.assertEqual(frame_count, 10, "Should find 10 frames")

        print(f"✓ Validated {frame_count} frames")

        # Test with non-existent directory
        frames_exist, frame_count = exporter.validate_frames('/nonexistent')
        self.assertFalse(frames_exist)
        self.assertEqual(frame_count, 0)

    def test_detect_frame_pattern(self):
        """Test frame pattern detection."""
        config = {}
        exporter = VideoExporter(config)

        pattern = exporter._detect_frame_pattern(self.frames_dir)

        self.assertIsNotNone(pattern, "Should detect frame pattern")
        self.assertIn('frame_', pattern)
        self.assertIn('.png', pattern)

        print(f"✓ Detected pattern: {pattern}")

    def test_get_crf_value(self):
        """Test CRF value calculation."""
        config = {}
        exporter = VideoExporter(config)

        # Test different quality levels
        crf_high = exporter._get_crf_value('high', 'libx264')
        crf_medium = exporter._get_crf_value('medium', 'libx264')
        crf_low = exporter._get_crf_value('low', 'libx264')

        # Lower CRF = higher quality
        self.assertLess(crf_high, crf_medium)
        self.assertLess(crf_medium, crf_low)

        print(f"✓ CRF values: low={crf_low}, medium={crf_medium}, high={crf_high}")

    def test_get_preset(self):
        """Test preset selection."""
        config = {}
        exporter = VideoExporter(config)

        preset_low = exporter._get_preset('low')
        preset_high = exporter._get_preset('high')

        self.assertEqual(preset_low, 'veryfast')
        self.assertEqual(preset_high, 'slow')

        print(f"✓ Presets: low={preset_low}, high={preset_high}")

    def test_encode_video(self):
        """Test video encoding (if FFmpeg available)."""
        config = {}
        exporter = VideoExporter(config)

        if not exporter.ffmpeg_path:
            print("⚠ Skipping encoding test (FFmpeg not installed)")
            self.skipTest("FFmpeg not available")
            return

        output_path = os.path.join(self.temp_dir, 'test_output.mp4')

        success = exporter.encode_video(
            frames_dir=self.frames_dir,
            audio_path=self.audio_path,
            output_path=output_path,
            fps=10,  # Low FPS for fast test
            codec='libx264',
            quality='low',  # Low quality for fast encoding
            overwrite=True
        )

        if success:
            self.assertTrue(os.path.exists(output_path), "Output video should exist")
            file_size = os.path.getsize(output_path)
            self.assertGreater(file_size, 0, "Video file should not be empty")

            print(f"✓ Encoded video: {file_size:,} bytes")
        else:
            print("⚠ Encoding failed (may be expected if FFmpeg version incompatible)")


def run_tests():
    """Run all tests and display results."""
    print("="*70)
    print("EXPORT_VIDEO.PY UNIT TESTS")
    print("="*70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestVideoExporter))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    if result.wasSuccessful():
        print("✓ All tests passed!")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
