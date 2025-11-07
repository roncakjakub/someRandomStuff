# Edge Cases & Solutions v3.1

**Date:** Nov 7, 2025

---

## 🚨 Potential Edge Cases & Solutions

### 1. **Single Scene Group (All Same Location)**

**Scenario:** User wants 8 scenes, all in the same kitchen

**Example:** "Life of coffee" but ALL scenes in kitchen:
- Woman making coffee
- Coffee beans
- Grinder working
- Espresso pouring
- Woman drinking
- Close-up of cup
- Woman smiling
- Final product shot

**Problem:** Only 1 scene group → only first shot uses Flux Dev, rest use Kontext Pro

**Solution:** ✅ **GOOD!** This is exactly what we want:
- Shot 1: Flux Dev (establish kitchen)
- Shots 2-8: Flux Kontext Pro (keep same kitchen)
- Result: Perfect environment consistency

**Cost:** $0.03 + (7 × $0.04) = $0.31 (vs $0.24 without Kontext)
**Extra:** +$0.07 for perfect consistency ✅

---

### 2. **All Human Scenes (No Products)**

**Scenario:** User wants only human character shots

**Example:** "Woman's morning routine":
- Sleeping
- Waking up
- Stretching
- Walking
- Brushing teeth
- Getting dressed
- Eating breakfast
- Leaving house

**Problem:** No product/environment scenes → no Flux Kontext Pro used

**Solution:** ✅ **GOOD!** Instant Character handles all:
- Shot 1: Midjourney (establish character)
- Shots 2-8: Instant Character (same person)
- Result: Perfect character consistency

**Cost:** $0.05 + (7 × $0.04) = $0.33
**No extra cost** for environment (not needed)

---

### 3. **All Product Scenes (No Humans)**

**Scenario:** User wants only product shots

**Example:** "Coffee product showcase":
- Beans in bag
- Beans pouring
- Grinder close-up
- Grinding action
- Espresso machine
- Espresso pouring
- Cup with foam
- Final product shot

**Problem:** All products, different angles/actions

**Question:** Should we use Kontext Pro for environment consistency?

**Solution:** ✅ **YES, if same location!**

**If all in same kitchen:**
- Shot 1: Flux Dev (establish kitchen)
- Shots 2-8: Flux Kontext Pro (keep kitchen)
- Result: All products in same environment

**If different locations (e.g., factory → café → home):**
- Scene detection will group by location
- Each location starts with Flux Dev
- Subsequent shots in same location use Kontext Pro

**Cost (same location):** $0.03 + (7 × $0.04) = $0.31
**Cost (3 locations, ~3 shots each):** (3 × $0.03) + (5 × $0.04) = $0.29

---

### 4. **Mixed Scene Groups with Multiple Locations**

**Scenario:** Complex story with location changes

**Example:** "Coffee journey":
- **Group 1 (Farm):** Farmer picking beans, beans drying, beans in bag
- **Group 2 (Factory):** Roasting machine, beans roasting, packaging
- **Group 3 (Café):** Barista making coffee, espresso pouring, customer drinking

**Problem:** Need to track BOTH character AND environment references per group

**Solution:** ✅ **Already handled!**

Router tracks:
- `group_first_human[scene_group]` → for character reference
- `group_first_environment[scene_group]` → for environment reference

**Example routing:**
```
Group 1 (Farm):
  Shot 1: Midjourney (farmer) → save as human ref
  Shot 2: Instant Character (farmer, ref: shot 1)
  Shot 3: Flux Dev (beans) → save as environment ref
  
Group 2 (Factory):
  Shot 4: Flux Dev (roasting machine) → new environment ref
  Shot 5: Flux Kontext Pro (beans roasting, ref: shot 4)
  Shot 6: Flux Kontext Pro (packaging, ref: shot 4)
  
Group 3 (Café):
  Shot 7: Midjourney (barista) → new human ref
  Shot 8: Instant Character (barista, ref: shot 7)
  Shot 9: Flux Kontext Pro (espresso, ref: shot 7 environment)
```

