"""
Instant Character Tool
High-quality, consistent character generation with strong identity control
"""

import fal_client
from typing import Dict, Any, Optional, List
import os


class InstantCharacterTool:
    """
    Generate consistent characters from text prompts with reference image support.
    
    Best for:
    - Same person across multiple scenes
    - Diverse poses, styles, and appearances
    - Strong identity control (no multiple persons bug!)
    - Human portraits and actions
    """
    
    def __init__(self):
        self.model_id = "fal-ai/instant-character"
        self.cost_per_image = 0.04  # Estimated based on similar models
        
    def execute(
        self,
        prompt: str,
        reference_image_url: Optional[str] = None,
        image_size: str = "landscape_16_9",
        scale: float = 1.0,
        negative_prompt: str = "",
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
        seed: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image with consistent character.
        
        Args:
            prompt: Description of the scene/action
            reference_image_url: Optional reference image for character consistency
                                If None, generates new character from prompt
            image_size: Size preset or custom dimensions
                       Options: "square_hd", "square", "portrait_4_3", "portrait_16_9",
                               "landscape_4_3", "landscape_16_9"
                       Or dict: {"width": 1280, "height": 720}
            scale: Character prominence (0.0-2.0, default: 1.0)
                  Higher = more prominent reference character
            negative_prompt: What to avoid in the image
            guidance_scale: Prompt adherence (default: 3.5)
            num_inference_steps: Quality vs speed (default: 28)
            seed: Optional seed for reproducibility
            output_path: Optional path to save the image
            
        Returns:
            Dict with image URL, cost, and metadata
        """
        
        # Validate inputs
        if not prompt:
            raise ValueError("Prompt is required")
        
        # Prepare request
        request_data = {
            "prompt": prompt,
            "image_size": image_size,
            "scale": scale,
            "negative_prompt": negative_prompt,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "enable_safety_checker": True,
            "output_format": "jpeg"
        }
        
        # Add reference image if provided
        if reference_image_url:
            request_data["image_url"] = reference_image_url
            print(f"🎨 Generating with character reference...")
            print(f"   Reference: {reference_image_url}")
        else:
            print(f"🎨 Generating new character...")
        
        print(f"   Prompt: {prompt}")
        print(f"   Size: {image_size}, Scale: {scale}")
        
        # Add seed if provided
        if seed is not None:
            request_data["seed"] = seed
        
        # Call fal.ai API
        try:
            result = fal_client.subscribe(
                self.model_id,
                arguments=request_data
            )
            
            # Extract image URL
            images = result.get("images", [])
            if not images:
                raise ValueError("No images in response")
            
            image_data = images[0]
            image_url = image_data.get("url")
            
            if not image_url:
                raise ValueError("No image URL in response")
            
            # Get actual seed used
            actual_seed = result.get("seed")
            
            # Download image if output path specified
            if output_path:
                import requests
                response = requests.get(image_url)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Image saved to: {output_path}")
            
            print(f"✅ Character image generated!")
            print(f"   Cost: ${self.cost_per_image:.2f}")
            print(f"   Seed: {actual_seed}")
            print(f"   URL: {image_url}")
            
            return {
                "image_url": image_url,
                "width": image_data.get("width"),
                "height": image_data.get("height"),
                "cost": self.cost_per_image,
                "seed": actual_seed,
                "model": self.model_id,
                "has_reference": reference_image_url is not None,
                "local_path": output_path if output_path else None
            }
            
        except Exception as e:
            print(f"❌ Instant Character generation failed: {str(e)}")
            raise
    
    def generate_character_series(
        self,
        base_prompt: str,
        scene_prompts: List[str],
        output_dir: str,
        image_size: str = "landscape_16_9",
        scale: float = 1.0,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a series of images with the same character across different scenes.
        
        Args:
            base_prompt: Base character description (e.g., "25-year-old woman with long brown hair")
            scene_prompts: List of scene descriptions (e.g., ["in bedroom", "in kitchen"])
            output_dir: Directory to save images
            image_size: Image size preset
            scale: Character prominence
            seed: Optional seed for consistency
            
        Returns:
            List of result dicts for each generated image
        """
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        reference_image_url = None
        
        for i, scene_prompt in enumerate(scene_prompts):
            # Combine base prompt with scene
            full_prompt = f"{base_prompt}, {scene_prompt}"
            
            # Generate image
            output_path = os.path.join(output_dir, f"scene_{i+1:02d}.jpg")
            
            result = self.execute(
                prompt=full_prompt,
                reference_image_url=reference_image_url,
                image_size=image_size,
                scale=scale,
                seed=seed,
                output_path=output_path
            )
            
            # Use first image as reference for subsequent images
            if i == 0:
                reference_image_url = result["image_url"]
                print(f"📌 Using scene 1 as character reference for remaining scenes")
            
            results.append(result)
        
        total_cost = sum(r["cost"] for r in results)
        print(f"\n✅ Character series completed!")
        print(f"   Total images: {len(results)}")
        print(f"   Total cost: ${total_cost:.2f}")
        
        return results


def create_character_prompt(
    character_description: str,
    action: str,
    location: str,
    style: str = "cinematic",
    lighting: Optional[str] = None,
    camera_angle: Optional[str] = None
) -> str:
    """
    Helper function to create well-structured character prompts.
    
    Args:
        character_description: Base character traits (age, appearance, clothing)
        action: What the character is doing
        location: Where the scene takes place
        style: Visual style (default: "cinematic")
        lighting: Optional lighting description
        camera_angle: Optional camera angle
        
    Returns:
        Formatted prompt string
        
    Example:
        >>> create_character_prompt(
        ...     "25-year-old woman with long brown hair, wearing white t-shirt",
        ...     "stretching arms above head",
        ...     "modern bedroom",
        ...     style="warm cinematic",
        ...     lighting="soft morning sunlight",
        ...     camera_angle="medium shot"
        ... )
        "25-year-old woman with long brown hair, wearing white t-shirt, 
         stretching arms above head in modern bedroom. Warm cinematic style. 
         Soft morning sunlight. Medium shot."
    """
    
    # Build main description
    parts = [f"{character_description}, {action} in {location}"]
    
    if style:
        parts.append(f"{style} style")
    
    if lighting:
        parts.append(lighting)
    
    if camera_angle:
        parts.append(camera_angle)
    
    # Add quality keywords
    parts.append("high quality, detailed, 4K")
    
    return ". ".join(parts) + "."


# Example usage
if __name__ == "__main__":
    tool = InstantCharacterTool()
    
    # Test 1: Generate single character image
    print("=== Test 1: Single Character ===")
    result1 = tool.execute(
        prompt=create_character_prompt(
            "25-year-old woman with long brown hair, wearing white pajamas",
            "sleeping peacefully",
            "cozy bedroom",
            lighting="soft morning light filtering through curtains"
        ),
        image_size="landscape_16_9",
        output_path="test_character_1.jpg"
    )
    
    # Test 2: Generate character series
    print("\n=== Test 2: Character Series ===")
    base_character = "25-year-old woman with long brown hair, wearing casual clothes"
    scenes = [
        "waking up in bedroom, morning light",
        "stretching arms in bedroom, energetic",
        "walking to kitchen, smiling"
    ]
    
    results = tool.generate_character_series(
        base_prompt=base_character,
        scene_prompts=scenes,
        output_dir="test_character_series",
        image_size="landscape_16_9"
    )
    
    print(f"\n✅ All tests completed!")
    print(f"Total cost: ${result1['cost'] + sum(r['cost'] for r in results):.2f}")
