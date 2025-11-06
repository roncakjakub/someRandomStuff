# 🚀 AI Router Quick Start Guide

Get started with the AI-Powered Workflow Router in 3 minutes!

---

## What is the AI Router?

The **AI Router** is an intelligent system that analyzes your video request and automatically selects the optimal combination of AI tools to use. This can **save you 50-90% on costs** while maintaining quality.

### Without Router (Old Way)
```bash
python main.py --topic "morning coffee"
```
**Result:** Uses ALL tools, costs $0.98, takes 8-10 minutes

### With Router (New Way)
```bash
python main.py --topic "morning coffee" --use-router --preset standard
```
**Result:** AI selects optimal tools, costs $0.20-0.40, takes 2-3 minutes

---

## 🎯 Quick Examples

### 1. Budget Mode (Fastest & Cheapest)
```bash
python main.py --topic "quick tip" --use-router --preset budget
```
**What happens:**
- AI skips expensive tools (Midjourney, Luma)
- Uses Flux Schnell (fast) + Ken Burns (free motion)
- **Cost:** $0.07
- **Time:** 20 seconds

**Perfect for:**
- Testing ideas
- High-volume content
- Daily posts

---

### 2. Standard Mode (Balanced)
```bash
python main.py --topic "product showcase" --use-router --preset standard
```
**What happens:**
- AI uses Flux Dev (good quality)
- Includes Luma if motion needed
- Includes text overlay if needed
- **Cost:** $0.20-0.40
- **Time:** 2-3 minutes

**Perfect for:**
- Regular content
- Most use cases
- Good quality on budget

---

### 3. Premium Mode (Maximum Quality)
```bash
python main.py --topic "brand campaign" --use-router --preset premium
```
**What happens:**
- AI uses Midjourney for cinematic opening
- Includes Luma for smooth motion
- Uses all relevant premium tools
- **Cost:** $0.80-0.98
- **Time:** 8-10 minutes

**Perfect for:**
- Important campaigns
- Brand content
- Professional work

---

### 4. Viral Mode (Engagement Optimized)
```bash
python main.py --topic "trending topic" --use-router --preset viral
```
**What happens:**
- AI ensures character consistency (Seedream 4)
- Includes text overlays (Ideogram)
- Uses video animation (Luma)
- **Cost:** $1.00-1.50
- **Time:** 10-12 minutes

**Perfect for:**
- Content meant to go viral
- Maximum engagement
- All features enabled

---

## 💰 Cost Constraints

### Set a Budget Limit
```bash
python main.py --topic "daily vlog" --use-router --max-cost 0.25
```
**What happens:**
- AI will NEVER exceed $0.25
- Automatically uses cheaper alternatives
- Skips expensive tools if needed

---

## ⚡ Time Constraints

### Need it Fast?
```bash
python main.py --topic "breaking news" --use-router --max-time 60
```
**What happens:**
- AI will deliver in under 60 seconds
- Skips slow tools (Midjourney, Luma)
- Uses fastest alternatives

---

## 🎓 Real-World Scenarios

### Scenario 1: Content Creator (Daily Posts)
**Goal:** Create 10 videos per day, budget $1/day

```bash
python main.py --topic "tip 1" --use-router --preset budget
python main.py --topic "tip 2" --use-router --preset budget
# ... 10 times
```
**Result:** $0.70 total (10 × $0.07), all done in 3-4 minutes

---

### Scenario 2: Marketing Agency (Client Work)
**Goal:** High-quality campaign video, no budget limit

```bash
python main.py --topic "new product launch" --use-router --preset premium
```
**Result:** $0.98, professional quality, 8-10 minutes

---

### Scenario 3: News Organization (Breaking News)
**Goal:** Fast turnaround, quality is secondary

```bash
python main.py --topic "breaking: earthquake" --use-router --max-time 60
```
**Result:** Video ready in 60 seconds, cost $0.10-0.15

---

### Scenario 4: E-commerce (Product Videos)
**Goal:** Good quality, include text, reasonable cost

```bash
python main.py --topic "iPhone 15 Pro features" --use-router --preset standard
```
**Result:** $0.20-0.30, includes text overlays, 2-3 minutes

---

## 📊 Understanding the Plan

