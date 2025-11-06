# Changelog

All notable changes to this project will be documented in this file.

## [2.1.4] - 2025-01-06

### 🐛 Critical Bug Fix

#### Fixed
- **Voice ID None Error** in `voiceover_agent.py`
  - Issue: Agent was passing `voice_id=None` explicitly, overriding default value
  - Error: "Input should be a valid string [input_value=None]"
  - Fix: Only include voice_id in input_data if explicitly provided (not None)
  - Impact: Tool now correctly uses default voice_id from settings
  - Location: Line 55-67 in `agents/voiceover_agent.py`

---

## [2.1.3] - 2025-01-06

### 🐛 Critical Bug Fix

#### Fixed
- **ElevenLabs Voice Object Error** in `elevenlabs_voice.py`
  - Issue: ElevenLabs API requires `Voice` object, not string
  - Error: "AssertionError: assert isinstance(voice, Voice)"
  - Fix: Create `Voice` object from voice_id before passing to `generate()`
  - Impact: Voiceover generation now works correctly
  - Location: Line 79-85 in `tools/elevenlabs_voice.py`

---

## [2.1.2] - 2025-01-06

### 🐛 Bug Fix

#### Fixed
- **ElevenLabs API Error** in `elevenlabs_voice.py`
  - Issue: `voice_settings` parameter no longer accepted by ElevenLabs API
  - Error: "generate() got an unexpected keyword argument 'voice_settings'"
  - Fix: Removed `voice_settings` parameter from `generate()` call
  - Note: Voice settings are now configured per voice in ElevenLabs dashboard
  - Location: Line 76-82 in `tools/elevenlabs_voice.py`

---

## [2.1.1] - 2025-01-06

### 🐛 Critical Bug Fix

#### Fixed
- **Empty Prompt Error** in `visual_production_agent.py`
  - Issue: Agent was looking for `opening_frame_prompt` and `scene_prompts` fields that don't exist
  - Root cause: Data structure mismatch between creative strategist output and visual agent expectations
  - Fix: Agent now correctly extracts prompts from `scenes` array
  - Impact: Workflow now completes successfully from start to finish
  - Location: Lines 60-105 in `agents/visual_production_agent.py`

#### Improved
- Better error handling for empty scenes and prompts
- Enhanced logging to show tool for each scene
- Cleaner code structure with single loop instead of multiple
- First generated image automatically becomes opening frame

### 📊 Technical Details

**Before (Broken):**
```python
prompts.get("opening_frame_prompt", "")  # ❌ Doesn't exist
prompts.get("scene_prompts", [])          # ❌ Doesn't exist
```

**After (Fixed):**
```python
scenes = prompts.get("scenes", [])  # ✅ Correct structure
for scene in scenes:
    prompt = scene.get("prompt", "")  # ✅ Extracts correctly
```

---

## [2.1.0] - 2025-01-06

### 🎉 Major Feature: AI-Powered Workflow Router

#### Added
- **AI-Powered Workflow Router** (`workflow_router.py`)
  - Intelligent tool selection based on request analysis
  - Cost optimization (50-90% savings on simple videos)
  - Speed optimization (skip slow unnecessary tools)
  - Smart presets: budget, standard, premium, viral
  - Constraint support: max cost and max time
  - GPT-4 powered decision making

- **New CLI Flags**
  - `--use-router`: Enable AI-powered workflow router
  - `--preset`: Quick presets (budget/standard/premium/viral)
  - `--max-cost`: Maximum budget constraint in USD
  - `--max-time`: Maximum time constraint in seconds

- **Documentation**
  - `ROUTER_GUIDE.md`: Comprehensive guide to AI Router
  - Updated `README.md` with router usage examples
  - Updated CLI help text with router examples

#### Changed
- `main.py`: Integrated router with workflow initialization
- `workflow.py`: Added `workflow_plan` parameter support
- `visual_production_agent.py`: Added router-aware tool selection
- CLI examples updated to showcase router capabilities

#### Technical Details
- Router uses GPT-4 for intelligent analysis
- Tool specifications include cost, speed, and use cases
- Automatic fallback to fixed workflow if router fails
- Plan validation and constraint enforcement
- Detailed reasoning provided for all decisions

### 🐛 Bug Fixes

#### Fixed
- **F-string Format Error** in `creative_strategist.py`
  - Issue: JSON template inside f-string had unescaped curly braces
  - Fix: Escaped all curly braces with `{{` and `}}`
  - Location: Line 172-191 in `_build_viral_context` method

### 📊 Cost Comparison

**Without Router (Fixed Workflow):**
- Every video: $0.98
- Time: 8-10 minutes

**With Router:**
- Budget preset: $0.07 (91% savings)
- Standard preset: $0.20-0.40 (60-80% savings)
- Premium preset: $0.80-0.98 (comparable quality)

### 🎯 Use Cases

1. **Content Creators**: Use budget preset for daily content ($0.07/video)
2. **Marketing Agencies**: Use premium preset for campaigns ($0.98/video)
3. **News Organizations**: Use time constraints for fast turnaround (60s)
4. **E-commerce**: Use standard preset for product showcases ($0.20/video)

---

## [2.0.3] - 2025-01-05

### Fixed
- Replicate API parameters for Flux models
- Import errors for standalone tool execution
- Apiframe endpoint URLs and response parsing
- Ideogram aspect ratio format (9x16 vs 9:16)
- Inference steps for different Flux variants

### Changed
- Updated package dependencies to resolve version conflicts
  - langchain-core: 0.3.27
  - langchain-community: 0.3.27

---

## [2.0.2] - 2025-01-04

### Added
- Apiframe integration for Midjourney, Seedream 4, Ideogram
- Character consistency tool (Seedream 4)
- Text overlay tool (Ideogram)

### Fixed
- Apiframe API endpoint corrections
- Response structure parsing for Apiframe tools
- Status checking (finished vs completed)

---

## [2.0.1] - 2025-01-03

### Added
- Multiple Flux variants support (schnell/dev/pro)
- Quality level configuration via CLI
- Run-specific output directories

### Fixed
- Replicate model version format
- Flux inference steps configuration

---

## [2.0.0] - 2025-01-02

### Added
- Multi-agent architecture with LangGraph
- 5 specialized agents:
  - Research Agent (Tavily Search)
  - Creative Strategist (GPT-4)
  - Visual Production Agent (Flux)
  - Voiceover Agent (ElevenLabs)
  - Assembly Agent (FFMPEG)
- Workflow orchestration with error handling
- Comprehensive logging system
- CLI interface with argument parsing

### Changed
- Complete system rewrite from scratch
- Modular tool architecture
- Production-ready error handling
- Configuration management system

---

## [1.0.0] - 2024-12-30

### Added
- Initial prototype
- Basic image generation
- Basic voiceover
- Simple video assembly

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
