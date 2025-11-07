"""Basic usage examples for image-to-tex."""

from pathlib import Path

from image_to_tex import convert_equation, convert_image, convert_table


def example_simple_conversion():
    """Simple image conversion with auto-detection."""
    print("=== Simple Conversion Example ===")

    # This would convert an actual image file
    # result = convert_image("path/to/equation.png")
    # print(f"LaTeX code: {result.latex_code}")
    # print(f"Content type: {result.content_type}")
    # print(f"Valid: {result.is_valid}")

    print("Example: result = convert_image('equation.png')")
    print("Output would include LaTeX code and metadata")


def example_equation_conversion():
    """Convert an equation image to LaTeX."""
    print("\n=== Equation Conversion Example ===")

    # Convert to display equation
    # latex_display = convert_equation("path/to/formula.png", inline=False)
    # print(f"Display equation: {latex_display}")

    # Convert to inline equation
    # latex_inline = convert_equation("path/to/formula.png", inline=True)
    # print(f"Inline equation: {latex_inline}")

    print("Example: latex = convert_equation('formula.png', inline=True)")
    print("Output: $E = mc^2$")


def example_table_conversion():
    """Convert a table image to LaTeX."""
    print("\n=== Table Conversion Example ===")

    # Convert table with caption
    # latex = convert_table("path/to/table.png", caption="Experimental Results")
    # print(f"Table LaTeX: {latex}")

    print("Example: latex = convert_table('table.png', caption='Results')")
    print("Output: \\begin{table}...\\end{table}")


def example_batch_processing():
    """Process multiple images."""
    print("\n=== Batch Processing Example ===")

    # image_paths = ["eq1.png", "eq2.png", "table1.png"]
    # results = []
    #
    # for path in image_paths:
    #     try:
    #         result = convert_image(path)
    #         results.append(result)
    #         print(f"Converted {path}: {result.content_type}")
    #     except Exception as e:
    #         print(f"Failed to convert {path}: {e}")

    print("Example: Loop through multiple images and convert each")
    print("Handles errors gracefully per image")


def example_save_to_file():
    """Convert and save to LaTeX file."""
    print("\n=== Save to File Example ===")

    # result = convert_image("path/to/equation.png")
    #
    # output_path = Path("output.tex")
    # output_path.write_text(result.latex_code)
    # print(f"LaTeX saved to {output_path}")

    print("Example: Convert and save result to .tex file")
    print("Use Path.write_text() to save the LaTeX code")


if __name__ == "__main__":
    print("Image-to-LaTeX Basic Usage Examples")
    print("=" * 50)
    print("\nNote: These examples show the API usage.")
    print("To run them, provide actual image paths and set API keys.\n")

    example_simple_conversion()
    example_equation_conversion()
    example_table_conversion()
    example_batch_processing()
    example_save_to_file()

    print("\n" + "=" * 50)
    print("See README.md for more information and setup instructions.")
