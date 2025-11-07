# HYBRID Style Specification v1.0

**Status:** Design Document (Not Yet Implemented)  
**Target Version:** v3.0.0  
**Date:** 2025-11-07

---

## 🎯 Vision

**HYBRID style** combines the best of **PIKA** (character consistency + smooth morphs) and **CINEMATIC** (beautiful product shots + camera movements) into a **single, intelligent workflow**.

### Key Concept:

> **Within-scene continuity** (Pika morph) + **Between-scene cuts** (hard transitions)

---

## 🎬 How It Works

### Scene Structure:

```
VIDEO = Multiple SCENES
SCENE = Multiple SHOTS

Within SCENE: Pika morph transitions (smooth)
Between SCENES: Hard cuts or fades
```

### Example: "Life of Coffee"

```
┌─ SCENE 1: Morning Garden (4 shots) ─────────────────┐
│ Shot 1: Woman waking up                              │
│   ↓ PIKA MORPH                                       │
│ Shot 2: Woman stretching                             │
│   ↓ PIKA MORPH                                       │
│ Shot 3: Woman walking to kitchen                     │
│   ↓ PIKA MORPH                                       │
│ Shot 4: Woman opening door                           │
└──────────────────────────────────────────────────────┘
                    ↓ HARD CUT
┌─ SCENE 2: Coffee Making (3 shots) ──────────────────┐
│ Shot 5: Coffee beans close-up                        │
│   ↓ PIKA MORPH                                       │
│ Shot 6: Grinder in action                            │
│   ↓ PIKA MORPH                                       │
│ Shot 7: Pouring coffee                               │
└──────────────────────────────────────────────────────┘
                    ↓ HARD CUT
┌─ SCENE 3: Enjoying Coffee (2 shots) ────────────────┐
│ Shot 8: Woman drinking coffee                        │
│   ↓ PIKA MORPH                                       │
│ Shot 9: Woman smiling                                │
└──────────────────────────────────────────────────────┘
```

---

## 🤖 Auto Scene Detection

### How Router Detects Scene Changes:

```python
def is_scene_change(shot1, shot2):
    """
    Detect if there's a major scene change between two shots.
    
    Returns:
        True: Hard cut (new scene)
        False: Pika morph (same scene)
    """
    
    # Rule 1: Location change
    if location_changed(shot1, shot2):
        return True  # Example: Garden → Kitchen
    
    # Rule 2: Subject change (person → object or vice versa)
    if subject_changed(shot1, shot2):
        return True  # Example: Woman → Coffee beans
    
    # Rule 3: Time jump
    if time_jump(shot1, shot2):
        return True  # Example: Morning → Afternoon
    
    # Rule 4: Camera distance jump (close-up → wide shot)
    if camera_distance_jump(shot1, shot2):
        return True  # Example: Macro → Landscape
    
    return False  # Same scene → Pika morph
```

### Detection Logic:

#### Location Change:

```python
def location_changed(shot1, shot2):
    """Detect location change from descriptions."""
    
    locations_1 = extract_locations(shot1.description)
    locations_2 = extract_locations(shot2.description)
    
    # Example:
    # Shot 1: "woman in garden" → ["garden"]
    # Shot 2: "coffee beans in kitchen" → ["kitchen"]
    # → Different locations → True
    
    return not any(loc in locations_2 for loc in locations_1)
```

#### Subject Change:

```python
def subject_changed(shot1, shot2):
    """Detect subject change (person ↔ object)."""
    
    # Check content_type
    human_types = ["human_portrait", "human_action"]
    object_types = ["object", "product", "food"]
    
    shot1_is_human = shot1.content_type in human_types
    shot2_is_human = shot2.content_type in human_types
    
    # Person → Object or Object → Person
    return shot1_is_human != shot2_is_human
```

#### Time Jump:

