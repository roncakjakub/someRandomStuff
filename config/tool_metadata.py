"""
Tool Metadata for Workflow AI Decision Making

This module contains metadata about all available tools to help the workflow AI
make intelligent decisions about which tool to use for each task.
"""

from typing import Dict, List, Any

# Tool metadata for AI decision making
TOOL_METADATA: Dict[str, Dict[str, Any]] = {
    
    # ===== VIDEO GENERATION TOOLS =====
    
    "veo31_flf2v": {
        "type": "video_generation",
        "mode": "first_last_frame",
        "provider": "fal.ai",
        "requires": ["first_frame_image", "last_frame_image", "prompt"],
        "outputs": ["video_path"],
        "strengths": [
            "smooth_morphing",
            "character_consistency",
            "premium_quality",
            "precise_transitions"
        ],
        "weaknesses": [
            "expensive",
            "content_policy_strict",
            "slow_generation"
        ],
        "cost_per_video": 0.80,
        "generation_time_seconds": 180,
        "aspect_ratios": ["9:16"],
        "duration_seconds": 8,
        "use_cases": [
            "character_transitions",
            "morph_effects",
            "premium_content",
            "smooth_scene_changes"
        ],
        "fallback_priority": 1,  # Primary choice
        "fallback_tools": ["minimax_i2v", "luma_i2v", "minimax_t2v"]
    },
    
    "minimax_i2v": {
        "type": "video_generation",
        "mode": "image_to_video",
        "provider": "replicate",
        "requires": ["first_frame_image", "prompt"],
        "outputs": ["video_path"],
        "strengths": [
            "preserves_aspect_ratio",
            "character_consistency",
            "good_quality",
            "affordable"
        ],
        "weaknesses": [
            "less_smooth_than_veo",
            "limited_duration_options"
        ],
        "cost_per_video": 0.28,
        "generation_time_seconds": 90,
        "aspect_ratios": ["follows_input_image"],
        "duration_seconds": [6, 10],
        "use_cases": [
            "character_animation",
            "scene_transitions",
            "general_i2v",
            "affordable_quality"
        ],
        "fallback_priority": 2,  # First fallback for Veo
        "fallback_tools": ["luma_i2v", "wan_i2v", "minimax_t2v"]
    },
    
    "minimax_t2v": {
        "type": "video_generation",
        "mode": "text_to_video",
        "provider": "replicate",
        "requires": ["prompt"],
        "outputs": ["video_path"],
        "strengths": [
            "no_image_required",
            "fast_generation",
            "affordable",
            "creative_freedom"
        ],
        "weaknesses": [
            "no_consistency",
            "fixed_16_9_aspect",
            "no_control_over_first_frame"
        ],
        "cost_per_video": 0.28,
        "generation_time_seconds": 70,
        "aspect_ratios": ["16:9"],
        "duration_seconds": [6, 10],
        "use_cases": [
            "general_scenes",
            "establishing_shots",
            "no_consistency_needed",
            "quick_generation"
        ],
        "fallback_priority": 4,  # Last resort
        "fallback_tools": []
    },
    
    "luma_i2v": {
        "type": "video_generation",
        "mode": "image_to_video",
        "provider": "replicate",
        "requires": ["first_frame_image", "prompt"],
        "outputs": ["video_path"],
        "strengths": [
            "smooth_motion",
            "high_quality",
            "good_physics",
            "reliable"
        ],
        "weaknesses": [
            "expensive",
            "slower_than_minimax"
        ],
        "cost_per_video": 0.50,
        "generation_time_seconds": 120,
        "aspect_ratios": ["follows_input_image"],
        "duration_seconds": 5,
        "use_cases": [
            "premium_quality",
            "smooth_animations",
            "reliable_fallback"
        ],
        "fallback_priority": 3,  # Second fallback
        "fallback_tools": ["wan_i2v", "minimax_t2v"]
    },
    
    "wan_i2v": {
        "type": "video_generation",
        "mode": "image_to_video",
        "provider": "replicate",
        "requires": ["first_frame_image", "prompt"],
        "outputs": ["video_path"],
        "strengths": [
            "balanced_cost_quality",
            "fast_generation",
            "reliable"
        ],
        "weaknesses": [
            "medium_quality",
            "less_smooth_than_luma"
        ],
        "cost_per_video": 0.40,
        "generation_time_seconds": 45,
        "aspect_ratios": ["follows_input_image"],
        "duration_seconds": 5,
        "use_cases": [
            "general_purpose",
            "balanced_workflow",
            "fast_turnaround"
        ],
        "fallback_priority": 3,  # Alternative to Luma
        "fallback_tools": ["minimax_t2v"]
    },
    
    # ===== IMAGE GENERATION TOOLS =====
    
    "midjourney": {
        "type": "image_generation",
        "mode": "text_to_image",
        "provider": "apiframe",
        "requires": ["prompt"],
        "outputs": ["image_path"],
        "strengths": [
            "premium_quality",
            "artistic_style",
            "cinematic_look",
            "high_detail"
        ],
        "weaknesses": [
            "expensive",
            "slower",
            "less_control"
        ],
        "cost_per_image": 0.05,
        "generation_time_seconds": 60,
        "aspect_ratios": ["1:1", "16:9", "9:16", "custom"],
        "use_cases": [
            "opening_frames",
            "hero_shots",
            "premium_content",
            "artistic_style"
        ],
        "fallback_priority": 1,
        "fallback_tools": ["flux_dev", "flux_schnell"]
    },
    
    "instant_character": {
        "type": "image_generation",
        "mode": "text_to_image_with_reference",
        "provider": "fal.ai",
        "requires": ["prompt", "reference_image_url"],
        "outputs": ["image_path"],
        "strengths": [
            "character_consistency",
            "reference_based",
            "good_quality",
            "fast"
        ],
        "weaknesses": [
            "requires_reference",
            "limited_to_characters"
        ],
        "cost_per_image": 0.04,
        "generation_time_seconds": 30,
        "aspect_ratios": ["1:1", "16:9", "9:16"],
        "use_cases": [
            "character_scenes",
            "consistency_required",
            "character_driven_stories"
        ],
        "fallback_priority": 1,
        "fallback_tools": ["flux_kontext_pro", "flux_dev"]
    },
    
    "flux_dev": {
        "type": "image_generation",
        "mode": "text_to_image",
        "provider": "replicate",
        "requires": ["prompt"],
        "outputs": ["image_path"],
        "strengths": [
            "balanced_quality",
            "affordable",
            "reliable",
            "good_detail"
        ],
        "weaknesses": [
            "not_premium",
            "slower_than_schnell"
        ],
        "cost_per_image": 0.03,
        "generation_time_seconds": 20,
        "aspect_ratios": ["1:1", "16:9", "9:16", "custom"],
        "use_cases": [
            "general_purpose",
            "balanced_workflow",
            "test_images",
            "reliable_fallback"
        ],
        "fallback_priority": 2,
        "fallback_tools": ["flux_schnell"]
    },
    
    "flux_schnell": {
        "type": "image_generation",
        "mode": "text_to_image",
        "provider": "replicate",
        "requires": ["prompt"],
        "outputs": ["image_path"],
        "strengths": [
            "very_fast",
            "very_cheap",
            "reliable",
            "good_for_testing"
        ],
        "weaknesses": [
            "lower_quality",
            "less_detail"
        ],
        "cost_per_image": 0.02,
        "generation_time_seconds": 5,
        "aspect_ratios": ["1:1", "16:9", "9:16", "custom"],
        "use_cases": [
            "testing",
            "drafts",
            "budget_content",
            "fast_iteration"
        ],
        "fallback_priority": 3,
        "fallback_tools": []
    },
}


