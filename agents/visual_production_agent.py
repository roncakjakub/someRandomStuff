"""
Visual Production Agent - Phase 2
Generates all visual content using Replicate (Flux).
"""
from typing import Dict, Any, List
import logging
from tools import FluxSchnellTool, FluxDevTool, FluxProTool

logger = logging.getLogger(__name__)


class VisualProductionAgent:
    """
    Agent responsible for generating all visual content.
    Uses Flux models via Replicate API.
    """
    
    def __init__(self, quality: str = "dev", workflow_plan = None):
        """
        Initialize visual production agent.
        
        Args:
            quality: Model quality - "schnell" (fast), "dev" (balanced), "pro" (best)
            workflow_plan: Optional WorkflowPlan from AI Router
        """
        self.name = "Visual Production Agent"
        self.logger = logging.getLogger(f"agents.{self.name}")
        self.workflow_plan = workflow_plan
        
        # Check if router specified tools to use
        if workflow_plan and hasattr(workflow_plan, 'tools'):
            self.enabled_tools = workflow_plan.tools
            self.logger.info(f"Router-selected tools: {self.enabled_tools}")
        else:
            # Default: all tools enabled
            self.enabled_tools = None
            self.logger.info("Using all tools (router disabled)")
        
        # Select appropriate Flux model
        if quality == "pro":
            self.image_tool = FluxProTool()
        elif quality == "dev":
            self.image_tool = FluxDevTool()
        else:
            self.image_tool = FluxSchnellTool()
        
        self.quality = quality
    
    def generate_visuals(self, prompts: Dict[str, Any], output_dir: str = None) -> Dict[str, Any]:
        """
        Generate all visual content based on prompts.
        
        Args:
            prompts: Prompts from Creative Strategist
            output_dir: Custom output directory
            
        Returns:
            Dictionary with all generated image paths
        """
        self.logger.info("Starting visual content generation...")
        
        all_images = []
        scene_images = []
        
        # Extract scenes from prompts
        scenes = prompts.get("scenes", [])
        
        if not scenes:
            self.logger.error("No scenes found in prompts")
            raise Exception("No scenes to generate")
        
        self.logger.info(f"Generating {len(scenes)} scenes...")
        
        # Generate all scene images
        for idx, scene in enumerate(scenes):
            scene_prompt = scene.get("prompt", "")
            scene_tool = scene.get("tool", "flux")
            
            if not scene_prompt:
                self.logger.warning(f"Scene {idx + 1} has empty prompt, skipping")
                continue
            
            self.logger.info(f"Generating scene {idx + 1}/{len(scenes)} (tool: {scene_tool})...")
            
            scene_result = self.image_tool.run({
                "prompt": scene_prompt,
                "aspect_ratio": "9:16",
                "num_outputs": 1,
                "output_dir": output_dir,
            })
            
            if scene_result.get("success"):
                scene_image = scene_result.get("images", [])[0]
                scene_images.append(scene_image)
                all_images.append(scene_image)
                self.logger.info(f"Scene {idx + 1} generated: {scene_image}")
            else:
                self.logger.warning(f"Failed to generate scene {idx + 1}")
        
        if not all_images:
            self.logger.error("No images were generated")
            raise Exception("Image generation failed")
        
        # Use first image as opening frame
        opening_frame = all_images[0]
        
        # 3. Generate text overlay image (if needed)
        text_overlay = prompts.get("text_overlay")
        overlay_image = None
        
        if text_overlay:
            self.logger.info("Generating text overlay...")
            overlay_prompt = f"Text overlay design, 9:16 vertical format, elegant typography: '{text_overlay}', minimalist, professional"
            
            overlay_result = self.image_tool.run({
                "prompt": overlay_prompt,
                "aspect_ratio": "9:16",
                "num_outputs": 1,
                "output_dir": output_dir,
            })
            
            if overlay_result.get("success"):
                overlay_image = overlay_result.get("images", [])[0]
                self.logger.info(f"Text overlay generated: {overlay_image}")
        
        self.logger.info(f"Visual production complete: {len(all_images)} images generated")
        
        return {
            "opening_frame": opening_frame,
            "scene_images": scene_images,
            "all_images": all_images,
            "text_overlay_image": overlay_image,
            "total_images": len(all_images),
        }
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated images
        """
        prompts = state.get("prompts", {})
        output_dir = state.get("run_output_dir")
        
        visuals = self.generate_visuals(prompts, output_dir)
        
        return {
            **state,
            **visuals,
        }


if __name__ == "__main__":
    # Test the agent (requires actual prompts)
    agent = VisualProductionAgent(quality="schnell")
    
    test_state = {
        "prompts": {
            "opening_frame_prompt": "Cinematic shot, 9:16, person pouring coffee, morning light, professional photography",
            "scene_prompts": [
                "Close-up of coffee cup, steam rising, warm lighting",
                "Person enjoying coffee, peaceful morning scene"
            ],
            "text_overlay": "Your Perfect Morning"
        }
    }
    
    # result = agent.run(test_state)
    # print(result)
