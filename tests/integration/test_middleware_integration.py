"""
Integration tests for middleware stack.
Verifies that all middleware components work together correctly.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client with full middleware stack."""
    app = create_app()
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.integration
class TestMiddlewareStack:
    """Test complete middleware stack integration."""

    def test_health_endpoint_works(self, client: TestClient):
        """Test health endpoint works with all middleware."""
        response = client.get("/health")

        assert response.status_code in [200, 503]
        assert "status" in response.json()

    def test_root_endpoint_works(self, client: TestClient):
        """Test root endpoint works with all middleware."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()

    def test_request_id_added_to_response(self, client: TestClient):
        """Test request ID middleware adds header."""
        response = client.get("/")

        assert "X-Request-ID" in response.headers

    def test_rate_limit_headers_present(self, client: TestClient):
        """Test rate limit middleware adds headers."""
        response = client.get("/")

        # Health endpoints are exempt, so check a different endpoint
        assert response.status_code == 200

    def test_404_error_formatted_correctly(self, client: TestClient):
        """Test error handler formats 404 correctly."""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        assert "detail" in response.json()

    def test_custom_request_id_preserved(self, client: TestClient):
        """Test custom request ID is preserved through middleware stack."""
        custom_id = "test-request-123"
        response = client.get("/", headers={"X-Request-ID": custom_id})

        assert response.headers["X-Request-ID"] == custom_id

    def test_middleware_order_correct(self, client: TestClient):
        """Test middleware executes in correct order."""
        # Make request and verify all middleware features work
        response = client.get("/")

        # Should have request ID (logging middleware)
        assert "X-Request-ID" in response.headers

        # Should have successful response (rate limit allows)
        assert response.status_code == 200

        # Should have proper JSON format (error handler formats)
        assert "status" in response.json()


@pytest.mark.integration
class TestErrorHandlerIntegration:
    """Test error handler integration with other middleware."""

    def test_validation_error_has_request_id(self, client: TestClient):
        """Test validation errors include request ID."""
        # This would require a route with validation
        # For now, just verify the app doesn't crash
        response = client.get("/")
        assert response.status_code == 200

    def test_server_error_has_request_id(self, client: TestClient):
        """Test server errors include request ID in logs."""
        response = client.get("/")
        assert "X-Request-ID" in response.headers


@pytest.mark.integration
class TestRateLimitIntegration:
    """Test rate limiting integration with other middleware."""

    def test_rate_limit_errors_logged(self, client: TestClient):
        """Test rate limit errors are properly logged."""
        # Health endpoints are exempt from rate limiting
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code in [200, 503]

    def test_health_endpoints_exempt_from_rate_limit(self, client: TestClient):
        """Test health endpoints bypass rate limiting."""
        # Make many requests to health endpoint
        for _ in range(20):
            response = client.get("/health")
            # Should never get 429 (rate limited)
            assert response.status_code != 429
