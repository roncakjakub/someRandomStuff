"""
Minimax Hailuo 2.3 Video Tool

High-fidelity video generation optimized for realistic human motion and cinematic VFX.
Best for human subjects, character animation, gestures, and emotional expressions.
"""

import os
import replicate
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool
from config.settings import REPLICATE_API_TOKEN

class MinimaxVideoTool(BaseTool):
    """
    Tool for converting images to videos using Minimax Hailuo 2.3.
    
    Uses Replicate's minimax/hailuo-2.3 model for image-to-video generation.
    Optimized for realistic human motion and cinematic VFX.
    Cost: Medium (~$0.30 per 5-second video)
    Time: ~120-180 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="minimax_video",
            description="Convert images to videos with realistic human motion using Minimax Hailuo 2.3"
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
        Generate video from static image using Minimax Hailuo 2.3.
        
        Args:
            input_data: Must contain:
                - image_path: Path to input image
                - prompt: Text description of desired motion
                - output_dir: Optional custom output directory
                - fast_mode: Optional boolean to use fast model (default: False)
                
        Returns:
            Dictionary with video file path and metadata
        """
        image_path = input_data["image_path"]
        prompt = input_data["prompt"]
        output_dir = input_data.get("output_dir")
        fast_mode = input_data.get("fast_mode", False)
        
        # Select model
        model = self.model_fast if fast_mode else self.model
        
        self.logger.info(f"Generating video from image: {image_path}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        self.logger.info(f"Model: {model}")
        
        # Open and upload the image
        with open(image_path, "rb") as image_file:
            # Run Minimax Hailuo model
            self.logger.info("Running Minimax Hailuo model (this may take 2-3 minutes)...")
            
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
                "duration_estimate": 5,  # Minimax generates ~5 second clips
                "model": model,
                "cost_estimate": 0.20 if fast_mode else 0.30,
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
            save_dir = Path("output") / "minimax_videos"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"minimax_{timestamp}_{unique_id}.mp4"
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
__all__ = ["MinimaxVideoTool"]
