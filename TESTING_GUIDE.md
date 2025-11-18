# Testing Guide - Quick Pipeline Validation

This guide shows how to test the full pipeline quickly with low-resolution rendering to verify everything works before doing a full production render.

## Quick Reference

| Config | Resolution | FPS | Render Time* | File Size | Use Case |
|--------|-----------|-----|--------------|-----------|----------|
| **config_ultra_fast.yaml** | 320x180 | 12 | ~2-3 min | ~200KB | Fastest verification |
| **config_quick_test.yaml** | 640x360 | 24 | ~5-10 min | ~1-2MB | Good quality test |
| **config.yaml** | 1920x1080 | 24 | ~30-60 min | ~5-10MB | Production quality |

*For 30-second song on typical hardware

---

## Method 1: Automated Quick Test (Recommended)

### Using the Quick Test Script

The `quick_test.py` script automates the entire pipeline:

```bash
# Basic quick test (uses existing lyrics.txt)
python quick_test.py

# Auto-generate lyrics + full test
python quick_test.py --auto-lyrics

# Test without lyrics display
python quick_test.py --no-lyrics

# Enable debug visualization
python quick_test.py --debug
```

**What it does:**
1. ✓ Checks all required files exist
2. ✓ Optionally generates lyrics with Whisper
3. ✓ Runs Phase 1 (audio prep) - ~10 seconds
4. ✓ Runs Phase 2 (rendering) - ~5-10 minutes at 360p
5. ✓ Runs Phase 3 (export) - ~30 seconds
6. ✓ Reports total time and output location

**Expected output:**
```
✓ Full pipeline completed in 7.3 minutes
Output video: outputs/quick_test/quick_test.mp4
Resolution: 640x360 (360p)
File size: 1.45 MB
```

---

## Method 2: Manual Step-by-Step

### Ultra-Fast Test (2-3 minutes total)

Fastest possible test - minimal quality but verifies pipeline works:

```bash
# 1. Optional: Auto-generate lyrics
python auto_lyrics_whisper.py assets/song.wav \
    --output assets/lyrics.txt \
    --model tiny

# 2. Run pipeline with ultra-fast config
python main.py --config config_ultra_fast.yaml

# 3. Check output
ls -lh outputs/ultra_fast/ultra_fast.mp4
```

**Resolution**: 320x180 (180p)
**Quality**: Very low (grainy, but proves it works)
**Time**: 2-3 minutes for 30s song

---

### Quick Test (5-10 minutes total)

Better quality while still being fast:

```bash
# 1. Optional: Auto-generate lyrics
python auto_lyrics_whisper.py assets/song.wav \
    --output assets/lyrics.txt \
    --model base

# 2. Run pipeline with quick test config
python main.py --config config_quick_test.yaml

# 3. Check output
ls -lh outputs/quick_test/quick_test.mp4
```

**Resolution**: 640x360 (360p)
**Quality**: Medium (clearly visible, good for testing)
**Time**: 5-10 minutes for 30s song

---

## Configuration Comparison

### Ultra-Fast Config Features

```yaml
resolution: [320, 180]  # 180p - tiny but fast
fps: 12                 # Half frame rate
samples: 16             # Minimal quality
mode: "2d_grease"       # 2D is faster than 3D
enable_effects: false   # No fog, particles, etc.
quality: "low"          # Fast encoding
```

**Use when**: You just want to verify the pipeline runs

---

### Quick Test Config Features

```yaml
resolution: [640, 360]  # 360p - watchable quality
fps: 24                 # Normal frame rate
samples: 32             # Decent quality
mode: "2d_grease"       # 2D for speed
enable_effects: false   # Minimal effects
quality: "medium"       # Balanced encoding
```

**Use when**: You want to check positioning, timing, and overall look

---

### Production Config Features

```yaml
resolution: [1920, 1080]  # 1080p - full HD
fps: 24                   # Standard
samples: 128              # High quality
mode: "3d" or "2d_grease" # Your choice
enable_effects: true      # All effects
quality: "high"           # Best encoding
```

**Use when**: Final output for sharing/publishing

---

## Timing Breakdown (30-second song)

### Ultra-Fast Config (320x180)

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1 (Audio Prep) | 10s | Same for all configs |
| Phase 2 (Rendering) | 1-2 min | 180p @ 12fps = ~180 frames |
| Phase 3 (Export) | 20s | Small file, quick encode |
| **Total** | **2-3 min** | Fastest verification |

### Quick Test Config (640x360)

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1 (Audio Prep) | 10s | Same for all configs |
| Phase 2 (Rendering) | 4-8 min | 360p @ 24fps = ~720 frames |
| Phase 3 (Export) | 30s | Medium file |
| **Total** | **5-10 min** | Good quality test |

### Production Config (1920x1080)

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1 (Audio Prep) | 10s | Same for all configs |
| Phase 2 (Rendering) | 25-50 min | 1080p @ 24fps = ~720 frames |
| Phase 3 (Export) | 1-2 min | Large file, slower encode |
| **Total** | **30-60 min** | Production quality |

*Times vary based on CPU/GPU performance*

---

## Performance Tips

