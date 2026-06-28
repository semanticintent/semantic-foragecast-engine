#!/usr/bin/env python3
"""
Sprite Compositor — Phase 2 of the animation pipeline.

Takes the mascot PNG, a set of mouth sprites (one per Rhubarb phoneme),
and the prep_data.json from Phase 1, then renders a frame sequence where:
  - The correct mouth sprite is composited over the mascot at each frame
  - The mascot body bobs vertically on detected beats
  - A simple background and optional vignette are applied
"""

import os
import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger(__name__)

# Rhubarb phoneme set — 9 mouth shapes
PHONEMES = ["X", "A", "B", "C", "D", "E", "F", "G", "H"]

# Phoneme fallback chain: if a sprite is missing, use the nearest shape
PHONEME_FALLBACK = {
    "A": "C", "B": "X", "C": "A", "D": "C",
    "E": "C", "F": "D", "G": "C", "H": "A", "X": "X",
}


class SpriteCompositor:
    """
    Composes mascot animation frames from a character image + mouth sprites
    driven by phoneme and beat timing data from Phase 1.
    """

    def __init__(self, config: Dict, prep_data: Dict):
        self.config = config
        self.prep_data = prep_data
        self.fps = config.get("animation", {}).get("fps", 24)

        char_cfg = config.get("character", {})
        self.mouth_region = char_cfg.get("mouth_region", {"x": 0, "y": 0, "w": 80, "h": 50})
        self.sprites_dir = char_cfg.get("sprites_dir", "sprites")

        anim_cfg = config.get("animation", {})
        self.bob_px = anim_cfg.get("body_bob_px", 8)
        self.bob_on_beats = anim_cfg.get("body_bob_beats", True)
        bg = anim_cfg.get("background_color", [20, 15, 30])
        self.bg_color = tuple(int(c) for c in bg)

        res = config.get("video", {}).get("resolution", [1280, 720])
        self.width, self.height = int(res[0]), int(res[1])

        self.base_image: Optional[Image.Image] = None
        self.mouth_sprites: Dict[str, Image.Image] = {}
        self._beat_times: List[float] = []
        self._lyric_font: Optional[ImageFont.FreeTypeFont] = None

        self._load_assets()
        self._index_beats()
        self._load_font()

    # ------------------------------------------------------------------ #
    # Asset loading
    # ------------------------------------------------------------------ #

    def _load_assets(self):
        """Load base mascot image and all available mouth sprites."""
        inputs = self.config.get("inputs", {})
        mascot_path = inputs.get("mascot_image")
        if not mascot_path or not os.path.exists(mascot_path):
            raise FileNotFoundError(f"Mascot image not found: {mascot_path}")

        self.base_image = Image.open(mascot_path).convert("RGBA")
        logger.info("Loaded mascot: %s (%dx%d)", mascot_path, *self.base_image.size)

        loaded, missing = [], []
        for phoneme in PHONEMES:
            sprite_path = os.path.join(self.sprites_dir, f"mouth_{phoneme}.png")
            if os.path.exists(sprite_path):
                sprite = Image.open(sprite_path).convert("RGBA")
                # Resize to match mouth_region dimensions
                target = (self.mouth_region["w"], self.mouth_region["h"])
                if sprite.size != target:
                    sprite = sprite.resize(target, Image.LANCZOS)
                self.mouth_sprites[phoneme] = sprite
                loaded.append(phoneme)
            else:
                missing.append(phoneme)

        if missing:
            logger.warning("Missing mouth sprites: %s — using fallbacks", missing)
        logger.info("Loaded mouth sprites: %s", loaded)

        if not self.mouth_sprites:
            raise FileNotFoundError(
                f"No mouth sprites found in {self.sprites_dir}. "
                "Run generate_sprites.py first."
            )

    def _index_beats(self):
        """Cache beat times from prep data for fast lookup."""
        beats = self.prep_data.get("beats", {})
        self._beat_times = [float(t) for t in beats.get("beat_times", [])]

    def _load_font(self):
        """Load the best available system font for lyric rendering."""
        candidates = [
            "/System/Library/Fonts/SFNSRounded.ttf",
            "/System/Library/Fonts/SFNS.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        font_size = max(int(self.height * 0.055), 24)
        for path in candidates:
            if os.path.exists(path):
                try:
                    self._lyric_font = ImageFont.truetype(path, font_size)
                    logger.info("Lyric font: %s @ %dpx", path, font_size)
                    return
                except Exception:
                    continue
        self._lyric_font = ImageFont.load_default()
        logger.warning("No system font found — using PIL default for lyrics")

    # ------------------------------------------------------------------ #
    # Per-frame logic
    # ------------------------------------------------------------------ #

    def _get_phoneme_at(self, timestamp: float) -> str:
        """Return the active Rhubarb phoneme at the given timestamp."""
        phonemes = self.prep_data.get("phonemes", [])
        active = "X"
        for entry in phonemes:
            if float(entry["time"]) <= timestamp:
                active = entry["phoneme"]
            else:
                break
        return active

    def _get_mouth_sprite(self, phoneme: str) -> Optional[Image.Image]:
        """Return the sprite for a phoneme, following the fallback chain."""
        if phoneme in self.mouth_sprites:
            return self.mouth_sprites[phoneme]
        fallback = PHONEME_FALLBACK.get(phoneme, "X")
        if fallback in self.mouth_sprites:
            return self.mouth_sprites[fallback]
        # Last resort: any available sprite
        return next(iter(self.mouth_sprites.values()), None)

    def _get_bob_offset(self, timestamp: float) -> int:
        """
        Return vertical bob offset (pixels) at this timestamp.
        Smooth sine wave centred on the nearest beat.
        """
        if not self.bob_on_beats or not self._beat_times:
            return 0

        # Find the nearest beat
        nearest = min(self._beat_times, key=lambda t: abs(t - timestamp))
        delta = timestamp - nearest
        beat_window = 0.25  # seconds either side of beat

        if abs(delta) < beat_window:
            phase = (delta / beat_window) * math.pi
            offset = int(self.bob_px * math.cos(phase))
        else:
            offset = 0
        return offset

    def _get_word_at(self, timestamp: float) -> Optional[str]:
        """Return the active lyric word at the given timestamp, or None."""
        words = self.prep_data.get("timed_words", [])
        if not words:
            return None
        active = None
        for entry in words:
            t = float(entry.get("time", entry.get("start", 0)))
            if t <= timestamp:
                active = entry.get("word", entry.get("text", ""))
            else:
                break
        return active or None

    def _render_lyric_overlay(self, frame: Image.Image, word: str):
        """Draw the current lyric word centred near the bottom of the frame."""
        if not word:
            return
        d = ImageDraw.Draw(frame)
        font = self._lyric_font

        # Measure text
        bbox = d.textbbox((0, 0), word.upper(), font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pad_x, pad_y = int(tw * 0.18), int(th * 0.30)
        x = (self.width - tw) // 2
        y = int(self.height * 0.82)

        # Pill background
        pill = [x - pad_x, y - pad_y, x + tw + pad_x, y + th + pad_y]
        d.rounded_rectangle(pill, radius=int(th * 0.4), fill=(0, 0, 0, 160))

        # White text with subtle shadow
        d.text((x + 2, y + 2), word.upper(), font=font, fill=(0, 0, 0, 120))
        d.text((x, y), word.upper(), font=font, fill=(255, 255, 255, 240))

    def _render_frame(self, timestamp: float) -> Image.Image:
        """Render a single composited frame at the given timestamp."""
        # 1. Background
        frame = Image.new("RGBA", (self.width, self.height), (*self.bg_color, 255))

        # 2. Position mascot centred with bob offset
        bob = self._get_bob_offset(timestamp)
        mascot_w, mascot_h = self.base_image.size
        mascot_x = (self.width - mascot_w) // 2
        mascot_y = (self.height - mascot_h) // 2 + bob

        # 3. Composite mascot onto background
        frame.paste(self.base_image, (mascot_x, mascot_y), self.base_image)

        # 4. Composite mouth sprite at the configured mouth_region (feathered edges)
        phoneme = self._get_phoneme_at(timestamp)
        mouth_sprite = self._get_mouth_sprite(phoneme)
        if mouth_sprite:
            mx = mascot_x + self.mouth_region["x"]
            my = mascot_y + self.mouth_region["y"] + bob
            # Build an elliptical feather mask so the sprite blends into the face
            fw, fh = mouth_sprite.size
            feather_mask = Image.new("L", (fw, fh), 0)
            inset_x = max(fw // 8, 4)
            inset_y = max(fh // 8, 4)
            ImageDraw.Draw(feather_mask).ellipse(
                [inset_x, inset_y, fw - inset_x, fh - inset_y], fill=255
            )
            feather_mask = feather_mask.filter(
                ImageFilter.GaussianBlur(radius=max(min(inset_x, inset_y), 4))
            )
            frame.paste(mouth_sprite, (mx, my), feather_mask)

        rgb = frame.convert("RGB")

        # 5. Lyric word overlay
        word = self._get_word_at(timestamp)
        if word:
            self._render_lyric_overlay(rgb, word)

        return rgb

    # ------------------------------------------------------------------ #
    # Sequence rendering
    # ------------------------------------------------------------------ #

    def render_sequence(self, output_dir: str) -> int:
        """
        Render all frames to output_dir/frame_NNNN.png.
        Returns the number of frames rendered.
        """
        os.makedirs(output_dir, exist_ok=True)

        audio = self.prep_data.get("audio", {})
        duration = float(audio.get("duration", 0))
        if duration <= 0:
            raise ValueError("Audio duration is 0 — check prep_data.json")

        total_frames = int(math.ceil(duration * self.fps))
        logger.info(
            "Rendering %d frames at %d fps (%.2fs) to %s",
            total_frames, self.fps, duration, output_dir
        )

        for frame_idx in range(total_frames):
            timestamp = frame_idx / self.fps
            frame = self._render_frame(timestamp)
            out_path = os.path.join(output_dir, f"frame_{frame_idx + 1:04d}.png")
            frame.save(out_path, "PNG", optimize=False)

            if (frame_idx + 1) % 24 == 0 or frame_idx == 0:
                progress = (frame_idx + 1) / total_frames * 100
                logger.info("  %.1f%% (%d/%d)", progress, frame_idx + 1, total_frames)

        logger.info("Rendered %d frames", total_frames)
        return total_frames


# ------------------------------------------------------------------ #
# CLI helper for standalone testing
# ------------------------------------------------------------------ #

def _load_json(path: str) -> Dict:
    import json
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    import argparse, json, yaml

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Run Phase 2 sprite compositor standalone")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--prep-data", default="outputs/prep_data.json")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)
    prep_data = _load_json(args.prep_data)

    compositor = SpriteCompositor(config, prep_data)
    frames_dir = config.get("output", {}).get("frames_dir", "outputs/frames")
    count = compositor.render_sequence(frames_dir)
    logger.info("Done — %d frames in %s", count, frames_dir)
