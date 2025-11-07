"""
Apiframe Midjourney Tool
Generates cinematic opening frames using Midjourney via Apiframe API
"""

import sys
from pathlib import Path
import requests
import time
import uuid
from typing import Dict, Any, Optional

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import APIFRAME_API_KEY, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import APIFRAME_API_KEY, OUTPUT_DIR

import logging
logger = logging.getLogger(__name__)


class ApiframeMidjourneyTool(BaseTool):
    """
    Tool for generating cinematic images using Midjourney via Apiframe API.
    Best for opening frames and hero shots.
    """
    
    def __init__(self):
        super().__init__(
            name="apiframe_midjourney",
            description="Generate cinematic images using Midjourney via Apiframe API"
        )
        self.api_key = APIFRAME_API_KEY
        self.base_url = "https://api.apiframe.ai/pro"
        
        if not self.api_key:
            raise ValueError("APIFRAME_API_KEY not found in environment variables")
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input data."""
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
        if not input_data["prompt"]:
            return False, "Prompt cannot be empty"
        return True, None
    
    @retry_on_error(max_retries=3, delay=5)
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate image using Midjourney via Apiframe.
        
        Args:
            input_data: {
                "prompt": str,  # Image generation prompt
                "aspect_ratio": str,  # e.g., "9:16" for vertical
                "output_dir": str,  # Optional custom output directory
            }
        
        Returns:
            {
                "success": bool,
                "image_path": str,
                "prompt": str,
                "model": "midjourney"
            }
        """
        prompt = input_data.get("prompt", "")
        aspect_ratio = input_data.get("aspect_ratio", "9:16")
        output_dir = input_data.get("output_dir", OUTPUT_DIR)
        
        if not prompt:
            raise ValueError("Prompt is required")
        
        logger.info(f"Generating Midjourney image via Apiframe: {prompt[:100]}...")
        
        # Create generation request
        response = self._create_generation(prompt, aspect_ratio)
        
        # Poll for completion
        image_url = self._wait_for_completion(response["id"])
        
        # Download image
        image_path = self._download_image(image_url, output_dir)
        
        logger.info(f"✅ Midjourney image generated: {image_path}")
        
        return {
            "success": True,
            "image_path": image_path,
            "prompt": prompt,
            "model": "midjourney"
        }
    
    def _create_generation(self, prompt: str, aspect_ratio: str) -> Dict[str, Any]:
        """Create a new image generation request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Add --ar parameter to prompt (Midjourney native syntax)
        # Apiframe may not respect aspect_ratio in payload, so we add it to prompt
        if "--ar" not in prompt:
            prompt = f"{prompt} --ar {aspect_ratio}"
        
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,  # Keep for API compatibility
            "process_mode": "fast"  # or "relax" for cheaper
        }
        
        response = requests.post(
            f"{self.base_url}/imagine",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Apiframe API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Check if response contains task ID
        if "id" not in result and "task_id" not in result:
            raise Exception(f"Apiframe API response missing task ID: {result}")
        
        # Normalize response to always have 'id' field
        if "task_id" in result and "id" not in result:
            result["id"] = result["task_id"]
        
        return result
    
    def _wait_for_completion(self, task_id: str, max_wait: int = 600) -> str:
        """Poll for generation completion and return image URL."""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.post(
                "https://api.apiframe.pro/fetch",
                headers=headers,
                json={"task_id": task_id},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to check status: {response.status_code} - {response.text}")
            
            data = response.json()
            status = data.get("status")
            
            # Debug: Log full response to understand structure
            logger.debug(f"Apiframe response: {data}")
            
            if status == "finished" or status == "completed":
                # Return the first image URL from the result
                # Apiframe returns image_urls array directly, not nested in result
                images = data.get("image_urls", [])
                if images:
                    return images[0]
                raise Exception(f"No images in result. Response: {data}")
            elif status == "failed":
                raise Exception(f"Generation failed: {data.get('error')}")
            
            elapsed = int(time.time() - start_time)
            logger.info(f"Midjourney status: {status} (elapsed: {elapsed}s / {max_wait}s)")
            print(f"⏳ Status: {status} | Elapsed: {elapsed}s / {max_wait}s")  # User feedback
            time.sleep(10)  # Poll every 10 seconds
        
        raise TimeoutError(f"Generation timed out after {max_wait} seconds")
    
    def _download_image(self, url: str, output_dir: str) -> str:
        """Download image from URL and save to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:8]
        filename = f"midjourney_{timestamp}_{random_id}.png"
        filepath = output_path / filename
        
        # Download image
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: {response.status_code}")
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return str(filepath)


# Test code
if __name__ == "__main__":
    print("Testing Apiframe Midjourney Tool...")
    
    tool = ApiframeMidjourneyTool()
    
    result = tool.run({
        "prompt": "cinematic establishing shot of a cozy coffee shop, morning golden hour, 35mm film, shallow depth of field, professional color grading, warm tones, film grain",
        "aspect_ratio": "9:16"
    })
    
    print(f"\n✅ Test Result:")
    print(f"Success: {result.get('success')}")
    print(f"Image: {result.get('image_path')}")
    print(f"Model: {result.get('model')}")
