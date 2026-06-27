#!/usr/bin/env python3
"""Tests for generate_sprites.py (V1 geometric mouth sprite generator)."""

import os
import sys
import shutil
import tempfile
import unittest
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)

PHONEMES = ["X", "A", "B", "C", "D", "E", "F", "G", "H"]


def _make_test_mascot(path: str, size: tuple = (512, 512)):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", size, (255, 140, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([150, 150, 362, 362], fill=(255, 180, 80, 255))
    img.save(path, "PNG")


class TestGenerateSprites(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sprites_test_")
        self.mascot_path = os.path.join(self.test_dir, "mascot.png")
        self.sprites_dir = os.path.join(self.test_dir, "sprites")
        _make_test_mascot(self.mascot_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generates_nine_sprites(self):
        from generate_sprites import generate_sprites
        region = (150, 280, 112, 60)
        count = generate_sprites(self.mascot_path, self.sprites_dir, region)
        self.assertEqual(count, 9)

    def test_all_phoneme_files_exist(self):
        from generate_sprites import generate_sprites
        region = (150, 280, 112, 60)
        generate_sprites(self.mascot_path, self.sprites_dir, region)
        for phoneme in PHONEMES:
            path = os.path.join(self.sprites_dir, f"mouth_{phoneme}.png")
            self.assertTrue(os.path.exists(path), f"Missing: mouth_{phoneme}.png")

    def test_sprites_are_correct_size(self):
        from generate_sprites import generate_sprites
        from PIL import Image
        region = (150, 280, 112, 60)
        generate_sprites(self.mascot_path, self.sprites_dir, region)
        for phoneme in PHONEMES:
            path = os.path.join(self.sprites_dir, f"mouth_{phoneme}.png")
            img = Image.open(path)
            self.assertEqual(img.size, (112, 60), f"mouth_{phoneme}.png wrong size")

    def test_sprites_are_rgba(self):
        from generate_sprites import generate_sprites
        from PIL import Image
        region = (150, 280, 112, 60)
        generate_sprites(self.mascot_path, self.sprites_dir, region)
        for phoneme in PHONEMES:
            path = os.path.join(self.sprites_dir, f"mouth_{phoneme}.png")
            img = Image.open(path)
            self.assertEqual(img.mode, "RGBA", f"mouth_{phoneme}.png not RGBA")

    def test_missing_image_raises(self):
        from generate_sprites import generate_sprites
        with self.assertRaises(Exception):
            generate_sprites("/nonexistent/mascot.png", self.sprites_dir, (0, 0, 80, 40))

    def test_sample_skin_tone_returns_rgba(self):
        from generate_sprites import _sample_skin_tone
        from PIL import Image
        img = Image.open(self.mascot_path)
        tone = _sample_skin_tone(img, (150, 150, 212, 212))
        self.assertEqual(len(tone), 4)
        for channel in tone:
            self.assertGreaterEqual(channel, 0)
            self.assertLessEqual(channel, 255)

    def test_make_sprite_all_phonemes(self):
        """All phoneme shapes render without error."""
        from generate_sprites import _make_sprite
        from PIL import Image
        skin = (255, 140, 0, 255)
        for phoneme in PHONEMES:
            sprite = _make_sprite(phoneme, 112, 60, skin)
            self.assertIsInstance(sprite, Image.Image)
            self.assertEqual(sprite.size, (112, 60))
            self.assertEqual(sprite.mode, "RGBA")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    unittest.main(verbosity=2)
