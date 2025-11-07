"""
Luma Ray Text-to-Video Tool

Generates videos from text prompts with smooth, realistic motion.
Known for high-quality physics and natural movement.
Best for: Premium quality, creative freedom, realistic scenes.
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

class LumaT2VTool(BaseTool):
    """
    Tool for generating videos from text using Luma Ray (Text-to-Video mode).
    
    Luma Ray (Dream Machine) is known for:
    - Smooth, realistic motion
    - High-quality physics simulation
    - Natural-looking animations
    - Premium quality output
    
    Use cases:
    - Premium quality video generation
    - Realistic scenes without existing images
    - Creative content with natural physics
    - High-end commercial content
    
    Cost: $0.45 per 5-second video
    Time: ~38 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="luma_t2v",
            description="Generate videos from text prompts with premium smooth motion (Text-to-Video mode)"
        )
        # Set Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = "luma/ray"
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Required:
            - prompt: Text description of desired video
        """
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from text prompt using Luma Ray (T2V mode).
        
        Args:
            input_data: Must contain:
                - prompt: Text description of desired video
                - aspect_ratio: Optional ("1:1", "3:4", "4:3", "9:16", "16:9", "9:21", "21:9", default: "16:9")
                - loop: Optional boolean for seamless loop (default: False)
                - output_dir: Optional custom output directory
                
        Returns:
            Dictionary with video file path and metadata
        """
        prompt = input_data["prompt"]
        aspect_ratio = input_data.get("aspect_ratio", "16:9")
        loop = input_data.get("loop", False)
        output_dir = input_data.get("output_dir")
        
        self.logger.info(f"Generating video from text (Luma T2V mode)")
        self.logger.info(f"Prompt: {prompt[:100]}...")
        self.logger.info(f"Aspect ratio: {aspect_ratio}")
        self.logger.info(f"Loop: {loop}")
        
        # Run Luma Ray model in T2V mode (no image input)
        self.logger.info("Running Luma Ray T2V model (this may take 30-60 seconds)...")
        
        output = self.client.run(
            self.model,
            input={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "loop": loop,
                # NO start_image parameter = T2V mode
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
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop,
            "duration": 5,  # Luma generates 5-second videos
            "mode": "text_to_video",
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
            save_dir = Path("output") / "luma_t2v"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"luma_t2v_{timestamp}_{unique_id}.mp4"
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
__all__ = ["LumaT2VTool"]
