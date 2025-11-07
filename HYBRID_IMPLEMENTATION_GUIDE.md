# HYBRID Style Implementation Guide 🎬

**Version:** v3.0.0 (Implementation Roadmap)  
**Date:** 2025-11-07  
**Status:** Design + Implementation Plan

---

## 🎯 Problem Statement

### Your Coffee Example:

```
Scene 1: Kava na strome (coffee on tree)
Scene 2: Kava cerstva pozbierana (fresh picked coffee)
Scene 3: Kava v mlynceku usušená (dried coffee in grinder)
```

**Current PIKA behavior:**
- ✅ All scenes use Seedream4
- ✅ All scenes use Pika morph transitions
- ❌ **Scene 1 used as reference for Scenes 2-3**

**Problem:**

> **Seedream4 používa Scene 1 (coffee on tree) ako reference pre Scene 2 (fresh coffee) a Scene 3 (grinder)!**

**Výsledok:**
- Scene 2 vyzerá ako "coffee on tree" (nie fresh picked!)
- Scene 3 vyzerá ako "coffee on tree" (nie grinder!)
- ❌ **Reference image KAZÍ product shots!**

---

## 🔍 Root Cause Analysis

### PIKA Style Logic (v2.9.0):

```python
# Current implementation
reference_image = None

for scene in scenes:
    if scene_number == 1:
        # Generate Scene 1
        image = generate(tool="midjourney")
        reference_image = image  # ✅ Save reference
    else:
        # Scenes 2+: Use Scene 1 as reference
        image = generate(
            tool="seedream4",
            reference_image=reference_image  # ❌ ALWAYS use Scene 1!
        )
```

**Problém:**

> **Reference image je dobrý pre CHARACTER consistency, nie pre PRODUCT variety!**

### When Reference Works:

**Character Story:**
```
Scene 1: Woman in garden (reference) ✅
Scene 2: Woman drinking coffee (use reference) ✅ → Same woman!
Scene 3: Woman smiling (use reference) ✅ → Same woman!
```

### When Reference FAILS:

**Product Story (Your Case):**
```
Scene 1: Coffee on tree (reference) ✅
Scene 2: Fresh coffee (use reference) ❌ → Looks like tree!
Scene 3: Grinder (use reference) ❌ → Looks like tree!
```

---

## ✅ Solution: Smart Reference Logic

### Rule:

> **Use reference ONLY when content_type is SAME as reference scene!**

### Implementation:

```python
reference_image = None
reference_content_type = None

for scene in scenes:
    if scene_number == 1:
        # Generate Scene 1
        image = generate(tool="midjourney", prompt=scene.prompt)
        reference_image = image
        reference_content_type = scene.content_type  # Save type!
    else:
        # Scenes 2+: Use reference ONLY if same content type
        if scene.content_type == reference_content_type:
            # Same type → Use reference
            use_reference = reference_image  # ✅
        else:
            # Different type → NO reference
            use_reference = None  # ✅
        
        image = generate(
            tool="seedream4",
            prompt=scene.prompt,
            reference_image=use_reference
        )
```

---

## 📊 Content Type Matching

### Content Types:

| Content Type | Description | Example |
|--------------|-------------|---------|
| **human_portrait** | Person face/body | "woman smiling" |
| **human_action** | Person doing action | "woman drinking coffee" |
| **object** | Single object | "coffee cup" |
| **product** | Product shot | "coffee beans" |
| **food** | Food/drink | "latte art" |
| **nature** | Landscape/plants | "coffee tree" |
| **abstract** | Abstract concept | "steam rising" |

### Matching Rules:

```python
def should_use_reference(reference_type, scene_type):
    """Determine if reference should be used."""
    
    # Rule 1: Exact match
    if reference_type == scene_type:
        return True  # ✅ Use reference
    
    # Rule 2: Human types match
    human_types = ["human_portrait", "human_action"]
    if reference_type in human_types and scene_type in human_types:
        return True  # ✅ Same person
    
    # Rule 3: Product types DON'T match
    product_types = ["object", "product", "food", "nature"]
    if reference_type in product_types and scene_type in product_types:
        return False  # ❌ Different products!
    
    # Rule 4: Default: No reference
    return False
```

---

## 🎬 Your Coffee Example - Fixed

### Input Scenes:

