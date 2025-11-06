# Video Tool Tests

Test scripts for verifying video generation tool integrations.

---

## Quick Start

```bash
# Test all tools
python tests/test_video_tools.py --all

# Test specific tool
python tests/test_video_tools.py --tool runway
python tests/test_video_tools.py --tool pika
python tests/test_video_tools.py --tool minimax
python tests/test_video_tools.py --tool luma
python tests/test_video_tools.py --tool wan
```

---

## What It Tests

### For Each Tool:

1. **API Connection**
   - Verifies API key is valid
   - Tests endpoint connectivity

2. **Image Upload** (if required)
   - Uploads test image
   - Verifies upload success

3. **Video Generation**
   - Generates 5-second video
   - Verifies video file created

4. **Response Format**
   - Checks for `video_path` in result
   - Validates response structure

5. **Aspect Ratio** (Minimax only)
   - Checks if output is 9:16 (1024×1792)
   - Warns if different

---

## Expected Output

```
============================================================
Testing RUNWAY GEN-4 TURBO
============================================================
Creating test image with Flux Dev...
✅ Test image created: ./test_output/test_image.png
Generating video with Runway...
✅ SUCCESS: Video created at ./test_output/runway_20251106_123456.mp4
   Duration: 5s
   Cost: $0.25

============================================================
TEST SUMMARY
============================================================
RUNWAY          ✅ PASSED
PIKA            ✅ PASSED
MINIMAX         ✅ PASSED
LUMA            ✅ PASSED
WAN             ✅ PASSED

Total: 5/5 passed (100%)

🎉 All tests passed!
```

---

## Troubleshooting

### Runway 400 Error

**Error:** `400 Client Error: Bad Request for url: https://api.dev.runwayml.com/v1/uploads`

**Possible Causes:**
1. Invalid RUNWAY_API_KEY
2. Image format not supported
3. Image too large
4. API endpoint changed

**Solutions:**
1. Verify API key in .env
2. Check Runway dashboard for API status
3. Try with smaller image
4. Check Runway API docs for changes

---

### Pika Missing video_path

**Error:** `No video_path in result`

**Possible Causes:**
1. Invalid FAL_KEY
2. Pika API response format changed
3. Video generation failed silently

**Solutions:**
1. Verify FAL_KEY in .env
2. Check fal.ai dashboard
3. Look at full result dict in logs

---

### Minimax Wrong Aspect Ratio

**Warning:** `Aspect ratio is 16:9, expected 9:16`

**Cause:** Minimax doesn't support 9:16 aspect ratio

**Solutions:**
1. Force 16:9 for all tools (landscape)
2. OR crop/resize Minimax output to 9:16
3. OR don't use Minimax for portrait videos

---

## API Keys Required

Make sure these are set in `.env`:

```bash
# Replicate (for Flux, Minimax, Luma, Wan)
REPLICATE_API_TOKEN=r8_...

# Runway
RUNWAY_API_KEY=sk-...

# Pika (via fal.ai)
FAL_KEY=...
```

---

## Output Files

Tests create files in `./test_output/`:

- `test_image.png` - Test image from Flux Dev
- `test_image_end.png` - Second image for Pika morph test
- `runway_*.mp4` - Runway video output
- `pika_*.mp4` - Pika video outputs (2 files)
- `minimax_*.mp4` - Minimax video output
- `luma_*.mp4` - Luma video output
- `wan_*.mp4` - Wan video output

---

## Next Steps

After tests pass:

1. **If all pass:** System is ready! ✅
2. **If Runway fails:** Debug Runway API integration
3. **If Pika fails:** Debug Pika/fal.ai integration
4. **If Minimax wrong ratio:** Fix aspect ratio in tool
5. **If multiple fail:** Check internet/API status

---

## Advanced Usage

### Custom Output Directory

```bash
python tests/test_video_tools.py --all --output-dir /path/to/output
```

### Debug Mode

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG
python tests/test_video_tools.py --tool runway
```

### Test Specific Scenario

Edit `test_video_tools.py` and modify test functions to test specific prompts, durations, or settings.

---

## Integration with CI/CD

```bash
# In CI pipeline
python tests/test_video_tools.py --all
if [ $? -eq 0 ]; then
    echo "All video tools working!"
else
    echo "Some tools failed, check logs"
    exit 1
fi
```

---

**Happy Testing!** 🧪
