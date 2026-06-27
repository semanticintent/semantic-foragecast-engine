#!/usr/bin/env python3
"""
Video Export Module - FFmpeg Integration
Phase 3: Rendering and Export

This module handles video encoding using FFmpeg:
1. Encode rendered frames to video
2. Composite audio track
3. Generate final MP4 output
4. Support multiple codecs and quality settings

"""

import os
import sys
import subprocess
import glob
import logging
from pathlib import Path
from typing import Optional, List, Dict
import shutil

logger = logging.getLogger(__name__)


class VideoExporter:
    """Handles video export using FFmpeg."""

    def __init__(self, config: Dict):
        """
        Initialize video exporter.

        Args:
            config: Pipeline configuration dictionary
        """
        self.config = config
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self) -> Optional[str]:
        """
        Locate FFmpeg executable.

        Returns:
            Path to FFmpeg or None if not found
        """
        # Check common paths on Windows
        if sys.platform == 'win32':
            common_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return os.path.normpath(path)

        # Check PATH
        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return os.path.normpath(ffmpeg)

        return None

    def validate_frames(self, frames_dir: str) -> tuple[bool, int]:
        """
        Validate that rendered frames exist.

        Args:
            frames_dir: Directory containing rendered frames

        Returns:
            Tuple of (frames_exist, frame_count)
        """
        if not os.path.exists(frames_dir):
            return False, 0

        # Look for common frame patterns (use a set to avoid double-counting)
        patterns = ['frame_*.png', '*.png', 'frame_*.jpg', '*.jpg']
        frames = set()

        for pattern in patterns:
            frames.update(glob.glob(os.path.join(frames_dir, pattern)))

        count = len(frames)
        return count > 0, count

    def encode_video(
        self,
        frames_dir: str,
        audio_path: str,
        output_path: str,
        fps: int = 24,
        codec: str = 'libx264',
        quality: str = 'high',
        overwrite: bool = True
    ) -> bool:
        """
        Encode video from frames and audio.

        Args:
            frames_dir: Directory containing rendered frames
            audio_path: Path to audio file
            output_path: Output video path
            fps: Frames per second
            codec: Video codec ('libx264', 'libx265', 'vp9')
            quality: Quality preset ('low', 'medium', 'high', 'ultra')
            overwrite: Overwrite existing output file

        Returns:
            True if successful, False otherwise
        """
        if not self.ffmpeg_path:
            logger.error("FFmpeg not found. Install FFmpeg and add to PATH.")
            logger.error("Download from: https://ffmpeg.org/download.html")
            return False

        # Validate inputs
        frames_exist, frame_count = self.validate_frames(frames_dir)
        if not frames_exist:
            logger.error(f"No frames found in {frames_dir}")
            return False

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return False

        logger.info(f"Encoding video from {frame_count} frames...")
        logger.info(f"Codec: {codec}")
        logger.info(f"Quality: {quality}")
        logger.info(f"FPS: {fps}")

        # Build FFmpeg command
        cmd = [self.ffmpeg_path]

        # Input options
        cmd.extend(['-framerate', str(fps)])

        # Frame input pattern (try different patterns)
        frame_pattern = self._detect_frame_pattern(frames_dir)
        if not frame_pattern:
            logger.error(f"Could not detect frame pattern in {frames_dir}")
            return False

        cmd.extend(['-i', frame_pattern])

        # Audio input
        cmd.extend(['-i', audio_path])

        # Video encoding options
        cmd.extend(['-c:v', codec])

        # Quality/CRF settings
        crf = self._get_crf_value(quality, codec)
        if codec in ['libx264', 'libx265']:
            cmd.extend(['-crf', str(crf)])
            cmd.extend(['-preset', self._get_preset(quality)])
        elif codec == 'vp9':
            cmd.extend(['-b:v', '0'])  # Constant quality mode
            cmd.extend(['-crf', str(crf)])

        # Audio encoding
        cmd.extend(['-c:a', 'aac'])
        cmd.extend(['-b:a', '192k'])

        # Pixel format
        cmd.extend(['-pix_fmt', 'yuv420p'])

        # Shortest stream (match video to audio duration)
        cmd.extend(['-shortest'])

        # Overwrite flag
        if overwrite:
            cmd.append('-y')

        # Output
        cmd.append(output_path)

        logger.debug(f"Running FFmpeg: {' '.join(cmd)}")

        # Execute FFmpeg
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg failed with code {result.returncode}")
                if result.stderr:
                    logger.error(f"FFmpeg error output:\n{result.stderr}")
                return False

            # Check output file exists
            if not os.path.exists(output_path):
                logger.error("Output file was not created")
                return False

            file_size = os.path.getsize(output_path)
            logger.info("Video encoded successfully")
            logger.info(f"Output: {output_path}")
            logger.info(f"Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

            return True

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg encoding timed out (>10 minutes)")
            return False
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {str(e)}")
            return False

    def _detect_frame_pattern(self, frames_dir: str) -> Optional[str]:
        """
        Detect frame naming pattern.

        Args:
            frames_dir: Directory containing frames

        Returns:
            Frame pattern for FFmpeg (e.g., "frames/frame_%04d.png")
        """
        # Check for common patterns
        patterns = [
            ('frame_*.png', 'frame_%04d.png'),
            ('frame*.png', 'frame%04d.png'),
            ('*.png', '%04d.png'),
            ('frame_*.jpg', 'frame_%04d.jpg'),
            ('*.jpg', '%04d.jpg'),
        ]

        for glob_pattern, ffmpeg_pattern in patterns:
            files = glob.glob(os.path.join(frames_dir, glob_pattern))
            if files:
                return os.path.join(frames_dir, ffmpeg_pattern)

        return None

    def _get_crf_value(self, quality: str, codec: str) -> int:
        """
        Get CRF (Constant Rate Factor) value for quality preset.

        Args:
            quality: Quality preset name
            codec: Video codec

        Returns:
            CRF value (lower = better quality, larger file)
        """
        # CRF ranges: 0-51 for x264/x265 (18-28 typical), 0-63 for VP9 (15-35 typical)
        crf_map = {
            'libx264': {'low': 28, 'medium': 23, 'high': 18, 'ultra': 15},
            'libx265': {'low': 30, 'medium': 25, 'high': 20, 'ultra': 17},
            'vp9': {'low': 35, 'medium': 30, 'high': 25, 'ultra': 20},
        }

        return crf_map.get(codec, crf_map['libx264']).get(quality, 23)

    def _get_preset(self, quality: str) -> str:
        """
        Get encoding preset for quality level.

        Args:
            quality: Quality preset name

        Returns:
            FFmpeg preset name
        """
        preset_map = {
            'low': 'veryfast',
            'medium': 'medium',
            'high': 'slow',
            'ultra': 'veryslow'
        }

        return preset_map.get(quality, 'medium')

    def create_preview(
        self,
        frames_dir: str,
        audio_path: str,
        output_path: str,
        fps: int = 24,
        scale: float = 0.5
    ) -> bool:
        """
        Create a low-resolution preview video.

        Args:
            frames_dir: Directory containing rendered frames
            audio_path: Path to audio file
            output_path: Output video path
            fps: Frames per second
            scale: Resolution scale factor (0.5 = half resolution)

        Returns:
            True if successful, False otherwise
        """
        if not self.ffmpeg_path:
            logger.error("FFmpeg not found")
            return False

        frames_exist, frame_count = self.validate_frames(frames_dir)
        if not frames_exist:
            logger.error(f"No frames found in {frames_dir}")
            return False

        logger.info(f"Creating preview video (scale: {scale})...")

        frame_pattern = self._detect_frame_pattern(frames_dir)
        if not frame_pattern:
            return False

        # Build command with scaling
        cmd = [
            self.ffmpeg_path,
            '-framerate', str(fps),
            '-i', frame_pattern,
            '-i', audio_path,
            '-vf', f'scale=iw*{scale}:ih*{scale}',
            '-c:v', 'libx264',
            '-crf', '28',
            '-preset', 'veryfast',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-y',
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Preview created: {output_path}")
                return True
            else:
                logger.error("Preview creation failed")
                return False

        except Exception as e:
            logger.error(f"Preview creation error: {str(e)}")
            return False


def export_video_from_config(config: Dict, prep_data: Optional[Dict] = None) -> bool:
    """
    Export video using configuration settings.

    Args:
        config: Pipeline configuration
        prep_data: Optional preprocessed audio data (for duration info)

    Returns:
        True if successful, False otherwise
    """
    exporter = VideoExporter(config)

    # Get paths from config
    frames_dir = config.get('output', {}).get('frames_dir', 'outputs/frames')
    output_dir = config.get('output', {}).get('output_dir', 'outputs')
    video_name = config.get('output', {}).get('video_name', 'final_video.mp4')
    audio_path = config.get('inputs', {}).get('song_file')

    output_path = os.path.join(output_dir, video_name)

    # Get video settings
    fps = config.get('video', {}).get('fps', 24)
    codec = config.get('video', {}).get('codec', 'libx264')
    quality = config.get('video', {}).get('quality', 'high')

    # Check if preview mode
    preview_mode = config.get('advanced', {}).get('preview_mode', False)

    if preview_mode:
        preview_scale = config.get('advanced', {}).get('preview_scale', 0.5)
        preview_path = os.path.join(output_dir, 'preview_' + video_name)

        logger.info("=" * 70)
        logger.info("CREATING PREVIEW VIDEO")
        logger.info("=" * 70)

        success = exporter.create_preview(
            frames_dir=frames_dir,
            audio_path=audio_path,
            output_path=preview_path,
            fps=fps,
            scale=preview_scale
        )

        return success
    else:
        logger.info("=" * 70)
        logger.info("ENCODING FINAL VIDEO")
        logger.info("=" * 70)

        success = exporter.encode_video(
            frames_dir=frames_dir,
            audio_path=audio_path,
            output_path=output_path,
            fps=fps,
            codec=codec,
            quality=quality
        )

        return success


if __name__ == '__main__':
    """Test video export functionality."""
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description='Video Export Module')
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--frames', required=True, help='Frames directory')
    parser.add_argument('--audio', required=True, help='Audio file')
    parser.add_argument('--output', required=True, help='Output video file')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second')
    parser.add_argument('--quality', choices=['low', 'medium', 'high', 'ultra'], default='high')
    parser.add_argument('--codec', choices=['libx264', 'libx265', 'vp9'], default='libx264')
    parser.add_argument('--preview', action='store_true', help='Create preview')

    args = parser.parse_args()

    # Create exporter
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except:
        config = {}

    exporter = VideoExporter(config)

    # Export
    if args.preview:
        success = exporter.create_preview(
            frames_dir=args.frames,
            audio_path=args.audio,
            output_path=args.output,
            fps=args.fps
        )
    else:
        success = exporter.encode_video(
            frames_dir=args.frames,
            audio_path=args.audio,
            output_path=args.output,
            fps=args.fps,
            codec=args.codec,
            quality=args.quality
        )

    sys.exit(0 if success else 1)
