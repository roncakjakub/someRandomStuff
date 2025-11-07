# Import Fixes for visual_production_agent.py v3.2.1

## ❌ Current Broken Imports:

```python
from tools.midjourney import MidjourneyTool  # ❌ File doesn't exist
from tools.flux_dev import FluxDevTool  # ❌ Wrong path
from tools.flux_pro import FluxProTool  # ❌ Wrong path
from tools.pika_v2 import PikaV2Tool  # ❌ Wrong name
```

---

## ✅ Correct Imports (Based on GitHub Repo):

```python
# Image Generation Tools
from tools.apiframe_midjourney import MidjourneyTool  # ✅ Correct
from tools.replicate_image import FluxDevTool, FluxProTool, FluxSchnellTool  # ✅ All in one file!
from tools.instant_character import InstantCharacterTool  # ✅ Correct
from tools.flux_kontext_pro import FluxKontextProTool  # ✅ Correct
from tools.seedream4 import Seedream4Tool  # ✅ Correct (if needed)
from tools.ideogram_text import IdeogramTool  # ✅ Correct (if needed)

# Video Generation Tools
from tools.veo31_flf2v import Veo31FLF2VTool  # ✅ Correct
from tools.wan_flf2v import WanFLF2VTool  # ✅ Correct
from tools.pika_video import PikaVideoTool  # ✅ Correct (not pika_v2!)
from tools.luma_video import LumaVideoTool  # ✅ Correct (if needed)
from tools.minimax_video import MinimaxVideoTool  # ✅ Correct (if needed)
from tools.runway_video import RunwayVideoTool  # ✅ Correct (if needed)

# Other Tools
from tools.elevenlabs_voice import ElevenLabsVoice  # ✅ Correct
from tools.video_assembly import VideoAssemblyTool  # ✅ Correct
```

---

## 🔧 Fixed visual_production_agent.py Header:

```python
"""
Visual Production Agent - Generates images and videos for social media content.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime
import uuid

# Image Generation Tools
from tools.apiframe_midjourney import MidjourneyTool  # ✅ FIXED!
from tools.replicate_image import FluxDevTool, FluxProTool  # ✅ FIXED!
from tools.instant_character import InstantCharacterTool  # ✅ Already correct
from tools.flux_kontext_pro import FluxKontextProTool  # ✅ Already correct

# Video Generation Tools  
from tools.veo31_flf2v import Veo31FLF2VTool  # ✅ Already correct
from tools.wan_flf2v import WanFLF2VTool  # ✅ Already correct
from tools.pika_video import PikaVideoTool  # ✅ FIXED! (was pika_v2)

# Other Tools
from tools.video_assembly import VideoAssemblyTool
from config.settings import OUTPUT_DIR


class VisualProductionAgent:
    """Agent for generating visual content (images and videos)."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(OUTPUT_DIR)
        
        # Image generation tools dictionary
        self.image_tools = {
            "midjourney": MidjourneyTool(),  # ✅ Now works!
            "flux_dev": FluxDevTool(),  # ✅ Now works!
            "flux_pro": FluxProTool(),  # ✅ Now works!
            "instant_character": InstantCharacterTool(),
            "flux_kontext_pro": FluxKontextProTool(),
        }
        
        # Video generation tools dictionary
        self.video_tools = {
            "veo31_flf2v": Veo31FLF2VTool(),
            "wan_flf2v": WanFLF2VTool(),
            "pika_video": PikaVideoTool(),  # ✅ Fixed name!
        }
        
        # Default tools
        self.default_image_tool = "flux_dev"
        self.default_video_tool = "veo31_flf2v"
        
        self.logger.info("✅ Visual Production Agent initialized with all tools!")
```

---

## 📝 Summary of Changes:

| Old Import | New Import | Status |
|------------|------------|--------|
| `tools.midjourney` | `tools.apiframe_midjourney` | ✅ FIXED |
| `tools.flux_dev` | `tools.replicate_image` | ✅ FIXED |
| `tools.flux_pro` | `tools.replicate_image` | ✅ FIXED |
| `tools.pika_v2` | `tools.pika_video` | ✅ FIXED |
| `tools.instant_character` | (same) | ✅ OK |
| `tools.flux_kontext_pro` | (same) | ✅ OK |
| `tools.veo31_flf2v` | (same) | ✅ OK |
| `tools.wan_flf2v` | (same) | ✅ OK |

---

## 🎯 Next Step:

Apply these fixes to `agents/visual_production_agent.py` and the import error will be resolved!
