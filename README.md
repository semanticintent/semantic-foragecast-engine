# Semantic Foragecast Engine

Audio-driven mascot animation pipeline. Give it a character image and an audio file — it returns a lip-synced, beat-synchronized animated video.

---

## How It Works

```
mascot.png + audio.wav → [Phase 1] → [Phase 2] → [Phase 3] → output.mp4
                          audio prep   compositing  FFmpeg
```

**Phase 1 — Audio Prep** (`prep_audio.py`)
Analyses the audio with LibROSA (beat detection, onset detection, tempo), extracts phoneme timings via Rhubarb Lip Sync (mock fallback included), and parses optional lyrics to a timed word list. Outputs `prep_data.json`.

**Phase 2 — Sprite Composition** (`compose_animation.py`)
Composites the mascot image frame-by-frame: swaps mouth sprites based on phoneme timing, applies beat-synchronized body motion (bob, scale pulse), and overlays background and lighting effects. Pure Python — no external renderer required.

**Phase 3 — Video Export** (`export_video.py`)
Encodes the frame sequence to MP4 via FFmpeg with configurable codec, quality, and resolution presets.

---

## Requirements

- Python 3.9+
- FFmpeg (for Phase 3)
- Rhubarb Lip Sync *(optional — mock fallback used if absent)*

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# Run the full pipeline
python main.py --config config.yaml

# Run only Phase 1 (audio analysis)
python main.py --phase 1

# Run only Phase 2 (composition, requires prep_data.json)
python main.py --phase 2

# Run only Phase 3 (video export, requires frames/)
python main.py --phase 3

# Validate config and inputs without running
python main.py --validate
```

---

## Configuration

All pipeline behaviour is driven by a YAML config file. Minimal example:

```yaml
inputs:
  mascot_image: examples/demo_fox.png
  song_file: examples/demo_song.wav
  lyrics_file: examples/demo_lyrics.txt   # optional

character:
  sprites_dir: sprites/                    # mouth sprites (A B C D E F G H X)
  mouth_region:
    x: 200    # pixel position on mascot image
    y: 280
    w: 112
    h: 70

animation:
  fps: 24
  body_bob_px: 8          # vertical bob amplitude in pixels
  body_bob_beats: true    # sync bob to detected beats
  background_color: [30, 20, 40]

output:
  output_dir: outputs/
  frames_dir: outputs/frames/
  prep_json: outputs/prep_data.json
  video_name: final_video.mp4

video:
  fps: 24
  resolution: [1920, 1080]
  codec: libx264
  quality: high           # ultra_fast | fast | medium | high | production

rhubarb:
  executable_path: null   # set to rhubarb binary path, or leave null for mock
```

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for the full config reference and extension examples.

---

## Mouth Sprites

Phase 2 expects 9 mouth sprite PNG files (transparent background, sized to fit `mouth_region`) in the configured `sprites_dir`. Filenames map to Rhubarb's phoneme set:

| File | Phoneme | Mouth shape |
|---|---|---|
| `mouth_X.png` | X (rest/silence) | Closed |
| `mouth_A.png` | A | Open, oval |
| `mouth_B.png` | B/M/P | Closed, pressed |
| `mouth_C.png` | C | Relaxed open |
| `mouth_D.png` | D | Slightly open |
| `mouth_E.png` | E | Wide, teeth showing |
| `mouth_F.png` | F/V | Bottom lip up |
| `mouth_G.png` | G | Narrow open |
| `mouth_H.png` | H | Open, round |

Use `generate_sprites.py` to create a starter set from your mascot image automatically:

```bash
python generate_sprites.py --image examples/demo_fox.png --out sprites/
```

---

## Project Structure

```
semantic-foragecast-engine/
├── main.py                  # Pipeline orchestrator + CLI
├── prep_audio.py            # Phase 1: audio analysis
├── compose_animation.py     # Phase 2: sprite compositor
├── export_video.py          # Phase 3: FFmpeg export
├── generate_sprites.py      # Helper: generate starter mouth sprites
├── examples/
│   ├── demo_fox.png
│   ├── demo_song.wav
│   └── demo_lyrics.txt
├── sprites/                 # Your mouth sprite PNGs go here
├── config.yaml              # Default configuration
├── requirements.txt
├── pyproject.toml
└── tests/
    ├── test_prep_audio.py
    ├── test_export_video.py
    └── test_e2e_pipeline.py
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

Phase 1 and Phase 3 have full test coverage. Phase 2 compositor tests require Pillow and opencv-python (included in `requirements.txt`).

---

## Roadmap

- [x] Phase 1: Audio analysis (LibROSA + Rhubarb)
- [x] Phase 3: Video export (FFmpeg)
- [x] Phase 2: Sprite compositor with beat-synced body motion
- [ ] AI-generated mouth sprites (Flux/SDXL via local diffusion)
- [ ] Lyric overlay rendering
- [ ] Advanced stage effects (glow, particle bursts, colour grading)
- [ ] Web UI for configuration
- [ ] PyPI package

---

## License

MIT — see [LICENSE](LICENSE)

## Acknowledgements

- [LibROSA](https://librosa.org/) — audio analysis
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) — phoneme extraction
- [FFmpeg](https://ffmpeg.org/) — video encoding
- [Pillow](https://pillow.readthedocs.io/) — image compositing
- [OpenCV](https://opencv.org/) — frame processing
