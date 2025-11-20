# Architecture Documentation

## System Overview

Semantic Foragecast Engine is a **configuration-first, modular pipeline** for generating audio-driven animated videos. The system is designed around clean separation of concerns, extensibility, and production deployment requirements.

**Core Philosophy**: Configuration over code changes. Users should be able to create entirely different outputs by modifying YAML files, not Python code.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Orchestrator                       │
│                      (main.py)                               │
│  - Validates configuration                                   │
│  - Ensures dependencies                                      │
│  - Routes to phase executors                                 │
└──────────────┬──────────────────────────────┬────────────────┘
               │                              │
               ▼                              ▼
   ┌───────────────────────┐      ┌──────────────────────────┐
   │   Phase Execution     │      │   Configuration Layer    │
   │   (Sequential)        │◄─────┤   (config.yaml)          │
   └───────────────────────┘      └──────────────────────────┘
               │
               │
   ┌───────────┴────────────────────────────────────────┐
   │                                                     │
   ▼                                                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PHASE 1        │  │   PHASE 2        │  │   PHASE 3        │
│   Audio Prep     │─▶│   Rendering      │─▶│   Export         │
│                  │  │                  │  │                  │
│ prep_audio.py    │  │ blender_script.py│  │ export_video.py  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
   prep_data.json        PNG frames              MP4 video
```

---

## Four-Phase Pipeline Design

### Phase 1: Audio Preparation
**File**: `prep_audio.py`
**Input**: Audio file (WAV), lyrics file (TXT), configuration
**Output**: `prep_data.json`

**Responsibilities**:
1. **Audio Analysis**
   - Duration calculation
   - Sample rate validation
   - Tempo detection (LibROSA)

2. **Beat Detection**
   - Beat times using LibROSA's onset detection
   - Onset times for finer-grained timing
   - Frame number conversion (based on configured FPS)

3. **Phoneme Extraction**
   - Rhubarb Lip Sync integration (if available)
   - Mock phoneme fallback for testing
   - Time-to-frame conversion

4. **Lyrics Parsing**
   - Pipe-delimited format parsing (word|start|end)
   - Word-level timing data
   - Frame-based timing calculation

**Design Pattern**: Data extraction layer
- No rendering logic
- Pure data processing
- Cacheable output (JSON)
- Can be run independently for validation

**Key Classes**:
```python
AudioPreprocessor
├── load_audio()
├── detect_beats()
├── extract_phonemes()
└── parse_lyrics()
```

---

### Phase 2: Blender Rendering
**File**: `blender_script.py`
**Input**: Configuration, prep_data.json, asset files
**Output**: PNG frame sequence

**Responsibilities**:
1. **Scene Setup**
   - Camera positioning
   - Lighting configuration
   - Render settings

2. **Animation Mode Dispatch**
   - 2D Grease Pencil mode
   - 3D Mesh mode
   - Hybrid mode
   - Extensible to new modes

3. **Animation Application**
   - Lip sync (phoneme-driven mouth shapes)
   - Beat gestures (scale/rotation on beats)
   - Lyrics display (timed text objects)

4. **Frame Rendering**
   - EEVEE or Cycles engine
   - Configurable quality/performance
   - Headless-compatible (Xvfb)

**Design Pattern**: Builder + Strategy
- Builder: `GreasePencilBuilder` constructs scene
- Strategy: Animation mode selected at runtime
- Factory: Creates appropriate builder based on config

**Key Classes**:
```python
BlenderSceneBuilder
├── __init__(config, prep_data)
├── setup_scene()
├── build_animation() → dispatches to:
│   ├── GreasePencilBuilder
│   ├── MeshBuilder (planned)
│   └── HybridBuilder (planned)
└── render_frames()

