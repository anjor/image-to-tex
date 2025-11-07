"""Vision AI client with support for Claude and GPT-4 Vision."""

import base64
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from anthropic import Anthropic
from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported vision model providers."""

    CLAUDE = "claude"
    OPENAI = "openai"
    NONE = "none"


class VisionClientError(Exception):
    """Base exception for vision client errors."""
    pass


class NoAPIKeyError(VisionClientError):
    """Raised when no API key is available."""
    pass


class VisionClient:
    """
    Client for vision AI models with automatic fallback support.

    Supports Claude (Anthropic) and GPT-4 Vision (OpenAI) with configurable
    primary and fallback models.
    """

    def __init__(
        self,
        primary_model: Optional[ModelProvider] = None,
        fallback_model: Optional[ModelProvider] = None,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        claude_model: str = "claude-sonnet-4-5-20250929",
        openai_model: str = "gpt-4-vision-preview",
    ):
        """
        Initialize the vision client.

        Args:
            primary_model: Primary model provider to use
            fallback_model: Fallback model provider if primary fails
            anthropic_api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            openai_api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            claude_model: Specific Claude model version
            openai_model: Specific OpenAI model version
        """
        # Get API keys from environment if not provided
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Set model preferences
        self.primary_model = primary_model or ModelProvider(
            os.getenv("PRIMARY_MODEL", "claude")
        )
        fallback_env = os.getenv("FALLBACK_MODEL", "openai")
        self.fallback_model = (
            fallback_model if fallback_model is not None
            else ModelProvider(fallback_env) if fallback_env != "none"
            else ModelProvider.NONE
        )

        self.claude_model = os.getenv("CLAUDE_MODEL", claude_model)
        self.openai_model = os.getenv("OPENAI_MODEL", openai_model)

        # Initialize clients
        self.anthropic_client = None
        self.openai_client = None

        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)

        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

        # Validate at least one API key is available
        if not self.anthropic_client and not self.openai_client:
            raise NoAPIKeyError(
                "No API keys provided. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
                "environment variable, or pass keys to the constructor."
            )

    def _encode_image(self, image_path: Union[str, Path]) -> tuple[str, str]:
        """
        Encode image to base64 and detect media type.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (base64_encoded_data, media_type)
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Detect media type
        img = Image.open(image_path)
        format_lower = img.format.lower() if img.format else "png"

        media_type_map = {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        media_type = media_type_map.get(format_lower, "image/png")

        # Read and encode
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        return image_data, media_type

    def _call_claude(self, prompt: str, image_path: Union[str, Path]) -> str:
        """
        Call Claude vision API.

        Args:
            prompt: Text prompt for the vision model
            image_path: Path to the image

        Returns:
            Model response text
        """
        if not self.anthropic_client:
            raise NoAPIKeyError("Anthropic API key not configured")

        image_data, media_type = self._encode_image(image_path)

        logger.info(f"Calling Claude model: {self.claude_model}")

        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        return message.content[0].text

    def _call_openai(self, prompt: str, image_path: Union[str, Path]) -> str:
        """
        Call OpenAI GPT-4 Vision API.

        Args:
            prompt: Text prompt for the vision model
            image_path: Path to the image

        Returns:
            Model response text
        """
        if not self.openai_client:
            raise NoAPIKeyError("OpenAI API key not configured")

        image_data, media_type = self._encode_image(image_path)

        logger.info(f"Calling OpenAI model: {self.openai_model}")

        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )

        return response.choices[0].message.content

    def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        use_fallback: bool = True,
    ) -> str:
        """
        Analyze an image using vision AI with automatic fallback.

        Args:
            image_path: Path to the image file
            prompt: Text prompt describing what to extract/analyze
            use_fallback: Whether to try fallback model if primary fails

        Returns:
            Model response text

        Raises:
            VisionClientError: If all attempts fail
        """
        # Try primary model
        try:
            if self.primary_model == ModelProvider.CLAUDE:
                return self._call_claude(prompt, image_path)
            elif self.primary_model == ModelProvider.OPENAI:
                return self._call_openai(prompt, image_path)
        except Exception as e:
            logger.warning(f"Primary model ({self.primary_model}) failed: {e}")

            if not use_fallback or self.fallback_model == ModelProvider.NONE:
                raise VisionClientError(
                    f"Primary model failed and no fallback configured: {e}"
                ) from e

        # Try fallback model
        if use_fallback and self.fallback_model != ModelProvider.NONE:
            try:
                logger.info(f"Attempting fallback model: {self.fallback_model}")

                if self.fallback_model == ModelProvider.CLAUDE:
                    return self._call_claude(prompt, image_path)
                elif self.fallback_model == ModelProvider.OPENAI:
                    return self._call_openai(prompt, image_path)
            except Exception as e:
                logger.error(f"Fallback model ({self.fallback_model}) failed: {e}")
                raise VisionClientError(
                    f"Both primary and fallback models failed. Last error: {e}"
                ) from e

        raise VisionClientError("No models available or all attempts failed")