```python
scenes = [
    {
        "number": 1,
        "content_type": "nature",  # Coffee tree
        "description": "kava na strome",
    },
    {
        "number": 2,
        "content_type": "product",  # Fresh coffee
        "description": "kava cerstva pozbierana",
    },
    {
        "number": 3,
        "content_type": "object",  # Grinder
        "description": "kava v mlynceku usušená",
    },
]
```

### Current Behavior (v2.9.0):

```
Scene 1: nature → Midjourney → "coffee on tree" ✅
  reference = Scene 1 image

Scene 2: product → Seedream4 + reference ❌
  → Looks like "coffee on tree" (wrong!)

Scene 3: object → Seedream4 + reference ❌
  → Looks like "coffee on tree" (wrong!)
```

### Fixed Behavior (v3.0.0):

```
Scene 1: nature → Midjourney → "coffee on tree" ✅
  reference = Scene 1 image
  reference_type = "nature"

Scene 2: product → Seedream4 + NO reference ✅
  → "nature" != "product" → NO reference
  → Fresh coffee (correct!) ✅

Scene 3: object → Seedream4 + NO reference ✅
  → "nature" != "object" → NO reference
  → Grinder (correct!) ✅
```

---

## 🔧 Implementation Steps

### Step 1: Update PIKA Workflow

**File:** `agents/visual_production_agent.py`

**Current code (line ~514):**

```python
reference_image = None

for scene_number, scene in enumerate(scenes, 1):
    if scene_number == 1:
        image_path = self._generate_image(...)
        reference_image = image_path  # ❌ Always save
    else:
        use_reference = reference_image if image_tool_name == "seedream4" else None
        image_path = self._generate_image(..., reference_image=use_reference)
```

**New code:**

```python
reference_image = None
reference_content_type = None

for scene_number, scene in enumerate(scenes, 1):
    scene_content_type = scene.get("content_type", "object")
    
    if scene_number == 1:
        image_path = self._generate_image(...)
        reference_image = image_path
        reference_content_type = scene_content_type  # ✅ Save type
    else:
        # Smart reference logic
        if self._should_use_reference(reference_content_type, scene_content_type):
            use_reference = reference_image  # ✅ Use reference
        else:
            use_reference = None  # ✅ NO reference
        
        image_path = self._generate_image(..., reference_image=use_reference)
```

### Step 2: Add Helper Method

**Add to `visual_production_agent.py`:**

```python
def _should_use_reference(self, reference_type: str, scene_type: str) -> bool:
    """
    Determine if reference image should be used for this scene.
    
    Args:
        reference_type: Content type of reference scene
        scene_type: Content type of current scene
    
    Returns:
        True if reference should be used, False otherwise
    """
    # Exact match
    if reference_type == scene_type:
        return True
    
    # Human types match (character consistency)
    human_types = ["human_portrait", "human_action"]
    if reference_type in human_types and scene_type in human_types:
        return True  # Same person
    
    # Product types DON'T match (variety needed)
    product_types = ["object", "product", "food", "nature"]
    if reference_type in product_types and scene_type in product_types:
        return False  # Different products
    
    # Default: No reference
    return False
```

---

## 📋 Test Cases

### Test 1: Character Story (Use Reference)

```python
scenes = [
    {"number": 1, "content_type": "human_portrait", "desc": "woman in garden"},
    {"number": 2, "content_type": "human_action", "desc": "woman drinking"},
    {"number": 3, "content_type": "human_portrait", "desc": "woman smiling"},
]

# Expected:
# Scene 1: Generate → reference
# Scene 2: Use reference ✅ (human_action matches human_portrait)
# Scene 3: Use reference ✅ (human_portrait matches)
```

### Test 2: Product Story (NO Reference)

```python
scenes = [
    {"number": 1, "content_type": "nature", "desc": "coffee tree"},
    {"number": 2, "content_type": "product", "desc": "fresh coffee"},
    {"number": 3, "content_type": "object", "desc": "grinder"},
]

# Expected:
# Scene 1: Generate → reference
# Scene 2: NO reference ✅ (product != nature)
# Scene 3: NO reference ✅ (object != nature)
```

### Test 3: Mixed Story (Smart Reference)

