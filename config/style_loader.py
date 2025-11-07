"""
Video Style Configuration Loader

Loads and validates video style presets from video_styles.json.
Provides modular, extensible system for adding new styles.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class StyleLoader:
    """Loads and manages video style configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize style loader.
        
        Args:
            config_path: Path to video_styles.json (optional)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "video_styles.json"
        
        self.config_path = Path(config_path)
        self.styles = self._load_styles()
        
        logger.info(f"Loaded {len(self.styles)} video styles: {list(self.styles.keys())}")
    
    def _load_styles(self) -> Dict[str, Any]:
        """Load styles from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                styles = json.load(f)
            return styles
        except FileNotFoundError:
            logger.error(f"Style config not found: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in style config: {e}")
            return {}
    
    def get_style(self, style_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific style.
        
        Args:
            style_name: Name of the style (e.g., "character", "cinematic")
        
        Returns:
            Style configuration dict or None if not found
        """
        style = self.styles.get(style_name)
        
        if style is None:
            logger.warning(f"Style '{style_name}' not found. Available: {list(self.styles.keys())}")
        
        return style
    
    def list_styles(self) -> list:
        """Get list of available style names."""
        return list(self.styles.keys())
    
    def get_workflow_for_scene(
        self,
        style_name: str,
        scene_number: int,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get workflow configuration for a specific scene.
        
        Args:
            style_name: Name of the style
            scene_number: Scene number (1-indexed)
            content_type: Content type (e.g., "human_action", "object")
        
        Returns:
            Workflow configuration for this scene
        """
        style = self.get_style(style_name)
        
        if style is None:
            return {}
        
        workflow = style.get("workflow", {})
        
        # Scene 1 has special configuration
        if scene_number == 1:
            return workflow.get("scene_1", {})
        
        # Scenes 2+ use scene_2_plus configuration
        scene_config = workflow.get("scene_2_plus", {})
        
        # For hybrid style, select based on content_type
        if style_name == "hybrid" and content_type:
            is_character = content_type in ["human_action", "human_portrait", "character"]
            
            # Replace conditional keys with actual values
            resolved_config = {}
            for key, value in scene_config.items():
                if key.endswith("_if_character") and is_character:
                    new_key = key.replace("_if_character", "")
                    resolved_config[new_key] = value
                elif key.endswith("_if_object") and not is_character:
                    new_key = key.replace("_if_object", "")
                    resolved_config[new_key] = value
                elif not key.endswith("_if_character") and not key.endswith("_if_object"):
                    resolved_config[key] = value
            
            return resolved_config
        
        return scene_config
    
    def get_transition_type(
        self,
        style_name: str,
        from_content_type: Optional[str] = None,
        to_content_type: Optional[str] = None
    ) -> str:
        """
        Get transition type between scenes.
        
        Args:
            style_name: Name of the style
            from_content_type: Content type of previous scene
            to_content_type: Content type of next scene
        
        Returns:
            Transition type (e.g., "pika_morph", "crossfade")
        """
        style = self.get_style(style_name)
        
        if style is None:
            return "crossfade"  # Default fallback
        
        transitions = style.get("transitions", {})
        transition_type = transitions.get("type", "crossfade")
        
        # Smart transitions for hybrid style
        if transition_type == "smart" and from_content_type and to_content_type:
            is_from_character = from_content_type in ["human_action", "human_portrait", "character"]
            is_to_character = to_content_type in ["human_action", "human_portrait", "character"]
            
            if is_from_character and is_to_character:
                return transitions.get("character_to_character", "pika_morph")
            elif not is_from_character and not is_to_character:
                return transitions.get("object_to_object", "crossfade")
            else:
                return transitions.get("mixed", "crossfade")
        
        return transition_type
    
    def should_use_character_consistency(
        self,
        style_name: str,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Check if character consistency should be enforced.
        
        Args:
            style_name: Name of the style
            content_type: Content type of the scene
        
        Returns:
            True if character consistency should be used
        """
        style = self.get_style(style_name)
        
        if style is None:
            return False
        
        char_config = style.get("character_consistency", {})
        enabled = char_config.get("enabled", False)
        
        if not enabled:
            return False
        
        # For hybrid style, only enforce for character scenes
        only_for_character = char_config.get("only_for_character_scenes", False)
        
        if only_for_character and content_type:
            is_character = content_type in ["human_action", "human_portrait", "character"]
            return is_character
        
        return True
    
    def get_reference_scene(self, style_name: str) -> int:
        """
        Get the scene number to use as reference for consistency.
        
        Args:
            style_name: Name of the style
        
        Returns:
            Reference scene number (usually 1)
        """
        style = self.get_style(style_name)
        
        if style is None:
            return 1
        
        char_config = style.get("character_consistency", {})
        return char_config.get("reference_scene", 1)


# Global style loader instance
_style_loader = None

def get_style_loader() -> StyleLoader:
    """Get global style loader instance (singleton)."""
    global _style_loader
    
    if _style_loader is None:
        _style_loader = StyleLoader()
    
    return _style_loader
