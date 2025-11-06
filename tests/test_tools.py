"""
Unit tests for tools.
"""
import pytest
from unittest.mock import Mock, patch
from tools import TavilySearchTool, FluxSchnellTool, ElevenLabsVoiceTool, VideoAssemblyTool


class TestTavilySearchTool:
    """Tests for Tavily Search Tool."""
    
    def test_validate_input_success(self):
        tool = TavilySearchTool()
        is_valid, error = tool.validate_input({"query": "test query"})
        assert is_valid is True
        assert error is None
    
    def test_validate_input_missing_query(self):
        tool = TavilySearchTool()
        is_valid, error = tool.validate_input({})
        assert is_valid is False
        assert "query" in error.lower()
    
    def test_validate_input_empty_query(self):
        tool = TavilySearchTool()
        is_valid, error = tool.validate_input({"query": ""})
        assert is_valid is False
        assert "empty" in error.lower()


class TestFluxSchnellTool:
    """Tests for Flux Image Generation Tool."""
    
    def test_validate_input_success(self):
        tool = FluxSchnellTool()
        is_valid, error = tool.validate_input({"prompt": "test prompt"})
        assert is_valid is True
        assert error is None
    
    def test_validate_input_missing_prompt(self):
        tool = FluxSchnellTool()
        is_valid, error = tool.validate_input({})
        assert is_valid is False
        assert "prompt" in error.lower()


class TestElevenLabsVoiceTool:
    """Tests for ElevenLabs Voice Tool."""
    
    def test_validate_input_success(self):
        tool = ElevenLabsVoiceTool()
        is_valid, error = tool.validate_input({"text": "test text"})
        assert is_valid is True
        assert error is None
    
    def test_validate_input_missing_text(self):
        tool = ElevenLabsVoiceTool()
        is_valid, error = tool.validate_input({})
        assert is_valid is False
        assert "text" in error.lower()


class TestVideoAssemblyTool:
    """Tests for Video Assembly Tool."""
    
    def test_validate_input_success(self):
        tool = VideoAssemblyTool()
        is_valid, error = tool.validate_input({"images": ["img1.png", "img2.png"]})
        assert is_valid is True
        assert error is None
    
    def test_validate_input_missing_images(self):
        tool = VideoAssemblyTool()
        is_valid, error = tool.validate_input({})
        assert is_valid is False
        assert "images" in error.lower()
    
    def test_validate_input_empty_images(self):
        tool = VideoAssemblyTool()
        is_valid, error = tool.validate_input({"images": []})
        assert is_valid is False
        assert "empty" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
