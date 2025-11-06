# 🎬 Social Video Agent

AI-powered multi-agent system for automated social media video content creation. Generate professional-quality vertical videos (Instagram Reels, TikTok) from a simple text prompt.

## ✨ Features

- **🤖 Multi-Agent Architecture**: Coordinated AI agents working together
- **🎨 Professional Quality**: Uses Flux (Replicate) for cinematic visuals
- **🎤 Multilingual Voiceover**: ElevenLabs TTS with Slovak, Czech, English support
- **🔄 LangGraph Orchestration**: Robust workflow management with error handling
- **💻 Local Deployment**: Run entirely on your machine via command line
- **⚙️ Configurable**: Customize quality, language, and brand identity

## 🏗️ Architecture

The system uses a **pipeline multi-agent architecture** with 5 phases:

```
Phase 1A: Research Agent
    ↓ (Trend analysis)
Phase 1B: Creative Strategist
    ↓ (Prompt generation)
Phase 2:  Visual Production Agent
    ↓ (Image generation)
Phase 4:  Voiceover Agent
    ↓ (Audio generation)
Phase 5:  Assembly Agent
    ↓ (Video compilation)
    → Final Video
```

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| **Research Agent** | Analyzes social media trends | Tavily Search API |
| **Creative Strategist** | Creates scenario and prompts | GPT-4 (OpenAI) |
| **Visual Production** | Generates all images | Flux (Replicate) |
| **Voiceover Agent** | Creates audio narration | ElevenLabs TTS |
| **Assembly Agent** | Combines into final video | FFMPEG |

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **FFMPEG**: Must be installed on your system
- **API Keys**: OpenAI, Tavily, Replicate, ElevenLabs

### Installing FFMPEG

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## 🚀 Installation

### 1. Clone or extract the project

```bash
cd social_video_agent
```

### 2. Create virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
REPLICATE_API_TOKEN=r8_...
ELEVENLABS_API_KEY=...
```

### 5. Verify configuration

```bash
python config/settings.py
```

You should see: `✅ Configuration is valid!`

## 🎯 Usage

### Basic Usage

```bash
python main.py --topic "morning coffee ritual"
```

### With Custom Brand Hub

```bash
python main.py --topic "new product launch" --brand-hub data/brand_hub.json
```

### High Quality Mode

```bash
python main.py --topic "summer vibes" --quality pro --language en
```

### Test Mode

```bash
python main.py --test
```

### Command-Line Options

```
--topic TEXT          Video topic/theme (required unless --test)
--brand-hub PATH      Path to brand_hub.json file
--quality CHOICE      Image quality: schnell (fast), dev (balanced), pro (best)
--language CODE       Voiceover language: sk, cs, en, etc.
--test                Run with test data
--verbose             Enable verbose logging
```

## 📁 Project Structure

```
social_video_agent/
├── agents/                 # AI agents
│   ├── research_agent.py
│   ├── creative_strategist.py
│   ├── visual_production_agent.py
│   ├── voiceover_agent.py
│   └── assembly_agent.py
├── tools/                  # Modular tools
│   ├── base_tool.py
│   ├── tavily_search.py
│   ├── replicate_image.py
│   ├── elevenlabs_voice.py
│   └── video_assembly.py
├── config/                 # Configuration
│   └── settings.py
├── data/                   # Input data
│   └── brand_hub.json      # Brand identity (optional)
├── output/                 # Generated videos and assets
├── logs/                   # Workflow logs
├── workflow.py             # LangGraph orchestration
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
└── README.md              # This file
```

## 🎨 Brand Hub Configuration

Create a `brand_hub.json` file to customize your brand identity:

```json
{
  "tone_of_voice": "warm and inviting",
  "colors": ["#8B4513", "#F5DEB3", "#FFFFFF"],
  "values": "quality, authenticity, mindfulness",
  "language": "sk"
}
```

Place it in the `data/` folder and reference it:

```bash
python main.py --topic "your topic" --brand-hub data/brand_hub.json
```

## 🔧 Configuration

### Video Settings

Edit `.env` to customize video output:

```env
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
VIDEO_DURATION=30
```

### Quality vs Speed

| Quality | Model | Speed | Cost | Use Case |
|---------|-------|-------|------|----------|
| `schnell` | Flux Schnell | ⚡ Fast | 💰 Low | Testing, drafts |
| `dev` | Flux Dev | ⚖️ Balanced | 💰💰 Medium | Production (recommended) |
| `pro` | Flux Pro | 🐌 Slow | 💰💰💰 High | Premium content |

### Language Support

ElevenLabs supports 29 languages including:

- 🇸🇰 Slovak (`sk`)
- 🇨🇿 Czech (`cs`)
- 🇬🇧 English (`en`)
- 🇩🇪 German (`de`)
- 🇪🇸 Spanish (`es`)
- 🇫🇷 French (`fr`)
- And many more...

## 📊 Output

After successful execution, you'll find:

- **Final Video**: `output/video_YYYYMMDD_HHMMSS_final.mp4`
- **Voiceover Audio**: `output/voiceover_LANG_YYYYMMDD_HHMMSS.mp3`
- **Generated Images**: `output/flux_*_*.png`
- **Results JSON**: `output/results_YYYYMMDD_HHMMSS.json`
- **Workflow Log**: `logs/workflow_YYYYMMDD_HHMMSS.log`

## 🧪 Testing

### Test Individual Tools

```bash
# Test Tavily search
python tools/tavily_search.py

