#!/usr/bin/env python3
"""
Unit tests for prep_audio.py

Tests audio processing, beat detection, phoneme extraction, and lyrics parsing.
Includes mock WAV generation for sandbox testing.

"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path

import numpy as np
import soundfile as sf

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prep_audio import (
    AudioPreprocessor,
    PhonemeExtractor,
    LyricsParser,
    process_audio
)


class TestMockAudioGeneration(unittest.TestCase):
    """Test mock audio generation for sandbox testing."""

    def test_generate_mock_wav(self):
        """Generate a 5-second test tone WAV file."""
        duration = 5.0  # seconds
        sample_rate = 22050  # Hz
        frequency = 440.0  # A4 note

        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = np.sin(2 * np.pi * frequency * t)

        # Add some amplitude variation for interest
        envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
        audio = audio * envelope * 0.5  # Scale to prevent clipping

        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            wav_path = tmp.name

        sf.write(wav_path, audio, sample_rate)

        # Verify file exists and has correct size
        self.assertTrue(os.path.exists(wav_path))
        file_size = os.path.getsize(wav_path)
        self.assertGreater(file_size, 0)

        # Clean up
        os.unlink(wav_path)

        print(f"✓ Generated mock WAV: {duration}s, {sample_rate}Hz, {file_size} bytes")


class TestAudioPreprocessor(unittest.TestCase):
    """Test audio loading and beat detection."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary test WAV file."""
        cls.temp_wav = cls._create_test_wav()

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files."""
        if os.path.exists(cls.temp_wav):
            os.unlink(cls.temp_wav)

    @staticmethod
    def _create_test_wav(duration=5.0, sample_rate=22050):
        """Create a test WAV with beats at regular intervals."""
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        # Create tone with periodic beats (every 0.5s)
        tone = np.sin(2 * np.pi * 440 * t)

        # Add beat impulses
        beat_interval = 0.5
        beats = np.zeros_like(t)
        for beat_time in np.arange(0, duration, beat_interval):
            beat_idx = int(beat_time * sample_rate)
            if beat_idx < len(beats) - 1000:
                beats[beat_idx:beat_idx + 1000] = 1.0

        # Combine
        audio = (tone + beats * 2.0) * 0.3

        # Save
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            wav_path = tmp.name

        sf.write(wav_path, audio, sample_rate)

        return wav_path

    def test_load_audio(self):
        """Test audio file loading."""
        preprocessor = AudioPreprocessor()
        y, sr = preprocessor.load_audio(self.temp_wav)

        self.assertIsInstance(y, np.ndarray)
        self.assertEqual(sr, 22050)
        self.assertGreater(len(y), 0)

        print(f"✓ Loaded audio: {len(y)} samples, {sr}Hz")

    def test_detect_beats(self):
        """Test beat and onset detection."""
        preprocessor = AudioPreprocessor()
        y, sr = preprocessor.load_audio(self.temp_wav)

        beats_data = preprocessor.detect_beats(y, sr)

        # Verify structure
        self.assertIn('beat_times', beats_data)
        self.assertIn('onset_times', beats_data)
        self.assertIn('tempo', beats_data)

        # Verify we found beats
        self.assertGreater(len(beats_data['beat_times']), 0, "Should detect at least one beat")
        self.assertGreater(len(beats_data['onset_times']), 0, "Should detect at least one onset")

        # Verify tempo is reasonable
        self.assertGreater(beats_data['tempo'], 0)
        self.assertLess(beats_data['tempo'], 300)

        print(f"✓ Detected {len(beats_data['beat_times'])} beats, {len(beats_data['onset_times'])} onsets")
        print(f"  Tempo: {beats_data['tempo']:.1f} BPM")


class TestPhonemeExtractor(unittest.TestCase):
    """Test phoneme extraction."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary test WAV file."""
        duration = 3.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = np.sin(2 * np.pi * 440 * t) * 0.5

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            cls.temp_wav = tmp.name

        sf.write(cls.temp_wav, audio, sample_rate)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files."""
        if os.path.exists(cls.temp_wav):
            os.unlink(cls.temp_wav)

    def test_extract_phonemes_mock(self):
        """Test mock phoneme generation (when Rhubarb unavailable)."""
        extractor = PhonemeExtractor(rhubarb_path=None)
        phonemes = extractor.extract_phonemes(self.temp_wav)

        # Verify we got phonemes
        self.assertGreater(len(phonemes), 0, "Should generate mock phonemes")

        # Verify structure
        for phoneme in phonemes:
            self.assertIn('time', phoneme)
            self.assertIn('phoneme', phoneme)
            self.assertIsInstance(phoneme['time'], (int, float))
            self.assertIsInstance(phoneme['phoneme'], str)

        # Verify phonemes are in chronological order
        times = [p['time'] for p in phonemes]
        self.assertEqual(times, sorted(times), "Phonemes should be chronologically ordered")

        print(f"✓ Generated {len(phonemes)} mock phonemes")
        print(f"  Sample: {phonemes[:3]}")


class TestLyricsParser(unittest.TestCase):
    """Test lyrics parsing."""

    def test_parse_piped_format(self):
        """Test parsing of pipe-delimited lyrics."""
        lyrics_content = """0:00-0:05 Hello|world|this|is|a|test
