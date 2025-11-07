# InstantCharacterTool Parameters

## Source:
https://github.com/roncakjakub/someRandomStuff/blob/master/tools/instant_character.py

## execute() Method Signature (Line 26-29):

```python
def execute(
    self,
    prompt: str,  # ✅ STRING, not dict!
    reference_image_url: Optional[str] = None,  # ✅ reference_image_URL, not reference_image!
    image_size: str = "landscape_16_9",
    scale: float = 1.0,
    negative_prompt: str = "",
    guidance_scale: float = 3.5,
    num_inference_steps: int = 28,
    seed: Optional[int] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
```

## Agent Currently Sends (WRONG):

```python
tool_input = {
    "prompt": {...},  # ❌ DICT! Should be STRING!
    "reference_image": "...",  # ❌ Wrong param name! Should be "reference_image_url"!
    "aspect_ratio": "9:16",  # ❌ Wrong param name! Should be "image_size"!
    "num_outputs": 1,  # ❌ Not a valid parameter!
    "output_dir": "...",  # ❌ Wrong param name! Should be "output_path"!
}
```

## Tool Actually Expects:

```python
{
    "prompt": "string description",  # ✅ STRING
    "reference_image_url": "path/to/image.png",  # ✅ Correct param name
    "image_size": "landscape_16_9",  # ✅ Correct param name
    "output_path": "output/dir",  # ✅ Correct param name
    # No num_outputs parameter!
}
```

## Fix Required:

In `visual_production_agent.py` `_generate_image()` method:

1. Extract prompt STRING from tool_input dict
2. Rename "reference_image" → "reference_image_url"
3. Rename "aspect_ratio" → "image_size" (or map values)
4. Rename "output_dir" → "output_path"
5. Remove "num_outputs" parameter

## Alternative Solution:

Create a wrapper in InstantCharacterTool that accepts dict and extracts parameters:

```python
def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper to accept dict input"""
    prompt = input_data.get("prompt")
    if isinstance(prompt, dict):
        prompt = prompt.get("prompt", "")  # Extract string from dict
    
    return self._execute_internal(
        prompt=prompt,
        reference_image_url=input_data.get("reference_image") or input_data.get("reference_image_url"),
        image_size=input_data.get("aspect_ratio", "landscape_16_9"),
        output_path=input_data.get("output_dir") or input_data.get("output_path"),
        ...
    )
```
