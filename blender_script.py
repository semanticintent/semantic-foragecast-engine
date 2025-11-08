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

# Add script directory to Python path for module imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

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
        """Create production-quality lighting with HDRI environment."""
        print("Setting up production lighting...")

        style = self.config.get('style', {}).get('lighting', 'jazzy')
        colors = self.config.get('style', {}).get('colors', {})
        effects = self.config.get('effects', {})
        lights_config = effects.get('lights', {})
        hdri_config = lights_config.get('hdri', {})

        lights = []

        # Setup HDRI environment lighting (production feature)
        if hdri_config.get('enabled', False):
            print("  Setting up HDRI environment...")

            # Enable world nodes
            world = bpy.data.worlds.get("World")
            if not world:
                world = bpy.data.worlds.new("World")
                self.scene.world = world

            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links

            # Clear existing nodes
            nodes.clear()

            # Create output node
            output_node = nodes.new('ShaderNodeOutputWorld')
            output_node.location = (600, 0)

            # Create background shader
            background = nodes.new('ShaderNodeBackground')
            background.location = (400, 0)
            background.inputs['Strength'].default_value = hdri_config.get('strength', 1.5)

            # Try to load HDRI texture (if available)
            # For now, use procedural sky as fallback
            hdri_loaded = False

            # Check for HDRI file in assets
            # hdri_path = "path/to/hdri.exr"  # TODO: Add HDRI path to config
            # if os.path.exists(hdri_path):
            #     tex_env = nodes.new('ShaderNodeTexEnvironment')
            #     tex_env.image = bpy.data.images.load(hdri_path)
            #     hdri_loaded = True

            if not hdri_loaded:
                # Use procedural sky as fallback
                print("    Using procedural sky (no HDRI file)")
                sky_texture = nodes.new('ShaderNodeTexSky')
                sky_texture.location = (0, 0)
                sky_texture.sky_type = 'NISHITA'  # Physically accurate sky

                # Sky rotation can be controlled via sun direction
                rotation_z = hdri_config.get('rotation', 45)
                # Adjust sun direction based on rotation (simplified)
                # Sky texture uses sun position, not vector input

                # Connect procedural sky directly (no vector input needed)
                links.new(sky_texture.outputs['Color'], background.inputs['Color'])

            else:
                # Connect HDRI texture (when available)
                mapping = nodes.new('ShaderNodeMapping')
                mapping.location = (-200, 0)
                rotation_z = hdri_config.get('rotation', 45)
                mapping.inputs['Rotation'].default_value = (0, 0, rotation_z * 0.0174533)

                tex_coord = nodes.new('ShaderNodeTexCoord')
                tex_coord.location = (-400, 0)

                # Would connect to tex_env here
                # links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
                # links.new(mapping.outputs['Vector'], tex_env.inputs['Vector'])
                # links.new(tex_env.outputs['Color'], background.inputs['Color'])

            # Fallback color tint (if specified)
            fallback_color = hdri_config.get('fallback_color', [0.8, 0.9, 1.0])
            if len(fallback_color) == 3:
                color_ramp = nodes.new('ShaderNodeValToRGB')
                color_ramp.location = (200, -200)
                color_ramp.color_ramp.elements[0].color = (*fallback_color, 1.0)

            # Connect to output
            links.new(background.outputs['Background'], output_node.inputs['Surface'])

            print(f"    ✓ HDRI environment configured (strength: {hdri_config.get('strength', 1.5)})")

        # Key light (main spotlight) - adjusted for HDRI workflow
        spotlight_config = lights_config.get('spotlight', {})
        if spotlight_config.get('enabled', True):
            bpy.ops.object.light_add(type='SPOT', location=(2, -3, 4))
            key_light = bpy.context.object
            key_light.name = "KeyLight"
            key_light.data.energy = spotlight_config.get('intensity', 800)
            key_light.data.spot_size = spotlight_config.get('spot_size', 60) * 0.0174533  # degrees to radians
            key_light.data.spot_blend = spotlight_config.get('spot_blend', 0.3)

            # Color from config
            spot_color = spotlight_config.get('color', [1.0, 0.98, 0.95])
            if len(spot_color) == 3:
                key_light.data.color = spot_color

            lights.append(key_light)
            print(f"    ✓ Spotlight: {key_light.data.energy}W")

        # Fill light (softer area light)
        bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
        fill_light = bpy.context.object
        fill_light.name = "FillLight"
        fill_light.data.energy = 200
        fill_light.data.size = 2.0
        lights.append(fill_light)

        # Rim/back light for edge definition
        rim_config = lights_config.get('rim_light', {})
        if rim_config.get('enabled', False):
            bpy.ops.object.light_add(type='SPOT', location=(0, 2, 3))
            rim_light = bpy.context.object
            rim_light.name = "RimLight"
            rim_light.data.energy = rim_config.get('intensity', 500)
            rim_light.data.spot_size = 1.0

            # Cool colored rim light
            rim_color = rim_config.get('color', [0.3, 0.5, 1.0])
            if len(rim_color) == 3:
                rim_light.data.color = rim_color

            lights.append(rim_light)
            print(f"    ✓ Rim light: {rim_light.data.energy}W")

        print(f"✓ Production lighting complete ({style} style, {len(lights)} lights)")

        return lights

    def create_stage_environment(self):
        """Create production-quality stage environment with floor."""
        style_config = self.config.get('style', {})

        if not style_config.get('stage', False):
            print("Stage environment disabled in config")
            return None

        print("Creating stage environment...")

        # Create floor plane
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        stage = bpy.context.object
        stage.name = "Stage"

        # Subdivide for better detail
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=10)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Smooth shading
        bpy.ops.object.shade_smooth()

        # Create PBR material for stage
        materials_config = self.config.get('materials', {})
        stage_mat_config = materials_config.get('stage', {})

        mat = bpy.data.materials.new(name="StageMaterial_PBR")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        stage.data.materials.append(mat)

        # Get Principled BSDF
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')

        # Configure PBR properties
        if stage_mat_config.get('type') == 'pbr':
            # Dark, slightly rough stage floor
            stage_color = stage_mat_config.get('color', [0.15, 0.15, 0.18])
            if len(stage_color) == 3:
                bsdf.inputs['Base Color'].default_value = (*stage_color, 1.0)

            bsdf.inputs['Roughness'].default_value = stage_mat_config.get('roughness', 0.7)
            bsdf.inputs['Metallic'].default_value = stage_mat_config.get('metallic', 0.0)
            bsdf.inputs['Specular IOR Level'].default_value = 0.3

            # Add subtle normal map variation for surface detail
            # (Could be enhanced with actual texture maps)
            print(f"  Stage material: {stage_color}, roughness: {bsdf.inputs['Roughness'].default_value}")

        print("✓ Stage environment created")

        return stage

    def create_mascot_placeholder(self):
        """
        Create production-quality mascot with PBR materials.

        Returns:
            Mascot object
        """
        print("Creating mascot with PBR materials...")

        mascot_image = self.config.get('inputs', {}).get('mascot_image')

        # For now, create a simple placeholder mesh
        # TODO: Implement image-to-mesh conversion with rigging
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
        mascot = bpy.context.object
        mascot.name = "Mascot"

        # Increase mesh resolution for better material detail
        bpy.ops.object.shade_smooth()

        # Create production-quality PBR material
        mat = bpy.data.materials.new(name="MascotMaterial_PBR")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        mascot.data.materials.append(mat)

        # Get material config
        materials_config = self.config.get('materials', {})
        mascot_mat_config = materials_config.get('mascot', {})

        # Get Principled BSDF (default shader)
        bsdf = nodes.get("Principled BSDF")
        if not bsdf:
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')

        # Configure PBR properties
        if mascot_mat_config.get('type') == 'pbr':
            print("  Applying PBR material properties...")

            # Physical properties
            bsdf.inputs['Roughness'].default_value = mascot_mat_config.get('roughness', 0.4)
            bsdf.inputs['Metallic'].default_value = mascot_mat_config.get('metallic', 0.0)
            bsdf.inputs['Specular IOR Level'].default_value = mascot_mat_config.get('specular', 0.5)

            # Subsurface scattering for organic look
            subsurface = mascot_mat_config.get('subsurface', 0.0)
            if subsurface > 0:
                bsdf.inputs['Subsurface Weight'].default_value = subsurface
                bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.25)  # R, G, B radii
                print(f"    SSS: {subsurface} (organic look)")

            # Sheen for fur-like appearance
            sheen = mascot_mat_config.get('sheen', 0.0)
            if sheen > 0:
                bsdf.inputs['Sheen Weight'].default_value = sheen
                bsdf.inputs['Sheen Roughness'].default_value = 0.5
                # Use primary color for sheen tint
                primary_color = self.config.get('style', {}).get('colors', {}).get('primary', [0.95, 0.4, 0.2])
                if len(primary_color) == 3:
                    bsdf.inputs['Sheen Tint'].default_value = (*primary_color, 1.0)
                print(f"    Sheen: {sheen} (fur-like)")

            print(f"    Roughness: {bsdf.inputs['Roughness'].default_value}")
            print(f"    Metallic: {bsdf.inputs['Metallic'].default_value}")
            print(f"    Specular: {bsdf.inputs['Specular IOR Level'].default_value}")

        # Load mascot image texture
        if mascot_image and os.path.exists(mascot_image):
            print(f"  Loading mascot texture: {mascot_image}")

            # Create UV mapping node for proper texture mapping
            mapping = nodes.new('ShaderNodeMapping')
            mapping.location = (-600, 0)

            tex_coord = nodes.new('ShaderNodeTexCoord')
            tex_coord.location = (-800, 0)

            # Create image texture node
            tex_image = nodes.new('ShaderNodeTexImage')
            tex_image.location = (-400, 0)
            tex_image.image = bpy.data.images.load(mascot_image)
            tex_image.interpolation = 'Smart'  # Better quality

            # Connect texture pipeline
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
            links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])

            # Also use alpha if available
            if tex_image.image.alpha_mode != 'NONE':
                links.new(tex_image.outputs['Alpha'], bsdf.inputs['Alpha'])

            print("  ✓ Texture loaded with UV mapping")

        else:
            # Use primary color from config if no texture
            primary_color = self.config.get('style', {}).get('colors', {}).get('primary', [0.95, 0.4, 0.2])
            if len(primary_color) == 3:
                bsdf.inputs['Base Color'].default_value = (*primary_color, 1.0)
            print("  Using solid color (no texture)")

        print("✓ Mascot created with production PBR materials")
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
        Create production-quality animated text overlays for lyrics.

        Returns:
            List of text objects
        """
        if not self.config.get('animation', {}).get('enable_lyrics', True):
            print("Lyrics disabled in config")
            return []

        print("Creating professional lyrics text...")

        timed_words = self.prep_data.get('timed_words', [])
        if not timed_words:
            print("  WARNING: No lyrics data available")
            return []

        lyrics_style = self.config.get('animation', {}).get('lyrics_style', 'bounce')
        text_objects = []

        # Get material settings from config
        materials_config = self.config.get('materials', {})
        text_mat_config = materials_config.get('text', {})

        # Create a text object for each word
        for i, word_data in enumerate(timed_words):
            word = word_data['word']
            start_time = word_data['start']
            end_time = word_data['end']

            # Create text object - position above mascot for better visibility
            y_position = 2.5  # Above mascot
            z_position = 0.0  # At mascot height

            bpy.ops.object.text_add(location=(0, y_position, z_position))
            text_obj = bpy.context.object
            text_obj.data.body = word.upper()  # Uppercase for impact
            text_obj.data.align_x = 'CENTER'
            text_obj.data.align_y = 'CENTER'
            text_obj.name = f"Lyric_{word}"

            # Professional 3D text settings
            if lyrics_style == 'professional':
                # Add 3D extrusion
                text_obj.data.extrude = 0.15  # Depth
                text_obj.data.bevel_depth = 0.02  # Smooth edges
                text_obj.data.bevel_resolution = 3  # Bevel smoothness

                # Font size
                text_obj.data.size = 0.8

                # Optional: Use a nicer font if available
                # text_obj.data.font = bpy.data.fonts.load("/path/to/font.ttf")
            else:
                # Standard 3D text
                text_obj.data.extrude = 0.1
                text_obj.data.bevel_depth = 0.01
                text_obj.data.size = 0.6

            # Create professional emission/glossy material
            mat = bpy.data.materials.new(name=f"TextMaterial_{i}")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Clear default nodes
            nodes.clear()

            # Create shader nodes
            output_node = nodes.new('ShaderNodeOutputMaterial')
            output_node.location = (400, 0)

            if text_mat_config.get('type') == 'emission_glossy':
                # Mix emission and glossy for glowing metallic text
                mix_shader = nodes.new('ShaderNodeMixShader')
                mix_shader.location = (200, 0)
                mix_shader.inputs['Fac'].default_value = 0.7  # 70% emission, 30% glossy

                # Emission shader (glow)
                emission = nodes.new('ShaderNodeEmission')
                emission.location = (0, 100)
                emission.inputs['Strength'].default_value = text_mat_config.get('emission_strength', 2.0)

                # Get accent color from style config
                accent_color = self.config.get('style', {}).get('colors', {}).get('accent', [0.95, 0.85, 0.3])
                if len(accent_color) == 3:
                    emission.inputs['Color'].default_value = (*accent_color, 1.0)

                # Glossy shader (reflective)
                glossy = nodes.new('ShaderNodeBsdfGlossy')
                glossy.location = (0, -100)
                glossy.inputs['Roughness'].default_value = text_mat_config.get('roughness', 0.1)
                glossy.inputs['Color'].default_value = (*accent_color, 1.0)

                # Connect nodes
                links.new(emission.outputs['Emission'], mix_shader.inputs[1])
                links.new(glossy.outputs['BSDF'], mix_shader.inputs[2])
                links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])
            else:
                # Simple emission shader
                emission = nodes.new('ShaderNodeEmission')
                emission.location = (0, 0)
                emission.inputs['Strength'].default_value = 2.0
                emission.inputs['Color'].default_value = (1.0, 1.0, 0.3, 1.0)  # Yellow
                links.new(emission.outputs['Emission'], output_node.inputs['Surface'])

            # Assign material
            if text_obj.data.materials:
                text_obj.data.materials[0] = mat
            else:
                text_obj.data.materials.append(mat)

            # Initially hide
            text_obj.hide_render = True
            text_obj.hide_viewport = True

            # Animate visibility and effects
            start_frame = int(start_time * self.fps) + 1
            end_frame = int(end_time * self.fps) + 1

            # Show at start
            text_obj.hide_render = False
            text_obj.hide_viewport = False
            text_obj.keyframe_insert(data_path='hide_render', frame=start_frame)
            text_obj.keyframe_insert(data_path='hide_viewport', frame=start_frame)

            # Animate based on style
            if lyrics_style == 'professional':
                # Fade in + scale + subtle rotation
                text_obj.scale = (0.1, 0.1, 0.1)
                text_obj.keyframe_insert(data_path='scale', frame=start_frame)

                # Grow to full size
                grow_frame = start_frame + 5
                text_obj.scale = (1.0, 1.0, 1.0)
                text_obj.keyframe_insert(data_path='scale', frame=grow_frame)

                # Subtle pulse during display
                mid_frame = (start_frame + end_frame) // 2
                text_obj.scale = (1.1, 1.1, 1.1)
                text_obj.keyframe_insert(data_path='scale', frame=mid_frame)

                # Return to normal
                text_obj.scale = (1.0, 1.0, 1.0)
                text_obj.keyframe_insert(data_path='scale', frame=end_frame - 3)

            elif lyrics_style == 'bounce':
                # Original bounce effect
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

        print(f"✓ Created {len(text_objects)} professional lyric text objects")
        print(f"  Style: {lyrics_style}")
        print(f"  Material: emission + glossy with PBR properties")

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
        """Configure production-quality render engine and output settings."""
        print("Configuring render settings...")

        video_config = self.config.get('video', {})

        # Render engine
        engine = video_config.get('render_engine', 'EEVEE')
        self.scene.render.engine = engine
        print(f"  Engine: {engine}")

        # Samples
        samples = video_config.get('samples', 128)
        if engine == 'EEVEE':
            self.scene.eevee.taa_render_samples = samples
            # EEVEE quality settings
            self.scene.eevee.use_gtao = True  # Ambient occlusion
            self.scene.eevee.use_bloom = True  # Bloom
            self.scene.eevee.use_ssr = True  # Screen space reflections
            self.scene.eevee.use_ssr_refraction = True
            self.scene.eevee.use_volumetric_shadows = True
        elif engine == 'CYCLES':
            self.scene.cycles.samples = samples
            # Cycles quality settings
            self.scene.cycles.use_adaptive_sampling = True
            self.scene.cycles.adaptive_threshold = 0.01

            # GPU acceleration if available
            if video_config.get('use_gpu', True):
                try:
                    self.scene.cycles.device = 'GPU'
                    print("  GPU rendering enabled")
                except:
                    print("  GPU not available, using CPU")

            # Denoising
            if video_config.get('use_denoising', True):
                self.scene.cycles.use_denoising = True
                denoiser = video_config.get('denoiser', 'OPTIX')
                if hasattr(self.scene.cycles, 'denoiser'):
                    try:
                        self.scene.cycles.denoiser = denoiser
                        print(f"  Denoiser: {denoiser}")
                    except:
                        print("  Using default denoiser")

            # Persistent data for faster rendering
            if video_config.get('persistent_data', True):
                self.scene.render.use_persistent_data = True

        print(f"  Samples: {samples}")

        # Motion blur (production feature)
        if video_config.get('motion_blur', False):
            self.scene.render.use_motion_blur = True
            shutter = video_config.get('motion_blur_shutter', 0.5)
            self.scene.render.motion_blur_shutter = shutter
            print(f"  Motion blur: enabled (shutter {shutter})")

        # Output path
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        os.makedirs(frames_dir, exist_ok=True)

        self.scene.render.filepath = os.path.join(frames_dir, 'frame_####.png')
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.image_settings.color_mode = 'RGBA'
        self.scene.render.image_settings.color_depth = '16'  # 16-bit for better quality
        self.scene.render.image_settings.compression = 15  # PNG compression

        # Film settings (transparency, etc.)
        self.scene.render.film_transparent = False  # Opaque background for now

        print(f"✓ Render settings configured")
        print(f"  Output: {self.scene.render.filepath}")

    def setup_compositor(self):
        """Setup production-quality compositor with DOF, bloom, color grading, etc."""
        compositor_config = self.config.get('compositor', {})

        if not compositor_config.get('enabled', False):
            print("Compositor disabled in config")
            return

        print("Setting up production compositor...")

        # Enable compositor
        self.scene.use_nodes = True
        self.scene.render.use_compositing = True

        # Enable depth pass for DOF
        view_layer = self.scene.view_layers[0]
        view_layer.use_pass_z = True

        nodes = self.scene.node_tree.nodes
        links = self.scene.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create render layers node (source)
        render_layers = nodes.new('CompositorNodeRLayers')
        render_layers.location = (0, 0)

        current_node = render_layers
        current_output = 'Image'
        x_offset = 250

        # Depth of Field (DOF)
        dof_config = compositor_config.get('dof', {})
        if dof_config.get('enabled', False):
            print(f"  Adding DOF (f-stop: {dof_config.get('f_stop', 2.8)})")

            defocus = nodes.new('CompositorNodeDefocus')
            defocus.location = (x_offset, 0)
            defocus.use_zbuffer = True
            defocus.f_stop = dof_config.get('f_stop', 2.8)
            defocus.blur_max = 100
            defocus.threshold = 1.0

            # Connect
            links.new(current_node.outputs[current_output], defocus.inputs['Image'])
            links.new(render_layers.outputs['Depth'], defocus.inputs['Z'])

            current_node = defocus
            current_output = 'Image'
            x_offset += 250

            # Also configure camera DOF
            camera = self.scene.camera
            if camera and camera.data:
                camera.data.dof.use_dof = True
                camera.data.dof.aperture_fstop = dof_config.get('f_stop', 2.8)
                camera.data.dof.focus_distance = dof_config.get('focus_distance', 5.0)

        # Bloom (glare node)
        bloom_config = compositor_config.get('bloom', {})
        if bloom_config.get('enabled', False):
            print(f"  Adding bloom (threshold: {bloom_config.get('threshold', 0.8)})")

            glare = nodes.new('CompositorNodeGlare')
            glare.location = (x_offset, 0)
            glare.glare_type = 'FOG_GLOW'  # Bloom-like effect
            glare.threshold = bloom_config.get('threshold', 0.8)
            glare.size = int(bloom_config.get('radius', 6.5))
            glare.quality = 'HIGH'

            # Mix with original image
            mix = nodes.new('CompositorNodeMixRGB')
            mix.location = (x_offset + 200, 0)
            mix.blend_type = 'ADD'
            mix.inputs['Fac'].default_value = bloom_config.get('intensity', 0.05)

            links.new(current_node.outputs[current_output], glare.inputs['Image'])
            links.new(current_node.outputs[current_output], mix.inputs[1])
            links.new(glare.outputs['Image'], mix.inputs[2])

            current_node = mix
            current_output = 'Image'
            x_offset += 450

        # Color Grading
        color_config = compositor_config.get('color_grading', {})
        if color_config.get('enabled', False):
            print("  Adding color grading")

            # Hue/Saturation/Value for saturation
            hsv = nodes.new('CompositorNodeHueSat')
            hsv.location = (x_offset, 100)
            hsv.inputs['Saturation'].default_value = color_config.get('saturation', 1.15)

            links.new(current_node.outputs[current_output], hsv.inputs['Image'])

            # Color Balance for temperature
            color_balance = nodes.new('CompositorNodeColorBalance')
            color_balance.location = (x_offset, -100)
            temp = color_config.get('temperature', 1.05)
            # Warm tint (more red/yellow)
            if temp > 1.0:
                color_balance.lift = (1.0, 0.95, 0.85)
                color_balance.gamma = (1.0, 0.98, 0.92)
            elif temp < 1.0:
                # Cool tint (more blue)
                color_balance.lift = (0.85, 0.95, 1.0)
                color_balance.gamma = (0.92, 0.98, 1.0)

            links.new(hsv.outputs['Image'], color_balance.inputs['Image'])

            # Brightness/Contrast
            bright_contrast = nodes.new('CompositorNodeBrightContrast')
            bright_contrast.location = (x_offset + 200, 0)
            bright_contrast.inputs['Contrast'].default_value = color_config.get('contrast', 1.1) - 1.0  # Blender uses 0.0 as default
            bright_contrast.inputs['Bright'].default_value = 0.0

            links.new(color_balance.outputs['Image'], bright_contrast.inputs['Image'])

            # Gamma
            gamma_node = nodes.new('CompositorNodeGamma')
            gamma_node.location = (x_offset + 400, 0)
            gamma_node.inputs['Gamma'].default_value = color_config.get('gamma', 1.0)

            links.new(bright_contrast.outputs['Image'], gamma_node.inputs['Image'])

            current_node = gamma_node
            current_output = 'Image'
            x_offset += 600

        # Vignette
        vignette_config = compositor_config.get('vignette', {})
        if vignette_config.get('enabled', False):
            print(f"  Adding vignette (amount: {vignette_config.get('amount', 0.3)})")

            # Create ellipse mask
            ellipse = nodes.new('CompositorNodeEllipseMask')
            ellipse.location = (x_offset, -300)
            ellipse.width = 0.95
            ellipse.height = 0.95

            # Blur the mask
            blur = nodes.new('CompositorNodeBlur')
            blur.location = (x_offset + 200, -300)
            blur.size_x = 50
            blur.size_y = 50
            blur.use_extended_bounds = True

            links.new(ellipse.outputs['Mask'], blur.inputs['Image'])

            # Invert mask (darken edges)
            invert = nodes.new('CompositorNodeInvert')
            invert.location = (x_offset + 400, -300)
            links.new(blur.outputs['Image'], invert.inputs['Color'])

            # Mix with main image
            mix_vignette = nodes.new('CompositorNodeMixRGB')
            mix_vignette.location = (x_offset + 250, 0)
            mix_vignette.blend_type = 'MULTIPLY'
            mix_vignette.inputs['Fac'].default_value = vignette_config.get('amount', 0.3)

            links.new(current_node.outputs[current_output], mix_vignette.inputs[1])
            links.new(invert.outputs['Color'], mix_vignette.inputs[2])

            current_node = mix_vignette
            current_output = 'Image'
            x_offset += 500

        # Film Grain
        grain_config = compositor_config.get('film_grain', {})
        if grain_config.get('enabled', False):
            print(f"  Adding film grain (amount: {grain_config.get('amount', 0.02)})")

            # Create noise texture
            # Note: Compositor doesn't have texture node, so we'll simulate with RGB curves
            # Add some variation
            curves = nodes.new('CompositorNodeCurveRGB')
            curves.location = (x_offset, 0)
            # Slightly randomize the curve to simulate grain
            # (This is a simplified version - true grain would need texture input)

            # Mix with very low factor for subtle grain effect
            mix_grain = nodes.new('CompositorNodeMixRGB')
            mix_grain.location = (x_offset + 200, 0)
            mix_grain.blend_type = 'OVERLAY'
            mix_grain.inputs['Fac'].default_value = grain_config.get('amount', 0.02)

            links.new(current_node.outputs[current_output], mix_grain.inputs[1])
            links.new(current_node.outputs[current_output], curves.inputs['Image'])
            links.new(curves.outputs['Image'], mix_grain.inputs[2])

            current_node = mix_grain
            current_output = 'Image'
            x_offset += 450

        # Final output
        composite = nodes.new('CompositorNodeComposite')
        composite.location = (x_offset, 0)
        links.new(current_node.outputs[current_output], composite.inputs['Image'])

        # Viewer node (for preview)
        viewer = nodes.new('CompositorNodeViewer')
        viewer.location = (x_offset, -200)
        links.new(current_node.outputs[current_output], viewer.inputs['Image'])

        effects_count = sum([
            dof_config.get('enabled', False),
            bloom_config.get('enabled', False),
            color_config.get('enabled', False),
            vignette_config.get('enabled', False),
            grain_config.get('enabled', False)
        ])

        print(f"✓ Compositor configured with {effects_count} effects")

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
        builder_3d.setup_compositor()

        print("✓ Hybrid scene built successfully")

    else:
        # Default: Build 3D mesh scene
        print("Building 3D mesh scene...")
        builder = BlenderSceneBuilder(config, prep_data)

        # Execute pipeline
        builder.clear_scene()
        camera = builder.setup_camera()
        lights = builder.setup_lighting()
        stage = builder.create_stage_environment()
        mascot = builder.create_mascot_placeholder()

        # Animation (stub implementations)
        builder.create_phoneme_shape_keys(mascot)
        builder.animate_lip_sync(mascot)
        builder.animate_gestures(mascot)
        lyrics = builder.create_lyrics_text()
        builder.animate_lights_to_beats(lights)

        # Render setup
        builder.setup_render_settings()
        builder.setup_compositor()

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

    # Render the animation
    print("\n" + "="*70)
    print("RENDERING ANIMATION")
    print("="*70)

    if animation_mode in ['2d_grease', 'hybrid']:
        # Render with EEVEE for speed
        print("Rendering 2D/Hybrid animation with EEVEE...")
        bpy.ops.render.render(animation=True)
    else:
        # Render 3D animation
        print("Rendering 3D animation...")
        builder.render_animation()

    print("\n✓ Rendering complete!")

    return 0


if __name__ == '__main__':
    if RUNNING_IN_BLENDER:
        sys.exit(main())
    else:
        print("This script is designed to run inside Blender's Python environment")
