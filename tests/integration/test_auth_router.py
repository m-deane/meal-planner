"""
Integration tests for authentication router endpoints.
Tests user registration, login, profile management, and password changes.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.main import create_app
from src.api.dependencies import get_db
from src.api.services.user_service import UserService


class TestAuthRouter:
    """Test suite for authentication endpoints."""

    @pytest.fixture
    def client(self, db_session: Session) -> TestClient:
        """Create test client with database override."""
        with patch("src.api.main.check_connection", return_value=True):
            app = create_app()

            def override_get_db():
                try:
                    yield db_session
                finally:
                    pass

            app.dependency_overrides[get_db] = override_get_db

            with TestClient(app) as client:
                yield client

    @pytest.fixture
    def test_user(self, db_session: Session) -> dict:
        """Create a test user and return credentials."""
        user = UserService.create_user(
            db=db_session,
            email="authtest@example.com",
            username="authtest",
            password="TestPass123",
            full_name="Auth Test User"
        )

        return {
            "user": user,
            "username": "authtest",
            "password": "TestPass123"
        }

    @pytest.fixture
    def auth_headers(self, client: TestClient, test_user: dict) -> dict:
        """Get authentication headers with valid token."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    def test_register_user_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_user_duplicate_username(self, client: TestClient, test_user: dict):
        """Test registration fails with duplicate username."""
        response = client.post(
            "/auth/register",
            json={
                "username": test_user["username"],
                "email": "different@example.com",
                "password": "AnotherPass123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_user_duplicate_email(self, client: TestClient, test_user: dict):
        """Test registration fails with duplicate email."""
        response = client.post(
            "/auth/register",
            json={
                "username": "differentuser",
                "email": test_user["user"].email,
                "password": "AnotherPass123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_user_weak_password(self, client: TestClient):
        """Test registration fails with weak password."""
        response = client.post(
            "/auth/register",
            json={
                "username": "weakpass",
                "email": "weakpass@example.com",
                "password": "weak"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_user_invalid_username(self, client: TestClient):
        """Test registration fails with invalid username characters."""
        response = client.post(
            "/auth/register",
            json={
                "username": "invalid user!",
                "email": "invalid@example.com",
                "password": "ValidPass123"
            }
        )

        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user: dict):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_with_email(self, client: TestClient, test_user: dict):
        """Test login using email instead of username."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user["user"].email,
                "password": test_user["password"]
            }
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client: TestClient, test_user: dict):
        """Test login fails with wrong password."""
        response = client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login fails for non-existent user."""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "SomePass123"
            }
        )

        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, test_user: dict, auth_headers: dict):
        """Test getting current user profile."""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["user"].email
        assert data["full_name"] == test_user["user"].full_name
        assert data["id"] == test_user["user"].id

    def test_get_current_user_no_auth(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_update_current_user_email(
        self, client: TestClient, test_user: dict, auth_headers: dict
    ):
        """Test updating user email."""
        response = client.put(
            "/auth/me",
            headers=auth_headers,
            json={"email": "newemail@example.com"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "newemail@example.com"
        assert data["username"] == test_user["username"]

    def test_update_current_user_full_name(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating user full name."""
        response = client.put(
            "/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["full_name"] == "Updated Name"

    def test_update_current_user_duplicate_email(
        self, client: TestClient, db_session: Session, auth_headers: dict
    ):
        """Test update fails with duplicate email."""
        # Create another user
        UserService.create_user(
            db=db_session,
            email="another@example.com",
            username="another",
            password="Pass123"
        )

        response = client.put(
            "/auth/me",
            headers=auth_headers,
            json={"email": "another@example.com"}
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_update_current_user_no_auth(self, client: TestClient):
        """Test updating user without authentication."""
        response = client.put(
            "/auth/me",
            json={"email": "newemail@example.com"}
        )

        assert response.status_code == 401

    def test_delete_current_user(
        self, client: TestClient, auth_headers: dict, db_session: Session, test_user: dict
    ):
        """Test deleting user account."""
        response = client.delete("/auth/me", headers=auth_headers)

        assert response.status_code == 204

        # Verify user is deactivated
        user = UserService.get_user_by_id(db_session, test_user["user"].id)
        assert user is not None
        assert user.is_active is False

    def test_delete_current_user_no_auth(self, client: TestClient):
        """Test deleting user without authentication."""
        response = client.delete("/auth/me")

        assert response.status_code == 401

    def test_change_password_success(
        self, client: TestClient, test_user: dict, auth_headers: dict
    ):
        """Test successful password change."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user["password"],
                "new_password": "NewSecurePass456"
            }
        )

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

        # Verify can login with new password
        login_response = client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": "NewSecurePass456"
            }
        )

        assert login_response.status_code == 200

    def test_change_password_wrong_current(
        self, client: TestClient, auth_headers: dict
    ):
        """Test password change fails with wrong current password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewSecurePass456"
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_weak_new_password(
        self, client: TestClient, test_user: dict, auth_headers: dict
    ):
        """Test password change fails with weak new password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": test_user["password"],
                "new_password": "weak"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_change_password_no_auth(self, client: TestClient):
        """Test password change without authentication."""
        response = client.post(
            "/auth/change-password",
            json={
                "current_password": "OldPass123",
                "new_password": "NewPass456"
            }
        )

        assert response.status_code == 401

    def test_login_updates_last_login(
        self, client: TestClient, test_user: dict, db_session: Session
    ):
        """Test that login updates last_login timestamp."""
        # Get user before login
        user_before = UserService.get_user_by_id(db_session, test_user["user"].id)
        last_login_before = user_before.last_login

        # Login
        client.post(
            "/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        # Get user after login
        db_session.expire_all()  # Refresh from database
        user_after = UserService.get_user_by_id(db_session, test_user["user"].id)

        assert user_after.last_login is not None
        if last_login_before is not None:
            assert user_after.last_login > last_login_before
