"""
Ideogram Tool
Generates images with readable, high-quality text and typography
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
    from config.settings import IDEOGRAM_API_KEY, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import IDEOGRAM_API_KEY, OUTPUT_DIR

import logging
logger = logging.getLogger(__name__)


class IdeogramTextTool(BaseTool):
    """
    Tool for generating images with readable text using Ideogram API.
    Perfect for text overlays, typography, and graphics.
    """
    
    def __init__(self):
        super().__init__(
            name="ideogram_text",
            description="Generate images with readable text and typography"
        )
        self.api_key = IDEOGRAM_API_KEY
        self.base_url = "https://api.ideogram.ai/v1/ideogram-v3"
        
        if not self.api_key:
            raise ValueError("IDEOGRAM_API_KEY not found in environment variables")
    
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
        Generate image with text using Ideogram.
        
        Args:
            input_data: {
                "prompt": str,  # Text and style description
                "aspect_ratio": str,  # e.g., "9:16" for vertical
                "model": str,  # "v3" or "v3-turbo" (default: "v3")
                "output_dir": str,  # Optional custom output directory
            }
        
        Returns:
            {
                "success": bool,
                "image_path": str,
                "prompt": str,
                "model": "ideogram"
            }
        """
        prompt = input_data.get("prompt", "")
        aspect_ratio = input_data.get("aspect_ratio", "9x16")  # Ideogram uses 'x' not ':'
        model = input_data.get("model", "v3")
        output_dir = input_data.get("output_dir", OUTPUT_DIR)
        
        if not prompt:
            raise ValueError("Prompt is required")
        
        logger.info(f"Generating text image with Ideogram: {prompt[:100]}...")
        
        # Create generation request
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "rendering_speed": "TURBO" if model == "v3-turbo" else "STANDARD",
            "magic_prompt_option": "AUTO"  # Enhance prompt automatically
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ideogram API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        # Get image URL
        if not data.get("data") or len(data["data"]) == 0:
            raise Exception("No images generated")
        
        image_url = data["data"][0].get("url")
        
        # Download image
        image_path = self._download_image(image_url, output_dir)
        
        logger.info(f"✅ Ideogram text image generated: {image_path}")
        
        return {
            "success": True,
            "image_path": image_path,
            "prompt": prompt,
            "model": "ideogram"
        }
    
    def _download_image(self, url: str, output_dir: str) -> str:
        """Download image from URL and save to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:8]
        filename = f"ideogram_{timestamp}_{random_id}.png"
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
    print("Testing Ideogram Text Tool...")
    
    tool = IdeogramTextTool()
    
    result = tool.run({
        "prompt": "Bold modern typography: 'GAME CHANGER' in white text on dark background, minimalist design, high contrast",
        "aspect_ratio": "9:16"
    })
    
    print(f"\n✅ Test Result:")
    print(f"Success: {result.get('success')}")
    print(f"Image: {result.get('image_path')}")
    print(f"Model: {result.get('model')}")
