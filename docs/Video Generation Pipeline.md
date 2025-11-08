# Video Generation Pipeline: Requirements Document

## Version History
- **Version**: 1.0
- **Date**: November 07, 2025
- **Author**: Grok (xAI Assistant)
- **Purpose**: Defines the functional and non-functional requirements for a modular, non-AI procedural video generation pipeline focused on creating high-quality music videos featuring an animated mascot.

## Project Overview
This pipeline automates the creation of short (30-60s), broadcast-quality MP4 videos where a customizable mascot (e.g., cartoon animal like a fox) lip-syncs a user-provided song, with on-screen kinetic lyrics and dynamic stage effects (e.g., flashing lights, spotlights). The system uses Python scripting for orchestration and Blender for rendering, emphasizing transparency, offline operation, and extensibility. Target use: Social media shorts, promotional content, or educational videos.

## Stakeholder
- **Primary User**: Content creator/developer on Windows 11, with basic Python/Blender familiarity.
- **Secondary**: Team collaborators for iteration.

## Functional Requirements
### Core Features
1. **Input Handling**:
   - Accept: AI-generated mascot image (PNG/JPG), song audio (MP3/WAV), timed lyrics (TXT/SRT).
   - Validate inputs (e.g., audio duration ≤ 60s, image resolution ≥ 512x512).

2. **Mascot Preparation**:
   - Convert 2D image to rigged 3D model (low-poly head/body with shape keys for mouth poses).
   - Auto-generate basic rig (bones for head, arms) for gestures.

3. **Audio Processing**:
   - Detect beats/onsets for syncing gestures and lights.
   - Generate phoneme timings for lip-sync (rule-based, no neural nets).

4. **Animation Generation**:
   - Lip-sync: Map phonemes to mouth shape keys with smooth interpolation.
   - Body Gestures: Idle sway + beat-synced waves (e.g., arm pumps).
   - Lyrics: Animate text overlays (scale, glow, bounce) timed to words.

5. **Stage Effects**:
   - Procedural lighting: Pulsing spotlights, random flashes (color, intensity) synced to beats.
   - Atmosphere: Fog volumes, particle sparks, HDRI backdrop for concert vibe.

6. **Rendering & Output**:
   - Compose scene in Blender (Eevee for previews, Cycles for finals).
   - Export: 4K/24fps MP4 with H.265 encoding, embedded audio.
   - Options: Low-res preview mode, batch processing.

### User Stories
- As a user, I want to upload a fox image and song, so the script auto-rigs and syncs a singing performance in <5 mins setup.
- As a user, I want YAML config for styles (e.g., "jazzy stage: purple hues"), so I can reuse for variants without recoding.
- As a user, I want error logs and previews, so I can debug without full renders.

## Non-Functional Requirements
### Performance
- Render time: ≤10 mins for 30s 4K clip on mid-tier GPU (e.g., RTX 3060).
- Script execution: <30s for prep (audio analysis, phoneme gen).

### Usability
- CLI interface (e.g., `python generate_video.py --config config.yaml`).
- Modular code: Functions for each step, with docstrings.
- Documentation: Inline comments + this README.

### Reliability & Security
- Offline-only: No cloud deps; handle file paths cross-platform (Win11 focus).
- Error Handling: Graceful failures (e.g., "Invalid audio: retry?").
- Versioning: Git-friendly; deps pinned (requirements.txt).

### Constraints
- Platform: Windows 11 primary; Python 3.11+.
- Budget: Free/open-source tools only.
- Scalability: Handle up to 10 batches/day; no real-time.

### Assumptions & Dependencies
- User has Blender 4.2+, FFmpeg, Rhubarb installed.
- No advanced rigging skills needed—script automates basics.

## Acceptance Criteria
- Pipeline produces a playable MP4 with synced lips, visible lyrics, and effects.
- Unit tests: Audio beat detection accuracy >90% on sample tracks.
- Integration Test: End-to-end run with provided assets yields <5% sync drift.

## Risks & Mitigations
- Risk: Blender scripting bugs. *Mitigation*: Modular tests in Python REPL.
- Risk: Phoneme accuracy for non-English songs. *Mitigation*: Fallback to generic mouth opens.

---

# Video Generation Pipeline: Technical Implementation Document

## Version History
- **Version**: 1.0
- **Date**: November 07, 2025
- **Author**: Grok (xAI Assistant)
- **Purpose**: Outlines the architecture, tools, and step-by-step implementation for the requirements above.

## System Architecture
The pipeline is a Python-orchestrated workflow: Prep (audio/image) → Blender Automation (scene build/animate) → Render/Export. It's event-driven via functions, with YAML config for inputs/styles.

### High-Level Diagram (Text-Based)
```
[Inputs: Image, Song, Lyrics] --> Python Prep (LibROSA + Rhubarb) --> [Phonemes, Beats]
                                                        |
                                                        v
[Blender Script (bpy)] <--> [Rig Mascot] --> [Animate: Lips/Gestures/Lyrics/Lights] --> [Render Frames]
                                                        |
                                                        v
[FFmpeg Composite] --> [Output MP4]
```

