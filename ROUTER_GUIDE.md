# AI-Powered Workflow Router Guide

## Overview

The **AI-Powered Workflow Router** intelligently decides which tools to use for your video based on:
- The topic and requirements
- Budget constraints
- Time constraints
- Quality expectations

This can **save 50-90% on costs** for simple videos while maintaining quality.

---

## How It Works

### Without Router (Default)
```bash
python main.py --topic "morning coffee"
```
**Always uses ALL tools:**
- Midjourney (opening frame)
- Seedream 4 (character consistency)
- Flux (multiple angles)
- Ideogram (text overlays)
- Luma (video animation)
- ElevenLabs (voiceover)

**Cost:** ~$0.98 per video  
**Time:** ~8-10 minutes

---

### With Router Enabled
```bash
python main.py --topic "morning coffee" --use-router
```
**AI analyzes and selects optimal tools:**
- Skips unnecessary expensive tools
- Uses cheaper alternatives when appropriate
- Maintains quality for the use case

**Cost:** $0.07 - $0.98 (depends on needs)  
**Time:** 1-10 minutes (depends on tools)

---

## Usage Examples

### 1. Budget Mode (Fast & Cheap)
```bash
python main.py --topic "quick tip" --use-router --preset budget
```
**What it does:**
- Uses Flux Schnell (fast, cheap)
- Skips Luma (uses Ken Burns effects instead)
- Skips optional tools (Midjourney, Seedream, Ideogram)
- Only essential: Flux + Ken Burns + Voice

**Cost:** ~$0.07  
**Time:** ~20 seconds  
**Best for:** High-volume content, testing, simple posts

---

### 2. Standard Mode (Balanced)
```bash
python main.py --topic "product showcase" --use-router --preset standard
```
**What it does:**
- Uses Flux Dev (good quality)
- Includes Luma if motion needed
- Includes text overlay if needed
- Skips Midjourney (uses Flux instead)

**Cost:** ~$0.25-0.40  
**Time:** ~2-3 minutes  
**Best for:** Most use cases, regular content

---

### 3. Premium Mode (Max Quality)
```bash
python main.py --topic "brand campaign" --use-router --preset premium
```
**What it does:**
- Uses Midjourney for cinematic opening
- Uses Luma for smooth motion
- Includes all relevant tools
- No compromises on quality

**Cost:** ~$0.80-0.98  
**Time:** ~8-10 minutes  
**Best for:** Important content, brand campaigns

---

### 4. Viral Mode (Optimized for Engagement)
```bash
python main.py --topic "trending topic" --use-router --preset viral
```
**What it does:**
- Ensures character consistency (Seedream 4)
- Includes text overlays (Ideogram)
- Uses video animation (Luma)
- Premium quality throughout

**Cost:** ~$1.00-1.50  
**Time:** ~10-12 minutes  
**Best for:** Content meant to go viral

---

## Advanced: Custom Constraints

### Cost Constraint
```bash
python main.py --topic "daily vlog" --use-router --max-cost 0.25
```
**AI will:**
- Select cheapest tools that meet requirements
- Replace expensive tools with alternatives
- Stay within $0.25 budget

---

### Time Constraint
```bash
python main.py --topic "breaking news" --use-router --max-time 60
```
**AI will:**
- Select fastest tools
- Skip slow tools (Midjourney, Luma)
- Deliver video in under 60 seconds

---

### Combined Constraints
```bash
python main.py --topic "quick post" --use-router --max-cost 0.15 --max-time 30
```
**AI will:**
- Optimize for BOTH cost and speed
- Use only essential fast/cheap tools
- Deliver in 30s for under $0.15

---

## Presets Comparison

| Preset | Cost | Time | Tools Used | Best For |
|--------|------|------|------------|----------|
| **budget** | $0.07 | 20s | Flux Schnell, Ken Burns, Voice | Testing, high-volume |
| **standard** | $0.25-0.40 | 2-3min | Flux Dev, Luma (if needed), Voice | Regular content |
| **premium** | $0.80-0.98 | 8-10min | Midjourney, Luma, all tools | Important content |
| **viral** | $1.00-1.50 | 10-12min | All premium tools + extras | Viral-optimized |

---

## Tool Selection Logic

The AI Router considers:

### 1. **Character Consistency**
- Detected: Person/character in topic
- Tool: Seedream 4 ($0.04, 30s)
- Example: "my morning routine" → Uses Seedream 4

### 2. **Text Overlays**
- Detected: Quotes, statistics, key words
- Tool: Ideogram ($0.02, 15s)
- Example: "motivational quote" → Uses Ideogram

### 3. **Motion Requirements**
- Premium: Luma ($0.10/clip, 2min)
- Budget: Ken Burns (free, instant)
- Example: Budget preset → Uses Ken Burns

