#!/usr/bin/env python3
"""
Lyrics Timing using Gentle Forced Aligner
Aligns known lyrics text to audio using Gentle (requires Gentle server running).

Gentle: https://github.com/lowerquality/gentle

Requirements:
    - Gentle server running locally (Docker recommended)
    - requests library: pip install requests

Docker setup:
    docker run -p 8765:8765 lowerquality/gentle

Usage:
    python auto_lyrics_gentle.py --audio song.wav --lyrics known_lyrics.txt --output lyrics.txt
"""

import argparse
import os
import json
from typing import List, Dict

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests library not installed")
    print("Install with: pip install requests")


def align_with_gentle(
    audio_path: str,
    transcript: str,
    gentle_url: str = "http://localhost:8765"
) -> List[Dict]:
    """
    Use Gentle forced aligner to align transcript to audio.

    Args:
        audio_path: Path to audio file
        transcript: Known lyrics/transcript text
        gentle_url: URL of Gentle server

    Returns:
        List of aligned words with timestamps
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests library not installed")

    print(f"Connecting to Gentle server at {gentle_url}")

    # Prepare request
    with open(audio_path, 'rb') as audio_file:
        files = {
            'audio': audio_file,
            'transcript': (None, transcript)
        }

        print("Sending alignment request...")
        response = requests.post(
            f"{gentle_url}/transcriptions?async=false",
            files=files,
            timeout=300  # 5 minute timeout for long files
        )

    if response.status_code != 200:
        raise Exception(f"Gentle server error: {response.status_code}")

    result = response.json()

    # Extract aligned words
    timed_words = []
    for word_data in result.get('words', []):
        if word_data.get('case') == 'success':
            timed_words.append({
                'word': word_data['word'],
                'start': word_data['start'],
                'end': word_data['end']
            })
        else:
            # Word couldn't be aligned - estimate timing
            print(f"  WARNING: Could not align word: {word_data.get('word', 'unknown')}")

    print(f"Aligned {len(timed_words)} words")
    return timed_words


def group_words_into_phrases(
    timed_words: List[Dict],
    words_per_phrase: int = 4,
    max_phrase_duration: float = 3.0
) -> List[Dict]:
    """Group individual words into readable phrases."""
    phrases = []
    current_phrase = []
    phrase_start = None

    for i, word_data in enumerate(timed_words):
        if not current_phrase:
            phrase_start = word_data['start']

        current_phrase.append(word_data['word'])

        phrase_duration = word_data['end'] - phrase_start
        should_break = (
            len(current_phrase) >= words_per_phrase or
            phrase_duration >= max_phrase_duration or
            i == len(timed_words) - 1
        )

        if should_break:
            phrases.append({
                'words': current_phrase.copy(),
                'start': phrase_start,
                'end': word_data['end']
            })
            current_phrase = []
            phrase_start = None

    return phrases


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def save_to_lyrics_format(phrases: List[Dict], output_path: str):
    """Save to lyrics.txt format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for phrase in phrases:
            start_str = format_timestamp(phrase['start'])
            end_str = format_timestamp(phrase['end'])
            words_str = '|'.join(phrase['words'])
            f.write(f"{start_str}-{end_str} {words_str}\n")

    print(f"Saved {len(phrases)} phrases to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Align lyrics to audio using Gentle'
    )
    parser.add_argument(
        '--audio',
        required=True,
        help='Path to audio file'
    )
    parser.add_argument(
        '--lyrics',
        required=True,
        help='Path to text file with known lyrics'
    )
    parser.add_argument(
        '--output',
        default='lyrics.txt',
        help='Output lyrics file (default: lyrics.txt)'
    )
    parser.add_argument(
        '--gentle-url',
        default='http://localhost:8765',
        help='Gentle server URL (default: http://localhost:8765)'
    )
    parser.add_argument(
        '--words-per-phrase',
        type=int,
        default=4,
        help='Target words per phrase (default: 4)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"ERROR: Audio file not found: {args.audio}")
        return 1

    if not os.path.exists(args.lyrics):
        print(f"ERROR: Lyrics file not found: {args.lyrics}")
        return 1

    if not REQUESTS_AVAILABLE:
        print("\nERROR: requests library not installed")
        print("Install with: pip install requests")
        return 1

    # Load lyrics text
    with open(args.lyrics, 'r', encoding='utf-8') as f:
        transcript = f.read()

    try:
        # Step 1: Align with Gentle
        timed_words = align_with_gentle(args.audio, transcript, args.gentle_url)

        # Step 2: Group into phrases
        phrases = group_words_into_phrases(
            timed_words,
            words_per_phrase=args.words_per_phrase
        )

        # Step 3: Save
        save_to_lyrics_format(phrases, args.output)

        print("\n" + "=" * 50)
        print("SUCCESS!")
        print("=" * 50)
        print(f"Aligned {len(timed_words)} words")
        print(f"Grouped into {len(phrases)} phrases")
        print(f"Output: {args.output}")

        return 0

    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to Gentle server")
        print("\nMake sure Gentle is running:")
        print("  docker run -p 8765:8765 lowerquality/gentle")
        return 1

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
