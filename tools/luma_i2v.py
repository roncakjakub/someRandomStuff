"""
Luma Ray Image-to-Video Tool

Converts static images to videos with smooth, realistic motion.
Known for high-quality physics and natural movement.
Best for: Premium quality, smooth animations, realistic motion.
"""

import os
import sys
import replicate
from typing import Dict, Any, Optional
from pathlib import Path

# Handle imports for both standalone and module usage
try:
    from .base_tool import BaseTool
    from config.settings import REPLICATE_API_TOKEN
except ImportError:
    # Standalone mode - use environment variable directly
    from dotenv import load_dotenv
    load_dotenv()
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    
    # Minimal BaseTool for standalone
    import logging
    class BaseTool:
        def __init__(self, name, description):
            self.name = name
            self.description = description
            self.logger = logging.getLogger(name)
            logging.basicConfig(level=logging.INFO)

class LumaI2VTool(BaseTool):
    """
    Tool for converting images to videos using Luma Ray (Image-to-Video mode).
    
    Luma Ray (Dream Machine) is known for:
    - Smooth, realistic motion
    - High-quality physics simulation
    - Natural-looking animations
    - Premium quality output
    
    Use cases:
    - Premium quality animations
    - Smooth character movements
    - Realistic physics (water, smoke, fabric)
    - High-end commercial content
    
    Cost: $0.45 per 5-second video
    Time: ~38 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="luma_i2v",
            description="Convert images to videos with premium smooth motion (Image-to-Video mode)"
        )
        # Set Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = "luma/ray"
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Required:
            - start_image: Path to input image (will be first frame)
            - prompt: Text description of desired motion/animation
        """
        if "start_image" not in input_data:
            return False, "Missing required field: start_image"
        
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
            
        # Check if image file exists
        image_path = input_data["start_image"]
        if not os.path.exists(image_path):
            return False, f"Image file not found: {image_path}"
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from static image using Luma Ray (I2V mode).
        
        Args:
            input_data: Must contain:
                - start_image: Path to input image (first frame)
                - prompt: Text description of desired motion
                - aspect_ratio: Optional ("1:1", "3:4", "4:3", "9:16", "16:9", "9:21", "21:9")
                - loop: Optional boolean for seamless loop (default: False)
                - end_image: Optional last frame for controlled transitions
                - output_dir: Optional custom output directory
                
        Returns:
            Dictionary with video file path and metadata
        """
        start_image = input_data["start_image"]
        prompt = input_data["prompt"]
        aspect_ratio = input_data.get("aspect_ratio")  # None = follow image
        loop = input_data.get("loop", False)
        end_image = input_data.get("end_image")
        output_dir = input_data.get("output_dir")
        
        self.logger.info(f"Generating video from image (Luma I2V mode): {start_image}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        if aspect_ratio:
            self.logger.info(f"Aspect ratio: {aspect_ratio}")
        else:
            self.logger.info(f"Aspect ratio: Following input image")
        self.logger.info(f"Loop: {loop}")
        
        # Prepare input
        api_input = {
            "prompt": prompt,
            "loop": loop,
        }
        
        # Add aspect ratio if specified
        if aspect_ratio:
            api_input["aspect_ratio"] = aspect_ratio
        
        # Open and upload the start image
        with open(start_image, "rb") as start_file:
            api_input["start_image"] = start_file
            
            # Add end image if provided
            if end_image and os.path.exists(end_image):
                with open(end_image, "rb") as end_file:
                    api_input["end_image"] = end_file
                    self.logger.info(f"Using end image: {end_image}")
            
            # Run Luma Ray model in I2V mode
            self.logger.info("Running Luma Ray I2V model (this may take 30-60 seconds)...")
            
            output = self.client.run(
                self.model,
                input=api_input
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
                "start_image": start_image,
                "end_image": end_image if end_image else None,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio if aspect_ratio else "follows_input",
                "loop": loop,
                "duration": 5,  # Luma generates 5-second videos
                "mode": "image_to_video",
                "model": self.model,
                "cost_estimate": 0.45,
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
            save_dir = Path("output") / "luma_i2v"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"luma_i2v_{timestamp}_{unique_id}.mp4"
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
__all__ = ["LumaI2VTool"]
