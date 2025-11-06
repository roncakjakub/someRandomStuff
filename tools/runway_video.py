"""
Runway Gen-4 Turbo Video Tool

Fast and cost-effective image-to-video generation using Runway's Gen-4 Turbo model.
Best for universal video generation with good quality at low cost ($0.05/sec).
"""

import os
import time
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool

class RunwayVideoTool(BaseTool):
    """
    Tool for converting static images to videos using Runway Gen-4 Turbo.
    
    Uses Runway's official API for image-to-video generation.
    Cost: $0.05 per second ($0.25 for 5-second video)
    Time: ~60-90 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="runway_video",
            description="Convert static images to videos using Runway Gen-4 Turbo (fast, cheap, versatile)"
        )
        
        # Get API key from environment
        self.api_key = os.getenv("RUNWAY_API_KEY")
        if not self.api_key:
            self.logger.warning("RUNWAY_API_KEY not found in environment variables")
        
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.model = "gen4_turbo"
        self.api_version = "2024-11-06"  # Required API version
        
        # Map common aspect ratios to Runway's expected format
        self.ratio_map = {
            "16:9": "1280:720",
            "9:16": "720:1280",
            "4:3": "1104:832",
            "3:4": "832:1104",
            "1:1": "960:960",
        }
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Required:
            - image_path: Path to input image
            - prompt: Text description of desired motion/animation
        """
        if not self.api_key:
            return False, "RUNWAY_API_KEY not set in environment variables"
            
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
        Generate video from static image using Runway Gen-4 Turbo.
        
        Args:
            input_data: Must contain:
                - image_path: Path to input image
                - prompt: Text description of desired motion
                - output_dir: Optional custom output directory
                - duration: Optional video duration in seconds (default: 5)
                - ratio: Optional aspect ratio (default: "9:16" for vertical)
                
        Returns:
            Dictionary with video file path and metadata
        """
        image_path = input_data["image_path"]
        prompt = input_data["prompt"]
        output_dir = input_data.get("output_dir")
        duration = input_data.get("duration", 5)  # Default 5 seconds
        ratio = input_data.get("ratio", "9:16")  # Vertical for social media
        
        self.logger.info(f"Generating video from image: {image_path}")
        self.logger.info(f"Motion prompt: {prompt[:100]}...")
        self.logger.info(f"Settings: duration={duration}s, ratio={ratio}")
        
        # Step 1: Convert image to data URI (no upload needed)
        image_data_uri = self._image_to_data_uri(image_path)
        self.logger.info(f"Image converted to data URI")
        
        # Step 2: Create video generation task
        task_id = self._create_task(image_data_uri, prompt, duration, ratio)
        self.logger.info(f"Task created: {task_id}")
        
        # Step 3: Poll for completion
        self.logger.info("Waiting for video generation (this may take 60-90 seconds)...")
        video_url = self._wait_for_completion(task_id)
        self.logger.info(f"Video generated: {video_url}")
        
        # Step 4: Download the video
        video_path = self._download_video(video_url, output_dir)
        self.logger.info(f"Video saved to: {video_path}")
        
        return {
            "video_path": video_path,
            "video_url": video_url,
            "source_image": image_path,
            "prompt": prompt,
            "duration": duration,
            "ratio": ratio,
            "model": self.model,
            "cost_estimate": duration * 0.05,  # $0.05 per second
        }
    
    def _image_to_data_uri(self, image_path: str) -> str:
        """Convert local image to data URI for direct API use.
        
        Runway API accepts data URIs directly, no upload needed.
        Format: data:image/jpeg;base64,<base64_data>
        """
        import base64
        from pathlib import Path
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Detect image format from extension
        ext = Path(image_path).suffix.lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
        }.get(ext, 'image/jpeg')
        
        # Encode to base64
        b64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Create data URI
        data_uri = f"data:{mime_type};base64,{b64_data}"
        
        self.logger.debug(f"Converted image to data URI: {len(b64_data)} bytes")
        return data_uri
    
    def _create_task(self, image_data_uri: str, prompt: str, duration: int, ratio: str) -> str:
        """Create video generation task."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": self.api_version,  # Required header
        }
        
        # Convert ratio to Runway's expected format
        runway_ratio = self.ratio_map.get(ratio, "720:1280")  # Default to 9:16
        
        payload = {
            "model": self.model,
            "promptImage": image_data_uri,  # Data URI or HTTPS URL
            "promptText": prompt,
            "duration": duration,
            "ratio": runway_ratio,
            "position": "first",  # Required: image position in video
        }
        
        self.logger.debug(f"Creating task with payload: {payload}")
        
        response = requests.post(
            f"{self.base_url}/image_to_video",  # Correct endpoint
            headers=headers,
            json=payload,
        )
        
        # Log response for debugging
        if response.status_code != 200:
            self.logger.error(f"API Error {response.status_code}: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        return result["id"]
    
    def _wait_for_completion(self, task_id: str, max_wait: int = 300) -> str:
        """Poll task status until completion."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Runway-Version": self.api_version,  # Required header
        }
        
        start_time = time.time()
        
        while True:
            # Check if max wait time exceeded
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Video generation timed out after {max_wait} seconds")
            
            # Get task status
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers,
            )
            response.raise_for_status()
            
            result = response.json()
            status = result["status"]
            
            if status == "SUCCEEDED":
                # Return video URL
                return result["output"][0]
            elif status == "FAILED":
                error = result.get("failure", "Unknown error")
                raise RuntimeError(f"Video generation failed: {error}")
            
            # Still processing, wait and retry
            self.logger.debug(f"Task status: {status}, waiting...")
            time.sleep(5)
    
    def _download_video(self, video_url: str, output_dir: Optional[str] = None) -> str:
        """Download video from URL and save to disk."""
        from datetime import datetime
        import uuid
        
        # Determine output directory
        if output_dir:
            save_dir = Path(output_dir)
        else:
            save_dir = Path("output") / "runway_videos"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"runway_{timestamp}_{unique_id}.mp4"
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
__all__ = ["RunwayVideoTool"]
