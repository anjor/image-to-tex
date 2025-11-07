"""
Image-to-LaTeX converter using vision AI models.

Convert images of scientific work (equations, tables, diagrams) to LaTeX code
using Claude (Anthropic) or GPT-4 Vision (OpenAI).

Basic usage:
    >>> from image_to_tex import convert_image
    >>> result = convert_image("equation.png")
    >>> print(result.latex_code)

Advanced usage:
    >>> from image_to_tex import ImageToLaTeXConverter, VisionClient
    >>> from image_to_tex.utils.latex_formatter import ContentType
    >>>
    >>> # Custom configuration
    >>> client = VisionClient(primary_model="claude", fallback_model="openai")
    >>> converter = ImageToLaTeXConverter(vision_client=client)
    >>>
    >>> # Convert with specific content type
    >>> result = converter.convert("table.png", content_type=ContentType.TABLE)
    >>> print(result.latex_code)
"""

from .core.converter import (
    ConversionError,
    ConverterResult,
    ImageToLaTeXConverter,
)
from .core.vision_client import (
    ModelProvider,
    NoAPIKeyError,
    VisionClient,
    VisionClientError,
)
from .utils.image_handler import ImageHandler, ImageHandlerError
from .utils.latex_formatter import ContentType, LaTeXFormatter

__version__ = "0.1.0"
__all__ = [
    # Main converter
    "ImageToLaTeXConverter",
    "ConverterResult",
    "ConversionError",
    # Vision client
    "VisionClient",
    "VisionClientError",
    "NoAPIKeyError",
    "ModelProvider",
    # Utilities
    "ImageHandler",
    "ImageHandlerError",
    "LaTeXFormatter",
    "ContentType",
    # Convenience functions
    "convert_image",
    "convert_equation",
    "convert_table",
]


# Convenience function for simple usage
def convert_image(image_path: str, **kwargs) -> ConverterResult:
    """
    Convert an image to LaTeX code (convenience function).

    Args:
        image_path: Path to the image file
        **kwargs: Additional arguments passed to ImageToLaTeXConverter.convert()

    Returns:
        ConverterResult with LaTeX code and metadata

    Example:
        >>> result = convert_image("equation.png")
        >>> print(result.latex_code)
        >>> print(result.content_type)
    """
    converter = ImageToLaTeXConverter()
    return converter.convert(image_path, **kwargs)


def convert_equation(image_path: str, inline: bool = False) -> str:
    """
    Convert an image containing equations to LaTeX (convenience function).

    Args:
        image_path: Path to the image file
        inline: Whether to format as inline math

    Returns:
        Formatted LaTeX equation code

    Example:
        >>> latex = convert_equation("formula.png")
        >>> print(latex)
    """
    converter = ImageToLaTeXConverter()
    return converter.convert_equation(image_path, inline=inline)


def convert_table(image_path: str, caption: str = None) -> str:
    """
    Convert an image containing a table to LaTeX (convenience function).

    Args:
        image_path: Path to the image file
        caption: Optional table caption

    Returns:
        Formatted LaTeX table code

    Example:
        >>> latex = convert_table("data.png", caption="Experimental Results")
        >>> print(latex)
    """
    converter = ImageToLaTeXConverter()
    return converter.convert_table(image_path, caption=caption)
