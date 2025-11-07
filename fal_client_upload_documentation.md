# fal_client File Upload Documentation

## Source:
https://docs.fal.ai/model-apis/client#3-file-uploads

## Python Example:

```python
url = fal_client.upload_file("path/to/file")
```

**That's it!** ✅

## Usage:

```python
import fal_client

# Upload a local file
local_path = "output/20251107_184147_life_of_coffee/midjourney_20251107_184405_a4256956.png"
public_url = fal_client.upload_file(local_path)

# Returns: "https://fal.media/files/xxx/midjourney_20251107_184405_a4256956.png"

# Use the public URL in API requests
result = fal_client.subscribe(
    "fal-ai/instant-character",
    arguments={
        "prompt": "woman reaching for coffee",
        "image_url": public_url  # ✅ Public URL!
    }
)
```

## Key Points:

1. **Simple API:** Just `fal_client.upload_file(path)`
2. **Returns URL:** Returns a publicly accessible URL
3. **Temporary Storage:** Files are stored temporarily on fal.ai CDN
4. **Auto-cleanup:** Files are cleaned up after some time
5. **No S3 needed:** Built-in to fal_client

## Implementation in InstantCharacterTool:

```python
def execute(
    self,
    prompt: str,
    reference_image_url: Optional[str] = None,
    ...
) -> Dict[str, Any]:
    
    # Add reference image if provided
    if reference_image_url:
        # Check if it's a local file path
        if os.path.exists(reference_image_url):
            print(f"📤 Uploading local reference image...")
            print(f"   Local path: {reference_image_url}")
            
            # Upload to fal.ai storage
            import fal_client
            uploaded_url = fal_client.upload_file(reference_image_url)
            
            print(f"✅ Uploaded to: {uploaded_url}")
            reference_image_url = uploaded_url
        
        request_data["image_url"] = reference_image_url
        print(f"🎨 Generating with character reference...")
        print(f"   Reference URL: {reference_image_url}")
```

**Result:**
- ✅ Works with local paths: `reference_image_url="output/.../midjourney_xxx.png"`
- ✅ Works with URLs: `reference_image_url="https://example.com/image.png"`
- ✅ Transparent to caller
- ✅ No changes needed in visual_production_agent.py
