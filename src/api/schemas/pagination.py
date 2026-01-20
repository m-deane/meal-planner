"""
Pagination and sorting schemas for API endpoints.
"""

from typing import Generic, TypeVar, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, description="Items per page (max 100)")

    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """Ensure page size is within reasonable limits."""
        if v > 100:
            return 100
        return v

    @property
    def offset(self) -> int:
        """Calculate database offset from page and page_size."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias for page_size for database queries."""
        return self.page_size

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"page": 1, "page_size": 20},
                {"page": 2, "page_size": 50}
            ]
        }
    }


class SortParams(BaseModel):
    """Sorting query parameters."""

    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order (asc/desc)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"sort_by": "created_at", "sort_order": "desc"},
                {"sort_by": "name", "sort_order": "asc"}
            ]
        }
    }


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(..., description="List of items for current page")
    total: int = Field(..., ge=0, description="Total number of items across all pages")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int
    ) -> 'PaginatedResponse[T]':
        """Factory method to create paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [],
                    "total": 150,
                    "page": 2,
                    "page_size": 20,
                    "total_pages": 8,
                    "has_next": True,
                    "has_previous": True
                }
            ]
        }
    }
