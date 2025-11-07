"""
AI-Powered Workflow Router v2

Intelligently decides which tools to use for each scene based on content analysis,
optimizing for cost, speed, and quality with support for multiple video generation tools.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class ToolSpec:
    """Specification for an AI tool."""
    name: str
    description: str
    cost: float  # USD per use
    speed: int  # seconds
    use_cases: List[str]
    best_for: str  # What this tool excels at


@dataclass
class ScenePlan:
    """Plan for a single scene."""
    scene_number: int
    description: str
    image_tool: str  # Tool to generate the image
    video_tool: str  # Tool to animate the image
    reasoning: str  # Why these tools were selected


@dataclass
class WorkflowPlan:
    """Optimized workflow plan with per-scene tool selection."""
    image_tools: List[str]  # Unique image generation tools needed
    video_tools: List[str]  # Unique video animation tools needed
    scene_plans: List[ScenePlan]  # Per-scene tool selection
    reasoning: str  # Overall strategy
    estimated_cost: float  # Total estimated cost
    estimated_time: int  # Total estimated time in seconds
    quality_level: str  # "budget", "standard", "premium"


class WorkflowRouterV2:
    """
    AI-Powered Workflow Router V2
    
    Analyzes video requests and intelligently selects which tools to use
    for EACH SCENE based on content type, requirements, budget, and quality.
    """
    
    # Image generation tools
    IMAGE_TOOLS = {
        "midjourney": ToolSpec(
            name="midjourney",
            description="Cinematic images with dramatic lighting",
            cost=0.05,
            speed=300,
            use_cases=["cinematic", "dramatic", "hero shots", "premium"],
            best_for="Opening frames and premium quality shots"
        ),
        "flux_schnell": ToolSpec(
            name="flux_schnell",
            description="Fast image generation (4 steps)",
            cost=0.02,
            speed=10,
            use_cases=["fast", "budget", "general scenes"],
            best_for="Budget mode and filler shots"
        ),
        "flux_dev": ToolSpec(
            name="flux_dev",
            description="High-quality images (28 steps)",
            cost=0.03,
            speed=30,
            use_cases=["standard", "detailed", "balanced"],
            best_for="Standard quality scenes"
        ),
        "flux_pro": ToolSpec(
            name="flux_pro",
            description="Premium images (25 steps)",
            cost=0.04,
            speed=25,
            use_cases=["premium", "professional", "high detail"],
            best_for="Premium quality scenes"
        ),
        "seedream4": ToolSpec(
            name="seedream4",
            description="Character consistency across scenes",
            cost=0.04,
            speed=30,
            use_cases=["character", "person", "consistency"],
            best_for="Multiple shots of the same person/character"
        ),
        "ideogram": ToolSpec(
            name="ideogram",
            description="Text overlays and typography",
            cost=0.02,
            speed=15,
            use_cases=["text", "typography", "quotes"],
            best_for="Scenes with text overlays"
        ),
    }
    
    # Video animation tools
    VIDEO_TOOLS = {
        "runway_gen4_turbo": ToolSpec(
            name="runway_gen4_turbo",
            description="Premium image-to-video with high quality ($0.05/sec)",
            cost=0.25,  # 5 seconds @ $0.05/sec
            speed=90,
            use_cases=["premium", "products", "high-end"],
            best_for="Premium product shots and high-end scenes (EXPENSIVE)"
        ),
        "pika_v2": ToolSpec(
            name="pika_v2",
            description="Smooth morphs and creative effects ($0.15/video)",
            cost=0.15,
            speed=120,
            use_cases=["morphs", "transitions", "creative effects"],
            best_for="Smooth transitions between states, dynamic morphs"
        ),
        "minimax_hailuo": ToolSpec(
            name="minimax_hailuo",
            description="Realistic human motion and VFX ($0.30/video)",
            cost=0.30,
            speed=180,
            use_cases=["humans", "characters", "gestures", "emotions"],
            best_for="Scenes with people - realistic motion and expressions"
        ),
        "luma_ray": ToolSpec(
            name="luma_ray",
            description="High-quality versatile image-to-video ($0.03/sec)",
            cost=0.15,  # 5 seconds @ $0.03/sec
            speed=150,
            use_cases=["universal", "standard", "reliable", "general"],
            best_for="Default choice for most scenes - best quality/price ratio"
        ),
        "wan_i2v": ToolSpec(
            name="wan_i2v",
            description="Budget-friendly animation ($0.08/video)",
            cost=0.08,
            speed=60,
            use_cases=["budget", "fast", "basic animation"],
            best_for="Budget mode - cheapest option"
        ),
        "ken_burns": ToolSpec(
            name="ken_burns",
            description="Static pan/zoom effects (free, instant)",
            cost=0.00,
            speed=1,
            use_cases=["budget", "fast", "simple motion"],
            best_for="Extreme budget mode - no real animation"
        ),
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the router with OpenAI client."""
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.available_tools = self._check_available_tools()
        logger.info(f"Workflow Router V2 initialized - {len(self.available_tools['image'])} image tools, {len(self.available_tools['video'])} video tools available")
    
    def _check_available_tools(self) -> Dict[str, List[str]]:
        """Check which tools are available based on API keys."""
        import os
        available = {
            "image": [],
            "video": []
        }
        
        # Image tools (Replicate)
        if os.getenv("REPLICATE_API_TOKEN"):
            available["image"].extend(["flux_schnell", "flux_dev", "flux_pro"])
        
        if os.getenv("APIFRAME_API_KEY"):
            available["image"].append("midjourney")
        
        # Seedream4 and Ideogram also on Replicate
        if os.getenv("REPLICATE_API_TOKEN"):
            available["image"].extend(["seedream4", "ideogram"])
        
        # Video tools
        if os.getenv("REPLICATE_API_TOKEN"):
            available["video"].extend(["minimax_hailuo", "luma_ray", "wan_i2v"])
        
        if os.getenv("RUNWAY_API_KEY"):
            available["video"].append("runway_gen4_turbo")
        
        if os.getenv("FAL_KEY"):
            available["video"].append("pika_v2")
        
        # Ken Burns is always available (local)
        available["video"].append("ken_burns")
        
        return available
    
    def analyze_request(
        self,
        topic: str,
        scenes: List[Dict[str, Any]] = None,
        brand_identity: Any = None,
        max_cost: Optional[float] = None,
        max_time: Optional[int] = None,
        quality_preset: Optional[str] = None,
        video_style: str = "cinematic"
    ) -> WorkflowPlan:
        """
        Analyze the request and generate an optimized workflow plan with per-scene tool selection.
        
        Args:
            topic: Video topic/subject
            scenes: List of scene dictionaries with content_type (from Creative Strategist)
            brand_identity: Optional brand identity object
            max_cost: Maximum budget in USD (optional)
            max_time: Maximum time in seconds (optional)
            quality_preset: "budget", "standard", "premium", "viral" (optional)
            video_style: Video style preset ("character", "cinematic", "pika", "hybrid")
        
        Returns:
            WorkflowPlan with per-scene tool selection
        """
        num_scenes = len(scenes) if scenes else 8
        logger.info(f"Analyzing request for topic: {topic}, {num_scenes} scenes")
        
        # Build tool catalogs (only available tools)
        available_image_tools = {k: v for k, v in self.IMAGE_TOOLS.items() if k in self.available_tools["image"]}
        available_video_tools = {k: v for k, v in self.VIDEO_TOOLS.items() if k in self.available_tools["video"]}
        
        image_catalog = self._build_catalog(available_image_tools)
        video_catalog = self._build_catalog(available_video_tools)
        
        logger.info(f"Available tools - Images: {list(available_image_tools.keys())}, Videos: {list(available_video_tools.keys())}")
        
        # Warn if critical tools are missing
        if "runway_gen4_turbo" not in self.available_tools["video"]:
            logger.warning("RUNWAY_API_KEY not found - Runway Gen-4 Turbo unavailable")
        if "pika_v2" not in self.available_tools["video"]:
            logger.warning("FAL_KEY not found - Pika v2 unavailable")
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            topic=topic,
            scenes=scenes,
            brand_identity=brand_identity,
            image_catalog=image_catalog,
            video_catalog=video_catalog,
            max_cost=max_cost,
            max_time=max_time,
            quality_preset=quality_preset,
            video_style=video_style
        )
        
        # Get AI recommendation
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert workflow optimizer for AI video generation.
You analyze video topics and select the optimal tools for EACH SCENE based on:
- Content type (humans vs objects vs text)
- Quality requirements
- Budget constraints
- Time constraints

