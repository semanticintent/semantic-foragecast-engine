#!/usr/bin/env python3
"""
Automatic Lyrics Timing using Whisper
Generates timed lyrics from audio file using OpenAI Whisper with word-level timestamps.

Requirements:
    pip install openai-whisper

Usage:
    python auto_lyrics_whisper.py path/to/song.wav --output lyrics.txt
"""

import argparse
import os
from typing import List, Dict

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("WARNING: openai-whisper not installed")
    print("Install with: pip install openai-whisper")


def transcribe_with_whisper(audio_path: str, model_size: str = "base") -> List[Dict]:
    """
    Transcribe audio and extract word-level timestamps using Whisper.

    Args:
        audio_path: Path to audio file
        model_size: Whisper model size ("tiny", "base", "small", "medium", "large")

    Returns:
        List of word dictionaries with timing:
        [
            {"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.5, "end": 1.0},
            ...
        ]
    """
    if not WHISPER_AVAILABLE:
        raise ImportError("openai-whisper not installed")

    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)

    print(f"Transcribing: {audio_path}")
    # word_timestamps=True enables word-level timing
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        language="en"  # Change if needed
    )

    # Extract words with timestamps
    timed_words = []

    for segment in result['segments']:
        # Each segment contains words with timestamps
        if 'words' in segment:
            for word_info in segment['words']:
                timed_words.append({
                    'word': word_info['word'].strip(),
                    'start': word_info['start'],
                    'end': word_info['end']
                })

    print(f"Extracted {len(timed_words)} words")
    return timed_words


def group_words_into_phrases(
    timed_words: List[Dict],
    words_per_phrase: int = 4,
    max_phrase_duration: float = 3.0
) -> List[Dict]:
    """
    Group individual words into phrases for better readability.

    Args:
        timed_words: List of individual timed words
        words_per_phrase: Target number of words per phrase
        max_phrase_duration: Maximum duration for a phrase in seconds

    Returns:
        List of phrase dictionaries:
        [
            {"words": ["Hello", "world", "this", "is"], "start": 0.0, "end": 2.0},
            ...
        ]
    """
    phrases = []
    current_phrase = []
    phrase_start = None

    for i, word_data in enumerate(timed_words):
        if not current_phrase:
            phrase_start = word_data['start']

        current_phrase.append(word_data['word'])

        # Determine if we should end this phrase
        phrase_duration = word_data['end'] - phrase_start
        should_break = (
            len(current_phrase) >= words_per_phrase or
            phrase_duration >= max_phrase_duration or
            i == len(timed_words) - 1  # Last word
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
    """
    Save phrases to lyrics.txt format.

    Format: START-END word|word|word
    Example: 0:00-0:03 Hello|world|this|is
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for phrase in phrases:
            start_str = format_timestamp(phrase['start'])
            end_str = format_timestamp(phrase['end'])
            words_str = '|'.join(phrase['words'])

            f.write(f"{start_str}-{end_str} {words_str}\n")

    print(f"Saved {len(phrases)} phrases to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate timed lyrics from audio using Whisper'
    )
    parser.add_argument(
        'audio_path',
        help='Path to audio file (WAV, MP3, etc.)'
    )
    parser.add_argument(
        '--output',
        default='lyrics.txt',
        help='Output lyrics file (default: lyrics.txt)'
    )
    parser.add_argument(
        '--model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )
    parser.add_argument(
        '--words-per-phrase',
        type=int,
        default=4,
        help='Target words per phrase (default: 4)'
    )
    parser.add_argument(
        '--max-duration',
        type=float,
        default=3.0,
        help='Maximum phrase duration in seconds (default: 3.0)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.audio_path):
        print(f"ERROR: Audio file not found: {args.audio_path}")
        return 1

    if not WHISPER_AVAILABLE:
        print("\nERROR: Whisper not installed")
        print("Install with: pip install openai-whisper")
        return 1

    try:
        # Step 1: Transcribe with word-level timestamps
        timed_words = transcribe_with_whisper(args.audio_path, args.model)

        # Step 2: Group words into phrases
        phrases = group_words_into_phrases(
            timed_words,
            words_per_phrase=args.words_per_phrase,
            max_phrase_duration=args.max_duration
        )

        # Step 3: Save to lyrics format
        save_to_lyrics_format(phrases, args.output)

        print("\n" + "=" * 50)
        print("SUCCESS!")
        print("=" * 50)
        print(f"Transcribed {len(timed_words)} words")
        print(f"Grouped into {len(phrases)} phrases")
        print(f"Output: {args.output}")
        print("\nYou can now use this file with the pipeline:")
        print("  python main.py --config config.yaml")

        return 0

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
