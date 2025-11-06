"""
Luma AI Video Animation Tool

Converts static images into animated video clips using Luma's Dream Machine (Ray model).
Adds motion, depth, and cinematic effects to create engaging viral-style videos.
"""

import os
import time
import replicate
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool
from config.settings import REPLICATE_API_TOKEN

class LumaVideoTool(BaseTool):
    """
    Tool for converting static images to animated videos using Luma AI.
    
    Uses Replicate's luma/ray model for image-to-video generation.
    Cost: $0.45 per video clip
    Time: ~120 seconds per clip
    """
    
    def __init__(self):
        super().__init__(
            name="luma_video",
            description="Convert static images to animated video clips with motion and depth"
        )
        # Set Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = "luma/ray"
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Required:
            - image_path: Path to input image
            - prompt: Text description of desired motion/animation
        """
        if "image_path" not in input_data:
            return False, "Missing required field: image_path"
        
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
            
        # Check if image file exists
        image_path = input_data["image_path"]
        if not os.path.exists(image_path):
            return False, f"Image file not found: {image_path}"
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate animated video from static image.
        
        Args:
            input_data: Must contain:
                - image_path: Path to input image
                - prompt: Text description of desired motion
                - output_dir: Optional custom output directory
                - loop: Optional boolean to create looping video (default: False)
                - aspect_ratio: Optional aspect ratio (default: "9:16" for vertical)
                
        Returns:
            Dictionary with video file path and metadata
        """
        image_path = input_data["image_path"]
        prompt = input_data["prompt"]
        output_dir = input_data.get("output_dir")
        loop = input_data.get("loop", False)
        aspect_ratio = input_data.get("aspect_ratio", "9:16")  # Vertical for social media
        
        self.logger.info(f"Generating video from image: {image_path}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        self.logger.info(f"Settings: aspect_ratio={aspect_ratio}, loop={loop}")
        
        # Open and upload the image
        with open(image_path, "rb") as image_file:
            # Run Luma Ray model
            self.logger.info("Running Luma Ray model (this may take 2-3 minutes)...")
            
            output = self.client.run(
                self.model,
                input={
                    "prompt": prompt,
                    "start_image": image_file,
                    "loop": loop,
                    "aspect_ratio": aspect_ratio,
                }
            )
            
            # Output is a FileOutput object with a URL
            video_url = str(output)
            self.logger.info(f"Video generated: {video_url}")
            
            # Download the video
            video_path = self._download_video(video_url, output_dir)
            
            self.logger.info(f"Video saved to: {video_path}")
            
            return {
                "video_path": video_path,
                "video_url": video_url,
                "source_image": image_path,
                "prompt": prompt,
                "duration_estimate": 5,  # Luma generates ~5 second clips
                "aspect_ratio": aspect_ratio,
            }
    
    def _download_video(self, video_url: str, output_dir: Optional[str] = None) -> str:
        """Download video from URL and save to disk."""
        import requests
        from datetime import datetime
        import uuid
        
        # Determine output directory
        if output_dir:
            save_dir = Path(output_dir)
        else:
            save_dir = Path("output") / "luma_videos"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"luma_{timestamp}_{unique_id}.mp4"
        filepath = save_dir / filename
        
        # Download video
        self.logger.info(f"Downloading video from {video_url}...")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(filepath)


# Export the tool
__all__ = ["LumaVideoTool"]
