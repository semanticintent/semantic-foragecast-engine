#!/usr/bin/env python3
"""
Simple Beat-Based Lyrics Timing
Distributes known lyrics text across detected beats.

Usage:
    python auto_lyrics_beats.py --prep-data prep_data.json --lyrics-text "Your lyrics here" --output lyrics.txt
"""

import argparse
import json
from typing import List, Dict


def load_prep_data(prep_data_path: str) -> Dict:
    """Load preprocessed audio data with beat times."""
    with open(prep_data_path, 'r') as f:
        return json.load(f)


def distribute_lyrics_on_beats(
    lyrics_text: str,
    beat_times: List[float],
    words_per_beat: int = 2
) -> List[Dict]:
    """
    Distribute lyrics words across detected beats.

    Args:
        lyrics_text: Full lyrics as plain text
        beat_times: List of beat timestamps
        words_per_beat: How many words to show per beat

    Returns:
        List of timed word groups
    """
    # Split lyrics into words
    words = lyrics_text.split()

    # Group words into chunks
    word_chunks = []
    for i in range(0, len(words), words_per_beat):
        chunk = words[i:i + words_per_beat]
        word_chunks.append(chunk)

    # Assign chunks to beat intervals
    timed_phrases = []
    for i, chunk in enumerate(word_chunks):
        if i >= len(beat_times):
            break

        start_time = beat_times[i]

        # End time is next beat, or estimate
        if i + 1 < len(beat_times):
            end_time = beat_times[i + 1]
        else:
            # Estimate 0.5 seconds per word
            end_time = start_time + (len(chunk) * 0.5)

        timed_phrases.append({
            'words': chunk,
            'start': start_time,
            'end': end_time
        })

    return timed_phrases


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def save_to_lyrics_format(phrases: List[Dict], output_path: str):
    """Save to lyrics.txt format: START-END word|word|word"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for phrase in phrases:
            start_str = format_timestamp(phrase['start'])
            end_str = format_timestamp(phrase['end'])
            words_str = '|'.join(phrase['words'])
            f.write(f"{start_str}-{end_str} {words_str}\n")

    print(f"Saved {len(phrases)} phrases to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate beat-synchronized lyrics'
    )
    parser.add_argument(
        '--prep-data',
        required=True,
        help='Path to prep_data.json (contains beat times)'
    )
    parser.add_argument(
        '--lyrics-text',
        help='Lyrics as plain text (inline)'
    )
    parser.add_argument(
        '--lyrics-file',
        help='Path to plain text file with lyrics'
    )
    parser.add_argument(
        '--output',
        default='lyrics.txt',
        help='Output lyrics file (default: lyrics.txt)'
    )
    parser.add_argument(
        '--words-per-beat',
        type=int,
        default=2,
        help='Words to show per beat (default: 2)'
    )

    args = parser.parse_args()

    # Get lyrics text
    if args.lyrics_text:
        lyrics_text = args.lyrics_text
    elif args.lyrics_file:
        with open(args.lyrics_file, 'r', encoding='utf-8') as f:
            lyrics_text = f.read()
    else:
        print("ERROR: Provide --lyrics-text or --lyrics-file")
        return 1

    # Load beat data
    prep_data = load_prep_data(args.prep_data)
    beat_times = prep_data.get('beats', {}).get('beat_times', [])

    if not beat_times:
        print("ERROR: No beat times found in prep_data.json")
        return 1

    print(f"Found {len(beat_times)} beats")
    print(f"Lyrics: {len(lyrics_text.split())} words")

    # Distribute lyrics
    phrases = distribute_lyrics_on_beats(
        lyrics_text,
        beat_times,
        words_per_beat=args.words_per_beat
    )

    # Save
    save_to_lyrics_format(phrases, args.output)

    print("\nSUCCESS!")
    print(f"Created {len(phrases)} timed phrases")
    print(f"\nNote: This is a simple beat-based distribution.")
    print("For accurate timing, use Whisper or manual editing.")

    return 0


if __name__ == '__main__':
    exit(main())
