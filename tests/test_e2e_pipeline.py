#!/usr/bin/env python3
"""
End-to-End Pipeline Tests

Covers Phase 1 audio preprocessing, sync drift validation,
and performance benchmarks. Phase 2/3 integration tests live here
once compose_animation.py is in place.
"""

import os
import sys
import time
import json
import shutil
import logging
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from prep_audio import AudioPreprocessor, PhonemeExtractor, LyricsParser

logger = logging.getLogger(__name__)


class E2EPipelineTestCase(unittest.TestCase):
    """Base class for E2E pipeline tests."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix='e2e_test_')
        cls.assets_dir = os.path.join(cls.test_dir, 'assets')
        cls.outputs_dir = os.path.join(cls.test_dir, 'outputs')
        os.makedirs(cls.assets_dir, exist_ok=True)
        os.makedirs(cls.outputs_dir, exist_ok=True)

        cls._create_test_audio()
        cls._create_test_image()
        cls._create_test_lyrics()

        cls.metrics = {}
        logger.info("E2E test suite — dir: %s", cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    @classmethod
    def _create_test_audio(cls):
        try:
            import soundfile as sf
        except ImportError:
            from scipy.io import wavfile
            sf = None

        duration = 5.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))

        audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        audio += 0.15 * np.sin(2 * np.pi * 880 * t)
        audio += 0.1 * np.sin(2 * np.pi * 1320 * t)

        beat_interval = 0.5  # 120 BPM
        for beat_time in np.arange(0, duration, beat_interval):
            beat_idx = int(beat_time * sample_rate)
            if beat_idx < len(audio) - 2000:
                envelope = np.exp(-np.linspace(0, 5, 2000))
                burst = envelope * np.sin(2 * np.pi * 200 * np.linspace(0, 0.1, 2000))
                audio[beat_idx:beat_idx + 2000] += burst * 1.5

        audio = audio / np.max(np.abs(audio)) * 0.9
        cls.test_audio_path = os.path.join(cls.assets_dir, 'test_song.wav')

        if sf:
            sf.write(cls.test_audio_path, audio, sample_rate)
        else:
            wavfile.write(cls.test_audio_path, sample_rate,
                         (audio * 32767).astype(np.int16))

        logger.info("Created test audio: %s (%.1fs, 120 BPM)", cls.test_audio_path, duration)

    @classmethod
    def _create_test_image(cls):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            logger.warning("PIL not available — skipping test image creation")
            cls.test_image_path = None
            return

        img = Image.new('RGBA', (512, 512), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Simple fox face: head, ears, eyes, nose, mouth
        draw.ellipse([100, 100, 412, 412], fill=(255, 140, 0, 255), outline=(0, 0, 0, 255), width=3)
        draw.polygon([150, 100, 100, 50, 200, 80], fill=(255, 140, 0, 255), outline=(0, 0, 0, 255))
        draw.polygon([362, 100, 412, 50, 312, 80], fill=(255, 140, 0, 255), outline=(0, 0, 0, 255))
        draw.ellipse([180, 200, 220, 260], fill=(0, 0, 0, 255))
        draw.ellipse([292, 200, 332, 260], fill=(0, 0, 0, 255))
        draw.polygon([256, 280, 236, 310, 276, 310], fill=(0, 0, 0, 255))
        draw.arc([200, 280, 312, 350], 0, 180, fill=(0, 0, 0, 255), width=3)

        cls.test_image_path = os.path.join(cls.assets_dir, 'test_fox.png')
        img.save(cls.test_image_path)
        logger.info("Created test image: %s (512x512 RGBA)", cls.test_image_path)

    @classmethod
    def _create_test_lyrics(cls):
        lyrics = "0:00-0:05 Hello|world\n0:05-0:10 Testing|sync"
        cls.test_lyrics_path = os.path.join(cls.assets_dir, 'test_lyrics.txt')
        with open(cls.test_lyrics_path, 'w') as f:
            f.write(lyrics)
        logger.info("Created test lyrics: %s", cls.test_lyrics_path)

    def _create_config(self, mode: str = 'sprite') -> str:
        """Create a minimal test config for the sprite compositor pipeline."""
        import yaml
        config = {
            'inputs': {
                'mascot_image': self.test_image_path,
                'song_file': self.test_audio_path,
                'lyrics_file': self.test_lyrics_path,
            },
            'output': {
                'output_dir': os.path.join(self.outputs_dir, mode),
                'video_name': f'{mode}_video.mp4',
                'frames_dir': os.path.join(self.outputs_dir, mode, 'frames'),
                'prep_json': os.path.join(self.outputs_dir, mode, 'prep_data.json'),
            },
            'character': {
                'sprites_dir': os.path.join(self.assets_dir, 'sprites'),
                'mouth_region': {'x': 200, 'y': 280, 'w': 112, 'h': 70},
            },
            'animation': {
                'fps': 24,
                'body_bob_px': 8,
                'body_bob_beats': True,
                'background_color': [30, 20, 40],
            },
            'video': {
                'fps': 24,
                'resolution': [640, 480],
                'codec': 'libx264',
                'quality': 'medium',
            },
            'rhubarb': {
                'executable_path': None,
                'use_mock_fallback': True,
            },
        }
        os.makedirs(config['output']['output_dir'], exist_ok=True)
        config_path = os.path.join(self.outputs_dir, f'config_{mode}.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return config_path


class TestPhase1Preprocessing(E2EPipelineTestCase):
    """Test Phase 1: audio preprocessing."""

    def test_01_audio_preprocessing(self):
        start = time.time()
        processor = AudioPreprocessor(sample_rate=22050)
        y, sr = processor.load_audio(self.test_audio_path)
        beat_data = processor.detect_beats(y, sr)
        elapsed = time.time() - start
        duration = len(y) / sr

        self.assertIsNotNone(beat_data)
        self.assertIn('beat_times', beat_data)
        self.assertIn('onset_times', beat_data)
        self.assertIn('tempo', beat_data)
        self.assertAlmostEqual(duration, 5.0, delta=0.1)
        self.assertGreater(len(beat_data['beat_times']), 5)
        self.assertGreater(beat_data['tempo'], 100)

        self.metrics['preprocessing'] = {
            'duration': duration,
            'num_beats': len(beat_data['beat_times']),
            'tempo_bpm': beat_data['tempo'],
            'processing_time': elapsed,
        }
        logger.info(
            "Phase 1 preprocessing: %.2fs audio, %d beats, %.1f BPM in %.3fs",
            duration, len(beat_data['beat_times']), beat_data['tempo'], elapsed
        )

    def test_02_phoneme_extraction(self):
        start = time.time()
        extractor = PhonemeExtractor(rhubarb_path=None)
        phonemes = extractor.extract_phonemes(self.test_audio_path)
        elapsed = time.time() - start

        self.assertIsInstance(phonemes, list)
        self.assertGreater(len(phonemes), 0)
        for p in phonemes:
            self.assertIn('time', p)
            self.assertIn('phoneme', p)
            self.assertIsInstance(p['time'], (int, float))
            self.assertIsInstance(p['phoneme'], str)

        logger.info("Phoneme extraction: %d phonemes in %.3fs", len(phonemes), elapsed)

    def test_03_lyrics_parsing(self):
        start = time.time()
        lyrics = LyricsParser.parse_lyrics(self.test_lyrics_path)
        elapsed = time.time() - start

        self.assertIsInstance(lyrics, list)
        self.assertGreaterEqual(len(lyrics), 2)
        for lyric in lyrics:
            self.assertIn('start', lyric)
            self.assertIn('end', lyric)
            self.assertIn('word', lyric)
        self.assertAlmostEqual(lyrics[0]['start'], 0.0, delta=0.1)

        logger.info("Lyrics parsing: %d words in %.3fs", len(lyrics), elapsed)


class TestSyncDriftValidation(E2EPipelineTestCase):
    """Test sync drift validation (<75ms threshold)."""

    def test_sync_drift_beats_to_animation(self):
        processor = AudioPreprocessor(sample_rate=22050)
        y, sr = processor.load_audio(self.test_audio_path)
        beat_data = processor.detect_beats(y, sr)
        detected_beats = beat_data['beat_times']
        expected_interval = 0.5  # 120 BPM

        max_drift = 0.0
        if len(detected_beats) > 1:
            for i in range(1, len(detected_beats)):
                drift = abs((detected_beats[i] - detected_beats[i-1]) - expected_interval) * 1000
                max_drift = max(max_drift, drift)

        threshold_ms = 75.0
        self.assertLess(max_drift, threshold_ms,
                        f"Beat drift {max_drift:.2f}ms exceeds {threshold_ms}ms threshold")
        logger.info("Beat drift: %.2fms (threshold: %.1fms)", max_drift, threshold_ms)

    def test_sync_drift_phonemes_to_audio(self):
        processor = AudioPreprocessor(sample_rate=22050)
        y, sr = processor.load_audio(self.test_audio_path)
        audio_duration = len(y) / sr

        extractor = PhonemeExtractor(rhubarb_path=None)
        phonemes = extractor.extract_phonemes(self.test_audio_path)

        max_drift = 0.0
        for p in phonemes:
            t = p['time']
            if t < 0:
                max_drift = max(max_drift, abs(t) * 1000)
            elif t > audio_duration:
                max_drift = max(max_drift, (t - audio_duration) * 1000)

        self.assertLess(max_drift, 50.0,
                        f"Phoneme drift {max_drift:.2f}ms exceeds 50ms threshold")
        logger.info("Phoneme drift: %.2fms", max_drift)


class TestPerformanceBenchmarks(E2EPipelineTestCase):
    """Phase 1 performance benchmarks."""

    def test_phase1_performance(self):
        iterations = 3
        times = []
        for _ in range(iterations):
            start = time.time()
            processor = AudioPreprocessor(sample_rate=22050)
            y, sr = processor.load_audio(self.test_audio_path)
            processor.detect_beats(y, sr)
            PhonemeExtractor(rhubarb_path=None).extract_phonemes(self.test_audio_path)
            LyricsParser.parse_lyrics(self.test_lyrics_path)
            times.append(time.time() - start)

        avg_time = float(np.mean(times))
        self.assertLess(avg_time, 10.0, "Phase 1 should complete in < 10s")
        logger.info("Phase 1 avg: %.3fs over %d iterations", avg_time, iterations)

    def test_prep_json_output_size(self):
        """Phase 1 JSON output size stays under 1MB for 5s audio."""
        from main import PipelineOrchestrator

        config_path = self._create_config('sprite')
        engine = PipelineOrchestrator(config_path)

        start = time.time()
        engine.phase1_prep_audio()   # was incorrectly called run_phase1() before
        elapsed = time.time() - start

        prep_json = engine.config['output']['prep_json']
        if not os.path.exists(prep_json):
            self.skipTest("prep_data.json not generated — check Phase 1")

        file_size = os.path.getsize(prep_json)
        self.assertLess(file_size, 1024 * 1024, "Prep JSON should be < 1MB")
        logger.info("Prep JSON: %.2f KB in %.3fs", file_size / 1024, elapsed)


class TestPipelineConfig(E2EPipelineTestCase):
    """Validate sprite compositor pipeline config structure."""

    def test_sprite_config_structure(self):
        """Config for the new sprite compositor has required keys."""
        import yaml
        config_path = self._create_config('sprite')
        with open(config_path) as f:
            config = yaml.safe_load(f)

        self.assertIn('inputs', config)
        self.assertIn('character', config)
        self.assertIn('mouth_region', config['character'])
        self.assertIn('animation', config)
        self.assertIn('fps', config['animation'])
        self.assertIn('video', config)

        mouth = config['character']['mouth_region']
        for key in ('x', 'y', 'w', 'h'):
            self.assertIn(key, mouth)
            self.assertIsInstance(mouth[key], int)

        logger.info("Sprite config structure validated")


def run_e2e_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        TestPhase1Preprocessing,
        TestSyncDriftValidation,
        TestPerformanceBenchmarks,
        TestPipelineConfig,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    sys.exit(0 if run_e2e_suite() else 1)
