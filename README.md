# Semantic Foragecast Engine

> **Production-ready pipeline for audio-driven animation in Blender**
>
> A configuration-first, modular system demonstrating Blender automation, audio analysis integration, and headless rendering architecture.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Blender 4.0+](https://img.shields.io/badge/blender-4.0+-orange.svg)](https://www.blender.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI Status](https://github.com/semanticintent/semantic-foragecast-engine/workflows/CI%20-%20Semantic%20Foragecast%20Engine/badge.svg)](https://github.com/semanticintent/semantic-foragecast-engine/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/semanticintent/semantic-foragecast-engine?style=social)](https://github.com/semanticintent/semantic-foragecast-engine/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/semanticintent/semantic-foragecast-engine)](https://github.com/semanticintent/semantic-foragecast-engine/issues)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue)](https://github.com/semanticintent/semantic-foragecast-engine#documentation)
[![Featured](https://img.shields.io/badge/Featured-LinkedIn-0077B5)](https://foragecast.dev)

---

## What This Is

A **fully functional pipeline** that transforms audio files into animated videos with synchronized lip movements, beat-reactive gestures, and timed lyrics — all driven by YAML configuration files instead of manual animation.

**But more importantly**: A **technical demonstration** of production-ready Blender automation, showcasing:
- ✅ Configuration-first architecture (no code changes for different outputs)
- ✅ Headless rendering (cloud/container deployment ready)
- ✅ Modular 4-phase pipeline with clean separation of concerns
- ✅ Extensible plugin system (easy to add new animation modes)
- ✅ Real-world performance benchmarks (tested in cloud environments)

**Use Case**: Automated music video generation (lyric videos, podcasts, educational content)

**Learning Value**: Demonstrates Blender Python API patterns, audio analysis integration, and pipeline architecture rarely documented elsewhere.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Blender 4.0+ and FFmpeg
# https://www.blender.org/download/
# https://ffmpeg.org/download.html

# 3. Run the pipeline with test config (renders in 4-6 minutes)
python main.py --config config_ultra_fast.yaml

# 4. Find output video
ls outputs/ultra_fast/ultra_fast.mp4
```

**Result**: 30-second video with animated mascot, lip sync, and lyrics.

---

## Documentation

### For Developers

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flow, extension points, deployment patterns
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Step-by-step tutorials for adding modes, effects, and audio analysis
- **[CASE_STUDIES.md](CASE_STUDIES.md)** - Real-world benchmarks, cloud rendering, performance optimization

### For Users

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Quality/speed configurations, testing workflow
- **[AUTOMATED_LYRICS_GUIDE.md](AUTOMATED_LYRICS_GUIDE.md)** - Whisper integration for auto lyrics timing
- **[POSITIONING_GUIDE.md](POSITIONING_GUIDE.md)** - Scene layout and debug visualization

### Technical Docs

- **[PIPELINE_TEST_EVALUATION.md](PIPELINE_TEST_EVALUATION.md)** - Complete test results from cloud environment
- **[CROSS_PLATFORM_DEV_GUIDE.md](CROSS_PLATFORM_DEV_GUIDE.md)** - Windows/Linux development setup

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Phase 1   │────▶│   Phase 2    │────▶│   Phase 3   │
│ Audio Prep  │     │  Rendering   │     │   Export    │
│             │     │              │     │             │
│ - Beats     │     │ - 2D/3D Mode │     │ - MP4       │
│ - Phonemes  │     │ - Lip Sync   │     │ - H.264     │
│ - Lyrics    │     │ - Gestures   │     │ - Audio Sync│
└─────────────┘     └──────────────┘     └─────────────┘
      ↓                     ↓                     ↓
  prep_data.json       PNG frames             final.mp4
```

**Key Design Principles**:
- **Separation of concerns**: Each phase independent, cacheable outputs
- **Configuration over code**: YAML drives all behavior
- **Extensibility**: Plugin-style animation modes
- **Production-ready**: Headless rendering, error handling, validation

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system design.

---

## Features

### Core Pipeline (4 Phases - All Complete ✅)

**Phase 1: Audio Preprocessing**
- Beat/onset detection (LibROSA)
- Phoneme extraction (Rhubarb Lip Sync or mock fallback)
- Lyrics parsing (manual or automated with Whisper)
- JSON output for downstream processing

**Phase 2: Blender Rendering**
- 2D Grease Pencil mode (fast, stylized)
- 3D mesh mode (planned)
- Hybrid mode (planned)
- Automated lip sync from phonemes
- Beat-synchronized gestures
- Timed lyric text objects

**Phase 3: Video Export**
- FFmpeg integration (H.264, H.265, VP9)
- Quality presets (low, medium, high, ultra)
- Preview mode for rapid iteration
- Audio synchronization

**Phase 4: 2D Animation System**
- Image-to-stroke conversion
- Grease Pencil animation
- ~2x faster rendering than 3D
- Stylized artistic output

### Technical Highlights

**Headless Rendering**
- Tested in Docker containers with Xvfb
- No GUI required
- Cloud deployment ready (AWS, GCP)
- See [CASE_STUDIES.md](CASE_STUDIES.md) for cloud setup

**Performance Optimization**
- Progressive quality configs (180p → 360p → 1080p)
- Render time: 4 min (ultra-fast) to 50 min (production) for 30s video
- Benchmarks included in [CASE_STUDIES.md](CASE_STUDIES.md)

**Automated Lyrics**
- Whisper integration for auto-transcription
- Gentle forced alignment
- Beat-based distribution
- See [AUTOMATED_LYRICS_GUIDE.md](AUTOMATED_LYRICS_GUIDE.md)

---

## Configuration-Based Workflow

**No code changes needed** - just swap YAML files:

```yaml
# config_ultra_fast.yaml (testing - 4 min render)
video:
  resolution: [320, 180]
  fps: 12
  samples: 16

# config_quick_test.yaml (preview - 12 min render)
video:
  resolution: [640, 360]
  fps: 24
  samples: 32

# config.yaml (production - 50 min render)
video:
  resolution: [1920, 1080]
  fps: 24
  samples: 64
```

Run with: `python main.py --config <config_file>`

---

## Usage Examples

### Basic Pipeline

```bash
# Run complete pipeline (all 3 phases)
python main.py --config config.yaml

# Run individual phases
python main.py --config config.yaml --phase 1  # Audio prep only
python main.py --config config.yaml --phase 2  # Render only
python main.py --config config.yaml --phase 3  # Export only

# Validate configuration
python main.py --config config.yaml --validate
```

### Automated Lyrics

```bash
# Instead of manual lyrics.txt, auto-generate with Whisper
pip install openai-whisper
python auto_lyrics_whisper.py assets/song.wav --output assets/lyrics.txt

# Then run pipeline as normal
python main.py
```

### Quick Testing

```bash
# Use ultra-fast config for rapid iteration (4 min for 30s video)
python main.py --config config_ultra_fast.yaml

# Or use the quick test script
python quick_test.py --auto-lyrics --debug
```

---

## Extension Examples

### Adding a New Animation Mode

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for complete tutorials.

**Quick example** - Add particle system mode:

1. Create `particle_system.py` with builder class
2. Register in `blender_script.py` dispatcher
3. Add `mode: "particles"` to config
4. Run pipeline - no other code changes needed

**Full tutorial with code samples** in DEVELOPER_GUIDE.md

### Adding a New Effect

**Example** - Camera shake on beats:

```python
# effects.py
class CameraShakeEffect:
    def apply(self, camera):
        for beat_frame in self.prep_data['beats']['beat_frames']:
            # Add shake keyframes
            camera.location = shake_position
            camera.keyframe_insert(data_path="location", frame=beat_frame)
```

Add to config:
```yaml
effects:
  camera_shake:
    enabled: true
    intensity: 0.2
```

**Full implementation** in DEVELOPER_GUIDE.md

---

## Project Structure

```
semantic-foragecast-engine/
├── main.py                      # Orchestrator
├── prep_audio.py                # Phase 1: Audio analysis
├── blender_script.py            # Phase 2: Blender automation
├── grease_pencil.py             # 2D animation mode
├── export_video.py              # Phase 3: FFmpeg export
├── config.yaml                  # Production config
├── config_ultra_fast.yaml       # Fast testing config
├── config_360p_12fps.yaml       # Mid-quality config
├── quick_test.py                # Automated testing script
├── auto_lyrics_whisper.py       # Automated lyrics (Whisper)
├── auto_lyrics_gentle.py        # Automated lyrics (Gentle)
├── auto_lyrics_beats.py         # Beat-based lyrics
├── assets/                      # Sample inputs
│   ├── song.wav                 # 30s test audio
│   ├── fox.png                  # Mascot image
│   └── lyrics.txt               # Timed lyrics
├── outputs/                     # Generated outputs
│   ├── ultra_fast/              # Fast test outputs
│   ├── test_360p/               # Mid-quality outputs
│   └── production/              # High-quality outputs
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System design
│   ├── DEVELOPER_GUIDE.md       # Extension tutorials
│   ├── CASE_STUDIES.md          # Benchmarks & examples
│   ├── TESTING_GUIDE.md         # Quality/speed configs
│   ├── AUTOMATED_LYRICS_GUIDE.md
│   └── POSITIONING_GUIDE.md
└── tests/                       # Unit tests
```

---

## Performance Benchmarks

**30-second video render times** (tested in cloud container, CPU only):

| Config | Resolution | FPS | Samples | Render Time | File Size | Use Case |
|--------|-----------|-----|---------|-------------|-----------|----------|
| Ultra Fast | 320x180 | 12 | 16 | **4 min** | 489 KB | Testing pipeline |
| 360p 12fps | 640x360 | 12 | 16 | **6 min** | 806 KB | Quality check |
| Quick Test | 640x360 | 24 | 32 | **13 min** | ~1.5 MB | Preview |
| Production | 1920x1080 | 24 | 64 | **50 min** | ~8 MB | Final output |

**Key finding**: 360p @ 12fps is the sweet spot for development (6 min, good quality)

See [CASE_STUDIES.md](CASE_STUDIES.md) for complete benchmarks and optimization strategies.

---

## Technical Stack

**Core**:
- Python 3.11+
- Blender 4.0+ (Python API)
- FFmpeg 4.4+

**Audio Analysis**:
- LibROSA 0.10.1 (beat detection, tempo)
- Rhubarb Lip Sync (phoneme extraction)
- Whisper (optional, auto lyrics)

**Rendering**:
- Blender EEVEE engine
- Grease Pencil for 2D mode
- Xvfb for headless rendering

**Configuration**:
- PyYAML 6.0.1
- JSON for intermediate data

---

## Platform Support

- **Development**: Windows 11, macOS, Linux
- **Production**: Ubuntu 22.04/24.04 (tested in Docker)
- **Cloud**: AWS EC2, GCP Compute (headless mode)
- **Offline**: No cloud dependencies required

See [CROSS_PLATFORM_DEV_GUIDE.md](CROSS_PLATFORM_DEV_GUIDE.md) for setup instructions.

---

## Real-World Applications

**Tested Use Cases**:
1. **Music lyric videos** - Automated generation for indie musicians
2. **Podcast visualization** - Animated host for audio podcasts
3. **Educational content** - Narrated lessons with animated teacher
4. **Brand mascot videos** - Company mascot delivering announcements

**Deployment Scenarios**:
- Local rendering (Windows/Mac development)
- Docker containers (reproducible builds)
- Cloud rendering (AWS/GCP for batch processing)
- CI/CD integration (automated video generation)

See [CASE_STUDIES.md](CASE_STUDIES.md) for detailed case studies.

---

## Why This Project Exists

**Problem**: Few production-ready examples exist for Blender automation. Most tutorials show basic concepts but not real-world architecture.

**Solution**: This project demonstrates:
- How to structure a multi-phase pipeline
- Configuration-first design patterns
- Headless rendering in cloud environments
- Audio-driven procedural animation
- Extensible plugin architecture

**Target Audience**:
- Developers learning Blender Python API
- Pipeline engineers building automation tools
- DevOps teams deploying headless rendering
- Anyone needing automated video generation

---

## Detailed Usage

### Phase 1: Audio Preparation

```bash
# Run audio prep manually
python prep_audio.py assets/song.wav --output outputs/prep_data.json

# With lyrics
python prep_audio.py assets/song.wav --lyrics assets/lyrics.txt --output outputs/prep_data.json

# With Rhubarb for real phonemes (not mock)
python prep_audio.py assets/song.wav --rhubarb /path/to/rhubarb --output outputs/prep_data.json
```

**Output**: `prep_data.json` containing beats, phonemes, and lyrics timing

### Phase 2: Blender Rendering

```bash
# Render with 2D Grease Pencil mode (fastest)
python main.py --config config.yaml --phase 2

# Enable debug visualization (colored position markers)
# Set debug_mode: true in config.yaml, then:
python main.py --config config.yaml --phase 2
```

**Output**: PNG frames in `outputs/*/frames/`

### Phase 3: Video Export

```bash
# Encode frames to video
python main.py --config config.yaml --phase 3

# Or use export_video.py directly
python export_video.py \
  --frames outputs/frames \
  --audio assets/song.wav \
  --output outputs/video.mp4 \
  --quality high
```

**Output**: Final MP4 video

### Automated Lyrics

```bash
# Method 1: Whisper (auto-transcribe, no lyrics needed)
pip install openai-whisper
python auto_lyrics_whisper.py assets/song.wav --output assets/lyrics.txt

# Method 2: Gentle (align known lyrics to audio)
docker run -p 8765:8765 lowerquality/gentle
python auto_lyrics_gentle.py --audio song.wav --lyrics text.txt --output lyrics.txt

# Method 3: Beat-based (distribute lyrics on beats)
python auto_lyrics_beats.py --prep-data prep_data.json --lyrics-text "Your lyrics here"
```

See [AUTOMATED_LYRICS_GUIDE.md](AUTOMATED_LYRICS_GUIDE.md) for detailed comparison.

---

## Configuration Reference

### Video Settings

```yaml
video:
  resolution: [1920, 1080]  # Output resolution
  fps: 24                   # Frame rate
  render_engine: "EEVEE"    # EEVEE (fast) or CYCLES (quality)
  samples: 64               # Render samples (16-256)
  codec: "libx264"          # Video codec
  quality: "high"           # low, medium, high, ultra
```

### Animation Settings

```yaml
animation:
  mode: "2d_grease"         # 2d_grease, 3d, or hybrid
  enable_lipsync: true      # Phoneme-based lip sync
  enable_gestures: true     # Beat-synced movement
  enable_lyrics: true       # Timed lyric text
  gesture_intensity: 0.7    # 0.0-1.0
```

### Style Settings

```yaml
style:
  lighting: "jazzy"         # Lighting preset
  colors:
    primary: [0.8, 0.3, 0.9]
    secondary: [0.3, 0.8, 0.9]
    accent: [0.9, 0.8, 0.3]
  background: "solid"       # solid or hdri

gp_style:                   # 2D mode only
  stroke_thickness: 3
  ink_type: "clean"         # clean, sketchy, wobbly
  enable_wobble: false
  wobble_intensity: 0.5
```

### Advanced Settings

```yaml
advanced:
  debug_mode: false         # Show position markers
  preview_mode: false       # Low-res preview
  preview_scale: 0.5        # Preview resolution scale
  threads: null             # Render threads (null = auto)
  verbose: true             # Detailed logging
```

---

## Testing

### Unit Tests

```bash
# Run all tests
python -m unittest discover tests/

# Test specific phase
python tests/test_prep_audio.py
python tests/test_export_video.py
```

### Integration Tests

```bash
# Test complete pipeline with ultra-fast config
python main.py --config config_ultra_fast.yaml

# Automated testing script
python quick_test.py
```

### Manual Verification

```bash
# Enable debug mode to visualize positioning
# In config.yaml: debug_mode: true
python main.py --config config.yaml --phase 2

# Check frame 100 for colored markers
ls outputs/*/frames/frame_0100.png
```

---

## Troubleshooting

### Blender Not Found

```bash
# Linux: Install via apt
sudo apt-get install blender

# Mac: Install via Homebrew
brew install --cask blender

# Windows: Download installer
# https://www.blender.org/download/
```

### Headless Rendering Fails

```bash
# Install Xvfb virtual display
sudo apt-get install xvfb

# Run with xvfb-run
xvfb-run -a python main.py --config config.yaml --phase 2
```

### FFmpeg Not Found

```bash
# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

### Lyrics Behind Mascot

Check positioning in config - text should be at `y=-2.0, z=0.2`:
- See [POSITIONING_GUIDE.md](POSITIONING_GUIDE.md)
- Enable `debug_mode: true` to see position markers

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Update documentation
5. Submit pull request

### What We're Looking For

- New animation modes (3D, particle systems, etc.)
- Audio analysis improvements (melody extraction, harmony)
- Effects (camera movements, post-processing)
- Performance optimizations
- Bug fixes with tests
- Documentation improvements

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for extension tutorials.

---

## Roadmap

### Completed ✅
- [x] Phase 1: Audio preprocessing
- [x] Phase 2: Blender automation
- [x] Phase 3: Video export
- [x] Phase 4: 2D Grease Pencil mode
- [x] Headless rendering support
- [x] Automated lyrics (Whisper)
- [x] Debug visualization
- [x] Comprehensive documentation

### Planned 🚧
- [ ] 3D mesh animation mode
- [ ] Hybrid mode (2D + 3D)
- [ ] Advanced effects (fog, particles, camera shake)
- [ ] Melody extraction and pitch-based animation
- [ ] Multi-character support
- [ ] Web UI for configuration
- [ ] Real-time preview

---

## FAQ

**Q: Can I use this for commercial projects?**
A: Yes, MIT licensed. Attribution appreciated.

**Q: Why is rendering slow?**
A: Use `config_ultra_fast.yaml` for testing (4 min). Production 1080p takes 50 min for 30s video.

**Q: Can I run this without Blender installed?**
A: No, Phase 2 requires Blender. But you can run Phase 1 (audio prep) standalone.

**Q: Does this require GPU?**
A: No, CPU rendering works. GPU recommended for faster production renders.

**Q: Can I deploy this in Docker?**
A: Yes, see [CASE_STUDIES.md](CASE_STUDIES.md) for cloud deployment example.

**Q: Is this AI-generated?**
A: No, this is procedural animation based on audio analysis, not machine learning.

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- [LibROSA](https://librosa.org/) - Audio analysis library
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) - Phoneme extraction
- [Blender](https://www.blender.org/) - 3D creation suite
- [FFmpeg](https://ffmpeg.org/) - Video encoding
- [Whisper](https://github.com/openai/whisper) - Speech recognition

---

## Links

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/semanticintent/semantic-foragecast-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/semanticintent/semantic-foragecast-engine/discussions)

---

**Built with ❤️ for the Blender automation community**
