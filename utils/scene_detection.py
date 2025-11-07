"""
Scene Detection Utilities for HYBRID Style
Auto-detects scene changes for smart transition selection
"""
import re
from typing import Dict, List, Any


class SceneDetector:
    """
    Detects scene changes between shots for HYBRID style workflow.
    
    Rules:
    1. Location change → CUT
    2. Subject change (person ↔ object) → CUT
    3. Time jump → CUT
    4. Camera distance jump → CUT
    5. Otherwise → MORPH (same scene)
    """
    
    # Location keywords
    LOCATIONS = [
        "garden", "kitchen", "bedroom", "bathroom", "living room", "office",
        "street", "park", "beach", "mountain", "forest", "city",
        "cafe", "restaurant", "bar", "shop", "store", "mall",
        "studio", "stage", "gym", "pool", "spa"
    ]
    
    # Time keywords
    TIME_PERIODS = {
        "dawn": 1,
        "morning": 2,
        "noon": 3,
        "afternoon": 4,
        "evening": 5,
        "dusk": 6,
        "night": 7,
        "midnight": 8
    }
    
    # Human content types
    HUMAN_TYPES = ["human_portrait", "human_action", "person", "character"]
    
    # Object content types
    OBJECT_TYPES = ["object", "product", "food", "nature", "landscape", "abstract"]
    
    @classmethod
    def detect_scene_groups(cls, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect scene groups and transitions.
        
        Args:
            scenes: List of scene dictionaries with 'description' and 'content_type'
        
        Returns:
            List of scenes with added 'scene_group' and 'transition' fields
        """
        if not scenes:
            return []
        
        # First scene starts a new group
        current_group = 1
        scenes[0]["scene_group"] = current_group
        scenes[0]["transition"] = "morph"  # First scene has no transition
        
        for i in range(1, len(scenes)):
            prev_scene = scenes[i - 1]
            curr_scene = scenes[i]
            
            # Check if scene change
            is_cut = cls.is_scene_change(prev_scene, curr_scene)
            
            if is_cut:
                # New scene group
                current_group += 1
                curr_scene["transition"] = "cut"
            else:
                # Same scene group
                curr_scene["transition"] = "morph"
            
            curr_scene["scene_group"] = current_group
        
        return scenes
    
    @classmethod
    def is_scene_change(cls, scene1: Dict[str, Any], scene2: Dict[str, Any]) -> bool:
        """
        Detect if there's a major scene change between two scenes.
        
        Returns:
            True: Hard cut (new scene)
            False: Pika morph (same scene)
        """
        desc1 = scene1.get("description", "").lower()
        desc2 = scene2.get("description", "").lower()
        
        content1 = scene1.get("content_type", "general")
        content2 = scene2.get("content_type", "general")
        
        # Rule 1: Location change
        if cls._location_changed(desc1, desc2):
            return True
        
        # Rule 2: Subject change (person ↔ object)
        if cls._subject_changed(content1, content2):
            return True
        
        # Rule 3: Time jump
        if cls._time_jump(desc1, desc2):
            return True
        
        # Rule 4: Camera distance jump
        if cls._camera_distance_jump(desc1, desc2):
            return True
        
        return False
    
    @classmethod
    def _location_changed(cls, desc1: str, desc2: str) -> bool:
        """Detect location change from descriptions."""
        locations1 = [loc for loc in cls.LOCATIONS if loc in desc1]
        locations2 = [loc for loc in cls.LOCATIONS if loc in desc2]
        
        # If both have locations and they're different
        if locations1 and locations2:
            return not any(loc in locations2 for loc in locations1)
        
        return False
    
    @classmethod
    def _subject_changed(cls, content1: str, content2: str) -> bool:
        """Detect subject change (person ↔ object)."""
        is_human1 = content1 in cls.HUMAN_TYPES
        is_human2 = content2 in cls.HUMAN_TYPES
        
        # Person → Object or Object → Person
        return is_human1 != is_human2
    
    @classmethod
    def _time_jump(cls, desc1: str, desc2: str) -> bool:
        """Detect time jump from descriptions."""
        time1 = cls._extract_time(desc1)
        time2 = cls._extract_time(desc2)
        
        # If both have time and jump more than 1 period
        if time1 and time2:
            return abs(time1 - time2) > 1
        
        return False
    
    @classmethod
    def _extract_time(cls, description: str) -> int:
        """Extract time period from description."""
        for keyword, value in cls.TIME_PERIODS.items():
            if keyword in description:
                return value
        return 0
    
    @classmethod
    def _camera_distance_jump(cls, desc1: str, desc2: str) -> bool:
        """Detect camera distance jump."""
        # Close-up keywords
        close_keywords = ["close-up", "macro", "detail", "zoom"]
        
        # Wide shot keywords
        wide_keywords = ["wide", "landscape", "panorama", "aerial", "establishing"]
        
        is_close1 = any(kw in desc1 for kw in close_keywords)
        is_wide1 = any(kw in desc1 for kw in wide_keywords)
        
        is_close2 = any(kw in desc2 for kw in close_keywords)
        is_wide2 = any(kw in desc2 for kw in wide_keywords)
        
        # Close → Wide or Wide → Close
        if (is_close1 and is_wide2) or (is_wide1 and is_close2):
            return True
        
        return False
    
    @classmethod
    def get_scene_summary(cls, scenes: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable summary of scene grouping.
        
        Args:
            scenes: List of scenes with scene_group and transition fields
        
        Returns:
            Formatted summary string
        """
        if not scenes:
            return "No scenes"
        
        summary = []
        current_group = None
        group_scenes = []
        
        for scene in scenes:
            group = scene.get("scene_group", 1)
            
            if group != current_group:
                # New group
                if group_scenes:
                    summary.append(cls._format_group(current_group, group_scenes))
                
                current_group = group
                group_scenes = [scene]
            else:
                group_scenes.append(scene)
        
        # Add last group
        if group_scenes:
            summary.append(cls._format_group(current_group, group_scenes))
        
        return "\n".join(summary)
    
    @classmethod
    def _format_group(cls, group_num: int, scenes: List[Dict[str, Any]]) -> str:
        """Format a scene group for display."""
        lines = [f"\nScene Group {group_num}: ({len(scenes)} shots)"]
        
        for scene in scenes:
            num = scene.get("number", scene.get("scene_number", "?"))
            desc = scene.get("description", "")
            transition = scene.get("transition", "morph")
            
            arrow = " → MORPH" if transition == "morph" else " → CUT"
            lines.append(f"  Shot {num}: {desc}{arrow}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Test scene detection
    test_scenes = [
        {"number": 1, "description": "woman waking up in bedroom", "content_type": "human_portrait"},
        {"number": 2, "description": "woman stretching in bedroom", "content_type": "human_action"},
        {"number": 3, "description": "woman walking to kitchen", "content_type": "human_action"},
        {"number": 4, "description": "coffee beans close-up on counter", "content_type": "product"},
        {"number": 5, "description": "coffee grinder in action", "content_type": "object"},
        {"number": 6, "description": "pouring coffee into cup", "content_type": "object"},
        {"number": 7, "description": "woman drinking coffee in kitchen", "content_type": "human_portrait"},
        {"number": 8, "description": "woman smiling with cup", "content_type": "human_portrait"},
    ]
    
    detector = SceneDetector()
    scenes_with_groups = detector.detect_scene_groups(test_scenes)
    
    print("Scene Detection Results:")
    print("="*60)
    print(detector.get_scene_summary(scenes_with_groups))
    print("\n" + "="*60)
    
    for scene in scenes_with_groups:
        print(f"Shot {scene['number']}: Group {scene['scene_group']}, Transition: {scene['transition']}")
