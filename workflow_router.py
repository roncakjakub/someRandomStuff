"""
AI-Powered Workflow Router

Intelligently decides which tools to use based on the request,
optimizing for cost, speed, and quality.
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
    required_for: List[str]  # Scenarios where this tool is mandatory


@dataclass
class WorkflowPlan:
    """Optimized workflow plan."""
    tools: List[str]  # List of tool names to use
    reasoning: str  # Why these tools were selected
    estimated_cost: float  # Total estimated cost
    estimated_time: int  # Total estimated time in seconds
    quality_level: str  # "budget", "standard", "premium"


class WorkflowRouter:
    """
    AI-Powered Workflow Router
    
    Analyzes video requests and intelligently selects which tools to use
    based on requirements, budget, time constraints, and quality expectations.
    """
    
    # Tool specifications
    TOOLS = {
        "midjourney": ToolSpec(
            name="midjourney",
            description="Cinematic opening frames with dramatic lighting and composition",
            cost=0.05,
            speed=300,  # 5 minutes
            use_cases=["cinematic", "dramatic", "hero shots", "premium quality"],
            required_for=["cinematic opening", "premium quality"]
        ),
        "flux_schnell": ToolSpec(
            name="flux_schnell",
            description="Fast image generation for general scenes (4 inference steps)",
            cost=0.02,
            speed=10,
            use_cases=["fast", "budget", "general scenes", "filler shots"],
            required_for=[]
        ),
        "flux_dev": ToolSpec(
            name="flux_dev",
            description="High-quality image generation (28 inference steps)",
            cost=0.03,
            speed=30,
            use_cases=["standard quality", "detailed scenes", "balanced cost/quality"],
            required_for=[]
        ),
        "flux_pro": ToolSpec(
            name="flux_pro",
            description="Premium image generation (25 inference steps)",
            cost=0.04,
            speed=25,
            use_cases=["premium quality", "professional work", "high detail"],
            required_for=[]
        ),
        "seedream4": ToolSpec(
            name="seedream4",
            description="Character consistency across multiple scenes",
            cost=0.04,
            speed=30,
            use_cases=["character", "person", "consistency", "multiple shots of same subject"],
            required_for=["character consistency", "person in video"]
        ),
        "ideogram": ToolSpec(
            name="ideogram",
            description="Text overlays and typography generation",
            cost=0.02,
            speed=15,
            use_cases=["text", "typography", "words", "quotes", "captions"],
            required_for=["text overlay", "typography"]
        ),
        "luma": ToolSpec(
            name="luma",
            description="Video animation - converts static images to moving video clips",
            cost=0.10,  # per clip
            speed=120,  # 2 minutes per clip
            use_cases=["motion", "animation", "viral quality", "smooth movement"],
            required_for=["video animation", "moving video"]
        ),
        "ken_burns": ToolSpec(
            name="ken_burns",
            description="Static images with pan/zoom effects (free, instant)",
            cost=0.00,
            speed=1,
            use_cases=["budget", "fast", "simple motion", "slideshow"],
            required_for=[]
        ),
        "elevenlabs": ToolSpec(
            name="elevenlabs",
            description="Professional voiceover in 29 languages - ALWAYS REQUIRED for engaging videos",
            cost=0.05,
            speed=10,
            use_cases=["voiceover", "narration", "multilingual", "ALL VIDEOS"],
            required_for=["voiceover", "ALL VIDEOS", "ALWAYS"]  # Always include voiceover!
        )
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the router with OpenAI client."""
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        logger.info("Workflow Router initialized")
    
    def analyze_request(
        self,
        topic: str,
        requirements: Dict[str, Any],
        max_cost: Optional[float] = None,
        max_time: Optional[int] = None,
        quality_preset: Optional[str] = None
    ) -> WorkflowPlan:
        """
        Analyze the request and generate an optimized workflow plan.
        
        Args:
            topic: Video topic/subject
            requirements: Dict with keys like:
                - character_consistency: bool
                - text_overlay: bool
                - motion_required: bool (video animation vs static)
                - style: str ("cinematic", "casual", "corporate")
                - language: str
            max_cost: Maximum budget in USD (optional)
            max_time: Maximum time in seconds (optional)
            quality_preset: "budget", "standard", "premium" (optional)
        
        Returns:
            WorkflowPlan with selected tools and reasoning
        """
        logger.info(f"Analyzing request for topic: {topic}")
        
        # Build tool catalog for AI
        tool_catalog = self._build_tool_catalog()
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            topic=topic,
            requirements=requirements,
            tool_catalog=tool_catalog,
            max_cost=max_cost,
            max_time=max_time,
            quality_preset=quality_preset
        )
        
        # Get AI recommendation
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert workflow optimizer for AI video generation. You analyze requests and select the optimal combination of tools based on requirements, budget, time, and quality expectations."
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
            logger.info(f"AI recommendation: {result}")
            
            # Parse and validate the plan
            plan = self._parse_plan(result)
            
            # Apply constraints
            plan = self._apply_constraints(plan, max_cost, max_time)
            
            logger.info(f"Final plan: {plan.tools}, cost: ${plan.estimated_cost:.2f}, time: {plan.estimated_time}s")
            
            return plan
            
        except Exception as e:
            logger.error(f"Router analysis failed: {e}")
            # Fallback to standard workflow
            return self._fallback_plan(requirements)
    
    def _build_tool_catalog(self) -> str:
        """Build a formatted catalog of available tools."""
        catalog = []
        for tool_name, spec in self.TOOLS.items():
            catalog.append(f"""
**{spec.name}**
- Description: {spec.description}
- Cost: ${spec.cost:.2f} per use
- Speed: {spec.speed}s
- Use cases: {', '.join(spec.use_cases)}
- Required for: {', '.join(spec.required_for) if spec.required_for else 'Optional'}
""")
        return "\n".join(catalog)
    
    def _build_analysis_prompt(
        self,
        topic: str,
        requirements: Dict[str, Any],
        tool_catalog: str,
        max_cost: Optional[float],
        max_time: Optional[int],
        quality_preset: Optional[str]
    ) -> str:
        """Build the analysis prompt for the AI."""
        
        constraints = []
        if max_cost:
            constraints.append(f"- Maximum budget: ${max_cost:.2f}")
        if max_time:
            constraints.append(f"- Maximum time: {max_time}s ({max_time//60}min)")
        if quality_preset:
            constraints.append(f"- Quality preset: {quality_preset}")
        
        constraints_text = "\n".join(constraints) if constraints else "- No specific constraints"
        
        prompt = f"""
Analyze this video generation request and recommend the optimal set of tools to use.

**VIDEO REQUEST:**
- Topic: {topic}
- Requirements: {json.dumps(requirements, indent=2)}

**CONSTRAINTS:**
{constraints_text}

**AVAILABLE TOOLS:**
{tool_catalog}

**YOUR TASK:**
1. Analyze what the video needs based on the topic and requirements
2. Select the MINIMUM set of tools needed to achieve the goal
3. Balance cost, speed, and quality
4. Prioritize tools that are "required_for" the specific use case
5. Consider cheaper/faster alternatives when appropriate

**DECISION RULES:**
- If character consistency needed → MUST use seedream4
- If text overlay needed → MUST use ideogram
- If motion_required=true → Use luma (premium) OR ken_burns (budget)
- If motion_required=false → Use ken_burns only
- For opening frame: Use midjourney (premium) OR flux_dev (standard) OR flux_schnell (budget)
- For general scenes: Use flux_dev (standard) OR flux_schnell (budget)
- Voiceover: ALWAYS use elevenlabs

**QUALITY PRESETS:**
- budget: flux_schnell + ken_burns + skip optional tools
- standard: flux_dev + luma (if motion needed) + essential tools only
- premium: midjourney + luma + all relevant tools

**OUTPUT FORMAT (JSON):**
{{
  "selected_tools": ["tool1", "tool2", ...],
  "reasoning": "Why these tools were selected and why others were skipped",
  "estimated_cost": 0.00,
  "estimated_time": 0,
  "quality_level": "budget|standard|premium",
  "alternatives": "Cheaper/faster alternatives if applicable"
}}

Respond ONLY with valid JSON.
"""
        return prompt
    
    def _parse_plan(self, result: Dict[str, Any]) -> WorkflowPlan:
        """Parse AI response into a WorkflowPlan."""
        return WorkflowPlan(
            tools=result.get("selected_tools", []),
            reasoning=result.get("reasoning", ""),
            estimated_cost=float(result.get("estimated_cost", 0.0)),
            estimated_time=int(result.get("estimated_time", 0)),
            quality_level=result.get("quality_level", "standard")
        )
    
    def _apply_constraints(
        self,
        plan: WorkflowPlan,
        max_cost: Optional[float],
        max_time: Optional[int]
    ) -> WorkflowPlan:
        """Apply hard constraints and adjust plan if needed."""
        
        # Check cost constraint
        if max_cost and plan.estimated_cost > max_cost:
            logger.warning(f"Plan exceeds budget (${plan.estimated_cost:.2f} > ${max_cost:.2f}), applying cost optimization")
            plan = self._optimize_for_cost(plan, max_cost)
        
        # Check time constraint
        if max_time and plan.estimated_time > max_time:
            logger.warning(f"Plan exceeds time limit ({plan.estimated_time}s > {max_time}s), applying speed optimization")
            plan = self._optimize_for_speed(plan, max_time)
        
        return plan
    
    def _optimize_for_cost(self, plan: WorkflowPlan, max_cost: float) -> WorkflowPlan:
        """Optimize plan to fit within cost budget."""
        # Replace expensive tools with cheaper alternatives
        new_tools = []
        new_cost = 0.0
        
        for tool in plan.tools:
            # Replacements
            if tool == "midjourney" and new_cost + 0.02 <= max_cost:
                new_tools.append("flux_schnell")
                new_cost += 0.02
            elif tool == "luma" and new_cost + 0.00 <= max_cost:
                new_tools.append("ken_burns")
                new_cost += 0.00
            elif tool == "flux_dev" and new_cost + 0.02 <= max_cost:
                new_tools.append("flux_schnell")
                new_cost += 0.02
            else:
                spec = self.TOOLS.get(tool)
                if spec and new_cost + spec.cost <= max_cost:
                    new_tools.append(tool)
                    new_cost += spec.cost
        
        plan.tools = new_tools
        plan.estimated_cost = new_cost
        plan.reasoning += f" [Cost-optimized to fit ${max_cost:.2f} budget]"
        
        return plan
    
    def _optimize_for_speed(self, plan: WorkflowPlan, max_time: int) -> WorkflowPlan:
        """Optimize plan to fit within time budget."""
        # Replace slow tools with faster alternatives
        new_tools = []
        new_time = 0
        
        for tool in plan.tools:
            # Replacements
            if tool == "midjourney" and new_time + 10 <= max_time:
                new_tools.append("flux_schnell")
                new_time += 10
            elif tool == "luma" and new_time + 1 <= max_time:
                new_tools.append("ken_burns")
                new_time += 1
            else:
                spec = self.TOOLS.get(tool)
                if spec and new_time + spec.speed <= max_time:
                    new_tools.append(tool)
                    new_time += spec.speed
        
        plan.tools = new_tools
        plan.estimated_time = new_time
        plan.reasoning += f" [Speed-optimized to fit {max_time}s time limit]"
        
        return plan
    
    def _fallback_plan(self, requirements: Dict[str, Any]) -> WorkflowPlan:
        """Generate a fallback plan if AI analysis fails."""
        logger.warning("Using fallback plan due to router failure")
        
        tools = ["flux_dev", "elevenlabs"]
        cost = 0.03 + 0.05
        time = 30 + 10
        
        if requirements.get("character_consistency"):
            tools.append("seedream4")
            cost += 0.04
            time += 30
        
        if requirements.get("text_overlay"):
            tools.append("ideogram")
            cost += 0.02
            time += 15
        
        if requirements.get("motion_required"):
            tools.append("luma")
            cost += 0.10
            time += 120
        else:
            tools.append("ken_burns")
        
        return WorkflowPlan(
            tools=tools,
            reasoning="Fallback plan: standard quality with essential tools",
            estimated_cost=cost,
            estimated_time=time,
            quality_level="standard"
        )


