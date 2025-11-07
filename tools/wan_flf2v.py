"""
Wan-2.1 FLF2V Tool - First-Last-Frame-to-Video

Generates videos from start and end images using Wan-2.1 via fal.ai API.
Supports smooth morph transitions between two images.
"""

import os
import logging
import fal_client
from typing import Dict, Any, Optional


class WanFLF2VTool:
    """Tool for generating videos using Wan-2.1 First-Last-Frame-to-Video via fal.ai."""
    
    def __init__(self):
        """Initialize Wan FLF2V tool."""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("FAL_KEY")
        
        if not self.api_key:
            raise ValueError("FAL_KEY environment variable not set")
        
        # Set fal_client API key
        os.environ["FAL_KEY"] = self.api_key
        
        self.model = "fal-ai/wan-flf2v"
        self.logger.info(f"Initialized Wan FLF2V tool with model: {self.model}")
    
    def execute(self, start_image_path: str = None, start_image_url: str = None,
                end_image_path: str = None, end_image_url: str = None,
                prompt: str = "", resolution: str = "720p",
                num_frames: int = 81, frames_per_second: int = 16,
                negative_prompt: str = None, output_path: str = None,
                seed: int = None) -> Dict[str, Any]:
        """
        Generate video from start and end images using Wan-2.1.
        
        Args:
            start_image_path: Path to start image file (will be uploaded)
            start_image_url: URL to start image (if already uploaded)
            end_image_path: Path to end image file (will be uploaded)
            end_image_url: URL to end image (if already uploaded)
            prompt: Text prompt for video generation
            resolution: Video resolution (480p or 720p)
            num_frames: Number of frames (81-100, default 81)
            frames_per_second: FPS (5-24, default 16)
            negative_prompt: Negative prompt (optional)
            output_path: Path to save output video (optional)
            seed: Random seed for reproducibility (optional)
        
        Returns:
            Dict with video_url and metadata
        """
        try:
            # Upload start image if path provided
            if start_image_path and not start_image_url:
                self.logger.info(f"Uploading start image: {start_image_path}")
                start_image_url = fal_client.upload_file(start_image_path)
                self.logger.info(f"Start image uploaded: {start_image_url}")
            
            if not start_image_url:
                raise ValueError("Either start_image_path or start_image_url must be provided")
            
            # Upload end image if path provided
            if end_image_path and not end_image_url:
                self.logger.info(f"Uploading end image: {end_image_path}")
                end_image_url = fal_client.upload_file(end_image_path)
                self.logger.info(f"End image uploaded: {end_image_url}")
            
            if not end_image_url:
                raise ValueError("Either end_image_path or end_image_url must be provided")
            
            # Prepare arguments
            arguments = {
                "start_image_url": start_image_url,
                "end_image_url": end_image_url,
                "prompt": prompt,
                "resolution": resolution,
                "num_frames": num_frames,
                "frames_per_second": frames_per_second,
                "aspect_ratio": "9:16",  # Force vertical for social media
            }
            
            # Add optional parameters
            if negative_prompt:
                arguments["negative_prompt"] = negative_prompt
            
            if seed is not None:
                arguments["seed"] = seed
            
            self.logger.info(f"Submitting Wan FLF2V request with arguments: {arguments}")
            
            # Submit request and wait for result (fal_client handles queue)
            result = fal_client.subscribe(
                self.model,
                arguments=arguments,
                with_logs=True,
            )
            
            self.logger.info(f"Wan FLF2V video generated successfully")
            
            # Extract video URL from result
            video_url = result.get("video", {}).get("url")
            
            if not video_url:
                raise ValueError(f"No video URL in result: {result}")
            
            self.logger.info(f"Video URL: {video_url}")
            
            # Calculate duration in seconds
            duration = num_frames / frames_per_second
            
            # Download video if output_path provided
            if output_path:
                self.logger.info(f"Downloading video to: {output_path}")
                import requests
                response = requests.get(video_url)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Video saved to: {output_path}")
            
            return {
                "video_url": video_url,
                "video_path": output_path if output_path else None,
                "duration": duration,
                "resolution": resolution,
                "prompt": prompt,
                "num_frames": num_frames,
                "fps": frames_per_second,
                "mode": "morph",
            }
        
        except Exception as e:
            self.logger.error(f"Error in wan_flf2v: {e}", exc_info=True)
            raise
    
    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Backward compatibility wrapper for execute().
        
        Args:
            params: Dict with keys:
                - start_image: Path to start image
                - end_image: Path to end image
                - prompt: Text prompt
                - duration: Video duration (ignored, calculated from frames/fps)
                - output_dir: Output directory
                - filename: Output filename
        
        Returns:
            Dict with video_path and metadata
        """
        # Extract parameters
        start_image = params.get("start_image")
        end_image = params.get("end_image")
        prompt = params.get("prompt", "")
        output_dir = params.get("output_dir", ".")
        filename = params.get("filename", "output.mp4")
        
        # Build output path
        import os
        output_path = os.path.join(output_dir, filename)
        
        # Call execute()
        result = self.execute(
            start_image_path=start_image,
            end_image_path=end_image,
            prompt=prompt,
            output_path=output_path,
        )
        
        # Return in expected format
        return {
            "video_path": result["video_path"],
            "video_url": result["video_url"],
            "duration": result["duration"],
            "prompt": result["prompt"],
        }
