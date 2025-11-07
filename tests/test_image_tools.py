#!/usr/bin/env python3
"""
Test suite for Image Generation Tools
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_PROMPT = "A cup of coffee on a wooden table, morning light, cinematic, 9:16 aspect ratio"
TEST_OUTPUT_DIR = project_root / "tests" / "outputs" / "image_tools"
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_result(name, status, time_taken=None, cost=None, output=None, error=None):
    """Create test result dictionary."""
    return {
        "name": name,
        "status": status,
        "time": time_taken,
        "cost": cost,
        "output": str(output) if output else None,
        "error": str(error) if error else None
    }

def test_flux_dev():
    """Test Flux Dev (Replicate)."""
    print("\n🧪 Testing Flux Dev...")
    
    try:
        from tools.replicate_image import FluxDevTool
        
        tool = FluxDevTool()
        start_time = time.time()
        
        result = tool.execute({
            "prompt": TEST_PROMPT,
            "aspect_ratio": "9:16",
            "num_inference_steps": 28,
            "output_dir": str(TEST_OUTPUT_DIR)
        })
        
        time_taken = time.time() - start_time
        
        if result and "images" in result and result["images"]:
            print(f"   ✅ Flux Dev passed ({time_taken:.1f}s)")
            print(f"   Output: {result['images'][0]}")
            return test_result("flux_dev", "passed", time_taken, 0.03, result["images"][0])
        else:
            print(f"   ❌ Flux Dev failed: No images generated")
            return test_result("flux_dev", "failed", time_taken, error="No images generated")
            
    except Exception as e:
        print(f"   ❌ Flux Dev failed: {e}")
        return test_result("flux_dev", "failed", error=str(e))

def test_flux_schnell():
    """Test Flux Schnell (Replicate) - Fast & cheap."""
    print("\n🧪 Testing Flux Schnell...")
    
    try:
        from tools.replicate_image import FluxSchnellTool
        
        tool = FluxSchnellTool()
        start_time = time.time()
        
        result = tool.execute({
            "prompt": TEST_PROMPT,
            "aspect_ratio": "9:16",
            "num_inference_steps": 4,  # Fast mode
            "output_dir": str(TEST_OUTPUT_DIR)
        })
        
        time_taken = time.time() - start_time
        
        if result and "images" in result and result["images"]:
            print(f"   ✅ Flux Schnell passed ({time_taken:.1f}s)")
            print(f"   Output: {result['images'][0]}")
            return test_result("flux_schnell", "passed", time_taken, 0.02, result["images"][0])
        else:
            print(f"   ❌ Flux Schnell failed: No images generated")
            return test_result("flux_schnell", "failed", time_taken, error="No images generated")
            
    except Exception as e:
        print(f"   ❌ Flux Schnell failed: {e}")
        return test_result("flux_schnell", "failed", error=str(e))

def test_instant_character():
    """Test InstantCharacter (fal.ai) - Requires reference image."""
    print("\n🧪 Testing InstantCharacter...")
    print("   ⏭️  Skipped: Requires reference image")
    return test_result("instant_character", "skipped", error="Requires reference image")

def test_flux_kontext_pro():
    """Test Flux Kontext Pro (fal.ai) - Requires reference image."""
    print("\n🧪 Testing Flux Kontext Pro...")
    print("   ⏭️  Skipped: Requires reference image")
    return test_result("flux_kontext_pro", "skipped", error="Requires reference image")

def test_midjourney():
    """Test Midjourney (APIFRAME)."""
    print("\n🧪 Testing Midjourney...")
    
    try:
        from tools.apiframe_midjourney import ApiframeMidjourneyTool
        
        tool = ApiframeMidjourneyTool()
        start_time = time.time()
        
        result = tool.execute({
            "prompt": TEST_PROMPT,
            "aspect_ratio": "9:16",
            "output_dir": str(TEST_OUTPUT_DIR)
        })
        
        time_taken = time.time() - start_time
        
        if result and "image_path" in result:
            print(f"   ✅ Midjourney passed ({time_taken:.1f}s)")
            print(f"   Output: {result['image_path']}")
            return test_result("midjourney", "passed", time_taken, 0.05, result["image_path"])
        else:
            print(f"   ❌ Midjourney failed: No image generated")
            return test_result("midjourney", "failed", time_taken, error="No image generated")
            
    except Exception as e:
        print(f"   ❌ Midjourney failed: {e}")
        return test_result("midjourney", "failed", error=str(e))

def test_ideogram():
    """Test Ideogram (Ideogram)."""
    print("\n🧪 Testing Ideogram...")
    
    try:
        from tools.ideogram_text import IdeogramTextTool
        
        tool = IdeogramTextTool()
        start_time = time.time()
        
        result = tool.execute({
            "prompt": "COFFEE TIME - bold typography, modern design",
            "output_dir": str(TEST_OUTPUT_DIR)
        })
        
        time_taken = time.time() - start_time
        
        if result and "image_path" in result:
            print(f"   ✅ Ideogram passed ({time_taken:.1f}s)")
            print(f"   Output: {result['image_path']}")
            return test_result("ideogram", "passed", time_taken, 0.02, result["image_path"])
        else:
            print(f"   ❌ Ideogram failed: No image generated")
            return test_result("ideogram", "failed", time_taken, error="No image generated")
            
    except Exception as e:
        print(f"   ❌ Ideogram failed: {e}")
        return test_result("ideogram", "failed", error=str(e))

def run_all():
    """Run all image tool tests."""
    results = {}
    
    # Priority 1: Most used tools
    results["flux_dev"] = test_flux_dev()
    
    # Priority 2: Fast & cheap
    results["flux_schnell"] = test_flux_schnell()
    
    # Priority 3: Premium
    # results["midjourney"] = test_midjourney()  # Expensive, uncomment when ready
    
    # Priority 4: Specialized
    # results["ideogram"] = test_ideogram()  # Uncomment when ready
    
    # Skip tools that require reference images
    results["instant_character"] = test_instant_character()
    results["flux_kontext_pro"] = test_flux_kontext_pro()
    
    return results

if __name__ == "__main__":
    print("="*60)
    print("IMAGE TOOLS TEST SUITE")
    print("="*60)
    
    results = run_all()
    
    # Print summary
    print("\n" + "="*60)
    print("IMAGE TOOLS SUMMARY")
    print("="*60)
    for name, result in results.items():
        status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⏭️"
        print(f"{status_icon} {name}: {result['status']}")
    print("="*60)