# Test Flux image generation
python tools/replicate_image.py

# Test ElevenLabs voiceover
python tools/elevenlabs_voice.py
```

### Test Individual Agents

```bash
# Test research agent
python agents/research_agent.py

# Test creative strategist
python agents/creative_strategist.py
```

### Test Complete Workflow

```bash
python main.py --test --verbose
```

## 🐛 Troubleshooting

### "Configuration validation failed"

Make sure all API keys are set in `.env`:
```bash
python config/settings.py
```

### "FFMPEG not found"

Install FFMPEG:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

### "API rate limit exceeded"

- Wait a few minutes and try again
- Check your API usage limits
- Use `--quality schnell` for faster/cheaper generation

### Images not generating

- Check Replicate API key is valid
- Verify you have credits in your Replicate account
- Try `--quality schnell` (faster, more reliable)

### Voiceover fails

- Verify ElevenLabs API key
- Check you have credits (free tier: 10,000 chars/month)
- Try shorter voiceover script

## 💰 Cost Estimation

Approximate costs per video (30 seconds, 3-4 images):

| Service | Usage | Cost |
|---------|-------|------|
| OpenAI (GPT-4) | ~500 tokens | $0.01 |
| Tavily Search | 2-3 queries | $0.01 |
| Replicate (Flux Dev) | 3-4 images | $0.03-0.04 |
| ElevenLabs | ~200 chars | Free tier |
| **Total** | | **~$0.05-0.06** |

*Using Flux Pro increases cost to ~$0.15-0.20 per video*

## 🔒 Security

- API keys are stored in `.env` (never commit to git)
- `.gitignore` excludes sensitive files
- All API calls use HTTPS

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues or questions:

1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Enable verbose mode: `--verbose`

## 🎓 Examples

### Example 1: Coffee Shop Promo

```bash
python main.py \
  --topic "artisan coffee brewing experience" \
  --quality dev \
  --language en
```

### Example 2: Product Launch (Slovak)

```bash
python main.py \
  --topic "nový smart watch s AI asistentom" \
  --quality pro \
  --language sk \
  --brand-hub data/brand_hub.json
```

### Example 3: Quick Test

```bash
python main.py --test --quality schnell
```

## 🚀 Advanced Usage

### Custom Workflow

You can import and use the workflow programmatically:

```python
from workflow import SocialVideoWorkflow

workflow = SocialVideoWorkflow(
    visual_quality="dev",
    default_language="sk"
)

brand_hub = {
    "tone_of_voice": "energetic and fun",
    "colors": ["#FF6B6B", "#4ECDC4"],
    "language": "sk"
}

result = workflow.run(
    topic="summer beach party",
    brand_hub=brand_hub
)

print(f"Video: {result['final_video']}")
```

### Extending the System

To add new tools:

1. Create a new tool in `tools/` inheriting from `BaseTool`
2. Implement `execute()`, `validate_input()` methods
3. Add to `tools/__init__.py`
4. Use in agents or create new agent

---

**Made with ❤️ using LangChain, LangGraph, and cutting-edge AI tools**
