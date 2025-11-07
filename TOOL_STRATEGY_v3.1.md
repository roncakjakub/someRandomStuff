# Tool Strategy v3.1 - Complete Scene Coverage

**Date:** Nov 7, 2025

---

## 🎯 Scene Types & Tool Mapping

### 1. **Human Portraits / Actions** (with character consistency)

**Use Case:** Same person across multiple scenes  
**Example:** Woman waking up → stretching → drinking coffee

**Tool:** `fal-ai/instant-character` ✅

**Why:**
- ✅ Strong identity control
- ✅ No multiple persons bug
- ✅ Reference image support
- ✅ Diverse poses & styles

**API:**
```javascript
{
  "prompt": "woman stretching in bedroom, morning light",
  "image_url": "reference_woman.jpg", // From Scene 1
  "scale": 1, // Character prominence
  "guidance_scale": 3.5
}
```

**Cost:** ~$0.03-0.04 per image

---

### 2. **Product Shots / Objects** (no people)

**Use Case:** Coffee beans, cup, grinder, etc.  
**Example:** "coffee beans falling", "espresso machine close-up"

**Tool:** `fal-ai/flux/dev` ✅ (current)

**Why:**
- ✅ Best for products & objects
- ✅ High quality, detailed
- ✅ No character needed
- ✅ Fast & cheap

**API:**
```javascript
{
  "prompt": "close-up of coffee beans, warm lighting, 4K",
  "image_size": "landscape_16_9",
  "num_inference_steps": 28
}
```

**Cost:** $0.025 per megapixel (~$0.03)

---

### 3. **Creative / Abstract Scenes** (no people, no specific objects)

**Use Case:** Abstract visuals, artistic shots  
**Example:** "steam rising", "liquid swirling", "light rays"

**Tool:** `fal-ai/flux/dev` ✅ (current)

**Why:**
- ✅ Best for abstract concepts
- ✅ Creative freedom
- ✅ No consistency needed

**Same as Product Shots**

---

### 4. **Environment / Style Consistency** (same location, different actions)

**Use Case:** Multiple scenes in the same kitchen/bedroom  
**Example:** "woman in kitchen" → "coffee machine in kitchen" → "woman drinking in kitchen"

**Tool:** `fal-ai/flux-pro/kontext` ⭐ NEW!

**Why:**
- ✅ **"Preserve objects or styles across different scenes"**
- ✅ Style transfer & consistency
- ✅ Environment preservation
- ✅ Can combine with character consistency

**API:**
```javascript
{
  "prompt": "Add a woman drinking coffee, keep the kitchen style",
  "image_url": "kitchen_scene1.jpg", // Reference environment
  "guidance_scale": 3.5
}
```

**Cost:** **$0.04 per image**

**Use Cases:**
- Same kitchen across multiple shots
- Same lighting/mood across scenes
- Same artistic style (e.g., all scenes in "warm cinematic" style)

---

### 5. **Video Morph Transitions** (between scenes)

**Use Case:** Smooth transitions within scene groups  
**Example:** Woman waking → stretching (same bedroom)

**Tool:** `fal-ai/veo3.1/fast/first-last-frame-to-video` ⭐ NEW!

**Why:**
- ✅ Google's latest model
- ✅ 8-second videos
- ✅ Natural motion
- ✅ Much better than Wan

**API:**
```javascript
{
  "first_frame_url": "scene1_image.jpg",
  "last_frame_url": "scene2_image.jpg",
  "prompt": "Woman slowly stretches and sits up in bed",
  "duration": "8s",
  "resolution": "720p",
  "generate_audio": false // Save 33%
}
```

**Cost:** $0.80 per 8s video (no audio)

---

## 📊 Complete Tool Matrix

| Scene Type | Tool | Cost | Use For |
|------------|------|------|---------|
| **Human (consistent)** | Instant Character | $0.03-0.04 | Same person, different poses |
| **Product/Object** | Flux Dev | $0.03 | Coffee, products, objects |
| **Creative/Abstract** | Flux Dev | $0.03 | Steam, abstract visuals |
| **Environment Style** | Flux Kontext Pro | $0.04 | Same location/style |
| **Video Morph** | Veo 3.1 FLF2V | $0.80/8s | Smooth transitions |

---

## 🎬 Example: "Life of Coffee" (8 scenes)

### Scene Group 1: Morning (Woman in Bedroom)

**Shot 1:** Woman sleeping  
**Tool:** Instant Character (generate first)  
**Cost:** $0.04

**Shot 2:** Woman waking up  
**Tool:** Instant Character (reference: Shot 1)  
**Cost:** $0.04

**Shot 3:** Woman stretching  
**Tool:** Instant Character (reference: Shot 1)  
**Cost:** $0.04

**Transitions:**
- Shot 1 → 2: Veo 3.1 morph ($0.80)
- Shot 2 → 3: Veo 3.1 morph ($0.80)

**Subtotal:** $0.12 (images) + $1.60 (video) = **$1.72**

---

### Scene Group 2: Coffee Making (Products in Kitchen)

