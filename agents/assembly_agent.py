"""
Final Assembly Agent - Phase 5
Assembles all components into final video.
"""
from typing import Dict, Any, List
import logging
from tools import VideoAssemblyTool

logger = logging.getLogger(__name__)


class AssemblyAgent:
    """
    Agent responsible for assembling final video.
    Combines images and audio using FFMPEG.
    """
    
    def __init__(self):
        self.name = "Final Assembly Agent"
        self.assembly_tool = VideoAssemblyTool()
        self.logger = logging.getLogger(f"agents.{self.name}")
    
    def assemble_video(
        self,
        images: List[str],
        audio_path: str = None,
        duration_per_image: float = 3.0,
        output_dir: str = None
    ) -> Dict[str, Any]:
        """
        Assemble final video from components.
        
        Args:
            images: List of image file paths
            audio_path: Optional audio file path
            duration_per_image: Duration to show each image
            
        Returns:
            Dictionary with video path and metadata
        """
        self.logger.info(f"Assembling final video from {len(images)} images...")
        
        # Calculate duration per image based on audio if provided
        if audio_path:
            # TODO: Get actual audio duration
            # For now, use equal distribution
            pass
        
        # Assemble video
        result = self.assembly_tool.run({
            "images": images,
            "audio_path": audio_path,
            "duration_per_image": duration_per_image,
            "output_dir": output_dir,
        })
        
        if result.get("success"):
            video_path = result.get("video_path")
            self.logger.info(f"Video assembled successfully: {video_path}")
            
            return {
                "video_path": video_path,
                "num_images": len(images),
                "has_audio": audio_path is not None,
            }
        else:
            self.logger.error("Video assembly failed")
            raise Exception(f"Video assembly failed: {result.get('error')}")
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with final video
        """
        # Check if we have video clips (new workflow) or images (legacy)
        scene_videos = state.get("scene_videos", [])
        images = state.get("all_images", [])
        audio_path = state.get("voiceover_audio")
        output_dir = state.get("run_output_dir")
        
        # Prefer video clips over images
        if scene_videos:
            self.logger.info(f"Assembling {len(scene_videos)} video clips with transitions...")
            
            # Use new transition-based assembly
            video_result = self.assembly_tool.create_video_with_transitions(
                video_clips=scene_videos,
                audio_path=audio_path,
                transition_duration=0.3,  # 300ms crossfade
                output_dir=output_dir
            )
            
            return {
                **state,
                "final_video": video_result.get("video_path"),
                "video_metadata": {
                    "num_clips": video_result.get("num_clips"),
                    "has_audio": video_result.get("has_audio"),
                    "has_transitions": video_result.get("has_transitions"),
                }
            }
        
        elif images:
            # Legacy path: images only
            self.logger.info(f"Assembling {len(images)} images (legacy mode)...")
            
            if not images:
                raise Exception("No images available for video assembly")
            
            # Calculate duration per image
            duration_per_image = 3.0  # Default
            if audio_path:
                # Estimate: ~15 characters per second of speech
                script = state.get("voiceover_script", "")
                estimated_duration = len(script) / 15
                duration_per_image = estimated_duration / len(images)
                # Clamp between 2 and 5 seconds
                duration_per_image = max(2.0, min(5.0, duration_per_image))
            
            video_result = self.assemble_video(
                images=images,
                audio_path=audio_path,
                duration_per_image=duration_per_image,
                output_dir=output_dir
            )
            
            return {
                **state,
                "final_video": video_result.get("video_path"),
                "video_metadata": {
                    "num_images": video_result.get("num_images"),
                    "has_audio": video_result.get("has_audio"),
                    "duration_per_image": duration_per_image,
                }
            }
        
        else:
            raise Exception("No video clips or images available for assembly")


if __name__ == "__main__":
    # Test the agent
    agent = AssemblyAgent()
    
    # This would need actual files to test
    # test_state = {
    #     "all_images": ["image1.png", "image2.png", "image3.png"],
    #     "voiceover_audio": "voiceover.mp3",
    #     "voiceover_script": "This is a test script."
    # }
    # result = agent.run(test_state)
    # print(result)
