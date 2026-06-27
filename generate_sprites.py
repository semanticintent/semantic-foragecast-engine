#!/usr/bin/env python3
"""
Mouth sprite generator — creates a starter set of 9 mouth sprites
(one per Rhubarb phoneme) from a mascot image.

V1: Geometric shapes drawn in the skin/fur tone of the mascot's mouth region.
    Fast, zero external dependencies beyond Pillow.

V2 (future): AI inpainting via local Flux/SDXL to generate photo-realistic or
    style-matched mouth shapes.

Usage:
    # Generate sprites from the demo fox:
    python generate_sprites.py --image examples/demo_fox.png --out sprites/

    # Override mouth region (x y w h):
    python generate_sprites.py --image mascot.png --out sprites/ --region 200 280 112 70

    # Sample the skin tone from a specific point instead of the region centre:
    python generate_sprites.py --image mascot.png --out sprites/ --sample-point 256 310
"""

import os
import argparse
import logging
from typing import Tuple, Optional

import numpy as np
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 9 Rhubarb phoneme mouth shapes, described as (openness_ratio, width_ratio, shape)
# openness_ratio: vertical opening as fraction of sprite height (0 = closed, 1 = fully open)
# width_ratio: horizontal width as fraction of sprite width
# shape: 'oval' | 'pressed' | 'narrow' | 'wide' | 'round' | 'lip'
PHONEME_SHAPES = {
    "X": {"openness": 0.00, "width": 0.85, "shape": "pressed"},   # silence / rest
    "A": {"openness": 0.65, "width": 0.80, "shape": "oval"},      # "father"
    "B": {"openness": 0.02, "width": 0.88, "shape": "pressed"},   # "bad" / M / P
    "C": {"openness": 0.40, "width": 0.75, "shape": "oval"},      # "cut"
    "D": {"openness": 0.25, "width": 0.72, "shape": "oval"},      # "dead"
    "E": {"openness": 0.30, "width": 0.95, "shape": "wide"},      # "bed" — teeth showing
    "F": {"openness": 0.15, "width": 0.70, "shape": "lip"},       # "fat" — bottom lip up
    "G": {"openness": 0.45, "width": 0.60, "shape": "narrow"},    # "good"
    "H": {"openness": 0.55, "width": 0.68, "shape": "round"},     # "hot"
}


def _sample_skin_tone(
    image: Image.Image,
    region: Tuple[int, int, int, int],
    sample_point: Optional[Tuple[int, int]] = None,
) -> Tuple[int, int, int, int]:
    """Sample the dominant colour from the mascot's mouth region."""
    if sample_point:
        px, py = sample_point
        px = max(0, min(px, image.width - 1))
        py = max(0, min(py, image.height - 1))
        rgba = image.convert("RGBA").getpixel((px, py))
        return rgba[:4]

    x, y, w, h = region
    crop = image.convert("RGBA").crop((x, y, x + w, y + h))
    # Average the centre 40% of the region to avoid edge noise
    cx, cy = crop.width // 2, crop.height // 2
    inner = crop.crop((
        cx - crop.width // 5, cy - crop.height // 5,
        cx + crop.width // 5, cy + crop.height // 5,
    ))
    arr = np.array(inner)  # shape (H, W, 4)
    r = int(arr[:, :, 0].mean())
    g = int(arr[:, :, 1].mean())
    b = int(arr[:, :, 2].mean())
    return (r, g, b, 255)


