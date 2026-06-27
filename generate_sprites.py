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

# 9 Rhubarb phoneme mouth shapes
# openness: vertical opening as fraction of sprite height (0=closed, 1=fully open)
# width:    horizontal opening as fraction of sprite width
# shape:    controls cavity geometry
# teeth:    show upper teeth strip
# tongue:   show tongue at cavity bottom
PHONEME_SHAPES = {
    "X": {"openness": 0.00, "width": 0.82, "shape": "closed",  "teeth": False, "tongue": False},
    "A": {"openness": 0.62, "width": 0.78, "shape": "oval",    "teeth": True,  "tongue": True},
    "B": {"openness": 0.00, "width": 0.85, "shape": "pressed", "teeth": False, "tongue": False},
    "C": {"openness": 0.36, "width": 0.72, "shape": "oval",    "teeth": True,  "tongue": False},
    "D": {"openness": 0.20, "width": 0.68, "shape": "oval",    "teeth": False, "tongue": False},
    "E": {"openness": 0.26, "width": 0.92, "shape": "wide",    "teeth": True,  "tongue": False},
    "F": {"openness": 0.14, "width": 0.64, "shape": "lip",     "teeth": True,  "tongue": False},
    "G": {"openness": 0.42, "width": 0.54, "shape": "narrow",  "teeth": False, "tongue": False},
    "H": {"openness": 0.48, "width": 0.62, "shape": "round",   "teeth": False, "tongue": True},
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
) -> Image.Image:
    """
    Draw a layered cartoon mouth sprite for the given phoneme.
    Layers (bottom→top): lip fill → cavity → teeth → tongue → lip outline.
    Returns an RGBA image with a transparent background.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cfg = PHONEME_SHAPES[phoneme]
    openness   = cfg["openness"]
    w_ratio    = cfg["width"]
    shape      = cfg["shape"]
    show_teeth = cfg["teeth"]
    show_tongue= cfg["tongue"]

    cx, cy = width // 2, height // 2

    # Colour palette derived from mascot skin tone
    r0, g0, b0 = skin_tone[0], skin_tone[1], skin_tone[2]
    lip_fill   = (r0, g0, b0, 255)
    lip_shadow = (max(0, r0 - 60), max(0, g0 - 60), max(0, b0 - 60), 255)
    cavity_col = (18, 6, 4, 250)
    teeth_col  = (245, 240, 228, 240)
    tongue_col = (210, 82, 78, 230)

    # ── Outer lip ellipse ───────────────────────────────────────────────
    lw = int(width  * min(w_ratio + 0.14, 0.96))
    lh = int(height * 0.62)
    ll = cx - lw // 2
    lr = cx + lw // 2
    lt = cy - lh // 2
    lb = cy + lh // 2

    # 1. Filled skin-tone lip
    d.ellipse([ll, lt, lr, lb], fill=lip_fill)

    is_closed = openness < 0.04

    if not is_closed:
        ow = int(width  * w_ratio)
        oh = int(height * openness)

        # Cavity centre sits slightly below sprite centre (lower lip is fuller)
        kcy = cy + max(int(lh * 0.07), 2)

        # Size cavity geometry per phoneme shape
        if shape == "wide":
            cw = int(ow * 0.88); ch = int(oh * 0.78)
        elif shape == "round":
            sz = int(min(ow, oh * 1.3) * 0.50)
            cw = sz * 2; ch = int(sz * 1.5)
        elif shape == "narrow":
            cw = int(ow * 0.52); ch = oh
        elif shape == "lip":
            cw = int(ow * 0.65); ch = int(oh * 0.62)
            kcy = cy - max(int(oh * 0.10), 1)
        else:  # oval (A, C, D)
            cw = int(ow * 0.82); ch = oh

        # Clamp cavity strictly inside lip bounds
        cl = max(cx - cw // 2, ll + 3)
        cr = min(cx + cw // 2, lr - 3)
        ct = max(kcy - ch // 2, lt + 3)
        cb = min(kcy + ch // 2, lb - 3)
        if cr - cl < 4: cr = cl + 4
        if cb - ct < 4: cb = ct + 4

        ch_actual = cb - ct
        cw_actual = cr - cl

        # 2. Dark mouth cavity
        d.ellipse([cl, ct, cr, cb], fill=cavity_col)

        # 3. Upper teeth — cream ellipse covering top of cavity
        if show_teeth and ch_actual > 10:
            th = max(ch_actual // 4, 5)
            d.ellipse([cl + 2, ct, cr - 2, ct + th * 2], fill=teeth_col)

        # 4. Tongue — pink rounded shape at cavity bottom
        if show_tongue and ch_actual > 16:
            tw = int(cw_actual * 0.64)
            ts = max(ch_actual // 3, 7)
            td_top = max(cb - ts, ct + ch_actual // 2)
            td_bot = min(cb, lb - 2)
            if td_bot > td_top + 3:
                d.ellipse(
                    [cx - tw // 2, td_top, cx + tw // 2, td_bot],
                    fill=tongue_col,
                )

    # 5. Re-draw lip outline on top of all layers
    d.ellipse([ll, lt, lr, lb], fill=None, outline=lip_shadow, width=3)

    # 6. Centre mouth crease (always visible)
    crease_y = cy + 1
    d.line([(ll + 10, crease_y), (lr - 10, crease_y)], fill=lip_shadow, width=2)

    return img


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
        default=[376, 615, 272, 110],
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
