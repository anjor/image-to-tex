"""Tests for converter module."""

import pytest
from pathlib import Path

from image_to_tex.core.converter import ImageToLaTeXConverter, ConversionError
from image_to_tex.core.vision_client import VisionClient, NoAPIKeyError
from image_to_tex.utils.latex_formatter import ContentType


class TestConverter:
    """Test cases for ImageToLaTeXConverter."""

    def test_converter_initialization(self):
        """Test converter can be initialized."""
        # This will fail if no API keys are set, which is expected
        try:
            converter = ImageToLaTeXConverter()
            assert converter is not None
            assert converter.vision_client is not None
        except NoAPIKeyError:
            pytest.skip("No API keys configured")

    def test_converter_with_invalid_image(self):
        """Test converter with invalid image path."""
        try:
            converter = ImageToLaTeXConverter()
        except NoAPIKeyError:
            pytest.skip("No API keys configured")

        with pytest.raises(ConversionError):
            converter.convert("nonexistent_image.png")

    def test_converter_result_attributes(self):
        """Test ConverterResult has expected attributes."""
        from image_to_tex.core.converter import ConverterResult

        result = ConverterResult(
            latex_code="E = mc^2",
            content_type=ContentType.EQUATION,
            raw_response="The equation is E = mc^2",
            is_valid=True,
            validation_error=None,
        )

        assert result.latex_code == "E = mc^2"
        assert result.content_type == ContentType.EQUATION
        assert result.is_valid is True
        assert result.validation_error is None

        # Test to_dict
        result_dict = result.to_dict()
        assert "latex_code" in result_dict
        assert "content_type" in result_dict
        assert result_dict["content_type"] == "equation"


class TestVisionClient:
    """Test cases for VisionClient."""

    def test_vision_client_no_api_keys(self, monkeypatch):
        """Test vision client raises error with no API keys."""
        # Remove all API keys
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(NoAPIKeyError):
            VisionClient()

    def test_vision_client_with_anthropic_key(self, monkeypatch):
        """Test vision client initializes with Anthropic key."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        client = VisionClient()
        assert client.anthropic_client is not None
        assert client.openai_client is None

    def test_vision_client_with_openai_key(self, monkeypatch):
        """Test vision client initializes with OpenAI key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        client = VisionClient()
        assert client.anthropic_client is None
        assert client.openai_client is not None
