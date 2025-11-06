"""Configuration package for Social Video Agent."""
from .settings import *
from .brand_loader import BrandIdentity, load_brand_identity, list_available_brands

__all__ = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "TAVILY_API_KEY",
    "REPLICATE_API_TOKEN",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "VIDEO_WIDTH",
    "VIDEO_HEIGHT",
    "VIDEO_FPS",
    "VIDEO_DURATION",
    "OUTPUT_DIR",
    "LOGS_DIR",
    "DATA_DIR",
    "validate_config",
    "BrandIdentity",
    "load_brand_identity",
    "list_available_brands",
]
