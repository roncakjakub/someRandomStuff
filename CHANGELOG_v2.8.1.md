# Changelog v2.8.1 - Crossfade Transitions Fixed 🎬

**Date:** 2025-11-07  
**Status:** Production Ready ✅

---

## 🎯 Fix: CINEMATIC Crossfade Transitions

### Problem:

**CINEMATIC style** had hard cuts between videos instead of smooth crossfades.

**Before:**
```
Video 1 → [hard cut] → Video 2 → [hard cut] → Video 3
```

**Expected:**
```
Video 1 → [crossfade 0.3s] → Video 2 → [crossfade 0.3s] → Video 3
```

---

### Root Cause:

**Incorrect offset calculation** in `create_video_with_transitions()`:

```python
# OLD (v2.8.0)
offset = (5.0 * i) - (transition_duration * i)
```

**Problem:** Assumed all videos are **exactly 5 seconds**, but:
- Luma videos: 4-6 seconds
- Minimax videos: 5-6 seconds
- Actual duration varies!

→ Wrong offset → Crossfade applied at wrong time → Looks like hard cut

---

### Solution:

**Get actual video duration** using `ffprobe` before calculating offset:

```python
# NEW (v2.8.1)
# Step 1: Get actual duration of each clip
clip_durations = []
for clip_path in video_clips:
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(clip_path)]
    duration = float(json.loads(probe_result.stdout)["format"]["duration"])
    clip_durations.append(duration)

# Step 2: Calculate cumulative offset
cumulative_offset = 0.0
for i in range(1, len(video_clips)):
    cumulative_offset += clip_durations[i-1] - transition_duration
    offset = cumulative_offset
```

**Result:** Crossfade now happens at **correct time** between clips! ✅

---

## 🔍 What Changed

### File: `tools/video_assembly.py`

**Method:** `create_video_with_transitions()`

**Changes:**
1. ✅ Added `ffprobe` to get actual video duration
2. ✅ Calculate cumulative offset based on real durations
3. ✅ Fallback to 5.0s if ffprobe fails

**Lines:** 275-310

---

## 📊 Expected Behavior

### CINEMATIC Style:

```bash
python main.py --topic "coffee" --style cinematic --language sk
```

**Output:**
- 8 videos (Luma/Minimax)
- Smooth 0.3s crossfade transitions between all videos ✅
- No hard cuts ✅

---

### PIKA Style:

```bash
python main.py --topic "life of coffee" --style pika --language sk
```

**Output:**
- 7 Pika morph transition videos
- No crossfade needed (Pika morph is the transition) ✅

---

## 🎬 Technical Details

### FFMPEG xfade Filter:

**Before (wrong offset):**
```
[0:v][1:v]xfade=transition=fade:duration=0.3:offset=5.0[v01];
[v01][2:v]xfade=transition=fade:duration=0.3:offset=10.0[v02];
```
→ If video 1 is 4.5s, crossfade starts at 5.0s (after video ends!) ❌

**After (correct offset):**
```
[0:v][1:v]xfade=transition=fade:duration=0.3:offset=4.2[v01];
[v01][2:v]xfade=transition=fade:duration=0.3:offset=8.4[v02];
```
→ Crossfade starts at (4.5s - 0.3s) = 4.2s (correct!) ✅

---

## ✅ All Features (v2.8.1):

| Feature | CINEMATIC | PIKA |
|---------|-----------|------|
| Opening | Midjourney | Midjourney |
| Scenes 2-8 | Flux Dev | Seedream4 |
| Images | 8 | 8 |
| Videos | 8 | 7 (transitions) |
| Transitions | **Crossfade (fixed)** ✅ | Pika Morph |
| Cost/Scene | $0.15 | $0.25 |
| Time/Scene | 30s | 60s |

---

## 📦 Files Changed

### Modified Files:
1. `tools/video_assembly.py` - Fixed crossfade offset calculation

---

**Version:** 2.8.1  
**Previous Version:** 2.8.0  
**Release Date:** 2025-11-07  
**Status:** ✅ Production Ready
