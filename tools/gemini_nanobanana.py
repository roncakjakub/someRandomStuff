"""
Gemini Nano Banana Tool
Face restoration, image editing, and enhancement using Google Gemini 2.5 Flash
"""

import sys
from pathlib import Path
import google.generativeai as genai
import time
import uuid
from typing import Dict, Any, Optional
from PIL import Image

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import GOOGLE_API_KEY, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import GOOGLE_API_KEY, OUTPUT_DIR

import logging
logger = logging.getLogger(__name__)


class GeminiNanoBananaTool(BaseTool):
    """
    Tool for face restoration and image editing using Google Gemini (Nano Banana).
    Perfect for fixing faces, blending scenes, and changing backgrounds.
    """
    
    def __init__(self):
        super().__init__(
            name="gemini_nanobanana",
            description="Face restoration and image editing using Google Gemini"
        )
        self.api_key = GOOGLE_API_KEY
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input data."""
        if "image_path" not in input_data:
            return False, "Missing required field: image_path"
        if not input_data["image_path"]:
            return False, "image_path cannot be empty"
        return True, None
    
    @retry_on_error(max_retries=3, delay=5)
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit/enhance image using Gemini Nano Banana.
        
        Args:
            input_data: {
                "image_path": str,  # Path to input image
                "edit_prompt": str,  # What to edit (e.g., "fix the face", "change background to sunset")
                "output_dir": str,  # Optional custom output directory
            }
        
        Returns:
            {
                "success": bool,
                "image_path": str,
                "edit_prompt": str,
                "model": "gemini_nanobanana"
            }
        """
        image_path = input_data.get("image_path", "")
        edit_prompt = input_data.get("edit_prompt", "enhance and fix any face issues")
        output_dir = input_data.get("output_dir", OUTPUT_DIR)
        
        if not image_path:
            raise ValueError("image_path is required")
        
        logger.info(f"Editing image with Gemini Nano Banana: {edit_prompt}")
        
        # Load image
        image = Image.open(image_path)
        
        # Create edit prompt
        full_prompt = f"Edit this image: {edit_prompt}. Maintain the overall composition and style. Only modify what was requested."
        
        # Generate edited image
        response = self.model.generate_content([full_prompt, image])
        
        # Check if response contains image
        if not response.parts:
            raise Exception("No image generated in response")
        
        # Save edited image
        output_path = self._save_image(response, output_dir)
        
        logger.info(f"✅ Image edited with Nano Banana: {output_path}")
        
        return {
            "success": True,
            "image_path": output_path,
            "edit_prompt": edit_prompt,
            "model": "gemini_nanobanana"
        }
    
    def _save_image(self, response, output_dir: str) -> str:
        """Save generated image to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:8]
        filename = f"nanobanana_{timestamp}_{random_id}.png"
        filepath = output_path / filename
        
        # Extract image from response
        # Note: Gemini API may return image in different formats
        # This is a simplified version - may need adjustment based on actual API response
        for part in response.parts:
            if hasattr(part, 'inline_data'):
                image_data = part.inline_data.data
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                return str(filepath)
        
        raise Exception("No image data found in response")


# Test code
if __name__ == "__main__":
    print("Testing Gemini Nano Banana Tool...")
    print("Note: This tool requires an existing image to edit.")
    print("Skipping test - use in workflow with generated images.")
    
    # Example usage:
    # tool = GeminiNanoBananaTool()
    # result = tool.run({
    #     "image_path": "/path/to/image.png",
    #     "edit_prompt": "fix the face and enhance details"
    # })
