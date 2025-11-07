# Tool Interface Analysis

## Source:
https://github.com/roncakjakub/someRandomStuff/blob/master/tools/instant_character.py

## InstantCharacterTool Interface:

**Line 26:** `def execute(`

**Method signature:**
```python
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
    
    Returns:
        Dict with image URL, cost, and metadata
    """
```

## Problem:

**Agent calls:** `tool.run(tool_input)`  
**Tool has:** `tool.execute(prompt, ...)`

**❌ Mismatch!**

## Solution Options:

### Option 1: Add run() wrapper to tools
```python
class InstantCharacterTool:
    def execute(...):
        # existing code
        
    def run(self, input_data: Dict) -> Dict:
        """Wrapper for compatibility"""
        return self.execute(**input_data)
```

### Option 2: Change agent to call execute()
```python
# In visual_production_agent.py:
result = tool.execute(tool_input)  # Instead of tool.run()
```

### Option 3: Use BaseTool interface
Check if there's a BaseTool class that defines standard interface.

## Recommendation:

**Option 2** is cleanest - agent should call `execute()` which is the standard method name in all tools.

Need to check:
- ApiframeMidjourneyTool - has `execute()`? ✅ (line 51 in apiframe_midjourney.py)
- FluxDevTool - has `execute()`? (need to check)
- All other tools - consistent interface?
