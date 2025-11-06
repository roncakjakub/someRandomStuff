"""
Test script for Wan 2.5 i2v video generation.
Verifies that Wan correctly inherits 9:16 aspect ratio from input image.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.wan_video import WanVideoTool
from tools.replicate_image import FluxSchnellTool
import os

def test_wan_video():
    """Test Wan video generation with 9:16 aspect ratio."""
    print("=" * 60)
    print("Testing Wan 2.5 i2v Video Generation")
    print("=" * 60)
    
    # Step 1: Generate test image in 9:16
    print("\n[1/3] Generating test image with Flux in 9:16...")
    image_tool = FluxSchnellTool()
    
    image_result = image_tool.run({
        "prompt": "Abstract flowing liquid art, vibrant colors, artistic style",
        "aspect_ratio": "9:16",  # CRITICAL: Must be 9:16
        "output_dir": "output/test"
    })
    
    if not image_result.get("success"):
        print(f"❌ Image generation failed: {image_result.get('error')}")
        return False
    
    image_path = image_result["images"][0]
    print(f"✅ Image generated: {image_path}")
    
    # Verify image aspect ratio
    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height",
             "-of", "csv=p=0", image_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            width, height = result.stdout.strip().split(',')
            print(f"✅ Image dimensions: {width}×{height}")
            aspect = int(width) / int(height)
            expected = 9 / 16
            if abs(aspect - expected) < 0.01:
                print("✅ Image aspect ratio correct: 9:16")
            else:
                print(f"⚠️  Image aspect ratio: {aspect:.3f} (expected {expected:.3f})")
    except:
        pass
    
    # Step 2: Test Wan video generation
    print("\n[2/3] Testing Wan 2.5 i2v API...")
    print("Key insight:")
    print("  - Wan inherits aspect ratio from input image")
    print("  - No explicit aspect_ratio parameter")
    print("  - Input image MUST be 9:16 for output to be 9:16")
    
    video_tool = WanVideoTool()
    
    try:
        video_result = video_tool.run({
            "image_path": image_path,
            "prompt": "The liquid flows and swirls in mesmerizing patterns",
            "output_dir": "output/test",
            "fast_mode": True  # Use fast model for quicker testing
        })
        
        if not video_result.get("success"):
            print(f"❌ Video generation failed: {video_result.get('error')}")
            return False
        
        video_path = video_result["video_path"]
        print(f"✅ Video generated: {video_path}")
        
        # Step 3: Verify video aspect ratio
        print("\n[3/3] Verifying video aspect ratio...")
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"✅ Video file exists: {file_size:.2f} MB")
            
            # Check video properties
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
                    
                    # Verify aspect ratio (9:16)
                    aspect = int(width) / int(height)
                    expected_aspect = 9 / 16
                    if abs(aspect - expected_aspect) < 0.01:
                        print(f"✅ Aspect ratio correct: {width}×{height} (9:16)")
                        print("✅ Wan correctly inherited 9:16 from input image!")
                    else:
                        print(f"❌ Aspect ratio WRONG: {width}×{height}")
                        print(f"   Expected 9:16, got {aspect:.3f}")
                        print("   This means input image was not 9:16!")
                        return False
            except FileNotFoundError:
                print("⚠️  ffprobe not available, skipping video verification")
            
            print("\n" + "=" * 60)
            print("✅ WAN TEST PASSED")
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
    success = test_wan_video()
    sys.exit(0 if success else 1)
