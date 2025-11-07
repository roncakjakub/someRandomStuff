# Changelog v2.6.5 - Midjourney Aspect Ratio + Voiceover Style Fix

**Date:** 2025-11-07  
**Status:** Production Ready ✅

---

## 🎯 Fixes

### Fix #1: Midjourney Landscape Format ⚠️ CRITICAL

**Problem:**  
Midjourney generated landscape images (1024×683) instead of vertical 9:16 format

**Root Cause:**  
Apiframe API ignored `aspect_ratio` parameter in JSON payload

**Solution:**  
Added `--ar 9:16` to prompt (Midjourney native syntax)

**Implementation:**
- File: `tools/apiframe_midjourney.py`
- Line 104-107: Check if `--ar` exists in prompt, if not, append `--ar {aspect_ratio}`

**Before:**
```python
payload = {
    "prompt": prompt,
    "aspect_ratio": "9:16"  # Ignored by API!
}
```

**After:**
```python
if "--ar" not in prompt:
    prompt = f"{prompt} --ar {aspect_ratio}"

payload = {
    "prompt": prompt,  # Now includes "--ar 9:16"
    "aspect_ratio": "9:16"
}
```

---

### Fix #2: Slow Documentary Voiceover ⚠️ CRITICAL

**Problem:**  
Voiceover generated in slow, poetic, documentary style:
```
"Osamelé zelené kávové zrno, dozrievajúce na konári. 
Zníkajú len dva ročné obdobia..."
```

**Expected:**  
Fast, punchy, viral style:
```
"Zelené zrno. Dva ročné obdobia. Zber. Praženie. 
Zmena farby. Vôňa. Chuť. Zdieľanie. Toto je káva."
```

**Root Cause:**  
AI interpreted "life of coffee" as documentary/story topic

**Solution:**  
Added explicit anti-documentary rules and Slovak example

**Implementation:**
- File: `agents/creative_strategist.py`
- Line 120-124: Added Slovak viral example
- Line 169-173: Added explicit DON'T rules for poetic/documentary style

**Added Rules:**
```
❌ DON'T:
- Poetic/literary language ("Osamelé zelené kávové zrno..." ❌)
- Documentary narration (slow, descriptive, contemplative)
- Storytelling tone (once upon a time, journey, etc.)

VIRAL STYLE = FAST, DIRECT, PUNCHY. NOT poetic or documentary!
```

**Added Example:**
```
Slovak Example (for coffee topic):
"Zelené zrno. Dva ročné obdobia. Zber. Praženie. 
Zmena farby. Vôňa. Chuť. Zdieľanie. Toto je káva."

NOT like this (too poetic/documentary):
"❌ Osamelé zelené kávové zrno, dozrievajúce na konári..."
```

---

## 📊 What's Fixed

### From Previous Versions:
- ✅ v2.6.2: ElevenLabs stability, scene count
- ✅ v2.6.3: Router Seedream4 rule removed
- ✅ v2.6.4: FFMPEG path bug, language support
- ✅ v2.6.5: Midjourney aspect ratio, voiceover style

### Current Status:
- ✅ Midjourney 9:16 vertical (native --ar syntax)
- ✅ Voiceover fast & punchy (anti-documentary rules)
- ✅ No Seedream4 in CINEMATIC
- ✅ Exactly 8 scenes
- ✅ Language control (Slovak/English/Czech)
- ✅ Video assembly works

---

## 🎬 Expected Output

### Before (v2.6.4):
```
Midjourney: 1024×683 (landscape) ❌
Voiceover: "Osamelé zelené kávové zrno, dozrievajúce na konári..." (slow) ❌
```

### After (v2.6.5):
```
Midjourney: 1080×1920 (9:16 vertical) ✅
Voiceover: "Zelené zrno. Dva ročné obdobia. Zber. Praženie..." (punchy) ✅
```

---

## 🔍 Technical Details

### Midjourney --ar Parameter

**Why add to prompt instead of payload?**

Apiframe API documentation says it accepts `aspect_ratio` in JSON, but in practice it's ignored. Midjourney's native syntax `--ar 9:16` in the prompt itself is more reliable.

**Supported aspect ratios:**
- `9:16` - Vertical (social media)
- `16:9` - Horizontal (YouTube)
- `1:1` - Square (Instagram)
- `4:5` - Portrait (Instagram feed)

---

### Voiceover Style Enforcement

**Why was AI generating documentary style?**

Topics like "life of coffee", "journey of...", "story of..." trigger AI's storytelling mode → poetic, descriptive, slow narration.

**Solution:**
1. Explicit negative examples (show what NOT to do)
2. Language-specific examples (Slovak viral style)
3. Emphasized "VIRAL STYLE = FAST, DIRECT, PUNCHY"

---

## 📝 Known Issues (Non-Critical)

### Transition Scenes Generate 2 Images
**Status:** By design (for future Pika morph feature)

**Current behavior:**
- Transition scenes (3, 5, 7) generate 2 images (start + end)
- Only 1 image used for video (Luma/Minimax don't support morph)
- Result: Extra unused images

**Future fix:** Implement Pika morph for smooth transitions

**Workaround:** Acceptable - 10 images tell better story than 8

---

## 🚀 Usage

### Test Midjourney 9:16:
```bash
python main.py --topic "coffee" --style cinematic --language sk --verbose
```

### Verify:
```bash
# Check Midjourney image dimensions
file output/*/midjourney_*.png

# Should show: 1080 x 1920 (9:16)
```

### Test Voiceover Style:
```bash
# Check voiceover script
cat output/*/results_*.json | jq '.voiceover_script'

# Should be short, punchy sentences (not poetic)
```

---

## 📦 Files Changed

### Modified Files:
1. `tools/apiframe_midjourney.py` - Added --ar to prompt
2. `agents/creative_strategist.py` - Anti-documentary rules + Slovak example

### Previous Fixes:
1. `tools/elevenlabs_voice.py` - Stability fix (v2.6.2)
2. `tools/video_assembly.py` - FFMPEG path fix (v2.6.4)
3. `workflow_router_v2.py` - Seedream4 rule removed (v2.6.3)

---

## 🎯 Version Comparison

| Version | Midjourney | Voiceover Style | Status |
|---------|------------|-----------------|--------|
| v2.6.4 | Landscape ❌ | Documentary ❌ | ⚠️ |
| v2.6.5 | 9:16 Vertical ✅ | Viral Punchy ✅ | ✅ |

---

**Version:** 2.6.5  
**Previous Version:** 2.6.4  
**Release Date:** 2025-11-07  
**Status:** ✅ Production Ready - Midjourney 9:16 + Viral Voiceover Style