def _make_sprite(
    phoneme: str,
    width: int,
    height: int,
    skin_tone: Tuple[int, int, int, int],
    outline_color: Tuple[int, int, int, int] = (30, 15, 10, 255),
    interior_color: Tuple[int, int, int, int] = (20, 10, 10, 230),
) -> Image.Image:
    """
    Draw a single mouth sprite for the given phoneme.
    Returns an RGBA image with a transparent background.
    """
    sprite = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    shape_cfg = PHONEME_SHAPES[phoneme]
    openness = shape_cfg["openness"]
    w_ratio = shape_cfg["width"]
    shape = shape_cfg["shape"]

    cx, cy = width // 2, height // 2
    ow = int(width * w_ratio)  # mouth opening width
    oh = int(height * openness) if openness > 0 else 2  # mouth opening height

    # Outer lip boundary (always present)
    lip_w = int(width * min(w_ratio + 0.08, 1.0))
    lip_h = max(int(height * 0.20), 6)
    lip_left = cx - lip_w // 2
    lip_right = cx + lip_w // 2
    lip_top = cy - lip_h // 2
    lip_bot = cy + lip_h // 2

    if shape == "pressed" or openness < 0.05:
        # Closed / pressed lips — just the lip line
        draw.ellipse(
            [lip_left, lip_top, lip_right, lip_bot],
            fill=skin_tone,
            outline=outline_color,
            width=2,
        )
        # Mouth line
        draw.line(
            [(lip_left + 4, cy), (lip_right - 4, cy)],
            fill=outline_color,
            width=2,
        )

    else:
        left = cx - ow // 2
        right = cx + ow // 2
        top = cy - oh // 2
        bot = cy + oh // 2

        if shape == "wide":
            # Wide open with flat top (E sound, teeth showing)
            draw.ellipse([left, top, right, bot], fill=interior_color, outline=outline_color, width=2)
            # Suggest teeth with a light stripe near top
            teeth_y = top + max(oh // 6, 2)
            draw.rectangle([left + 2, top + 1, right - 2, teeth_y],
                           fill=(220, 215, 210, 200))
        elif shape == "round":
            # Rounder, more circular (H/O sound)
            r = min(ow, oh) // 2
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=interior_color, outline=outline_color, width=2)
        elif shape == "narrow":
            # Narrow vertical oval (G sound)
            draw.ellipse([left + ow // 4, top, right - ow // 4, bot],
                         fill=interior_color, outline=outline_color, width=2)
        elif shape == "lip":
            # Bottom lip slightly raised (F/V sound)
            draw.ellipse([left, top + oh // 4, right, bot],
                         fill=interior_color, outline=outline_color, width=2)
        else:
            # Default oval (A, C, D, H)
            draw.ellipse([left, top, right, bot],
                         fill=interior_color, outline=outline_color, width=2)

        # Lip surround
        draw.ellipse([lip_left, lip_top, lip_right, lip_bot],
                     fill=None, outline=skin_tone, width=3)
        lower_top = min(top + oh, lip_bot)
        lower_bot = max(lip_bot + max(oh // 3, 3), lower_top + 2)
        draw.ellipse([lip_left, lower_top, lip_right, lower_bot],
                     fill=None, outline=skin_tone, width=2)

    return sprite


def generate_sprites(
    image_path: str,
    out_dir: str,
    region: Tuple[int, int, int, int],
    sample_point: Optional[Tuple[int, int]] = None,
) -> int:
    """
    Generate all 9 mouth sprites and save them to out_dir.
    Returns the number of sprites written.
    """
    os.makedirs(out_dir, exist_ok=True)

    image = Image.open(image_path)
    skin_tone = _sample_skin_tone(image, region, sample_point)
    logger.info(
        "Sampled skin tone from %s: RGBA%s",
        image_path, skin_tone
    )

    x, y, w, h = region
    count = 0
    for phoneme in PHONEME_SHAPES:
        sprite = _make_sprite(phoneme, w, h, skin_tone)
        out_path = os.path.join(out_dir, f"mouth_{phoneme}.png")
        sprite.save(out_path, "PNG")
        logger.info("  Wrote: %s", out_path)
        count += 1

    logger.info("Generated %d sprites in %s", count, out_dir)
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Generate geometric mouth sprites for the Semantic Foragecast Engine"
    )
    parser.add_argument("--image", required=True, help="Path to mascot PNG")
    parser.add_argument("--out", default="sprites/", help="Output directory for sprites")
    parser.add_argument(
        "--region", nargs=4, type=int, metavar=("X", "Y", "W", "H"),
        default=[200, 280, 112, 70],
        help="Mouth region on the mascot image (x y w h). Default: 200 280 112 70"
    )
    parser.add_argument(
        "--sample-point", nargs=2, type=int, metavar=("X", "Y"),
        help="Specific pixel to sample skin tone from (overrides region centre)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.image):
        logger.error("Image not found: %s", args.image)
        return 1

    region = tuple(args.region)
    sample = tuple(args.sample_point) if args.sample_point else None

    count = generate_sprites(args.image, args.out, region, sample)
    logger.info("Done — %d sprites ready in %s", count, args.out)
    logger.info("Next: update 'character.mouth_region' in config.yaml to match x=%d y=%d w=%d h=%d",
                *region)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
