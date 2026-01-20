"""
Authentication and user management schemas for API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
import re


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """User login credentials."""

    username: str = Field(..., min_length=3, max_length=100, description="Username or email")
    password: str = Field(..., min_length=8, description="User password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john.doe@example.com",
                    "password": "SecureP@ssw0rd"
                }
            ]
        }
    }


class UserCreate(BaseModel):
    """User registration data."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (alphanumeric, underscores, hyphens)"
    )
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must contain uppercase, lowercase, number)"
    )
    full_name: Optional[str] = Field(None, max_length=200, description="User's full name")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                'Username can only contain alphanumeric characters, underscores, and hyphens'
            )
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "email": "john.doe@example.com",
                    "password": "SecureP@ssw0rd123",
                    "full_name": "John Doe"
                }
            ]
        }
    }


class PasswordChangeRequest(BaseModel):
    """Password change request."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 chars)"
    )

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "OldP@ssw0rd123",
                    "new_password": "NewSecureP@ssw0rd456"
                }
            ]
        }
    }


class PasswordResetRequest(BaseModel):
    """Password reset request (forgot password)."""

    email: EmailStr = Field(..., description="Email address for password reset")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "john.doe@example.com"}
            ]
        }
    }


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token."""

    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "abc123def456",
                    "new_password": "NewSecureP@ssw0rd789"
                }
            ]
        }
    }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "refresh_token": "def456ghi789..."
                }
            ]
        }
    }


class UserBase(BaseModel):
    """Base user information."""

    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Complete user information for responses."""

    id: int = Field(..., description="User ID")
    is_active: bool = Field(True, description="Whether user account is active")
    is_verified: bool = Field(False, description="Whether email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    # User preferences
    preferences: Optional[dict] = Field(None, description="User preferences and settings")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2026-01-01T10:00:00Z",
                    "last_login": "2026-01-20T09:30:00Z",
                    "preferences": {
                        "theme": "dark",
                        "notifications_enabled": True
                    }
                }
            ]
        }
    )


class UserUpdate(BaseModel):
    """User profile update data."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, max_length=200, description="New full name")
    preferences: Optional[dict] = Field(None, description="User preferences")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newemail@example.com",
                    "full_name": "John Smith",
                    "preferences": {
                        "theme": "light",
                        "notifications_enabled": False
                    }
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""

    refresh_token: str = Field(..., description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"refresh_token": "def456ghi789..."}
            ]
        }
    }


class EmailVerificationRequest(BaseModel):
    """Request to verify email address."""

    token: str = Field(..., description="Email verification token")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"token": "abc123def456ghi789"}
            ]
        }
    }
