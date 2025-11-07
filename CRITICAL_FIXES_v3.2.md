# CRITICAL FIXES v3.2

## 🚨 Problems Found

### 1. Router Disabled by Default
- User ran with `--style pika` but router was OFF
- PIKA style REQUIRES router for tool selection
- **Fix:** Auto-enable router for PIKA/HYBRID styles

### 2. Visual Production Agent Ignores Router
- Agent uses single `self.image_tool` for ALL scenes
- Router tool selection (`scene.get("tool")`) is completely ignored
- **Fix:** Rewrite `generate_visuals()` to use dynamic tool selection

### 3. Tools Not in Dictionary
- `instant_character` imported but not in `self.image_tools`
- `veo31_flf2v` imported but not in `self.video_tools`
- **Fix:** Add all tools to proper dictionaries

### 4. PIKA/HYBRID Workflows Not Called
- `_generate_pika_style()` exists but never called
- `_generate_hybrid_style()` missing entirely
- **Fix:** Add style routing in `generate_visuals()`

---

## 🔧 Implementation Plan

### Fix #1: Auto-Enable Router (main.py)

**Location:** `main.py` line ~304

**Change:**
```python
# OLD:
if args.use_router:
    logger.info("\n🤖 AI-Powered Router ENABLED")

# NEW:
# Auto-enable router for styles that require it
use_router = args.use_router or (args.style in ["pika", "hybrid"])

if use_router:
    logger.info("\n🤖 AI-Powered Router ENABLED")
    if args.style in ["pika", "hybrid"]:
        logger.info(f"  (Auto-enabled for {args.style} style)")
```

---

### Fix #2: Rewrite Visual Production Agent

**This is the BIG one - complete rewrite needed!**

#### Step 2.1: Update __init__ to Create Tool Dictionaries

```python
def __init__(self, quality: str = "dev", workflow_plan = None):
    self.name = "Visual Production Agent"
    self.logger = logging.getLogger(f"agents.{self.name}")
    self.workflow_plan = workflow_plan
    self.quality = quality
    
    # Image generation tools
    self.image_tools = {
        "flux_schnell": FluxSchnellTool(),
        "flux_dev": FluxDevTool(),
        "flux_pro": FluxProTool(),
        "midjourney": MidjourneyTool(),
        "instant_character": InstantCharacterTool(),
        "flux_kontext_pro": FluxKontextProTool(),
    }
    
    # Video generation tools
    self.video_tools = {
        "veo31_flf2v": Veo31FLF2VTool(),
        "wan_flf2v": WanFLF2VTool(),
        "pika_v2": PikaV2Tool(),
        # ... other video tools
    }
    
    # Default tool based on quality
    if quality == "pro":
        self.default_image_tool = "flux_pro"
    elif quality == "dev":
        self.default_image_tool = "flux_dev"
    else:
        self.default_image_tool = "flux_schnell"
```

#### Step 2.2: Rewrite generate_visuals() for Dynamic Tool Selection

```python
def generate_visuals(self, prompts: Dict[str, Any], output_dir: str = None) -> Dict[str, Any]:
    """Generate visuals using Router-selected tools."""
    
    scenes = prompts.get("scenes", [])
    self.logger.info(f"Generating {len(scenes)} scenes...")
    
    all_images = []
    
    for idx, scene in enumerate(scenes):
        scene_number = scene.get("number", idx + 1)
        scene_prompt = scene.get("prompt", "")
        
        # GET TOOL FROM ROUTER (this was missing!)
        scene_tool = scene.get("tool", self.default_image_tool)
        
        self.logger.info(f"Scene {scene_number}: Using tool '{scene_tool}'")
        
        # SELECT TOOL FROM DICTIONARY (this was missing!)
        if scene_tool in self.image_tools:
            tool = self.image_tools[scene_tool]
        else:
            self.logger.warning(f"Tool '{scene_tool}' not found, using default")
            tool = self.image_tools[self.default_image_tool]
        
        # GENERATE IMAGE
        result = tool.run({
            "prompt": scene_prompt,
            "aspect_ratio": "9:16",
            "num_outputs": 1,
            "output_dir": output_dir,
        })
        
        image_path = result.get("image_paths", [])[0]
        all_images.append(image_path)
    
    return {
        "all_images": all_images,
        "scene_images": all_images,
        "total_images": len(all_images)
    }
```

---

### Fix #3: Add Style-Specific Workflows

**Location:** After `generate_visuals()` method

```python
def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point - routes to style-specific workflow."""
    
    prompts = state.get("prompts", {})
    output_dir = state.get("run_output_dir")
    video_style = state.get("video_style", "cinematic")
    scene_plans = state.get("scene_plans", [])
    
    self.logger.info(f"Running {video_style} style workflow...")
    
    # Route to style-specific workflow
    if video_style == "pika":
        return self._generate_pika_style(
            scenes=prompts.get("scenes", []),
            scene_plans=scene_plans,
            output_dir=output_dir
        )
    elif video_style == "hybrid":
        return self._generate_hybrid_style(
            scenes=prompts.get("scenes", []),
            scene_plans=scene_plans,
            output_dir=output_dir
        )
    else:
        # Cinematic/viral style - just generate images
        return self.generate_visuals(prompts, output_dir)
```

---

### Fix #4: Pass workflow_plan to Visual Agent

**Location:** `workflow.py` line ~118

```python
# OLD:
self.visual_agent = VisualProductionAgent(quality=visual_quality)

# NEW:
self.visual_agent = VisualProductionAgent(
    quality=visual_quality,
    workflow_plan=None  # Will be set later after router runs
)
```

**Then in workflow run() method:**

```python
# After router runs:
if workflow_plan:
    self.visual_agent.workflow_plan = workflow_plan
    self.visual_agent.scene_plans = scene_plans
```

---

## 📊 Summary

| Fix | File | Lines | Priority |
|-----|------|-------|----------|
| Auto-enable router | main.py | ~304 | 🔴 CRITICAL |
| Tool dictionaries | visual_production_agent.py | ~18-48 | 🔴 CRITICAL |
| Dynamic tool selection | visual_production_agent.py | ~49-120 | 🔴 CRITICAL |
| Style routing | visual_production_agent.py | new method | 🔴 CRITICAL |
| Pass workflow_plan | workflow.py | ~118, ~200 | 🟡 IMPORTANT |

---

## 🎯 Testing Plan

After fixes:

```bash
python main.py --topic "life of coffee" --style pika --scenes 9
```

**Expected:**
1. ✅ Router auto-enabled
2. ✅ Scene 1: Midjourney
3. ✅ Scenes 2-9: Instant Character
4. ✅ Videos: Veo 3.1 FLF2V morphs
5. ✅ Final video: Smooth morph transitions

---

**All fixes are CRITICAL - without them, PIKA style cannot work!**
