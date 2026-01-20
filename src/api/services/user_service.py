"""
User authentication and management service.
Handles user creation, authentication, and profile management.
"""

from datetime import datetime
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.database.models import User, UserPreference
from src.utils.logger import get_logger

logger = get_logger("api.services.user")

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user authentication and management operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Example:
            hashed = UserService.hash_password("MyPassword123")
        """
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password_truncated)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise

        Example:
            is_valid = UserService.verify_password("MyPassword123", user.password_hash)
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Create a new user account with hashed password.

        Args:
            db: Database session
            email: User email address
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: Optional full name

        Returns:
            Created User instance

        Raises:
            ValueError: If username or email already exists

        Example:
            user = UserService.create_user(
                db, "user@example.com", "johndoe", "SecurePass123", "John Doe"
            )
        """
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            or_(User.username == username, User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise ValueError("Username already registered")
            if existing_user.email == email:
                raise ValueError("Email already registered")

        # Create user with hashed password
        hashed_password = UserService.hash_password(password)
        user = User(
            email=email,
            username=username,
            password_hash=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new user: {username} (ID: {user.id})")

        # Create default preferences for the user
        preferences = UserPreference(
            user_id=user.id,
            default_servings=2
        )
        db.add(preferences)
        db.commit()

        logger.info(f"Created default preferences for user {user.id}")

        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user by username/email and password.

        Args:
            db: Database session
            username: Username or email address
            password: Plain text password

        Returns:
            User instance if authentication successful, None otherwise

        Example:
            user = UserService.authenticate_user(db, "johndoe", "MyPassword123")
            if user:
                # Authentication successful
                pass
        """
        # Try to find user by username or email
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()

        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: User inactive - {username}")
            return None

        # Verify password
        if not UserService.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            return None

        logger.info(f"User authenticated successfully: {username} (ID: {user.id})")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User instance or None if not found

        Example:
            user = UserService.get_user_by_id(db, 1)
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: Email address

        Returns:
            User instance or None if not found

        Example:
            user = UserService.get_user_by_email(db, "user@example.com")
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User instance or None if not found

        Example:
            user = UserService.get_user_by_username(db, "johndoe")
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> Optional[User]:
        """
        Update user profile information.

        Args:
            db: Database session
            user_id: User ID
            email: New email address (optional)
            full_name: New full name (optional)

        Returns:
            Updated User instance or None if not found

        Raises:
            ValueError: If email already exists for another user

        Example:
            user = UserService.update_user(db, 1, email="newemail@example.com")
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        # Check if email is being changed and if it already exists
        if email and email != user.email:
            existing_user = UserService.get_user_by_email(db, email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")
            user.email = email

        if full_name is not None:
            user.full_name = full_name

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        logger.info(f"Updated user profile: {user.username} (ID: {user.id})")
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete user account (soft delete by deactivating).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if user was deleted, False if not found

        Example:
            success = UserService.delete_user(db, 1)
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Deactivated user account: {user.username} (ID: {user.id})")
        return True

    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user_id: User ID

        Example:
            UserService.update_last_login(db, 1)
        """
        user = UserService.get_user_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
            logger.debug(f"Updated last login for user {user_id}")

    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password after verifying current password.

        Args:
            db: Database session
            user_id: User ID
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if password changed successfully, False if current password invalid

        Example:
            success = UserService.change_password(db, 1, "OldPass123", "NewPass456")
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        # Verify current password
        if not UserService.verify_password(current_password, user.password_hash):
            logger.warning(f"Password change failed: Invalid current password for user {user_id}")
            return False

        # Set new password
        user.password_hash = UserService.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Password changed successfully for user {user_id}")
        return True