0:06-0:10 Another|line|here
0:11-0:15 Final|words"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(lyrics_content)
            lyrics_path = tmp.name

        try:
            parser = LyricsParser()
            timed_words = parser.parse_lyrics(lyrics_path)

            # Verify we parsed words
            self.assertGreater(len(timed_words), 0, "Should parse timed words")

            # Verify structure
            for word_data in timed_words:
                self.assertIn('start', word_data)
                self.assertIn('end', word_data)
                self.assertIn('word', word_data)
                self.assertIsInstance(word_data['start'], (int, float))
                self.assertIsInstance(word_data['end'], (int, float))
                self.assertIsInstance(word_data['word'], str)

            # Verify chronological order
            starts = [w['start'] for w in timed_words]
            self.assertEqual(starts, sorted(starts), "Words should be chronologically ordered")

            # Verify specific words
            words = [w['word'] for w in timed_words]
            self.assertIn('Hello', words)
            self.assertIn('world', words)

            print(f"✓ Parsed {len(timed_words)} timed words")
            print(f"  Sample: {timed_words[:3]}")

        finally:
            os.unlink(lyrics_path)

    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        parser = LyricsParser()

        self.assertEqual(parser._parse_timestamp("0:05"), 5.0)
        self.assertEqual(parser._parse_timestamp("1:23"), 83.0)
        self.assertEqual(parser._parse_timestamp("0:00.5"), 0.5)

        print("✓ Timestamp parsing works correctly")


class TestIntegration(unittest.TestCase):
    """Integration tests for full processing pipeline."""

    @classmethod
    def setUpClass(cls):
        """Create test assets."""
        # Create test WAV with beats
        duration = 5.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        # Create audio with some variation and beats
        audio = np.sin(2 * np.pi * 440 * t) * 0.5
        audio += np.sin(2 * np.pi * 880 * t) * 0.25

        # Add beat impulses every 0.5 seconds for onset detection
        beat_interval = 0.5
        for beat_time in np.arange(0, duration, beat_interval):
            beat_idx = int(beat_time * sample_rate)
            if beat_idx < len(audio) - 1000:
                # Short percussive burst
                audio[beat_idx:beat_idx + 1000] += np.sin(2 * np.pi * 1000 * np.arange(1000) / sample_rate) * 2.0 * np.exp(-np.arange(1000) / 100)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            cls.temp_wav = tmp.name

        sf.write(cls.temp_wav, audio, sample_rate)

        # Create test lyrics
        lyrics_content = """0:00-0:02 Testing|audio
0:03-0:05 Processing|pipeline"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(lyrics_content)
            cls.temp_lyrics = tmp.name

        # Output JSON path
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            cls.temp_json = tmp.name

    @classmethod
    def tearDownClass(cls):
        """Clean up test assets."""
        for path in [cls.temp_wav, cls.temp_lyrics, cls.temp_json]:
            if os.path.exists(path):
                os.unlink(path)

    def test_full_pipeline(self):
        """Test complete audio processing pipeline."""
        result = process_audio(
            audio_path=self.temp_wav,
            lyrics_path=self.temp_lyrics,
            rhubarb_path=None,  # Use mock phonemes
            output_json=self.temp_json
        )

        # Verify result structure
        self.assertIn('audio', result)
        self.assertIn('beats', result)
        self.assertIn('phonemes', result)
        self.assertIn('timed_words', result)

        # Verify audio metadata
        self.assertGreater(result['audio']['duration'], 0)
        self.assertEqual(result['audio']['sample_rate'], 22050)

        # Verify beats detected
        self.assertGreater(len(result['beats']['beat_times']), 0)
        self.assertGreater(len(result['beats']['onset_times']), 0)

        # Verify phonemes generated
        self.assertGreater(len(result['phonemes']), 0)

        # Verify lyrics parsed
        self.assertGreater(len(result['timed_words']), 0)

        # Verify JSON output created
        self.assertTrue(os.path.exists(self.temp_json))

        # Verify JSON is valid
        with open(self.temp_json, 'r') as f:
            json_data = json.load(f)
            self.assertEqual(json_data, result)

        print("✓ Full pipeline integration test passed")
        print(f"  Audio: {result['audio']['duration']}s, {result['audio']['tempo']:.1f} BPM")
        print(f"  Beats: {len(result['beats']['beat_times'])}")
        print(f"  Phonemes: {len(result['phonemes'])}")
        print(f"  Words: {len(result['timed_words'])}")


def run_tests():
    """Run all tests and display results."""
    print("="*70)
    print("PREP_AUDIO.PY UNIT TESTS")
    print("="*70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMockAudioGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestAudioPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestPhonemeExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestLyricsParser))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

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
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
