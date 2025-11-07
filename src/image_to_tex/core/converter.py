"""Main converter engine for image-to-LaTeX conversion."""

import logging
from pathlib import Path
from typing import Optional, Union

from ..utils.image_handler import ImageHandler, ImageHandlerError
from ..utils.latex_formatter import ContentType, LaTeXFormatter
from .vision_client import VisionClient, VisionClientError

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Base exception for conversion errors."""
    pass


class ConverterResult:
    """Result of an image-to-LaTeX conversion."""

    def __init__(
        self,
        latex_code: str,
        content_type: ContentType,
        raw_response: str,
        is_valid: bool = True,
        validation_error: Optional[str] = None,
    ):
        """
        Initialize conversion result.

        Args:
            latex_code: The generated LaTeX code
            content_type: Detected type of content
            raw_response: Raw response from vision model
            is_valid: Whether LaTeX passed validation
            validation_error: Error message if validation failed
        """
        self.latex_code = latex_code
        self.content_type = content_type
        self.raw_response = raw_response
        self.is_valid = is_valid
        self.validation_error = validation_error

    def __str__(self) -> str:
        return self.latex_code

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "latex_code": self.latex_code,
            "content_type": self.content_type.value,
            "is_valid": self.is_valid,
            "validation_error": self.validation_error,
        }


class ImageToLaTeXConverter:
    """
    Main converter for transforming images to LaTeX code.

    Handles equations, tables, diagrams, and full documents.
    """

    # Prompts for different content types
    PROMPTS = {
        ContentType.EQUATION: """Analyze this image and convert any mathematical equations or formulas to LaTeX code.

Instructions:
- Extract all visible equations and mathematical notation
- Use proper LaTeX math syntax (e.g., \\frac, \\int, \\sum, etc.)
- For multiple equations, use appropriate environments (align, gather, etc.)
- Include any subscripts, superscripts, and special symbols
- Return ONLY the LaTeX code, no explanations

If the image contains multiple equations, separate them appropriately.""",

        ContentType.TABLE: """Analyze this image and convert any tables to LaTeX code.

Instructions:
- Extract the table structure with all rows and columns
- Use the tabular environment
- Use \\hline for horizontal lines and & for column separators
- Preserve alignment (l, c, r) based on the table layout
- Include any headers or special formatting
- Return ONLY the LaTeX code, no explanations

If the table has headers, make them bold using \\textbf{}.""",

        ContentType.DIAGRAM: """Analyze this image and describe how to recreate this diagram in LaTeX.

Instructions:
- If it's a simple geometric diagram, provide TikZ code
- If it's a complex image, provide a figure environment with description
- Include any labels, annotations, or text visible in the diagram
- Return ONLY the LaTeX code, no explanations

Prefer TikZ for simple diagrams (shapes, arrows, nodes). For complex diagrams, provide a figure environment with a detailed caption.""",

        ContentType.DOCUMENT: """Analyze this image and convert the entire document content to LaTeX.

Instructions:
- Extract all text, maintaining structure (sections, paragraphs, etc.)
- Convert any equations to LaTeX math mode
- Convert any tables to LaTeX tables
- Identify document structure (title, sections, subsections)
- Return ONLY the LaTeX code, no explanations

Maintain the original document hierarchy and formatting as closely as possible.""",
    }

    GENERAL_PROMPT = """Analyze this image containing scientific or mathematical content and convert it to LaTeX code.

Instructions:
- Identify the type of content (equation, table, diagram, or text)
- Convert the content to proper LaTeX syntax
- Use appropriate LaTeX environments and commands
- Be precise with mathematical notation, table structure, or text formatting
- Return ONLY the LaTeX code without any explanations or markdown formatting

Provide clean, compilable LaTeX code."""

    def __init__(
        self,
        vision_client: Optional[VisionClient] = None,
        validate_output: bool = True,
    ):
        """
        Initialize the converter.

        Args:
            vision_client: VisionClient instance (creates default if not provided)
            validate_output: Whether to validate LaTeX output
        """
        self.vision_client = vision_client or VisionClient()
        self.validate_output = validate_output
        self.image_handler = ImageHandler()

    def convert(
        self,
        image_path: Union[str, Path],
        content_type: Optional[ContentType] = None,
        auto_detect: bool = True,
    ) -> ConverterResult:
        """
        Convert an image to LaTeX code.

        Args:
            image_path: Path to the image file
            content_type: Type of content (if known), or None to auto-detect
            auto_detect: Whether to auto-detect content type from response

        Returns:
            ConverterResult with LaTeX code and metadata

        Raises:
            ConversionError: If conversion fails
        """
        image_path = Path(image_path)

        # Validate image
        try:
            self.image_handler.validate_image(image_path)
        except ImageHandlerError as e:
            raise ConversionError(f"Image validation failed: {e}") from e

        # Select prompt based on content type
        if content_type and content_type != ContentType.UNKNOWN:
            prompt = self.PROMPTS.get(content_type, self.GENERAL_PROMPT)
            logger.info(f"Using specific prompt for content type: {content_type}")
        else:
            prompt = self.GENERAL_PROMPT
            logger.info("Using general prompt for content detection")

        # Call vision model
        try:
            raw_response = self.vision_client.analyze_image(image_path, prompt)
            logger.info(f"Received response from vision model ({len(raw_response)} chars)")
        except VisionClientError as e:
            raise ConversionError(f"Vision model failed: {e}") from e

        # Extract LaTeX code
        latex_code = LaTeXFormatter.extract_latex_code(raw_response)

        # Detect content type if not specified or auto-detect enabled
        if auto_detect or content_type is None:
            detected_type = LaTeXFormatter.detect_content_type(latex_code)
            logger.info(f"Detected content type: {detected_type}")
        else:
            detected_type = content_type

        # Validate LaTeX
        is_valid = True
        validation_error = None
        if self.validate_output:
            is_valid, validation_error = LaTeXFormatter.validate_latex(latex_code)
            if not is_valid:
                logger.warning(f"LaTeX validation failed: {validation_error}")

        return ConverterResult(
            latex_code=latex_code,
            content_type=detected_type,
            raw_response=raw_response,
            is_valid=is_valid,
            validation_error=validation_error,
        )

    def convert_equation(self, image_path: Union[str, Path], inline: bool = False) -> str:
        """
        Convert an image containing equations to LaTeX.

        Args:
            image_path: Path to the image file
            inline: Whether to format as inline math

        Returns:
            Formatted LaTeX equation code
        """
        result = self.convert(image_path, content_type=ContentType.EQUATION)
        return LaTeXFormatter.wrap_equation(result.latex_code, inline=inline)

    def convert_table(
        self,
        image_path: Union[str, Path],
        caption: Optional[str] = None,
    ) -> str:
        """
        Convert an image containing a table to LaTeX.

        Args:
            image_path: Path to the image file
            caption: Optional table caption

        Returns:
            Formatted LaTeX table code
        """
        result = self.convert(image_path, content_type=ContentType.TABLE)
        return LaTeXFormatter.wrap_table(result.latex_code, caption=caption)

    def convert_to_document(
        self,
        image_path: Union[str, Path],
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> str:
        """
        Convert an image to a complete LaTeX document.

        Args:
            image_path: Path to the image file
            title: Optional document title
            author: Optional document author

        Returns:
            Complete LaTeX document
        """
        result = self.convert(image_path, content_type=ContentType.DOCUMENT)
        return LaTeXFormatter.create_full_document(
            result.latex_code,
            title=title,
            author=author,
        )
