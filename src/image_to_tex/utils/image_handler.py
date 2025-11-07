"""Image handling and preprocessing utilities."""

import logging
from pathlib import Path
from typing import Union

from PIL import Image

logger = logging.getLogger(__name__)


class ImageHandlerError(Exception):
    """Base exception for image handler errors."""
    pass


class ImageHandler:
    """Handle image preprocessing and validation."""

    SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "GIF", "WEBP", "BMP", "TIFF"}
    MAX_SIZE_MB = 20  # Maximum image size in MB

    @staticmethod
    def validate_image(image_path: Union[str, Path]) -> bool:
        """
        Validate that an image file is readable and supported.

        Args:
            image_path: Path to the image file

        Returns:
            True if valid

        Raises:
            ImageHandlerError: If validation fails
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise ImageHandlerError(f"Image file not found: {image_path}")

        if not image_path.is_file():
            raise ImageHandlerError(f"Path is not a file: {image_path}")

        # Check file size
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > ImageHandler.MAX_SIZE_MB:
            raise ImageHandlerError(
                f"Image file too large: {file_size_mb:.2f}MB "
                f"(max: {ImageHandler.MAX_SIZE_MB}MB)"
            )

        # Try to open and validate format
        try:
            with Image.open(image_path) as img:
                if img.format not in ImageHandler.SUPPORTED_FORMATS:
                    raise ImageHandlerError(
                        f"Unsupported image format: {img.format}. "
                        f"Supported: {', '.join(ImageHandler.SUPPORTED_FORMATS)}"
                    )
                logger.info(
                    f"Validated image: {image_path.name} "
                    f"({img.format}, {img.size[0]}x{img.size[1]})"
                )
        except Exception as e:
            if isinstance(e, ImageHandlerError):
                raise
            raise ImageHandlerError(f"Failed to open image: {e}") from e

        return True

    @staticmethod
    def get_image_info(image_path: Union[str, Path]) -> dict:
        """
        Get metadata about an image.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with image metadata
        """
        image_path = Path(image_path)

        with Image.open(image_path) as img:
            return {
                "path": str(image_path),
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.size[0],
                "height": img.size[1],
                "file_size_mb": image_path.stat().st_size / (1024 * 1024),
            }

    @staticmethod
    def preprocess_image(
        image_path: Union[str, Path],
        max_dimension: int = 2048,
    ) -> Path:
        """
        Preprocess image for optimal API usage.

        Resizes large images while maintaining aspect ratio.

        Args:
            image_path: Path to the image file
            max_dimension: Maximum width or height in pixels

        Returns:
            Path to the preprocessed image (may be same as input)
        """
        image_path = Path(image_path)

        with Image.open(image_path) as img:
            # Check if resizing is needed
            if max(img.size) <= max_dimension:
                logger.info("Image size acceptable, no preprocessing needed")
                return image_path

            # Calculate new size maintaining aspect ratio
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)

            logger.info(
                f"Resizing image from {img.size} to {new_size} "
                f"(max_dimension={max_dimension})"
            )

            # Resize
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save to temporary file
            output_path = image_path.parent / f"{image_path.stem}_processed{image_path.suffix}"
            img_resized.save(output_path)

            return output_path
