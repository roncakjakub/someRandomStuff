"""
Pika Video Tool - v2 (fal_client SDK)

Generates videos from images using Pika v2.2 via fal.ai API.
Supports both single-image and dual-image (morph) transitions.
"""

import os
import logging
import fal_client
from typing import Dict, Any, Optional


class PikaVideoTool:
    """Tool for generating videos using Pika v2.2 via fal.ai."""
    
    def __init__(self):
        """Initialize Pika video tool."""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("FAL_KEY")
        
        if not self.api_key:
            raise ValueError("FAL_KEY environment variable not set")
        
        # Set fal_client API key
        os.environ["FAL_KEY"] = self.api_key
        
        self.model = "fal-ai/pika/v2.2/image-to-video"
        self.logger.info(f"Initialized Pika video tool with model: {self.model}")
    
    def execute(self, image_path: str = None, image_url: str = None,
                end_image_path: str = None, end_image_url: str = None,
                prompt: str = "", duration: int = 3, resolution: str = "720p",
                negative_prompt: str = None, output_path: str = None) -> Dict[str, Any]:
        """
        Generate video from image(s) using Pika v2.2.
        
        Args:
            image_path: Path to start image file (will be uploaded)
            image_url: URL to start image (if already uploaded)
            end_image_path: Path to end image for morph (optional)
            end_image_url: URL to end image for morph (optional)
            prompt: Text prompt for video generation
            duration: Video duration in seconds (1-5)
            resolution: Video resolution (720p or 1080p)
            negative_prompt: Negative prompt (optional)
            output_path: Path to save output video (optional)
        
        Returns:
            Dict with video_url and metadata
        """
        try:
            # Upload start image if path provided
            if image_path and not image_url:
                self.logger.info(f"Uploading start image: {image_path}")
                image_url = fal_client.upload_file(image_path)
                self.logger.info(f"Start image uploaded: {image_url}")
            
            if not image_url:
                raise ValueError("Either image_path or image_url must be provided")
            
            # Upload end image if path provided (for morph)
            if end_image_path and not end_image_url:
                self.logger.info(f"Uploading end image: {end_image_path}")
                end_image_url = fal_client.upload_file(end_image_path)
                self.logger.info(f"End image uploaded: {end_image_url}")
            
            # Prepare arguments
            arguments = {
                "image_url": image_url,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": "9:16",  # Force vertical for social media
            }
            
            # Add end image for morph transition
            if end_image_url:
                arguments["end_image_url"] = end_image_url
                self.logger.info("Morph mode: dual-image transition")
            
            # Add negative prompt if provided
            if negative_prompt:
                arguments["negative_prompt"] = negative_prompt
            
            self.logger.info(f"Submitting Pika request with arguments: {arguments}")
            
            # Submit request and wait for result (fal_client handles queue)
            result = fal_client.subscribe(
                self.model,
                arguments=arguments,
                with_logs=True,
            )
            
            self.logger.info(f"Pika video generated successfully")
            
            # Extract video URL from result
            video_url = result.get("video", {}).get("url")
            
            if not video_url:
                raise ValueError(f"No video URL in result: {result}")
            
            self.logger.info(f"Video URL: {video_url}")
            
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
                "mode": "morph" if end_image_url else "single",
            }
        
        except Exception as e:
            self.logger.error(f"Error in pika_video: {e}", exc_info=True)
            raise
