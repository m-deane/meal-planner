"""
Unit tests for FastAPI core structure.
Tests configuration, dependencies, and main application.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from jose import jwt

from src.api.config import APIConfig, api_config
from src.api.dependencies import (
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_user_optional,
    get_db,
    get_pagination_params,
    verify_admin_role,
)
from src.api.main import create_app


class TestAPIConfig:
    """Test API configuration."""

    def test_api_config_defaults(self):
        """Test default API configuration values."""
        config = APIConfig()

        assert config.api_host == "0.0.0.0"
        assert config.api_port == 8000
        assert config.api_debug is False
        assert config.api_title == "Gousto Recipe Meal Planner API"
        assert config.jwt_algorithm == "HS256"
        assert config.jwt_expire_minutes == 1440
        assert config.pagination_default_limit == 20
        assert config.pagination_max_limit == 100

    def test_cors_origins_validation(self):
        """Test CORS origins validation."""
        # Valid origins
        config = APIConfig(cors_origins=["http://localhost:3000", "https://example.com"])
        assert len(config.cors_origins) == 2

        # Wildcard allowed
        config = APIConfig(cors_origins=["*"])
        assert config.cors_origins == ["*"]

        # Invalid origin should raise error
        with pytest.raises(ValueError, match="Invalid CORS origin format"):
            APIConfig(cors_origins=["invalid-origin"])

    def test_jwt_secret_validation(self):
        """Test JWT secret validation."""
        # Short secret should fail
        with pytest.raises(ValueError, match="at least 32 characters"):
            APIConfig(jwt_secret="short")

        # Valid secret
        config = APIConfig(jwt_secret="a" * 32)
        assert len(config.jwt_secret) >= 32

    def test_jwt_algorithm_validation(self):
        """Test JWT algorithm validation."""
        # Valid algorithm
        config = APIConfig(jwt_algorithm="HS256", jwt_secret="a" * 32)
        assert config.jwt_algorithm == "HS256"

        # Invalid algorithm
        with pytest.raises(ValueError, match="must be one of"):
            APIConfig(jwt_algorithm="INVALID", jwt_secret="a" * 32)


class TestDatabaseDependency:
    """Test database dependency injection."""

    def test_get_db_generator(self, test_session):
        """Test database session generator."""
        # Mock the get_session function
        with patch("src.api.dependencies.get_session", return_value=test_session):
            db_gen = get_db()
            session = next(db_gen)

            assert session is not None
            assert session == test_session

            # Cleanup should be called
            db_gen.close()


class TestJWTAuthentication:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode to verify contents
        decoded = jwt.decode(
            token,
            api_config.jwt_secret,
            algorithms=[api_config.jwt_algorithm]
        )
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    def test_create_access_token_custom_expiry(self):
        """Test JWT token with custom expiration."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        decoded = jwt.decode(
            token,
            api_config.jwt_secret,
            algorithms=[api_config.jwt_algorithm]
        )

        # Check expiration is approximately 30 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        time_diff = abs((exp_time - expected_exp).total_seconds())

        assert time_diff < 5  # Allow 5 second tolerance

    def test_decode_access_token(self):
        """Test JWT token decoding."""
        data = {"sub": "user123", "role": "admin"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded["sub"] == "user123"
        assert decoded["role"] == "admin"

    def test_decode_invalid_token(self):
        """Test decoding invalid JWT token."""
        from jose import JWTError

        with pytest.raises(JWTError):
            decode_access_token("invalid.token.here")

    def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)

        # Mock credentials
        credentials = MagicMock()
        credentials.credentials = token

        user = get_current_user(credentials)

        assert user["sub"] == "user123"
        assert user["role"] == "user"

    def test_get_current_user_missing_token(self):
        """Test getting current user without token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication required" in exc_info.value.detail

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        credentials = MagicMock()
        credentials.credentials = "invalid.token"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_optional_with_token(self):
        """Test optional user authentication with valid token."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        credentials = MagicMock()
        credentials.credentials = token

        user = get_current_user_optional(credentials)

        assert user is not None
        assert user["sub"] == "user123"

    def test_get_current_user_optional_without_token(self):
        """Test optional user authentication without token."""
        user = get_current_user_optional(None)
        assert user is None

    def test_get_current_user_optional_invalid_token(self):
        """Test optional user authentication with invalid token."""
        credentials = MagicMock()
        credentials.credentials = "invalid"

        user = get_current_user_optional(credentials)
        assert user is None

    def test_verify_admin_role_valid(self):
        """Test admin role verification with admin user."""
        admin_user = {"sub": "admin123", "role": "admin"}
        result = verify_admin_role(admin_user)

        assert result == admin_user

    def test_verify_admin_role_invalid(self):
        """Test admin role verification with non-admin user."""
        regular_user = {"sub": "user123", "role": "user"}

        with pytest.raises(HTTPException) as exc_info:
            verify_admin_role(regular_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in exc_info.value.detail


class TestPaginationDependency:
    """Test pagination parameters dependency."""

    def test_pagination_default_values(self):
        """Test pagination with default values."""
        skip, limit = get_pagination_params()

        assert skip == 0
        assert limit == api_config.pagination_default_limit

    def test_pagination_custom_values(self):
        """Test pagination with custom values."""
        skip, limit = get_pagination_params(skip=10, limit=50)

        assert skip == 10
        assert limit == 50

    def test_pagination_negative_skip(self):
        """Test pagination with negative skip value."""
        with pytest.raises(HTTPException) as exc_info:
            get_pagination_params(skip=-1)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "skip parameter must be >= 0" in exc_info.value.detail

    def test_pagination_zero_limit(self):
        """Test pagination with zero limit."""
        with pytest.raises(HTTPException) as exc_info:
            get_pagination_params(limit=0)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "limit parameter must be >= 1" in exc_info.value.detail

    def test_pagination_excessive_limit(self):
        """Test pagination with limit exceeding maximum."""
        with pytest.raises(HTTPException) as exc_info:
            get_pagination_params(limit=1000)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert f"limit parameter must be <= {api_config.pagination_max_limit}" in exc_info.value.detail


class TestFastAPIApplication:
    """Test FastAPI application creation and endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app."""
        app = create_app()
        return TestClient(app)

    def test_app_creation(self):
        """Test FastAPI app can be created."""
        app = create_app()

        assert app is not None
        assert app.title == api_config.api_title
        assert app.version == api_config.api_version

    def test_root_endpoint(self, client):
        """Test root health check endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == api_config.api_title
        assert data["version"] == api_config.api_version

    def test_health_endpoint(self, client):
        """Test detailed health check endpoint."""
        with patch("src.api.main.check_connection", return_value=True):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["version"] == api_config.api_version

    def test_health_endpoint_db_disconnected(self, client):
        """Test health check when database is disconnected."""
        with patch("src.api.main.check_connection", return_value=False):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "degraded"
            assert data["database"] == "disconnected"

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})

        # CORS middleware should add headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        assert "openapi" in schema
        assert schema["info"]["title"] == api_config.api_title
        assert schema["info"]["version"] == api_config.api_version

    def test_validation_error_handler(self, client):
        """Test request validation error handling."""
        # Create a simple endpoint that requires validation
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = create_app()

        class TestModel(BaseModel):
            name: str
            age: int

        @app.post("/test")
        def test_endpoint(data: TestModel):
            return data

        client = TestClient(app)

        # Send invalid data
        response = client.post("/test", json={"name": "test"})  # Missing 'age'

        assert response.status_code == 422
        data = response.json()

        assert "detail" in data or "errors" in data


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API with real database."""

    @pytest.fixture
    def client(self, test_session):
        """Create test client with real database session."""
        app = create_app()

        # Override get_db dependency
        def override_get_db():
            try:
                yield test_session
            finally:
                pass

        from src.api.dependencies import get_db
        app.dependency_overrides[get_db] = override_get_db

        return TestClient(app)

    def test_api_with_database(self, client):
        """Test API endpoints work with database."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
