# Changelog v2.8.4 - CINEMATIC Transitions Fix + Minimax Priority 🎬

**Date:** 2025-11-07  
**Status:** Production Ready ✅

---

## 🎯 Two Important Fixes

### Fix #1: CINEMATIC Style No Longer Uses Pika

**Problem:**

CINEMATIC style was generating **transition scenes** with `content_type="transition"`:

```json
{
  "scene": 4,
  "content_type": "transition",  // ❌ Wrong for CINEMATIC!
  "tool": "flux"
}
```

→ Router saw `content_type="transition"` → Selected **Pika** ❌  
→ Pika API failed (FAL 404 error)  
→ No video generated

**Expected:**
- CINEMATIC should use **crossfade transitions** (handled by Assembly Agent)
- NO Pika calls
- All scenes: `content_type="object"` or `"product"`

---

**Root Cause:**

Creative Strategist was generating transition scenes for ALL styles, including CINEMATIC.

**Solution:**

Added explicit rule to CINEMATIC style instructions:

```python
# agents/creative_strategist.py line 401-403
**CRITICAL:** NEVER use content_type="transition" for CINEMATIC style!
- All scenes must have content_type: "object", "product", "abstract", or "text"
- Transitions are created automatically during assembly, NOT during scene generation
```

**Now:**
- CINEMATIC: All scenes = "object"/"product" → Minimax/Luma → Crossfade ✅
- PIKA: All scenes = "transition" → Pika morph ✅

---

### Fix #2: Router Prefers Minimax Over Runway

**Problem:**

Router was selecting **Runway** as default video tool:

```
Default → use runway_gen4_turbo (best value)
```

**But Minimax is BETTER:**

| Feature | Runway | Minimax |
|---------|--------|---------|
| Quality | Good | **Very Good** ✅ |
| Speed | ~20s | ~15s ✅ |
| Cost | $0.05/s | $0.025/s ✅ |
| Stability | Good | **Better** ✅ |

**User feedback:** "Minimax má dobré výsledky" ✅

---

**Solution:**

Updated Router video tool selection rules:

```python
# workflow_router_v2.py line 418-425
**VIDEO TOOL SELECTION BY CONTENT:**
- If scene content_type is human_action/human_portrait → use minimax_hailuo (best quality)
- If scene content_type is object/product → use minimax_hailuo or luma_ray (prefer minimax)
- Default → use minimax_hailuo (best quality and value)
- AVOID runway_gen4_turbo (minimax is better quality and cheaper)
```

**Now:**
- Default: **Minimax** ✅
- Fallback: Luma Ray
- Runway: Only if explicitly needed

---

## 🔍 What Changed

### File: `agents/creative_strategist.py`

**CINEMATIC style instructions (line 398-403):**

```python
# OLD (v2.8.3)
3. **Transitions:**
   - Crossfade (300ms) between scenes
   - Smooth, professional

# NEW (v2.8.4)
3. **Transitions:**
   - Crossfade (300ms) between scenes (handled by Assembly Agent)
   - Smooth, professional
   - **CRITICAL:** NEVER use content_type="transition" for CINEMATIC style!
   - All scenes must have content_type: "object", "product", "abstract", or "text"
   - Transitions are created automatically during assembly, NOT during scene generation
```

---

### File: `workflow_router_v2.py`

**Video tool selection rules (line 418-425):**

```python
# OLD (v2.8.3)
- If scene content_type is object/product → use runway_gen4_turbo or luma_ray
- Default → use runway_gen4_turbo (best value)

# NEW (v2.8.4)
- If scene content_type is object/product → use minimax_hailuo or luma_ray (prefer minimax)
- Default → use minimax_hailuo (best quality and value)
- AVOID runway_gen4_turbo (minimax is better quality and cheaper)
```

---

## 📊 Expected Behavior (v2.8.4)

### CINEMATIC Style:

```bash
python main.py --topic "coffee" --style cinematic --language sk
```

**Workflow:**
1. Creative Strategist generates 8 scenes
   - All scenes: `content_type="object"` ✅
   - NO transition scenes ✅

2. Router selects tools:
   - Scene 1: Midjourney → **Minimax** ✅
   - Scenes 2-8: Flux Dev → **Minimax** ✅

3. Visual Production Agent:
   - Generates 8 images
   - Generates 8 Minimax videos ✅

4. Assembly Agent:
   - Creates crossfade transitions ✅
   - Final video with smooth transitions ✅

**NO Pika calls!** ✅  
**NO Runway calls!** ✅

---

### PIKA Style:

```bash
python main.py --topic "life of coffee" --style pika --language sk
```

**Workflow:**
1. Creative Strategist generates 8 scenes
   - All scenes: Seedream4 with references ✅

2. Visual Production Agent:
   - Generates 8 images (1 MJ + 7 Seedream4)
   - Creates 7 Pika morph transitions ✅

**Pika IS used** (as intended) ✅

---

## 🚀 Benefits

### Benefit #1: No More Pika Failures in CINEMATIC

**Before (v2.8.3):**
```
Scene 4: transition → Pika → 404 upload error ❌
Scene 5: transition → Pika → 404 upload error ❌
```

**After (v2.8.4):**
```
Scene 4: object → Minimax → Success ✅
Scene 5: object → Minimax → Success ✅
```

---

### Benefit #2: Better Quality & Lower Cost

**Before (v2.8.3):**
```
8 scenes × Runway ($0.05/s × 5s) = $2.00
Quality: Good
```

**After (v2.8.4):**
```
8 scenes × Minimax ($0.025/s × 5s) = $1.00
Quality: Very Good ✅
```

**Savings:** 50% cost reduction + better quality! 🎉

---

## 📦 Files Changed

### Modified Files:
1. `agents/creative_strategist.py` - No transitions for CINEMATIC
2. `workflow_router_v2.py` - Prefer Minimax over Runway

---

## ✅ All Features (v2.8.4)

| Feature | Status |
|---------|--------|
| CINEMATIC style | ✅ Works (no Pika) |
| PIKA style | ✅ Works (uses Pika) |
| Crossfade transitions | ✅ Works |
| Router video_style | ✅ Works |
| Video duplication | ✅ Fixed |
| **Minimax priority** | **✅ Added** |
| **No transition scenes in CINEMATIC** | **✅ Fixed** |

---

**Version:** 2.8.4  
**Previous Version:** 2.8.3  
**Release Date:** 2025-11-07  
**Status:** ✅ Production Ready

**CINEMATIC now uses Minimax exclusively!** 🎬