GreasePencilBuilder
├── convert_image_to_strokes()
├── animate_lipsync()
├── add_beat_gestures()
└── create_lyric_text()
```

**Extension Point**: Add new animation modes by:
1. Create new builder class (e.g., `ParticleSystemBuilder`)
2. Implement required methods
3. Register in `build_animation()` dispatcher
4. Add mode to config schema

---

### Phase 3: Video Export
**File**: `export_video.py`
**Input**: PNG frames, audio file, configuration
**Output**: MP4 video file

**Responsibilities**:
1. **Frame Validation**
   - Check all frames rendered
   - Validate frame numbering
   - Verify frame resolution

2. **Video Encoding**
   - FFmpeg integration
   - Codec configuration (libx264, libx265, etc.)
   - Quality presets (low, medium, high)

3. **Audio Synchronization**
   - Embed original audio track
   - Ensure frame rate matches audio timing
   - Verify final duration

4. **Preview Generation**
   - Optional lower-resolution preview
   - Quick validation output

**Design Pattern**: Facade
- Abstracts FFmpeg complexity
- Provides simple encode() interface
- Handles cross-platform paths

**Key Classes**:
```python
VideoExporter
├── validate_frames()
├── encode_video()
└── create_preview()
```

---

## Data Flow Diagram

```
Audio File (song.wav)
      │
      ▼
┌─────────────────────┐
│   LibROSA           │
│   - Analyze tempo   │
│   - Detect beats    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐       ┌──────────────────┐
│   Rhubarb/Mock      │       │  Lyrics Parser   │
│   - Extract phonemes│       │  - Parse timing  │
└──────┬──────────────┘       └────────┬─────────┘
       │                               │
       └───────────┬───────────────────┘
                   ▼
            prep_data.json
         {beats, phonemes, lyrics}
                   │
                   ▼
       ┌───────────────────────┐
       │   Blender Python API  │
       │   - Build scene       │
       │   - Apply animations  │
       │   - Render frames     │
       └───────────┬───────────┘
                   │
                   ▼
            PNG Frames (0001-NNNN)
                   │
                   ▼
       ┌───────────────────────┐
       │      FFmpeg           │
       │   - Encode video      │
       │   - Sync audio        │
       └───────────┬───────────┘
                   │
                   ▼
              Final MP4
```

---

## Component Responsibilities

### Configuration System
**Pattern**: Hierarchical YAML with inheritance

```yaml
# Top level: environment settings
inputs: {mascot, song, lyrics}
output: {directories, naming}

# Middle: rendering specifications
video: {resolution, fps, quality}
style: {colors, lighting, effects}

# Bottom: implementation details
animation: {mode, features, parameters}
advanced: {debug, threads, optimization}
```

**Responsibility**: Single source of truth for all system behavior

**Benefits**:
- No code changes for different outputs
- Shareable presets (ultra_fast, production, etc.)
- Validation at startup (fail fast)
- Documentation via example configs

---

### Asset Management
**Pattern**: Declarative references, validated at startup

**Assets**:
- `mascot_image`: Source image for character
- `song_file`: Audio track (WAV preferred)
- `lyrics_file`: Timed lyrics text

**Validation**:
1. Check existence
2. Verify format/extension
3. Validate content (sample rate, image dimensions, etc.)

---

### Rendering Abstraction
**Pattern**: Render engine agnostic design

```python
# Blender-specific implementation hidden behind interface
class Renderer(ABC):
    @abstractmethod
    def setup_scene(self): pass

    @abstractmethod
    def render_frame(self, frame_num): pass

