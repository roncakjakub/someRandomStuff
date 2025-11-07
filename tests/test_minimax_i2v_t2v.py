"""
Test script for MinimaxI2VTool and MinimaxT2VTool

Tests both Image-to-Video and Text-to-Video modes of Minimax Hailuo 2.3.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.minimax_i2v import MinimaxI2VTool
from tools.minimax_t2v import MinimaxT2VTool
from tools.replicate_image import FluxDevTool

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
        "prompt": "A simple white coffee cup on a wooden table, product photography, clean background, minimalist",
        "aspect_ratio": "9:16",  # Vertical!
        "output_dir": "test_output"
    })
    
    image_path = result["images"][0]
    logger.info(f"✅ Test image created: {image_path}")
    
    return image_path


def test_minimax_i2v():
    """Test Minimax Image-to-Video (I2V) mode."""
    logger.info("\n" + "="*60)
    logger.info("Testing MINIMAX IMAGE-TO-VIDEO (I2V)")
    logger.info("="*60)
    
    try:
        # Create test image
        test_image = create_test_image_9_16()
        
        # Test I2V
        logger.info("\nGenerating video from image (I2V mode)...")
        tool = MinimaxI2VTool()
        
        result = tool.execute({
            "first_frame_image": test_image,
            "prompt": "Steam slowly rises from the hot coffee, camera slowly zooms in",
            "duration": 6,
            "resolution": "768p",
            "output_dir": "test_output"
        })
        
        logger.info(f"\n✅ SUCCESS: I2V video created")
        logger.info(f"   Video path: {result['video_path']}")
        logger.info(f"   Mode: {result['mode']}")
        logger.info(f"   Duration: {result['duration']}s")
        logger.info(f"   Cost: ${result['cost_estimate']}")
        
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
        logger.info(f"   Duration: {duration:.1f}s")
        
        # Check if aspect ratio is preserved
        # Input image should be 9:16 (vertical)
        # Expected: height > width
        if height > width:
            logger.info(f"   ✅ Aspect ratio preserved (vertical)")
        else:
            logger.warning(f"   ⚠️  Aspect ratio NOT preserved (should be vertical)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_minimax_t2v():
    """Test Minimax Text-to-Video (T2V) mode."""
    logger.info("\n" + "="*60)
    logger.info("Testing MINIMAX TEXT-TO-VIDEO (T2V)")
    logger.info("="*60)
    
    try:
        logger.info("\nGenerating video from text (T2V mode)...")
        tool = MinimaxT2VTool()
        
        result = tool.execute({
            "prompt": "A white coffee cup on a wooden table, steam slowly rising from hot coffee, cinematic lighting, product shot",
            "duration": 6,
            "resolution": "768p",
            "output_dir": "test_output"
        })
        
        logger.info(f"\n✅ SUCCESS: T2V video created")
        logger.info(f"   Video path: {result['video_path']}")
        logger.info(f"   Mode: {result['mode']}")
        logger.info(f"   Duration: {result['duration']}s")
        logger.info(f"   Aspect ratio: {result['aspect_ratio']}")
        logger.info(f"   Cost: ${result['cost_estimate']}")
        
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
        logger.info(f"   Actual aspect ratio: {width}:{height}")
        logger.info(f"   Duration: {duration:.1f}s")
        
        # T2V should default to 16:9 (horizontal)
        # Expected: width > height
        if width > height:
            logger.info(f"   ✅ Aspect ratio correct (16:9 horizontal)")
        else:
            logger.warning(f"   ⚠️  Unexpected aspect ratio")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("Starting Minimax I2V/T2V tests...")
    
    # Create output directory
    Path("test_output").mkdir(exist_ok=True)
    
    results = {}
    
    # Test I2V
    results["i2v"] = test_minimax_i2v()
    
    # Test T2V
    results["t2v"] = test_minimax_t2v()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    logger.info(f"Minimax I2V:  {'✅ PASSED' if results['i2v'] else '❌ FAILED'}")
    logger.info(f"Minimax T2V:  {'✅ PASSED' if results['t2v'] else '❌ FAILED'}")
    
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} passed ({passed/total*100:.0f}%)")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