**Shot 4:** Coffee beans close-up  
**Tool:** Flux Dev  
**Cost:** $0.03

**Shot 5:** Grinder working  
**Tool:** Flux Dev  
**Cost:** $0.03

**Shot 6:** Espresso pouring  
**Tool:** Flux Dev  
**Cost:** $0.03

**Transitions:**
- Shot 4 → 5: Veo 3.1 morph ($0.80)
- Shot 5 → 6: Veo 3.1 morph ($0.80)

**Subtotal:** $0.09 (images) + $1.60 (video) = **$1.69**

---

### Scene Group 3: Enjoying (Woman in Kitchen)

**Shot 7:** Woman holding cup  
**Tool:** Instant Character (reference: Shot 1)  
**Cost:** $0.04

**Shot 8:** Woman smiling, drinking  
**Tool:** Instant Character (reference: Shot 1)  
**Cost:** $0.04

**Transition:**
- Shot 7 → 8: Veo 3.1 morph ($0.80)

**Subtotal:** $0.08 (images) + $0.80 (video) = **$0.88**

---

### Total Cost (8 scenes, HYBRID style):

| Component | Cost |
|-----------|------|
| **Images (8 total)** | $0.29 |
| **Videos (5 morphs)** | $4.00 |
| **TOTAL** | **$4.29** |

**Compare to old (Wan + Seedream):** $2.30  
**Increase:** +$1.99 (87% more)  
**BUT:** Much better quality! ✅

---

## 🤔 What about "Same Kitchen" consistency?

### Option A: Use Flux Kontext Pro

**Workflow:**
1. Generate Shot 4 (kitchen) with Flux Dev
2. Use Flux Kontext Pro for Shots 5, 6 with reference to Shot 4
3. Prompt: "Add espresso machine, keep the kitchen style"

**Cost:**
- Shot 4: $0.03 (Flux Dev)
- Shot 5: $0.04 (Kontext Pro)
- Shot 6: $0.04 (Kontext Pro)
- **Total:** $0.11 (vs $0.09 without)

**Trade-off:** +$0.02 per scene group for style consistency

### Option B: Use detailed prompts (current)

**Workflow:**
1. Generate all shots with Flux Dev
2. Use very detailed prompt: "modern white kitchen, marble countertop, morning light from left window, minimalist style"
3. Same prompt for all kitchen shots

**Cost:** $0.03 per shot (no extra)

**Trade-off:** Less consistent, but cheaper

---

## 💡 Recommendations

### For HYBRID Style v3.1:

**Image Generation:**
1. **Human scenes:** Instant Character (character consistency)
2. **Product scenes:** Flux Dev (best quality)
3. **Creative scenes:** Flux Dev (abstract)
4. **Environment consistency:** Flux Kontext Pro (optional, +$0.01)

**Video Transitions:**
- **All morphs:** Veo 3.1 FLF2V (best quality)

### Cost Optimization:

**Budget Mode:**
- Skip Flux Kontext Pro
- Use detailed prompts for environment consistency
- **Cost:** $4.29 per 8-scene video

**Premium Mode:**
- Use Flux Kontext Pro for environment consistency
- Generate audio with Veo 3.1 (+33%)
- **Cost:** ~$5.50 per 8-scene video

---

## 🚀 Implementation Plan

### Phase 1: Core Tools ✅ PRIORITY

1. ✅ Implement Veo 3.1 FLF2V (replace Wan)
2. ✅ Implement Instant Character (replace Seedream4)
3. ✅ Keep Flux Dev (products/creative)

### Phase 2: Advanced Features (Optional)

4. ⏳ Implement Flux Kontext Pro (environment consistency)
5. ⏳ Add "Premium Mode" toggle (audio, kontext)

### Phase 3: Router Logic

6. ✅ Update scene detection
7. ✅ Map content_type → tool selection:
   - `human_portrait` → Instant Character
   - `human_action` → Instant Character
   - `product` → Flux Dev
   - `creative` → Flux Dev
   - `environment_ref` → Flux Kontext Pro (optional)

---

## 📝 Router Content Type Mapping

```python
TOOL_MAPPING = {
    "human_portrait": "instant_character",
    "human_action": "instant_character",
    "human_closeup": "instant_character",
    
    "product": "flux_dev",
    "product_closeup": "flux_dev",
    "object": "flux_dev",
    
    "creative": "flux_dev",
    "abstract": "flux_dev",
    "environment": "flux_dev",
    
    # Optional: environment consistency
    "environment_ref": "flux_kontext_pro",
}

VIDEO_TOOL = "veo31_flf2v"  # For all morph transitions
```

---

## ✅ Next Steps

1. **Implement Veo 3.1 tool** - `tools/veo31_flf2v.py`
2. **Implement Instant Character tool** - `tools/instant_character.py`
3. **Update Router** - content_type → tool mapping
4. **Test HYBRID workflow** - "life of coffee" example
5. **Optional:** Implement Flux Kontext Pro for premium mode

**Súhlasíš s týmto plánom?** 🚀
