# 🚀 Quick Start Guide

Get started with Social Video Agent in 5 minutes!

## Prerequisites

- Python 3.11+
- FFMPEG installed
- API keys ready

## Step 1: Install FFMPEG

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Step 2: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

Add your keys:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
REPLICATE_API_TOKEN=r8_...
ELEVENLABS_API_KEY=...
```

## Step 4: Verify Setup

```bash
python config/settings.py
```

You should see: ✅ Configuration is valid!

## Step 5: Run Your First Video

```bash
python main.py --test
```

This will generate a test video about "morning coffee ritual".

## Step 6: Create Custom Video

```bash
python main.py --topic "your amazing topic here"
```

## 📺 Example Topics

Try these:
- "morning coffee ritual"
- "summer beach vibes"
- "fitness motivation"
- "healthy breakfast ideas"
- "urban photography tips"
- "meditation and mindfulness"

## 🎛️ Customize

### Change Language

```bash
python main.py --topic "váš úžasný nápad" --language sk
```

### Higher Quality

```bash
python main.py --topic "premium content" --quality pro
```

### Use Brand Hub

```bash
python main.py --topic "your topic" --brand-hub data/brand_hub.json
```

## 📂 Where to Find Output

After running, check:
- **Video**: `output/video_*_final.mp4`
- **Audio**: `output/voiceover_*.mp3`
- **Images**: `output/flux_*.png`
- **Results**: `output/results_*.json`

## 🆘 Common Issues

### "Configuration validation failed"
→ Check your `.env` file has all API keys

### "FFMPEG not found"
→ Install FFMPEG (see Step 1)

### "API rate limit"
→ Wait a few minutes, or use `--quality schnell`

## 💡 Pro Tips

1. **Start with test mode** to verify everything works
2. **Use `schnell` quality** for testing (faster, cheaper)
3. **Use `dev` quality** for production (best balance)
4. **Use `pro` quality** only for premium content
5. **Check logs** in `logs/` if something fails

## 📖 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize `data/brand_hub.json` for your brand
- Explore individual tools in `tools/` directory
- Check example videos in `output/` after running

---

**Need help?** Check the full README or enable verbose mode:
```bash
python main.py --topic "your topic" --verbose
```