### Speed Up Rendering

1. **Use 2D mode instead of 3D:**
   ```yaml
   animation:
     mode: "2d_grease"  # ~2x faster than "3d"
   ```

2. **Lower resolution:**
   ```yaml
   video:
     resolution: [640, 360]  # 1/9th pixels of 1080p
   ```

3. **Reduce samples:**
   ```yaml
   video:
     samples: 32  # Lower = faster but grainier
   ```

4. **Disable effects:**
   ```yaml
   animation:
     enable_effects: false
   effects:
     fog:
       enabled: false
     particles:
       enabled: false
   ```

5. **Use EEVEE not CYCLES:**
   ```yaml
   video:
     render_engine: "EEVEE"  # Much faster than CYCLES
   ```

6. **Lower FPS for testing:**
   ```yaml
   video:
     fps: 12  # Half the frames = half the time
   ```

---

## Testing Checklist

After running quick test, verify:

### Visual Elements
- [ ] Mascot visible and positioned correctly
- [ ] Lyrics appear in lower third of frame
- [ ] Lyrics NOT behind mascot
- [ ] Text is readable (even at low res)

### Animation
- [ ] Mascot moves on beats (gesture animation)
- [ ] Mouth shapes change (lip sync)
- [ ] Lyrics appear/disappear at correct times

### Audio
- [ ] Audio is synchronized with video
- [ ] No audio crackling or distortion
- [ ] Volume levels appropriate

### Timing
- [ ] Video length matches audio length
- [ ] All lyrics show up (none missing)
- [ ] Transitions are smooth

---

## Troubleshooting

### Rendering Takes Too Long

**Problem**: Phase 2 taking over 30 minutes for quick test

**Solutions**:
1. Use `config_ultra_fast.yaml` instead
2. Check CPU/GPU usage (should be high)
3. Close other applications
4. Reduce resolution further: `[320, 180]`

### Timeout Errors

**Problem**: Pipeline times out during rendering

**Solutions**:
1. Use quick test script with longer timeout:
   ```python
   # quick_test.py already has generous timeouts
   python quick_test.py
   ```

2. Run phases separately:
   ```bash
   python main.py --config config_quick_test.yaml --phase 1
   python main.py --config config_quick_test.yaml --phase 2
   python main.py --config config_quick_test.yaml --phase 3
   ```

### Output Video Too Small to See

**Problem**: 180p or 360p video too small

**Solutions**:
1. Use media player zoom/fullscreen
2. Use `config_quick_test.yaml` (360p) instead of ultra-fast
3. Remember: this is just for verification

### Lyrics Not Appearing

**Problem**: No lyrics visible in output

**Check**:
1. Does `assets/lyrics.txt` exist?
2. Is `enable_lyrics: true` in config?
3. Are lyrics timing within video duration?
4. Run with `debug_mode: true` to see text zone marker

---

## Complete Test Workflow

### First Time Setup

```bash
# 1. Install optional dependencies
pip install -r requirements-lyrics-auto.txt

# 2. Verify files
ls assets/song.wav assets/fox.png

# 3. Run ultra-fast test (verify it works)
python main.py --config config_ultra_fast.yaml

# 4. Check output
ls outputs/ultra_fast/ultra_fast.mp4
```

### Typical Development Workflow

```bash
# 1. Make changes to config or code

# 2. Quick test with automation
python quick_test.py --auto-lyrics

# 3. Review output
# (Check positioning, timing, etc.)

# 4. If good, render production quality
python main.py --config config.yaml
```

### Before Final Render

```bash
# 1. Test with quick config
python main.py --config config_quick_test.yaml

# 2. Verify everything looks good
# - Positioning correct
# - Timing accurate
# - Animations working

# 3. Enable debug mode for verification
# Edit config_quick_test.yaml: debug_mode: true
python main.py --config config_quick_test.yaml --phase 2

# 4. Check first frame for debug markers
# Should see colored spheres at key positions

# 5. If all good, do production render
python main.py --config config.yaml
```

---

## Expected File Sizes

| Resolution | Duration | Quality | Size Range |
|-----------|----------|---------|------------|
| 320x180 | 30s | Low | 100-300KB |
| 640x360 | 30s | Medium | 800KB-2MB |
| 1920x1080 | 30s | High | 4-10MB |

Larger files indicate:
- Higher quality (good)
- Longer duration (good)
- Encoding issues (check logs)

---

## Next Steps After Testing

Once quick test succeeds:

1. **Adjust positioning if needed** (see POSITIONING_GUIDE.md)
2. **Fine-tune lyrics timing** (edit lyrics.txt or regenerate)
3. **Enable debug mode** to verify positions
4. **Test with different styles** (2D vs 3D, different effects)
5. **Run production render** with full quality

---

## Summary

**For fastest verification**:
```bash
python main.py --config config_ultra_fast.yaml
```

**For better quality test**:
```bash
python quick_test.py --auto-lyrics
```

**For production**:
```bash
python main.py --config config.yaml
```

---

**Created**: 2025-11-18
**Related**: AUTOMATED_LYRICS_GUIDE.md, POSITIONING_GUIDE.md, README.md