# Workflow-specific tool recommendations
WORKFLOW_RECOMMENDATIONS = {
    "pika": {
        "description": "Premium character-driven content with smooth transitions",
        "image_tools": ["midjourney", "instant_character", "flux_dev"],
        "video_tools": ["veo31_flf2v", "minimax_i2v"],
        "estimated_cost_per_scene": 0.90,
        "use_cases": ["character_stories", "premium_content", "smooth_transitions"]
    },
    
    "hybrid": {
        "description": "Balanced quality and cost for general content",
        "image_tools": ["flux_dev", "instant_character"],
        "video_tools": ["wan_i2v", "minimax_i2v"],
        "estimated_cost_per_scene": 0.45,
        "use_cases": ["general_content", "balanced_workflow", "mixed_scenes"]
    },
    
    "kontext": {
        "description": "Environment-focused content with spatial consistency",
        "image_tools": ["midjourney", "flux_kontext_pro"],
        "video_tools": ["wan_i2v", "minimax_i2v"],
        "estimated_cost_per_scene": 0.50,
        "use_cases": ["interior_design", "architecture", "environment_focused"]
    },
    
    "budget": {
        "description": "Fast and affordable content for testing and drafts",
        "image_tools": ["flux_schnell"],
        "video_tools": ["minimax_t2v", "wan_i2v"],
        "estimated_cost_per_scene": 0.30,
        "use_cases": ["testing", "drafts", "budget_content", "fast_iteration"]
    }
}


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """Get metadata for a specific tool."""
    return TOOL_METADATA.get(tool_name, {})


def get_fallback_tools(tool_name: str) -> List[str]:
    """Get list of fallback tools for a given tool."""
    metadata = get_tool_metadata(tool_name)
    return metadata.get("fallback_tools", [])


def get_tools_by_type(tool_type: str) -> List[str]:
    """Get all tools of a specific type (e.g., 'video_generation')."""
    return [
        name for name, meta in TOOL_METADATA.items()
        if meta.get("type") == tool_type
    ]


def get_tools_by_mode(mode: str) -> List[str]:
    """Get all tools of a specific mode (e.g., 'image_to_video')."""
    return [
        name for name, meta in TOOL_METADATA.items()
        if meta.get("mode") == mode
    ]


def get_workflow_tools(workflow_name: str) -> Dict[str, List[str]]:
    """Get recommended tools for a specific workflow."""
    workflow = WORKFLOW_RECOMMENDATIONS.get(workflow_name, {})
    return {
        "image_tools": workflow.get("image_tools", []),
        "video_tools": workflow.get("video_tools", [])
    }


# Export
__all__ = [
    "TOOL_METADATA",
    "WORKFLOW_RECOMMENDATIONS",
    "get_tool_metadata",
    "get_fallback_tools",
    "get_tools_by_type",
    "get_tools_by_mode",
    "get_workflow_tools"
]
