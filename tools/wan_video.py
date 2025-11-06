"""
Wan 2.5 Image-to-Video Tool

Budget-friendly image-to-video generation using Alibaba's open-source Wan 2.5 model.
Best for cost-effective video animation when budget is a priority.
"""

import os
import replicate
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool
from config.settings import REPLICATE_API_TOKEN

class WanVideoTool(BaseTool):
    """
    Tool for converting images to videos using Wan 2.5 i2v.
    
    Uses Replicate's wan-video/wan-2.5-i2v model for image-to-video generation.
    Open source, budget-friendly option.
    Cost: Low (~$0.10 per 5-second video)
    Time: ~60-90 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="wan_video",
            description="Convert images to videos using budget-friendly Wan 2.5 i2v"
        )
        # Set Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = "wan-video/wan-2.5-i2v"
        self.model_fast = "wan-video/wan-2.5-i2v-fast"
        
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
        Generate video from static image using Wan 2.5 i2v.
        
        Args:
            input_data: Must contain:
                - image_path: Path to input image
                - prompt: Text description of desired motion
                - output_dir: Optional custom output directory
                - fast_mode: Optional boolean to use fast model (default: True)
                
        Returns:
            Dictionary with video file path and metadata
        """
        image_path = input_data["image_path"]
        prompt = input_data["prompt"]
        output_dir = input_data.get("output_dir")
        fast_mode = input_data.get("fast_mode", True)  # Default to fast for budget
        
        # Select model
        model = self.model_fast if fast_mode else self.model
        
        self.logger.info(f"Generating video from image: {image_path}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        self.logger.info(f"Model: {model}")
        
        # Open and upload the image
        with open(image_path, "rb") as image_file:
            # Run Wan 2.5 model
            self.logger.info("Running Wan 2.5 i2v model (this may take 60-90 seconds)...")
            
            output = self.client.run(
                model,
                input={
                    "prompt": prompt,
                    "image": image_file,
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
                "duration_estimate": 5,  # Wan generates ~5 second clips
                "model": model,
                "cost_estimate": 0.08 if fast_mode else 0.12,
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
            save_dir = Path("output") / "wan_videos"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"wan_{timestamp}_{unique_id}.mp4"
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
__all__ = ["WanVideoTool"]
