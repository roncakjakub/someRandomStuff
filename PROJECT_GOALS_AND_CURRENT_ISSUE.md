# 🎯 Project Goals & Current Issue

## What We're Trying to Achieve:

### **Social Video Agent** - AI-Powered Vertical Video Creation

**Goal:** Generate viral-style vertical videos (15-60s) for Instagram/TikTok automatically.

**Workflow:**
1. **Research Agent** → Analyzes trends
2. **Creative Strategist** → Generates script + visual prompts
3. **Visual Production Agent** → Creates images
4. **Voiceover Agent** → Generates narration
5. **Assembly Agent** → Combines into final video

---

## 🎨 PIKA Style (What We're Testing):

**Concept:**
- Generate **multiple images** for each scene
- Use **character consistency** (same person across all shots)
- Create **morph transitions** between images (smooth video)
- Final: Professional vertical video with smooth animations

**Tools:**
1. **Midjourney** → First image (opening frame, establishes character)
2. **Instant Character** → Rest of images (same character, different poses)
3. **Veo 3.1 FLF2V** → Morph videos (image A → image B smooth transition)
4. **ElevenLabs** → Voiceover
5. **FFMPEG** → Assembly

---

## 📊 Example: "Life of Coffee" (9 scenes)

**Scene 1:** Woman waking up (Midjourney) → **Reference image**
**Scene 2:** Woman reaching for coffee (Instant Character, ref: Scene 1)
**Scene 3:** Hand holding coffee beans (Instant Character, ref: Scene 1)
**Scene 4:** Woman in kitchen (Instant Character, ref: Scene 1)
...

**Result:** Same woman across all scenes! ✅

---

## ❌ Current Issue:

### Error:
```
Could not load image from url: output/20251107_184147_life_of_coffee/midjourney_20251107_184405_a4256956.png
```

### Problem:
**Line 7:**
```
Reference: output/20251107_184147_life_of_coffee/midjourney_20251107_184405_a4256956.png
```

**This is a LOCAL FILE PATH!**

**But fal.ai API expects a PUBLIC URL!**

```python
# Agent sends:
reference_image_url = "output/20251107_184147_life_of_coffee/midjourney_20251107_184405_a4256956.png"  # ❌ Local path!

# fal.ai tries to download:
GET https://output/20251107_184147_life_of_coffee/midjourney_20251107_184405_a4256956.png  # ❌ Invalid URL!
```

---

## 🔍 Root Cause:

**InstantCharacterTool.execute()** expects `reference_image_url` to be a **publicly accessible URL**, not a local file path!

**From fal.ai docs:**
```python
reference_image_url: str  # URL to a publicly accessible image
```

**Examples of valid URLs:**
- `https://example.com/image.png` ✅
- `https://storage.googleapis.com/bucket/image.png` ✅
- `output/local/image.png` ❌ NOT A URL!

---

## 💡 Solutions:

### Option A: Upload to S3/Cloud Storage
```python
# 1. Generate image with Midjourney
image_path = "output/.../midjourney_xxx.png"

# 2. Upload to S3
public_url = upload_to_s3(image_path)
# → "https://s3.amazonaws.com/bucket/midjourney_xxx.png"

# 3. Pass public URL to InstantCharacter
tool.execute(reference_image_url=public_url)  # ✅
```

### Option B: Use fal.ai File Upload API
```python
# 1. Generate image with Midjourney
image_path = "output/.../midjourney_xxx.png"

# 2. Upload to fal.ai storage
from fal_client import upload_file
public_url = upload_file(image_path)
# → "https://fal.media/files/xxx/midjourney_xxx.png"

# 3. Pass public URL to InstantCharacter
tool.execute(reference_image_url=public_url)  # ✅
```

### Option C: Use Base64 Data URL (if supported)
```python
# 1. Generate image with Midjourney
image_path = "output/.../midjourney_xxx.png"

# 2. Convert to base64
import base64
with open(image_path, "rb") as f:
    data = base64.b64encode(f.read()).decode()
data_url = f"data:image/png;base64,{data}"

# 3. Pass data URL to InstantCharacter
tool.execute(reference_image_url=data_url)  # ✅ (if supported)
```

---

## 🎯 Recommended Solution:

**Option B: fal.ai File Upload API**

**Why:**
- ✅ Built-in to fal_client
- ✅ No S3 setup needed
- ✅ Fast and reliable
- ✅ Temporary storage (auto-cleanup)

**Implementation:**
```python
# In InstantCharacterTool.execute():
if reference_image_url and os.path.exists(reference_image_url):
    # It's a local file, upload it
    from fal_client import upload_file
    reference_image_url = upload_file(reference_image_url)
    logger.info(f"Uploaded reference image: {reference_image_url}")
```

---

## 📝 Summary:

**What we want:**
- PIKA style videos with character consistency
- Same person across all scenes
- Smooth morph transitions

**What's broken:**
- Reference image is local path, not URL
- fal.ai can't download local files
- InstantCharacter fails

**Fix:**
- Upload reference image to fal.ai storage
- Get public URL
- Pass URL to InstantCharacter
- ✅ Character consistency works!

---

## 🚀 Next Step:

Fix `InstantCharacterTool.execute()` to:
1. Check if `reference_image_url` is a local file
2. If yes, upload to fal.ai storage
3. Use the returned public URL
4. ✅ Done!
