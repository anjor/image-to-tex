"""Example API client for the image-to-tex REST API."""

import httpx
from pathlib import Path


class ImageToLaTeXClient:
    """Simple client for the image-to-tex API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)

    def health_check(self) -> dict:
        """Check API health and available models."""
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()

    def convert_image(
        self,
        image_path: str,
        content_type: str = "auto",
        inline: bool = False,
        caption: str = None,
        title: str = None,
        author: str = None,
    ) -> dict:
        """
        Convert an image to LaTeX.

        Args:
            image_path: Path to the image file
            content_type: Type of content (equation, table, diagram, document, auto)
            inline: Format equations as inline math
            caption: Table caption
            title: Document title
            author: Document author

        Returns:
            Dictionary with conversion result
        """
        image_path = Path(image_path)

        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/png")}
            data = {"content_type": content_type}

            if inline:
                data["inline"] = "true"
            if caption:
                data["caption"] = caption
            if title:
                data["title"] = title
            if author:
                data["author"] = author

            response = self.client.post("/convert", files=files, data=data)
            response.raise_for_status()
            return response.json()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def example_basic_api_usage():
    """Basic API usage example."""
    print("=== Basic API Usage Example ===")

    # with ImageToLaTeXClient() as client:
    #     # Check health
    #     health = client.health_check()
    #     print(f"API Status: {health['status']}")
    #     print(f"Models: {health['models_available']}")
    #
    #     # Convert image
    #     result = client.convert_image("equation.png", content_type="equation")
    #     print(f"LaTeX: {result['latex_code']}")
    #     print(f"Type: {result['content_type']}")
    #     print(f"Valid: {result['is_valid']}")

    print("Example: Use context manager for API client")
    print("Automatically handles connection cleanup")


def example_batch_api_processing():
    """Process multiple images via API."""
    print("\n=== Batch API Processing Example ===")

    # images = ["eq1.png", "eq2.png", "table1.png"]
    #
    # with ImageToLaTeXClient() as client:
    #     for image_path in images:
    #         try:
    #             result = client.convert_image(image_path)
    #             print(f"✓ Converted {image_path}")
    #
    #             # Save to file
    #             output_path = Path(image_path).with_suffix(".tex")
    #             output_path.write_text(result["latex_code"])
    #
    #         except httpx.HTTPError as e:
    #             print(f"✗ Failed to convert {image_path}: {e}")

    print("Example: Process multiple images in batch")
    print("Handles errors per image, saves results to .tex files")


def example_async_api_client():
    """Async API client example."""
    print("\n=== Async API Client Example ===")

    import asyncio

    async def convert_async(image_paths: list[str]):
        """Convert multiple images asynchronously."""
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:
            tasks = []

            for image_path in image_paths:
                # Create async task for each image
                with open(image_path, "rb") as f:
                    files = {"file": (Path(image_path).name, f.read(), "image/png")}
                    data = {"content_type": "auto"}
                    task = client.post("/convert", files=files, data=data)
                    tasks.append(task)

            # Wait for all conversions
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for image_path, response in zip(image_paths, responses):
                if isinstance(response, Exception):
                    print(f"✗ {image_path}: {response}")
                else:
                    result = response.json()
                    print(f"✓ {image_path}: {result['content_type']}")

    # To run:
    # asyncio.run(convert_async(["eq1.png", "eq2.png"]))

    print("Example: Process images concurrently with async/await")
    print("Faster for large batches with network latency")


def example_error_handling_api():
    """API error handling example."""
    print("\n=== API Error Handling Example ===")

    # with ImageToLaTeXClient() as client:
    #     try:
    #         result = client.convert_image("image.png")
    #     except httpx.HTTPStatusError as e:
    #         if e.response.status_code == 400:
    #             print(f"Bad request: {e.response.json()}")
    #         elif e.response.status_code == 500:
    #             print(f"Server error: {e.response.json()}")
    #         else:
    #             print(f"HTTP error: {e}")
    #     except httpx.RequestError as e:
    #         print(f"Connection error: {e}")

    print("Example: Handle different HTTP error types")
    print("400: Bad request (invalid image)")
    print("500: Server error (conversion failed)")
    print("Connection errors: Network issues")


def example_curl_commands():
    """Show equivalent curl commands."""
    print("\n=== Equivalent curl Commands ===")

    print("Health check:")
    print('curl http://localhost:8000/health')

    print("\nConvert image:")
    print('curl -X POST "http://localhost:8000/convert" \\')
    print('  -F "file=@equation.png" \\')
    print('  -F "content_type=equation"')

    print("\nConvert table with caption:")
    print('curl -X POST "http://localhost:8000/convert" \\')
    print('  -F "file=@table.png" \\')
    print('  -F "content_type=table" \\')
    print('  -F "caption=Experimental Results"')


if __name__ == "__main__":
    print("Image-to-LaTeX API Client Examples")
    print("=" * 50)
    print("\nNote: Start the API server first:")
    print("  uvicorn image_to_tex.api.routes:app --reload\n")

    example_basic_api_usage()
    example_batch_api_processing()
    example_async_api_client()
    example_error_handling_api()
    example_curl_commands()

    print("\n" + "=" * 50)
    print("Visit http://localhost:8000/docs for interactive API documentation")