**Cost:** 
- Midjourney: 2 × $0.05 = $0.10
- Instant Character: 1 × $0.04 = $0.04
- Flux Dev: 2 × $0.03 = $0.06
- Flux Kontext Pro: 4 × $0.04 = $0.16
- **Total images:** $0.36

**Videos:** 8 morphs × $0.80 = $6.40
**Total:** $6.76 for 9 scenes

---

### 5. **Character + Environment in Same Scene**

**Scenario:** Human in specific environment that needs consistency

**Example:** "Woman in HER kitchen" (same person, same kitchen across multiple scenes)

**Problem:** Need BOTH character AND environment consistency simultaneously

**Current Solution:** ❌ **CONFLICT!**
- Instant Character → preserves character
- Flux Kontext Pro → preserves environment
- **Can't use both at once!**

**Better Solution:** ✅ **Use Instant Character with environment prompt!**

**Workflow:**
```
Group 1 (Woman in Kitchen):
  Shot 1: Midjourney (woman in kitchen) → save as character ref
  Shot 2: Instant Character (
    prompt: "woman stretching in THE SAME modern white kitchen, 
             keep marble countertop, warm lighting, minimalist style",
    reference: shot 1
  )
  Shot 3: Instant Character (
    prompt: "woman pouring coffee in THE SAME kitchen...",
    reference: shot 1
  )
```

**Key:** Use **detailed environment description** in Instant Character prompts!

**Alternative:** Use Flux Kontext Pro for environment, accept slight character variation

**Recommendation:** 
- **Primary character focus** → Instant Character + detailed environment prompts
- **Primary environment focus** → Flux Kontext Pro (character can vary slightly)

---

### 6. **Very Short Videos (2-3 scenes)**

**Scenario:** User wants only 2-3 scenes

**Example:** "Quick coffee ad":
- Coffee beans
- Espresso pouring
- Final cup

**Problem:** Only 1 scene group, only 2 morphs

**Solution:** ✅ **Works fine!**
- Shot 1: Flux Dev ($0.03)
- Shot 2: Flux Kontext Pro ($0.04)
- Shot 3: Flux Kontext Pro ($0.04)
- Videos: 2 × $0.80 = $1.60
- **Total:** $1.71

**Cost-effective for short videos!**

---

### 7. **Very Long Videos (20+ scenes)**

**Scenario:** User wants long-form content

**Example:** "Complete coffee story" with 20 scenes

**Problem:** High cost with Veo 3.1 ($0.80 per morph)

**Cost Breakdown:**
- Images: ~$0.80 (mix of tools)
- Videos: 19 morphs × $0.80 = **$15.20**
- **Total:** ~$16.00

**Solution Options:**

**A) Keep Veo 3.1 (premium quality)**
- Best quality
- Expensive but worth it

**B) Offer "Budget Mode"**
- Use cheaper video tool for some transitions
- E.g., Luma Ray ($0.15) for filler shots
- Veo 3.1 ($0.80) for key transitions
- **Hybrid pricing:** ~$8-10 for 20 scenes

**C) Warn user about cost**
- Show estimated cost upfront
- Let user decide: quality vs budget

**Recommendation:** Implement **Budget Mode toggle** for long videos!

---

### 8. **API Failures & Retries**

**Scenario:** Veo 3.1 or Instant Character API fails

**Problem:** Expensive tools failing = wasted money

**Solution:** ✅ **Implement retry logic with fallbacks**

**Retry Strategy:**
```python
def generate_with_retry(tool, max_retries=3):
    for attempt in range(max_retries):
        try:
            return tool.execute(...)
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt+1} failed, retrying...")
                time.sleep(5)
            else:
                logger.error(f"All retries failed!")
                raise
```