Key principles:
1. Use Minimax Hailuo for scenes with people/characters
2. Use Runway Gen-4 Turbo as default (best price/quality)
3. Use Pika for smooth transitions/morphs
4. Use Luma for cinematic product shots
5. Use Wan i2v for extreme budget mode
6. Never use Ken Burns unless explicitly budget mode

Return a JSON object with per-scene tool selection."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"AI recommendation received")
            
            # Parse and validate the plan
            plan = self._parse_plan(result, num_scenes)
            
            # Validate style requirements (warnings only)
            self._validate_style_requirements(plan, video_style, scenes)
            
            # Enforce PIKA style rules (hard constraint)
            if video_style == "pika":
                plan = self._enforce_pika_style(plan)
            
            # Apply constraints
            plan = self._apply_constraints(plan, max_cost, max_time)
            
            logger.info(f"Final plan: {len(plan.scene_plans)} scenes, cost: ${plan.estimated_cost:.2f}, time: {plan.estimated_time}s")
            
            return plan
            
        except Exception as e:
            logger.error(f"Router analysis failed: {e}")
            # Fallback to standard workflow
            return self._fallback_plan(num_scenes, quality_preset)
    
    def _build_catalog(self, tools: Dict[str, ToolSpec]) -> str:
        """Build a formatted catalog of tools."""
        catalog = []
        for tool_name, spec in tools.items():
            catalog.append(f"""
**{spec.name}**
- Description: {spec.description}
- Cost: ${spec.cost:.2f}
- Speed: {spec.speed}s
- Best for: {spec.best_for}
""")
        return "\n".join(catalog)
    
    def _build_analysis_prompt(
        self,
        topic: str,
        scenes: List[Dict[str, Any]],
        brand_identity: Any,
        image_catalog: str,
        video_catalog: str,
        max_cost: Optional[float],
        max_time: Optional[int],
        quality_preset: Optional[str],
        video_style: str = "cinematic"
    ) -> str:
        """Build the analysis prompt for the AI."""
        
        num_scenes = len(scenes) if scenes else 8
        
        constraints = []
        if max_cost:
            constraints.append(f"- Maximum budget: ${max_cost:.2f}")
        if max_time:
            constraints.append(f"- Maximum time: {max_time}s")
        if quality_preset:
            constraints.append(f"- Quality preset: {quality_preset}")
        
        constraints_text = "\n".join(constraints) if constraints else "- No specific constraints"
        
        # Build scenes context
        scenes_context = ""
        if scenes:
            scenes_list = []
            for i, scene in enumerate(scenes, 1):
                content_type = scene.get("content_type", "unknown")
                description = scene.get("description", scene.get("prompt", "")[:100])
                scenes_list.append(f"  {i}. [{content_type}] {description}")
            scenes_context = "\n".join(scenes_list)
        else:
            scenes_context = f"  (No scene details provided - analyze topic to infer {num_scenes} scenes)"
        
        # Build brand context
        brand_context = ""
        if brand_identity:
            try:
                style = getattr(brand_identity, 'visual_identity', {}).get('style', 'standard')
                mood = getattr(brand_identity, 'visual_identity', {}).get('mood', 'professional')
                brand_context = f"""
**BRAND IDENTITY:**
- Style: {style}
- Mood: {mood}
- Consider brand aesthetic when selecting tools (e.g., luxury brands → Luma, modern brands → Runway)
"""
            except:
                brand_context = ""
        
        prompt = f"""
Analyze this video topic and recommend the optimal tools for EACH SCENE.

**VIDEO REQUEST:**
- Topic: {topic}
- Number of scenes: {num_scenes}
- Video style: {video_style}

**SCENES:**
{scenes_context}
{brand_context}
**CONSTRAINTS:**
{constraints_text}

**AVAILABLE IMAGE TOOLS:**
{image_catalog}

**AVAILABLE VIDEO TOOLS:**
{video_catalog}

**YOUR TASK:**
For each of the {num_scenes} scenes, select:
1. An image generation tool (to create the static frame)
2. A video animation tool (to bring it to life)

Consider:

**IMAGE TOOL SELECTION RULES:** ⭐ CRITICAL

**Scene 1 (Opening Frame):**
- Scene 1 MUST ALWAYS use "midjourney" regardless of preset
- This is a viral video best practice - opening frame must be scroll-stopping
- Exception: Only use flux_schnell if budget preset AND no midjourney available

**Scenes 2+ (All Remaining Scenes):**
- budget preset → flux_schnell (fastest, cheapest)
- standard preset → flux_dev (balanced quality/cost)
- premium preset → flux_pro or flux_dev
- NEVER use ideogram unless text overlay needed
- Use seedream4 if:
  * video_style is "character" AND content_type is "human_portrait" or "human_action"
  * OR video_style is "pika" (for visual consistency across all scenes)

**VIDEO TOOL SELECTION BY CONTENT:**
- If scene content_type is human_action/human_portrait → use luma_ray (best I2V consistency)
- If scene content_type is object/product → use luma_ray (best visual consistency)
- If scene content_type is transition → use pika_v2
- If budget mode → use wan_i2v
- Default → use luma_ray (best image-to-video consistency)
- PREFER luma_ray over minimax_hailuo (luma preserves image style better)
- AVOID runway_gen4_turbo (no credits)
- Match tool quality to brand style (premium → luma_ray, budget → minimax)

Return JSON in this format:
{{
  "reasoning": "Overall strategy explanation",
  "quality_level": "budget|standard|premium",
  "scenes": [
    {{
      "scene_number": 1,
      "description": "Brief scene description",
      "image_tool": "tool_name",
      "video_tool": "tool_name",
      "reasoning": "Why these tools"
    }},
    ...
  ]
}}
"""
        return prompt
    
    def _parse_plan(self, result: Dict[str, Any], num_scenes: int) -> WorkflowPlan:
        """Parse AI response into WorkflowPlan."""
        
        # Extract scene plans
        scene_plans = []
        for scene_data in result.get("scenes", []):
            scene_plan = ScenePlan(
                scene_number=scene_data["scene_number"],
                description=scene_data.get("description", ""),
                image_tool=scene_data["image_tool"],
                video_tool=scene_data["video_tool"],
                reasoning=scene_data.get("reasoning", "")
            )
            scene_plans.append(scene_plan)
        
        # Calculate unique tools needed
        image_tools = list(set(sp.image_tool for sp in scene_plans))
        video_tools = list(set(sp.video_tool for sp in scene_plans))
        
        # Calculate costs and time
        total_cost = 0
        total_time = 0
        
        for scene_plan in scene_plans:
            # Add image generation cost
            if scene_plan.image_tool in self.IMAGE_TOOLS:
                img_spec = self.IMAGE_TOOLS[scene_plan.image_tool]
                total_cost += img_spec.cost
                total_time += img_spec.speed
            
            # Add video animation cost
            if scene_plan.video_tool in self.VIDEO_TOOLS:
                vid_spec = self.VIDEO_TOOLS[scene_plan.video_tool]
                total_cost += vid_spec.cost
                total_time += vid_spec.speed
        
        return WorkflowPlan(
            image_tools=image_tools,
            video_tools=video_tools,
            scene_plans=scene_plans,
            reasoning=result.get("reasoning", ""),
            estimated_cost=total_cost,
            estimated_time=total_time,
            quality_level=result.get("quality_level", "standard")
        )
    
    def _validate_style_requirements(self, plan: WorkflowPlan, video_style: str, scenes: List[Dict[str, Any]]) -> None:
        """
        Validate that scenes match style requirements.
        Logs warnings if scenes don't match expected style.
        
        Args:
            plan: Workflow plan
            video_style: Video style (pika/cinematic/hybrid)
            scenes: List of scene dictionaries
        """
        if video_style == "pika":
            # PIKA requires all scenes to have character
            for i, scene in enumerate(scenes, 1):
                content_type = scene.get("content_type", "object")
                if content_type not in ["human_portrait", "human_action"]:
                    logger.warning(
                        f"⚠️  PIKA style violation: Scene {i} has content_type '{content_type}' "
                        f"but PIKA requires 'human_portrait' or 'human_action' (character in all scenes)!"
                    )
        
        elif video_style == "cinematic":
            # CINEMATIC should focus on products/objects (characters optional)
            character_count = sum(
                1 for scene in scenes
                if scene.get("content_type") in ["human_portrait", "human_action"]
            )
            if character_count > len(scenes) * 0.5:
                logger.warning(
                    f"⚠️  CINEMATIC style suggestion: {character_count}/{len(scenes)} scenes have characters. "
                    f"CINEMATIC style works best with product/object focus."
                )
        
        elif video_style == "hybrid":
            # HYBRID should have mix of character and product scenes
            character_scenes = [
                scene for scene in scenes
                if scene.get("content_type") in ["human_portrait", "human_action"]
            ]
            product_scenes = [
                scene for scene in scenes
                if scene.get("content_type") in ["object", "product", "food", "nature"]
            ]
            
            if not character_scenes:
                logger.warning(
                    f"⚠️  HYBRID style suggestion: No character scenes found. "
                    f"HYBRID works best with mix of character AND product scenes."
                )
            if not product_scenes:
                logger.warning(
                    f"⚠️  HYBRID style suggestion: No product scenes found. "
                    f"HYBRID works best with mix of character AND product scenes."
                )
    
    def _enforce_pika_style(self, plan: WorkflowPlan) -> WorkflowPlan:
        """
        Enforce PIKA style rules (hard constraint).
        
        PIKA style requirements:
        - Scene 1: Midjourney (opening shot)
        - Scenes 2+: Seedream4 (for character/visual consistency)
        - Video tool: pika_v2 (for morph transitions)
        
        This overrides AI recommendations to ensure visual consistency.
        """
        logger.info("Enforcing PIKA style rules...")
        
        for scene_plan in plan.scene_plans:
            # Scene 1: Use Midjourney
            if scene_plan.scene_number == 1:
                if scene_plan.image_tool != "midjourney":
                    logger.info(f"  Scene {scene_plan.scene_number}: Changed {scene_plan.image_tool} → midjourney (PIKA rule)")
                    scene_plan.image_tool = "midjourney"
            
            # Scenes 2+: Use Seedream4 for consistency
            else:
                if scene_plan.image_tool != "seedream4":
                    logger.info(f"  Scene {scene_plan.scene_number}: Changed {scene_plan.image_tool} → seedream4 (PIKA rule)")
                    scene_plan.image_tool = "seedream4"
            
            # All scenes: Use pika_v2 for video (morph transitions)
            if scene_plan.video_tool != "pika_v2" and "pika_v2" in self.available_tools["video"]:
                logger.info(f"  Scene {scene_plan.scene_number}: Changed {scene_plan.video_tool} → pika_v2 (PIKA rule)")
                scene_plan.video_tool = "pika_v2"
        
        # Recalculate plan after changes
        plan = self._recalculate_plan(plan)
        logger.info(f"PIKA style enforced: {len(plan.scene_plans)} scenes, cost: ${plan.estimated_cost:.2f}")
        
        return plan
    
    def _apply_constraints(
        self,
        plan: WorkflowPlan,
        max_cost: Optional[float],
        max_time: Optional[int]
    ) -> WorkflowPlan:
        """Apply budget and time constraints by downgrading tools if needed."""
        
        # Check if constraints are violated
        if max_cost and plan.estimated_cost > max_cost:
            logger.warning(f"Plan exceeds budget (${plan.estimated_cost:.2f} > ${max_cost:.2f}), downgrading...")
            plan = self._downgrade_for_cost(plan, max_cost)
        
        if max_time and plan.estimated_time > max_time:
            logger.warning(f"Plan exceeds time ({plan.estimated_time}s > {max_time}s), optimizing...")
            plan = self._downgrade_for_time(plan, max_time)
        
        return plan
    
    def _downgrade_for_cost(self, plan: WorkflowPlan, max_cost: float) -> WorkflowPlan:
        """Downgrade tools to meet cost constraint."""
        # Replace expensive video tools with cheaper alternatives
        # Order: runway (most expensive) → luma → pika → wan (cheapest)
        for scene_plan in plan.scene_plans:
            if scene_plan.video_tool == "runway_gen4_turbo":
                scene_plan.video_tool = "luma_ray"  # Downgrade from runway to luma
            elif scene_plan.video_tool == "minimax_hailuo":
                scene_plan.video_tool = "luma_ray"  # Downgrade from minimax to luma
            elif scene_plan.video_tool == "luma_ray":
                scene_plan.video_tool = "pika_v2"  # Downgrade from luma to pika
            elif scene_plan.video_tool == "pika_v2":
                scene_plan.video_tool = "wan_i2v"  # Downgrade from pika to wan
        
        # Recalculate cost
        plan = self._recalculate_plan(plan)
        return plan
    
    def _downgrade_for_time(self, plan: WorkflowPlan, max_time: int) -> WorkflowPlan:
        """Downgrade tools to meet time constraint."""
        # Replace slow tools with faster alternatives
        # Fastest: wan (60s) < runway (90s) < luma (150s) < minimax (180s)
        for scene_plan in plan.scene_plans:
            if scene_plan.video_tool == "minimax_hailuo":
                scene_plan.video_tool = "luma_ray"  # Downgrade from minimax to luma
            elif scene_plan.video_tool == "luma_ray":
                scene_plan.video_tool = "runway_gen4_turbo"  # Downgrade from luma to runway (faster)
            elif scene_plan.video_tool == "runway_gen4_turbo":
                scene_plan.video_tool = "wan_i2v"  # Downgrade from runway to wan (fastest)
            if scene_plan.image_tool == "midjourney":
                scene_plan.image_tool = "flux_dev"
        
        # Recalculate time
        plan = self._recalculate_plan(plan)
        return plan
    
    def _recalculate_plan(self, plan: WorkflowPlan) -> WorkflowPlan:
        """Recalculate cost and time after modifications."""
        total_cost = 0
        total_time = 0
        
        for scene_plan in plan.scene_plans:
            if scene_plan.image_tool in self.IMAGE_TOOLS:
                img_spec = self.IMAGE_TOOLS[scene_plan.image_tool]
                total_cost += img_spec.cost
                total_time += img_spec.speed
            
            if scene_plan.video_tool in self.VIDEO_TOOLS:
                vid_spec = self.VIDEO_TOOLS[scene_plan.video_tool]
                total_cost += vid_spec.cost
                total_time += vid_spec.speed
        
        plan.estimated_cost = total_cost
        plan.estimated_time = total_time
        
        # Update unique tools
        plan.image_tools = list(set(sp.image_tool for sp in plan.scene_plans))
        plan.video_tools = list(set(sp.video_tool for sp in plan.scene_plans))
        
        return plan
    
    def _fallback_plan(self, num_scenes: int, quality_preset: Optional[str]) -> WorkflowPlan:
        """Generate a fallback plan if AI analysis fails."""
        logger.info("Using fallback plan")
        
        # Determine tools based on preset
        if quality_preset == "budget":
            image_tool = "flux_schnell"
            video_tool = "wan_i2v"
        elif quality_preset == "premium":
            image_tool = "flux_pro"
            video_tool = "runway_gen4_turbo"
        else:  # standard
            image_tool = "flux_dev"
            video_tool = "luma_ray"  # Changed from runway (cheaper and better default)
        
        # Create scene plans
        scene_plans = []
        for i in range(num_scenes):
            scene_plans.append(ScenePlan(
                scene_number=i + 1,
                description=f"Scene {i + 1}",
                image_tool=image_tool,
                video_tool=video_tool,
                reasoning="Fallback plan"
            ))
        
        # Calculate costs
        img_spec = self.IMAGE_TOOLS[image_tool]
        vid_spec = self.VIDEO_TOOLS[video_tool]
        
        total_cost = num_scenes * (img_spec.cost + vid_spec.cost)
        total_time = num_scenes * (img_spec.speed + vid_spec.speed)
        
        return WorkflowPlan(
            image_tools=[image_tool],
            video_tools=[video_tool],
            scene_plans=scene_plans,
            reasoning="Fallback to standard workflow",
            estimated_cost=total_cost,
            estimated_time=total_time,
            quality_level=quality_preset or "standard"
        )


# Export
__all__ = ["WorkflowRouterV2", "WorkflowPlan", "ScenePlan"]
