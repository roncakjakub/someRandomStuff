"""
Pika Labs Video Tool (via fal.ai)

Image-to-video generation with smooth morphs and creative effects using Pika v2.2.
Best for dynamic transitions, morphs between states, and creative video effects.
UPDATED: Now supports morph mode with dual images (start_image + end_image)
"""

import os
import time
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool

class PikaVideoTool(BaseTool):
    """
    Tool for converting images to videos using Pika v2.2 via fal.ai.
    
    Uses fal.ai's Pika API for image-to-video generation.
    
    Supports two modes:
    1. Single image animation (image_path)
    2. Dual image morph (start_image + end_image)
    
    Cost: ~$0.15-0.20 per video
    Time: ~60-120 seconds per generation
    """
    
    def __init__(self):
        super().__init__(
            name="pika_video",
            description="Convert images to videos with smooth morphs and creative effects using Pika v2.2"
        )
        
        # Get API key from environment
        self.api_key = os.getenv("FAL_KEY")
        if not self.api_key:
            self.logger.warning("FAL_KEY not found in environment variables")
        
        self.base_url = "https://queue.fal.run"
        self.model = "fal-ai/pika/v2.2/image-to-video"
        
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input parameters.
        
        Supports two modes:
        1. Single image: image_path + prompt
        2. Morph mode: start_image + end_image + prompt
        """
        if not self.api_key:
            return False, "FAL_KEY not set in environment variables"
        
        # Check for morph mode (dual images)
        has_morph_images = "start_image" in input_data and "end_image" in input_data
        has_single_image = "image_path" in input_data
        
        if not has_morph_images and not has_single_image:
            return False, "Missing required field: either 'image_path' OR ('start_image' AND 'end_image')"
        
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
        
        # Validate file existence
        if has_morph_images:
            if not os.path.exists(input_data["start_image"]):
                return False, f"Start image file not found: {input_data['start_image']}"
            if not os.path.exists(input_data["end_image"]):
                return False, f"End image file not found: {input_data['end_image']}"
        elif has_single_image:
            if not os.path.exists(input_data["image_path"]):
                return False, f"Image file not found: {input_data['image_path']}"
        
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video from image(s) using Pika v2.2.
        
        Args:
            input_data: Must contain EITHER:
                MODE 1 - Single image animation:
                    - image_path: Path to input image
                    - prompt: Text description of desired motion
                
                MODE 2 - Dual image morph:
                    - start_image: Path to start image
                    - end_image: Path to end image
                    - prompt: Text description of transition
                
                Optional for both modes:
                    - output_dir: Custom output directory
                    - duration: Video duration (default: 5)
                    - resolution: Resolution (default: "720p")
                    - negative_prompt: Negative prompt
                    - filename: Custom output filename
                
        Returns:
            Dictionary with video file path and metadata
        """
        # Detect mode
        is_morph_mode = "start_image" in input_data and "end_image" in input_data
        
        prompt = input_data["prompt"]
        output_dir = input_data.get("output_dir")
        duration = input_data.get("duration", 5)
        resolution = input_data.get("resolution", "720p")
        negative_prompt = input_data.get("negative_prompt", "")
        custom_filename = input_data.get("filename")
        
        if is_morph_mode:
            # MORPH MODE: Two images
            start_image_path = input_data["start_image"]
            end_image_path = input_data["end_image"]
            
            self.logger.info(f"🎬 MORPH MODE: Creating transition between two images")
            self.logger.info(f"  Start image: {start_image_path}")
            self.logger.info(f"  End image: {end_image_path}")
            self.logger.info(f"  Motion prompt: {prompt[:100]}...")
            self.logger.info(f"  Settings: duration={duration}s, resolution={resolution}")
            
            # Step 1: Upload both images
            start_url = self._upload_image(start_image_path)
            self.logger.info(f"  Start image uploaded: {start_url}")
            
            end_url = self._upload_image(end_image_path)
            self.logger.info(f"  End image uploaded: {end_url}")
            
            # Step 2: Submit morph request
            request_id = self._submit_morph_request(
                start_url, end_url, prompt, duration, resolution, negative_prompt
            )
            self.logger.info(f"  Morph request submitted: {request_id}")
            
            # Step 3: Wait for completion
            self.logger.info("  Waiting for morph generation (60-120 seconds)...")
            video_url = self._wait_for_completion(request_id)
            self.logger.info(f"  Morph video generated: {video_url}")
            
            # Step 4: Download
            video_path = self._download_video(video_url, output_dir, custom_filename)
            self.logger.info(f"  ✓ Morph video saved: {video_path}")
            
            return {
                "video_path": video_path,
                "video_url": video_url,
                "start_image": start_image_path,
                "end_image": end_image_path,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "model": self.model,
                "mode": "morph",
                "cost_estimate": 0.15,
            }
            
        else:
            # SINGLE IMAGE MODE: One image
            image_path = input_data["image_path"]
            
            self.logger.info(f"🎬 SINGLE IMAGE MODE: Animating image")
            self.logger.info(f"  Image: {image_path}")
            self.logger.info(f"  Motion prompt: {prompt[:100]}...")
            self.logger.info(f"  Settings: duration={duration}s, resolution={resolution}")
            
            # Step 1: Upload image
            image_url = self._upload_image(image_path)
            self.logger.info(f"  Image uploaded: {image_url}")
            
            # Step 2: Submit request
            request_id = self._submit_request(
                image_url, prompt, duration, resolution, negative_prompt
            )
            self.logger.info(f"  Request submitted: {request_id}")
            
            # Step 3: Wait for completion
            self.logger.info("  Waiting for video generation (60-120 seconds)...")
            video_url = self._wait_for_completion(request_id)
            self.logger.info(f"  Video generated: {video_url}")
            
            # Step 4: Download
            video_path = self._download_video(video_url, output_dir, custom_filename)
            self.logger.info(f"  ✓ Video saved: {video_path}")
            
            return {
                "video_path": video_path,
                "video_url": video_url,
                "source_image": image_path,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "model": self.model,
                "mode": "single_image",
                "cost_estimate": 0.15,
            }
    
    def _upload_image(self, image_path: str) -> str:
        """Upload image to fal.ai storage and get URL."""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }
        
        # Read image file
        with open(image_path, "rb") as f:
            files = {"file": f}
            
            response = requests.post(
                "https://fal.run/storage/upload",
                headers=headers,
                files=files,
            )
            response.raise_for_status()
        
        result = response.json()
        return result["url"]
    
    def _submit_request(self, image_url: str, prompt: str, duration: int, 
                       resolution: str, negative_prompt: str) -> str:
        """Submit single-image video generation request to fal.ai queue."""
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": "9:16",  # Force vertical format for social media
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        self.logger.debug(f"Submitting request with payload: {payload}")
        
        response = requests.post(
            f"{self.base_url}/{self.model}",
            headers=headers,
            json=payload,
        )
        
        if response.status_code != 200:
            self.logger.error(f"API Error {response.status_code}: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        return result["request_id"]
    
    def _submit_morph_request(self, start_url: str, end_url: str, prompt: str, 
                             duration: int, resolution: str, negative_prompt: str) -> str:
        """Submit dual-image morph request to fal.ai queue."""
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "image_url": start_url,
            "end_image_url": end_url,  # End image for morph
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": "9:16",  # Force vertical format for social media
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        self.logger.debug(f"Submitting morph request with payload: {payload}")
        
        response = requests.post(
            f"{self.base_url}/{self.model}",
            headers=headers,
            json=payload,
        )
        
        if response.status_code != 200:
            self.logger.error(f"API Error {response.status_code}: {response.text}")
        
        response.raise_for_status()
        
        result = response.json()
        return result["request_id"]
    
    def _wait_for_completion(self, request_id: str, max_wait: int = 300) -> str:
        """Poll request status until completion."""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }
        
        status_url = f"{self.base_url}/{self.model}/requests/{request_id}/status"
        start_time = time.time()
        
        while True:
            # Check if max wait time exceeded
            if time.time() - start_time > max_wait:
                raise TimeoutError(f"Video generation timed out after {max_wait} seconds")
            
            # Get request status
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            status = result["status"]
            
            if status == "COMPLETED":
                # Get the result
                result_url = f"{self.base_url}/{self.model}/requests/{request_id}"
                result_response = requests.get(result_url, headers=headers)
                result_response.raise_for_status()
                
                result_data = result_response.json()
                self.logger.debug(f"Result data structure: {result_data.keys()}")
                
                # Handle queue API response structure (has "data" wrapper)
                if "data" in result_data:
                    video_data = result_data["data"]
                else:
                    video_data = result_data
                
                # Extract video URL
                if "video" in video_data and "url" in video_data["video"]:
                    return video_data["video"]["url"]
                else:
                    self.logger.error(f"Unexpected response structure: {result_data}")
                    raise RuntimeError(f"Could not find video URL in response: {result_data}")
                
            elif status == "FAILED":
                error = result.get("error", "Unknown error")
                raise RuntimeError(f"Video generation failed: {error}")
            
            # Still processing, wait and retry
            self.logger.debug(f"Request status: {status}, waiting...")
            time.sleep(5)
    
    def _download_video(self, video_url: str, output_dir: Optional[str] = None, 
                       custom_filename: Optional[str] = None) -> str:
        """Download video from URL and save to disk."""
        from datetime import datetime
        import uuid
        
        # Determine output directory
        if output_dir:
            save_dir = Path(output_dir)
        else:
            save_dir = Path("output") / "pika_videos"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"pika_{timestamp}_{unique_id}.mp4"
        
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
__all__ = ["PikaVideoTool"]
