"""Tests for API module."""

import pytest
from fastapi.testclient import TestClient

# Note: These are basic structural tests. Full integration tests would require
# mock images and API keys.


def test_api_import():
    """Test that API modules can be imported."""
    from image_to_tex.api import models, routes

    assert models is not None
    assert routes is not None


def test_api_models():
    """Test API model definitions."""
    from image_to_tex.api.models import (
        ConversionRequest,
        ConversionResponse,
        ErrorResponse,
        HealthResponse,
    )

    # Test ConversionRequest
    request = ConversionRequest(content_type="equation")
    assert request.content_type == "equation"

    # Test ConversionResponse
    response = ConversionResponse(
        latex_code="E=mc^2",
        content_type="equation",
        is_valid=True,
        validation_error=None,
    )
    assert response.latex_code == "E=mc^2"

    # Test ErrorResponse
    error = ErrorResponse(error="Test error", detail="Detail")
    assert error.error == "Test error"

    # Test HealthResponse
    health = HealthResponse(
        status="healthy",
        version="0.1.0",
        models_available={"claude": True, "openai": False},
    )
    assert health.status == "healthy"


def test_api_app_creation():
    """Test that FastAPI app can be created."""
    from image_to_tex.api.routes import app

    assert app is not None
    assert app.title == "Image-to-LaTeX API"


@pytest.mark.asyncio
async def test_api_root_endpoint():
    """Test root endpoint."""
    from image_to_tex.api.routes import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
