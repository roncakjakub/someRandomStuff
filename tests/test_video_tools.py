#!/usr/bin/env python3
"""
Test script for all video generation tools.

Tests each tool individually to verify API integration, response format,
and output quality.

Usage:
    python tests/test_video_tools.py --tool runway
    python tests/test_video_tools.py --tool pika
    python tests/test_video_tools.py --tool minimax
    python tests/test_video_tools.py --tool luma
    python tests/test_video_tools.py --tool wan
    python tests/test_video_tools.py --all
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.runway_video import RunwayVideoTool
from tools.pika_video import PikaVideoTool
from tools.minimax_video import MinimaxVideoTool
from tools.luma_video import LumaVideoTool
from tools.wan_video import WanVideoTool
from tools.replicate_flux_dev import FluxDevTool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_image(output_dir: str) -> str:
    """Generate a test image using Flux Dev."""
    logger.info("Creating test image with Flux Dev...")
    
    flux = FluxDevTool()
    result = flux.run({
        "prompt": "A simple coffee cup on a wooden table, product photography, clean background",
        "output_dir": output_dir,
        "filename": "test_image.png"
    })
    
    if "images" in result and len(result["images"]) > 0:
        image_path = result["images"][0]
        logger.info(f"✅ Test image created: {image_path}")
        return image_path
    elif "image_path" in result:
        logger.info(f"✅ Test image created: {result['image_path']}")
        return result["image_path"]
    else:
        raise ValueError("Failed to create test image")


def test_runway(output_dir: str):
    """Test Runway Gen-4 Turbo."""
    logger.info("\n" + "="*60)
    logger.info("Testing RUNWAY GEN-4 TURBO")
    logger.info("="*60)
    
    try:
        # Create test image
        image_path = create_test_image(output_dir)
        
        # Test Runway
        runway = RunwayVideoTool()
        logger.info("Generating video with Runway...")
        
        result = runway.run({
            "image_path": image_path,
            "prompt": "Camera slowly zooms in on the coffee cup, steam rising",
            "duration": 5,
            "ratio": "9:16",
            "output_dir": output_dir
        })
        
        if "video_path" in result:
            logger.info(f"✅ SUCCESS: Video created at {result['video_path']}")
            logger.info(f"   Duration: {result.get('duration', 'unknown')}s")
            logger.info(f"   Cost: ${result.get('cost', 0):.2f}")
            return True
        else:
            logger.error(f"❌ FAILED: No video_path in result")
            logger.error(f"   Result keys: {list(result.keys())}")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pika(output_dir: str):
    """Test Pika v2.2 (single image and morph)."""
    logger.info("\n" + "="*60)
    logger.info("Testing PIKA V2.2")
    logger.info("="*60)
    
    try:
        # Test 1: Single image animation
        logger.info("\n--- Test 1: Single Image Animation ---")
        image_path = create_test_image(output_dir)
        
        pika = PikaVideoTool()
        result = pika.run({
            "image_path": image_path,
            "prompt": "Camera slowly zooms in, steam rises from coffee",
            "output_dir": output_dir
        })
        
        if "video_path" not in result:
            logger.error(f"❌ FAILED: No video_path in result")
            logger.error(f"   Result keys: {list(result.keys())}")
            return False
        
        logger.info(f"✅ Single image animation SUCCESS: {result['video_path']}")
        
        # Test 2: Morph (two images)
        logger.info("\n--- Test 2: Image Morph ---")
        
        # Create second image
        flux = FluxDevTool()
        result2 = flux.run({
            "prompt": "Empty coffee cup on wooden table, product photography",
            "output_dir": output_dir,
            "filename": "test_image_end.png"
        })
        
        if "images" in result2:
            image_path_end = result2["images"][0]
        else:
            image_path_end = result2["image_path"]
        
        # Test morph
        result_morph = pika.run({
            "image_path": image_path,
            "end_image_path": image_path_end,
            "prompt": "Smooth transition from full to empty coffee cup",
            "output_dir": output_dir
        })
        
        if "video_path" in result_morph:
            logger.info(f"✅ Morph SUCCESS: {result_morph['video_path']}")
            return True
        else:
            logger.error(f"❌ Morph FAILED: No video_path")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_minimax(output_dir: str):
    """Test Minimax Hailuo 2.3."""
    logger.info("\n" + "="*60)
    logger.info("Testing MINIMAX HAILUO 2.3")
    logger.info("="*60)
    
    try:
        image_path = create_test_image(output_dir)
        
        minimax = MinimaxVideoTool()
        logger.info("Generating video with Minimax...")
        
        result = minimax.run({
            "image_path": image_path,
            "prompt": "Person's hand reaches for the coffee cup and picks it up",
            "output_dir": output_dir
        })
        
        if "video_path" in result:
            logger.info(f"✅ SUCCESS: Video created at {result['video_path']}")
            
            # Check aspect ratio
            import subprocess
            cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {result['video_path']}"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            width, height = map(int, output.split(','))
            ratio = f"{width}:{height}"
            
            logger.info(f"   Resolution: {width}×{height} ({ratio})")
            logger.info(f"   Duration: {result.get('duration', 'unknown')}s")
            
            if width == 1024 and height == 1792:
                logger.info("   ✅ Aspect ratio is correct (9:16)")
            else:
                logger.warning(f"   ⚠️  Aspect ratio is {ratio}, expected 9:16 (1024×1792)")
            
            return True
        else:
            logger.error(f"❌ FAILED: No video_path in result")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_luma(output_dir: str):
    """Test Luma Ray."""
    logger.info("\n" + "="*60)
    logger.info("Testing LUMA RAY")
    logger.info("="*60)
    
    try:
        image_path = create_test_image(output_dir)
        
        luma = LumaVideoTool()
        logger.info("Generating video with Luma...")
        
        result = luma.run({
            "image_path": image_path,
            "prompt": "Cinematic shot, camera slowly orbits around the coffee cup, dramatic lighting",
            "output_dir": output_dir
        })
        
        if "video_path" in result:
            logger.info(f"✅ SUCCESS: Video created at {result['video_path']}")
            logger.info(f"   Duration: {result.get('duration', 'unknown')}s")
            logger.info(f"   Cost: ${result.get('cost', 0):.2f}")
            return True
        else:
            logger.error(f"❌ FAILED: No video_path in result")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_wan(output_dir: str):
    """Test Wan 2.5 i2v."""
    logger.info("\n" + "="*60)
    logger.info("Testing WAN 2.5 I2V")
    logger.info("="*60)
    
    try:
        image_path = create_test_image(output_dir)
        
        wan = WanVideoTool()
        logger.info("Generating video with Wan...")
        
        result = wan.run({
            "image_path": image_path,
            "prompt": "Gentle camera movement, steam rises from coffee",
            "output_dir": output_dir
        })
        
        if "video_path" in result:
            logger.info(f"✅ SUCCESS: Video created at {result['video_path']}")
            logger.info(f"   Duration: {result.get('duration', 'unknown')}s")
            return True
        else:
            logger.error(f"❌ FAILED: No video_path in result")
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Test video generation tools")
    parser.add_argument("--tool", choices=["runway", "pika", "minimax", "luma", "wan"], 
                       help="Test specific tool")
    parser.add_argument("--all", action="store_true", help="Test all tools")
    parser.add_argument("--output-dir", default="./test_output", 
                       help="Output directory for test files")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    # Run tests
    results = {}
    
    if args.all:
        tools = ["runway", "pika", "minimax", "luma", "wan"]
    elif args.tool:
        tools = [args.tool]
    else:
        parser.print_help()
        return
    
    for tool in tools:
        if tool == "runway":
            results["runway"] = test_runway(str(output_dir))
        elif tool == "pika":
            results["pika"] = test_pika(str(output_dir))
        elif tool == "minimax":
            results["minimax"] = test_minimax(str(output_dir))
        elif tool == "luma":
            results["luma"] = test_luma(str(output_dir))
        elif tool == "wan":
            results["wan"] = test_wan(str(output_dir))
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for tool, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{tool.upper():15} {status}")
    
    total = len(results)
    passed = sum(results.values())
    logger.info(f"\nTotal: {passed}/{total} passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        logger.info("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("\n⚠️  Some tests failed. Check logs above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
