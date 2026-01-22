"""
Shared fixtures for integration tests.
Provides authenticated test client and database session.

Uses file-based SQLite to ensure database state persists across requests.
"""

import os
import tempfile
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.main import create_app
from src.api.dependencies import get_db
from src.api.services.user_service import UserService
from src.database.models import Base


@pytest.fixture(scope="function")
def integration_db():
    """Create a file-based SQLite database for integration tests."""
    # Create a temporary file for the database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create engine and tables
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    # Create session factory
    SessionLocal = sessionmaker(bind=engine)

    yield engine, SessionLocal

    # Cleanup
    engine.dispose()
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def db_session(integration_db):
    """Create database session for integration tests."""
    engine, SessionLocal = integration_db
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def client(integration_db) -> TestClient:
    """Create test client with database override."""
    engine, SessionLocal = integration_db

    with patch("src.api.main.check_connection", return_value=True):
        app = create_app()

        def override_get_db():
            session = SessionLocal()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client


@pytest.fixture
def test_user(integration_db) -> dict:
    """Create a test user and return credentials."""
    engine, SessionLocal = integration_db
    session = SessionLocal()

    try:
        user = UserService.create_user(
            db=session,
            email="testuser@example.com",
            username="testuser",
            password="TestPass123",
            full_name="Test User"
        )
        session.commit()

        return {
            "user": user,
            "user_id": user.id,
            "username": "testuser",
            "password": "TestPass123"
        }
    finally:
        session.close()


@pytest.fixture
def auth_headers(client: TestClient, test_user: dict) -> dict:
    """Get authentication headers with valid token."""
    response = client.post(
        "/auth/login",
        json={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )

    # If login fails, return empty headers (test will fail appropriately)
    if response.status_code != 200:
        return {}

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
