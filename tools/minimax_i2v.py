"""
Minimax Hailuo 2.3 Image-to-Video Tool

Converts static images to videos with realistic motion.
Preserves the aspect ratio of the input image.
Best for: Character consistency, scene transitions, morph effects.
"""

import os
import replicate
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool
from config.settings import REPLICATE_API_TOKEN

class MinimaxI2VTool(BaseTool):
    """
    Tool for converting images to videos using Minimax Hailuo 2.3 (Image-to-Video mode).
    
    This tool takes an existing image and animates it based on a text prompt.
    The output video preserves the aspect ratio of the input image.
    
    Use cases:
    - Character animation with consistency
    - Scene transitions between frames
    - Morph effects
    - Animating existing artwork
    
    Cost: $0.28 per 6-second video (768p)
    Time: ~90 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="minimax_i2v",
            description="Convert images to videos with motion (Image-to-Video mode)"
        )
        # Set Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = "minimax/hailuo-2.3"
        self.model_fast = "minimax/hailuo-2.3-fast"
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Required:
            - first_frame_image: Path to input image (will be first frame)
            - prompt: Text description of desired motion/animation
        """
        if "first_frame_image" not in input_data:
            return False, "Missing required field: first_frame_image"
        
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
            
        # Check if image file exists
        image_path = input_data["first_frame_image"]
        if not os.path.exists(image_path):
            return False, f"Image file not found: {image_path}"
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from static image using Minimax Hailuo 2.3 (I2V mode).
        
        Args:
            input_data: Must contain:
                - first_frame_image: Path to input image (first frame)
                - prompt: Text description of desired motion
                - duration: Optional (6 or 10 seconds, default: 6)
                - resolution: Optional ("768p" or "1080p", default: "768p")
                - output_dir: Optional custom output directory
                - fast_mode: Optional boolean to use fast model (default: False)
                
        Returns:
            Dictionary with video file path and metadata
        """
        first_frame_image = input_data["first_frame_image"]
        prompt = input_data["prompt"]
        duration = input_data.get("duration", 6)
        resolution = input_data.get("resolution", "768p")
        output_dir = input_data.get("output_dir")
        fast_mode = input_data.get("fast_mode", False)
        
        # Select model
        model = self.model_fast if fast_mode else self.model
        
        self.logger.info(f"Generating video from image (I2V mode): {first_frame_image}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Duration: {duration}s, Resolution: {resolution}")
        
        # Open and upload the image
        with open(first_frame_image, "rb") as image_file:
            # Run Minimax Hailuo model in I2V mode
            self.logger.info("Running Minimax Hailuo I2V model (this may take 1-2 minutes)...")
            
            output = self.client.run(
                model,
                input={
                    "prompt": prompt,
                    "first_frame_image": image_file,  # Correct parameter name!
                    "duration": duration,
                    "resolution": resolution,
                    "prompt_optimizer": True,
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
                "first_frame_image": first_frame_image,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "mode": "image_to_video",
                "model": model,
                "cost_estimate": 0.28 if duration == 6 else 0.56,
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
            save_dir = Path("output") / "minimax_i2v"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"minimax_i2v_{timestamp}_{unique_id}.mp4"
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
__all__ = ["MinimaxI2VTool"]
