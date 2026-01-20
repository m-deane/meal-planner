"""
Authentication endpoints for user registration, login, and profile management.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.config import api_config
from src.api.dependencies import (
    DatabaseSession, create_access_token, CurrentUser, get_db
)
from src.api.schemas.auth import (
    UserCreate, LoginRequest, PasswordChangeRequest,
    TokenResponse, UserResponse, UserUpdate
)
from src.api.services.user_service import UserService
from src.utils.logger import get_logger

logger = get_logger("api.routers.auth")

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, username, and password"
)
def register_user(
    user_data: UserCreate,
    db: DatabaseSession
) -> UserResponse:
    """
    Register a new user account.

    Creates a new user with hashed password and default preferences.

    Args:
        user_data: User registration data (username, email, password)
        db: Database session

    Returns:
        Created user information

    Raises:
        400: If username or email already exists
        422: If validation fails

    Example:
        POST /auth/register
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePass123",
            "full_name": "John Doe"
        }
    """
    try:
        user = UserService.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )

        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")

        return UserResponse.model_validate(user)

    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT access token"
)
def login(
    credentials: LoginRequest,
    db: DatabaseSession
) -> TokenResponse:
    """
    Authenticate user and return access token.

    Accepts username or email as the username field.

    Args:
        credentials: Login credentials (username/email and password)
        db: Database session

    Returns:
        JWT access token and metadata

    Raises:
        401: If credentials are invalid or user is inactive

    Example:
        POST /auth/login
        {
            "username": "johndoe",
            "password": "SecurePass123"
        }

        Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "expires_in": 86400
        }
    """
    # Authenticate user
    user = UserService.authenticate_user(
        db=db,
        username=credentials.username,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    UserService.update_last_login(db, user.id)

    # Create access token
    access_token_expires = timedelta(minutes=api_config.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "email": user.email},
        expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {user.username} (ID: {user.id})")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=api_config.jwt_expire_minutes * 60  # Convert to seconds
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user's profile information"
)
def get_current_user_profile(
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserResponse:
    """
    Get current authenticated user's profile.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        User profile information

    Raises:
        401: If not authenticated
        404: If user not found

    Example:
        GET /auth/me
        Authorization: Bearer <token>

        Response:
        {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "is_verified": false,
            "created_at": "2026-01-20T10:00:00Z",
            "last_login": "2026-01-20T15:30:00Z"
        }
    """
    user_id = int(current_user.get("sub"))
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update authenticated user's profile information"
)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserResponse:
    """
    Update current user's profile.

    Args:
        user_update: Profile update data
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Updated user profile

    Raises:
        401: If not authenticated
        400: If email already exists
        404: If user not found

    Example:
        PUT /auth/me
        Authorization: Bearer <token>
        {
            "email": "newemail@example.com",
            "full_name": "John Smith"
        }
    """
    user_id = int(current_user.get("sub"))

    try:
        user = UserService.update_user(
            db=db,
            user_id=user_id,
            email=user_update.email,
            full_name=user_update.full_name
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"User profile updated: {user.username} (ID: {user.id})")

        return UserResponse.model_validate(user)

    except ValueError as e:
        logger.warning(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
    description="Delete (deactivate) authenticated user's account"
)
def delete_current_user_account(
    current_user: CurrentUser,
    db: DatabaseSession
) -> None:
    """
    Delete current user's account (soft delete).

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Raises:
        401: If not authenticated
        404: If user not found

    Example:
        DELETE /auth/me
        Authorization: Bearer <token>
    """
    user_id = int(current_user.get("sub"))

    success = UserService.delete_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"User account deleted: ID {user_id}")


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change authenticated user's password"
)
def change_password(
    password_change: PasswordChangeRequest,
    current_user: CurrentUser,
    db: DatabaseSession
) -> dict:
    """
    Change current user's password.

    Args:
        password_change: Current and new password
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Success message

    Raises:
        401: If not authenticated or current password is incorrect
        404: If user not found

    Example:
        POST /auth/change-password
        Authorization: Bearer <token>
        {
            "current_password": "OldPass123",
            "new_password": "NewSecurePass456"
        }

        Response:
        {
            "message": "Password changed successfully"
        }
    """
    user_id = int(current_user.get("sub"))

    success = UserService.change_password(
        db=db,
        user_id=user_id,
        current_password=password_change.current_password,
        new_password=password_change.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    logger.info(f"Password changed for user ID {user_id}")

    return {"message": "Password changed successfully"}


# Export router
auth_router = router
