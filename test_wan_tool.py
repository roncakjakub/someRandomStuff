"""
Simple test for Wan FLF2V tool
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.wan_flf2v import WanFLF2VTool

def test_wan_flf2v():
    """Test Wan FLF2V tool with two test images."""
    print("=" * 60)
    print("Testing Wan FLF2V Tool")
    print("=" * 60)
    
    # Check if FAL_KEY is set
    if not os.getenv("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable not set")
        return False
    
    print(f"✓ FAL_KEY found: {os.getenv('FAL_KEY')[:10]}...")
    
    # Initialize tool
    print("\n1. Initializing Wan FLF2V tool...")
    tool = WanFLF2VTool()
    print(f"✓ Tool initialized: {tool.model}")
    
    # Create test images directory
    test_dir = Path("test_output/wan_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create two simple test images
    print("\n2. Creating test images...")
    from PIL import Image, ImageDraw, ImageFont
    
    # Start image: Blue background with text
    start_img = Image.new('RGB', (720, 1280), color='blue')
    draw = ImageDraw.Draw(start_img)
    draw.text((360, 640), "START", fill='white', anchor='mm')
    start_path = test_dir / "start.png"
    start_img.save(start_path)
    print(f"✓ Start image: {start_path}")
    
    # End image: Red background with text
    end_img = Image.new('RGB', (720, 1280), color='red')
    draw = ImageDraw.Draw(end_img)
    draw.text((360, 640), "END", fill='white', anchor='mm')
    end_path = test_dir / "end.png"
    end_img.save(end_path)
    print(f"✓ End image: {end_path}")
    
    # Test the tool
    print("\n3. Generating morph video...")
    print("   (This will take ~60 seconds)")
    
    try:
        result = tool.execute(
            start_image_path=str(start_path),
            end_image_path=str(end_path),
            prompt="Smooth transition from blue to red",
            resolution="480p",  # Use 480p for faster/cheaper test
            output_path=str(test_dir / "morph_test.mp4")
        )
        
        print(f"\n✓ SUCCESS!")
        print(f"  Video URL: {result['video_url']}")
        print(f"  Video path: {result['video_path']}")
        print(f"  Duration: {result['duration']:.2f}s")
        print(f"  Resolution: {result['resolution']}")
        print(f"  Frames: {result['num_frames']}")
        print(f"  FPS: {result['fps']}")
        
        # Check if file exists and get size
        if result['video_path'] and os.path.exists(result['video_path']):
            size_mb = os.path.getsize(result['video_path']) / (1024 * 1024)
            print(f"  File size: {size_mb:.2f} MB")
            
            if size_mb < 0.01:
                print(f"\n⚠ WARNING: Video file is very small ({size_mb:.2f} MB)")
                print("  This might indicate a problem with video generation")
                return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wan_flf2v()
    sys.exit(0 if success else 1)
