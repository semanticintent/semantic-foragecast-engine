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

## Phase 2: Orchestrator + Blender Integration (COMPLETED)

Phase 2 provides the main orchestration layer and Blender automation for scene generation.

### Components

#### Main Orchestrator (`main.py`)
Command-line interface that orchestrates the complete pipeline:
- Loads YAML configuration
- Validates inputs
- Runs Phase 1 (audio prep)
- Executes Phase 2 (Blender automation)
- Manages output directories

#### Blender Script (`blender_script.py`)
Automated scene building script that runs inside Blender:
- Scene setup and clearing
- Camera and lighting configuration
- Mascot placeholder creation
- Phoneme shape keys generation
- Lip-sync animation (stub)
- Gesture animation (beat-synced)
- Lyrics text overlay animation
- Render settings configuration

#### Configuration (`config.yaml`)
YAML-based configuration system with:
- Input file paths (audio, image, lyrics)
- Video settings (resolution, fps, render engine)
- Style configuration (colors, lighting presets)
- Animation settings (gestures, lip-sync, effects)
- Advanced options (preview mode, threading)

### Usage

```bash
# Run full pipeline with default config
python main.py

# Use custom configuration
python main.py --config custom.yaml

# Run only specific phases
python main.py --phase 1  # Audio prep only
python main.py --phase 2  # Blender only (requires Phase 1 output)

# Validate configuration without running
python main.py --validate

# Enable verbose output
python main.py --verbose
```

### Configuration Example

See `config.yaml` for the complete configuration schema. Key sections:

```yaml
inputs:
  mascot_image: "assets/fox.png"
  song_file: "assets/song.wav"
  lyrics_file: "assets/lyrics.txt"

video:
  resolution: [1920, 1080]
  fps: 24
  render_engine: "EEVEE"

style:
  lighting: "jazzy"
  colors:
    primary: [0.8, 0.3, 0.9]
    secondary: [0.3, 0.8, 0.9]

animation:
  enable_lipsync: true
  enable_gestures: true
  enable_lyrics: true
  gesture_intensity: 0.7
```

### Sample Assets

The `assets/` directory includes complete test assets:
- `song.wav` - 30-second musical test track with chord progression
- `fox.png` - 512x512 sample mascot image
- `lyrics.txt` - Timed lyrics in pipe-delimited format
- `create_sample_assets.py` - Script to regenerate assets

Generate new assets with:
```bash
python assets/create_sample_assets.py
```

### Blender Requirements

Phase 2 requires Blender 4.2+ for full functionality:

```bash
# Download Blender
# https://www.blender.org/download/

# Windows: Install to default location or set in config.yaml
# Linux/Mac: Ensure 'blender' is in PATH

# Test Blender integration
python main.py --phase 2  # Requires Phase 1 output first
```

**Note**: Blender automation is currently a **stub implementation**. The script sets up the scene structure, creates placeholder objects, and demonstrates the animation pipeline, but does not perform full rendering. This provides the foundation for Phase 3.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the complete pipeline (uses default config.yaml)
python main.py

# 3. Or run individual phases
python main.py --phase 1  # Audio prep only
python main.py --phase 2  # Blender animation only (requires Phase 1 data)

# 4. Validate configuration
python main.py --validate
```

## Architecture

### Phase 1: Prep Module ✅ **COMPLETED**
- Audio analysis (LibROSA)
- Beat/onset detection
- Phoneme extraction (Rhubarb)
- Lyrics parsing
- JSON output

### Phase 2: Orchestrator + Blender ✅ **COMPLETED**
- Main orchestration script (`main.py`)
- Blender automation (`blender_script.py`)
- Scene setup and configuration
- Animation generation (stub)
- CLI interface with phase control

### Phase 3: Rendering + Export (PLANNED)
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
├── main.py                     # Phase 2: Main orchestrator CLI
├── prep_audio.py               # Phase 1: Audio prep module
├── blender_script.py           # Phase 2: Blender automation (bpy)
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── assets/                     # Sample input files
│   ├── song.wav                # 30s test audio
│   ├── fox.png                 # Sample mascot image
│   ├── lyrics.txt              # Timed lyrics
│   └── create_sample_assets.py # Asset generator
├── outputs/                    # Generated outputs
│   ├── prep_data.json          # Phase 1 output
│   ├── sandbox_demo_output.json
│   └── frames/                 # Rendered frames (Phase 3)
├── tests/                      # Unit tests
│   ├── test_prep_audio.py      # Phase 1 tests
│   ├── sandbox_demo.py         # Demo script
│   ├── test_output.log
│   ├── sandbox_demo_output.log
│   └── phase1_integration_test.log
└── docs/                       # Documentation
    ├── prompt.md
    └── Video Generation Pipeline.md
```

## Next Steps (Phase 3)

Phase 3 will complete the pipeline with full rendering and export:

1. Implement full mascot rigging (image-to-mesh conversion)
2. Complete animation implementations (not just stubs)
3. Add stage effects (fog, particles, dynamic lighting)
4. Implement FFmpeg export module
5. Create end-to-end integration tests
6. Add preview mode and batch processing

## License

Open source - details TBD

## References

- [LibROSA Documentation](https://librosa.org/)
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Requirements Document](docs/Video%20Generation%20Pipeline.md)
