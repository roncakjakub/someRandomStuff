"""
Video Assembly Tool for combining images and audio into final video.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(PathLib(__file__).parent.parent))
    from tools.base_tool import BaseTool
    from config.settings import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS
else:
    from .base_tool import BaseTool
    from config.settings import OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


class VideoAssemblyTool(BaseTool):
    """
    Tool for assembling final video from images and audio using FFMPEG.
    """
    
    def __init__(self):
        super().__init__(
            name="video_assembly",
            description="Assemble images and audio into final video"
        )
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that images are provided."""
        if "images" not in input_data:
            return False, "Missing required field: images"
        if not isinstance(input_data["images"], list):
            return False, "Images must be a list"
        if len(input_data["images"]) == 0:
            return False, "Images list cannot be empty"
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble video from images and optional audio.
        
        Args:
            input_data: Must contain 'images' list, optional 'audio_path', 'duration_per_image',
                       'background_music_path', 'music_volume'
            
        Returns:
            Dictionary with video file path
        """
        images = input_data["images"]
        audio_path = input_data.get("audio_path")
        background_music_path = input_data.get("background_music_path")
        music_volume = input_data.get("music_volume", 0.15)
        duration_per_image = input_data.get("duration_per_image", 3.0)  # seconds
        output_dir = input_data.get("output_dir")  # Custom output directory
        
        self.logger.info(f"Assembling video from {len(images)} images...")
        
        # Create video from images
        video_path = self._create_video_from_images(images, duration_per_image, output_dir)
        
        # Add audio if provided
        if audio_path:
            video_path = self._add_audio_to_video(
                video_path, 
                audio_path,
                background_music_path=background_music_path,
                music_volume=music_volume
            )
        
        self.logger.info(f"Video assembled: {video_path}")
        
        return {
            "video_path": str(video_path),
            "num_images": len(images),
            "has_audio": audio_path is not None,
        }
    
    def _create_video_from_images(
        self, 
        images: List[str], 
        duration_per_image: float,
        output_dir: str = None
    ) -> Path:
        """
        Create video from list of images using FFMPEG.
        
        Args:
            images: List of image file paths
            duration_per_image: Duration to show each image (seconds)
            output_dir: Custom output directory (uses OUTPUT_DIR if not provided)
            
        Returns:
            Path to created video
        """
        import uuid
        from datetime import datetime
        from pathlib import Path
        
        # Use provided output_dir or fallback to OUTPUT_DIR
        target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"video_{timestamp}_{unique_id}_no_audio.mp4"
        output_path = target_dir / output_filename
        
        # Create a temporary file list for FFMPEG concat
        filelist_path = target_dir / f"filelist_{unique_id}.txt"
        with open(filelist_path, "w") as f:
            for image in images:
                # Convert to absolute path to avoid FFMPEG concat issues
                abs_image_path = Path(image).resolve()
                f.write(f"file '{abs_image_path}'\n")
                f.write(f"duration {duration_per_image}\n")
            # Add last image again (FFMPEG concat quirk)
            abs_last_image = Path(images[-1]).resolve()
            f.write(f"file '{abs_last_image}'\n")
        
        # FFMPEG command to create video from images
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-r", str(VIDEO_FPS),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        self.logger.info(f"Running FFMPEG: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("Video created successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFMPEG error: {e.stderr}")
            raise
        finally:
            # Clean up temporary file list
            if filelist_path.exists():
                filelist_path.unlink()
        
        return output_path
    
    def _add_audio_to_video(
        self, 
        video_path: Path, 
        audio_path: str,
        background_music_path: Optional[str] = None,
        music_volume: float = 0.15
    ) -> Path:
        """
        Add audio track (voiceover + optional background music) to video using FFMPEG.
        
        Args:
            video_path: Path to video file
            audio_path: Path to voiceover audio file
            background_music_path: Optional path to background music file
            music_volume: Background music volume (0.0-1.0, default 0.15 = 15%)
            
        Returns:
            Path to video with audio
        """
        # Generate output filename
        output_filename = video_path.stem.replace("_no_audio", "") + "_final.mp4"
        output_path = video_path.parent / output_filename
        
        # Check if background music file exists
        if background_music_path and not Path(background_music_path).exists():
            self.logger.warning(f"Background music file not found: {background_music_path}. Skipping music.")
            background_music_path = None
        
        # If no background music, use simple audio addition
        if not background_music_path:
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-y",
                str(output_path)
            ]
        else:
            # Mix voiceover + background music
            # Voiceover at 100%, music at music_volume (default 15%)
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-i", audio_path,  # Voiceover
                "-i", background_music_path,  # Background music
                "-filter_complex",
                f"[2:a]volume={music_volume}[music];[1:a][music]amix=inputs=2:duration=shortest[audio]",
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-y",
                str(output_path)
            ]
        
        self.logger.info(f"Adding audio to video...")
        if background_music_path:
            self.logger.info(f"  Voiceover: {audio_path}")
            self.logger.info(f"  Background music: {background_music_path} (volume: {music_volume*100:.0f}%)")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("Audio added successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFMPEG error: {e.stderr}")
            raise
        
        # Remove temporary video without audio
        if video_path.exists():
            video_path.unlink()
        
        return output_path
    
    def create_video_with_transitions(
        self,
        video_clips: List[str],
        audio_path: Optional[str] = None,
        transition_duration: float = 0.3,
        output_dir: str = None,
        background_music_path: Optional[str] = None,
        music_volume: float = 0.15
    ) -> Dict[str, Any]:
        """
        Create video with smooth crossfade transitions between video clips.
        
        Args:
            video_clips: List of video file paths (not images!)
            audio_path: Optional audio file path
            transition_duration: Duration of crossfade in seconds (default 0.3s)
            output_dir: Custom output directory
            
        Returns:
            Video creation result with final path
        """
        import uuid
        from datetime import datetime
        from pathlib import Path
        
        self.logger.info(f"Creating video with crossfade transitions from {len(video_clips)} clips...")
        
        # Use provided output_dir or fallback to OUTPUT_DIR
        target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"video_{timestamp}_{unique_id}_no_audio.mp4"
        output_path = target_dir / output_filename
        
        # Get actual duration of each video clip using ffprobe
        import json
        clip_durations = []
        for clip_path in video_clips:
            try:
                probe_cmd = [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    str(clip_path)
                ]
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                duration_data = json.loads(probe_result.stdout)
                duration = float(duration_data["format"]["duration"])
                clip_durations.append(duration)
                self.logger.debug(f"Clip {Path(clip_path).name}: {duration:.2f}s")
            except Exception as e:
                self.logger.warning(f"Could not get duration for {clip_path}, assuming 5.0s: {e}")
                clip_durations.append(5.0)
        
        # Build complex filter for crossfades between all clips
        # Format: [0:v][1:v]xfade=transition=fade:duration=0.3:offset=4.7[v01];
        #         [v01][2:v]xfade=transition=fade:duration=0.3:offset=9.4[v02];
        
        filter_parts = []
        last_label = "0:v"
        cumulative_offset = 0.0
        
        for i in range(1, len(video_clips)):
            current_label = f"v{i-1:02d}" if i > 1 else "0:v"
            next_input = f"{i}:v"
            output_label = f"v{i:02d}"
            
            # Calculate offset: cumulative duration of previous clips minus transition overlap
            cumulative_offset += clip_durations[i-1] - transition_duration
            offset = cumulative_offset
            
            filter_parts.append(
                f"[{current_label}][{next_input}]xfade=transition=fade:duration={transition_duration}:offset={offset:.1f}[{output_label}]"
            )
            last_label = output_label
        
        # Join all filter parts
        filter_complex = ";".join(filter_parts)
        
        # Build FFMPEG command
        cmd = ["ffmpeg"]
        
        # Add all input clips
        for clip in video_clips:
            cmd.extend(["-i", str(clip)])
        
        # Add filter complex and output
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", f"[{last_label}]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_path)
        ])
        
        self.logger.info(f"Running FFMPEG with crossfade transitions...")
        self.logger.debug(f"Filter: {filter_complex}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("Video with transitions created successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFMPEG error: {e.stderr}")
            # Fallback: concatenate without transitions
            self.logger.warning("Falling back to simple concatenation...")
            return self._concatenate_videos_simple(
                video_clips, 
                audio_path, 
                output_dir,
                background_music_path=background_music_path,
                music_volume=music_volume
            )
        
        # Add audio if provided
        final_path = output_path
        if audio_path:
            final_path = self._add_audio_to_video(
                output_path, 
                audio_path,
                background_music_path=background_music_path,
                music_volume=music_volume
            )
        
        return {
            "video_path": str(final_path),
            "num_clips": len(video_clips),
            "has_audio": audio_path is not None,
            "has_transitions": True
        }
    
    def _concatenate_videos_simple(
        self,
        video_clips: List[str],
        audio_path: Optional[str] = None,
        output_dir: str = None,
        background_music_path: Optional[str] = None,
        music_volume: float = 0.15
    ) -> Dict[str, Any]:
        """
        Simple video concatenation without transitions (fallback).
        
        Args:
            video_clips: List of video file paths
            audio_path: Optional audio file path
            output_dir: Custom output directory
            
        Returns:
            Video creation result
        """
        import uuid
        from datetime import datetime
        from pathlib import Path
        
        target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"video_{timestamp}_{unique_id}_no_audio.mp4"
        output_path = target_dir / output_filename
        
        # Create concat file
        filelist_path = target_dir / f"filelist_{unique_id}.txt"
        with open(filelist_path, "w") as f:
            for clip in video_clips:
                f.write(f"file '{clip}'\n")
        
        # FFMPEG concat command
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-c", "copy",
            "-y",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info("Videos concatenated successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFMPEG error: {e.stderr}")
            raise
        finally:
            if filelist_path.exists():
                filelist_path.unlink()
        
        # Add audio if provided
        final_path = output_path
        if audio_path:
            final_path = self._add_audio_to_video(
                output_path, 
                audio_path,
                background_music_path=background_music_path,
                music_volume=music_volume
            )
        
        return {
            "video_path": str(final_path),
            "num_clips": len(video_clips),
            "has_audio": audio_path is not None,
            "has_transitions": False
        }


if __name__ == "__main__":
    # Test the tool
    tool = VideoAssemblyTool()
    
    # This would need actual image files to test
    # result = tool.create_video_with_transitions(
    #     images=["image1.png", "image2.png", "image3.png"],
    #     audio_path="voiceover.mp3"
    # )
    # print(result)
