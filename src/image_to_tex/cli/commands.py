"""CLI commands for image-to-tex."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from ..core.converter import ConversionError, ImageToLaTeXConverter
from ..core.vision_client import NoAPIKeyError
from ..utils.latex_formatter import ContentType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="image-to-tex")
def cli():
    """
    Image-to-LaTeX converter using vision AI models.

    Convert images of scientific work (equations, tables, diagrams) to LaTeX code.
    """
    pass


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path (default: print to stdout)",
)
@click.option(
    "-t", "--type",
    type=click.Choice(["equation", "table", "diagram", "document", "auto"], case_sensitive=False),
    default="auto",
    help="Type of content to convert (default: auto-detect)",
)
@click.option(
    "--inline",
    is_flag=True,
    help="Format equations as inline math (only for equation type)",
)
@click.option(
    "--caption",
    type=str,
    help="Table caption (only for table type)",
)
@click.option(
    "--title",
    type=str,
    help="Document title (only for document type)",
)
@click.option(
    "--author",
    type=str,
    help="Document author (only for document type)",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def convert(
    image_path: str,
    output: Optional[str],
    type: str,
    inline: bool,
    caption: Optional[str],
    title: Optional[str],
    author: Optional[str],
    verbose: bool,
):
    """
    Convert an image to LaTeX code.

    Example usage:

    \b
    # Auto-detect content type
    image-to-tex convert equation.png

    \b
    # Convert equation and save to file
    image-to-tex convert equation.png -o output.tex

    \b
    # Convert table with caption
    image-to-tex convert table.png --type table --caption "Results"

    \b
    # Convert to full document
    image-to-tex convert page.png --type document --title "My Paper"
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    try:
        # Initialize converter
        converter = ImageToLaTeXConverter()

        # Map CLI type to ContentType enum
        content_type_map = {
            "equation": ContentType.EQUATION,
            "table": ContentType.TABLE,
            "diagram": ContentType.DIAGRAM,
            "document": ContentType.DOCUMENT,
            "auto": None,
        }
        content_type = content_type_map[type]

        # Convert based on type
        if type == "equation":
            latex_code = converter.convert_equation(image_path, inline=inline)
        elif type == "table":
            latex_code = converter.convert_table(image_path, caption=caption)
        elif type == "document":
            latex_code = converter.convert_to_document(
                image_path, title=title, author=author
            )
        else:
            # Auto-detect
            result = converter.convert(image_path, content_type=content_type)
            latex_code = result.latex_code

            if verbose:
                click.echo(f"Detected content type: {result.content_type.value}", err=True)
                if not result.is_valid:
                    click.echo(f"Warning: {result.validation_error}", err=True)

        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(latex_code)
            click.echo(f"LaTeX code saved to: {output_path}", err=True)
        else:
            click.echo(latex_code)

    except NoAPIKeyError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.", err=True)
        click.echo("See .env.example for configuration options.", err=True)
        sys.exit(1)
    except ConversionError as e:
        click.echo(f"Conversion error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
def info(image_path: str):
    """
    Display information about an image file.

    Shows image format, dimensions, and file size.
    """
    try:
        from ..utils.image_handler import ImageHandler

        handler = ImageHandler()
        handler.validate_image(image_path)
        image_info = handler.get_image_info(image_path)

        click.echo("Image Information:")
        click.echo(f"  Path: {image_info['path']}")
        click.echo(f"  Format: {image_info['format']}")
        click.echo(f"  Mode: {image_info['mode']}")
        click.echo(f"  Dimensions: {image_info['width']}x{image_info['height']}")
        click.echo(f"  File size: {image_info['file_size_mb']:.2f} MB")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Display version information."""
    click.echo("image-to-tex version 0.1.0")
    click.echo("Convert images to LaTeX using vision AI models")


if __name__ == "__main__":
    cli()