When you run with router, you'll see:

```
📋 WORKFLOW PLAN:
  Tools: flux_dev, ideogram, luma, elevenlabs
  Estimated Cost: $0.20
  Estimated Time: 175s (2min)
  Quality Level: standard
  Reasoning: Topic requires text overlay (Ideogram) and smooth motion (Luma).
             Using Flux Dev for balanced quality/cost. Skipping Midjourney to save
             $0.05 and 5 minutes. Skipping Seedream 4 as no character consistency needed.
```

**This shows:**
- Which tools will be used
- Why each tool was selected
- Why some tools were skipped
- Total estimated cost and time

---

## 🔄 Comparing Presets

| Preset | Cost | Time | Tools | Best For |
|--------|------|------|-------|----------|
| **budget** | $0.07 | 20s | Flux Schnell, Ken Burns | Testing, high-volume |
| **standard** | $0.20-0.40 | 2-3min | Flux Dev, Luma (if needed) | Most use cases |
| **premium** | $0.80-0.98 | 8-10min | Midjourney, Luma, all tools | Important content |
| **viral** | $1.00-1.50 | 10-12min | All premium + extras | Viral-optimized |

---

## 💡 Pro Tips

### Tip 1: Start with Standard
```bash
python main.py --topic "your topic" --use-router --preset standard
```
This is the sweet spot for most use cases.

### Tip 2: Test with Budget First
```bash
# First, test your idea
python main.py --topic "your topic" --use-router --preset budget

# If it works, upgrade to premium
python main.py --topic "your topic" --use-router --preset premium
```

### Tip 3: Use Constraints for Control
```bash
# I have $0.30 budget and need it in 2 minutes
python main.py --topic "your topic" --use-router --max-cost 0.30 --max-time 120
```

### Tip 4: Check the Reasoning
Always read the workflow plan to understand why AI made its choices.

### Tip 5: Override if Needed
If router's choice doesn't match your vision, use fixed workflow:
```bash
python main.py --topic "your topic" --quality pro
```

---

## 🆚 Router vs Fixed Workflow

### Use Router When:
✅ You want to save money  
✅ You need fast turnaround  
✅ You're producing high-volume content  
✅ You want smart tool selection  
✅ You have budget/time constraints  

### Use Fixed Workflow When:
✅ You want maximum quality always  
✅ You want predictable costs  
✅ You're producing premium content  
✅ You don't mind using all tools  

---

## 🎬 Your First Router Video

**Step 1:** Choose a topic
```
"morning coffee ritual"
```

**Step 2:** Decide on quality level
- Testing? → `--preset budget`
- Regular content? → `--preset standard`
- Important? → `--preset premium`

**Step 3:** Run it!
```bash
python main.py --topic "morning coffee ritual" --use-router --preset standard
```

**Step 4:** Check the output
```
output/20250106_143022_morning_coffee_ritual/final_video.mp4
```

**Step 5:** Review the plan
Look at the logs to see what the AI decided and why.

---

## 🐛 Troubleshooting

### "Router selects wrong tools"
**Try:**
- Different preset: `--preset premium`
- Add constraints: `--max-cost 0.50`
- Use fixed workflow if you need specific tools

### "Cost still too high"
**Try:**
- `--preset budget`
- `--max-cost 0.15`
- Router will use cheapest alternatives

### "Quality not good enough"
**Try:**
- `--preset premium`
- `--quality pro`
- Or disable router: remove `--use-router`

---

## 📚 Next Steps

1. **Read the full guide:** [ROUTER_GUIDE.md](ROUTER_GUIDE.md)
2. **Explore presets:** Try all 4 presets with the same topic
3. **Experiment with constraints:** Test different cost/time limits
4. **Compare costs:** Run same topic with and without router

---

## 🎉 Summary

**The AI Router is your secret weapon for:**
- 💰 Saving 50-90% on costs
- ⚡ Faster video generation
- 🧠 Smart tool selection
- 🎯 Flexible presets and constraints

**Get started now:**
```bash
python main.py --topic "your topic" --use-router --preset standard
```

**Questions?** Check [ROUTER_GUIDE.md](ROUTER_GUIDE.md) for detailed documentation!

---

**Made with ❤️ for smart creators**
