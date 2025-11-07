# Instant Character Tool Analysis

## Current Implementation (v3.1.0):

### execute() Method Signature:
```python
def execute(
    self,
    prompt: str,
    reference_image_url: Optional[str] = None,  # ⚠️ EXPECTS URL!
    image_size: str = "landscape_16_9",
    scale: float = 1.0,
    negative_prompt: str = "",
    guidance_scale: float = 3.5,
    num_inference_steps: int = 28,
    seed: Optional[int] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
```

### Key Observations:

**Line 394-397:**
```python
# Add reference image if provided
if reference_image_url:
    request_data["image_url"] = reference_image_url  # ⚠️ Passed directly to fal.ai!
    print(f"🎨 Generating with character reference...")
    print(f"   Reference: {reference_image_url}")
```

**❌ PROBLEM:**
- `reference_image_url` is passed DIRECTLY to fal.ai API
- No validation if it's a URL vs local path
- No file upload handling
- fal.ai expects a publicly accessible URL!

**Line 409-413:**
```python
# Call fal.ai API
try:
    result = fal_client.subscribe(
        self.model_id,
        arguments=request_data  # Contains "image_url": reference_image_url
    )
```

**Line 430-435:**
```python
# Download image if output path specified
if output_path:
    import requests
    response = requests.get(image_url)  # ✅ Downloads RESULT image
    with open(output_path, 'wb') as f:
        f.write(response.content)
```

**✅ GOOD:** Tool knows how to download images from URLs
**❌ BAD:** Tool doesn't know how to upload local files to URLs

---

## The Issue:

### What visual_production_agent.py does:
```python
# Scene 1: Generate with Midjourney
result = midjourney_tool.execute(prompt="woman waking up")
# Returns: {"image_path": "output/.../midjourney_xxx.png"}

# Scene 2: Generate with InstantCharacter
reference_path = "output/.../midjourney_xxx.png"  # ❌ LOCAL PATH!
result = instant_character_tool.execute(
    prompt="woman reaching for coffee",
    reference_image_url=reference_path  # ❌ SHOULD BE URL!
)
```

### What happens:
```python
# InstantCharacter passes to fal.ai:
request_data = {
    "image_url": "output/.../midjourney_xxx.png"  # ❌ NOT A URL!
}

# fal.ai tries to download:
GET https://output/.../midjourney_xxx.png  # ❌ FAILS!
# Error: "Could not load image from url: output/.../midjourney_xxx.png"
```

---

## Solution: Add File Upload Support

### Option 1: Upload in InstantCharacterTool.execute()
```python
def execute(self, prompt: str, reference_image_url: Optional[str] = None, ...):
    # ... existing code ...
    
    # Add reference image if provided
    if reference_image_url:
        # Check if it's a local file
        if os.path.exists(reference_image_url):
            print(f"📤 Uploading local reference image...")
            from fal_client import upload_file
            reference_image_url = upload_file(reference_image_url)
            print(f"✅ Uploaded: {reference_image_url}")
        
        request_data["image_url"] = reference_image_url
        print(f"🎨 Generating with character reference...")
        print(f"   Reference: {reference_image_url}")
```

**Pros:**
- ✅ Transparent to caller
- ✅ Works with both URLs and local paths
- ✅ Minimal code changes

**Cons:**
- ⚠️ Uploads same file multiple times if used in multiple scenes
- ⚠️ No caching

### Option 2: Upload in visual_production_agent.py
```python
# In visual_production_agent.py:
def _generate_image(self, scene_data, reference_image_path=None):
    # ... existing code ...
    
    # Upload reference image if it's a local file
    if reference_image_path and os.path.exists(reference_image_path):
        from fal_client import upload_file
        reference_image_url = upload_file(reference_image_path)
        print(f"📤 Uploaded reference: {reference_image_url}")
    else:
        reference_image_url = reference_image_path
    
    # Use InstantCharacter
    result = tool.execute(
        prompt=prompt,
        reference_image_url=reference_image_url  # ✅ NOW IT'S A URL!
    )
```

**Pros:**
- ✅ Can cache uploaded URLs
- ✅ Upload once, use multiple times
- ✅ More control

**Cons:**
- ⚠️ Agent needs to know about upload logic
- ⚠️ More complex

---

## Recommended: Option 1 (Upload in Tool)

**Why:**
- Follows "tool should handle its own requirements" principle
- Transparent to agent
- Simpler to implement
- Works with any caller

**Implementation:**
```python
# In tools/instant_character.py:

def execute(
    self,
    prompt: str,
    reference_image_url: Optional[str] = None,
    image_size: str = "landscape_16_9",
    scale: float = 1.0,
    negative_prompt: str = "",
    guidance_scale: float = 3.5,
    num_inference_steps: int = 28,
    seed: Optional[int] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate image with consistent character.
    
    Args:
        reference_image_url: Optional reference image for character consistency
                            Can be either:
                            - Public URL (e.g., "https://example.com/image.png")
                            - Local file path (will be uploaded automatically)
    """
    
    # Validate inputs
    if not prompt:
        raise ValueError("Prompt is required")
    
    # Prepare request
    request_data = {
        "prompt": prompt,
        "image_size": image_size,
        "scale": scale,
        "negative_prompt": negative_prompt,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
        "enable_safety_checker": True,
        "output_format": "jpeg"
    }
    
    # Add reference image if provided
    if reference_image_url:
        # Check if it's a local file path
        if os.path.exists(reference_image_url):
            print(f"📤 Uploading local reference image...")
            print(f"   Local path: {reference_image_url}")
            
            # Upload to fal.ai storage
            from fal_client import upload_file
            uploaded_url = upload_file(reference_image_url)
            
            print(f"✅ Uploaded to: {uploaded_url}")
            reference_image_url = uploaded_url
        
        request_data["image_url"] = reference_image_url
        print(f"🎨 Generating with character reference...")
        print(f"   Reference URL: {reference_image_url}")
    else:
        print(f"🎨 Generating new character...")
    
    # ... rest of the method ...
```

**Changes:**
1. Add `os.path.exists()` check
2. Import `upload_file` from `fal_client`
3. Upload local files and get public URL
4. Use the uploaded URL in API request
5. Update docstring to mention both URL and local path support

**Result:**
- ✅ Works with URLs: `reference_image_url="https://example.com/image.png"`
- ✅ Works with local paths: `reference_image_url="output/.../midjourney_xxx.png"`
- ✅ No changes needed in visual_production_agent.py
- ✅ Transparent to all callers
