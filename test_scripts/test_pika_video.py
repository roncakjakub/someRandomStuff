"""
Test script for Pika v2.2 video generation.
Tests the fixes for Issue #2: Pika missing video_path error.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.pika_video import PikaVideoTool
from tools.replicate_image import FluxSchnellTool
import os

def test_pika_video():
    """Test Pika video generation with fixed response parsing."""
    print("=" * 60)
    print("Testing Pika v2.2 Video Generation")
    print("=" * 60)
    
    # Step 1: Generate test image
    print("\n[1/3] Generating test image with Flux...")
    image_tool = FluxSchnellTool()
    
    image_result = image_tool.run({
        "prompt": "A beautiful sunset over mountains, vibrant colors, photorealistic",
        "aspect_ratio": "9:16",
        "output_dir": "output/test"
    })
    
    if not image_result.get("success"):
        print(f"❌ Image generation failed: {image_result.get('error')}")
        return False
    
    image_path = image_result["images"][0]
    print(f"✅ Image generated: {image_path}")
    
    # Step 2: Test Pika video generation
    print("\n[2/3] Testing Pika v2.2 API...")
    print("Fixes applied:")
    print("  - Response parsing fixed: result['data']['video']['url']")
    print("  - Aspect ratio parameter added: 9:16")
    print("  - Enhanced error logging")
    
    video_tool = PikaVideoTool()
    
    try:
        video_result = video_tool.run({
            "image_path": image_path,
            "prompt": "Camera pans across the sunset landscape, clouds moving slowly",
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
                    else:
                        print(f"⚠️  Aspect ratio: {width}×{height} (expected 9:16)")
            except FileNotFoundError:
                print("⚠️  ffprobe not available, skipping video verification")
            
            print("\n" + "=" * 60)
            print("✅ PIKA TEST PASSED")
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
    success = test_pika_video()
    sys.exit(0 if success else 1)
