# Automated Lyrics Timing Guide

This guide explains three methods for automatically generating timed lyrics from audio files.

## Quick Comparison

| Method | Accuracy | Speed | Requirements | Best For |
|--------|----------|-------|--------------|----------|
| **Whisper** | ⭐⭐⭐⭐⭐ | Medium | `pip install openai-whisper` | Unknown lyrics, transcription needed |
| **Gentle** | ⭐⭐⭐⭐⭐ | Fast | Docker + Gentle server | Known lyrics, high accuracy |
| **Beat-Based** | ⭐⭐⭐ | Very Fast | Built-in (uses prep_data.json) | Quick tests, beat-synchronized songs |

---

## Method 1: Whisper (Recommended for Most Users)

### What It Does
- **Transcribes** audio automatically (no lyrics needed!)
- Provides **word-level timestamps**
- Works with any language
- Runs locally (no internet needed after model download)

### Installation

```bash
pip install openai-whisper
```

**Note**: First run will download ~150MB model file.

### Usage

```bash
# Basic usage
python auto_lyrics_whisper.py assets/song.wav --output assets/lyrics.txt

# With options
python auto_lyrics_whisper.py assets/song.wav \
    --output assets/lyrics.txt \
    --model base \
    --words-per-phrase 4 \
    --max-duration 3.0
```

### Model Sizes

| Model | Size | Speed | Accuracy | RAM Required |
|-------|------|-------|----------|--------------|
| `tiny` | 39MB | Very Fast | Good | ~1GB |
| `base` | 74MB | Fast | Better | ~1GB |
| `small` | 244MB | Medium | Very Good | ~2GB |
| `medium` | 769MB | Slow | Excellent | ~5GB |
| `large` | 1.5GB | Very Slow | Best | ~10GB |

**Recommended**: `base` for most users, `small` for better accuracy.

### Parameters

- `--model`: Whisper model size (tiny/base/small/medium/large)
- `--words-per-phrase`: How many words per line (default: 4)
- `--max-duration`: Max seconds per phrase (default: 3.0)

### Example Output

Input audio: "Welcome to the show, dancing in the lights"

Generated `lyrics.txt`:
```
0:00-0:02 Welcome|to|the|show
0:02-0:04 dancing|in|the|lights
```

### Pros & Cons

✅ **Pros:**
- No lyrics text needed (transcribes automatically)
- Very accurate timing
- Handles any language
- Works offline after setup

❌ **Cons:**
- Requires GPU for large models (CPU works but slower)
- First run downloads model (~150MB+)
- May mishear words in noisy audio

---

## Method 2: Gentle Forced Aligner (Highest Accuracy)

### What It Does
- **Aligns** known lyrics to audio
- Extremely accurate word timing
- Fast processing
- Requires you to provide correct lyrics text

### Installation

**Option A: Docker (Recommended)**
```bash
docker run -p 8765:8765 lowerquality/gentle
```

**Option B: Manual Install**
See: https://github.com/lowerquality/gentle

Plus Python package:
```bash
pip install requests
```

### Usage

1. **Start Gentle server:**
```bash
docker run -p 8765:8765 lowerquality/gentle
```

2. **Create a plain text file with lyrics:**
```bash
# Create known_lyrics.txt
echo "Welcome to the show dancing in the lights" > known_lyrics.txt
```

3. **Run alignment:**
```bash
python auto_lyrics_gentle.py \
    --audio assets/song.wav \
    --lyrics known_lyrics.txt \
    --output assets/lyrics.txt
```

### Parameters

