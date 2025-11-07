# Changelog v2.8.3 - Video Duplication Fix 🎬

**Date:** 2025-11-07  
**Status:** Production Ready ✅

---

## 🎯 Fix: Duplicated Video in Final Output

### Problem:

When **only 1 video** was generated (due to API failures), the **final video contained that video 2× in a row**.

**Example:**
```
Input: 1 Minimax video (5s)
Output: Final video with same video played twice (10s total)
```

---

### Root Cause:

**VideoAssemblyTool** had an "FFMPEG concat quirk" that **duplicated the last item**:

```python
# OLD (v2.8.2)
for image in images:
    f.write(f"file '{image}'\n")
    f.write(f"duration {duration}\n")

# Add last image again (FFMPEG concat quirk)
f.write(f"file '{images[-1]}'\n")  # ❌ Always duplicates!
```

**Why this quirk exists:**
- For **images**, FFMPEG concat needs the last frame twice to show it for the full duration
- But for **videos**, this creates a duplicate!

**What happened:**
```
# Filelist for 1 video
file 'minimax_video.mp4'
duration 5.0
file 'minimax_video.mp4'  ← Duplicate!
```

→ FFMPEG played the video twice!

---

### Solution:

**Detect if inputs are videos or images**, and only apply quirk for images:

```python
# NEW (v2.8.3)
# Detect if inputs are videos or images
first_item = Path(images[0])
is_video = first_item.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']

for image in images:
    f.write(f"file '{image}'\n")
    if not is_video:
        # Only add duration for images, not videos
        f.write(f"duration {duration}\n")

if not is_video:
    # Add last image again (FFMPEG concat quirk for images only)
    f.write(f"file '{images[-1]}'\n")
```

**Now:**
- **Images** → Quirk applied ✅
- **Videos** → No quirk, no duplication ✅

---

## 🔍 What Changed

### File: `tools/video_assembly.py`

**Method:** `_create_video_from_images()`

**Changes:**
1. ✅ Detect if inputs are videos or images (line 111-113)
2. ✅ Only add `duration` for images (line 122-124)
3. ✅ Only apply quirk for images (line 126-129)

**Lines:** 111-129

---

## 📊 Expected Behavior (v2.8.3)

### Scenario 1: All videos generated successfully

```bash
python main.py --topic "coffee" --style cinematic
```

**Output:**
- 8 videos (Luma/Minimax)
- Assembly uses `create_video_with_transitions()` ✅
- Smooth crossfade transitions ✅
- No duplication ✅

---

### Scenario 2: Only 1 video generated (API failures)

**What happens:**
- Most video generations fail (Runway credits, Pika API)
- Only 1 video succeeds (e.g., Minimax)
- Assembly falls back to legacy mode

**Before (v2.8.2):**
```
Final video: [Video 1] [Video 1] ❌ Duplicate!
```

**After (v2.8.3):**
```
Final video: [Video 1] ✅ No duplicate!
```

---

### Scenario 3: Only images (no videos)

**What happens:**
- No videos generated
- Only images available
- Assembly uses legacy mode with images

**Behavior:**
- Quirk still applied ✅
- Last image shown for full duration ✅
- Works as before ✅

---

## ⚠️ Note: API Failures

**From user logs:**

1. **Runway:** `You do not have enough credits`
   - Add Runway credits
   - Or remove Runway from available tools

2. **Pika:** `404 Client Error: Not Found`
   - External FAL API issue
   - Retry later

3. **Minimax:** ✅ Worked!

**When APIs fail, workflow continues with whatever videos were generated.**

---

## 📦 Files Changed

### Modified Files:
1. `tools/video_assembly.py` - Fixed video duplication in concat

---

## ✅ All Features (v2.8.3)

| Feature | Status |
|---------|--------|
| CINEMATIC style | ✅ Works |
| PIKA style | ✅ Works |
| Crossfade transitions | ✅ Works |
| Router video_style | ✅ Works |
| **Video duplication** | **✅ Fixed** |
| Fallback for API failures | ✅ Works |

---

**Version:** 2.8.3  
**Previous Version:** 2.8.2  
**Release Date:** 2025-11-07  
**Status:** ✅ Production Ready

**No more duplicated videos!** 🎬
