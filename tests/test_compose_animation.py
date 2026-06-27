#!/usr/bin/env python3
"""Tests for compose_animation.py (Phase 2 sprite compositor)."""

import os
import sys
import json
import shutil
import tempfile
import unittest
import logging
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np

logger = logging.getLogger(__name__)


def _make_test_prep_data(duration: float = 3.0) -> dict:
    """Minimal valid prep_data for compositor tests."""
    fps = 24
    beat_times = [i * 0.5 for i in range(int(duration / 0.5))]
    phoneme_cycle = ["X", "A", "B", "C", "D", "E", "F", "G", "H"]
    phonemes = [
        {"time": i * (duration / 30), "phoneme": phoneme_cycle[i % len(phoneme_cycle)]}
        for i in range(30)
    ]
    return {
        "audio": {"duration": duration, "tempo": 120.0, "sample_rate": 22050},
        "beats": {"beat_times": beat_times, "onset_times": beat_times},
        "phonemes": phonemes,
        "timed_words": [],
    }


def _make_mascot_image(path: str, size: tuple = (256, 256)):
    """Create a simple RGBA mascot PNG for testing."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", size, (255, 140, 0, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    # Simple face: eyes + mouth
    draw.ellipse([cx - 30, cy - 20, cx - 10, cy], fill=(0, 0, 0, 255))
    draw.ellipse([cx + 10, cy - 20, cx + 30, cy], fill=(0, 0, 0, 255))
    draw.arc([cx - 25, cy + 10, cx + 25, cy + 40], 0, 180, fill=(0, 0, 0, 255), width=3)
    img.save(path, "PNG")


def _make_mouth_sprites(sprites_dir: str, w: int = 80, h: int = 40):
    """Create minimal mouth sprites for testing."""
    from PIL import Image
    os.makedirs(sprites_dir, exist_ok=True)
    for phoneme in ["X", "A", "B", "C", "D", "E", "F", "G", "H"]:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        img.save(os.path.join(sprites_dir, f"mouth_{phoneme}.png"))


def _make_config(test_dir: str, mascot_path: str, sprites_dir: str) -> dict:
    return {
        "inputs": {"mascot_image": mascot_path, "song_file": "", "lyrics_file": None},
        "character": {
            "sprites_dir": sprites_dir,
            "mouth_region": {"x": 90, "y": 130, "w": 80, "h": 40},
        },
        "animation": {
            "fps": 24,
            "body_bob_px": 6,
            "body_bob_beats": True,
            "background_color": [20, 15, 30],
        },
        "output": {
            "frames_dir": os.path.join(test_dir, "frames"),
            "prep_json": os.path.join(test_dir, "prep_data.json"),
        },
        "video": {"fps": 24, "resolution": [320, 240], "codec": "libx264", "quality": "fast"},
    }


class TestSpriteCompositorInit(unittest.TestCase):
    """Test SpriteCompositor initialisation."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="comp_test_")
        self.mascot_path = os.path.join(self.test_dir, "mascot.png")
        self.sprites_dir = os.path.join(self.test_dir, "sprites")
        _make_mascot_image(self.mascot_path)
        _make_mouth_sprites(self.sprites_dir)
        self.prep_data = _make_test_prep_data(3.0)
        self.config = _make_config(self.test_dir, self.mascot_path, self.sprites_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_loads_mascot(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        self.assertIsNotNone(c.base_image)
        self.assertEqual(c.base_image.size, (256, 256))

    def test_loads_all_nine_sprites(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        self.assertEqual(len(c.mouth_sprites), 9)

    def test_missing_mascot_raises(self):
        from compose_animation import SpriteCompositor
        cfg = dict(self.config)
        cfg["inputs"] = {"mascot_image": "/nonexistent/mascot.png"}
        with self.assertRaises(FileNotFoundError):
            SpriteCompositor(cfg, self.prep_data)

    def test_missing_sprites_dir_raises(self):
        from compose_animation import SpriteCompositor
        cfg = dict(self.config)
        cfg["character"] = dict(self.config["character"])
        cfg["character"]["sprites_dir"] = "/nonexistent/sprites"
        with self.assertRaises(FileNotFoundError):
            SpriteCompositor(cfg, self.prep_data)


class TestSpriteCompositorFrameLogic(unittest.TestCase):
    """Test per-frame rendering logic."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="comp_test_")
        self.mascot_path = os.path.join(self.test_dir, "mascot.png")
        self.sprites_dir = os.path.join(self.test_dir, "sprites")
        _make_mascot_image(self.mascot_path)
        _make_mouth_sprites(self.sprites_dir)
        self.prep_data = _make_test_prep_data(3.0)
        self.config = _make_config(self.test_dir, self.mascot_path, self.sprites_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_render_single_frame(self):
        from compose_animation import SpriteCompositor
        from PIL import Image
        c = SpriteCompositor(self.config, self.prep_data)
        frame = c._render_frame(0.0)
        self.assertIsInstance(frame, Image.Image)
        self.assertEqual(frame.size, (320, 240))
        self.assertEqual(frame.mode, "RGB")

    def test_phoneme_at_start_is_x(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        phoneme = c._get_phoneme_at(0.0)
        self.assertIn(phoneme, ["X", "A", "B", "C", "D", "E", "F", "G", "H"])

    def test_bob_offset_near_beat(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        # At a beat time, offset should be near max
        beat_time = self.prep_data["beats"]["beat_times"][0]
        offset = c._get_bob_offset(beat_time)
        self.assertGreater(abs(offset), 0)

    def test_bob_offset_far_from_beat(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        # Between beats offset should be 0
        beat_times = self.prep_data["beats"]["beat_times"]
        midpoint = (beat_times[0] + beat_times[1]) / 2 if len(beat_times) > 1 else 0.25
        offset = c._get_bob_offset(midpoint)
        self.assertEqual(offset, 0)

    def test_frame_background_colour(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        frame = c._render_frame(0.0)
        # Top-left pixel should be close to the background colour
        corner = frame.getpixel((0, 0))
        bg = tuple(self.config["animation"]["background_color"])
        for i in range(3):
            self.assertAlmostEqual(corner[i], bg[i], delta=10)


class TestSpriteCompositorSequence(unittest.TestCase):
    """Test full sequence rendering."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="comp_test_")
        self.mascot_path = os.path.join(self.test_dir, "mascot.png")
        self.sprites_dir = os.path.join(self.test_dir, "sprites")
        self.frames_dir = os.path.join(self.test_dir, "frames")
        _make_mascot_image(self.mascot_path)
        _make_mouth_sprites(self.sprites_dir)
        self.prep_data = _make_test_prep_data(1.0)
        self.config = _make_config(self.test_dir, self.mascot_path, self.sprites_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_renders_correct_frame_count(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        count = c.render_sequence(self.frames_dir)
        expected = int(1.0 * 24)  # 1 second at 24fps
        self.assertEqual(count, expected)

    def test_frame_files_exist(self):
        from compose_animation import SpriteCompositor
        c = SpriteCompositor(self.config, self.prep_data)
        count = c.render_sequence(self.frames_dir)
        files = sorted(os.listdir(self.frames_dir))
        self.assertEqual(len(files), count)
        self.assertTrue(files[0].startswith("frame_"))
        self.assertTrue(files[0].endswith(".png"))

    def test_zero_duration_raises(self):
        from compose_animation import SpriteCompositor
        bad_prep = dict(self.prep_data)
        bad_prep["audio"] = {"duration": 0, "tempo": 120.0}
        c = SpriteCompositor(self.config, bad_prep)
        with self.assertRaises(ValueError):
            c.render_sequence(self.frames_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main(verbosity=2)
