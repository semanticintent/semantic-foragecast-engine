#!/usr/bin/env python3
"""
Video Generation Pipeline - Main Orchestrator

Orchestrates the complete audio-driven mascot animation pipeline:
1. Audio prep (Phase 1): beat detection, phoneme extraction, lyrics parsing
2. Animation composition (Phase 2): sprite compositing, effects
3. Video export (Phase 3): FFmpeg encoding
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional

import yaml

from prep_audio import process_audio
from export_video import VideoExporter, export_video_from_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the complete video generation pipeline."""

    def __init__(self, config_path: str):
        self.config_path = os.path.normpath(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info("Loaded configuration: %s", self.config_path)
            return config
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse configuration: {e}")

    def _ensure_directories(self):
        output_dir = self.config.get('output', {}).get('output_dir', 'outputs')
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        for directory in [output_dir, frames_dir]:
            os.makedirs(directory, exist_ok=True)
            logger.debug("Directory ready: %s", directory)

    def _validate_inputs(self):
        inputs = self.config.get('inputs', {})
        required = {
            'mascot_image': inputs.get('mascot_image'),
            'song_file': inputs.get('song_file'),
        }
        lyrics_file = inputs.get('lyrics_file')
        if lyrics_file:
            required['lyrics_file'] = lyrics_file

        missing = [
            f"{name}: {path or '(not set)'}"
            for name, path in required.items()
            if not path or not os.path.exists(path)
        ]
        if missing:
            raise FileNotFoundError(
                "Missing required input files:\n" +
                "\n".join(f"  - {f}" for f in missing)
            )
        logger.info("All input files validated")

    def phase1_prep_audio(self) -> Dict:
        """Execute Phase 1: audio preparation."""
        logger.info("=" * 60)
        logger.info("PHASE 1: AUDIO PREPARATION")
        logger.info("=" * 60)

        inputs = self.config.get('inputs', {})
        output = self.config.get('output', {})
        audio_path = inputs.get('song_file')
        lyrics_path = inputs.get('lyrics_file')
        rhubarb_path = self.config.get('rhubarb', {}).get('executable_path')
        prep_json = output.get('prep_json', 'outputs/prep_data.json')

        logger.info("Processing audio: %s", audio_path)
        if lyrics_path:
            logger.info("Processing lyrics: %s", lyrics_path)

        result = process_audio(
            audio_path=audio_path,
            lyrics_path=lyrics_path,
            rhubarb_path=rhubarb_path,
            output_json=prep_json
        )

        logger.info(
            "Phase 1 complete — %.1fs @ %.1f BPM, %d beats, %d phonemes, %d words",
            result['audio']['duration'],
            result['audio']['tempo'],
            len(result['beats']['beat_times']),
            len(result['phonemes']),
            len(result['timed_words']),
        )
        return result

    def phase2_compose_animation(self, prep_data: Dict):
        """Execute Phase 2: sprite-based animation composition."""
        logger.info("=" * 60)
        logger.info("PHASE 2: ANIMATION COMPOSITION")
        logger.info("=" * 60)

        try:
            from compose_animation import SpriteCompositor
        except ImportError:
            raise RuntimeError(
                "compose_animation module not found. "
                "Ensure compose_animation.py is present."
            )

        compositor = SpriteCompositor(self.config, prep_data)
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        frame_count = compositor.render_sequence(frames_dir)
        logger.info("Phase 2 complete — %d frames rendered to %s", frame_count, frames_dir)

    def phase3_export_video(self, prep_data: Optional[Dict] = None):
        """Execute Phase 3: FFmpeg video export."""
        logger.info("=" * 60)
        logger.info("PHASE 3: VIDEO EXPORT")
        logger.info("=" * 60)

        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        exporter = VideoExporter(self.config)
        frames_exist, frame_count = exporter.validate_frames(frames_dir)

        if not frames_exist:
            raise RuntimeError(
                f"No rendered frames found in {frames_dir}. "
                "Run Phase 2 first to generate frames."
            )

        logger.info("Found %d frames in %s", frame_count, frames_dir)
        success = export_video_from_config(self.config, prep_data)

        if not success:
            raise RuntimeError("Video export failed — check FFmpeg installation")

        output_dir = self.config.get('output', {}).get('output_dir', 'outputs')
        video_name = self.config.get('output', {}).get('video_name', 'final_video.mp4')
        logger.info("Phase 3 complete — %s", os.path.join(output_dir, video_name))

    def run(self) -> int:
        """Execute the complete pipeline. Returns exit code."""
        try:
            logger.info("=" * 60)
            logger.info("SEMANTIC FORAGECAST ENGINE")
            logger.info("=" * 60)

            self._ensure_directories()
            self._validate_inputs()

            prep_data = self.phase1_prep_audio()
            self.phase2_compose_animation(prep_data)
            self.phase3_export_video(prep_data)

            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)
            return 0

        except Exception as e:
            logger.error("Pipeline failed: %s", e, exc_info=True)
            return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic Foragecast Engine — audio-driven mascot animation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                        # Run full pipeline with config.yaml
  python main.py --config custom.yaml  # Use custom config
  python main.py --phase 1             # Run only Phase 1 (audio prep)
  python main.py --validate            # Validate config and inputs, then exit
        """
    )
    parser.add_argument('--config', '-c', default='config.yaml',
                        help='Path to configuration YAML (default: config.yaml)')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3],
                        help='Run only specified phase (1=prep, 2=animate, 3=export)')
    parser.add_argument('--validate', action='store_true',
                        help='Validate config and inputs, then exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable debug logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        orchestrator = PipelineOrchestrator(args.config)

        if args.validate:
            orchestrator._ensure_directories()
            orchestrator._validate_inputs()
            logger.info("Configuration and inputs validated successfully")
            return 0

        if args.phase:
            orchestrator._ensure_directories()
            orchestrator._validate_inputs()

            if args.phase == 1:
                orchestrator.phase1_prep_audio()
            elif args.phase == 2:
                prep_json = orchestrator.config.get('output', {}).get(
                    'prep_json', 'outputs/prep_data.json'
                )
                if not os.path.exists(prep_json):
                    logger.error("Prep data not found: %s — run Phase 1 first", prep_json)
                    return 1
                with open(prep_json, 'r') as f:
                    prep_data = json.load(f)
                orchestrator.phase2_compose_animation(prep_data)
            elif args.phase == 3:
                prep_json = orchestrator.config.get('output', {}).get(
                    'prep_json', 'outputs/prep_data.json'
                )
                prep_data = None
                if os.path.exists(prep_json):
                    with open(prep_json, 'r') as f:
                        prep_data = json.load(f)
                orchestrator.phase3_export_video(prep_data)
            return 0

        return orchestrator.run()

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error("%s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