```python
def time_jump(shot1, shot2):
    """Detect time jump from descriptions."""
    
    time_keywords = {
        "morning": 1,
        "afternoon": 2,
        "evening": 3,
        "night": 4,
    }
    
    time1 = extract_time(shot1.description, time_keywords)
    time2 = extract_time(shot2.description, time_keywords)
    
    # Jump more than 1 time period
    return abs(time1 - time2) > 1
```

---

## 🎨 Image Generation Strategy

### Character Consistency:

**Reference Image Management:**

```python
reference_image = None  # Global reference for character

for shot in shots:
    # First human shot: Create reference
    if shot.content_type in ["human_portrait", "human_action"]:
        if reference_image is None:
            # Generate with Midjourney (high quality)
            image = generate_image(tool="midjourney", prompt=shot.prompt)
            reference_image = image  # Save as reference
        else:
            # Use reference for consistency
            image = generate_image(
                tool="seedream4",
                prompt=shot.prompt,
                reference_image=reference_image
            )
    
    # Object shots: No reference needed
    else:
        image = generate_image(tool="flux_dev", prompt=shot.prompt)
```

### Tool Selection:

| Content Type | Tool | Reference | Why |
|--------------|------|-----------|-----|
| **human_portrait** (first) | Midjourney | None | High quality character |
| **human_portrait** (2+) | Seedream4 | Scene 1 | Same character |
| **human_action** | Seedream4 | Scene 1 | Same character |
| **object** | Flux Dev | None | Beautiful products |
| **product** | Flux Dev | None | Beautiful products |
| **food** | Flux Dev | None | Beautiful food |
| **nature** | Flux Dev | None | Beautiful landscapes |

---

## 🎥 Video Generation Strategy

### Within Scene (Pika Morph):

```python
for i in range(len(scene_shots) - 1):
    shot1 = scene_shots[i]
    shot2 = scene_shots[i + 1]
    
    # Generate Pika morph transition
    video = pika_tool.execute(
        image_url=shot1.image_url,
        end_image_url=shot2.image_url,  # Morph to next shot
        prompt=f"{shot1.description} morphing to {shot2.description}",
        duration=3,
    )
```

### Between Scenes (Hard Cut):

```python
# No transition video needed
# Just concatenate scenes with hard cut in final assembly
```

---

## 📊 Workflow Comparison

| Feature | PIKA | CINEMATIC | **HYBRID** |
|---------|------|-----------|------------|
| **Character Consistency** | ✅ Same person | ❌ Different | ✅ Same person |
| **Product Shots** | ⚠️ OK | ✅ Beautiful | ✅ Beautiful |
| **Transitions** | ✅ All morph | ⚠️ All Luma | ✅ Smart mix |
| **Scene Changes** | ❌ No cuts | ✅ Hard cuts | ✅ Auto cuts |
| **Flexibility** | ❌ One style | ❌ One style | ✅ Adaptive |
| **Best For** | Character stories | Products/Nature | **Everything** |

---

## 🔧 Implementation Plan

### Phase 1: Scene Detection (v3.0.0)

**Files to modify:**

1. `workflow_router_v2.py`
   - Add `is_scene_change()` logic
   - Add scene grouping to plan output

2. `agents/visual_production_agent.py`
   - Read scene groups from plan
   - Generate Pika morph within scenes
   - Hard cut between scenes

**New fields in plan:**

```python
{
    "number": 1,
    "scene_group": 1,  # NEW: Scene grouping
    "content_type": "human_portrait",
    "description": "woman in garden",
    "image_tool": "midjourney",
    "video_tool": "pika_v2",
    "transition": "morph",  # NEW: morph or cut
}
```

### Phase 2: Smart Reference Management (v3.0.0)

**Logic:**

```python
# Track reference per scene_group
scene_references = {}  # {scene_group: reference_image}

for shot in shots:
    group = shot.scene_group
    
    if shot.content_type in ["human_portrait", "human_action"]:
        if group not in scene_references:
            # First human in this scene
            image = generate(..., tool="midjourney")
            scene_references[group] = image
        else:
            # Use scene reference
            image = generate(..., reference=scene_references[group])
```

