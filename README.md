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

`generate_sprites.py` supports two modes:

```bash
# V1 — geometric: instant, zero GPU, skin-tone matched cartoon shapes
python generate_sprites.py --image examples/demo_fox.png --out sprites/

# V2 — AI: SD 1.5 inpainting on Apple MPS (~15s/phoneme, ~2.5 min total)
python generate_sprites.py --image examples/demo_fox.png --out sprites/ --mode ai
```

The AI mode uses `StableDiffusionInpaintPipeline` with an elliptical mask centred on the mouth region and phoneme-specific prompts. Sprites are feathered into the mascot face using a Gaussian ellipse mask at composite time.

---

## Project Structure

```
semantic-foragecast-engine/
├── main.py                  # Pipeline orchestrator + CLI
├── prep_audio.py            # Phase 1: audio analysis
├── compose_animation.py     # Phase 2: sprite compositor
├── export_video.py          # Phase 3: FFmpeg export
├── generate_sprites.py      # Helper: geometric (V1) + AI inpainting (V2) sprites
├── examples/
│   ├── demo_fox.png         # Built-in fox mascot (RGBA, transparent bg)
│   ├── mascot_cat.png       # AI-generated cat mascot (SD 1.5 text-to-image)
│   ├── demo_song.wav
│   └── demo_lyrics.txt
├── sprites/                 # Fox mouth sprites (geometric or AI)
├── sprites_cat/             # Cat mouth sprites
├── config.yaml              # Fox pipeline configuration
├── config_cat.yaml          # Cat pipeline configuration
├── requirements.txt
├── pyproject.toml
└── tests/
    ├── test_prep_audio.py
    ├── test_compose_animation.py
    ├── test_generate_sprites.py
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

### Shipped
- [x] Phase 1: Audio analysis — LibROSA beat detection, Rhubarb phoneme timing, lyrics parsing
- [x] Phase 2: Sprite compositor — phoneme-driven mouth swap, beat-synced body bob, feathered compositing
- [x] Phase 3: Video export — FFmpeg MP4 with configurable codec and quality presets
- [x] Geometric mouth sprites — V1, instant, skin-tone matched cartoon shapes (9 phonemes)
- [x] AI mouth sprites — V2, SD 1.5 inpainting on Apple MPS, phoneme-specific prompts
- [x] Lyric word overlay — per-word pill (SF Rounded font, drop shadow, beat-synced)
- [x] Transparent mascot backgrounds — saturation + flood-fill alpha removal pipeline
- [x] AI mascot generation — SD 1.5 text-to-image → background removal → full pipeline
- [x] Multi-mascot support — config-based character swap (fox + cat demonstrated)
- [x] Test suite — 40 tests across all pipeline phases (pytest + coverage)
- [x] Docs site — [foragecast.semanticintent.dev](https://foragecast.semanticintent.dev) (React/Vite, Cloudflare Pages)

### Next
- [ ] Cartoon LoRA — fine-tuned SD model for cleaner AI mascot generation on first try
- [ ] Real Rhubarb lip-sync — replace mock phoneme data with actual binary
- [ ] Head/body split — separate mascot layers for independent head-bob vs body-bob
- [ ] AI mouth sprites per character — cat, owl, and future mascots get V2 sprite sets
- [ ] Stage effects — glow, colour grading, vignette, particle bursts on beat drops
- [ ] PyPI package — `pip install semantic-foragecast-engine`

---

## License

MIT — see [LICENSE](LICENSE)

## Acknowledgements

- [LibROSA](https://librosa.org/) — audio analysis
- [Rhubarb Lip Sync](https://github.com/DanielSWolf/rhubarb-lip-sync) — phoneme extraction
- [FFmpeg](https://ffmpeg.org/) — video encoding
- [Pillow](https://pillow.readthedocs.io/) — image compositing
- [OpenCV](https://opencv.org/) — frame processing
