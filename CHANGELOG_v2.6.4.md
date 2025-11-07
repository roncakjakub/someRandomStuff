# Changelog v2.6.4 - Language Support + FFMPEG Fix

**Date:** 2025-11-07  
**Status:** Production Ready ✅

---

## 🎯 New Features & Fixes

### Feature #1: Voiceover Language Control ✨ NEW

**Problem:**  
English topic → English voiceover (even for Slovak clients)

**Solution:**  
Added `--language` parameter (already existed but wasn't used!)

**Implementation:**
- File: `agents/creative_strategist.py`
- Added `language` parameter to `create_strategy()` method
- Added language instruction in voiceover generation context
- Visual prompts stay in English (better AI generation)
- Voiceover text generated in specified language

**Usage:**
```bash
# Slovak voiceover (default)
python main.py --topic "coffee" --style cinematic

# English voiceover
python main.py --topic "coffee" --style cinematic --language en

# Czech voiceover
python main.py --topic "coffee" --style cinematic --language cs
```

**Supported Languages:**
- `sk` - Slovak (default)
- `cs` - Czech
- `en` - English
- `de` - German
- `pl` - Polish
- `hu` - Hungarian

---

### Fix #1: FFMPEG Path Duplication Bug ⚠️ CRITICAL

**Problem:**
```
[concat @ 0x126f05f60] Impossible to open 
'output/20251107_104939_coffee/output/20251107_104939_coffee/luma_20251107_105241_237539f0.mp4'
```

Path was duplicated → FFMPEG couldn't find video files → Assembly failed

**Root Cause:**  
`video_assembly.py` wrote relative paths to filelist, FFMPEG interpreted them relative to output_dir → double path

**Fix:**
- File: `tools/video_assembly.py`
- Line 116-117: Convert image paths to absolute paths using `Path.resolve()`
- Line 120-121: Same for last image

**Before:**
```python
f.write(f"file '{image}'\n")  # Relative path
```

**After:**
```python
abs_image_path = Path(image).resolve()  # Absolute path
f.write(f"file '{abs_image_path}'\n")
```

---

## 📊 What's Fixed

### From Previous Versions:
- ✅ v2.6.2: ElevenLabs stability fix, scene count limit
- ✅ v2.6.3: Router hardcoded Seedream4 rule removed
- ✅ v2.6.4: FFMPEG path bug + Language support

### Current Status:
- ✅ Voiceover works (ElevenLabs stability fixed)
- ✅ No Seedream4 in CINEMATIC (Router fixed)
- ✅ Exactly 8 scenes (Creative Strategist fixed)
- ✅ Video assembly works (FFMPEG path fixed)
- ✅ Language control (Slovak/English/Czech voiceover)

---

## 🎬 Usage Examples

### Example 1: Slovak Voiceover (Default)
```bash
python main.py --topic "coffee" --style cinematic
```

**Output:**
- Visual prompts: English (for AI tools)
- Voiceover: Slovak

---

### Example 2: English Voiceover
```bash
python main.py --topic "coffee" --style cinematic --language en
```

**Output:**
- Visual prompts: English
- Voiceover: English

---

### Example 3: Czech Voiceover
```bash
python main.py --topic "káva" --style cinematic --language cs
```

**Output:**
- Visual prompts: English (even if topic is Czech)
- Voiceover: Czech

---

## 🔍 Technical Details

### Language Implementation

**Creative Strategist Context:**
```python
**LANGUAGE:** Generate voiceover text in {language_name} language.
- Visual prompts: Keep in English (for better AI image/video generation)
- Voiceover segments: Write in {language_name} (language code: {language})
```

**Why English Prompts?**
- AI image/video tools (Midjourney, Flux, Luma) trained primarily on English
- English prompts = better quality, more accurate results
- Slovak prompts = worse quality, misinterpretations

**Why Separate Voiceover Language?**
- Voiceover is for end users (Slovak clients need Slovak audio)
- ElevenLabs supports multiple languages natively
- Best of both worlds: English prompts + Slovak voiceover

---

### FFMPEG Path Fix

**Problem Scenario:**
```python
# Input
images = ["output/20251107_104939_coffee/luma_xxx.mp4"]
output_dir = "output/20251107_104939_coffee/"

# Filelist (OLD - relative path)
file 'output/20251107_104939_coffee/luma_xxx.mp4'

# FFMPEG interprets as:
output_dir + image_path = 
"output/20251107_104939_coffee/" + "output/20251107_104939_coffee/luma_xxx.mp4"
= "output/20251107_104939_coffee/output/20251107_104939_coffee/luma_xxx.mp4" ❌
```

**Solution:**
```python
# Filelist (NEW - absolute path)
file '/Users/jakubroncak/Downloads/social_video_agent/output/20251107_104939_coffee/luma_xxx.mp4'

# FFMPEG uses absolute path directly ✅
```

---

## 📦 Files Changed

### Modified Files:
1. `agents/creative_strategist.py` - Language parameter + helper method
2. `tools/video_assembly.py` - FFMPEG absolute path fix
3. `workflow.py` - Pass language to Creative Strategist

### Previous Fixes:
1. `tools/elevenlabs_voice.py` - Stability fix (v2.6.2)
2. `agents/creative_strategist.py` - Scene count + content-type (v2.6.2, v2.6.3)
3. `workflow_router_v2.py` - Seedream4 hardcoded rule removed (v2.6.3)

---

## 🚀 Quick Start

### Test Slovak Voiceover:
```bash
python main.py --topic "coffee" --style cinematic --verbose
```

### Test English Voiceover:
```bash
python main.py --topic "coffee" --style cinematic --language en --verbose
```

### Verify Output:
```bash
# Check voiceover language
ls output/*/voiceover_*.mp3

# Check final video
ls output/*/final_video*.mp4
```

---

## 🎯 Version Comparison

| Version | Seedream4 | FFMPEG | Language | Status |
|---------|-----------|--------|----------|--------|
| v2.6.1 | 5 images | OK | English only | ❌ |
| v2.6.2 | 2 images | OK | English only | ⚠️ |
| v2.6.3 | 0 images | **BUG** | English only | ⚠️ |
| v2.6.4 | 0 images | **FIXED** | **Multi-language** | ✅ |

---

## 📝 Known Issues (Non-Critical)

Same as previous versions:
1. **Black video from Luma** (rare, external API issue)
2. **Scene consistency ~60%** (acceptable for production)
3. **Minimax + Luma mix** (Router selects based on content_type, not a bug)

---

## 🔄 Upgrade Instructions

### From v2.6.3:
1. Extract new ZIP
2. No config changes needed
3. Test with `--language sk` or `--language en`

### From v2.6.2 or older:
1. Extract new ZIP
2. Update `.env` with API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Test

---

**Version:** 2.6.4  
**Previous Version:** 2.6.3  
**Release Date:** 2025-11-07  
**Status:** ✅ Production Ready - FFMPEG Fixed + Multi-Language Support