# Currently: BlenderRenderer
# Future: Unity, Unreal, Custom engines
```

---

## Design Decisions & Tradeoffs

### 1. **Phase Separation vs. Monolithic**

**Decision**: Separate phases with JSON intermediate format

**Rationale**:
- ✅ Can re-render without re-analyzing audio
- ✅ Each phase independently testable
- ✅ Failed renders don't require audio re-processing
- ✅ Parallel development possible
- ❌ Slight disk I/O overhead (negligible)

**Alternative Rejected**: Single monolithic process
- Would couple audio analysis to rendering
- Makes testing harder
- No caching benefits

---

### 2. **Configuration-First vs. Code-First**

**Decision**: YAML configuration drives all behavior

**Rationale**:
- ✅ Non-programmers can create presets
- ✅ Easier A/B testing (just swap configs)
- ✅ Configuration can be versioned separately
- ✅ Reduces code changes for common variations
- ❌ More complex validation required
- ❌ Harder to express complex logic in YAML

**Alternative Rejected**: Programmatic API
- Steeper learning curve
- Less shareable
- Would still need configs for common cases

---

### 3. **2D vs 3D Default**

**Decision**: 2D Grease Pencil as primary mode

**Rationale**:
- ✅ Faster rendering (2-3x speedup)
- ✅ Unique artistic style
- ✅ More forgiving of low-quality input images
- ✅ Smaller file sizes
- ❌ Less "polished" appearance
- ❌ Fewer effects available

**Alternative Available**: 3D mesh mode (config: `mode: "3d"`)
- Higher quality but slower
- More realistic lighting
- Better for professional output

---

### 4. **Lip Sync Approach**

**Decision**: Phoneme-based with Rhubarb integration

**Rationale**:
- ✅ Industry-standard approach
- ✅ Accurate mouth shapes
- ✅ Works with any audio (speech or song)
- ✅ Fallback mock mode for testing
- ❌ External dependency (Rhubarb)
- ❌ Requires audio processing time

**Alternative Rejected**: Volume-based (mouth opens on loud sounds)
- Inaccurate, looks amateurish
- No correlation to actual words
- Cheaper but not production-quality

---

### 5. **Headless Rendering Support**

**Decision**: Built-in Xvfb compatibility, no GUI required

**Rationale**:
- ✅ Cloud deployment (AWS, GCP, containers)
- ✅ CI/CD integration possible
- ✅ Batch processing on servers
- ✅ Scalable to render farms
- ❌ Slightly complex local setup (need Xvfb)

**Alternative Rejected**: Require display/GUI
- Limits deployment options
- Can't run in containers
- Not automation-friendly

---

## Extension Points

### Adding a New Animation Mode

**Example**: Particle system mode

1. **Create builder class**:
```python
# particle_system.py
class ParticleSystemBuilder:
    def __init__(self, config, prep_data):
        self.config = config
        self.prep_data = prep_data

    def build_scene(self):
        # Setup particle emitter
        # Configure physics
        pass

    def animate(self):
        # Trigger emissions on beats
        # Color changes on phonemes
        pass
```

2. **Register in dispatcher**:
```python
# blender_script.py
def build_animation(config, prep_data):
    mode = config['animation']['mode']

    if mode == '2d_grease':
        return GreasePencilBuilder(config, prep_data)
    elif mode == '3d':
        return MeshBuilder(config, prep_data)
    elif mode == 'particles':  # NEW
        return ParticleSystemBuilder(config, prep_data)
```

3. **Add config schema**:
```yaml
# config_particles.yaml
animation:
  mode: "particles"
  particle_count: 1000
  emission_rate: 100
```

### Adding a New Audio Analysis Method

**Example**: Melody extraction

1. **Extend preprocessor**:
```python
# prep_audio.py
class AudioPreprocessor:
    def extract_melody(self):
        # Use librosa.piptrack or CREPE
        pitches = librosa.piptrack(y=self.audio, sr=self.sr)
        return self._convert_to_frame_data(pitches)
```

2. **Save to prep_data**:
```python
prep_data['melody'] = {
    'pitches': [...],
    'confidence': [...]
}
```

3. **Use in animation**:
```python
# blender_script.py
def apply_melody_animation(self):
    melody = self.prep_data['melody']
    # Map pitch to mascot height/color
```

### Adding a New Effect

**Example**: Camera shake on beats

1. **Add to config schema**:
```yaml
effects:
  camera_shake:
    enabled: true
    intensity: 0.1
    frequency: 2
```

2. **Implement in builder**:
```python
def add_camera_shake(self):
    camera = bpy.data.objects['Camera']
    for beat in self.prep_data['beats']['beat_frames']:
        # Add location keyframe with noise
