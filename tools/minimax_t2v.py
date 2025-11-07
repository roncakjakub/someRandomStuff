"""
Minimax Hailuo 2.3 Text-to-Video Tool

Generates videos from text prompts without requiring an input image.
Default aspect ratio: 16:9 (horizontal).
Best for: General scenes, establishing shots, creative freedom.
"""

import os
import replicate
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool
from config.settings import REPLICATE_API_TOKEN

class MinimaxT2VTool(BaseTool):
    """
    Tool for generating videos from text using Minimax Hailuo 2.3 (Text-to-Video mode).
    
    This tool generates videos from scratch based on text prompts only.
    No input image required. Default aspect ratio is 16:9.
    
    Use cases:
    - General scene generation
    - Establishing shots
    - Creative content without existing images
    - Quick video generation
    
    Cost: $0.28 per 6-second video (768p)
    Time: ~70 seconds per generation (faster than I2V)
    """
    
    def __init__(self):
        super().__init__(
            name="minimax_t2v",
            description="Generate videos from text prompts (Text-to-Video mode)"
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
            - prompt: Text description of desired video
        """
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from text prompt using Minimax Hailuo 2.3 (T2V mode).
        
        Args:
            input_data: Must contain:
                - prompt: Text description of desired video
                - duration: Optional (6 or 10 seconds, default: 6)
                - resolution: Optional ("768p" or "1080p", default: "768p")
                - output_dir: Optional custom output directory
                - fast_mode: Optional boolean to use fast model (default: False)
                
        Returns:
            Dictionary with video file path and metadata
        """
        prompt = input_data["prompt"]
        duration = input_data.get("duration", 6)
        resolution = input_data.get("resolution", "768p")
        output_dir = input_data.get("output_dir")
        fast_mode = input_data.get("fast_mode", False)
        
        # Select model
        model = self.model_fast if fast_mode else self.model
        
        self.logger.info(f"Generating video from text (T2V mode)")
        self.logger.info(f"Prompt: {prompt[:100]}...")
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Duration: {duration}s, Resolution: {resolution}")
        
        # Run Minimax Hailuo model in T2V mode (no image input)
        self.logger.info("Running Minimax Hailuo T2V model (this may take 1-2 minutes)...")
        
        output = self.client.run(
            model,
            input={
                "prompt": prompt,
                # NO first_frame_image parameter = T2V mode
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
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "mode": "text_to_video",
            "aspect_ratio": "16:9",  # T2V defaults to 16:9
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
            save_dir = Path("output") / "minimax_t2v"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"minimax_t2v_{timestamp}_{unique_id}.mp4"
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
__all__ = ["MinimaxT2VTool"]