```python
scenes = [
    {"number": 1, "content_type": "human_portrait", "desc": "woman waking"},
    {"number": 2, "content_type": "human_action", "desc": "woman stretching"},
    {"number": 3, "content_type": "product", "desc": "coffee beans"},
    {"number": 4, "content_type": "human_action", "desc": "woman drinking"},
]

# Expected:
# Scene 1: Generate → reference (human_portrait)
# Scene 2: Use reference ✅ (human_action matches human_portrait)
# Scene 3: NO reference ✅ (product != human_portrait)
# Scene 4: Use reference ✅ (human_action matches human_portrait)
```

---

## 🎨 HYBRID Style vs PIKA Style

### PIKA Style (Current v2.9.0):

**Use case:** Character stories ONLY

```python
# All scenes have SAME character
scenes = [
    {"content_type": "human_portrait", ...},
    {"content_type": "human_action", ...},
    {"content_type": "human_portrait", ...},
]

# Behavior:
# - Scene 1 → reference
# - All scenes 2+ → use reference
# - Result: Same person ✅
```

### HYBRID Style (v3.0.0):

**Use case:** Mixed character + products

```python
# Mix of character and products
scenes = [
    {"content_type": "human_portrait", ...},  # Woman
    {"content_type": "human_action", ...},    # Woman action
    {"content_type": "product", ...},         # Coffee
    {"content_type": "human_action", ...},    # Woman again
]

# Behavior:
# - Scene 1 → reference (woman)
# - Scene 2 → use reference ✅ (same woman)
# - Scene 3 → NO reference ✅ (different product)
# - Scene 4 → use reference ✅ (same woman)
# - Result: Same woman + variety products ✅
```

---

## 🚀 Migration Path

### Phase 1: Fix PIKA Style (v2.9.2)

**Quick fix for your coffee example:**

```python
# Add smart reference logic to PIKA workflow
# Use reference ONLY for matching content types
```

**Impact:**
- ✅ Coffee products look correct
- ✅ Character stories still work
- ✅ Backward compatible

### Phase 2: Add HYBRID Style (v3.0.0)

**Full HYBRID implementation:**

```python
# Add scene detection
# Add smart transitions (morph vs cut)
# Add scene grouping
```

**Impact:**
- ✅ Auto scene detection
- ✅ Smart reference logic
- ✅ Mixed content types
- ✅ Professional output

---

## 📊 Comparison Table

| Feature | PIKA (v2.9.0) | PIKA (v2.9.2) | HYBRID (v3.0.0) |
|---------|---------------|---------------|-----------------|
| **Character Consistency** | ✅ Always | ✅ Smart | ✅ Smart |
| **Product Variety** | ❌ Broken | ✅ Fixed | ✅ Perfect |
| **Reference Logic** | ❌ Always use | ✅ Content-aware | ✅ Content-aware |
| **Scene Detection** | ❌ No | ❌ No | ✅ Auto |
| **Transitions** | ✅ All morph | ✅ All morph | ✅ Smart mix |
| **Use Case** | Character only | Character + Products | Everything |

---

## 🎯 Recommendation

### For Your Coffee Example:

**Immediate (v2.9.2):**

```bash
# Fix PIKA style with smart reference logic
python main.py --topic "life of coffee" --style pika
```

**Expected result:**
- ✅ Scene 1: Coffee on tree (unique)
- ✅ Scene 2: Fresh coffee (unique, NO reference)
- ✅ Scene 3: Grinder (unique, NO reference)
- ✅ All scenes look DIFFERENT (correct!)

**Future (v3.0.0):**

```bash
# Use HYBRID style for mixed content
python main.py --topic "life of coffee" --style hybrid
```

**Expected result:**
- ✅ Character scenes: Same person
- ✅ Product scenes: Variety
- ✅ Auto scene detection
- ✅ Smart transitions

---

## 📝 Summary

### Problem:

> **PIKA style používa Scene 1 ako reference pre VŠETKY scény, čo kazí product variety!**

### Solution:

> **Smart reference logic: Use reference ONLY for matching content types!**

### Implementation:

```python
# v2.9.2: Quick fix
if reference_content_type == scene_content_type:
    use_reference = reference_image  # ✅
else:
    use_reference = None  # ✅

# v3.0.0: Full HYBRID
+ Auto scene detection
+ Smart transitions
+ Scene grouping
```

---

**Your coffee example will work perfectly with v2.9.2!** ☕🎬
