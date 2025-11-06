# Video Tool Test Scripts

These test scripts verify that all 6 critical issues have been fixed in v2.3.0.

---

## Test Scripts

### 1. `test_runway_video.py`
**Tests:** Issue #1 - Runway API 400 error

**What it does:**
- Generates a test image in 9:16 format
- Calls Runway Gen-4 API with fixed parameters
- Verifies video is generated with correct aspect ratio (720×1280)

**Fixes verified:**
- ✅ X-Runway-Version header
- ✅ Correct endpoint (/image_to_video)
- ✅ Aspect ratio mapping (9:16 → 720:1280)
- ✅ Position parameter

### 2. `test_pika_video.py`
**Tests:** Issue #2 - Pika missing video_path error

**What it does:**
- Generates a test image in 9:16 format
- Calls Pika v2.2 API
- Verifies response parsing works correctly

**Fixes verified:**
- ✅ Response parsing: result['data']['video']['url']
- ✅ Aspect ratio parameter: 9:16
- ✅ Enhanced error logging

### 3. `test_minimax_video.py`
**Tests:** Issue #3 - Aspect ratio consistency (Minimax)

**What it does:**
- Generates a test image in 9:16 format
- Verifies image is actually 9:16
- Calls Minimax Hailuo 2.3 API
- Verifies output video is 9:16 (inherited from input)

**Fixes verified:**
- ✅ Input image is 9:16
- ✅ Minimax inherits aspect ratio correctly
- ✅ Output video is 9:16

### 4. `test_luma_video.py`
**Tests:** Luma Ray aspect ratio (verification)

**What it does:**
- Generates a test image in 9:16 format
- Calls Luma Ray API with aspect_ratio parameter
- Verifies output video is 9:16

**Fixes verified:**
- ✅ Luma respects aspect_ratio parameter
- ✅ Output video is 9:16

### 5. `test_wan_video.py`
**Tests:** Issue #3 - Aspect ratio consistency (Wan)

**What it does:**
- Generates a test image in 9:16 format
- Verifies image is actually 9:16
- Calls Wan 2.5 i2v API
- Verifies output video is 9:16 (inherited from input)

**Fixes verified:**
- ✅ Input image is 9:16
- ✅ Wan inherits aspect ratio correctly
- ✅ Output video is 9:16

---

## How to Run

### Prerequisites
1. Extract the main code archive
2. Set up `.env` file with API keys
3. Install dependencies: `pip install -r requirements.txt`

### Run Individual Tests
```bash
# From the social_video_agent directory
cd social_video_agent/

# Test Runway
python ../test_scripts/test_runway_video.py

# Test Pika
python ../test_scripts/test_pika_video.py

# Test Minimax
python ../test_scripts/test_minimax_video.py

# Test Luma
python ../test_scripts/test_luma_video.py

# Test Wan
python ../test_scripts/test_wan_video.py
```

### Run All Tests
```bash
# Run all tests in sequence
for test in ../test_scripts/test_*_video.py; do
    echo "Running $test..."
    python "$test" || echo "FAILED: $test"
    echo ""
done
```

---

## Expected Results

### Success Output
Each test should show:
```
============================================================
Testing [Tool Name] Video Generation
============================================================

[1/3] Generating test image with Flux...
✅ Image generated: output/test/...

[2/3] Testing [Tool Name] API...
✅ Video generated: output/test/...

[3/3] Verifying video...
✅ Video file exists: X.XX MB
✅ Video properties: WIDTHxHEIGHT, X.Xs
✅ Aspect ratio correct: WIDTHxHEIGHT (9:16)

============================================================
✅ [TOOL NAME] TEST PASSED
============================================================
```

### Failure Output
If a test fails, it will show:
```
❌ [Step] failed: [error message]
[Traceback if applicable]
```

---

## Troubleshooting

### API Key Errors
**Error:** "API key not found" or "Authentication failed"

**Solution:**
- Check `.env` file has correct API keys
- Verify API keys are valid and have credits
- Check specific API dashboard for issues

### Image Generation Fails
**Error:** "Image generation failed"

**Solution:**
- Check `REPLICATE_API_TOKEN` in `.env`
- Verify Replicate account has credits
- Try running test again (temporary API issue)

### Video Generation Fails
**Error:** "Video generation failed"

**Solution:**
- Check specific API key in `.env`
- Verify API account has credits
- Check API status page for outages
- Review error message for specific issue

### Wrong Aspect Ratio
**Error:** "Aspect ratio WRONG: 1280x720"

**Solution:**
- This means the fix didn't work correctly
- Check that you're using v2.3.0 code
- Verify image generation shows aspect_ratio=9:16 in logs
- Report issue with full error output

### ffprobe Not Available
**Warning:** "ffprobe not available, skipping video verification"

**Solution:**
- Install ffmpeg: `sudo apt-get install ffmpeg`
- Or ignore warning - video still generated, just not verified

---

## Test Output Location

All test outputs are saved to:
```
output/test/
├── flux_schnell_[timestamp]_[id]_0.png  # Test images
├── [tool]_[timestamp]_[id].mp4          # Test videos
└── ...
```

You can review these files manually to verify quality.

---

## Notes

### Test Duration
- Each test takes 2-5 minutes (image + video generation)
- Minimax and Wan are slower (~3-5 minutes each)
- Runway and Pika are faster (~2-3 minutes each)
- Luma is medium (~3-4 minutes)

### Test Cost
- Each test costs ~$0.20-0.50
- Total for all 5 tests: ~$1.50-2.50
- Uses fast/cheap models where possible

### Test Requirements
- Internet connection
- Valid API keys with credits
- ~500MB disk space for test outputs
- ffmpeg/ffprobe (optional, for verification)

---

## Success Criteria

All tests should pass with:
- ✅ No API errors
- ✅ Videos generated successfully
- ✅ All videos are 9:16 aspect ratio
- ✅ No exceptions or crashes

If all 5 tests pass, v2.3.0 is working correctly!
