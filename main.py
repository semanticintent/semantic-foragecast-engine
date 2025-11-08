#!/usr/bin/env python3
"""
Video Generation Pipeline - Main Orchestrator
Phase 2: Orchestrator + Blender Integration

This script orchestrates the entire video generation pipeline:
1. Load configuration
2. Run audio prep (Phase 1)
3. Execute Blender automation (Phase 2)
4. Export final video (Phase 3)

Author: Claude (Anthropic)
Version: 2.0
Date: November 2025
Platform: Cross-platform (Windows 11 optimized)
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional
import shutil

import yaml

from prep_audio import process_audio
from export_video import VideoExporter, export_video_from_config


class PipelineOrchestrator:
    """Orchestrates the complete video generation pipeline."""

    def __init__(self, config_path: str):
        """
        Initialize the orchestrator with configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = os.path.normpath(config_path)
        self.verbose = True  # Default, will be updated from config
        self.config = self._load_config()
        self.verbose = self.config.get('advanced', {}).get('verbose', True)

    def _load_config(self) -> Dict:
        """
        Load and validate configuration from YAML.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if self.verbose:
                print(f"✓ Loaded configuration from: {self.config_path}")

            return config

        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse configuration: {str(e)}")

    def _log(self, message: str, level: str = "INFO"):
        """
        Log message if verbose mode enabled.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        if self.verbose:
            prefix = {
                "INFO": "ℹ",
                "WARNING": "⚠",
                "ERROR": "✗"
            }.get(level, "•")
            print(f"{prefix} {message}")

    def _ensure_directories(self):
        """Create output directories if they don't exist."""
        output_dir = self.config.get('output', {}).get('output_dir', 'outputs')
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')

        for directory in [output_dir, frames_dir]:
            os.makedirs(directory, exist_ok=True)
            self._log(f"Ensured directory exists: {directory}")

    def _validate_inputs(self):
        """
        Validate that all required input files exist.

        Raises:
            FileNotFoundError: If required files are missing
        """
        inputs = self.config.get('inputs', {})
        required_files = {
            'mascot_image': inputs.get('mascot_image'),
            'song_file': inputs.get('song_file'),
        }

        # Lyrics are optional
        lyrics_file = inputs.get('lyrics_file')
        if lyrics_file:
            required_files['lyrics_file'] = lyrics_file

        missing_files = []
        for name, path in required_files.items():
            if not path:
                missing_files.append(f"{name} (not specified in config)")
            elif not os.path.exists(path):
                missing_files.append(f"{name}: {path}")

        if missing_files:
            raise FileNotFoundError(
                f"Missing required input files:\n" +
                "\n".join(f"  - {f}" for f in missing_files)
            )

        self._log("✓ All input files validated")

    def _find_blender(self) -> Optional[str]:
        """
        Locate Blender executable.

        Returns:
            Path to Blender or None if not found
        """
        # Check config first
        blender_path = self.config.get('blender', {}).get('executable_path')
        if blender_path and os.path.exists(blender_path):
            return os.path.normpath(blender_path)

        # Check common paths
        if sys.platform == 'win32':
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return os.path.normpath(path)

        # Check PATH
        blender = shutil.which('blender')
        if blender:
            return os.path.normpath(blender)

        return None

    def phase1_prep_audio(self) -> Dict:
        """
        Execute Phase 1: Audio preparation.

        Returns:
            Dictionary with prep data (beats, phonemes, lyrics)
        """
        self._log("=" * 70)
        self._log("PHASE 1: AUDIO PREPARATION")
        self._log("=" * 70)

        inputs = self.config.get('inputs', {})
        output = self.config.get('output', {})

        audio_path = inputs.get('song_file')
        lyrics_path = inputs.get('lyrics_file')
        rhubarb_path = self.config.get('rhubarb', {}).get('executable_path')
        prep_json = output.get('prep_json', 'outputs/prep_data.json')

        self._log(f"Processing audio: {audio_path}")
        if lyrics_path:
            self._log(f"Processing lyrics: {lyrics_path}")

        # Run audio processing
        result = process_audio(
            audio_path=audio_path,
            lyrics_path=lyrics_path,
            rhubarb_path=rhubarb_path,
            output_json=prep_json
        )

        self._log("✓ Phase 1 complete")
        self._log(f"  Audio: {result['audio']['duration']}s @ {result['audio']['tempo']:.1f} BPM")
        self._log(f"  Beats: {len(result['beats']['beat_times'])}")
        self._log(f"  Phonemes: {len(result['phonemes'])}")
        self._log(f"  Words: {len(result['timed_words'])}")
        self._log("")

        return result

    def phase2_blender_animation(self, prep_data: Dict):
        """
        Execute Phase 2: Blender animation generation.

        Args:
            prep_data: Output from Phase 1 (beats, phonemes, etc.)
        """
        self._log("=" * 70)
        self._log("PHASE 2: BLENDER ANIMATION")
        self._log("=" * 70)

        # Find Blender
        blender_path = self._find_blender()
        if not blender_path:
            self._log("WARNING: Blender not found. Skipping Phase 2.", "WARNING")
            self._log("  Install Blender 4.2+ or set 'blender.executable_path' in config.yaml", "WARNING")
            return

        self._log(f"Blender executable: {blender_path}")

        # Get script path
        script_path = self.config.get('blender', {}).get('script_path', 'blender_script.py')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Blender script not found: {script_path}")

        # Prepare arguments for Blender
        background = self.config.get('blender', {}).get('background', True)
        prep_json = self.config.get('output', {}).get('prep_json', 'outputs/prep_data.json')

        # Build Blender command
        cmd = [blender_path]

        if background:
            cmd.extend(['--background'])

        cmd.extend([
            '--python', script_path,
            '--',
            '--config', self.config_path,
            '--prep-data', prep_json
        ])

        self._log(f"Executing: {' '.join(cmd)}")

        # Run Blender
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                self._log(f"Blender exited with code {result.returncode}", "ERROR")
                if result.stderr:
                    self._log(f"Error output:\n{result.stderr}", "ERROR")
                raise Exception(f"Blender execution failed")

            if result.stdout and self.verbose:
                print(result.stdout)

            self._log("✓ Phase 2 complete")
            self._log("")

        except subprocess.TimeoutExpired:
            raise Exception("Blender execution timed out (>10 minutes)")

    def phase3_export_video(self, prep_data: Optional[Dict] = None):
        """
        Execute Phase 3: Video export with FFmpeg.

        Args:
            prep_data: Optional preprocessed audio data
        """
        self._log("=" * 70)
        self._log("PHASE 3: VIDEO EXPORT")
        self._log("=" * 70)

        # Check if frames exist
        frames_dir = self.config.get('output', {}).get('frames_dir', 'outputs/frames')
        exporter = VideoExporter(self.config)

        frames_exist, frame_count = exporter.validate_frames(frames_dir)

        if not frames_exist:
            self._log("WARNING: No rendered frames found. Skipping video export.", "WARNING")
            self._log(f"  Expected frames in: {frames_dir}", "WARNING")
            self._log("  Run Phase 2 (Blender) first to generate frames.", "WARNING")
            self._log("")
            return

        self._log(f"Found {frame_count} frames in {frames_dir}")

        # Export video
        success = export_video_from_config(self.config, prep_data)

        if success:
            self._log("✓ Phase 3 complete")
            output_dir = self.config.get('output', {}).get('output_dir', 'outputs')
            video_name = self.config.get('output', {}).get('video_name', 'final_video.mp4')
            output_path = os.path.join(output_dir, video_name)
            self._log(f"  Video: {output_path}")
        else:
            self._log("Phase 3 failed", "ERROR")
            raise Exception("Video export failed")

        self._log("")

    def run(self):
        """Execute the complete pipeline."""
        try:
            self._log("=" * 70)
            self._log("SEMANTIC FORAGECAST ENGINE - VIDEO PIPELINE")
            self._log("=" * 70)
            self._log("")

            # Setup
            self._ensure_directories()
            self._validate_inputs()

            # Phase 1: Prep
            prep_data = self.phase1_prep_audio()

            # Phase 2: Blender
            self.phase2_blender_animation(prep_data)

            # Phase 3: Export
            self.phase3_export_video(prep_data)

            self._log("=" * 70)
            self._log("✓ PIPELINE COMPLETE")
            self._log("=" * 70)

            output_dir = self.config.get('output', {}).get('output_dir', 'outputs')
            self._log(f"Check output directory: {output_dir}")

            return 0

        except Exception as e:
            self._log(f"Pipeline failed: {str(e)}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Semantic Foragecast Engine - Video Generation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                      # Use default config.yaml
  python main.py --config custom.yaml # Use custom config
  python main.py --phase 1            # Run only Phase 1 (prep)
  python main.py --validate           # Validate config and exit

For more information, see README.md
        """
    )

    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration YAML file (default: config.yaml)'
    )

    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3],
        help='Run only specified phase (1=prep, 2=blender, 3=export)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration and inputs, then exit'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Create orchestrator
        orchestrator = PipelineOrchestrator(args.config)

        # Override verbosity if specified
        if args.verbose:
            orchestrator.config['advanced']['verbose'] = True
            orchestrator.verbose = True

        # Validate mode
        if args.validate:
            orchestrator._ensure_directories()
            orchestrator._validate_inputs()
            print("✓ Configuration and inputs validated successfully")
            return 0

        # Single phase mode
        if args.phase:
            orchestrator._ensure_directories()
            orchestrator._validate_inputs()

            if args.phase == 1:
                orchestrator.phase1_prep_audio()
            elif args.phase == 2:
                prep_json = orchestrator.config.get('output', {}).get('prep_json', 'outputs/prep_data.json')
                if not os.path.exists(prep_json):
                    print(f"ERROR: Prep data not found: {prep_json}")
                    print("Run Phase 1 first: python main.py --phase 1")
                    return 1
                with open(prep_json, 'r') as f:
                    prep_data = json.load(f)
                orchestrator.phase2_blender_animation(prep_data)
            elif args.phase == 3:
                # Load prep data if available
                prep_json = orchestrator.config.get('output', {}).get('prep_json', 'outputs/prep_data.json')
                prep_data = None
                if os.path.exists(prep_json):
                    with open(prep_json, 'r') as f:
                        prep_data = json.load(f)
                orchestrator.phase3_export_video(prep_data)

            return 0

        # Full pipeline
        return orchestrator.run()

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        return 130
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