```

---

## Performance Characteristics

### Resolution vs. Render Time

Based on empirical testing (30s video, 2D mode, 12fps):

| Resolution | Pixels | Render Time | File Size | Use Case |
|------------|--------|-------------|-----------|----------|
| 180p (320x180) | 57.6K | ~3 min | 489KB | Fast testing |
| 360p (640x360) | 230.4K | ~6 min | 806KB | Quality check |
| 540p (960x540) | 518.4K | ~12 min | ~2MB | Preview |
| 1080p (1920x1080) | 2.07M | ~45 min | ~8MB | Production |

**Scaling**: Roughly linear with pixel count at low resolutions, sub-linear at high (due to Blender optimizations)

### FPS vs. Render Time

| FPS | Frames (30s) | Render Time | Smoothness |
|-----|--------------|-------------|------------|
| 12 | 360 | 1x (base) | Acceptable |
| 24 | 720 | 2x | Good |
| 30 | 900 | 2.5x | Excellent |
| 60 | 1800 | 5x | Overkill (web video) |

**Recommendation**: 24 FPS for production (best quality/time ratio)

### Mode Comparison

| Mode | Speed | Quality | File Size | Best For |
|------|-------|---------|-----------|----------|
| 2D Grease | ⚡⚡⚡ Fast | ⭐⭐ Good | Small | Testing, artistic style |
| 3D Mesh | ⚡⚡ Medium | ⭐⭐⭐ Best | Medium | Professional output |
| Hybrid | ⚡ Slow | ⭐⭐⭐ Best | Large | Maximum quality |

---

## Deployment Architectures

### Local Development
```
User Machine (Windows/Mac/Linux)
├── Blender installed locally
├── Python environment
└── Direct file system access
```
**Pros**: Full GUI access, easy debugging
**Cons**: Manual setup per machine

### Docker Container
```
Container Image
├── Ubuntu base
├── Blender 4.0+
├── Python + dependencies
├── Xvfb for headless
└── FFmpeg
```
**Pros**: Reproducible, portable
**Cons**: No GPU acceleration (CPU only)

### Cloud Rendering (AWS/GCP)
```
EC2/Compute Instance
├── Headless Blender
├── GPU-enabled instance (optional)
├── S3/Cloud Storage for outputs
└── Queue-based job system
```
**Pros**: Scalable, parallel renders
**Cons**: Network transfer overhead, cost

### Render Farm
```
Coordinator Node
├── Job queue
├── Asset distribution
└── Result aggregation

Worker Nodes (1-N)
├── Blender + Xvfb
├── Pull jobs from queue
└── Upload rendered frames
```
**Pros**: Massive parallelization
**Cons**: Complex setup, only worth at scale

---

## Error Handling Strategy

### Fail Fast Principles

1. **Startup Validation**
   - Check all files exist
   - Validate config schema
   - Verify dependencies (Blender, FFmpeg)

2. **Phase Boundaries**
   - Validate phase 1 output before phase 2
   - Check frame count before encoding
   - Verify video duration matches audio

3. **Graceful Degradation**
   - Rhubarb missing? Use mock phonemes
   - Lyrics file missing? Skip lyrics
   - Effects unsupported? Disable cleanly

### Logging Strategy

```python
# Structured logging at multiple levels
[OK]    # Success messages
[INFO]  # Informational progress
[WARN]  # Non-fatal issues (fallback used)
[ERROR] # Fatal issues (abort)
```

**Output**: Console for interactive, file for batch

---

## Testing Strategy

### Unit Tests
- Audio parsing logic
- Configuration validation
- Math utilities (frame conversion, etc.)

### Integration Tests
- Full pipeline with test assets
- Multiple config variations
- Headless vs. GUI modes

### Performance Tests
- Render time benchmarks
- Memory usage profiling
- Scalability testing (long videos)

### Visual Tests
- Frame comparison (detect regressions)
- Position verification (debug mode)
- Output quality checks

---

## Future Architecture Considerations

### Potential Improvements

1. **Plugin System**
   - External plugins for effects
   - Community-contributed animation modes
   - Hot-reload during development

2. **Real-time Preview**
   - WebSocket-based progress streaming
   - Browser-based preview player
   - Live scrubbing of timeline

3. **Distributed Rendering**
   - Split frames across multiple machines
   - Coordinator node for job distribution
   - Result merging and encoding

4. **API Service**
   - REST API for job submission
   - Webhook callbacks on completion
   - Multi-tenancy support

5. **Web UI**
   - No-code configuration builder
   - Asset upload interface
   - Progress monitoring dashboard

---

## Conclusion

The architecture prioritizes:
- **Modularity**: Each phase independent
- **Extensibility**: Easy to add features
- **Configurability**: No code changes for variations
- **Production-readiness**: Headless, scalable, error-handled

This design enables both rapid experimentation (swap configs) and production deployment (Docker, cloud, render farms).
