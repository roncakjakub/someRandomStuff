"""
Test script for Runway Gen-4 video generation.
Tests the fixes for Issue #1: Runway API 400 error.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.runway_video import RunwayVideoTool
from tools.replicate_image import FluxSchnellTool
import os

def test_runway_video():
    """Test Runway video generation with fixed API."""
    print("=" * 60)
    print("Testing Runway Gen-4 Video Generation")
    print("=" * 60)
    
    # Step 1: Generate test image
    print("\n[1/3] Generating test image with Flux...")
    image_tool = FluxSchnellTool()
    
    image_result = image_tool.run({
        "prompt": "A steaming cup of coffee on a wooden table, morning light, photorealistic",
        "aspect_ratio": "9:16",
        "output_dir": "output/test"
    })
    
    if not image_result.get("success"):
        print(f"❌ Image generation failed: {image_result.get('error')}")
        return False
    
    image_path = image_result["images"][0]
    print(f"✅ Image generated: {image_path}")
    
    # Step 2: Test Runway video generation
    print("\n[2/3] Testing Runway Gen-4 API...")
    print("Fixes applied:")
    print("  - X-Runway-Version header added")
    print("  - Endpoint changed to /image_to_video")
    print("  - Aspect ratio mapping: 9:16 → 720:1280")
    print("  - Position parameter added")
    
    video_tool = RunwayVideoTool()
    
    try:
        video_result = video_tool.run({
            "image_path": image_path,
            "prompt": "Camera slowly zooms in on the coffee cup, steam rising gently",
            "duration": 5,
            "output_dir": "output/test"
        })
        
        if not video_result.get("success"):
            print(f"❌ Video generation failed: {video_result.get('error')}")
            return False
        
        video_path = video_result["video_path"]
        print(f"✅ Video generated: {video_path}")
        
        # Step 3: Verify video
        print("\n[3/3] Verifying video...")
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"✅ Video file exists: {file_size:.2f} MB")
            
            # Check video properties with ffprobe if available
            try:
                import subprocess
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=width,height,duration",
                     "-of", "csv=p=0", video_path],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    width, height, duration = result.stdout.strip().split(',')
                    print(f"✅ Video properties: {width}×{height}, {float(duration):.1f}s")
                    
                    # Verify aspect ratio
                    if width == "720" and height == "1280":
                        print("✅ Aspect ratio correct: 720×1280 (9:16)")
                    else:
                        print(f"⚠️  Aspect ratio: {width}×{height} (expected 720×1280)")
            except FileNotFoundError:
                print("⚠️  ffprobe not available, skipping video verification")
            
            print("\n" + "=" * 60)
            print("✅ RUNWAY TEST PASSED")
            print("=" * 60)
            return True
        else:
            print(f"❌ Video file not found: {video_path}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_runway_video()
    sys.exit(0 if success else 1)
