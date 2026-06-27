#!/usr/bin/env python3
"""
Create test frames for Phase 3 testing.

Generates simple colored frames for testing video export.

"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_test_frames(output_dir='outputs/frames', count=60, width=640, height=480):
    """
    Create test frames for video export testing.

    Args:
        output_dir: Directory to save frames
        count: Number of frames to generate
        width: Frame width in pixels
        height: Frame height in pixels
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Creating {count} test frames in {output_dir}...")

    for i in range(count):
        # Create gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Color gradient based on frame number
        hue = (i * 360 // count) % 360

        # Simple color transition
        r = int(128 + 127 * (i / count))
        g = int(128 + 127 * ((count - i) / count))
        b = int(128 + 64 * abs(count/2 - i) / (count/2))

        # Fill with color
        draw.rectangle([(0, 0), (width, height)], fill=(r, g, b))

        # Add frame number
        text = f"Frame {i:04d}"
        try:
            # Try to use a larger font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            # Fallback to default font
            font = None

        # Calculate text position
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = 100, 20

        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Draw text with outline
        outline_color = (0, 0, 0)
        fill_color = (255, 255, 255)

        for offset_x, offset_y in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            draw.text((text_x + offset_x, text_y + offset_y), text, font=font, fill=outline_color)

        draw.text((text_x, text_y), text, font=font, fill=fill_color)

        # Add border
        draw.rectangle([(0, 0), (width-1, height-1)], outline=(255, 255, 255), width=2)

        # Save frame
        frame_path = os.path.join(output_dir, f'frame_{i:04d}.png')
        img.save(frame_path)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/{count} frames...")

    print(f"✓ Created {count} frames successfully")
    print(f"  Output: {output_dir}")
    print(f"  Resolution: {width}x{height}")
    print(f"  Total size: ~{count * 50 // 1024} MB (estimated)")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create test frames for Phase 3')
    parser.add_argument('--output', default='outputs/frames', help='Output directory')
    parser.add_argument('--count', type=int, default=60, help='Number of frames (default: 60 = ~2.5s @ 24fps)')
    parser.add_argument('--width', type=int, default=640, help='Frame width')
    parser.add_argument('--height', type=int, default=480, help='Frame height')

    args = parser.parse_args()

    create_test_frames(args.output, args.count, args.width, args.height)
