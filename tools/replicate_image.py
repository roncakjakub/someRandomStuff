"""
Replicate Image Generation Tool for creating visual content.
"""
from typing import Dict, Any, Optional, List
import replicate
from pathlib import Path
import requests
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(PathLib(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import REPLICATE_API_TOKEN, REPLICATE_MODELS, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import REPLICATE_API_TOKEN, REPLICATE_MODELS, OUTPUT_DIR


class ReplicateImageTool(BaseTool):
    """
    Tool for generating images using Replicate API (Flux, SDXL, etc.).
    """
    
    def __init__(self, model_name: str = "flux_schnell"):
        super().__init__(
            name=f"replicate_{model_name}",
            description=f"Generate images using {model_name} model via Replicate"
        )
        self.model_name = model_name
        self.model_id = REPLICATE_MODELS.get(model_name)
        if not self.model_id:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Set API token
        import os
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that prompt is provided."""
        if "prompt" not in input_data:
            return False, "Missing required field: prompt"
        if not isinstance(input_data["prompt"], str):
            return False, "Prompt must be a string"
        if len(input_data["prompt"].strip()) == 0:
            return False, "Prompt cannot be empty"
        return True, None
    
    @retry_on_error(max_retries=3, delay=10)
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate image using Replicate API.
        
        Args:
            input_data: Must contain 'prompt' field, optional 'image' for img2img, 'output_dir' for custom output
            
        Returns:
            Dictionary with generated image path
        """
        prompt = input_data["prompt"]
        aspect_ratio = input_data.get("aspect_ratio", "9:16")  # Vertical for social media
        num_outputs = input_data.get("num_outputs", 1)
        reference_image = input_data.get("image")  # For ControlNet/img2img
        output_dir = input_data.get("output_dir")  # Custom output directory
        
        self.logger.info(f"Generating image with {self.model_name}: {prompt[:50]}...")
        
        # Prepare input based on model
        model_input = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "num_outputs": num_outputs,
            "output_format": "png",
            "output_quality": 90,
        }
        
        # Add model-specific parameters
        if "schnell" in self.model_name:
            # Flux Schnell: Fast model, max 4 steps
            model_input["go_fast"] = True
            model_input["num_inference_steps"] = 4
        elif "dev" in self.model_name:
            # Flux Dev: Balanced model, 28-50 steps recommended
            model_input["num_inference_steps"] = 28
            model_input["guidance"] = 3.5
        elif "pro" in self.model_name:
            # Flux Pro: Premium model, has different parameters
            model_input["num_inference_steps"] = 25
            model_input["guidance"] = 3
        
        # Add reference image if provided (for ControlNet)
        if reference_image:
            model_input["image"] = reference_image
            model_input["prompt_strength"] = 0.8
        
        # Run the model
        output = replicate.run(
            self.model_id,
            input=model_input
        )
        
        # Download and save images
        image_paths = []
        for idx, image_url in enumerate(output):
            image_path = self._download_image(image_url, idx, output_dir)
            image_paths.append(str(image_path))
        
        self.logger.info(f"Generated {len(image_paths)} image(s)")
        
        return {
            "images": image_paths,
            "prompt": prompt,
            "model": self.model_name,
        }
    
    def _download_image(self, url: str, index: int = 0, output_dir: str = None) -> Path:
        """
        Download image from URL and save to output directory.
        
        Args:
            url: Image URL
            index: Image index for naming
            output_dir: Custom output directory (uses OUTPUT_DIR if not provided)
            
        Returns:
            Path to saved image
        """
        import uuid
        from datetime import datetime
        
        # Use provided output_dir or fallback to OUTPUT_DIR
        target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{self.model_name}_{timestamp}_{unique_id}_{index}.png"
        filepath = target_dir / filename
        
        # Download image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save image
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        self.logger.info(f"Saved image to {filepath}")
        return filepath
    
    def generate_opening_frame(self, prompt: str) -> Dict[str, Any]:
        """
        Generate cinematic opening frame.
        
        Args:
            prompt: Detailed prompt for the opening frame
            
        Returns:
            Generation result
        """
        enhanced_prompt = f"Cinematic shot, 9:16 vertical format, {prompt}. Hyper-realistic, film grain, professional photography, high quality."
        return self.run({"prompt": enhanced_prompt, "aspect_ratio": "9:16"})
    
    def generate_sequence(self, base_prompt: str, scene_descriptions: List[str]) -> Dict[str, Any]:
        """
        Generate sequence of images with consistent style.
        
        Args:
            base_prompt: Base style description
            scene_descriptions: List of scene descriptions
            
        Returns:
            Generation results for all scenes
        """
        results = []
        for idx, scene_desc in enumerate(scene_descriptions):
            full_prompt = f"{base_prompt}. Scene {idx + 1}: {scene_desc}"
            result = self.run({"prompt": full_prompt, "aspect_ratio": "9:16"})
            if result.get("success"):
                results.extend(result.get("images", []))
        
        return {
            "images": results,
            "base_prompt": base_prompt,
            "num_scenes": len(scene_descriptions),
        }


class FluxProTool(ReplicateImageTool):
    """Flux Pro model - highest quality."""
    def __init__(self):
        super().__init__(model_name="flux_pro")


class FluxDevTool(ReplicateImageTool):
    """Flux Dev model - good balance of quality and speed."""
    def __init__(self):
        super().__init__(model_name="flux_dev")


class FluxSchnellTool(ReplicateImageTool):
    """Flux Schnell model - fastest generation."""
    def __init__(self):
        super().__init__(model_name="flux_schnell")


if __name__ == "__main__":
    # Test the tool
    tool = FluxSchnellTool()
    result = tool.generate_opening_frame(
        "a person's hands gently pouring hot water over coffee grounds in a V60 dripper. Steam is rising. Morning light streams through a window."
    )
    print(result)
