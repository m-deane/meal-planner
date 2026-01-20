"""
Unit tests for UserService.
Tests user authentication, creation, and management operations.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.api.services.user_service import UserService
from src.database.models import User, UserPreference


class TestUserService:
    """Test suite for UserService operations."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "SecurePassword123"
        hashed = UserService.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "SecurePassword123"
        hashed = UserService.hash_password(password)

        assert UserService.verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "SecurePassword123"
        wrong_password = "WrongPassword456"
        hashed = UserService.hash_password(password)

        assert UserService.verify_password(wrong_password, hashed) is False

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation."""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="SecurePass123",
            full_name="Test User"
        )

        assert user is not None
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.password_hash != "SecurePass123"
        assert user.password_hash.startswith("$2b$")

        # Verify preferences were created
        prefs = db_session.query(UserPreference).filter(
            UserPreference.user_id == user.id
        ).first()
        assert prefs is not None
        assert prefs.default_servings == 2

    def test_create_user_duplicate_username(self, db_session: Session):
        """Test user creation fails with duplicate username."""
        UserService.create_user(
            db=db_session,
            email="user1@example.com",
            username="duplicate",
            password="Pass123"
        )

        with pytest.raises(ValueError, match="Username already registered"):
            UserService.create_user(
                db=db_session,
                email="user2@example.com",
                username="duplicate",
                password="Pass456"
            )

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation fails with duplicate email."""
        UserService.create_user(
            db=db_session,
            email="duplicate@example.com",
            username="user1",
            password="Pass123"
        )

        with pytest.raises(ValueError, match="Email already registered"):
            UserService.create_user(
                db=db_session,
                email="duplicate@example.com",
                username="user2",
                password="Pass456"
            )

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication."""
        # Create user
        created_user = UserService.create_user(
            db=db_session,
            email="auth@example.com",
            username="authuser",
            password="AuthPass123"
        )

        # Authenticate with username
        user = UserService.authenticate_user(
            db=db_session,
            username="authuser",
            password="AuthPass123"
        )

        assert user is not None
        assert user.id == created_user.id
        assert user.username == "authuser"

    def test_authenticate_user_with_email(self, db_session: Session):
        """Test authentication using email instead of username."""
        # Create user
        created_user = UserService.create_user(
            db=db_session,
            email="email@example.com",
            username="emailuser",
            password="EmailPass123"
        )

        # Authenticate with email
        user = UserService.authenticate_user(
            db=db_session,
            username="email@example.com",
            password="EmailPass123"
        )

        assert user is not None
        assert user.id == created_user.id

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test authentication fails with wrong password."""
        UserService.create_user(
            db=db_session,
            email="wrong@example.com",
            username="wrongpass",
            password="CorrectPass123"
        )

        user = UserService.authenticate_user(
            db=db_session,
            username="wrongpass",
            password="WrongPass123"
        )

        assert user is None

    def test_authenticate_user_not_found(self, db_session: Session):
        """Test authentication fails for non-existent user."""
        user = UserService.authenticate_user(
            db=db_session,
            username="nonexistent",
            password="Pass123"
        )

        assert user is None

    def test_authenticate_inactive_user(self, db_session: Session):
        """Test authentication fails for inactive user."""
        user = UserService.create_user(
            db=db_session,
            email="inactive@example.com",
            username="inactive",
            password="Pass123"
        )

        # Deactivate user
        user.is_active = False
        db_session.commit()

        # Try to authenticate
        authenticated = UserService.authenticate_user(
            db=db_session,
            username="inactive",
            password="Pass123"
        )

        assert authenticated is None

    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID."""
        created_user = UserService.create_user(
            db=db_session,
            email="byid@example.com",
            username="byid",
            password="Pass123"
        )

        user = UserService.get_user_by_id(db_session, created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.username == "byid"

    def test_get_user_by_id_not_found(self, db_session: Session):
        """Test getting non-existent user by ID."""
        user = UserService.get_user_by_id(db_session, 99999)
        assert user is None

    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email."""
        created_user = UserService.create_user(
            db=db_session,
            email="byemail@example.com",
            username="byemail",
            password="Pass123"
        )

        user = UserService.get_user_by_email(db_session, "byemail@example.com")

        assert user is not None
        assert user.id == created_user.id
        assert user.email == "byemail@example.com"

    def test_get_user_by_username(self, db_session: Session):
        """Test getting user by username."""
        created_user = UserService.create_user(
            db=db_session,
            email="byusername@example.com",
            username="byusername",
            password="Pass123"
        )

        user = UserService.get_user_by_username(db_session, "byusername")

        assert user is not None
        assert user.id == created_user.id
        assert user.username == "byusername"

    def test_update_user_email(self, db_session: Session):
        """Test updating user email."""
        user = UserService.create_user(
            db=db_session,
            email="old@example.com",
            username="updateuser",
            password="Pass123"
        )

        updated = UserService.update_user(
            db=db_session,
            user_id=user.id,
            email="new@example.com"
        )

        assert updated is not None
        assert updated.email == "new@example.com"
        assert updated.username == "updateuser"

    def test_update_user_full_name(self, db_session: Session):
        """Test updating user full name."""
        user = UserService.create_user(
            db=db_session,
            email="name@example.com",
            username="nameuser",
            password="Pass123",
            full_name="Old Name"
        )

        updated = UserService.update_user(
            db=db_session,
            user_id=user.id,
            full_name="New Name"
        )

        assert updated is not None
        assert updated.full_name == "New Name"

    def test_update_user_duplicate_email(self, db_session: Session):
        """Test update fails with duplicate email."""
        user1 = UserService.create_user(
            db=db_session,
            email="user1@example.com",
            username="user1",
            password="Pass123"
        )

        user2 = UserService.create_user(
            db=db_session,
            email="user2@example.com",
            username="user2",
            password="Pass123"
        )

        with pytest.raises(ValueError, match="Email already registered"):
            UserService.update_user(
                db=db_session,
                user_id=user2.id,
                email="user1@example.com"
            )

    def test_update_user_not_found(self, db_session: Session):
        """Test updating non-existent user."""
        result = UserService.update_user(
            db=db_session,
            user_id=99999,
            email="new@example.com"
        )

        assert result is None

    def test_delete_user(self, db_session: Session):
        """Test deleting (deactivating) user."""
        user = UserService.create_user(
            db=db_session,
            email="delete@example.com",
            username="deleteuser",
            password="Pass123"
        )

        success = UserService.delete_user(db_session, user.id)

        assert success is True

        # User should still exist but be inactive
        deleted_user = UserService.get_user_by_id(db_session, user.id)
        assert deleted_user is not None
        assert deleted_user.is_active is False

    def test_delete_user_not_found(self, db_session: Session):
        """Test deleting non-existent user."""
        success = UserService.delete_user(db_session, 99999)
        assert success is False

    def test_update_last_login(self, db_session: Session):
        """Test updating last login timestamp."""
        user = UserService.create_user(
            db=db_session,
            email="login@example.com",
            username="loginuser",
            password="Pass123"
        )

        assert user.last_login is None

        UserService.update_last_login(db_session, user.id)

        updated_user = UserService.get_user_by_id(db_session, user.id)
        assert updated_user.last_login is not None
        assert isinstance(updated_user.last_login, datetime)

    def test_change_password_success(self, db_session: Session):
        """Test successful password change."""
        user = UserService.create_user(
            db=db_session,
            email="changepass@example.com",
            username="changepass",
            password="OldPass123"
        )

        success = UserService.change_password(
            db=db_session,
            user_id=user.id,
            current_password="OldPass123",
            new_password="NewPass456"
        )

        assert success is True

        # Verify new password works
        authenticated = UserService.authenticate_user(
            db=db_session,
            username="changepass",
            password="NewPass456"
        )
        assert authenticated is not None

        # Verify old password doesn't work
        old_auth = UserService.authenticate_user(
            db=db_session,
            username="changepass",
            password="OldPass123"
        )
        assert old_auth is None

    def test_change_password_wrong_current(self, db_session: Session):
        """Test password change fails with wrong current password."""
        user = UserService.create_user(
            db=db_session,
            email="wrongcurrent@example.com",
            username="wrongcurrent",
            password="CorrectPass123"
        )

        success = UserService.change_password(
            db=db_session,
            user_id=user.id,
            current_password="WrongPass123",
            new_password="NewPass456"
        )

        assert success is False

    def test_change_password_user_not_found(self, db_session: Session):
        """Test password change for non-existent user."""
        success = UserService.change_password(
            db=db_session,
            user_id=99999,
            current_password="Pass123",
            new_password="NewPass456"
        )

        assert success is False
