"""
Unit tests for error handler middleware.
Tests custom exception handlers, validation errors, and database errors.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

from src.api.middleware import APIException, register_exception_handlers


class SampleModel(BaseModel):
    """Sample Pydantic model for testing validation."""
    name: str
    age: int


@pytest.fixture
def app() -> FastAPI:
    """Create test FastAPI application."""
    app = FastAPI()

    # Register exception handlers
    register_exception_handlers(app)

    # Test endpoints
    @app.get("/test/api-exception")
    async def raise_api_exception():
        """Endpoint that raises APIException."""
        raise APIException(
            status_code=404,
            detail="Resource not found",
            headers={"X-Custom": "header"}
        )

    @app.get("/test/integrity-error")
    async def raise_integrity_error():
        """Endpoint that raises IntegrityError."""
        raise IntegrityError(
            "INSERT failed",
            params=None,
            orig=Exception("UNIQUE constraint failed")
        )

    @app.get("/test/operational-error")
    async def raise_operational_error():
        """Endpoint that raises OperationalError."""
        raise OperationalError(
            "Connection failed",
            params=None,
            orig=Exception("Cannot connect to database")
        )

    @app.get("/test/general-error")
    async def raise_general_error():
        """Endpoint that raises general exception."""
        raise ValueError("Something went wrong")

    @app.post("/test/validation")
    async def validate_data(data: SampleModel):
        """Endpoint with request validation."""
        return {"data": data}

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client with exception handling."""
    return TestClient(app, raise_server_exceptions=False)


class TestAPIException:
    """Test custom APIException handling."""

    def test_api_exception_with_detail(self, client: TestClient):
        """Test APIException returns correct status and detail."""
        response = client.get("/test/api-exception")

        assert response.status_code == 404
        assert response.json()["detail"] == "Resource not found"
        assert response.json()["status"] == "error"
        assert response.json()["error_type"] == "api_error"

    def test_api_exception_with_custom_headers(self, client: TestClient):
        """Test APIException includes custom headers."""
        response = client.get("/test/api-exception")

        assert "X-Custom" in response.headers
        assert response.headers["X-Custom"] == "header"

    def test_api_exception_raises_in_code(self):
        """Test APIException can be raised programmatically."""
        with pytest.raises(APIException) as exc_info:
            raise APIException(
                status_code=403,
                detail="Forbidden"
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Forbidden"
        assert str(exc_info.value) == "Forbidden"


class TestValidationErrors:
    """Test request validation error handling."""

    def test_missing_required_field(self, client: TestClient):
        """Test validation error for missing required field."""
        response = client.post("/test/validation", json={"age": 25})

        assert response.status_code == 422
        assert response.json()["detail"] == "Validation error"
        assert response.json()["error_type"] == "validation_error"

        errors = response.json()["errors"]
        assert len(errors) == 1
        assert "name" in errors[0]["field"]

    def test_invalid_field_type(self, client: TestClient):
        """Test validation error for invalid field type."""
        response = client.post("/test/validation", json={
            "name": "John",
            "age": "not-a-number"
        })

        assert response.status_code == 422
        errors = response.json()["errors"]
        assert any("age" in error["field"] for error in errors)

    def test_multiple_validation_errors(self, client: TestClient):
        """Test multiple validation errors at once."""
        response = client.post("/test/validation", json={})

        assert response.status_code == 422
        errors = response.json()["errors"]
        assert len(errors) >= 2  # Missing name and age

    def test_validation_error_includes_type(self, client: TestClient):
        """Test validation errors include error type."""
        response = client.post("/test/validation", json={"age": 25})

        errors = response.json()["errors"]
        assert all("type" in error for error in errors)

    def test_pydantic_validation_error_direct(self):
        """Test direct Pydantic validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SampleModel(name="John", age="invalid")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("age",)


class TestDatabaseErrors:
    """Test SQLAlchemy database error handling."""

    def test_integrity_error_returns_409(self, client: TestClient):
        """Test IntegrityError returns 409 Conflict."""
        response = client.get("/test/integrity-error")

        assert response.status_code == 409
        assert response.json()["detail"] == "Database constraint violation"
        assert response.json()["error_type"] == "integrity_error"

    def test_operational_error_returns_503(self, client: TestClient):
        """Test OperationalError returns 503 Service Unavailable."""
        response = client.get("/test/operational-error")

        assert response.status_code == 503
        assert response.json()["detail"] == "Database temporarily unavailable"
        assert response.json()["error_type"] == "database_error"

    def test_integrity_error_hides_details_in_production(self, client: TestClient):
        """Test database errors hide sensitive details in production."""
        response = client.get("/test/integrity-error")

        # In non-debug mode, should not expose internal error details
        assert "debug" not in response.json() or response.json().get("debug") is None


class TestGeneralErrors:
    """Test general exception handling."""

    def test_general_exception_returns_500(self, client: TestClient):
        """Test general exceptions return 500 Internal Server Error."""
        response = client.get("/test/general-error")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert response.json()["error_type"] == "internal_error"

    def test_general_error_includes_status(self, client: TestClient):
        """Test general errors include error status."""
        response = client.get("/test/general-error")

        assert response.json()["status"] == "error"


class TestErrorResponseFormat:
    """Test consistent error response formatting."""

    def test_all_errors_have_detail(self, client: TestClient):
        """Test all error responses include detail field."""
        endpoints = [
            "/test/api-exception",
            "/test/integrity-error",
            "/test/operational-error",
            "/test/general-error"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "detail" in response.json()

    def test_all_errors_have_status(self, client: TestClient):
        """Test all error responses include status field."""
        endpoints = [
            "/test/api-exception",
            "/test/integrity-error",
            "/test/operational-error",
            "/test/general-error"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "status" in response.json()
            assert response.json()["status"] == "error"

    def test_all_errors_have_error_type(self, client: TestClient):
        """Test all error responses include error_type field."""
        endpoints = [
            "/test/api-exception",
            "/test/integrity-error",
            "/test/operational-error",
            "/test/general-error"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "error_type" in response.json()

    def test_validation_errors_have_errors_list(self, client: TestClient):
        """Test validation errors include errors list."""
        response = client.post("/test/validation", json={})

        assert "errors" in response.json()
        assert isinstance(response.json()["errors"], list)


@pytest.mark.unit
class TestAPIExceptionInitialization:
    """Test APIException class initialization."""

    def test_exception_with_all_parameters(self):
        """Test creating exception with all parameters."""
        exc = APIException(
            status_code=400,
            detail="Bad request",
            headers={"X-Error": "test"}
        )

        assert exc.status_code == 400
        assert exc.detail == "Bad request"
        assert exc.headers == {"X-Error": "test"}

    def test_exception_without_headers(self):
        """Test creating exception without headers."""
        exc = APIException(status_code=404, detail="Not found")

        assert exc.status_code == 404
        assert exc.detail == "Not found"
        assert exc.headers is None

    def test_exception_string_representation(self):
        """Test exception string representation."""
        exc = APIException(status_code=500, detail="Server error")

        assert str(exc) == "Server error"
