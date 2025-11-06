"""
Visual Production Agent V2 - Phase 3
Generates animated video content using AI-selected tools per scene.
Supports multiple video generation tools based on content type.
UPDATED: Now supports dual-image generation for transition scenes (PikaMorph feature)
"""
from typing import Dict, Any, List, Optional
import logging
import os
from pathlib import Path

# Image generation tools
from tools import (
    FluxSchnellTool, FluxDevTool, FluxProTool,
    ApiframeMidjourneyTool, Seedream4Tool, IdeogramTextTool
)

# Video generation tools
from tools.luma_video import LumaVideoTool
from tools.runway_video import RunwayVideoTool
from tools.pika_video import PikaVideoTool
from tools.minimax_video import MinimaxVideoTool
from tools.wan_video import WanVideoTool

logger = logging.getLogger(__name__)


class VisualProductionAgent:
    """
    Visual Production Agent V2
    
    Generates animated video clips for each scene using:
    1. Image generation (Flux)
    2. Video animation (Minimax/Luma/Runway/Pika/Wan)
    
    Tool selection is driven by Workflow Router's scene_plans.
    
    NEW: Supports dual-image generation for transition scenes with Pika morph.
    """
    
    def __init__(self, quality: str = "dev"):
        """
        Initialize visual production agent.
        
        Args:
            quality: Image quality - "schnell" (fast), "dev" (balanced), "pro" (best)
                    This is used as DEFAULT when router doesn't specify image tool
        """
        self.name = "Visual Production Agent"
        self.logger = logging.getLogger(f"agents.{self.name}")
        self.quality = quality
        
        # Initialize ALL available image generation tools
        self.image_tools = {
            "flux_schnell": FluxSchnellTool(),
            "flux_dev": FluxDevTool(),
            "flux_pro": FluxProTool(),
            "midjourney": ApiframeMidjourneyTool(),
            "seedream4": Seedream4Tool(),
            "ideogram": IdeogramTextTool(),
        }
        
        # Set default image tool based on quality
        if quality == "pro":
            self.default_image_tool = "flux_pro"
        elif quality == "dev":
            self.default_image_tool = "flux_dev"
        else:
            self.default_image_tool = "flux_schnell"
        
        # Initialize video generation tools
        self.video_tools = {
            "luma_ray": LumaVideoTool(),
            "runway_gen4": RunwayVideoTool(),
            "pika_v2": PikaVideoTool(),
            "minimax_hailuo": MinimaxVideoTool(),
            "wan_i2v": WanVideoTool(),
        }
        
        self.logger.info(f"Initialized with default image quality: {quality} ({self.default_image_tool})")
        self.logger.info(f"Available image tools: {list(self.image_tools.keys())}")
        self.logger.info(f"Available video tools: {list(self.video_tools.keys())}")
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point called by workflow.
        
        Args:
            state: Workflow state containing:
                - prompts: Scenes from Creative Strategist
                - scene_plans: Tool selection from Workflow Router (optional)
                - run_output_dir: Output directory
        
        Returns:
            Updated state with generated video clips
        """
        prompts = state.get("prompts", {})
        scene_plans = state.get("scene_plans", [])
        output_dir = state.get("run_output_dir")
        
        result = self.generate_visuals(
            prompts=prompts,
            scene_plans=scene_plans,
            output_dir=output_dir
        )
        
        # Update state
        state.update(result)
        return state
    
    def generate_visuals(
        self,
        prompts: Dict[str, Any],
        scene_plans: List[Dict[str, Any]] = None,
        output_dir: str = None
    ) -> Dict[str, Any]:
        """
        Generate animated video clips for all scenes.
        
        Args:
            prompts: Prompts from Creative Strategist with scenes
            scene_plans: Optional tool selection from Workflow Router
            output_dir: Custom output directory
        
        Returns:
            Dictionary with:
                - scene_videos: List of video file paths
                - total_videos: Number of videos generated
                - total_cost: Total generation cost
                - total_time: Total generation time
        """
        self.logger.info("Starting visual content generation...")
        
        # Extract scenes
        scenes = prompts.get("scenes", [])
        
        if not scenes:
            self.logger.error("No scenes found in prompts")
            raise Exception("No scenes to generate")
        
        self.logger.info(f"Generating {len(scenes)} animated scenes...")
        
        # Create output directory
        if not output_dir:
            output_dir = "output/visuals"
        os.makedirs(output_dir, exist_ok=True)
        
        scene_videos = []
        total_cost = 0.0
        total_time = 0
        
        # Generate each scene
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("number", idx + 1)
            scene_description = scene.get("description", "")
            content_type = scene.get("content_type", "object")
            
            self.logger.info(f"Scene {scene_number}/{len(scenes)}: {scene_description}")
            self.logger.info(f"  Content type: {content_type}")
            
            try:
                # Check if this is a transition scene with dual prompts
                if content_type == "transition" and "prompts" in scene:
                    # TRANSITION MODE: Generate 2 images and morph
                    self.logger.info(f"  Detected TRANSITION scene - generating dual images for morph")
                    
                    start_prompt = scene["prompts"]["start"]
                    end_prompt = scene["prompts"]["end"]
                    
                    # Get image tool selection from scene_plans
                    image_tool_name = self._get_image_tool_for_scene(
                        scene_number=scene_number,
                        scene_plans=scene_plans
                    )
                    
                    self.logger.info(f"  Selected image tool: {image_tool_name}")
                    
                    # Step 1: Generate start image
                    self.logger.info(f"  Step 1/3: Generating START image...")
                    start_image_path = self._generate_image(
                        prompt=start_prompt,
                        scene_number=scene_number,
                        output_dir=output_dir,
                        suffix="start",
                        image_tool_name=image_tool_name
                    )
                    
                    # Step 2: Generate end image
                    self.logger.info(f"  Step 2/3: Generating END image...")
                    end_image_path = self._generate_image(
                        prompt=end_prompt,
                        scene_number=scene_number,
                        output_dir=output_dir,
                        suffix="end",
                        image_tool_name=image_tool_name
                    )
                    
                    # Step 3: Create morph video with Pika
                    self.logger.info(f"  Step 3/3: Creating morph video with Pika...")
                    video_result = self._create_morph_video(
                        start_image=start_image_path,
                        end_image=end_image_path,
                        scene_description=scene_description,
                        scene_number=scene_number,
                        output_dir=output_dir
                    )
                    
                    video_path = video_result["video_path"]
                    total_cost += video_result.get("cost", 0.0)
                    total_time += video_result.get("time", 0)
                    
                else:
                    # NORMAL MODE: Single image + animation
                    scene_prompt = scene.get("prompt", "")
                    
                    if not scene_prompt:
                        self.logger.warning(f"Scene {scene_number} has empty prompt, skipping")
                        continue
                    
                    # Get tool selection from scene_plans
                    video_tool_name = self._get_video_tool_for_scene(
                        scene_number=scene_number,
                        content_type=content_type,
                        scene_plans=scene_plans
                    )
                    
                    self.logger.info(f"  Selected video tool: {video_tool_name}")
                    
                    # Get image tool selection from scene_plans
                    image_tool_name = self._get_image_tool_for_scene(
                        scene_number=scene_number,
                        scene_plans=scene_plans
                    )
                    
                    self.logger.info(f"  Selected image tool: {image_tool_name}")
                    
                    # Step 1: Generate static image
                    self.logger.info(f"  Step 1/2: Generating image...")
                    image_path = self._generate_image(
                        prompt=scene_prompt,
                        scene_number=scene_number,
                        output_dir=output_dir,
                        image_tool_name=image_tool_name
                    )
                    
                    # Step 2: Animate image to video
                    if video_tool_name and video_tool_name != "none":
                        self.logger.info(f"  Step 2/2: Animating with {video_tool_name}...")
                        video_result = self._animate_image(
                            image_path=image_path,
                            video_tool_name=video_tool_name,
                            scene_description=scene_description,
                            scene_number=scene_number,
                            output_dir=output_dir
                        )
                        
                        video_path = video_result["video_path"]
                        total_cost += video_result.get("cost", 0.0)
                        total_time += video_result.get("time", 0)
                    else:
                        # No animation - convert static image to video
                        self.logger.info(f"  Step 2/2: Converting static image to video...")
                        video_path = self._static_to_video(
                            image_path=image_path,
                            duration=scene.get("duration", 2.0),
                            scene_number=scene_number,
                            output_dir=output_dir
                        )
                
                scene_videos.append(video_path)
                self.logger.info(f"  ✓ Scene {scene_number} complete: {video_path}")
                
            except Exception as e:
                self.logger.error(f"  ✗ Scene {scene_number} failed: {e}")
                # Skip scene - no Ken Burns fallback (looks cheap)
                # User can retry with different tool or accept fewer scenes
                self.logger.warning(f"  Skipping scene {scene_number} (no fallback)")
                continue
        
        self.logger.info(f"Visual production complete: {len(scene_videos)} videos generated")
        self.logger.info(f"Total cost: ${total_cost:.2f}")
        self.logger.info(f"Total time: {total_time}s")
        
        return {
            "scene_videos": scene_videos,
            "all_images": scene_videos,  # For backward compatibility
            "total_videos": len(scene_videos),
            "total_cost": total_cost,
            "total_time": total_time
        }
    
    def _get_video_tool_for_scene(
        self,
        scene_number: int,
        content_type: str,
        scene_plans: List[Dict[str, Any]] = None
    ) -> str:
        """
        Get the video tool to use for this scene.
        
        Args:
            scene_number: Scene number (1-indexed)
            content_type: Content type from Creative Strategist
            scene_plans: Optional tool selection from Workflow Router
        
        Returns:
            Video tool name (e.g., "minimax_hailuo")
        """
        # If we have scene_plans from router, use that
        if scene_plans:
            for plan in scene_plans:
                # Handle both dict and dataclass formats
                plan_scene_num = getattr(plan, 'scene_number', plan.get('scene_number') if isinstance(plan, dict) else None)
                if plan_scene_num == scene_number:
                    return getattr(plan, 'video_tool', plan.get('video_tool', 'runway_gen4') if isinstance(plan, dict) else 'runway_gen4')
        
        # Otherwise, use content_type to decide
        tool_mapping = {
            "human_action": "minimax_hailuo",
            "human_portrait": "minimax_hailuo",
            "object": "luma_ray",
            "product": "runway_gen4",
            "text": "none",  # No animation for text
            "transition": "pika_v2",
            "abstract": "wan_i2v"
        }
        
        return tool_mapping.get(content_type, "runway_gen4")
    
    def _get_image_tool_for_scene(
        self,
        scene_number: int,
        scene_plans: List[Dict[str, Any]] = None
    ) -> str:
        """
        Get the image tool to use for this scene.
        
        Args:
            scene_number: Scene number (1-indexed)
            scene_plans: Optional tool selection from Workflow Router
        
        Returns:
            Image tool name (e.g., "flux_dev", "midjourney")
        """
        # CRITICAL: Scene 1 MUST use Midjourney for scroll-stopping opening frame
        # This is a viral video best practice - override router if needed
        if scene_number == 1:
            self.logger.info("  🎬 Enforcing Midjourney for Scene 1 (opening frame)")
            return "midjourney"
        
        # For other scenes, check router's recommendation
        if scene_plans:
            for plan in scene_plans:
                # Handle both dict and dataclass formats
                plan_scene_num = getattr(plan, 'scene_number', plan.get('scene_number') if isinstance(plan, dict) else None)
                if plan_scene_num == scene_number:
                    image_tool = getattr(plan, 'image_tool', plan.get('image_tool') if isinstance(plan, dict) else None)
                    if image_tool:
                        return image_tool
        
        # Otherwise, use default based on quality setting
        return self.default_image_tool
    
    def _generate_image(
        self,
        prompt: str,
        scene_number: int,
        output_dir: str,
        suffix: str = "image",
        image_tool_name: str = None
    ) -> str:
        """
        Generate static image using specified image tool.
        
        Args:
            prompt: Image generation prompt
            scene_number: Scene number for filename
            output_dir: Output directory
            suffix: Filename suffix (e.g., "start", "end", "image")
            image_tool_name: Name of image tool to use (e.g., "flux_dev", "midjourney")
        
        Returns:
            Path to generated image
        """
        # Select image tool
        if not image_tool_name:
            image_tool_name = self.default_image_tool
        
        image_tool = self.image_tools.get(image_tool_name)
        if not image_tool:
            self.logger.warning(f"Image tool '{image_tool_name}' not found, using default '{self.default_image_tool}'")
            image_tool = self.image_tools[self.default_image_tool]
        
        result = image_tool.run({
            "prompt": prompt,
            "output_dir": output_dir,
            "filename": f"scene_{scene_number:02d}_{suffix}.png",
            "aspect_ratio": "9:16",  # Force vertical format for social media
        })
        
        # Handle different return formats
        if "image_path" in result:
            return result["image_path"]
        elif "images" in result and len(result["images"]) > 0:
            return result["images"][0]
        else:
            raise ValueError("No image path found in result")
    
    def _create_morph_video(
        self,
        start_image: str,
        end_image: str,
        scene_description: str,
        scene_number: int,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Create morph video from two images using Pika.
        
        Args:
            start_image: Path to start image
            end_image: Path to end image
            scene_description: Description for motion prompt
            scene_number: Scene number for filename
            output_dir: Output directory
        
        Returns:
            Dictionary with video_path, cost, time
        """
        import time as time_module
        
        # Get Pika tool
        pika_tool = self.video_tools.get("pika_v2")
        
        if not pika_tool:
            raise Exception("Pika tool not available for morph generation")
        
        start_time = time_module.time()
        
        # Run Pika with dual images for morph
        result = pika_tool.run({
            "start_image": start_image,
            "end_image": end_image,
            "prompt": scene_description or "smooth transition",
            "duration": 5,
            "output_dir": output_dir,
            "filename": f"scene_{scene_number:02d}_morph.mp4"
        })
        
        elapsed_time = time_module.time() - start_time
        
        return {
            "video_path": result["video_path"],
            "cost": result.get("cost_estimate", 0.15),
            "time": int(elapsed_time)
        }
    
    def _animate_image(
        self,
        image_path: str,
        video_tool_name: str,
        scene_description: str,
        scene_number: int,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Animate static image to video using selected tool.
        
        Args:
            image_path: Path to static image
            video_tool_name: Name of video tool to use
            scene_description: Description for motion prompt
            scene_number: Scene number for filename
            output_dir: Output directory
        
        Returns:
            Dictionary with video_path, cost, time
        """
        import time as time_module
        
        # Get the tool
        video_tool = self.video_tools.get(video_tool_name)
        
        if not video_tool:
            self.logger.warning(f"Video tool '{video_tool_name}' not found, using runway_gen4")
            video_tool = self.video_tools["runway_gen4"]
        
        start_time = time_module.time()
        
        # Run the tool
        result = video_tool.run({
            "image_path": image_path,
            "prompt": scene_description,
            "duration": 5,  # Standard 5 seconds
            "output_dir": output_dir,
            "filename": f"scene_{scene_number:02d}_video.mp4"
        })
        
        elapsed_time = time_module.time() - start_time
        
        return {
            "video_path": result["video_path"],
            "cost": result.get("cost_estimate", 0.10),
            "time": int(elapsed_time)
        }
    
    def _static_to_video(
        self,
        image_path: str,
        duration: float,
        scene_number: int,
        output_dir: str
    ) -> str:
        """
        Convert static image to video with Ken Burns effect (zoom + pan).
        
        Args:
            image_path: Path to static image
            duration: Video duration in seconds
            scene_number: Scene number for filename
            output_dir: Output directory
        
        Returns:
            Path to video file
        """
        import subprocess
        import random
        
        output_path = os.path.join(output_dir, f"scene_{scene_number:02d}_kenburns.mp4")
        
        # Ken Burns effect: slow zoom in with slight pan
        # Randomize direction for variety
        zoom_direction = random.choice(["in", "out"])
        pan_direction = random.choice(["left", "right", "up", "down"])
        
        if zoom_direction == "in":
            # Zoom in: start at 1.0, end at 1.2 (20% zoom)
            zoom_start = 1.0
            zoom_end = 1.2
        else:
            # Zoom out: start at 1.2, end at 1.0
            zoom_start = 1.2
            zoom_end = 1.0
        
        # Pan movement (subtle)
        if pan_direction == "left":
            x_start, x_end = "(iw-iw/zoom)/2+50", "(iw-iw/zoom)/2-50"
        elif pan_direction == "right":
            x_start, x_end = "(iw-iw/zoom)/2-50", "(iw-iw/zoom)/2+50"
        else:
            x_start, x_end = "(iw-iw/zoom)/2", "(iw-iw/zoom)/2"
        
        if pan_direction == "up":
            y_start, y_end = "(ih-ih/zoom)/2+50", "(ih-ih/zoom)/2-50"
        elif pan_direction == "down":
            y_start, y_end = "(ih-ih/zoom)/2-50", "(ih-ih/zoom)/2+50"
        else:
            y_start, y_end = "(ih-ih/zoom)/2", "(ih-ih/zoom)/2"
        
        # Build zoompan filter
        # Format: zoompan=z='zoom_expr':x='x_expr':y='y_expr':d=frames:s=WxH
        fps = 30
        frames = int(duration * fps)
        
        # Zoompan filter with proper zoom interpolation
        # z: interpolate from zoom_start to zoom_end over the duration
        # x, y: pan from start to end positions
        # d: duration in frames
        # s: output size (1080x1920 for 9:16)
        # fps: frames per second
        
        zoompan_filter = (
            f"zoompan="
            f"z='{zoom_start}+({zoom_end}-{zoom_start})*on/{frames}':"  # Proper zoom interpolation
            f"x='{x_start}+(({x_end})-({x_start}))*on/{frames}':"  # Pan X
            f"y='{y_start}+(({y_end})-({y_start}))*on/{frames}':"  # Pan Y
            f"d={frames}:"  # Duration in frames
            f"s=1080x1920:"  # Output size (9:16)
            f"fps={fps}"  # Frame rate
        )
        
        self.logger.info(f"  Applying Ken Burns effect: {zoom_direction} zoom + {pan_direction} pan")
        
        # Use FFMPEG to create video with Ken Burns effect
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", zoompan_filter,
            "-r", str(fps),
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # If Ken Burns fails, fall back to simple static
            self.logger.warning(f"  Ken Burns effect failed, using simple static: {e}")
            cmd_simple = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", image_path,
                "-c:v", "libx264",
                "-t", str(duration),
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920",  # 9:16 vertical
                output_path
            ]
            subprocess.run(cmd_simple, check=True, capture_output=True)
        
        return output_path
    
    def _fallback_scene_generation(
        self,
        scene_prompt: str,
        scene_number: int,
        duration: float,
        output_dir: str
    ) -> str:
        """
        Fallback: Generate image and convert to static video.
        
        Args:
            scene_prompt: Image prompt
            scene_number: Scene number
            duration: Video duration
            output_dir: Output directory
        
        Returns:
            Path to video file
        """
        # Generate image
        image_path = self._generate_image(
            prompt=scene_prompt,
            scene_number=scene_number,
            output_dir=output_dir
        )
        
        # Convert to static video
        video_path = self._static_to_video(
            image_path=image_path,
            duration=duration,
            scene_number=scene_number,
            output_dir=output_dir
        )
        
        return video_path


# Export
__all__ = ["VisualProductionAgent"]
