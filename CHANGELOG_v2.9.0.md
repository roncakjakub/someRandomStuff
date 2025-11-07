# Changelog v2.9.0 - PIKA Character Consistency 👤

**Date:** 2025-11-07  
**Status:** Production Ready ✅

## 🎯 Major Feature: Character Consistency

### Problem:
Seedream4 generated DIFFERENT person than Midjourney Scene 1!

### Solution:
Seedream4 now uses Scene 1 image as reference → SAME person across all scenes! 👤

## 🔧 Changes:

1. Added `reference_image` parameter to `_generate_image()`
2. PIKA workflow passes Scene 1 image to Seedream4 for scenes 2+
3. Seedream4 uses `prompt_strength=0.8` (80% reference, 20% prompt)

## 📊 Result:

**Before (v2.8.8):**
- Scene 1: Woman A
- Scene 2: Woman B (different!)
- Scene 3: Woman C (different!)

**After (v2.9.0):**
- Scene 1: Woman A
- Scene 2: Woman A (same!)
- Scene 3: Woman A (same!)

**PIKA style now has TRUE character consistency!** 👤
