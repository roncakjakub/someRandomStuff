"""
Visual Production Agent v3.2 - Complete Rewrite
Properly handles Router tool selection and style-specific workflows.
"""
from typing import Dict, Any, List, Optional
import logging
import time

# Image generation tools
from tools.replicate_image import FluxSchnellTool, FluxDevTool, FluxProTool
from tools.apiframe_midjourney import ApiframeMidjourneyTool
from tools.instant_character import InstantCharacterTool
from tools.flux_kontext_pro import FluxKontextProTool

# Video generation tools
from tools.veo31_flf2v import Veo31FLF2VTool
from tools.wan_flf2v import WanFLF2VTool
from tools.pika_video import PikaVideoTool

logger = logging.getLogger(__name__)


class VisualProductionAgent:
    """
    Agent responsible for generating all visual content.
    Supports dynamic tool selection via Router and style-specific workflows.
    """
    
    def __init__(self, quality: str = "dev", workflow_plan=None):
        """
        Initialize visual production agent.
        
        Args:
            quality: Default quality - "schnell" (fast), "dev" (balanced), "pro" (best)
            workflow_plan: Optional WorkflowPlan from AI Router
        """
        self.name = "Visual Production Agent"
        self.logger = logging.getLogger(f"agents.{self.name}")
        self.workflow_plan = workflow_plan
        self.quality = quality
        
        # Initialize all image generation tools
        self.image_tools = {
            "flux_schnell": FluxSchnellTool(),
            "flux_dev": FluxDevTool(),
            "flux_pro": FluxProTool(),
            "midjourney": ApiframeMidjourneyTool(),
            "instant_character": InstantCharacterTool(),
            "flux_kontext_pro": FluxKontextProTool(),
        }
        
        # Initialize all video generation tools
        self.video_tools = {
            "veo31_flf2v": Veo31FLF2VTool(),
            "wan_flf2v": WanFLF2VTool(),
            "pika_video": PikaVideoTool(),
        }
        
        # Set default tools based on quality
        if quality == "pro":
            self.default_image_tool = "flux_pro"
        elif quality == "dev":
            self.default_image_tool = "flux_dev"
        else:
            self.default_image_tool = "flux_schnell"
        
        self.default_video_tool = "veo31_flf2v"
        
        self.logger.info(f"Initialized with {len(self.image_tools)} image tools, {len(self.video_tools)} video tools")
        self.logger.info(f"Default tools: {self.default_image_tool} (images), {self.default_video_tool} (videos)")
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - routes to style-specific workflow.
        
        Args:
            state: Workflow state containing prompts, scene_plans, video_style, etc.
            
        Returns:
            Updated state with generated visuals
        """
        prompts = state.get("prompts", {})
        output_dir = state.get("run_output_dir")
        video_style = state.get("video_style", "cinematic")
        scene_plans = state.get("scene_plans", [])
        
        self.logger.info(f"Running {video_style.upper()} style workflow...")
        
        # Route to style-specific workflow
        if video_style == "pika":
            result = self._generate_pika_style(
                scenes=prompts.get("scenes", []),
                scene_plans=scene_plans,
                output_dir=output_dir
            )
        elif video_style == "hybrid":
            result = self._generate_hybrid_style(
                scenes=prompts.get("scenes", []),
                scene_plans=scene_plans,
                output_dir=output_dir
            )
        else:
            # Cinematic/viral style - just generate images
            result = self.generate_visuals(prompts, output_dir, scene_plans)
        
        # Update state
        state.update(result)
        return state
    
    def generate_visuals(
        self, 
        prompts: Dict[str, Any], 
        output_dir: str = None,
        scene_plans: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Generate images using Router-selected tools.
        
        Args:
            prompts: Prompts from Creative Strategist
            output_dir: Output directory
            scene_plans: Tool selection from Router
            
        Returns:
            Dictionary with generated image paths
        """
        scenes = prompts.get("scenes", [])
        
        if not scenes:
            self.logger.error("No scenes found in prompts")
            raise Exception("No scenes to generate")
        
        self.logger.info(f"Generating {len(scenes)} images...")
        
        all_images = []
        total_cost = 0.0
        total_time = 0
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("number", idx + 1)
            scene_prompt = scene.get("prompt", "")
            
            if not scene_prompt:
                self.logger.warning(f"Scene {scene_number} has empty prompt, skipping")
                continue
            
            # Get tool from Router scene plan
            scene_tool = self._get_tool_for_scene(scene_number, scene, scene_plans)
            
            self.logger.info(f"  Scene {scene_number}/{len(scenes)}: Using '{scene_tool}'")
            
            # Generate image
            start_time = time.time()
            image_path = self._generate_image(
                prompt=scene_prompt,
                tool_name=scene_tool,
                output_dir=output_dir
            )
            elapsed_time = time.time() - start_time
            
            all_images.append(image_path)
            total_time += int(elapsed_time)
            
            # Estimate cost
            total_cost += self._estimate_image_cost(scene_tool)
        
        self.logger.info(f"Generated {len(all_images)} images in {total_time}s (${total_cost:.2f})")
        
        return {
            "all_images": all_images,
            "scene_images": all_images,
            "total_images": len(all_images),
            "total_cost": total_cost,
            "total_time": total_time
        }
    
    def _get_tool_for_scene(
        self, 
        scene_number: int, 
        scene: Dict[str, Any],
        scene_plans: List[Any]
    ) -> str:
        """
        Get the tool to use for a specific scene.
        Priority: scene_plans > scene.tool > default
        """
        # 1. Try to get from Router scene_plans
        if scene_plans:
            for plan in scene_plans:
                if hasattr(plan, 'scene_number') and plan.scene_number == scene_number:
                    if hasattr(plan, 'image_tool'):
                        return plan.image_tool
        
        # 2. Try to get from scene dict
        if "tool" in scene:
            tool_name = scene["tool"]
            # Map common aliases
            if tool_name == "seedream4":
                return "instant_character"
            elif tool_name == "flux":
                return self.default_image_tool
            return tool_name
        
        # 3. Use default
        return self.default_image_tool
    
    def _generate_image(
        self,
        prompt: str,
        tool_name: str,
        output_dir: str,
        reference_image: Optional[str] = None
    ) -> str:
        """
        Generate a single image using specified tool.
        
        Args:
            prompt: Image generation prompt
            tool_name: Name of tool to use
            output_dir: Output directory
            reference_image: Optional reference image for consistency
            
        Returns:
            Path to generated image
        """
        # Get tool from dictionary
        if tool_name not in self.image_tools:
            self.logger.warning(f"Tool '{tool_name}' not found, using default '{self.default_image_tool}'")
            tool_name = self.default_image_tool
        
        tool = self.image_tools[tool_name]
        
        # Prepare tool input based on tool type
        if tool_name in ["instant_character", "flux_kontext_pro"]:
            # These tools have specific parameter names
            tool_input = {
                "prompt": prompt,
                "image_size": "landscape_16_9",  # InstantCharacter uses image_size, not aspect_ratio
                "output_path": str(output_dir),  # InstantCharacter uses output_path, not output_dir
            }
            # Add reference image if provided
            if reference_image:
                tool_input["reference_image_url"] = reference_image  # InstantCharacter uses reference_image_url
        else:
            # Other tools (Flux, Midjourney, etc.)
            tool_input = {
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "num_outputs": 1,
                "output_dir": str(output_dir),
            }
        
        # Generate image
        result = tool.execute(tool_input)
        
        # Extract image path - handle different return formats
        # Some tools return "images" (list), others return "image_path" (string)
        if "images" in result:
            image_paths = result["images"]
        elif "image_path" in result:
            image_paths = [result["image_path"]]
        elif "image_paths" in result:
            image_paths = result["image_paths"]
        else:
            raise Exception(f"Tool '{tool_name}' returned no images (result keys: {list(result.keys())})")
        
        if not image_paths:
            raise Exception(f"Tool '{tool_name}' returned empty image list")
        
        return image_paths[0]
    
    def _estimate_image_cost(self, tool_name: str) -> float:
        """Estimate cost for image generation."""
        cost_map = {
            "midjourney": 0.05,
            "flux_pro": 0.04,
            "flux_dev": 0.03,
            "flux_schnell": 0.01,
            "instant_character": 0.04,
            "flux_kontext_pro": 0.04,
        }
        return cost_map.get(tool_name, 0.03)
    
    def _generate_pika_style(
        self,
        scenes: List[Dict[str, Any]],
        scene_plans: List[Any],
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Generate PIKA style workflow:
        1. Generate all images with character consistency
        2. Create morph transitions between all scenes
        
        Args:
            scenes: List of scenes from Creative Strategist
            scene_plans: Tool selection from Router
            output_dir: Output directory
            
        Returns:
            Dictionary with scene_videos, total_cost, total_time
        """
        self.logger.info(f"PIKA WORKFLOW: Step 1/2 - Generating {len(scenes)} images...")
        
        # Step 1: Generate all images with character consistency
        scene_images = []
        total_cost = 0.0
        total_time = 0
        reference_image = None
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("number", idx + 1)
            scene_prompt = scene.get("prompt", "")
            scene_content_type = scene.get("content_type", "object")
            
            if not scene_prompt:
                self.logger.warning(f"Scene {scene_number} has empty prompt, skipping")
                continue
            
            # Get tool from Router
            scene_tool = self._get_tool_for_scene(scene_number, scene, scene_plans)
            
            self.logger.info(f"  Scene {scene_number}: {scene_tool}, content: {scene_content_type}")
            
            # Use reference image for character consistency
            use_reference = None
            if scene_content_type in ["human_portrait", "human_action"] and reference_image:
                if scene_tool in ["instant_character", "flux_kontext_pro"]:
                    use_reference = reference_image
                    self.logger.info(f"    Using reference image for character consistency")
            
            # Generate image
            start_time = time.time()
            image_path = self._generate_image(
                prompt=scene_prompt,
                tool_name=scene_tool,
                output_dir=output_dir,
                reference_image=use_reference
            )
            elapsed_time = time.time() - start_time
            
            # Save first human scene as reference
            if not reference_image and scene_content_type in ["human_portrait", "human_action"]:
                reference_image = image_path
                self.logger.info(f"    Saved as reference image")
            
            scene_images.append({
                "scene_number": scene_number,
                "image_path": image_path,
                "description": scene.get("description", ""),
                "time": int(elapsed_time)
            })
            
            total_time += int(elapsed_time)
            total_cost += self._estimate_image_cost(scene_tool)
        
        self.logger.info(f"PIKA WORKFLOW: Step 1 complete - {len(scene_images)} images")
        
        # Step 2: Create morph videos between consecutive scenes
        self.logger.info(f"PIKA WORKFLOW: Step 2/2 - Creating {len(scene_images)-1} morph transitions...")
        
        # Get video tool from Router
        video_tool_name = self._get_video_tool_for_scene(1, scene_plans)
        
        scene_videos = []
        
        for i in range(len(scene_images) - 1):
            start_scene = scene_images[i]
            end_scene = scene_images[i + 1]
            
            self.logger.info(f"  Morph {i+1}: Scene {start_scene['scene_number']} → {end_scene['scene_number']}")
            
            start_time = time.time()
            
            video_result = self._create_morph_video(
                start_image=start_scene["image_path"],
                end_image=end_scene["image_path"],
                scene_description=f"{start_scene['description']} to {end_scene['description']}",
                video_tool_name=video_tool_name,
                output_dir=output_dir
            )
            
            elapsed_time = time.time() - start_time
            
            scene_videos.append(video_result["video_path"])
            total_cost += video_result.get("cost", 0.80)
            total_time += int(elapsed_time)
        
        self.logger.info(f"PIKA WORKFLOW: Complete! {len(scene_videos)} morph videos created")
        
        return {
            "scene_videos": scene_videos,
            "scene_images": [img["image_path"] for img in scene_images],
            "all_images": [img["image_path"] for img in scene_images],
            "total_videos": len(scene_videos),
            "total_images": len(scene_images),
            "total_cost": total_cost,
            "total_time": total_time
        }
    
    def _generate_hybrid_style(
        self,
        scenes: List[Dict[str, Any]],
        scene_plans: List[Any],
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Generate HYBRID style workflow:
        1. Generate all images with scene-group-aware reference management
        2. Create morph transitions within scene groups
        3. Use hard cuts between scene groups
        
        Args:
            scenes: List of scenes from Creative Strategist
            scene_plans: Tool selection from Router (with scene_group and transition info)
            output_dir: Output directory
            
        Returns:
            Dictionary with scene_videos, total_cost, total_time
        """
        self.logger.info(f"HYBRID WORKFLOW: Step 1/3 - Generating {len(scenes)} images...")
        
        # Step 1: Generate all images with scene-group-aware reference
        scene_images = []
        total_cost = 0.0
        total_time = 0
        
        # Track reference image per scene group
        group_references = {}  # {scene_group: {"image": path, "content_type": str}}
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("number", idx + 1)
            scene_prompt = scene.get("prompt", "")
            scene_content_type = scene.get("content_type", "object")
            
            # Get scene plan info
            scene_plan = self._get_scene_plan(scene_number, scene_plans)
            scene_group = getattr(scene_plan, 'scene_group', 1) if scene_plan else 1
            transition = getattr(scene_plan, 'transition', 'morph') if scene_plan else 'morph'
            
            if not scene_prompt:
                self.logger.warning(f"Scene {scene_number} has empty prompt, skipping")
                continue
            
            self.logger.info(f"  Scene {scene_number} (Group {scene_group}): {scene_content_type}, {transition}")
            
            # Get tool from Router
            scene_tool = self._get_tool_for_scene(scene_number, scene, scene_plans)
            
            # For HYBRID style: Use scene group reference for character consistency
            use_reference = None
            if scene_content_type in ["human_portrait", "human_action"]:
                if scene_group in group_references:
                    # Use reference from this scene group
                    ref_data = group_references[scene_group]
                    if scene_tool in ["instant_character", "flux_kontext_pro"]:
                        use_reference = ref_data["image"]
                        self.logger.info(f"    Using Group {scene_group} reference")
            
            # Generate image
            start_time = time.time()
            image_path = self._generate_image(
                prompt=scene_prompt,
                tool_name=scene_tool,
                output_dir=output_dir,
                reference_image=use_reference
            )
            elapsed_time = time.time() - start_time
            
            # Save as reference if first human in scene group
            if scene_content_type in ["human_portrait", "human_action"]:
                if scene_group not in group_references:
                    group_references[scene_group] = {
                        "image": image_path,
                        "content_type": scene_content_type
                    }
                    self.logger.info(f"    Saved as Group {scene_group} reference")
            
            scene_images.append({
                "scene_number": scene_number,
                "scene_group": scene_group,
                "transition": transition,
                "image_path": image_path,
                "description": scene.get("description", ""),
                "content_type": scene_content_type,
                "time": int(elapsed_time)
            })
            
            total_time += int(elapsed_time)
            total_cost += self._estimate_image_cost(scene_tool)
        
        self.logger.info(f"HYBRID WORKFLOW: Step 1 complete - {len(scene_images)} images, {len(group_references)} scene groups")
        
        # Get video tool
        video_tool_name = self._get_video_tool_for_scene(1, scene_plans)
        
        # Step 2: Group scenes by scene_group
        self.logger.info(f"HYBRID WORKFLOW: Step 2/3 - Grouping scenes...")
        
        scene_groups = {}
        for scene_img in scene_images:
            group = scene_img["scene_group"]
            if group not in scene_groups:
                scene_groups[group] = []
            scene_groups[group].append(scene_img)
        
        self.logger.info(f"  Found {len(scene_groups)} scene groups")
        for group_num, group_scenes in scene_groups.items():
            self.logger.info(f"    Group {group_num}: {len(group_scenes)} shots")
        
        # Step 3: Create morph videos within each scene group
        self.logger.info(f"HYBRID WORKFLOW: Step 3/3 - Creating transitions...")
        
        scene_videos = []
        
        for group_num in sorted(scene_groups.keys()):
            group_scenes = scene_groups[group_num]
            
            self.logger.info(f"\n  Processing Group {group_num} ({len(group_scenes)} shots)...")
            
            # Create morph transitions within this group
            for i in range(len(group_scenes) - 1):
                start_scene = group_scenes[i]
                end_scene = group_scenes[i + 1]
                
                self.logger.info(f"    Morph: Scene {start_scene['scene_number']} → {end_scene['scene_number']}")
                
                start_time = time.time()
                
                video_result = self._create_morph_video(
                    start_image=start_scene["image_path"],
                    end_image=end_scene["image_path"],
                    scene_description=f"{start_scene['description']} to {end_scene['description']}",
                    video_tool_name=video_tool_name,
                    output_dir=output_dir
                )
                
                elapsed_time = time.time() - start_time
                
                scene_videos.append(video_result["video_path"])
                total_cost += video_result.get("cost", 0.80)
                total_time += int(elapsed_time)
            
            # Add marker for hard cut after this group (except last group)
            if group_num < max(scene_groups.keys()):
                self.logger.info(f"    → HARD CUT after Group {group_num}")
        
        self.logger.info(f"\nHYBRID WORKFLOW: Complete!")
        self.logger.info(f"  {len(scene_videos)} morph transitions created")
        self.logger.info(f"  {len(scene_groups)} scene groups with hard cuts between them")
        
        return {
            "scene_videos": scene_videos,
            "scene_images": [img["image_path"] for img in scene_images],
            "all_images": [img["image_path"] for img in scene_images],
            "total_videos": len(scene_videos),
            "total_images": len(scene_images),
            "total_cost": total_cost,
            "total_time": total_time,
            "scene_groups": len(scene_groups),
            "video_metadata": [{"video_path": v} for v in scene_videos]
        }
    
    def _get_scene_plan(self, scene_number: int, scene_plans: List[Any]) -> Any:
        """Get scene plan for a specific scene number."""
        if not scene_plans:
            return None
        for plan in scene_plans:
            if hasattr(plan, 'scene_number') and plan.scene_number == scene_number:
                return plan
        return None
    
    def _get_video_tool_for_scene(self, scene_number: int, scene_plans: List[Any]) -> str:
        """Get video tool from Router scene plans."""
        if scene_plans:
            for plan in scene_plans:
                if hasattr(plan, 'scene_number') and plan.scene_number == scene_number:
                    if hasattr(plan, 'video_tool'):
                        return plan.video_tool
        return self.default_video_tool
    
    def _create_morph_video(
        self,
        start_image: str,
        end_image: str,
        scene_description: str,
        video_tool_name: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Create morph transition video between two images.
        
        Args:
            start_image: Path to start image
            end_image: Path to end image
            scene_description: Description for the transition
            video_tool_name: Name of video tool to use
            output_dir: Output directory
            
        Returns:
            Dictionary with video_path and cost
        """
        # Get tool from dictionary
        if video_tool_name not in self.video_tools:
            self.logger.warning(f"Video tool '{video_tool_name}' not found, using default '{self.default_video_tool}'")
            video_tool_name = self.default_video_tool
        
        tool = self.video_tools[video_tool_name]
        
        # Generate video
        result = tool.execute({
            "start_image": start_image,
            "end_image": end_image,
            "prompt": scene_description,
            "output_dir": str(output_dir),  # Convert Path to string for JSON serialization
        })
        
        # Estimate cost
        cost_map = {
            "veo31_flf2v": 0.80,  # $0.10/s × 8s
            "wan_flf2v": 0.40,
            "pika_v2": 0.15,
        }
        cost = cost_map.get(video_tool_name, 0.80)
        
        return {
            "video_path": result.get("video_path"),
            "cost": cost
        }
