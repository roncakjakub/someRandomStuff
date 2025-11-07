"""
Test Luma I2V for Steam Quality

This test specifically focuses on testing steam/smoke motion quality,
comparing Luma vs Minimax for realistic fluid dynamics.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.luma_i2v import LumaI2VTool
from tools.minimax_i2v import MinimaxI2VTool
from tools.replicate_flux_dev import FluxDevTool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_image_9_16():
    """Create a 9:16 test image using Flux Dev."""
    logger.info("Creating 9:16 test image with Flux Dev...")
    
    tool = FluxDevTool()
    result = tool.execute({
        "prompt": "A simple white coffee cup on a wooden table, product photography, clean background, minimalist, soft lighting",
        "aspect_ratio": "9:16",  # Vertical!
        "output_dir": "test_output"
    })
    
    image_path = result["images"][0]
    logger.info(f"✅ Test image created: {image_path}")
    
    return image_path


def test_luma_i2v_steam():
    """Test Luma I2V with focus on steam quality."""
    logger.info("\n" + "="*60)
    logger.info("Testing LUMA I2V - STEAM QUALITY")
    logger.info("="*60)
    
    try:
        # Create test image
        test_image = create_test_image_9_16()
        
        # Test Luma I2V with optimized steam prompt
        logger.info("\nGenerating video with Luma (I2V mode)...")
        logger.info("Focus: Realistic steam motion")
        
        tool = LumaI2VTool()
        
        # Optimized prompt for realistic steam
        steam_prompt = (
            "Gentle steam naturally rises from hot coffee, "
            "soft and wispy, realistic fluid dynamics, "
            "cinematic lighting, slow motion"
        )
        
        result = tool.execute({
            "start_image": test_image,
            "prompt": steam_prompt,
            "aspect_ratio": "9:16",  # Explicitly set to preserve vertical
            "loop": False,
            "output_dir": "test_output"
        })
        
        logger.info(f"\n✅ SUCCESS: Luma I2V video created")
        logger.info(f"   Video path: {result['video_path']}")
        logger.info(f"   Mode: {result['mode']}")
        logger.info(f"   Duration: {result['duration']}s")
        logger.info(f"   Cost: ${result['cost_estimate']}")
        logger.info(f"   Prompt used: {steam_prompt}")
        
        # Check video properties
        import cv2
        video = cv2.VideoCapture(result['video_path'])
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        video.release()
        
        logger.info(f"   Resolution: {width}×{height}")
        logger.info(f"   Aspect ratio: {width}:{height}")
        logger.info(f"   FPS: {fps:.1f}")
        logger.info(f"   Duration: {duration:.1f}s")
        
        # Check if aspect ratio is preserved
        if height > width:
            logger.info(f"   ✅ Aspect ratio preserved (vertical)")
        else:
            logger.warning(f"   ⚠️  Aspect ratio NOT preserved (should be vertical)")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_minimax_i2v_steam():
    """Test Minimax I2V with same steam prompt for comparison."""
    logger.info("\n" + "="*60)
    logger.info("Testing MINIMAX I2V - STEAM QUALITY (for comparison)")
    logger.info("="*60)
    
    try:
        # Use same test image
        test_image = "test_output/flux_dev_*.png"  # Will use existing image
        import glob
        test_images = glob.glob(test_image)
        if not test_images:
            logger.error("No test image found, run Luma test first")
            return None
        test_image = test_images[0]
        
        logger.info(f"Using existing test image: {test_image}")
        
        # Test Minimax I2V with same steam prompt
        logger.info("\nGenerating video with Minimax (I2V mode)...")
        logger.info("Focus: Realistic steam motion (same prompt as Luma)")
        
        tool = MinimaxI2VTool()
        
        # Same prompt as Luma for fair comparison
        steam_prompt = (
            "Gentle steam naturally rises from hot coffee, "
            "soft and wispy, realistic fluid dynamics, "
            "cinematic lighting, slow motion"
        )
        
        result = tool.execute({
            "first_frame_image": test_image,
            "prompt": steam_prompt,
            "duration": 6,
            "resolution": "768p",
            "output_dir": "test_output"
        })
        
        logger.info(f"\n✅ SUCCESS: Minimax I2V video created")
        logger.info(f"   Video path: {result['video_path']}")
        logger.info(f"   Mode: {result['mode']}")
        logger.info(f"   Duration: {result['duration']}s")
        logger.info(f"   Cost: ${result['cost_estimate']}")
        logger.info(f"   Prompt used: {steam_prompt}")
        
        # Check video properties
        import cv2
        video = cv2.VideoCapture(result['video_path'])
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        video.release()
        
        logger.info(f"   Resolution: {width}×{height}")
        logger.info(f"   Aspect ratio: {width}:{height}")
        logger.info(f"   FPS: {fps:.1f}")
        logger.info(f"   Duration: {duration:.1f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def compare_results(luma_result, minimax_result):
    """Compare Luma vs Minimax results."""
    logger.info("\n" + "="*60)
    logger.info("COMPARISON: LUMA vs MINIMAX")
    logger.info("="*60)
    
    if not luma_result or not minimax_result:
        logger.error("Cannot compare - one or both tests failed")
        return
    
    logger.info("\n📊 Side-by-side comparison:")
    logger.info(f"\n{'Metric':<20} {'Luma':<30} {'Minimax':<30}")
    logger.info("-" * 80)
    logger.info(f"{'Cost':<20} ${luma_result['cost_estimate']:<29.2f} ${minimax_result['cost_estimate']:<29.2f}")
    logger.info(f"{'Duration':<20} {luma_result['duration']}s{'':<28} {minimax_result['duration']}s")
    logger.info(f"{'Video path':<20} {Path(luma_result['video_path']).name:<30} {Path(minimax_result['video_path']).name}")
    
    logger.info("\n💡 Quality assessment:")
    logger.info("   Please manually review both videos and compare:")
    logger.info("   1. Steam motion smoothness")
    logger.info("   2. Realistic fluid dynamics")
    logger.info("   3. Overall visual quality")
    logger.info("   4. Artifacts or glitches")
    
    logger.info(f"\n📁 Videos saved to:")
    logger.info(f"   Luma:    {luma_result['video_path']}")
    logger.info(f"   Minimax: {minimax_result['video_path']}")


def main():
    """Run all tests."""
    logger.info("Starting Luma vs Minimax steam quality comparison...")
    
    # Create output directory
    Path("test_output").mkdir(exist_ok=True)
    
    # Test Luma
    luma_result = test_luma_i2v_steam()
    
    # Test Minimax
    minimax_result = test_minimax_i2v_steam()
    
    # Compare
    compare_results(luma_result, minimax_result)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Luma I2V:    {'✅ PASSED' if luma_result else '❌ FAILED'}")
    logger.info(f"Minimax I2V: {'✅ PASSED' if minimax_result else '❌ FAILED'}")
    
    if luma_result and minimax_result:
        logger.info("\n✅ Both tests passed - Ready for quality comparison!")
        logger.info(f"\nTotal cost: ${luma_result['cost_estimate'] + minimax_result['cost_estimate']:.2f}")
        return True
    else:
        logger.error("\n❌ One or both tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