### 4. **Opening Frame**
- Premium: Midjourney ($0.05, 5min)
- Standard: Flux Dev ($0.03, 30s)
- Budget: Flux Schnell ($0.02, 10s)

### 5. **Voiceover**
- Always: ElevenLabs ($0.05, 10s)
- Required for all videos

---

## Cost Savings Examples

### Example 1: Simple Quote Video
**Without Router:**
```
Midjourney: $0.05
Seedream 4: $0.04
Flux: $0.02
Ideogram: $0.02
Luma: $0.80
Voice: $0.05
Total: $0.98
```

**With Router (budget preset):**
```
Flux Schnell: $0.02
Ideogram: $0.02 (text needed)
Ken Burns: $0.00
Voice: $0.05
Total: $0.09
```
**Savings: 91%** 💰

---

### Example 2: Product Showcase
**Without Router:**
```
All tools: $0.98
```

**With Router (standard preset):**
```
Flux Dev: $0.03
Ideogram: $0.02 (specs text)
Luma: $0.10 (smooth motion)
Voice: $0.05
Total: $0.20
```
**Savings: 80%** 💰

---

### Example 3: Personal Vlog
**Without Router:**
```
All tools: $0.98
```

**With Router (standard preset):**
```
Flux Dev: $0.03
Seedream 4: $0.04 (character consistency)
Luma: $0.10
Voice: $0.05
Total: $0.22
```
**Savings: 78%** 💰

---

## When to Use Router vs Fixed Workflow

### Use Router When:
✅ You want to optimize costs  
✅ You have budget constraints  
✅ You need fast turnaround  
✅ You're producing high-volume content  
✅ You want smart tool selection  

### Use Fixed Workflow When:
✅ You want maximum quality always  
✅ You want predictable costs  
✅ You're producing premium content  
✅ You don't mind using all tools  

---

## Tips & Best Practices

### 1. Start with Router
Always try router first to see cost savings:
```bash
python main.py --topic "your topic" --use-router --preset standard
```

### 2. Use Presets
Presets are pre-configured for common scenarios:
- `budget` - Fast & cheap
- `standard` - Balanced (recommended)
- `premium` - Max quality
- `viral` - Engagement-optimized

### 3. Set Constraints
If you have hard limits, set them:
```bash
--max-cost 0.50  # Never exceed $0.50
--max-time 180   # Must finish in 3 minutes
```

### 4. Check the Plan
Router shows its reasoning before execution:
```
📋 WORKFLOW PLAN:
  Tools: flux_dev, ideogram, luma, elevenlabs
  Estimated Cost: $0.20
  Estimated Time: 175s (2min)
  Quality Level: standard
  Reasoning: Topic requires text overlay (Ideogram) and smooth motion (Luma)...
```

### 5. Override if Needed
If router's choice doesn't match your vision, use fixed workflow:
```bash
python main.py --topic "your topic" --quality pro
```

---

## Troubleshooting

### Router selects wrong tools?
- Try a different preset
- Add explicit constraints (--max-cost, --max-time)
- Use fixed workflow if you need specific tools

### Cost still too high?
- Use `--preset budget`
- Add `--max-cost 0.15`
- Router will use cheapest alternatives

### Quality not good enough?
- Use `--preset premium`
- Or disable router and use fixed workflow
- Specify `--quality pro`

---

## Technical Details

### How the AI Decides

The router uses **GPT-4** to analyze:
1. **Topic analysis**: What does the video need?
2. **Tool matching**: Which tools are required vs optional?
3. **Cost optimization**: Cheaper alternatives available?
4. **Time optimization**: Faster alternatives available?
5. **Constraint checking**: Fits within budget/time limits?

### Tool Specifications

| Tool | Cost | Speed | Use Case |
|------|------|-------|----------|
| Midjourney | $0.05 | 5min | Cinematic opening |
| Flux Schnell | $0.02 | 10s | Fast images |
| Flux Dev | $0.03 | 30s | Quality images |
| Flux Pro | $0.04 | 25s | Premium images |
| Seedream 4 | $0.04 | 30s | Character consistency |
| Ideogram | $0.02 | 15s | Text overlays |
| Luma | $0.10 | 2min | Video animation |
| Ken Burns | $0.00 | 1s | Static motion effects |
| ElevenLabs | $0.05 | 10s | Voiceover |

---

## Summary

**The AI-Powered Router is a game-changer for:**
- 💰 **Cost savings** (50-90% on simple videos)
- ⚡ **Speed** (skip slow unnecessary tools)
- 🧠 **Smart decisions** (AI analyzes and optimizes)
- 🎯 **Flexibility** (adapts to your needs)

**Start using it today:**
```bash
python main.py --topic "your topic" --use-router --preset standard
```

**Questions?** Check the logs - router explains its reasoning!
