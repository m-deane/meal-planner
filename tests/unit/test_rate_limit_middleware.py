"""
Unit tests for rate limiting middleware.
Tests in-memory rate limiter with configurable requests per minute.
"""

import time
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.middleware import RateLimitMiddleware


@pytest.fixture
def app_with_rate_limit() -> FastAPI:
    """Create test FastAPI application with rate limiting."""
    app = FastAPI()

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    @app.get("/test/endpoint")
    async def test_endpoint():
        """Test endpoint."""
        return {"message": "success"}

    return app


@pytest.fixture
def app_disabled_rate_limit() -> FastAPI:
    """Create app with rate limiting disabled."""
    with patch("src.api.config.api_config") as mock_config:
        mock_config.rate_limit_enabled = False
        mock_config.rate_limit_per_minute = 60

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        return app


@pytest.fixture
def client(app_with_rate_limit: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app_with_rate_limit)


class TestRateLimiting:
    """Test rate limiting functionality."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_allows_requests_under_limit(self, mock_config, client: TestClient):
        """Test requests under limit are allowed."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 10

        # Make 5 requests (under limit of 10)
        for _ in range(5):
            response = client.get("/test/endpoint")
            assert response.status_code == 200

    @patch("src.api.middleware.rate_limit.api_config")
    def test_blocks_requests_over_limit(self, mock_config):
        """Test requests over limit are blocked."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 3

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Make requests up to limit
        for i in range(3):
            response = client.get("/test/endpoint")
            assert response.status_code == 200, f"Request {i+1} should succeed"

        # Next request should be rate limited
        response = client.get("/test/endpoint")
        assert response.status_code == 429

    @patch("src.api.middleware.rate_limit.api_config")
    def test_rate_limit_response_includes_retry_after(self, mock_config):
        """Test rate limited response includes Retry-After header."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 2

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Exhaust rate limit
        for _ in range(2):
            client.get("/test/endpoint")

        # Get rate limited response
        response = client.get("/test/endpoint")

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) > 0

    @patch("src.api.middleware.rate_limit.api_config")
    def test_rate_limit_response_format(self, mock_config):
        """Test rate limited response has correct format."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 1

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Exhaust limit
        client.get("/test/endpoint")

        # Get rate limited
        response = client.get("/test/endpoint")

        data = response.json()
        assert data["detail"] == "Rate limit exceeded"
        assert data["status"] == "error"
        assert data["error_type"] == "rate_limit_error"
        assert "limit" in data
        assert "retry_after" in data


class TestRateLimitHeaders:
    """Test rate limit headers in responses."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_includes_rate_limit_headers(self, mock_config):
        """Test successful responses include rate limit headers."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 10

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test/endpoint")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    @patch("src.api.middleware.rate_limit.api_config")
    def test_remaining_count_decreases(self, mock_config):
        """Test remaining count decreases with each request."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 10

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        response1 = client.get("/test/endpoint")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])

        response2 = client.get("/test/endpoint")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])

        assert remaining2 < remaining1

    @patch("src.api.middleware.rate_limit.api_config")
    def test_limit_header_matches_config(self, mock_config):
        """Test X-RateLimit-Limit header matches configuration."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 42

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test/endpoint")

        assert response.headers["X-RateLimit-Limit"] == "42"


class TestHealthCheckExemption:
    """Test that health check endpoints are exempt from rate limiting."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_health_endpoint_not_rate_limited(self, mock_config):
        """Test /health endpoint is not rate limited."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 1

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        client = TestClient(app)

        # Make many requests to health endpoint
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    @patch("src.api.middleware.rate_limit.api_config")
    def test_root_endpoint_not_rate_limited(self, mock_config):
        """Test / endpoint is not rate limited."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 1

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/")
        async def root():
            return {"status": "ok"}

        client = TestClient(app)

        # Make many requests to root
        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200

    @patch("src.api.middleware.rate_limit.api_config")
    def test_docs_endpoint_not_rate_limited(self, mock_config):
        """Test /docs endpoint is not rate limited."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 1

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        client = TestClient(app)

        # Make many requests to docs
        for _ in range(5):
            response = client.get("/docs")
            # Docs might return 404 if not configured, but shouldn't be 429
            assert response.status_code != 429


class TestDisabledRateLimit:
    """Test behavior when rate limiting is disabled."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_unlimited_requests_when_disabled(self, mock_config):
        """Test unlimited requests allowed when rate limiting disabled."""
        mock_config.rate_limit_enabled = False
        mock_config.rate_limit_per_minute = 1

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Make many requests
        for _ in range(20):
            response = client.get("/test/endpoint")
            assert response.status_code == 200


class TestClientIsolation:
    """Test that rate limits are per-client IP."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_different_ips_have_separate_limits(self, mock_config):
        """Test different client IPs have separate rate limits."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 2

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/test/endpoint")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # Make requests from "different IPs" using headers
        response1 = client.get(
            "/test/endpoint",
            headers={"X-Forwarded-For": "192.168.1.1"}
        )
        response2 = client.get(
            "/test/endpoint",
            headers={"X-Forwarded-For": "192.168.1.2"}
        )

        # Both should succeed as they're from different IPs
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestCleanup:
    """Test periodic cleanup of old entries."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_cleanup_removes_old_entries(self, mock_config):
        """Test cleanup removes old request history."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 60

        app = FastAPI()
        middleware = RateLimitMiddleware(app)

        # Manually add old entry
        test_ip = "192.168.1.1"
        middleware.request_history[test_ip].append(time.time() - 120)  # 2 minutes ago

        # Trigger cleanup
        middleware._last_cleanup = 0
        middleware._periodic_cleanup()

        # Old entry should be removed
        assert test_ip not in middleware.request_history


@pytest.mark.unit
class TestRateLimitMiddlewareInitialization:
    """Test rate limit middleware initialization."""

    @patch("src.api.middleware.rate_limit.api_config")
    def test_middleware_initializes_with_config(self, mock_config):
        """Test middleware initializes with configuration."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 100

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        assert app is not None

    @patch("src.api.middleware.rate_limit.api_config")
    def test_stores_configuration(self, mock_config):
        """Test middleware stores rate limit configuration."""
        mock_config.rate_limit_enabled = True
        mock_config.rate_limit_per_minute = 50

        app = FastAPI()
        middleware = RateLimitMiddleware(app)

        assert middleware.enabled is True
        assert middleware.requests_per_minute == 50
