#!/usr/bin/env python3
"""
Test individual tools to verify they work correctly.

Usage:
    python test_tools.py              # Run all tests
    python test_tools.py midjourney   # Run specific test
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.apiframe_midjourney import ApiframeMidjourneyTool
from tools.instant_character import InstantCharacterTool
from tools.flux_kontext_pro import FluxKontextProTool
from tools.replicate_flux_dev import ReplicateFluxDevTool
from tools.veo31_flf2v import Veo31FLF2VTool
from tools.luma_video import LumaVideoTool
from tools.minimax_video import MinimaxVideoTool
from tools.elevenlabs_voice import ElevenLabsVoiceTool

# Test output directory
TEST_OUTPUT = "test_output"
os.makedirs(TEST_OUTPUT, exist_ok=True)

def test_midjourney():
    """Test Midjourney tool"""
    print("\n=== Testing Midjourney ===")
    tool = ApiframeMidjourneyTool()
    result = tool.execute({
        "prompt": "A cup of coffee on a table, cinematic lighting, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    print(f"✅ Result: {result}")
    assert "image_path" in result or "images" in result
    print("✅ Midjourney test passed!")
    return result

def test_instant_character():
    """Test InstantCharacter tool"""
    print("\n=== Testing InstantCharacter ===")
    
    # First generate a reference image
    print("Step 1: Generate reference image...")
    flux_tool = ReplicateFluxDevTool()
    ref_result = flux_tool.execute({
        "prompt": "Portrait of a woman in her 30s, professional photo, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    reference_image = ref_result["images"][0]
    print(f"Reference: {reference_image}")
    
    # Now test InstantCharacter
    print("Step 2: Generate with InstantCharacter...")
    tool = InstantCharacterTool()
    result = tool.execute(
        prompt="Same woman drinking coffee, warm lighting",
        reference_image_url=reference_image,
        image_size="landscape_16_9"
    )
    print(f"✅ Result: {result}")
    assert "image_url" in result
    print("✅ InstantCharacter test passed!")
    return result

def test_flux_kontext_pro():
    """Test FluxKontextPro tool"""
    print("\n=== Testing FluxKontextPro ===")
    
    # First generate a reference image
    print("Step 1: Generate reference image...")
    flux_tool = ReplicateFluxDevTool()
    ref_result = flux_tool.execute({
        "prompt": "Modern kitchen interior, warm lighting, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    reference_image = ref_result["images"][0]
    print(f"Reference: {reference_image}")
    
    # Now test FluxKontextPro
    print("Step 2: Generate with FluxKontextPro...")
    tool = FluxKontextProTool()
    result = tool.execute(
        prompt="Add a coffee machine on the counter, keep the kitchen style",
        reference_image_url=reference_image,
        guidance_scale=3.5,
        num_inference_steps=28
    )
    print(f"✅ Result: {result}")
    assert "image_url" in result
    print("✅ FluxKontextPro test passed!")
    return result

def test_flux_dev():
    """Test Flux Dev tool"""
    print("\n=== Testing Flux Dev ===")
    tool = ReplicateFluxDevTool()
    result = tool.execute({
        "prompt": "Coffee beans on a wooden table, close-up, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    print(f"✅ Result: {result}")
    assert "images" in result
    print("✅ Flux Dev test passed!")
    return result

def test_veo31():
    """Test Veo 3.1 tool"""
    print("\n=== Testing Veo 3.1 ===")
    
    # Generate two frame images first
    print("Step 1: Generate frame images...")
    flux_tool = ReplicateFluxDevTool()
    
    frame1_result = flux_tool.execute({
        "prompt": "Coffee beans in hand, natural light, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    frame1 = frame1_result["images"][0]
    
    frame2_result = flux_tool.execute({
        "prompt": "Coffee cup with steam, warm light, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    frame2 = frame2_result["images"][0]
    
    print(f"Frame 1: {frame1}")
    print(f"Frame 2: {frame2}")
    
    # Now test Veo 3.1
    print("Step 2: Generate morph video...")
    tool = Veo31FLF2VTool()
    result = tool.execute(
        first_frame_url=frame1,
        last_frame_url=frame2,
        prompt="Coffee beans transform into a cup of coffee",
        aspect_ratio="9:16"
    )
    print(f"✅ Result: {result}")
    assert "video_url" in result
    print("✅ Veo 3.1 test passed!")
    return result

def test_luma():
    """Test Luma tool"""
    print("\n=== Testing Luma ===")
    
    # Generate start image first
    print("Step 1: Generate start image...")
    flux_tool = ReplicateFluxDevTool()
    start_result = flux_tool.execute({
        "prompt": "Coffee cup on table, cinematic, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    start_image = start_result["images"][0]
    
    # Now test Luma
    print("Step 2: Generate video...")
    tool = LumaVideoTool()
    result = tool.execute(
        start_image=start_image,
        prompt="Camera slowly zooms into the coffee cup",
        aspect_ratio="9:16"
    )
    print(f"✅ Result: {result}")
    assert "video_url" in result or "video_path" in result
    print("✅ Luma test passed!")
    return result

def test_minimax():
    """Test Minimax tool"""
    print("\n=== Testing Minimax ===")
    
    # Generate start image first
    print("Step 1: Generate start image...")
    flux_tool = ReplicateFluxDevTool()
    start_result = flux_tool.execute({
        "prompt": "Coffee beans close-up, 9:16",
        "aspect_ratio": "9:16",
        "output_dir": TEST_OUTPUT
    })
    start_image = start_result["images"][0]
    
    # Now test Minimax
    print("Step 2: Generate video...")
    tool = MinimaxVideoTool()
    result = tool.execute(
        start_image=start_image,
        prompt="Coffee beans slowly rotating"
    )
    print(f"✅ Result: {result}")
    assert "video_url" in result or "video_path" in result
    print("✅ Minimax test passed!")
    return result

def test_elevenlabs():
    """Test ElevenLabs tool"""
    print("\n=== Testing ElevenLabs ===")
    tool = ElevenLabsVoiceTool()
    result = tool.execute(
        text="This is a test of the ElevenLabs voice generation.",
        language="en",
        output_dir=TEST_OUTPUT
    )
    print(f"✅ Result: {result}")
    assert "audio_path" in result
    print("✅ ElevenLabs test passed!")
    return result

# Test registry
TESTS = {
    "midjourney": test_midjourney,
    "instant_character": test_instant_character,
    "flux_kontext_pro": test_flux_kontext_pro,
    "flux_dev": test_flux_dev,
    "veo31": test_veo31,
    "luma": test_luma,
    "minimax": test_minimax,
    "elevenlabs": test_elevenlabs,
}

if __name__ == "__main__":
    print("🧪 Starting Tool Tests...")
    print("=" * 60)
    
    # Check if specific test requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name in TESTS:
            print(f"Running single test: {test_name}")
            try:
                TESTS[test_name]()
                print(f"\n✅ {test_name.upper()} TEST PASSED!")
            except Exception as e:
                print(f"\n❌ {test_name.upper()} TEST FAILED: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        else:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {', '.join(TESTS.keys())}")
            sys.exit(1)
    else:
        # Run all tests
        print("Running all tests...")
        failed = []
        
        for test_name, test_func in TESTS.items():
            try:
                test_func()
            except Exception as e:
                print(f"\n❌ {test_name.upper()} TEST FAILED: {e}")
                import traceback
                traceback.print_exc()
                failed.append(test_name)
        
        print("\n" + "=" * 60)
        if not failed:
            print("✅ ALL TOOL TESTS PASSED!")
        else:
            print(f"❌ {len(failed)} TEST(S) FAILED:")
            for name in failed:
                print(f"  - {name}")
        print("=" * 60)
        
        sys.exit(0 if not failed else 1)