- **Layers**:
  - **Orchestrator**: `main.py` (CLI entry, calls modules).
  - **Prep Module**: Audio analysis, phoneme gen.
  - **Blender Module**: `blender_script.py` (run headless).
  - **Export Module**: Post-processing.

## Tools & Dependencies
| Tool/Lib | Purpose | Version/Install |
|----------|---------|-----------------|
| **Python** | Core scripting | 3.11+ (python.org) |
| **Blender** | 3D animation/rendering | 4.2+ (blender.org; Windows installer) |
| **bpy** | Blender Python API | Bundled in Blender |
| **LibROSA** | Beat/onset detection | `pip install librosa` |
| **PyDub** | Audio mixing/trimming | `pip install pydub` |
| **Rhubarb Lip Sync** | Phoneme timing | Download .exe from GitHub; subprocess call |
| **FFmpeg** | Encoding/export | Static build (ffmpeg.org; add to PATH) |
| **YAML** | Config parsing | `pip install pyyaml` |
| **NumPy/Matplotlib** | Data viz (previews) | Bundled/pre-installed |

- **requirements.txt**:
  ```
  librosa==0.10.1
  pydub==0.25.1
  pyyaml==6.0.1
  numpy==1.26.4
  ```

- **One-Time Setup (Win11)**:
  1. Install Python/Blender/FFmpeg.
  2. `pip install -r requirements.txt`.
  3. Download Rhubarb.exe to project root.
  4. Test: `blender --background --python test_bpy.py` (echo "bpy" script).

## Implementation Steps
### 1. Project Structure
```
video_pipeline/
├── main.py                 # CLI orchestrator
├── config.yaml             # Inputs/styles
├── prep_audio.py           # LibROSA + Rhubarb
├── blender_script.py       # bpy automation
├── export_video.py         # FFmpeg wrapper
├── assets/                 # Sample image/song/lyrics
├── outputs/                # Generated MP4s
├── tests/                  # Unit tests
└── README.md              # Usage
```

### 2. Config Schema (YAML)
```yaml
inputs:
  mascot_image: "assets/fox.png"
  song_file: "assets/song.wav"
  lyrics_file: "assets/lyrics.txt"  # Format: "0:00-0:05 Hello|world"
duration: 30  # seconds
resolution: [3840, 2160]  # 4K
style:
  lighting: "jazzy"  # Presets: hues, intensity
  mascot: "fox"      # For future variants
```

### 3. Detailed Implementation
#### Prep Module (`prep_audio.py`)
- Load audio: `librosa.load(song_file, sr=22050)`.
- Beat detection: `onset_frames = librosa.onset.onset_detect(y=y, sr=sr)`.
- Phonemes: `subprocess.run(["rhubarb.exe", "-f", "dat", song_file])`; parse DAT for timings.
- Output: JSON with beats/phonemes for Blender.

#### Blender Script (`blender_script.py`)
- Clear scene: `bpy.ops.wm.read_factory_settings()`.
- Import image: `img = bpy.data.images.load(config['mascot_image'])`; apply as texture to plane mesh.
- Rigging: `bpy.ops.object.armature_add()`; add shape keys (e.g., 8 phoneme poses via manual extrusion—script approximates from image contours using bmesh).
- Animation Loop:
  - For each phoneme: `sk.value = 1; sk.keyframe_insert(frame=phoneme_frame)`.
  - Gestures: Interpolate bone rotations on beats (e.g., `bone.rotation_euler[0] = math.sin(beat_time) * 0.1`).
  - Lyrics: `bpy.ops.object.text_add()`; keyframe scale/color per word timing.
  - Lights: For each beat, randomize `light.data.energy = random.uniform(5,15)`; keyframe.
- Render: `bpy.context.scene.render.filepath = "outputs/frames/####.png"`; `bpy.ops.render.render(animation=True)`.

#### Orchestrator (`main.py`)
```python
import yaml
from prep_audio import process_audio
from subprocess import run
from export_video import encode_mp4

with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Prep
beats, phonemes = process_audio(config['song_file'])

# Blender
run(['blender', '--background', '--python', 'blender_script.py', '--', f"--config={yaml.dump(config)}"])

# Export
encode_mp4("outputs/frames/", config['song_file'], "outputs/final.mp4")
```

#### Export Module (`export_video.py`)
- `subprocess.run(['ffmpeg', '-framerate', '24', '-i', 'frames/%04d.png', '-i', song, '-c:v', 'libx265', output])`.

### 4. Testing & Deployment
- **Unit Tests**: `pytest` for prep (e.g., assert len(beats) > 0).
- **Integration**: Run full pipeline on sample assets; check sync with manual review.
- **Deployment**: Git repo; Win11 batch script for runs.
- **Extensibility**: Add hooks (e.g., `post_render_callback` for watermarks).

## Potential Enhancements
- GUI: Tkinter wrapper for non-CLI.
- Multi-Mascot: Variant rigs via config.
- Perf: GPU queues for batch renders.

This doc provides a blueprint—implement in phases (prep first, then Blender). If you need code stubs or refinements (e.g., for Claude handover), let me know!