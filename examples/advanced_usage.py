"""Advanced usage examples for image-to-tex."""

from image_to_tex import ImageToLaTeXConverter, VisionClient
from image_to_tex.core.vision_client import ModelProvider
from image_to_tex.utils.latex_formatter import ContentType, LaTeXFormatter


def example_custom_vision_client():
    """Create a custom vision client with specific configuration."""
    print("=== Custom Vision Client Example ===")

    # Create client with specific primary and fallback models
    client = VisionClient(
        primary_model=ModelProvider.CLAUDE,
        fallback_model=ModelProvider.OPENAI,
        claude_model="claude-sonnet-4-5-20250929",
        openai_model="gpt-4-vision-preview",
    )

    converter = ImageToLaTeXConverter(vision_client=client)

    print("Created converter with custom vision client")
    print("Primary: Claude, Fallback: OpenAI")


def example_specific_content_type():
    """Convert with specific content type (no auto-detection)."""
    print("\n=== Specific Content Type Example ===")

    converter = ImageToLaTeXConverter()

    # Force conversion as equation
    # result = converter.convert(
    #     "path/to/image.png",
    #     content_type=ContentType.EQUATION,
    #     auto_detect=False
    # )

    print("Example: Force specific content type")
    print("Useful when you know the content type in advance")


def example_latex_formatting():
    """Use LaTeX formatter utilities directly."""
    print("\n=== LaTeX Formatting Example ===")

    # Wrap equation
    raw_latex = "E = mc^2"
    display_eq = LaTeXFormatter.wrap_equation(raw_latex, inline=False)
    inline_eq = LaTeXFormatter.wrap_equation(raw_latex, inline=True)

    print(f"Display: {display_eq[:50]}...")
    print(f"Inline: {inline_eq}")

    # Validate LaTeX
    is_valid, error = LaTeXFormatter.validate_latex(display_eq)
    print(f"Valid: {is_valid}, Error: {error}")

    # Detect content type
    content_type = LaTeXFormatter.detect_content_type(display_eq)
    print(f"Detected type: {content_type}")


def example_full_document():
    """Create a complete LaTeX document."""
    print("\n=== Full Document Example ===")

    converter = ImageToLaTeXConverter()

    # Convert to complete document
    # latex_doc = converter.convert_to_document(
    #     "path/to/page.png",
    #     title="Research Paper",
    #     author="John Doe"
    # )

    print("Example: Convert to complete LaTeX document")
    print("Includes \\documentclass, packages, and \\begin{document}")


def example_error_handling():
    """Comprehensive error handling."""
    print("\n=== Error Handling Example ===")

    from image_to_tex.core.converter import ConversionError
    from image_to_tex.core.vision_client import NoAPIKeyError, VisionClientError
    from image_to_tex.utils.image_handler import ImageHandlerError

    # try:
    #     converter = ImageToLaTeXConverter()
    #     result = converter.convert("image.png")
    # except NoAPIKeyError as e:
    #     print(f"API key missing: {e}")
    # except ImageHandlerError as e:
    #     print(f"Image validation failed: {e}")
    # except VisionClientError as e:
    #     print(f"Vision API error: {e}")
    # except ConversionError as e:
    #     print(f"Conversion failed: {e}")
    # except Exception as e:
    #     print(f"Unexpected error: {e}")

    print("Example: Handle different error types appropriately")
    print("Provides specific exceptions for different failure modes")


def example_validation_and_fixing():
    """Validate LaTeX and handle validation errors."""
    print("\n=== Validation Example ===")

    converter = ImageToLaTeXConverter(validate_output=True)

    # result = converter.convert("path/to/image.png")
    #
    # if not result.is_valid:
    #     print(f"Validation failed: {result.validation_error}")
    #     # Could attempt to fix or re-convert
    # else:
    #     print("LaTeX is valid!")

    print("Example: Check validation status in result")
    print("Use result.is_valid and result.validation_error")


def example_custom_prompts():
    """Using the converter with understanding of prompts."""
    print("\n=== Understanding Prompts Example ===")

    converter = ImageToLaTeXConverter()

    # The converter uses specialized prompts for each content type
    print("Converter uses specialized prompts for:")
    print("- EQUATION: Extract mathematical formulas")
    print("- TABLE: Extract tabular structure")
    print("- DIAGRAM: Generate TikZ or figure environment")
    print("- DOCUMENT: Extract full document content")
    print("\nThese are automatically selected based on content_type parameter")


def example_image_preprocessing():
    """Preprocess images before conversion."""
    print("\n=== Image Preprocessing Example ===")

    from image_to_tex.utils.image_handler import ImageHandler

    handler = ImageHandler()

    # Validate image
    # handler.validate_image("path/to/image.png")

    # Get image info
    # info = handler.get_image_info("path/to/image.png")
    # print(f"Image: {info['width']}x{info['height']}, {info['format']}")

    # Preprocess (resize if too large)
    # processed_path = handler.preprocess_image("path/to/image.png", max_dimension=2048)

    print("Example: Validate and preprocess images before conversion")
    print("Ensures images meet requirements and are optimally sized")


if __name__ == "__main__":
    print("Image-to-LaTeX Advanced Usage Examples")
    print("=" * 50)
    print("\nNote: These examples show advanced API usage.")
    print("To run them, provide actual image paths and set API keys.\n")

    example_custom_vision_client()
    example_specific_content_type()
    example_latex_formatting()
    example_full_document()
    example_error_handling()
    example_validation_and_fixing()
    example_custom_prompts()
    example_image_preprocessing()

    print("\n" + "=" * 50)
    print("See README.md for more information and setup instructions.")