- `--gentle-url`: Gentle server URL (default: http://localhost:8765)
- `--words-per-phrase`: Words per line (default: 4)

### Pros & Cons

✅ **Pros:**
- **Most accurate** timing (when lyrics are correct)
- Very fast processing
- Professional-grade alignment
- Used in production by many studios

❌ **Cons:**
- Requires Docker or manual install
- Needs exact lyrics text beforehand
- Server must be running

---

## Method 3: Beat-Based Distribution (Quickest)

### What It Does
- **Distributes** known lyrics across detected beats
- Uses existing beat detection from Phase 1
- Simple and fast
- Less accurate than Whisper/Gentle

### Installation

No installation needed! Uses existing pipeline.

### Usage

1. **Run Phase 1 first** (to detect beats):
```bash
python main.py --phase 1
```

2. **Distribute lyrics across beats:**
```bash
python auto_lyrics_beats.py \
    --prep-data outputs/prep_data.json \
    --lyrics-text "Welcome to the show dancing in the lights" \
    --output assets/lyrics.txt
```

Or from file:
```bash
python auto_lyrics_beats.py \
    --prep-data outputs/prep_data.json \
    --lyrics-file known_lyrics.txt \
    --output assets/lyrics.txt \
    --words-per-beat 2
```

### Parameters

- `--words-per-beat`: How many words per beat (default: 2)
- `--lyrics-text`: Inline lyrics text
- `--lyrics-file`: Path to plain text lyrics file

### Pros & Cons

✅ **Pros:**
- **Fastest** method
- No additional dependencies
- Good for beat-synchronized songs
- Perfect for quick tests

❌ **Cons:**
- Less accurate than ASR methods
- Assumes lyrics follow beats evenly
- Requires manually writing lyrics first

---

## Complete Workflow Examples

### Workflow 1: Whisper (Fully Automated)

```bash
# Step 1: Auto-generate timed lyrics from audio
python auto_lyrics_whisper.py assets/song.wav --output assets/lyrics.txt

# Step 2: Run full pipeline
python main.py
```

That's it! Fully automated from audio to video.

### Workflow 2: Gentle (Highest Quality)

```bash
# Step 1: Start Gentle server
docker run -p 8765:8765 lowerquality/gentle

# Step 2: Create lyrics text file
cat > known_lyrics.txt << EOF
Welcome to the show
Dancing in the lights
Music brings us together
EOF

# Step 3: Align lyrics to audio
python auto_lyrics_gentle.py \
    --audio assets/song.wav \
    --lyrics known_lyrics.txt \
    --output assets/lyrics.txt

# Step 4: Run pipeline
python main.py
```

### Workflow 3: Beat-Based (Quick Test)

```bash
# Step 1: Detect beats
python main.py --phase 1

# Step 2: Distribute lyrics
python auto_lyrics_beats.py \
    --prep-data outputs/prep_data.json \
    --lyrics-text "Your song lyrics here" \
    --output assets/lyrics.txt

# Step 3: Run full pipeline
python main.py
```

---

## Comparison with Manual Timing

### Manual Method (Current)
```
# You write this by hand:
0:00-0:03 Welcome|to|the|show
0:03-0:06 Dancing|in|the|lights
```

**Time**: 5-10 minutes per 30-second song
**Accuracy**: Depends on your ear
**Effort**: High

### Automated Methods
```bash
# One command:
python auto_lyrics_whisper.py song.wav --output lyrics.txt
```

**Time**: 30-60 seconds
**Accuracy**: Very high
**Effort**: Minimal

---

## Troubleshooting

### Whisper Issues

**Problem**: "ModuleNotFoundError: No module named 'whisper'"
```bash
# Solution:
pip install openai-whisper
```

**Problem**: Slow transcription on CPU
```bash
# Solution: Use smaller model
python auto_lyrics_whisper.py song.wav --model tiny
```

**Problem**: Wrong words transcribed
```bash
# Solution:
# 1. Use larger model (--model small or medium)
# 2. Clean up audio (reduce background noise)
# 3. Fall back to Gentle with manual lyrics
```

### Gentle Issues

**Problem**: "Could not connect to Gentle server"
```bash
# Solution: Start the server first
docker run -p 8765:8765 lowerquality/gentle
```

**Problem**: Words not aligning
```bash
# Solution:
# 1. Check lyrics.txt spelling matches audio exactly
# 2. Use plain text (no special formatting)
# 3. Remove punctuation
```

### Beat-Based Issues

**Problem**: Lyrics timing feels off
```bash
# Solution:
# 1. Adjust --words-per-beat parameter
# 2. Use Whisper or Gentle for better accuracy
# 3. This method works best for beat-heavy music
```

---

## Integration with Pipeline

All three methods output the same format, so they work identically:

```bash
# Any of these creates lyrics.txt:
python auto_lyrics_whisper.py song.wav --output lyrics.txt
python auto_lyrics_gentle.py --audio song.wav --lyrics text.txt --output lyrics.txt
python auto_lyrics_beats.py --prep-data prep_data.json --lyrics-text "..." --output lyrics.txt

# Then use normally:
cp lyrics.txt assets/lyrics.txt
python main.py
```

---

## Recommendations by Use Case

### For Production Videos
→ **Use Gentle** (if you have lyrics) or **Whisper medium/small**

### For Quick Previews
→ **Use Beat-Based** or **Whisper tiny**

### For Unknown Songs
→ **Use Whisper** (only option that transcribes)

### For Multiple Languages
→ **Use Whisper** (supports 99 languages)

### For Perfect Accuracy
→ **Use Gentle** with manually verified lyrics

---

## Next Steps

1. **Choose your method** based on the comparison table
2. **Install dependencies** (if needed)
3. **Run the script** on your audio file
4. **Verify output** in generated `lyrics.txt`
5. **Run the pipeline** with `python main.py`

---

## Additional Resources

- **Whisper**: https://github.com/openai/whisper
- **Gentle**: https://github.com/lowerquality/gentle
- **Main README**: See pipeline documentation

---

**Created**: 2025-11-18
**Related**: POSITIONING_GUIDE.md, README.md
