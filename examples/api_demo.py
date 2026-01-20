"""
Demonstration script for the FastAPI application.
Shows how to start the API server and make basic requests.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_config():
    """Demonstrate API configuration."""
    from src.api.config import api_config

    print("=" * 80)
    print("API Configuration")
    print("=" * 80)
    print(f"Title: {api_config.api_title}")
    print(f"Version: {api_config.api_version}")
    print(f"Host: {api_config.api_host}")
    print(f"Port: {api_config.api_port}")
    print(f"Database: {api_config.database_url}")
    print(f"Debug Mode: {api_config.api_debug}")
    print(f"CORS Origins: {api_config.cors_origins}")
    print(f"JWT Algorithm: {api_config.jwt_algorithm}")
    print(f"JWT Expire Minutes: {api_config.jwt_expire_minutes}")
    print(f"Pagination Default: {api_config.pagination_default_limit}")
    print()


def demo_jwt():
    """Demonstrate JWT token creation and validation."""
    from src.api.dependencies import create_access_token, decode_access_token

    print("=" * 80)
    print("JWT Token Demo")
    print("=" * 80)

    # Create token
    user_data = {"sub": "user123", "role": "admin", "email": "admin@example.com"}
    token = create_access_token(user_data)

    print(f"Created Token: {token[:50]}...")
    print()

    # Decode token
    decoded = decode_access_token(token)
    print("Decoded Token:")
    for key, value in decoded.items():
        if key != 'exp':
            print(f"  {key}: {value}")

    print()


def demo_app_creation():
    """Demonstrate FastAPI app creation."""
    from src.api.main import create_app

    print("=" * 80)
    print("FastAPI Application")
    print("=" * 80)

    app = create_app()

    print(f"App Title: {app.title}")
    print(f"App Version: {app.version}")
    print(f"Number of Routes: {len(app.routes)}")
    print()

    print("Available Routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"  {methods:20s} {route.path}")

    print()


def demo_test_client():
    """Demonstrate using the test client."""
    from fastapi.testclient import TestClient
    from src.api.main import create_app

    print("=" * 80)
    print("Test Client Demo")
    print("=" * 80)

    app = create_app()
    client = TestClient(app)

    # Test root endpoint
    print("Testing GET /")
    response = client.get("/")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
    print()

    # Test health endpoint
    print("Testing GET /health")
    response = client.get("/health")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
    print()

    # Test OpenAPI schema
    print("Testing GET /openapi.json")
    response = client.get("/openapi.json")
    print(f"  Status Code: {response.status_code}")
    schema = response.json()
    print(f"  OpenAPI Version: {schema.get('openapi')}")
    print(f"  API Title: {schema.get('info', {}).get('title')}")
    print(f"  Number of Paths: {len(schema.get('paths', {}))}")
    print()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("FastAPI Meal Planner - API Core Demonstration")
    print("=" * 80 + "\n")

    try:
        demo_config()
        demo_jwt()
        demo_app_creation()
        demo_test_client()

        print("=" * 80)
        print("All Demonstrations Completed Successfully!")
        print("=" * 80)
        print()
        print("To start the API server, run:")
        print("  python -m src.api.main")
        print()
        print("Or use uvicorn:")
        print("  uvicorn src.api.main:app --reload")
        print()
        print("Then visit:")
        print("  http://localhost:8000 - API health check")
        print("  http://localhost:8000/docs - Swagger UI documentation")
        print("  http://localhost:8000/redoc - ReDoc documentation")
        print()

    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
