"""
Common response schemas for API endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")
    path: Optional[str] = Field(None, description="Request path that caused the error")
    timestamp: Optional[str] = Field(None, description="Error timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "ValidationError",
                    "message": "Invalid input parameters",
                    "details": {"field": "email", "reason": "Invalid email format"},
                    "path": "/api/v1/users",
                    "timestamp": "2026-01-20T10:30:00Z"
                }
            ]
        }
    }


class SuccessResponse(BaseModel):
    """Standard success response format."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[dict[str, Any]] = Field(None, description="Additional response data")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Recipe created successfully",
                    "data": {"recipe_id": 123}
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str = Field(..., description="Response message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "Operation completed successfully"}
            ]
        }
    }
