"""
Flux Kontext Pro Tool
Advanced image-to-image editing with environment and style consistency
"""

import fal_client
from typing import Dict, Any, Optional
import os


class FluxKontextProTool:
    """
    Transform images with intelligent editing while preserving environment/style consistency.
    
    Best for:
    - Preserving environment across multiple scenes (same kitchen, bedroom, etc.)
    - Style consistency across different shots
    - Adding/removing objects while keeping background
    - Character + environment consistency combined
    """
    
    def __init__(self):
        self.model_id = "fal-ai/flux-pro/kontext"
        self.cost_per_image = 0.04  # $0.04 per image
        
    def execute(
        self,
        prompt: str,
        reference_image_url: str,
        guidance_scale: float = 3.5,
        num_inference_steps: int = 28,
        seed: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image with environment/style consistency from reference.
        
        Args:
            prompt: Editing instruction - what to change/add
                   Should specify what to KEEP from reference
                   Example: "Add a coffee machine on the counter, keep the kitchen style"
            reference_image_url: Reference image for environment/style
            guidance_scale: Prompt adherence (default: 3.5)
            num_inference_steps: Quality vs speed (default: 28)
            seed: Optional seed for reproducibility
            output_path: Optional path to save the image
            
        Returns:
            Dict with image URL, cost, and metadata
            
        Prompt Best Practices:
        - Be explicit about what to KEEP: "keep the kitchen", "preserve lighting"
        - Specify what to CHANGE: "add woman drinking coffee", "change to evening"
        - Mention style consistency: "maintain the same warm cinematic style"
        """
        
        # Validate inputs
        if not prompt:
            raise ValueError("Prompt is required")
        
        if not reference_image_url:
            raise ValueError("Reference image URL is required")
        
        # Prepare request
        request_data = {
            "prompt": prompt,
            "image_url": reference_image_url,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps
        }
        
        print(f"🎨 Generating with Flux Kontext Pro...")
        print(f"   Reference: {reference_image_url}")
        print(f"   Prompt: {prompt}")
        
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
            
            print(f"✅ Kontext Pro image generated!")
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
                "reference_url": reference_image_url,
                "local_path": output_path if output_path else None
            }
            
        except Exception as e:
            print(f"❌ Flux Kontext Pro generation failed: {str(e)}")
            raise
    
    def generate_environment_series(
        self,
        reference_image_url: str,
        scene_prompts: List[str],
        output_dir: str,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a series of images in the same environment.
        
        Args:
            reference_image_url: First scene image (establishes environment)
            scene_prompts: List of editing instructions for each subsequent scene
            output_dir: Directory to save images
            seed: Optional seed for consistency
            
        Returns:
            List of result dicts for each generated image
            
        Example:
            reference = "kitchen_scene1.jpg"  # Coffee beans on counter
            prompts = [
                "Add a coffee grinder next to the beans, keep the kitchen style",
                "Show espresso pouring into cup, keep the same kitchen and lighting"
            ]
        """
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for i, scene_prompt in enumerate(scene_prompts):
            output_path = os.path.join(output_dir, f"scene_{i+2:02d}.jpg")
            
            result = self.execute(
                prompt=scene_prompt,
                reference_image_url=reference_image_url,
                seed=seed,
                output_path=output_path
            )
            
            results.append(result)
        
        total_cost = sum(r["cost"] for r in results)
        print(f"\n✅ Environment series completed!")
        print(f"   Total images: {len(results) + 1} (1 reference + {len(results)} generated)")
        print(f"   Total cost: ${total_cost:.2f}")
        
        return results


def create_environment_prompt(
    action: str,
    environment_description: str,
    preserve_elements: List[str],
    style_note: Optional[str] = None
) -> str:
    """
    Helper function to create well-structured Kontext Pro prompts.
    
    Args:
        action: What to add/change in the scene
        environment_description: What environment to preserve
        preserve_elements: List of specific elements to keep
        style_note: Optional style consistency note
        
    Returns:
        Formatted prompt string
        
    Example:
        >>> create_environment_prompt(
        ...     action="Add a woman pouring coffee",
        ...     environment_description="modern white kitchen",
        ...     preserve_elements=["marble countertop", "morning sunlight", "minimalist style"],
        ...     style_note="warm cinematic"
        ... )
        "Add a woman pouring coffee. Keep the modern white kitchen with marble countertop, 
         morning sunlight, and minimalist style. Maintain warm cinematic style."
    """
    
    # Build action
    parts = [action]
    
    # Build preservation instruction
    preserve_str = ", ".join(preserve_elements)
    parts.append(f"Keep the {environment_description} with {preserve_str}")
    
    # Add style note
    if style_note:
        parts.append(f"Maintain {style_note} style")
    
    return ". ".join(parts) + "."


# Example usage
if __name__ == "__main__":
    from typing import List
    
    tool = FluxKontextProTool()
    
    # Test 1: Single environment-consistent image
    print("=== Test 1: Single Image with Environment Reference ===")
    result1 = tool.execute(
        prompt=create_environment_prompt(
            action="Add a coffee grinder on the counter",
            environment_description="modern white kitchen",
            preserve_elements=["marble countertop", "warm lighting", "minimalist style"]
        ),
        reference_image_url="https://example.com/kitchen_scene1.jpg",
        output_path="test_kontext_1.jpg"
    )
    
    # Test 2: Environment series
    print("\n=== Test 2: Environment Series ===")
    reference_url = "https://example.com/kitchen_base.jpg"
    
    prompts = [
        create_environment_prompt(
            "Add coffee grinder working",
            "kitchen",
            ["countertop", "lighting", "style"]
        ),
        create_environment_prompt(
            "Show espresso pouring into cup",
            "kitchen",
            ["countertop", "lighting", "style"]
        ),
        create_environment_prompt(
            "Add woman holding coffee cup",
            "kitchen",
            ["countertop", "lighting", "style"]
        )
    ]
    
    results = tool.generate_environment_series(
        reference_image_url=reference_url,
        scene_prompts=prompts,
        output_dir="test_environment_series"
    )
    
    print(f"\n✅ All tests completed!")
    print(f"Total cost: ${result1['cost'] + sum(r['cost'] for r in results):.2f}")
