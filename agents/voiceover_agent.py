"""
Voiceover Agent - Phase 4
Generates voiceover audio using ElevenLabs.
"""
from typing import Dict, Any
import logging
from tools import ElevenLabsVoiceTool

logger = logging.getLogger(__name__)


class VoiceoverAgent:
    """
    Agent responsible for generating voiceover audio.
    Uses ElevenLabs API for high-quality multilingual TTS.
    """
    
    def __init__(self, default_language: str = "sk"):
        """
        Initialize voiceover agent.
        
        Args:
            default_language: Default language code (sk, cs, en, etc.)
        """
        self.name = "Voiceover Agent"
        self.voice_tool = ElevenLabsVoiceTool()
        self.default_language = default_language
        self.logger = logging.getLogger(f"agents.{self.name}")
    
    def generate_voiceover(
        self,
        script: str,
        language: str = None,
        voice_id: str = None,
        output_dir: str = None
    ) -> Dict[str, Any]:
        """
        Generate voiceover audio from script.
        
        Args:
            script: Voiceover script text
            language: Language code (defaults to agent's default)
            voice_id: Optional specific voice ID
            output_dir: Custom output directory
            
        Returns:
            Dictionary with audio path and metadata
        """
        if language is None:
            language = self.default_language
        
        self.logger.info(f"Generating voiceover in {language}...")
        self.logger.info(f"Script: {script[:100]}...")
        
        # Generate voiceover
        # Build input data, only include voice_id if it's not None
        input_data = {
            "text": script,
            "language": language,
            "output_dir": output_dir,
        }
        
        # Only include voice_id if explicitly provided (not None)
        if voice_id is not None:
            input_data["voice_id"] = voice_id
        
        result = self.voice_tool.run(input_data)
        
        if result.get("success"):
            audio_path = result.get("audio_path")
            self.logger.info(f"Voiceover generated: {audio_path}")
            
            return {
                "audio_path": audio_path,
                "script": script,
                "language": language,
                "duration_estimate": result.get("duration_estimate", 0),
            }
        else:
            self.logger.error("Voiceover generation failed")
            raise Exception(f"Voiceover generation failed: {result.get('error')}")
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with voiceover audio
        """
        prompts = state.get("prompts", {})
        script = prompts.get("voiceover_script", "")
        output_dir = state.get("run_output_dir")
        
        # Detect language from brand_hub or use default
        brand_hub = state.get("brand_hub", {})
        language = brand_hub.get("language", self.default_language)
        
        voiceover = self.generate_voiceover(script, language, output_dir=output_dir)
        
        return {
            **state,
            "voiceover_audio": voiceover.get("audio_path"),
            "voiceover_script": script,
            "voiceover_language": language,
        }


if __name__ == "__main__":
    # Test the agent
    agent = VoiceoverAgent(default_language="sk")
    
    test_state = {
        "prompts": {
            "voiceover_script": "Toto je viac ako len káva. Je to moment pokoja. Rituál na správny začiatok dňa."
        },
        "brand_hub": {
            "language": "sk"
        }
    }
    
    # result = agent.run(test_state)
    # print(result)
