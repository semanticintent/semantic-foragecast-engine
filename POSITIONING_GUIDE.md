# Positioning Guide - Lyrics and Mascot

## Overview

This guide explains how the mascot and lyrics positioning works in the Semantic Foragecast Engine, and how to debug positioning issues.

## Scene Layout

### Coordinate System

The scene uses Blender's coordinate system:
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Back (+) to Front (-)
- **Z-axis**: Down (-) to Up (+)

### Key Positions

| Element | Position (X, Y, Z) | Description |
|---------|-------------------|-------------|
| **Mascot** | (0, 0, 1) | Center of scene, 1 unit above origin |
| **Camera** | (0, -6, 1) | 6 units in front, looking back at mascot |
| **Lyrics Text** | (0, -2, 0.2) | 2 units in front of mascot, lower on screen |
| **Origin** | (0, 0, 0) | World center |

### Visual Layout

```
         [Camera at Y=-6]
              |
              | (looking this direction)
              v
     [Text at Y=-2, Z=0.2]

     [Mascot at Y=0, Z=1]

    ----- [Stage at Z=0] -----
```

## Lyrics Positioning

### Default Setup (Fixed in Latest Version)

**Previous Issue:**
- Lyrics were positioned at `(0, 0, -0.5)`
- This put them **behind** the mascot and often off-screen

**Current Fix:**
- Lyrics now positioned at `(0, -2, 0.2)`
- Y=-2: Closer to camera than mascot (better visibility)
- Z=0.2: In lower third of frame (subtitle position)

### Why This Works

1. **Camera at Y=-6** looks toward positive Y direction
2. **Text at Y=-2** is between camera and mascot
3. **Text appears "in front"** from camera's perspective
4. **Lower Z value (0.2)** places text in lower screen area

## Debug Mode

### Enabling Debug Visualization

Add this to your `config.yaml`:

```yaml
advanced:
  debug_mode: true
```

### What Debug Mode Shows

When enabled, colored sphere markers appear at key positions:

- 🔴 **Red Sphere**: Camera position
- 🟢 **Green Sphere**: Mascot position
- 🔵 **Blue Sphere**: Text zone position
- 🟡 **Yellow Sphere**: World origin

Each marker includes a text label for easy identification.

### Using Debug Mode

1. Enable `debug_mode: true` in config
2. Run the pipeline: `python main.py`
3. Check the first rendered frame
4. Verify all elements are positioned correctly
5. Disable debug mode for final render

## Adjusting Positions

### Moving Lyrics Horizontally

Edit `blender_script.py` line ~567:

```python
y_position = -2.0  # More negative = closer to camera
```

- `-1.5`: Very close to camera (large text)
- `-2.0`: Default (good visibility)
- `-3.0`: Further from camera (smaller text)

### Moving Lyrics Vertically

Edit `blender_script.py` line ~568:

```python
z_position = 0.2  # Higher = moves up on screen
```

- `0.5`: Middle of screen
- `0.2`: Lower third (subtitle position) - DEFAULT
- `-0.2`: Bottom of screen

### Moving Lyrics Left/Right

Add X-offset to text creation:

```python
bpy.ops.object.text_add(location=(x_offset, y_position, z_position))
```

- Negative X: Left
- Positive X: Right
- 0: Center (default)

## Synchronization

### How Lip Sync Works

1. **Audio File** → Analyzed by Phase 1 (`prep_audio.py`)
2. **Phonemes** → Extracted via Rhubarb or mock generation
3. **Timing Data** → Stored in `prep_data.json`
4. **Blender** → Applies phoneme shape keys to mascot mesh
5. **Result** → Mascot mouth moves in sync with audio

### How Lyrics Sync Works

1. **Lyrics File** (`lyrics.txt`) → Manually timed by you
2. **Format**: `START-END word|word|word`
3. **Phase 1** → Parses timing and words
4. **Blender** → Creates text objects with timed visibility
5. **Result** → Words appear/disappear at specified times

### Important: Manual Sync Required

⚠️ **The lyrics timing is NOT automatically synced to the audio!**

You must manually ensure:
- Lyrics timestamps match when words are actually sung
- Format: `0:00-0:03 Hello|world|test`
- Each word gets equal time in its range

### Example Lyrics File

```
0:00-0:03 Welcome|to|the|show
0:03-0:06 Dancing|in|the|lights
0:06-0:09 Music|brings|us|together
```

## Common Issues

### Issue: Lyrics Not Visible

**Symptoms**: Text doesn't appear in rendered frames

**Solutions**:
1. Enable `debug_mode: true` to see text zone marker
2. Check lyrics file exists and has content
3. Verify `enable_lyrics: true` in config
4. Ensure text timing overlaps with rendered frames

### Issue: Lyrics Behind Mascot

**Symptoms**: Text is blocked by mascot

**Solution**:
- Already fixed in latest version
- Text now at Y=-2 (in front of mascot at Y=0)

### Issue: Lip Sync Not Working

**Symptoms**: Mascot mouth doesn't move

**Solutions**:
1. Check `enable_lipsync: true` in config
2. Verify phoneme data in `prep_data.json`
3. Ensure mascot has shape keys (check Blender output)
4. For 3D mode: Requires actual mesh deformation (currently stub)

### Issue: Lyrics Out of Sync

**Symptoms**: Words appear at wrong time

**Solution**:
- Edit `lyrics.txt` manually to match audio timing
- Use audio editor to find exact timestamps
- Format: `MM:SS-MM:SS word|word|word`

## Technical Details

### Text Object Properties

Default text configuration:
- **Size**: 0.6-0.8 units (0.8 for professional style)
- **Alignment**: Centered X and Y
- **Material**: Emission shader (glows)
- **Extrusion**: 0.1-0.15 units (3D depth)
- **Animation**: Scale bounce or professional fade

### Text Materials

Professional style:
- 70% Emission (glow)
- 30% Glossy (reflective)
- Accent color from config
- Emission strength: 2.0

### Animation Timing

Lyrics animation phases:
1. **Appear** (frames 1-5): Scale from 0.1 to 1.0
2. **Display** (bulk of duration): Visible at scale 1.0
3. **Pulse** (mid-point): Brief scale to 1.1
4. **Disappear** (last 3 frames): Hide

## Best Practices

1. **Always test with debug mode first** when changing positions
2. **Use preview mode** (`preview_mode: true`) for fast iteration
3. **Check first frame** to verify positioning before full render
4. **Match lyrics timing** carefully to audio for best results
5. **Use professional style** for production-quality text rendering

## Related Files

- `blender_script.py` - Main positioning code (lines 563-570, 1046-1117)
- `grease_pencil.py` - 2D mode text positioning (lines 590-650)
- `config.yaml` - Configuration including debug_mode
- `assets/lyrics.txt` - Lyrics timing file

## Version History

- **v1.0**: Initial implementation (text behind mascot)
- **v1.1**: Fixed positioning (text in front at Y=-2, Z=0.2)
- **v1.1**: Added debug visualization mode

---

**Last Updated**: 2025-11-18
**Related**: See README.md for full pipeline documentation
