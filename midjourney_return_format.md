# Midjourney Tool Return Format

## Source:
https://github.com/roncakjakub/someRandomStuff/blob/master/tools/apiframe_midjourney.py

## Return Format (lines 90-95):

```python
return {
    "success": True,
    "image_path": image_path,
    "prompt": prompt,
    "model": "midjourney"
}
```

## Key Finding:

**Midjourney returns `"image_path"` (singular), NOT `"images"` (plural)!**

This is different from other tools like Flux which return:
```python
return {
    "images": [image_path1, image_path2, ...],  # List of images
    ...
}
```

## Problem in visual_production_agent.py:

The agent's `_generate_image()` method expects ALL tools to return `"images"` key:

```python
def _generate_image(...):
    result = tool.execute(...)
    
    # This fails for Midjourney!
    if not result.get("images"):  # ❌ Midjourney has "image_path", not "images"!
        raise Exception(f"Tool '{tool_name}' returned no images")
```

## Solution:

Need to handle both formats:
- `"images"` (list) - Flux, Replicate tools
- `"image_path"` (string) - Midjourney, Apiframe tools

```python
def _generate_image(...):
    result = tool.execute(...)
    
    # Handle both formats
    if "images" in result:
        image_paths = result["images"]
    elif "image_path" in result:
        image_paths = [result["image_path"]]  # Convert to list
    else:
        raise Exception(f"Tool '{tool_name}' returned no images")
```
