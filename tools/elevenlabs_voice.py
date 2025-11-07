"""
ElevenLabs Voiceover Tool for generating audio narration.
"""
from typing import Dict, Any, Optional
from pathlib import Path
from elevenlabs import generate, save, set_api_key, voices, Voice, VoiceSettings
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(PathLib(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL, OUTPUT_DIR
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL, OUTPUT_DIR


class ElevenLabsVoiceTool(BaseTool):
    """
    Tool for generating voiceover using ElevenLabs API.
    Supports multiple languages including Slovak.
    """
    
    def __init__(self):
        super().__init__(
            name="elevenlabs_voice",
            description="Generate professional voiceover in multiple languages"
        )
        set_api_key(ELEVENLABS_API_KEY)
        self.default_voice_id = ELEVENLABS_VOICE_ID
        self.model = ELEVENLABS_MODEL
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that text is provided."""
        if "text" not in input_data:
            return False, "Missing required field: text"
        if not isinstance(input_data["text"], str):
            return False, "Text must be a string"
        if len(input_data["text"].strip()) == 0:
            return False, "Text cannot be empty"
        return True, None
    
    @retry_on_error(max_retries=3, delay=5)
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate voiceover audio from text.
        
        Args:
            input_data: Must contain 'text' field, optional 'voice_id', 'language', 'voice_settings'
            
        Returns:
            Dictionary with audio file path
        """
        text = input_data["text"]
        voice_id = input_data.get("voice_id", self.default_voice_id)
        language = input_data.get("language", "sk")  # Default to Slovak
        output_dir = input_data.get("output_dir")  # Custom output directory
        
        # Get voice settings (use defaults optimized for emotion if not provided)
        voice_settings_dict = input_data.get("voice_settings", self._get_default_voice_settings())
        
        self.logger.info(f"Generating voiceover ({language}): {text[:50]}...")
        self.logger.info(f"Voice settings: stability={voice_settings_dict.get('stability')}, style={voice_settings_dict.get('style')}")
        
        # Create VoiceSettings object
        voice_settings = VoiceSettings(
            stability=voice_settings_dict.get("stability", 0.0),
            similarity_boost=voice_settings_dict.get("similarity_boost", 0.75),
            style=voice_settings_dict.get("style", 0.0),
            use_speaker_boost=voice_settings_dict.get("use_speaker_boost", True)
        )
        
        # Create Voice object with settings
        # Note: Voice object must include voice_id AND settings
        voice_obj = Voice(
            voice_id=voice_id,
            settings=voice_settings
        )
        
        # Generate audio with emotional voice settings
        audio = generate(
            text=text,
            voice=voice_obj,
            model=self.model,
        )
        
        # Save audio file
        audio_path = self._save_audio(audio, language, output_dir)
        
        self.logger.info(f"Voiceover generated: {audio_path}")
        
        return {
            "audio_path": str(audio_path),
            "text": text,
            "voice_id": voice_id,
            "language": language,
            "duration_estimate": len(text) / 15,  # Rough estimate: ~15 chars per second
        }
    
    def _get_default_voice_settings(self) -> Dict[str, Any]:
        """
        Get default voice settings optimized for emotional, engaging content.
        
        Settings tuned for VIRAL social media content:
        - Lower stability = MORE emotion and natural variation
        - Higher style = MORE expressive, dramatic delivery
        - Speaker boost = Enhanced clarity and presence
        
        Returns:
            Dictionary with voice settings
        """
        return {
            "stability": 0.0,          # Creative mode for MAXIMUM emotion (must be 0.0, 0.5, or 1.0)
            "similarity_boost": 0.8,   # Higher for better voice quality (0-1) - was 0.75
            "style": 0.0,              # Creative expression (must be 0.0, 0.5, or 1.0)
            "use_speaker_boost": True, # Enhanced clarity
        }
    
    def _save_audio(self, audio_data: bytes, language: str, output_dir: str = None) -> Path:
        """
        Save audio data to file.
        
        Args:
            audio_data: Audio bytes
            language: Language code for filename
            output_dir: Custom output directory (uses OUTPUT_DIR if not provided)
            
        Returns:
            Path to saved audio file
        """
        import uuid
        from datetime import datetime
        from pathlib import Path
        
        # Use provided output_dir or fallback to OUTPUT_DIR
        target_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"voiceover_{language}_{timestamp}_{unique_id}.mp3"
        filepath = target_dir / filename
        
        # Save audio
        save(audio_data, str(filepath))
        
        return filepath
    
    def list_available_voices(self) -> list:
        """
        List all available voices.
        
        Returns:
            List of available voices
        """
        try:
            all_voices = voices()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                }
                for voice in all_voices
            ]
        except Exception as e:
            self.logger.error(f"Failed to fetch voices: {e}")
            return []
    
    def generate_multilingual(
        self, 
        text: str, 
        language: str = "sk",
        voice_id: Optional[str] = None,
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate voiceover with explicit language support and emotion control.
        
        Args:
            text: Text to convert to speech
            language: Language code (sk, cs, en, etc.)
            voice_id: Optional specific voice ID
            voice_settings: Optional voice settings for emotion control
                - stability (0-1): Lower = more emotion, Higher = more stable
                - similarity_boost (0-1): How close to original voice
                - style (0-1): Style exaggeration level
                - use_speaker_boost (bool): Boost similarity to speaker
            
        Returns:
            Generation result
        """
        input_data = {
            "text": text,
            "language": language,
        }
        if voice_id:
            input_data["voice_id"] = voice_id
        if voice_settings:
            input_data["voice_settings"] = voice_settings
        
        return self.run(input_data)


if __name__ == "__main__":
    # Test the tool
    tool = ElevenLabsVoiceTool()
    
    # Test Slovak
    result = tool.generate_multilingual(
        "Toto je viac ako len káva. Je to moment pokoja. Rituál na správny začiatok dňa.",
        language="sk"
    )
    print("Slovak:", result)
    
    # Test English
    result = tool.generate_multilingual(
        "It's more than just coffee. It's a moment of peace.",
        language="en"
    )
    print("English:", result)
