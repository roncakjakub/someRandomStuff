"""
Veo 3.1 First-Last-Frame-to-Video Tool
Google's latest video generation model for smooth morph transitions
"""

import fal_client
from typing import Dict, Any, Optional
import os


class Veo31FLF2VTool:
    """
    Generate videos by animating between first and last frames using Google's Veo 3.1 Fast.
    
    Best for:
    - Smooth morph transitions between scenes
    - Natural motion and realistic animations
    - Character consistency across frames
    - High-quality 8-second videos
    """
    
    def __init__(self):
        self.model_id = "fal-ai/veo3.1/fast/first-last-frame-to-video"
        self.cost_per_second = 0.10  # $0.10/second without audio
        self.cost_per_second_audio = 0.15  # $0.15/second with audio
        self.duration = 8  # Fixed 8 seconds
        
    def execute(
        self,
        first_frame_url: str,
        last_frame_url: str,
        prompt: str,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = False,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video morphing from first frame to last frame.
        
        Args:
            first_frame_url: URL of the first frame
            last_frame_url: URL of the last frame
            prompt: Description of how to animate between frames
                   Should include: action, style, camera motion (optional), ambiance (optional)
            resolution: "720p" or "1080p" (default: "720p")
            aspect_ratio: "16:9", "9:16", "1:1", or "auto" (default: "16:9")
            generate_audio: Whether to generate audio (default: False, saves 33%)
            output_path: Optional path to save the video file
            
        Returns:
            Dict with video URL, cost, and metadata
            
        Example prompt structure:
            "A woman slowly sits up in bed and stretches her arms. 
             Cinematic style with warm morning lighting. 
             Static camera with soft focus. 
             Peaceful and energizing ambiance."
        """
        
        # Validate inputs
        if not first_frame_url or not last_frame_url:
            raise ValueError("Both first_frame_url and last_frame_url are required")
        
        if not prompt:
            raise ValueError("Prompt is required to describe the animation")
        
        # Prepare request
        request_data = {
            "first_frame_url": first_frame_url,
            "last_frame_url": last_frame_url,
            "prompt": prompt,
            "duration": "8s",  # Fixed at 8 seconds
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "generate_audio": generate_audio
        }
        
        print(f"🎬 Generating Veo 3.1 video...")
        print(f"   First frame: {first_frame_url}")
        print(f"   Last frame: {last_frame_url}")
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   Resolution: {resolution}, Aspect: {aspect_ratio}")
        print(f"   Audio: {'Yes' if generate_audio else 'No'}")
        
        # Call fal.ai API
        try:
            result = fal_client.subscribe(
                self.model_id,
                arguments=request_data
            )
            
            # Extract video URL
            video_url = result.get("video", {}).get("url")
            
            if not video_url:
                raise ValueError("No video URL in response")
            
            # Calculate cost
            cost = self.duration * (
                self.cost_per_second_audio if generate_audio 
                else self.cost_per_second
            )
            
            # Download video if output path specified
            if output_path:
                import requests
                response = requests.get(video_url)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Video saved to: {output_path}")
            
            print(f"✅ Veo 3.1 video generated!")
            print(f"   Duration: {self.duration}s")
            print(f"   Cost: ${cost:.2f}")
            print(f"   URL: {video_url}")
            
            return {
                "video_url": video_url,
                "duration": self.duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "has_audio": generate_audio,
                "cost": cost,
                "model": self.model_id,
                "local_path": output_path if output_path else None
            }
            
        except Exception as e:
            print(f"❌ Veo 3.1 generation failed: {str(e)}")
            raise


def create_morph_prompt(
    scene1_description: str,
    scene2_description: str,
    style: str = "cinematic",
    camera_motion: Optional[str] = None,
    ambiance: Optional[str] = None
) -> str:
    """
    Helper function to create well-structured Veo 3.1 prompts.
    
    Args:
        scene1_description: What's happening in the first frame
        scene2_description: What's happening in the last frame
        style: Visual style (default: "cinematic")
        camera_motion: Optional camera movement description
        ambiance: Optional mood/atmosphere description
        
    Returns:
        Formatted prompt string
        
    Example:
        >>> create_morph_prompt(
        ...     "woman sleeping in bed",
        ...     "woman sitting up and stretching",
        ...     style="warm cinematic",
        ...     camera_motion="static wide angle",
        ...     ambiance="peaceful morning energy"
        ... )
        "A woman transitions from sleeping in bed to sitting up and stretching. 
         Warm cinematic style. Static wide angle camera. Peaceful morning energy ambiance."
    """
    
    # Build action description
    action = f"Transition from {scene1_description} to {scene2_description}"
    
    # Build full prompt
    parts = [action]
    
    if style:
        parts.append(f"{style} style")
    
    if camera_motion:
        parts.append(f"{camera_motion} camera")
    
    if ambiance:
        parts.append(f"{ambiance} ambiance")
    
    return ". ".join(parts) + "."


# Example usage
if __name__ == "__main__":
    tool = Veo31FLF2VTool()
    
    # Test with example frames
    result = tool.execute(
        first_frame_url="https://example.com/frame1.jpg",
        last_frame_url="https://example.com/frame2.jpg",
        prompt=create_morph_prompt(
            "woman sleeping peacefully",
            "woman sitting up and stretching arms",
            style="warm cinematic",
            camera_motion="static wide angle",
            ambiance="peaceful morning energy"
        ),
        resolution="720p",
        aspect_ratio="16:9",
        generate_audio=False,
        output_path="test_morph.mp4"
    )
    
    print(f"\n✅ Test completed!")
    print(f"Video URL: {result['video_url']}")
    print(f"Cost: ${result['cost']:.2f}")
