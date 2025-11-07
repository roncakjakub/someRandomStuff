"""
Seedream 4 Tool (ByteDance)
Generates consistent character sequences across multiple images
"""

import sys
from pathlib import Path
import replicate
import time
import uuid
from typing import Dict, Any, List, Optional

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import REPLICATE_API_TOKEN, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import REPLICATE_API_TOKEN, OUTPUT_DIR

import logging
logger = logging.getLogger(__name__)


class Seedream4Tool(BaseTool):
    """
    Tool for generating character-consistent image sequences using Seedream 4.
    Perfect for maintaining character identity across multiple shots.
    """
    
    def __init__(self):
        super().__init__(
            name="seedream4",
            description="Generate character-consistent image sequences"
        )
        self.model_name = "bytedance/seedream-4"
        
        if not REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
    
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
        Generate character-consistent images using Seedream 4.
        
        Args:
            input_data: {
                "prompt": str,  # Main prompt
                "reference_image": str,  # Path or URL to reference image
                "num_outputs": int,  # Number of images to generate (1-15)
                "output_dir": str,  # Optional custom output directory
            }
        
        Returns:
            {
                "success": bool,
                "image_paths": List[str],
                "prompt": str,
                "model": "seedream4"
            }
        """
        prompt = input_data.get("prompt", "")
        reference_image = input_data.get("reference_image")
        num_outputs = input_data.get("num_outputs", 1)
        output_dir = input_data.get("output_dir", OUTPUT_DIR)
        
        if not prompt:
            raise ValueError("Prompt is required")
        
        logger.info(f"Generating {num_outputs} consistent images with Seedream 4...")
        
        # Prepare input
        model_input = {
            "prompt": prompt,
            "num_outputs": min(num_outputs, 15),  # Max 15
            "output_format": "png",
            "output_quality": 90,
        }
        
        # Add reference image if provided
        if reference_image:
            model_input["image"] = reference_image
            model_input["prompt_strength"] = 0.8  # How much to follow the reference
        
        # Run model
        logger.info(f"Running Seedream 4: {self.model_name}")
        output = replicate.run(
            self.model_name,
            input=model_input
        )
        
        # Download images
        image_paths = []
        for i, image_url in enumerate(output):
            image_path = self._download_image(image_url, output_dir, index=i)
            image_paths.append(image_path)
            logger.info(f"✅ Downloaded image {i+1}/{len(output)}: {image_path}")
        
        return {
            "success": True,
            "images": image_paths,  # Standard format
            "image_path": image_paths[0] if image_paths else None,  # Backward compatibility
            "image_paths": image_paths,  # Legacy format
            "prompt": prompt,
            "model": "seedream4",
            "num_generated": len(image_paths)
        }
    
    def _download_image(self, url: str, output_dir: str, index: int = 0) -> str:
        """Download image from URL and save to output directory."""
        import requests
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:8]
        filename = f"seedream4_{timestamp}_{random_id}_{index}.png"
        filepath = output_path / filename
        
        # Download image
        response = requests.get(str(url), timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: {response.status_code}")
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return str(filepath)


# Test code
if __name__ == "__main__":
    print("Testing Seedream 4 Tool...")
    
    tool = Seedream4Tool()
    
    result = tool.run({
        "prompt": "professional headshot of a young entrepreneur, confident expression, modern office background, natural lighting",
        "num_outputs": 3
    })
    
    print(f"\n✅ Test Result:")
    print(f"Success: {result.get('success')}")
    print(f"Generated: {result.get('num_generated')} images")
    print(f"Images: {result.get('image_paths')}")
