"""
Brand Identity Loader

Utility for loading and validating brand identity files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BrandIdentity:
    """Brand identity data container."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with brand data."""
        self.data = data
        self.client = data.get("client", {})
        
    @property
    def name(self) -> str:
        """Get brand name."""
        return self.client.get("name", "Unknown Brand")
    
    @property
    def industry(self) -> str:
        """Get industry."""
        return self.client.get("industry", "General")
    
    @property
    def target_audience(self) -> str:
        """Get target audience."""
        return self.client.get("target_audience", "General audience")
    
    @property
    def visual_identity(self) -> Dict[str, Any]:
        """Get visual identity guidelines."""
        return self.client.get("visual_identity", {})
    
    @property
    def tone_of_voice(self) -> Dict[str, Any]:
        """Get tone of voice guidelines."""
        return self.client.get("tone_of_voice", {})
    
    @property
    def brand_values(self) -> list:
        """Get brand values."""
        return self.client.get("brand_values", [])
    
    @property
    def content_guidelines(self) -> Dict[str, Any]:
        """Get content guidelines."""
        return self.client.get("content_guidelines", {})
    
    def get_context_string(self) -> str:
        """
        Get a formatted string representation for AI prompts.
        
        Returns:
            Formatted brand identity context for AI agents
        """
        visual = self.visual_identity
        tone = self.tone_of_voice
        guidelines = self.content_guidelines
        
        context = f"""
**BRAND IDENTITY: {self.name}**

Industry: {self.industry}
Target Audience: {self.target_audience}

**Visual Identity:**
- Style: {visual.get('style', 'Not specified')}
- Mood: {visual.get('mood', 'Not specified')}
- Primary Colors: {', '.join(visual.get('primary_colors', [])) or 'Not specified'}
- Avoid: {visual.get('avoid', 'Not specified')}

**Tone of Voice:**
- Personality: {', '.join(tone.get('personality', [])) or 'Not specified'}
- Style: {tone.get('style', 'Not specified')}
- Language: {tone.get('language', 'Not specified')}
- Avoid: {', '.join(tone.get('avoid', [])) or 'Not specified'}

**Brand Values:**
{chr(10).join(f'- {value}' for value in self.brand_values) if self.brand_values else '- Not specified'}

**Content Guidelines:**
Must Include: {', '.join(guidelines.get('must_include', [])) or 'Not specified'}
Must Avoid: {', '.join(guidelines.get('must_avoid', [])) or 'Not specified'}
Preferred Settings: {', '.join(guidelines.get('preferred_settings', [])) or 'Not specified'}
Brand Keywords: {', '.join(guidelines.get('brand_keywords', [])) or 'Not specified'}
"""
        return context.strip()
    
    def __str__(self) -> str:
        """String representation."""
        return f"BrandIdentity({self.name})"


def load_brand_identity(brand_file: Optional[str] = None) -> BrandIdentity:
    """
    Load brand identity from JSON file.
    
    Args:
        brand_file: Path to brand identity JSON file.
                   If None, loads default brand identity.
                   Can be:
                   - Full path: "/path/to/brand.json"
                   - Brand name: "artisan_coffee" (looks in brands/ directory)
                   - None: Uses default.json
    
    Returns:
        BrandIdentity object
    
    Raises:
        FileNotFoundError: If brand file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    # Determine file path
    if brand_file is None:
        # Use default
        brands_dir = Path(__file__).parent.parent / "brands"
        file_path = brands_dir / "default.json"
        logger.info("Using default brand identity")
    elif Path(brand_file).exists():
        # Full path provided
        file_path = Path(brand_file)
        logger.info(f"Loading brand identity from: {file_path}")
    else:
        # Assume it's a brand name, look in brands/ directory
        brands_dir = Path(__file__).parent.parent / "brands"
        
        # Try with .json extension
        file_path = brands_dir / f"{brand_file}.json"
        if not file_path.exists():
            # Try without adding extension (maybe already included)
            file_path = brands_dir / brand_file
        
        if not file_path.exists():
            logger.warning(f"Brand file not found: {brand_file}, using default")
            file_path = brands_dir / "default.json"
        else:
            logger.info(f"Loading brand identity: {brand_file}")
    
    # Load and parse JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        brand = BrandIdentity(data)
        logger.info(f"Brand identity loaded: {brand.name}")
        return brand
        
    except FileNotFoundError:
        logger.error(f"Brand file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in brand file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading brand identity: {e}")
        raise


def list_available_brands() -> list:
    """
    List all available brand identity files.
    
    Returns:
        List of brand file names (without .json extension)
    """
    brands_dir = Path(__file__).parent.parent / "brands"
    
    if not brands_dir.exists():
        return []
    
    brand_files = []
    for file_path in brands_dir.glob("*.json"):
        brand_files.append(file_path.stem)
    
    return sorted(brand_files)


# Export
__all__ = ["BrandIdentity", "load_brand_identity", "list_available_brands"]
