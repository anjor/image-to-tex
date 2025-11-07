"""Tests for utility modules."""

import pytest
from image_to_tex.utils.latex_formatter import LaTeXFormatter, ContentType


class TestLaTeXFormatter:
    """Test cases for LaTeXFormatter."""

    def test_wrap_equation_inline(self):
        """Test wrapping equation as inline math."""
        result = LaTeXFormatter.wrap_equation("E = mc^2", inline=True)
        assert result == "$E = mc^2$"

    def test_wrap_equation_display(self):
        """Test wrapping equation as display math."""
        result = LaTeXFormatter.wrap_equation("E = mc^2", inline=False)
        assert "\\begin{equation}" in result
        assert "E = mc^2" in result
        assert "\\end{equation}" in result

    def test_detect_content_type_equation(self):
        """Test content type detection for equations."""
        latex_code = "\\begin{equation}\nE = mc^2\n\\end{equation}"
        content_type = LaTeXFormatter.detect_content_type(latex_code)
        assert content_type == ContentType.EQUATION

    def test_detect_content_type_table(self):
        """Test content type detection for tables."""
        latex_code = "\\begin{tabular}{cc}\na & b \\\\\nc & d\n\\end{tabular}"
        content_type = LaTeXFormatter.detect_content_type(latex_code)
        assert content_type == ContentType.TABLE

    def test_detect_content_type_document(self):
        """Test content type detection for documents."""
        latex_code = "\\documentclass{article}\n\\begin{document}\nContent\n\\end{document}"
        content_type = LaTeXFormatter.detect_content_type(latex_code)
        assert content_type == ContentType.DOCUMENT

    def test_validate_latex_balanced_braces(self):
        """Test LaTeX validation with balanced braces."""
        latex_code = "\\frac{a}{b}"
        is_valid, error = LaTeXFormatter.validate_latex(latex_code)
        assert is_valid is True
        assert error is None

    def test_validate_latex_unbalanced_braces(self):
        """Test LaTeX validation with unbalanced braces."""
        latex_code = "\\frac{a}{b"
        is_valid, error = LaTeXFormatter.validate_latex(latex_code)
        assert is_valid is False
        assert "braces" in error.lower()

    def test_validate_latex_unbalanced_environment(self):
        """Test LaTeX validation with unbalanced environment."""
        latex_code = "\\begin{equation}\nE = mc^2"
        is_valid, error = LaTeXFormatter.validate_latex(latex_code)
        assert is_valid is False
        assert "environment" in error.lower()

    def test_extract_latex_code_with_markdown(self):
        """Test extracting LaTeX from markdown code blocks."""
        text = "```latex\n\\frac{a}{b}\n```"
        result = LaTeXFormatter.extract_latex_code(text)
        assert "\\frac{a}{b}" in result
        assert "```" not in result

    def test_create_full_document(self):
        """Test creating a full LaTeX document."""
        content = "This is the content."
        doc = LaTeXFormatter.create_full_document(
            content, title="Test Title", author="Test Author"
        )
        assert "\\documentclass" in doc
        assert "\\begin{document}" in doc
        assert "\\end{document}" in doc
        assert "Test Title" in doc
        assert "Test Author" in doc
        assert content in doc

    def test_wrap_table_with_caption(self):
        """Test wrapping table with caption."""
        table_code = "\\begin{tabular}{cc}\na & b\n\\end{tabular}"
        result = LaTeXFormatter.wrap_table(table_code, caption="Test Table")
        assert "\\begin{table}" in result
        assert "\\caption{Test Table}" in result
        assert "\\end{table}" in result
        assert table_code in result
