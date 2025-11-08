#!/usr/bin/env python3
"""
Blender Automation Script - Video Generation Pipeline
Phase 2: Scene Setup and Animation Stub

This script runs inside Blender to:
1. Set up the 3D scene
2. Import mascot image
3. Create basic rig (stub)
4. Generate animations (lip-sync, gestures, lyrics)
5. Set up lighting and effects
6. Render frames

Author: Claude (Anthropic)
Version: 2.0
Date: November 2025
Platform: Cross-platform (Windows 11 optimized)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Check if running in Blender
try:
    import bpy
    import mathutils
    RUNNING_IN_BLENDER = True
except ImportError:
    RUNNING_IN_BLENDER = False
    print("WARNING: Not running in Blender. This script requires Blender's Python environment.")
    print("Run with: blender --background --python blender_script.py -- [args]")

import yaml


class BlenderSceneBuilder:
    """Builds and configures the 3D scene in Blender."""

    def __init__(self, config: Dict, prep_data: Dict):
        """
        Initialize scene builder.

        Args:
            config: Pipeline configuration from YAML
            prep_data: Preprocessed audio data (beats, phonemes, etc.)
        """
        self.config = config
        self.prep_data = prep_data
        self.scene = bpy.context.scene

        # Set up scene basics
        self.fps = config.get('video', {}).get('fps', 24)
        self.scene.render.fps = self.fps
        self.scene.render.fps_base = 1.0

        # Calculate frame range from audio duration
        duration = prep_data.get('audio', {}).get('duration', 30)
        self.total_frames = int(duration * self.fps)
        self.scene.frame_start = 1
        self.scene.frame_end = self.total_frames

        print(f"Scene setup: {self.total_frames} frames @ {self.fps} fps")

    def clear_scene(self):
        """Clear default Blender scene."""
        print("Clearing default scene...")

        # Delete all objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Delete all materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

        # Delete all textures
        for texture in bpy.data.textures:
            bpy.data.textures.remove(texture)

        print("✓ Scene cleared")

    def setup_camera(self):
        """Create and position camera."""
        print("Setting up camera...")

        # Create camera
        bpy.ops.object.camera_add(location=(0, -5, 2))
        camera = bpy.context.object
        camera.name = "MainCamera"

        # Point camera at origin
        camera.rotation_euler = (1.3, 0, 0)  # About 75 degrees

        # Set as active camera
        self.scene.camera = camera

        # Configure render resolution
        resolution = self.config.get('video', {}).get('resolution', [1920, 1080])
        self.scene.render.resolution_x = resolution[0]
        self.scene.render.resolution_y = resolution[1]
        self.scene.render.resolution_percentage = 100

        print(f"✓ Camera created: {resolution[0]}x{resolution[1]}")

        return camera

    def setup_lighting(self):
        """Create stage lighting setup."""
        print("Setting up lighting...")

        style = self.config.get('style', {}).get('lighting', 'jazzy')
        colors = self.config.get('style', {}).get('colors', {})

        # Key light (main spotlight)
        bpy.ops.object.light_add(type='SPOT', location=(2, -3, 4))
        key_light = bpy.context.object
        key_light.name = "KeyLight"
        key_light.data.energy = 500
        key_light.data.spot_size = 1.2
        key_light.data.spot_blend = 0.5

        # Fill light (softer)
        bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
        fill_light = bpy.context.object
        fill_light.name = "FillLight"
        fill_light.data.energy = 200
        fill_light.data.size = 2.0

        # Back light (rim lighting)
        bpy.ops.object.light_add(type='SPOT', location=(0, 2, 3))
        back_light = bpy.context.object
        back_light.name = "BackLight"
        back_light.data.energy = 300
        back_light.data.spot_size = 1.0

        # Colored accent lights based on style
        if colors.get('primary'):
            primary_color = colors['primary']
            key_light.data.color = primary_color

        print(f"✓ Lighting setup complete ({style} style)")

        return [key_light, fill_light, back_light]

    def create_mascot_placeholder(self):
        """
        Create placeholder for mascot (to be replaced with image-based mesh).

        Returns:
            Mascot object
        """
        print("Creating mascot placeholder...")

        mascot_image = self.config.get('inputs', {}).get('mascot_image')

        # For now, create a simple placeholder mesh
        # TODO: Implement image-to-mesh conversion with rigging
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
        mascot = bpy.context.object
        mascot.name = "Mascot"

        # Create material
        mat = bpy.data.materials.new(name="MascotMaterial")
        mat.use_nodes = True
        mascot.data.materials.append(mat)

        # Load image if available
        if mascot_image and os.path.exists(mascot_image):
            print(f"  Loading mascot image: {mascot_image}")
            # TODO: Apply image as texture
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                tex_image = nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(mascot_image)
                mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

        print("✓ Mascot placeholder created")
        print("  NOTE: Full image-to-mesh rigging not yet implemented")

        return mascot

    def create_phoneme_shape_keys(self, mascot):
        """
        Create shape keys for phoneme-based lip sync.

        Args:
            mascot: Mascot mesh object

        Note: This is a stub. Full implementation requires proper mouth rigging.
        """
        print("Creating phoneme shape keys (stub)...")

        # Common phoneme shapes (Preston Blair mouth positions)
        phoneme_shapes = ['X', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        # Add basis shape key
        mascot.shape_key_add(name='Basis')

        # Add phoneme shape keys (placeholders)
        for phoneme in phoneme_shapes:
            sk = mascot.shape_key_add(name=f'Phoneme_{phoneme}')
            # TODO: Actually deform mesh for each phoneme

        print(f"✓ Created {len(phoneme_shapes)} phoneme shape keys (placeholders)")

    def animate_lip_sync(self, mascot):
        """
        Generate lip-sync animation from phoneme data.

        Args:
            mascot: Mascot mesh object with shape keys
        """
        if not self.config.get('animation', {}).get('enable_lipsync', True):
            print("Lip-sync disabled in config")
            return

        print("Generating lip-sync animation...")

        phonemes = self.prep_data.get('phonemes', [])
        if not phonemes:
            print("  WARNING: No phoneme data available")
            return

        # Animate shape keys based on phoneme timings
        for i, phoneme_data in enumerate(phonemes):
            time = phoneme_data['time']
            phoneme = phoneme_data['phoneme']

            # Convert time to frame
            frame = int(time * self.fps) + 1

            # Find corresponding shape key
            sk_name = f'Phoneme_{phoneme}'
            if sk_name in mascot.data.shape_keys.key_blocks:
                sk = mascot.data.shape_keys.key_blocks[sk_name]

                # Keyframe: set to 1.0 at this frame
                sk.value = 1.0
                sk.keyframe_insert(data_path='value', frame=frame)

                # Keyframe: set to 0.0 at next frame (or slightly after)
                next_time = phonemes[i + 1]['time'] if i + 1 < len(phonemes) else time + 0.15
                next_frame = int(next_time * self.fps) + 1
                sk.value = 0.0
                sk.keyframe_insert(data_path='value', frame=next_frame)

        print(f"✓ Lip-sync animation generated ({len(phonemes)} phoneme transitions)")

    def animate_gestures(self, mascot):
        """
        Generate body gesture animations synced to beats.

        Args:
            mascot: Mascot object
        """
        if not self.config.get('animation', {}).get('enable_gestures', True):
            print("Gestures disabled in config")
            return

        print("Generating gesture animation...")

        beat_times = self.prep_data.get('beats', {}).get('beat_times', [])
        if not beat_times:
            print("  WARNING: No beat data available")
            return

        intensity = self.config.get('animation', {}).get('gesture_intensity', 0.7)

        # Simple bounce animation on beats
        for beat_time in beat_times:
            frame = int(beat_time * self.fps) + 1

            # Slight upward movement
            mascot.location.z = 1.0 + (0.1 * intensity)
            mascot.keyframe_insert(data_path='location', frame=frame)

            # Return to rest position
            rest_frame = frame + 5
            mascot.location.z = 1.0
            mascot.keyframe_insert(data_path='location', frame=rest_frame)

        print(f"✓ Gesture animation generated ({len(beat_times)} beats)")

    def create_lyrics_text(self):
        """
        Create animated text overlays for lyrics.

        Returns:
            List of text objects
        """
        if not self.config.get('animation', {}).get('enable_lyrics', True):
            print("Lyrics disabled in config")
            return []

        print("Creating lyrics text...")

        timed_words = self.prep_data.get('timed_words', [])
        if not timed_words:
            print("  WARNING: No lyrics data available")
            return []

        lyrics_style = self.config.get('animation', {}).get('lyrics_style', 'bounce')
        text_objects = []

        # Create a text object for each word
        for word_data in timed_words:
            word = word_data['word']
            start_time = word_data['start']
            end_time = word_data['end']

            # Create text object
            bpy.ops.object.text_add(location=(0, 0, -1))
            text_obj = bpy.context.object
            text_obj.data.body = word
            text_obj.data.align_x = 'CENTER'
            text_obj.data.align_y = 'CENTER'
            text_obj.name = f"Lyric_{word}"

            # Initially hide
            text_obj.hide_render = True
            text_obj.hide_viewport = True

            # Animate visibility
            start_frame = int(start_time * self.fps) + 1
            end_frame = int(end_time * self.fps) + 1

            # Show at start
            text_obj.hide_render = False
            text_obj.hide_viewport = False
            text_obj.keyframe_insert(data_path='hide_render', frame=start_frame)
            text_obj.keyframe_insert(data_path='hide_viewport', frame=start_frame)

            # Animate scale (bounce effect)
            if lyrics_style == 'bounce':
                text_obj.scale = (0.5, 0.5, 0.5)
                text_obj.keyframe_insert(data_path='scale', frame=start_frame)

                mid_frame = start_frame + 3
                text_obj.scale = (1.2, 1.2, 1.2)
                text_obj.keyframe_insert(data_path='scale', frame=mid_frame)

                text_obj.scale = (1.0, 1.0, 1.0)
                text_obj.keyframe_insert(data_path='scale', frame=mid_frame + 2)

            # Hide at end
            text_obj.hide_render = True
            text_obj.hide_viewport = True
            text_obj.keyframe_insert(data_path='hide_render', frame=end_frame)
            text_obj.keyframe_insert(data_path='hide_viewport', frame=end_frame)

            text_objects.append(text_obj)

        print(f"✓ Created {len(text_objects)} lyric text objects")

        return text_objects

    def animate_lights_to_beats(self, lights):
        """
        Animate lights to pulse with beats.

        Args:
            lights: List of light objects
        """
        if not self.config.get('effects', {}).get('lights', {}).get('flashes', {}).get('enabled', True):
            print("Light flashes disabled in config")
            return

        print("Animating lights to beats...")

        beat_times = self.prep_data.get('beats', {}).get('beat_times', [])
        if not beat_times:
            return

        for light in lights:
            base_energy = light.data.energy

            for beat_time in beat_times:
                frame = int(beat_time * self.fps) + 1

                # Flash brighter
                light.data.energy = base_energy * 2
                light.data.keyframe_insert(data_path='energy', frame=frame)

                # Return to normal
                light.data.energy = base_energy
                light.data.keyframe_insert(data_path='energy', frame=frame + 3)

        print(f"✓ Lights animated to {len(beat_times)} beats")

    def setup_render_settings(self):
        """Configure render engine and output settings."""
        print("Configuring render settings...")

        # Render engine
        engine = self.config.get('video', {}).get('render_engine', 'EEVEE')
        self.scene.render.engine = engine

        # Samples
        samples = self.config.get('video', {}).get('samples', 128)
        if engine == 'EEVEE':
            self.scene.eevee.taa_render_samples = samples
        elif engine == 'CYCLES':
            self.scene.cycles.samples = samples

        # Output path
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        os.makedirs(frames_dir, exist_ok=True)

        self.scene.render.filepath = os.path.join(frames_dir, 'frame_####.png')
        self.scene.render.image_settings.file_format = 'PNG'

        print(f"✓ Render settings configured ({engine}, {samples} samples)")
        print(f"  Output: {self.scene.render.filepath}")

    def render_animation(self):
        """Render the animation."""
        print("=" * 70)
        print("RENDERING ANIMATION")
        print("=" * 70)

        print(f"Rendering frames {self.scene.frame_start} to {self.scene.frame_end}...")
        print("This may take several minutes...")

        bpy.ops.render.render(animation=True)

        print("✓ Rendering complete")


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_prep_data(prep_data_path: str) -> Dict:
    """Load preprocessed audio data from JSON."""
    with open(prep_data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main entry point when run in Blender."""
    if not RUNNING_IN_BLENDER:
        print("ERROR: This script must be run inside Blender")
        print("Usage: blender --background --python blender_script.py -- --config config.yaml --prep-data prep_data.json")
        return 1

    # Parse arguments (after '--')
    parser = argparse.ArgumentParser(description='Blender Scene Builder')
    parser.add_argument('--config', required=True, help='Path to config YAML')
    parser.add_argument('--prep-data', required=True, help='Path to prep data JSON')

    # Arguments after '--' in Blender command line
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []

    args = parser.parse_args(argv)

    print("=" * 70)
    print("BLENDER SCENE BUILDER - PHASE 2")
    print("=" * 70)
    print()

    # Load config and prep data
    print(f"Loading config: {args.config}")
    config = load_config(args.config)

    print(f"Loading prep data: {args.prep_data}")
    prep_data = load_prep_data(args.prep_data)

    print()

    # Detect animation mode
    animation_mode = config.get('animation', {}).get('mode', '3d')
    print(f"Animation Mode: {animation_mode}")
    print()

    # Route to appropriate builder based on mode
    if animation_mode == '2d_grease':
        # Build 2D Grease Pencil scene
        from grease_pencil import build_2d_scene
        builder = build_2d_scene(config, prep_data)
        print("✓ 2D Grease Pencil scene built successfully")

    elif animation_mode == 'hybrid':
        # Build hybrid scene (2D mascot on 3D stage)
        print("Building hybrid scene (2D on 3D stage)...")

        # First build 3D stage
        builder_3d = BlenderSceneBuilder(config, prep_data)
        builder_3d.clear_scene()
        camera = builder_3d.setup_camera()
        lights = builder_3d.setup_lighting()

        # Then add 2D GP mascot
        from grease_pencil import GreasePencilBuilder
        builder_2d = GreasePencilBuilder(config, prep_data)

        mascot_image = config.get('inputs', {}).get('mascot_image', '')
        gp_mascot = builder_2d.create_gp_object("Mascot_GP_Hybrid")
        mascot_layer = builder_2d.image_to_strokes(mascot_image, gp_mascot, "Mascot")

        # Animate 2D mascot
        builder_2d.create_mouth_shape_variations(gp_mascot, mascot_layer)
        builder_2d.animate_lip_sync(gp_mascot)

        intensity = config.get('animation', {}).get('gesture_intensity', 0.7)
        builder_2d.add_beat_gestures(gp_mascot, intensity)

        # Add lyrics (can be 3D or 2D)
        if config.get('animation', {}).get('enable_lyrics', True):
            lyrics = builder_2d.create_lyric_strokes()

        # Use 3D lighting with 2D mascot
        builder_3d.animate_lights_to_beats(lights)
        builder_3d.setup_render_settings()

        print("✓ Hybrid scene built successfully")

    else:
        # Default: Build 3D mesh scene
        print("Building 3D mesh scene...")
        builder = BlenderSceneBuilder(config, prep_data)

        # Execute pipeline
        builder.clear_scene()
        camera = builder.setup_camera()
        lights = builder.setup_lighting()
        mascot = builder.create_mascot_placeholder()

        # Animation (stub implementations)
        builder.create_phoneme_shape_keys(mascot)
        builder.animate_lip_sync(mascot)
        builder.animate_gestures(mascot)
        lyrics = builder.create_lyrics_text()
        builder.animate_lights_to_beats(lights)

        # Render setup
        builder.setup_render_settings()

        print("✓ 3D mesh scene built successfully")

    print()
    print("=" * 70)
    print("SCENE SETUP COMPLETE")
    print("=" * 70)
    print()
    print(f"Mode: {animation_mode}")
    print("Phase 2 (Blender) complete!")
    print("Full rendering disabled in stub mode.")
    print("To enable rendering, uncomment render code in blender_script.py")
    print()

    # Uncomment to actually render:
    # if animation_mode in ['2d_grease', 'hybrid']:
    #     # Render with EEVEE for speed
    #     bpy.ops.render.render(animation=True)
    # else:
    #     # builder.render_animation()

    return 0


if __name__ == '__main__':
    if RUNNING_IN_BLENDER:
        sys.exit(main())
    else:
        print("This script is designed to run inside Blender's Python environment")
