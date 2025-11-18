# Developer Guide

**For developers who want to extend, customize, or contribute to Semantic Foragecast Engine**

This guide provides practical examples for common extension scenarios.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Adding a New Animation Mode](#adding-a-new-animation-mode)
3. [Adding a New Effect](#adding-a-new-effect)
4. [Integrating New Audio Analysis](#integrating-new-audio-analysis)
5. [Creating Custom Configs](#creating-custom-configs)
6. [Testing Your Changes](#testing-your-changes)
7. [API Reference](#api-reference)
8. [Debugging Tips](#debugging-tips)

---

## Development Setup

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Blender (system-specific)
# macOS: brew install --cask blender
# Ubuntu: apt-get install blender
# Windows: Download from blender.org

# Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: apt-get install ffmpeg
# Windows: Download from ffmpeg.org

# Optional: Rhubarb Lip Sync
# Download from github.com/DanielSWolf/rhubarb-lip-sync
```

### Project Structure

```
semantic-foragecast-engine/
├── main.py                  # Entry point, orchestrator
├── prep_audio.py            # Phase 1: Audio preprocessing
├── blender_script.py        # Phase 2: Blender rendering
├── export_video.py          # Phase 3: Video export
├── grease_pencil.py         # 2D animation mode implementation
├── config.yaml              # Default configuration
├── assets/                  # Input files
│   ├── fox.png
│   ├── song.wav
│   └── lyrics.txt
├── outputs/                 # Generated outputs
└── docs/                    # Documentation (optional)
```

### Running in Development Mode

```bash
# Enable verbose logging
python main.py --config config.yaml --verbose

# Run single phase for testing
python main.py --config config.yaml --phase 1  # Audio only
python main.py --config config.yaml --phase 2  # Rendering only
python main.py --config config.yaml --phase 3  # Export only

# Enable debug visualization
# Set debug_mode: true in config.yaml
# Re-run phase 2 to see positioning markers
```

---

## Adding a New Animation Mode

### Example: Particle System Mode

**Goal**: Create an animation mode where particles emit from the mascot on beats and change color on phonemes.

#### Step 1: Create the Builder Class

Create `particle_system.py`:

```python
import bpy
import math

class ParticleSystemBuilder:
    """
    Particle system animation builder.
    Emits particles on beats, colors change on phonemes.
    """

    def __init__(self, config, prep_data):
        self.config = config
        self.prep_data = prep_data
        self.fps = config['video']['fps']
        self.total_frames = int(prep_data['audio']['duration'] * self.fps)

    def build_scene(self):
        """Setup particle system scene."""
        print("\n======================================================================")
        print("BUILDING PARTICLE SYSTEM SCENE")
        print("======================================================================\n")

        # Clear scene
        bpy.ops.wm.read_homefile(use_empty=True)

        # Setup camera
        self._setup_camera()

        # Setup lighting
        self._setup_lighting()

        # Create particle emitter
        self._create_emitter()

        # Setup particle system
        self._setup_particles()

        # Animate particles
        self._animate_particles()

        # Configure render settings
        self._configure_render_settings()

        print("[OK] Particle system scene built\n")

    def _setup_camera(self):
        """Create and position camera."""
        bpy.ops.object.camera_add(location=(0, -10, 5))
        camera = bpy.context.active_object
        camera.name = "Particle_Camera"
        camera.rotation_euler = (math.radians(60), 0, 0)

        # Set as active camera
        bpy.context.scene.camera = camera
        print("[OK] Camera configured")

    def _setup_lighting(self):
        """Add lighting for particles."""
        # Sun light for overall illumination
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.data.energy = 2.0

        # Point light at origin for particle illumination
        bpy.ops.object.light_add(type='POINT', location=(0, 0, 2))
        point = bpy.context.active_object
        point.data.energy = 500
        print("[OK] Lighting configured")

    def _create_emitter(self):
        """Create particle emitter object."""
        # Load mascot image and create plane
        mascot_path = self.config['inputs']['mascot_image']

        # Create UV sphere as emitter
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
        self.emitter = bpy.context.active_object
        self.emitter.name = "Particle_Emitter"

        # Apply mascot texture
        mat = bpy.data.materials.new(name="Emitter_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")

        # Load image texture
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(mascot_path)

        # Connect texture to base color
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_node.outputs['Color'])

        # Assign material
        self.emitter.data.materials.append(mat)
        print(f"[OK] Emitter created with texture: {mascot_path}")

    def _setup_particles(self):
        """Configure particle system settings."""
        # Get particle settings from config
        particle_config = self.config.get('animation', {}).get('particle_settings', {})
        count = particle_config.get('count', 1000)
        lifetime = particle_config.get('lifetime', 50)

        # Add particle system modifier
        bpy.context.view_layer.objects.active = self.emitter
        bpy.ops.object.particle_system_add()

        # Get particle settings
        ps = self.emitter.particle_systems[0]
        settings = ps.settings

        # Configure emission
        settings.count = count
        settings.frame_start = 1
        settings.frame_end = self.total_frames
        settings.lifetime = lifetime
        settings.emit_from = 'FACE'

        # Physics
        settings.physics_type = 'NEWTON'
        settings.normal_factor = 1.0  # Emit outward
        settings.factor_random = 0.5  # Some randomness

        # Render settings
        settings.render_type = 'OBJECT'

        # Create particle object (small sphere)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.05)
        particle_obj = bpy.context.active_object
        particle_obj.name = "Particle_Instance"
        settings.instance_object = particle_obj

        # Hide particle instance object
        particle_obj.hide_viewport = True
        particle_obj.hide_render = True

        print(f"[OK] Particle system configured ({count} particles)")

    def _animate_particles(self):
        """Animate particle emission and colors based on audio."""
        # Animate emission rate on beats
        self._animate_emission_on_beats()

        # Animate particle color on phonemes
        self._animate_color_on_phonemes()

    def _animate_emission_on_beats(self):
        """Increase emission rate on beats."""
        ps = self.emitter.particle_systems[0].settings
        beat_frames = self.prep_data['beats']['beat_frames']

        # Default low emission
        ps.keyframe_insert(data_path="count", frame=1)

        for beat_frame in beat_frames:
            # Spike emission on beat
            ps.count *= 2  # Double emission
            ps.keyframe_insert(data_path="count", frame=beat_frame)

            # Return to normal after 5 frames
            ps.count //= 2
            ps.keyframe_insert(data_path="count", frame=beat_frame + 5)

        print(f"[OK] Animated emission on {len(beat_frames)} beats")

    def _animate_color_on_phonemes(self):
        """Change emitter color based on phonemes."""
        # Get emitter material
        mat = self.emitter.data.materials[0]
        bsdf = mat.node_tree.nodes.get("Principled BSDF")

        # Phoneme to color mapping
        phoneme_colors = {
            'A': (1.0, 0.0, 0.0),  # Red
            'B': (1.0, 0.5, 0.0),  # Orange
            'C': (1.0, 1.0, 0.0),  # Yellow
            'D': (0.0, 1.0, 0.0),  # Green
            'E': (0.0, 1.0, 1.0),  # Cyan
            'F': (0.0, 0.0, 1.0),  # Blue
            'G': (0.5, 0.0, 1.0),  # Purple
            'H': (1.0, 0.0, 1.0),  # Magenta
            'X': (1.0, 1.0, 1.0),  # White
        }

        phonemes = self.prep_data['phonemes']
        for phoneme_data in phonemes:
            frame = int(phoneme_data['time'] * self.fps)
            phoneme = phoneme_data['phoneme']
            color = phoneme_colors.get(phoneme, (1.0, 1.0, 1.0))

            # Set emission color
            bsdf.inputs['Emission'].default_value = color + (1.0,)  # Add alpha
            bsdf.inputs['Emission'].keyframe_insert(data_path="default_value", frame=frame)

        print(f"[OK] Animated color on {len(phonemes)} phonemes")

    def _configure_render_settings(self):
        """Configure Blender render settings."""
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = self.total_frames

        # Resolution
        scene.render.resolution_x = self.config['video']['resolution'][0]
        scene.render.resolution_y = self.config['video']['resolution'][1]
        scene.render.fps = self.fps

        # Engine
        scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = self.config['video'].get('samples', 64)

        # Output
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = self.config['output']['frames_dir'] + "/frame_"

        print("[OK] Render settings configured")
```

#### Step 2: Register in Dispatcher

Modify `blender_script.py`:

```python
# At top of file
from particle_system import ParticleSystemBuilder

# In build_animation() function
def build_animation(config, prep_data):
    """
    Factory function to create appropriate animation builder.
    """
    mode = config['animation']['mode']

    if mode == '2d_grease':
        from grease_pencil import GreasePencilBuilder
        return GreasePencilBuilder(config, prep_data)

    elif mode == '3d':
        # Future: 3D mesh builder
        raise NotImplementedError("3D mode coming soon")

    elif mode == 'particles':  # NEW MODE
        return ParticleSystemBuilder(config, prep_data)

    else:
        raise ValueError(f"Unknown animation mode: {mode}")
```

#### Step 3: Create Configuration

Create `config_particles.yaml`:

```yaml
inputs:
  mascot_image: "assets/fox.png"
  song_file: "assets/song.wav"
  lyrics_file: "assets/lyrics.txt"

output:
  output_dir: "outputs/particles"
  video_name: "particles.mp4"
  frames_dir: "outputs/particles/frames"
  prep_json: "outputs/particles/prep_data.json"

video:
  resolution: [1920, 1080]
  fps: 24
  render_engine: "EEVEE"
  samples: 64

animation:
  mode: "particles"  # USE NEW MODE

  particle_settings:
    count: 1000
    lifetime: 50

  enable_lipsync: false  # Not applicable
  enable_gestures: false  # Handled by emission
  enable_lyrics: false  # Not implemented yet
```

#### Step 4: Test

```bash
python main.py --config config_particles.yaml
```

---

## Adding a New Effect

### Example: Camera Shake on Beats

**Goal**: Add camera shake effect triggered by beats.

#### Step 1: Add Config Schema

In your config file (e.g., `config.yaml`):

```yaml
effects:
  camera_shake:
    enabled: true
    intensity: 0.2      # Maximum displacement
    frequency: 10       # Oscillations per second
    duration_frames: 10  # How long shake lasts
```

#### Step 2: Implement Effect

Add to `blender_script.py` or create `effects.py`:

```python
import bpy
import math
import random

class CameraShakeEffect:
    """
    Adds camera shake on beats.
    """

    def __init__(self, config, prep_data):
        self.config = config
        self.prep_data = prep_data
        self.fps = config['video']['fps']

        # Get effect settings
        shake_config = config.get('effects', {}).get('camera_shake', {})
        self.enabled = shake_config.get('enabled', False)
        self.intensity = shake_config.get('intensity', 0.2)
        self.frequency = shake_config.get('frequency', 10)
        self.duration_frames = shake_config.get('duration_frames', 10)

    def apply(self, camera):
        """
        Apply shake effect to camera.
        """
        if not self.enabled:
            return

        beat_frames = self.prep_data['beats']['beat_frames']

        for beat_frame in beat_frames:
            # Original position
            original_loc = camera.location.copy()

            # Shake for duration
            for offset in range(self.duration_frames):
                frame = beat_frame + offset

                # Decay shake over time
                decay = 1.0 - (offset / self.duration_frames)

                # Random shake direction
                shake_x = random.uniform(-1, 1) * self.intensity * decay
                shake_y = random.uniform(-1, 1) * self.intensity * decay
                shake_z = random.uniform(-1, 1) * self.intensity * decay

                # Apply shake
                camera.location = (
                    original_loc.x + shake_x,
                    original_loc.y + shake_y,
                    original_loc.z + shake_z
                )
                camera.keyframe_insert(data_path="location", frame=frame)

            # Return to original position
            camera.location = original_loc
            camera.keyframe_insert(data_path="location", frame=beat_frame + self.duration_frames)

        print(f"[OK] Camera shake applied to {len(beat_frames)} beats")
```

#### Step 3: Integrate into Builder

In `grease_pencil.py` (or your animation builder):

```python
from effects import CameraShakeEffect

class GreasePencilBuilder:
    def build_scene(self):
        # ... existing scene setup ...

        # Add effects
        self._apply_effects()

    def _apply_effects(self):
        """Apply all enabled effects."""
        camera = bpy.data.objects.get("GP_Camera")

        # Camera shake
        shake = CameraShakeEffect(self.config, self.prep_data)
        shake.apply(camera)

        # Future effects...
```

#### Step 4: Test

```bash
# Enable in config
# Set effects.camera_shake.enabled: true

python main.py --config config.yaml --phase 2
```

---

## Integrating New Audio Analysis

### Example: Melody Extraction

**Goal**: Extract melody (pitch over time) and use it to animate mascot height.

#### Step 1: Add Analysis Function

Modify `prep_audio.py`:

```python
import librosa

class AudioPreprocessor:
    # ... existing code ...

    def extract_melody(self):
        """
        Extract pitch (melody) over time using librosa.
        Returns array of pitches and confidence values.
        """
        print("Extracting melody...")

        # Use piptrack for pitch detection
        pitches, magnitudes = librosa.piptrack(
            y=self.audio,
            sr=self.sample_rate,
            hop_length=512
        )

        # Get dominant pitch at each time
        melody = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            confidence = magnitudes[index, t]

            melody.append({
                'time': t * 512 / self.sample_rate,
                'frame': int((t * 512 / self.sample_rate) * self.fps),
                'pitch': float(pitch),  # Hz
                'confidence': float(confidence)
            })

        print(f"  Found {len(melody)} pitch samples")
        return melody

    def run(self):
        # ... existing analysis ...

        # Add melody extraction
        melody = self.extract_melody()

        # Save to output
        output = {
            'audio': audio_data,
            'beats': beat_data,
            'phonemes': phoneme_data,
            'timed_words': timed_words,
            'melody': melody  # NEW
        }

        return output
```

#### Step 2: Use in Animation

Modify animation builder:

```python
class GreasePencilBuilder:
    def animate_melody(self):
        """
        Animate mascot height based on melody pitch.
        Higher pitch = higher position.
        """
        if 'melody' not in self.prep_data:
            print("[WARN] No melody data, skipping melody animation")
            return

        melody = self.prep_data['melody']
        mascot = bpy.data.objects.get("Mascot_GP")

        # Find pitch range for normalization
        pitches = [m['pitch'] for m in melody if m['confidence'] > 0.1]
        if not pitches:
            return

        min_pitch = min(pitches)
        max_pitch = max(pitches)

        for m in melody:
            if m['confidence'] < 0.1:  # Skip low confidence
                continue

            # Normalize pitch to 0-1
            normalized = (m['pitch'] - min_pitch) / (max_pitch - min_pitch)

            # Map to height range (0.5 to 1.5)
            height = 0.5 + normalized * 1.0

            # Set z-position
            mascot.location.z = height
            mascot.keyframe_insert(data_path="location", index=2, frame=m['frame'])

        print(f"[OK] Animated melody with {len(pitches)} pitch samples")

    def build_scene(self):
        # ... existing setup ...

        # Add melody animation
        self.animate_melody()
```

#### Step 3: Enable in Config

```yaml
animation:
  enable_melody: true  # Optional flag
```

---

## Creating Custom Configs

### Config Inheritance Pattern

Create specialized configs that override defaults:

**Base config** (`config_base.yaml`):
```yaml
inputs:
  mascot_image: "assets/fox.png"
  song_file: "assets/song.wav"
  lyrics_file: "assets/lyrics.txt"

video:
  fps: 24
  render_engine: "EEVEE"
```

**High quality override** (`config_hq.yaml`):
```yaml
# Import base (conceptual - manually merge in practice)
video:
  resolution: [1920, 1080]  # Override
  samples: 128               # Override
  quality: "high"            # Override
```

**Fast test override** (`config_fast.yaml`):
```yaml
video:
  resolution: [640, 360]
  fps: 12
  samples: 16
  quality: "low"
```

### Configuration Best Practices

1. **Use descriptive names**: `config_360p_12fps.yaml` not `config2.yaml`
2. **Comment non-obvious values**:
   ```yaml
   samples: 16  # Low for speed, increase to 64+ for quality
   ```
3. **Group related settings**:
   ```yaml
   effects:
     fog: {...}
     particles: {...}
     camera_shake: {...}
   ```
4. **Provide defaults**: Ensure code handles missing values gracefully
5. **Validate at startup**: Fail fast if config is invalid

---

## Testing Your Changes

### Manual Testing

```bash
# Test single phase
python main.py --config your_config.yaml --phase 2

# Enable verbose output
python main.py --config your_config.yaml --verbose

# Check outputs
ls -lh outputs/your_output_dir/
```

### Unit Tests (Example)

Create `tests/test_audio.py`:

```python
import unittest
from prep_audio import AudioPreprocessor

class TestAudioPreprocessor(unittest.TestCase):
    def setUp(self):
        self.config = {
            'inputs': {'song_file': 'tests/fixtures/test_audio.wav'},
            'video': {'fps': 24}
        }
        self.prep = AudioPreprocessor(self.config)

    def test_load_audio(self):
        """Test audio file loading."""
        duration = self.prep.load_audio()
        self.assertGreater(duration, 0)

    def test_beat_detection(self):
        """Test beat detection returns reasonable results."""
        self.prep.load_audio()
        beat_data = self.prep.detect_beats()

        self.assertIn('beat_times', beat_data)
        self.assertGreater(len(beat_data['beat_times']), 0)

        # Check beat times are in order
        beat_times = beat_data['beat_times']
        self.assertEqual(beat_times, sorted(beat_times))

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m unittest discover tests/
```

### Integration Tests

Create `tests/test_pipeline.py`:

```python
import unittest
import subprocess
import os

class TestFullPipeline(unittest.TestCase):
    def test_full_pipeline_ultra_fast(self):
        """Test complete pipeline with ultra_fast config."""
        result = subprocess.run(
            ['python', 'main.py', '--config', 'config_ultra_fast.yaml'],
            capture_output=True,
            text=True
        )

        # Check exit code
        self.assertEqual(result.returncode, 0)

        # Check output file exists
        self.assertTrue(os.path.exists('outputs/ultra_fast/ultra_fast.mp4'))

        # Check file size is reasonable
        size = os.path.getsize('outputs/ultra_fast/ultra_fast.mp4')
        self.assertGreater(size, 100000)  # At least 100KB

if __name__ == '__main__':
    unittest.main()
```

---

## API Reference

### Main Classes

#### AudioPreprocessor

```python
class AudioPreprocessor:
    def __init__(self, config):
        """Initialize with configuration dict."""

    def load_audio(self) -> float:
        """Load audio file. Returns duration in seconds."""

    def detect_beats(self) -> dict:
        """
        Detect beats and onsets.

        Returns:
            {
                'beat_times': [float],      # Beat times in seconds
                'beat_frames': [int],       # Beat frame numbers
                'onset_times': [float],     # Onset times
                'onset_frames': [int]       # Onset frame numbers
            }
        """

    def extract_phonemes(self) -> list:
        """
        Extract phonemes using Rhubarb or mock.

        Returns:
            [{'time': float, 'phoneme': str}, ...]
        """

    def parse_lyrics(self) -> list:
        """
        Parse lyrics from file.

        Returns:
            [{'start': float, 'end': float, 'word': str}, ...]
        """

    def run(self) -> dict:
        """Run all preprocessing steps. Returns complete prep_data dict."""
```

#### GreasePencilBuilder

```python
class GreasePencilBuilder:
    def __init__(self, config, prep_data):
        """Initialize with config and preprocessed data."""

    def build_scene(self):
        """Build complete Blender scene."""

    def convert_image_to_strokes(self) -> list:
        """Convert mascot image to Grease Pencil strokes."""

    def animate_lipsync(self):
        """Apply phoneme-based lip sync animation."""

    def add_beat_gestures(self):
        """Add beat-synced scale/rotation animations."""

    def create_lyric_text(self):
        """Create and animate lyric text objects."""
```

#### VideoExporter

```python
class VideoExporter:
    def __init__(self, config):
        """Initialize with configuration."""

    def validate_frames(self) -> bool:
        """Check all frames exist and are valid."""

    def encode_video(self) -> str:
        """Encode frames to video. Returns path to output file."""

    def create_preview(self, scale=0.5) -> str:
        """Create lower-res preview. Returns path to preview file."""
```

### prep_data.json Schema

```json
{
  "audio": {
    "path": "string",
    "duration": "float",
    "sample_rate": "int",
    "tempo": "float"
  },
  "beats": {
    "beat_times": ["float"],
    "beat_frames": ["int"],
    "onset_times": ["float"],
    "onset_frames": ["int"]
  },
  "phonemes": [
    {
      "time": "float",
      "phoneme": "string (A-H or X)"
    }
  ],
  "timed_words": [
    {
      "start": "float",
      "end": "float",
      "word": "string"
    }
  ]
}
```

---

## Debugging Tips

### Enable Debug Mode

In `config.yaml`:
```yaml
advanced:
  debug_mode: true
```

This adds colored sphere markers at key positions:
- Red: Camera position
- Green: Mascot position
- Blue: Text zone
- Yellow: Origin

### Common Issues

**Issue**: Lyrics not visible
```bash
# Check positioning in frame 100
python main.py --config config.yaml --phase 2
# Open outputs/.../frames/frame_0100.png
# Look for text line in lower third
```

**Issue**: Lip sync not working
```bash
# Check phoneme data was generated
cat outputs/.../prep_data.json | grep -A 5 "phonemes"
# Ensure Rhubarb is installed or mock fallback is enabled
```

**Issue**: Blender crashes
```bash
# Run with headless mode
xvfb-run -a python main.py --config config.yaml --phase 2

# Check Blender logs
# (Usually in /tmp/ on Linux)
```

**Issue**: Rendering too slow
```bash
# Use ultra_fast config for testing
python main.py --config config_ultra_fast.yaml

# Or reduce samples in your config
# samples: 16  # vs 128 for production
```

### Logging

Add detailed logging to your code:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("Important milestone")
logger.warning("Something unexpected but handled")
logger.error("Fatal error")
```

### Profiling

Profile slow operations:

```python
import time

start = time.time()
# ... slow operation ...
elapsed = time.time() - start
print(f"Operation took {elapsed:.2f}s")
```

---

## Code Style Guidelines

### Python

- **PEP 8** compliant
- **Type hints** for function signatures (optional but recommended)
- **Docstrings** for all public methods
- **Comments** for non-obvious logic

Example:
```python
def detect_beats(self) -> dict:
    """
    Detect beats and onsets in audio using LibROSA.

    Returns:
        Dictionary containing beat_times, beat_frames,
        onset_times, and onset_frames arrays.
    """
    # Use onset_detect for beat detection (more accurate than beat_track)
    onset_env = librosa.onset.onset_strength(y=self.audio, sr=self.sample_rate)
    beats = librosa.onset.onset_detect(onset_envelope=onset_env, sr=self.sample_rate)

    return self._convert_to_frame_data(beats)
```

### Blender Python

- **bpy.ops** for operators (mesh creation, etc.)
- **bpy.data** for accessing data blocks
- **bpy.context** for current state
- **Use names** for objects: `obj.name = "Mascot_GP"` not `obj.name = "Object.001"`

### Configuration

- **snake_case** for keys: `mascot_image` not `MascotImage`
- **Nested logically**: Group related settings under common parent
- **Units in comments**: `duration: 30  # seconds`

---

## Contributing

### Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** with clear commit messages
4. **Test thoroughly**: Run full pipeline with multiple configs
5. **Update docs**: Add to DEVELOPER_GUIDE.md if API changes
6. **Submit PR**: Describe what and why

### What We're Looking For

- **New animation modes** (3D, hybrid, particle, etc.)
- **Audio analysis improvements** (better beat detection, melody, harmony)
- **Effects** (camera movements, particle systems, post-processing)
- **Performance optimizations** (faster rendering, caching)
- **Bug fixes** (with tests)
- **Documentation** (examples, tutorials, guides)

---

## Additional Resources

- **Blender Python API**: https://docs.blender.org/api/current/
- **LibROSA docs**: https://librosa.org/doc/latest/
- **FFmpeg guide**: https://trac.ffmpeg.org/wiki
- **Rhubarb Lip Sync**: https://github.com/DanielSWolf/rhubarb-lip-sync

---

## Questions?

- **GitHub Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: Check `examples/` directory for sample extensions

Happy coding! 🎨🎵