### Phase 3: Transition Assembly (v3.0.0)

**Video assembly:**

```python
final_clips = []

for scene_group in scene_groups:
    scene_clips = []
    
    # Within scene: Pika morph
    for i in range(len(scene_group.shots) - 1):
        morph_video = pika_morph(shot[i], shot[i+1])
        scene_clips.append(morph_video)
    
    # Concatenate scene clips
    scene_video = concatenate(scene_clips)
    final_clips.append(scene_video)

# Between scenes: Hard cut
final_video = concatenate(final_clips, transition="cut")
```

---

## 🎯 Use Cases

### ✅ Perfect For:

1. **Character Journey with Products**
   - Example: "Life of coffee" (woman + coffee products)
   - Character scenes: Pika morph
   - Product scenes: Flux Dev + Pika morph
   - Scene changes: Hard cuts

2. **Before/After Transformation**
   - Example: "Fitness journey"
   - Person scenes: Same character
   - Environment scenes: Different locations
   - Smooth within, cuts between

3. **Day in the Life**
   - Example: "Morning routine"
   - Multiple locations (bedroom, kitchen, bathroom)
   - Same person throughout
   - Scene changes at location changes

### ❌ Not Needed For:

1. **Pure Product Videos** → Use CINEMATIC
2. **Pure Character Stories** → Use PIKA
3. **Abstract Concepts** → Use CINEMATIC

---

## 📋 Configuration

### User Command:

```bash
python main.py --topic "life of coffee" --style hybrid --language sk
```

### Router Behavior:

```python
if video_style == "hybrid":
    # Auto-detect scene changes
    plan = create_plan_with_scene_detection(topic)
    
    # Smart tool selection
    for shot in plan:
        if shot.content_type in ["human_portrait", "human_action"]:
            shot.image_tool = "seedream4" if has_reference else "midjourney"
        else:
            shot.image_tool = "flux_dev"
        
        shot.video_tool = "pika_v2"  # Always Pika for transitions
```

---

## 🚀 Benefits

### 1. **Best of Both Worlds**

- ✅ Character consistency (PIKA)
- ✅ Beautiful products (CINEMATIC)
- ✅ Smooth transitions (PIKA)
- ✅ Scene structure (CINEMATIC)

### 2. **Fully Automatic**

- ✅ No manual scene grouping
- ✅ AI detects scene changes
- ✅ Smart tool selection
- ✅ Adaptive workflow

### 3. **Professional Output**

- ✅ Cinematic scene structure
- ✅ Smooth within-scene motion
- ✅ Clear scene boundaries
- ✅ Character consistency

---

## 📝 Example Output

### Input:

```bash
python main.py --topic "life of coffee" --style hybrid
```

### Router Plan:

```
Scene 1: Morning (Woman)
  Shot 1: Woman waking up [Midjourney] → morph
  Shot 2: Woman stretching [Seedream4 + ref] → morph
  Shot 3: Woman to kitchen [Seedream4 + ref] → CUT

Scene 2: Coffee Making (Products)
  Shot 4: Coffee beans [Flux Dev] → morph
  Shot 5: Grinder [Flux Dev] → morph
  Shot 6: Pouring [Flux Dev] → CUT

Scene 3: Enjoying (Woman)
  Shot 7: Woman drinking [Seedream4 + ref] → morph
  Shot 8: Woman smiling [Seedream4 + ref] → END
```

### Output Video:

```
[Woman waking → stretching → walking] MORPH MORPH
                                      CUT
[Beans → Grinder → Pouring] MORPH MORPH
                            CUT
[Woman drinking → smiling] MORPH
```

---

## 🎬 Summary

**HYBRID style = Smart, Adaptive, Professional**

- ✅ Auto scene detection
- ✅ Character consistency
- ✅ Beautiful products
- ✅ Smooth + structured
- ✅ Best for complex stories

**Target:** v3.0.0 (Future Implementation)

---

**This is the future of Social Video Agent!** 🚀
