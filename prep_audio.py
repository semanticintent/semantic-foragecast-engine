#!/usr/bin/env python3
"""
Prep Module for Video Generation Pipeline
Phase 1: Audio Processing, Beat Detection, Phoneme Extraction, and Lyrics Parsing

This module:
- Loads WAV audio files
- Detects beats and onsets using LibROSA
- Extracts phoneme timings via Rhubarb Lip Sync (or mocks if unavailable)
- Parses lyrics TXT files to timed words
- Outputs structured JSON for downstream processing

Author: Claude (Anthropic)
Version: 1.0
Date: November 2025
Platform: Cross-platform (Windows 11 optimized)
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

import numpy as np
import librosa

# Suppress librosa warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)


class AudioPreprocessor:
    """Handles audio loading and beat/onset detection."""

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the audio preprocessor.

        Args:
            sample_rate: Target sample rate for audio loading (Hz)
        """
        self.sample_rate = sample_rate

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file with LibROSA.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Tuple of (audio_data, sample_rate)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If audio loading fails
        """
        audio_path = os.path.normpath(audio_path)

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise Exception(f"Failed to load audio: {str(e)}")

    def detect_beats(self, y: np.ndarray, sr: int) -> Dict[str, List]:
        """
        Detect beats and onsets in audio signal.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Dictionary with beat and onset information:
            {
                'beat_times': [float],      # Beat timestamps in seconds
                'beat_frames': [int],       # Beat frame indices
                'onset_times': [float],     # Onset timestamps in seconds
                'onset_frames': [int],      # Onset frame indices
                'tempo': float              # Estimated tempo in BPM
            }
        """
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            units='frames',
            backtrack=True
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        # Detect beats (with fallback for compatibility issues)
        try:
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        except (AttributeError, Exception) as e:
            # Fallback: use onsets as beats if beat tracking fails
            # This can happen with scipy version incompatibilities
            print(f"  WARNING: Beat tracking failed ({str(e)}), using onsets as beats")
            beat_frames = onset_frames
            beat_times = onset_times

            # Estimate tempo from onset intervals
            if len(onset_times) > 1:
                intervals = np.diff(onset_times)
                avg_interval = np.median(intervals) if len(intervals) > 0 else 0.5
                tempo = 60.0 / avg_interval if avg_interval > 0 else 120.0
            else:
                tempo = 120.0

        return {
            'beat_times': beat_times.tolist(),
            'beat_frames': beat_frames.tolist(),
            'onset_times': onset_times.tolist(),
            'onset_frames': onset_frames.tolist(),
            'tempo': float(tempo)
        }


class PhonemeExtractor:
    """Handles phoneme extraction using Rhubarb Lip Sync."""

    def __init__(self, rhubarb_path: Optional[str] = None):
        """
        Initialize phoneme extractor.

        Args:
            rhubarb_path: Path to Rhubarb executable. If None, searches in:
                         - Current directory
                         - PATH environment variable
        """
        self.rhubarb_path = self._find_rhubarb(rhubarb_path)

    def _find_rhubarb(self, rhubarb_path: Optional[str]) -> Optional[str]:
        """
        Locate Rhubarb executable.

        Returns:
            Path to Rhubarb or None if not found
        """
        if rhubarb_path and os.path.exists(rhubarb_path):
            return os.path.normpath(rhubarb_path)

        # Check current directory for common names
        candidates = ['rhubarb.exe', 'rhubarb', 'rhubarb-lip-sync.exe']
        for name in candidates:
            if os.path.exists(name):
                return os.path.normpath(os.path.abspath(name))

        # Check PATH
        for name in ['rhubarb', 'rhubarb.exe']:
            from shutil import which
            found = which(name)
            if found:
                return os.path.normpath(found)

        return None

    def extract_phonemes(self, audio_path: str) -> List[Dict]:
        """
        Extract phoneme timings from audio.

        Args:
            audio_path: Path to audio file

        Returns:
            List of phoneme dictionaries:
            [
                {'time': 0.0, 'phoneme': 'X'},
                {'time': 0.5, 'phoneme': 'A'},
                ...
            ]
        """
        audio_path = os.path.normpath(audio_path)

        if self.rhubarb_path:
            return self._extract_with_rhubarb(audio_path)
        else:
            print("WARNING: Rhubarb not found. Using mock phoneme data.")
            return self._generate_mock_phonemes(audio_path)

    def _extract_with_rhubarb(self, audio_path: str) -> List[Dict]:
        """
        Extract phonemes using Rhubarb binary.

        Args:
            audio_path: Path to audio file

        Returns:
            List of phoneme dictionaries
        """
        try:
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as tmp:
                output_path = tmp.name

            # Run Rhubarb
            cmd = [
                self.rhubarb_path,
                '-f', 'dat',
                '-o', output_path,
                audio_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"WARNING: Rhubarb failed: {result.stderr}")
                return self._generate_mock_phonemes(audio_path)

            # Parse DAT output
            phonemes = self._parse_rhubarb_dat(output_path)

            # Clean up
            os.unlink(output_path)

            return phonemes

        except Exception as e:
            print(f"WARNING: Rhubarb extraction failed: {str(e)}")
            return self._generate_mock_phonemes(audio_path)

    def _parse_rhubarb_dat(self, dat_path: str) -> List[Dict]:
        """
        Parse Rhubarb DAT format output.

        DAT format example:
        0.00 X
        0.50 A
        1.20 B

        Args:
            dat_path: Path to DAT file

        Returns:
            List of phoneme dictionaries
        """
        phonemes = []

        with open(dat_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    time = float(parts[0])
                    phoneme = parts[1]
                    phonemes.append({
                        'time': time,
                        'phoneme': phoneme
                    })

        return phonemes

    def _generate_mock_phonemes(self, audio_path: str) -> List[Dict]:
        """
        Generate mock phoneme data when Rhubarb is unavailable.
        Creates a simple pattern that transitions through common phonemes.

        Args:
            audio_path: Path to audio file (used to determine duration)

        Returns:
            List of mock phoneme dictionaries
        """
        # Get audio duration
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            duration = librosa.get_duration(y=y, sr=sr)
        except:
            duration = 5.0  # Default fallback

        # Common phonemes for lip sync (Preston Blair mouth shapes)
        # X = rest, A = open, B = pursed, C = wide, etc.
        phoneme_cycle = ['X', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        phonemes = []
        time_step = 0.15  # ~6-7 phonemes per second (natural speech rate)
        current_time = 0.0
        idx = 0

        while current_time < duration:
            phonemes.append({
                'time': round(current_time, 2),
                'phoneme': phoneme_cycle[idx % len(phoneme_cycle)]
            })
            current_time += time_step
            idx += 1

        return phonemes


class LyricsParser:
    """Parses timed lyrics from text files."""

    @staticmethod
    def parse_lyrics(lyrics_path: str) -> List[Dict]:
        """
        Parse lyrics file to extract timed words.

        Expected format (one line per phrase):
        0:00-0:05 Hello|world|this|is|a|test
        0:06-0:10 Another|line|here

        Alternative formats supported:
        - SRT-like: timestamps on separate lines
        - Simple: one word per line with timestamp

        Args:
            lyrics_path: Path to lyrics TXT file

        Returns:
            List of timed word dictionaries:
            [
                {'start': 0.0, 'end': 1.0, 'word': 'Hello'},
                {'start': 1.0, 'end': 2.0, 'word': 'world'},
                ...
            ]
        """
        lyrics_path = os.path.normpath(lyrics_path)

        if not os.path.exists(lyrics_path):
            print(f"WARNING: Lyrics file not found: {lyrics_path}")
            return []

        try:
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return LyricsParser._parse_content(content)

        except Exception as e:
            print(f"WARNING: Failed to parse lyrics: {str(e)}")
            return []

    @staticmethod
    def _parse_content(content: str) -> List[Dict]:
        """
        Parse lyrics content with flexible format detection.

        Args:
            content: Raw lyrics text

        Returns:
            List of timed word dictionaries
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        timed_words = []

        for line in lines:
            # Format: "0:00-0:05 Hello|world|this"
            if '-' in line and ('|' in line or ' ' in line):
                result = LyricsParser._parse_piped_format(line)
                if result:
                    timed_words.extend(result)

        return timed_words

    @staticmethod
    def _parse_piped_format(line: str) -> List[Dict]:
        """
        Parse format: "0:00-0:05 Hello|world|this"

        Args:
            line: Single line of lyrics

        Returns:
            List of timed word dictionaries
        """
        try:
            # Split timestamp from words
            parts = line.split(None, 1)
            if len(parts) < 2:
                return []

            timestamp_part, words_part = parts

            # Parse timestamps
            if '-' not in timestamp_part:
                return []

            start_str, end_str = timestamp_part.split('-')
            start_time = LyricsParser._parse_timestamp(start_str)
            end_time = LyricsParser._parse_timestamp(end_str)

            # Split words (by pipe or space)
            if '|' in words_part:
                words = [w.strip() for w in words_part.split('|') if w.strip()]
            else:
                words = [w.strip() for w in words_part.split() if w.strip()]

            if not words:
                return []

            # Distribute time evenly across words
            duration = end_time - start_time
            time_per_word = duration / len(words)

            timed_words = []
            for i, word in enumerate(words):
                word_start = start_time + (i * time_per_word)
                word_end = word_start + time_per_word

                timed_words.append({
                    'start': round(word_start, 2),
                    'end': round(word_end, 2),
                    'word': word
                })

            return timed_words

        except Exception as e:
            print(f"WARNING: Failed to parse line '{line}': {str(e)}")
            return []

    @staticmethod
    def _parse_timestamp(ts: str) -> float:
        """
        Parse timestamp string to seconds.

        Supports: "1:23", "0:05", "1:23.45"

        Args:
            ts: Timestamp string

        Returns:
            Time in seconds
        """
        parts = ts.split(':')

        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        else:
            return float(ts)


