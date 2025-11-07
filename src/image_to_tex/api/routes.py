"""FastAPI routes for image-to-tex API."""

import logging
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.converter import ConversionError, ImageToLaTeXConverter
from ..core.vision_client import NoAPIKeyError, VisionClient
from ..utils.image_handler import ImageHandlerError
from ..utils.latex_formatter import ContentType
from .models import (
    ContentTypeEnum,
    ConversionResponse,
    ErrorResponse,
    HealthResponse,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Image-to-LaTeX API",
    description="Convert images of scientific work to LaTeX code using vision AI models",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global converter instance
converter: ImageToLaTeXConverter = None


@app.on_event("startup")
async def startup_event():
    """Initialize converter on startup."""
    global converter
    try:
        converter = ImageToLaTeXConverter()
        logger.info("Image-to-LaTeX API started successfully")
    except NoAPIKeyError as e:
        logger.error(f"Failed to initialize: {e}")
        logger.error("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Image-to-LaTeX API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns API status and available models.
    """
    if converter is None:
        raise HTTPException(
            status_code=503,
            detail="API not initialized. Check API keys configuration.",
        )

    # Check which models are available
    models_available = {
        "claude": converter.vision_client.anthropic_client is not None,
        "openai": converter.vision_client.openai_client is not None,
    }

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        models_available=models_available,
    )


@app.post(
    "/convert",
    response_model=ConversionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Conversion failed"},
    },
    tags=["Conversion"],
)
async def convert_image(
    file: UploadFile = File(..., description="Image file to convert"),
    content_type: ContentTypeEnum = Form(
        default=ContentTypeEnum.AUTO,
        description="Type of content (auto-detect if not specified)",
    ),
    inline: bool = Form(
        default=False,
        description="Format equations as inline math (equation type only)",
    ),
    caption: str = Form(
        default=None,
        description="Table caption (table type only)",
    ),
    title: str = Form(
        default=None,
        description="Document title (document type only)",
    ),
    author: str = Form(
        default=None,
        description="Document author (document type only)",
    ),
):
    """
    Convert an uploaded image to LaTeX code.

    Upload an image file and receive LaTeX code for the content.
    Supports equations, tables, diagrams, and full documents.

    Example:
        curl -X POST "http://localhost:8000/convert" \\
             -F "file=@equation.png" \\
             -F "content_type=equation"
    """
    if converter is None:
        raise HTTPException(
            status_code=503,
            detail="API not initialized. Check API keys configuration.",
        )

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Must be an image.",
        )

    temp_file_path = None

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)

        logger.info(f"Processing image: {file.filename} ({len(content)} bytes)")

        # Map ContentTypeEnum to internal ContentType
        content_type_map = {
            ContentTypeEnum.EQUATION: ContentType.EQUATION,
            ContentTypeEnum.TABLE: ContentType.TABLE,
            ContentTypeEnum.DIAGRAM: ContentType.DIAGRAM,
            ContentTypeEnum.DOCUMENT: ContentType.DOCUMENT,
            ContentTypeEnum.AUTO: None,
        }
        internal_content_type = content_type_map[content_type]

        # Convert based on type
        if content_type == ContentTypeEnum.EQUATION:
            latex_code = converter.convert_equation(temp_file_path, inline=inline)
            result_content_type = "equation"
            is_valid = True
            validation_error = None
        elif content_type == ContentTypeEnum.TABLE:
            latex_code = converter.convert_table(temp_file_path, caption=caption)
            result_content_type = "table"
            is_valid = True
            validation_error = None
        elif content_type == ContentTypeEnum.DOCUMENT:
            latex_code = converter.convert_to_document(
                temp_file_path, title=title, author=author
            )
            result_content_type = "document"
            is_valid = True
            validation_error = None
        else:
            # Auto-detect
            result = converter.convert(temp_file_path, content_type=internal_content_type)
            latex_code = result.latex_code
            result_content_type = result.content_type.value
            is_valid = result.is_valid
            validation_error = result.validation_error

        logger.info(f"Conversion successful: {result_content_type}")

        return ConversionResponse(
            latex_code=latex_code,
            content_type=result_content_type,
            is_valid=is_valid,
            validation_error=validation_error,
        )

    except ImageHandlerError as e:
        logger.error(f"Image validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConversionError as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        # Clean up temporary file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
