# Semantic Foragecast Engine

A modular, non-AI procedural video generation pipeline for creating broadcast-quality music videos with animated mascots.

## Project Overview

This pipeline automates the creation of short (30-60s), high-quality MP4 videos featuring a customizable mascot that lip-syncs to user-provided songs, with kinetic lyrics and dynamic stage effects. Built with Python and Blender, emphasizing transparency, offline operation, and extensibility.

## Phase 1: Prep Module (COMPLETED)

The Prep Module (`prep_audio.py`) handles audio processing, beat detection, phoneme extraction, and lyrics parsing.

### Features

- **Audio Loading**: Load WAV/MP3 files with LibROSA
- **Beat Detection**: Automatic beat and onset detection for syncing animations
- **Phoneme Extraction**: Rhubarb Lip Sync integration with mock fallback
- **Lyrics Parsing**: Parse timed lyrics from TXT files
- **JSON Output**: Structured data for downstream processing
- **Cross-Platform**: Windows 11 optimized with portable path handling

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Download Rhubarb Lip Sync
# https://github.com/DanielSWolf/rhubarb-lip-sync
# Place rhubarb.exe in project root or add to PATH
```

### Usage

#### Command Line

```bash
# Basic usage
python prep_audio.py path/to/song.wav --output output.json

# With lyrics
python prep_audio.py path/to/song.wav --lyrics path/to/lyrics.txt --output output.json

# With Rhubarb path
python prep_audio.py path/to/song.wav --rhubarb path/to/rhubarb.exe --output output.json
```

#### Python API

```python
from prep_audio import process_audio

result = process_audio(
    audio_path='assets/song.wav',
    lyrics_path='assets/lyrics.txt',
    rhubarb_path='rhubarb.exe',  # Optional
    output_json='outputs/result.json'
)

print(f"Detected {len(result['beats']['beat_times'])} beats")
print(f"Generated {len(result['phonemes'])} phonemes")
print(f"Parsed {len(result['timed_words'])} words")
```

### Lyrics Format

Lyrics should use the pipe-delimited format:

```
0:00-0:05 Hello|world|this|is|a|test
0:06-0:10 Another|line|here
0:11-0:15 Final|words
```

Format: `START_TIME-END_TIME word1|word2|word3`

### JSON Output Structure

```json
{
  "audio": {
    "path": "path/to/audio.wav",
    "duration": 5.0,
    "sample_rate": 22050,
    "tempo": 120.0
  },
  "beats": {
    "beat_times": [0.5, 1.0, 1.5],
    "beat_frames": [21, 42, 64],
    "onset_times": [0.5, 1.0, 1.5],
    "onset_frames": [21, 42, 64]
  },
  "phonemes": [
    {"time": 0.0, "phoneme": "X"},
    {"time": 0.15, "phoneme": "A"}
  ],
  "timed_words": [
    {"start": 0.0, "end": 1.0, "word": "Hello"},
    {"start": 1.0, "end": 2.0, "word": "world"}
  ]
}
```

### Testing

```bash
# Run unit tests
python tests/test_prep_audio.py

# Run sandbox demo (generates 5s test tone)
python tests/sandbox_demo.py
```

**Test Results**: 100% success rate (7/7 tests passing)

## Architecture

### Phase 1: Prep Module ✅
- Audio analysis (LibROSA)
- Beat/onset detection
- Phoneme extraction (Rhubarb)
- Lyrics parsing
- JSON output

### Phase 2: Orchestrator + Blender (UPCOMING)
- Main orchestration script
- Blender automation (bpy)
- Scene setup and rigging
- Animation generation

### Phase 3: Rendering + Export (UPCOMING)
- Blender rendering (Eevee/Cycles)
- FFmpeg encoding
- MP4 output

## Technical Stack

- **Python 3.11+**: Core scripting
- **LibROSA 0.10.1**: Audio analysis
- **NumPy 1.26.4**: Numerical computing
- **SciPy**: Signal processing
- **Rhubarb Lip Sync**: Phoneme extraction (optional)
- **Blender 4.2+**: 3D animation (Phase 2)
- **FFmpeg**: Video encoding (Phase 3)

## Platform Support

- **Primary**: Windows 11
- **Secondary**: Linux, macOS (cross-platform design)
- **Offline**: No cloud dependencies

## Project Structure

```
semantic-foragecast-engine/
├── prep_audio.py           # Phase 1: Audio prep module
├── requirements.txt        # Python dependencies
├── assets/                 # Sample inputs
├── outputs/                # Generated outputs
│   └── sandbox_demo_output.json
├── tests/                  # Unit tests
│   ├── test_prep_audio.py
│   ├── sandbox_demo.py
│   ├── test_output.log
│   └── sandbox_demo_output.log
└── docs/                   # Documentation
    ├── prompt.md
    └── Video Generation Pipeline.md
```

## Next Steps (Phase 2)

1. Implement orchestrator (`main.py`)
2. Create Blender automation script (`blender_script.py`)
3. Develop mascot rigging system
4. Add animation generation (lip-sync, gestures, lyrics)
5. Integrate stage effects (lighting, particles)

## License

Open source - details TBD

## References

- [LibROSA Documentation](https://librosa.org/)
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Requirements Document](docs/Video%20Generation%20Pipeline.md)
