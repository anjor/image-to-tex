"""LaTeX formatting and validation utilities."""

import logging
import re
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Types of scientific content that can be converted."""

    EQUATION = "equation"
    TABLE = "table"
    DIAGRAM = "diagram"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class LaTeXFormatter:
    """Format and validate LaTeX output."""

    DOCUMENT_PACKAGES = [
        r"\usepackage{amsmath}",
        r"\usepackage{amssymb}",
        r"\usepackage{amsfonts}",
        r"\usepackage{graphicx}",
        r"\usepackage{booktabs}",
        r"\usepackage{tikz}",
    ]

    @staticmethod
    def wrap_equation(latex_code: str, inline: bool = False) -> str:
        """
        Wrap LaTeX code in appropriate math environment.

        Args:
            latex_code: Raw LaTeX math code
            inline: Whether to use inline ($...$) or display math

        Returns:
            Properly wrapped LaTeX equation
        """
        # Clean up any existing delimiters
        latex_code = latex_code.strip()
        for delim in [r"\[", r"\]", "$$", "$"]:
            latex_code = latex_code.replace(delim, "")
        latex_code = latex_code.strip()

        if inline:
            return f"${latex_code}$"
        else:
            # Check if it's a multi-line equation
            if "\\\\" in latex_code or "align" in latex_code.lower():
                # Use align environment for multi-line
                if not latex_code.startswith(r"\begin{align"):
                    return f"\\begin{{align}}\n{latex_code}\n\\end{{align}}"
                return latex_code
            else:
                # Use equation environment for single-line
                if not latex_code.startswith(r"\begin{equation"):
                    return f"\\begin{{equation}}\n{latex_code}\n\\end{{equation}}"
                return latex_code

    @staticmethod
    def wrap_table(latex_code: str, caption: Optional[str] = None) -> str:
        """
        Wrap LaTeX table code in proper environment.

        Args:
            latex_code: Raw LaTeX table code
            caption: Optional table caption

        Returns:
            Properly wrapped LaTeX table
        """
        latex_code = latex_code.strip()

        # If already wrapped in table environment, return as-is
        if latex_code.startswith(r"\begin{table"):
            return latex_code

        # Build table wrapper
        result = "\\begin{table}[htbp]\n\\centering\n"

        if caption:
            result += f"\\caption{{{caption}}}\n"

        # Add the table code if not already wrapped in tabular
        if not latex_code.startswith(r"\begin{tabular"):
            result += "\\begin{tabular}{c}\n"  # Default to single centered column
            result += latex_code + "\n"
            result += "\\end{tabular}\n"
        else:
            result += latex_code + "\n"

        result += "\\end{table}"

        return result

    @staticmethod
    def create_full_document(
        latex_content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        document_class: str = "article",
    ) -> str:
        """
        Create a complete LaTeX document.

        Args:
            latex_content: Main document content
            title: Document title
            author: Document author
            document_class: LaTeX document class

        Returns:
            Complete LaTeX document
        """
        doc = f"\\documentclass{{{document_class}}}\n\n"

        # Add packages
        for package in LaTeXFormatter.DOCUMENT_PACKAGES:
            doc += package + "\n"

        doc += "\n\\begin{document}\n\n"

        # Add title if provided
        if title:
            doc += f"\\title{{{title}}}\n"
            if author:
                doc += f"\\author{{{author}}}\n"
            doc += "\\maketitle\n\n"

        # Add content
        doc += latex_content + "\n\n"

        doc += "\\end{document}\n"

        return doc

    @staticmethod
    def extract_latex_code(text: str) -> str:
        """
        Extract LaTeX code from model response.

        Handles common markdown code fences and LaTeX delimiters.

        Args:
            text: Raw model response text

        Returns:
            Extracted LaTeX code
        """
        # Remove markdown code fences
        text = re.sub(r"```latex\n", "", text)
        text = re.sub(r"```tex\n", "", text)
        text = re.sub(r"```\n", "", text)
        text = re.sub(r"```", "", text)

        # Remove common explanatory text patterns
        lines = text.split("\n")
        latex_lines = []
        started = False

        for line in lines:
            line_lower = line.lower().strip()

            # Skip explanatory lines
            if not started:
                if any(skip in line_lower for skip in [
                    "here is", "here's", "the latex", "this is",
                    "i've converted", "converted to", "latex code:",
                    "explanation:", "note:"
                ]):
                    continue

            # Start capturing at first LaTeX-like line
            if line.strip().startswith("\\") or line.strip().startswith("$"):
                started = True

            if started:
                latex_lines.append(line)

        result = "\n".join(latex_lines).strip()

        # If no LaTeX found, return original
        if not result:
            return text.strip()

        return result

    @staticmethod
    def detect_content_type(latex_code: str) -> ContentType:
        """
        Detect the type of content in LaTeX code.

        Args:
            latex_code: LaTeX code to analyze

        Returns:
            Detected content type
        """
        latex_lower = latex_code.lower()

        # Check for document structure
        if "\\documentclass" in latex_lower or "\\maketitle" in latex_lower:
            return ContentType.DOCUMENT

        # Check for tables
        if "\\begin{table" in latex_lower or "\\begin{tabular" in latex_lower:
            return ContentType.TABLE

        # Check for diagrams/figures
        if any(keyword in latex_lower for keyword in [
            "\\begin{tikz", "\\begin{figure", "\\includegraphics"
        ]):
            return ContentType.DIAGRAM

        # Check for equations
        if any(keyword in latex_lower for keyword in [
            "\\begin{equation", "\\begin{align", "\\[", "$",
            "\\frac", "\\int", "\\sum", "\\alpha"
        ]):
            return ContentType.EQUATION

        return ContentType.UNKNOWN

    @staticmethod
    def validate_latex(latex_code: str) -> tuple[bool, Optional[str]]:
        """
        Perform basic validation of LaTeX code.

        Args:
            latex_code: LaTeX code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for balanced braces
        if latex_code.count("{") != latex_code.count("}"):
            return False, "Unbalanced braces: {} count mismatch"

        # Check for balanced brackets
        if latex_code.count("[") != latex_code.count("]"):
            return False, "Unbalanced brackets: [] count mismatch"

        # Check for balanced environments
        begins = re.findall(r"\\begin\{(\w+)\}", latex_code)
        ends = re.findall(r"\\end\{(\w+)\}", latex_code)

        if len(begins) != len(ends):
            return False, "Unbalanced environments: \\begin{} and \\end{} count mismatch"

        # Check each environment is properly closed
        for env in begins:
            if env not in ends:
                return False, f"Environment '{env}' opened but not closed"

        logger.info("LaTeX validation passed")
        return True, None