# Preset configurations for common scenarios
PRESETS = {
    "budget": {
        "description": "Fast and cheap, good for testing or high-volume production",
        "requirements": {
            "motion_required": False,
            "quality_preset": "budget"
        },
        "max_cost": 0.15
    },
    "standard": {
        "description": "Balanced quality and cost, good for most use cases",
        "requirements": {
            "motion_required": True,
            "quality_preset": "standard"
        },
        "max_cost": 0.50
    },
    "premium": {
        "description": "Maximum quality, best for important content",
        "requirements": {
            "motion_required": True,
            "quality_preset": "premium"
        },
        "max_cost": None  # No limit
    },
    "viral": {
        "description": "Optimized for viral potential (motion + character + text)",
        "requirements": {
            "motion_required": True,
            "character_consistency": True,
            "text_overlay": True,
            "quality_preset": "premium"
        },
        "max_cost": 1.50
    }
}


def get_preset(preset_name: str) -> Dict[str, Any]:
    """Get a preset configuration by name."""
    return PRESETS.get(preset_name, PRESETS["standard"])


if __name__ == "__main__":
    # Test the router
    import os
    
    router = WorkflowRouter(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test 1: Budget video
    print("\n=== TEST 1: Budget Video ===")
    plan = router.analyze_request(
        topic="morning coffee ritual",
        requirements={"motion_required": False},
        max_cost=0.15,
        quality_preset="budget"
    )
    print(f"Tools: {plan.tools}")
    print(f"Cost: ${plan.estimated_cost:.2f}")
    print(f"Time: {plan.estimated_time}s")
    print(f"Reasoning: {plan.reasoning}")
    
    # Test 2: Premium video with character
    print("\n=== TEST 2: Premium Video ===")
    plan = router.analyze_request(
        topic="personal morning routine",
        requirements={
            "character_consistency": True,
            "text_overlay": True,
            "motion_required": True
        },
        quality_preset="premium"
    )
    print(f"Tools: {plan.tools}")
    print(f"Cost: ${plan.estimated_cost:.2f}")
    print(f"Time: {plan.estimated_time}s")
    print(f"Reasoning: {plan.reasoning}")
    
    # Test 3: Fast video (time constraint)
    print("\n=== TEST 3: Fast Video ===")
    plan = router.analyze_request(
        topic="quick motivational quote",
        requirements={"text_overlay": True},
        max_time=60,  # 1 minute max
        quality_preset="standard"
    )
    print(f"Tools: {plan.tools}")
    print(f"Cost: ${plan.estimated_cost:.2f}")
    print(f"Time: {plan.estimated_time}s")
    print(f"Reasoning: {plan.reasoning}")
