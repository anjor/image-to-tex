"""Pydantic models for API request/response."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContentTypeEnum(str, Enum):
    """Content type for conversion."""

    EQUATION = "equation"
    TABLE = "table"
    DIAGRAM = "diagram"
    DOCUMENT = "document"
    AUTO = "auto"


class ConversionRequest(BaseModel):
    """Request model for image conversion."""

    content_type: ContentTypeEnum = Field(
        default=ContentTypeEnum.AUTO,
        description="Type of content to convert (auto-detect if not specified)",
    )
    inline: bool = Field(
        default=False,
        description="Format equations as inline math (only for equation type)",
    )
    caption: Optional[str] = Field(
        default=None,
        description="Table caption (only for table type)",
    )
    title: Optional[str] = Field(
        default=None,
        description="Document title (only for document type)",
    )
    author: Optional[str] = Field(
        default=None,
        description="Document author (only for document type)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_type": "equation",
                "inline": False,
            }
        }
    )


class ConversionResponse(BaseModel):
    """Response model for successful conversion."""

    latex_code: str = Field(
        description="Generated LaTeX code",
    )
    content_type: str = Field(
        description="Detected or specified content type",
    )
    is_valid: bool = Field(
        description="Whether the LaTeX passed validation",
    )
    validation_error: Optional[str] = Field(
        default=None,
        description="Validation error message if validation failed",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latex_code": "\\begin{equation}\\nE = mc^2\\n\\end{equation}",
                "content_type": "equation",
                "is_valid": True,
                "validation_error": None,
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(
        description="Error message",
    )
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Conversion failed",
                "detail": "Image file not found",
            }
        }
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(
        description="API status",
    )
    version: str = Field(
        description="API version",
    )
    models_available: dict = Field(
        description="Available vision models",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "models_available": {
                    "claude": True,
                    "openai": True,
                },
            }
        }
    )
