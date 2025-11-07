"""
Configuration settings for the Social Video Agent system.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", BASE_DIR / "logs"))
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# Default voice: Peter (SK) - Multilingual male voice optimized for Slovak
# Voice ID: KXmit7OSDv7UUSoiQegm
# Alternative: 21m00Tcm4TlvDq8ikWAM (Rachel - English female)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "KXmit7OSDv7UUSoiQegm")
APIFRAME_API_KEY = os.getenv("APIFRAME_API_KEY")
IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Video Configuration
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
VIDEO_DURATION = int(os.getenv("VIDEO_DURATION", "30"))

# Workflow Configuration
ENABLE_CHECKPOINTS = os.getenv("ENABLE_CHECKPOINTS", "true").lower() == "true"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

# Debug Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

# Replicate Model IDs (with version hashes)
REPLICATE_MODELS = {
    "flux_pro": "black-forest-labs/flux-1.1-pro",
    "flux_dev": "black-forest-labs/flux-dev",
    "flux_schnell": "black-forest-labs/flux-schnell",
    "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    "controlnet": "jagilley/controlnet-canny:aff48af9c68d162388d230a2ab003f68d2638d88307bdaf1c2f1ac95079c9613",
}

# ElevenLabs Configuration
# eleven_v3 (alpha) - Most expressive model with emotion tags support
# Supports 70+ languages including Slovak
ELEVENLABS_MODEL = "eleven_v3"

# ElevenLabs Emotion Tags (inline in text)
# Supported tags: [sarcastically], [giggles], [whispers], [shouting], [sighs], [gasps], etc.
# Example: "Hello [giggles] this is fun [whispers] but secret"

# Tavily Configuration
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_MAX_RESULTS = 5


def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration is present.
    
    Returns:
        Tuple of (is_valid, list of missing items)
    """
    missing = []
    
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if not REPLICATE_API_TOKEN:
        missing.append("REPLICATE_API_TOKEN")
    if not ELEVENLABS_API_KEY:
        missing.append("ELEVENLABS_API_KEY")
    
    return len(missing) == 0, missing


if __name__ == "__main__":
    is_valid, missing = validate_config()
    if is_valid:
        print("✅ Configuration is valid!")
    else:
        print("❌ Missing configuration:")
        for item in missing:
            print(f"  - {item}")