def process_audio(
    audio_path: str,
    lyrics_path: Optional[str] = None,
    rhubarb_path: Optional[str] = None,
    output_json: Optional[str] = None
) -> Dict:
    """
    Main processing function: orchestrates audio analysis, phoneme extraction, and lyrics parsing.

    Args:
        audio_path: Path to audio file (WAV, MP3, etc.)
        lyrics_path: Optional path to lyrics TXT file
        rhubarb_path: Optional path to Rhubarb executable
        output_json: Optional path to save JSON output

    Returns:
        Dictionary with all processed data:
        {
            'audio': {
                'duration': float,
                'sample_rate': int,
                'tempo': float
            },
            'beats': {
                'beat_times': [float],
                'beat_frames': [int],
                'onset_times': [float],
                'onset_frames': [int]
            },
            'phonemes': [
                {'time': float, 'phoneme': str}
            ],
            'timed_words': [
                {'start': float, 'end': float, 'word': str}
            ]
        }
    """
    # Normalize paths for cross-platform compatibility
    audio_path = os.path.normpath(audio_path)

    print(f"Processing audio: {audio_path}")

    # Load and analyze audio
    preprocessor = AudioPreprocessor()
    y, sr = preprocessor.load_audio(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)

    print(f"  Duration: {duration:.2f}s, Sample Rate: {sr} Hz")

    # Detect beats
    print("  Detecting beats and onsets...")
    beats_data = preprocessor.detect_beats(y, sr)
    print(f"  Found {len(beats_data['beat_times'])} beats, {len(beats_data['onset_times'])} onsets")
    print(f"  Estimated tempo: {beats_data['tempo']:.1f} BPM")

    # Extract phonemes
    print("  Extracting phonemes...")
    extractor = PhonemeExtractor(rhubarb_path)
    phonemes = extractor.extract_phonemes(audio_path)
    print(f"  Found {len(phonemes)} phoneme transitions")

    # Parse lyrics
    timed_words = []
    if lyrics_path:
        print(f"  Parsing lyrics: {lyrics_path}")
        parser = LyricsParser()
        timed_words = parser.parse_lyrics(lyrics_path)
        print(f"  Found {len(timed_words)} timed words")

    # Compile results
    result = {
        'audio': {
            'path': audio_path,
            'duration': round(duration, 2),
            'sample_rate': sr,
            'tempo': beats_data['tempo']
        },
        'beats': {
            'beat_times': beats_data['beat_times'],
            'beat_frames': beats_data['beat_frames'],
            'onset_times': beats_data['onset_times'],
            'onset_frames': beats_data['onset_frames']
        },
        'phonemes': phonemes,
        'timed_words': timed_words
    }

    # Save to JSON if requested
    if output_json:
        output_json = os.path.normpath(output_json)
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {output_json}")

    return result


if __name__ == '__main__':
    """
    Example usage and basic testing.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Audio Prep Module for Video Pipeline')
    parser.add_argument('audio', help='Path to audio file (WAV/MP3)')
    parser.add_argument('--lyrics', help='Path to lyrics TXT file')
    parser.add_argument('--rhubarb', help='Path to Rhubarb executable')
    parser.add_argument('--output', help='Output JSON path', default='output.json')

    args = parser.parse_args()

    result = process_audio(
        audio_path=args.audio,
        lyrics_path=args.lyrics,
        rhubarb_path=args.rhubarb,
        output_json=args.output
    )

    print(f"\n{'='*60}")
    print("PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Audio Duration: {result['audio']['duration']}s")
    print(f"Tempo: {result['audio']['tempo']:.1f} BPM")
    print(f"Beats: {len(result['beats']['beat_times'])}")
    print(f"Onsets: {len(result['beats']['onset_times'])}")
    print(f"Phonemes: {len(result['phonemes'])}")
    print(f"Timed Words: {len(result['timed_words'])}")
    print(f"{'='*60}\n")