**Fallback Strategy:**
```python
# If Veo 3.1 fails, fallback to Wan FLF2V
# If Instant Character fails, fallback to Flux Dev
# If Flux Kontext Pro fails, fallback to Flux Dev
```

---

### 9. **Reference Image Quality Issues**

**Scenario:** First image in group is low quality → affects all subsequent images

**Problem:** Kontext Pro or Instant Character using bad reference

**Solution:** ✅ **Quality check on first image**

**Workflow:**
```python
def generate_first_image(scene):
    # Generate with Midjourney or Flux Dev
    image = tool.execute(...)
    
    # Quality check (optional)
    if quality_score(image) < threshold:
        logger.warning("Low quality reference, regenerating...")
        image = tool.execute(..., seed=new_seed)
    
    return image
```

**Alternative:** Let user review first image before proceeding

---

### 10. **Scene Detection Errors**

**Scenario:** AI incorrectly groups scenes

**Example:** Misses location change, groups "kitchen" and "café" together

**Problem:** Wrong reference images used

**Solution:** ✅ **Manual override option**

**Workflow:**
```python
# Auto-detect scene groups
scenes_with_groups = detector.detect_scene_groups(scenes)

# Show user for confirmation
print(detector.get_scene_summary(scenes_with_groups))

# Allow manual adjustment
if user_wants_to_adjust:
    scenes_with_groups = user.adjust_scene_groups(scenes_with_groups)
```

**Alternative:** Add confidence scores to scene detection

---

## 📊 Priority Ranking

| Edge Case | Impact | Likelihood | Priority | Solution Status |
|-----------|--------|------------|----------|-----------------|
| **Character + Environment** | High | High | 🔴 **P0** | ✅ Use detailed prompts |
| **API Failures** | High | Medium | 🔴 **P0** | ⏳ Need retry logic |
| **Long Videos (20+)** | High | Medium | 🟡 **P1** | ⏳ Need budget mode |
| **Scene Detection Errors** | Medium | Low | 🟡 **P1** | ⏳ Need manual override |
| **Reference Quality** | Medium | Low | 🟢 **P2** | ⏳ Optional feature |
| **Single Scene Group** | Low | High | ✅ **OK** | ✅ Works as intended |
| **All Human Scenes** | Low | Medium | ✅ **OK** | ✅ Works as intended |
| **All Product Scenes** | Low | Medium | ✅ **OK** | ✅ Works as intended |
| **Mixed Groups** | Low | High | ✅ **OK** | ✅ Already handled |
| **Short Videos (2-3)** | Low | Medium | ✅ **OK** | ✅ Works as intended |

---

## 🎯 Immediate Action Items

### P0 (Critical):
1. ✅ **Character + Environment:** Document best practices for prompts
2. ⏳ **API Retry Logic:** Implement retry with exponential backoff
3. ⏳ **Fallback Strategy:** Wan FLF2V, Flux Dev as fallbacks

### P1 (Important):
4. ⏳ **Budget Mode:** Toggle for long videos (use cheaper tools)
5. ⏳ **Manual Scene Override:** Let user adjust scene grouping
6. ⏳ **Cost Warning:** Show estimated cost before generation

### P2 (Nice to have):
7. ⏳ **Reference Quality Check:** Optional quality validation
8. ⏳ **Scene Detection Confidence:** Show confidence scores
9. ⏳ **Preview Mode:** Generate first image, let user approve

---

## ✅ Recommendations

### For v3.1 Launch:
1. ✅ **Ship with current implementation** (handles most cases well)
2. ✅ **Add detailed prompt guidelines** for character + environment
3. ⏳ **Add retry logic** for API failures (critical!)
4. ⏳ **Show cost estimate** before generation

### For v3.2 (Future):
5. ⏳ **Budget Mode** for long videos
6. ⏳ **Manual scene override** for power users
7. ⏳ **Reference quality check** for premium mode

---

**Súhlasíš s týmto plánom?** Ktoré edge cases sú pre teba najdôležitejšie? 🤔
