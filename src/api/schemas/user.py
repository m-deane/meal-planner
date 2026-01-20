"""
User preference and allergen profile schemas for API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# USER PREFERENCE SCHEMAS
# ============================================================================

class UserPreferenceBase(BaseModel):
    """Base user preference fields."""

    default_servings: Optional[int] = Field(None, ge=1, le=20, description="Default number of servings")
    calorie_target: Optional[int] = Field(None, ge=0, le=10000, description="Daily calorie target")
    protein_target_g: Optional[Decimal] = Field(None, ge=0, le=1000, description="Daily protein target (grams)")
    carb_limit_g: Optional[Decimal] = Field(None, ge=0, le=1000, description="Daily carbohydrate limit (grams)")
    fat_limit_g: Optional[Decimal] = Field(None, ge=0, le=500, description="Daily fat limit (grams)")
    preferred_cuisines: Optional[str] = Field(None, description="JSON array of preferred cuisine types")
    excluded_ingredients: Optional[str] = Field(None, description="JSON array of excluded ingredient IDs/names")

    model_config = ConfigDict(from_attributes=True)


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""

    default_servings: int = Field(2, ge=1, le=20, description="Default number of servings")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "default_servings": 4,
                    "calorie_target": 2000,
                    "protein_target_g": 150,
                    "carb_limit_g": 200,
                    "fat_limit_g": 70,
                    "preferred_cuisines": "[\"italian\", \"mexican\"]",
                    "excluded_ingredients": "[\"cilantro\", \"mushrooms\"]"
                }
            ]
        }
    }


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)."""

    default_servings: Optional[int] = Field(None, ge=1, le=20)
    calorie_target: Optional[int] = Field(None, ge=0, le=10000)
    protein_target_g: Optional[Decimal] = Field(None, ge=0, le=1000)
    carb_limit_g: Optional[Decimal] = Field(None, ge=0, le=1000)
    fat_limit_g: Optional[Decimal] = Field(None, ge=0, le=500)
    preferred_cuisines: Optional[str] = None
    excluded_ingredients: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "default_servings": 2,
                    "calorie_target": 1800,
                    "protein_target_g": 120
                }
            ]
        }
    }


class DietaryTagResponse(BaseModel):
    """Dietary tag information."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserPreferenceResponse(UserPreferenceBase):
    """Complete user preference response."""

    id: int
    user_id: int
    dietary_tags: List[DietaryTagResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "default_servings": 4,
                    "calorie_target": 2000,
                    "protein_target_g": 150,
                    "carb_limit_g": 200,
                    "fat_limit_g": 70,
                    "preferred_cuisines": "[\"italian\", \"mexican\"]",
                    "excluded_ingredients": "[\"cilantro\"]",
                    "dietary_tags": [
                        {"id": 1, "name": "Vegetarian", "slug": "vegetarian", "description": "No meat"}
                    ],
                    "created_at": "2026-01-20T10:00:00Z",
                    "updated_at": "2026-01-20T15:30:00Z"
                }
            ]
        }
    )


# ============================================================================
# ALLERGEN PROFILE SCHEMAS
# ============================================================================

class AllergenResponse(BaseModel):
    """Allergen information."""

    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserAllergenBase(BaseModel):
    """Base user allergen fields."""

    allergen_id: int = Field(..., gt=0, description="Allergen ID")
    severity: str = Field(
        ...,
        description="Severity level: 'avoid', 'severe', or 'trace_ok'"
    )

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level."""
        valid = ['avoid', 'severe', 'trace_ok']
        if v not in valid:
            raise ValueError(f"Severity must be one of {valid}")
        return v


class UserAllergenCreate(UserAllergenBase):
    """Schema for adding a single allergen to user profile."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "allergen_id": 5,
                    "severity": "severe"
                }
            ]
        }
    }


class UserAllergenBulkCreate(BaseModel):
    """Schema for setting multiple allergens at once."""

    allergens: List[UserAllergenBase] = Field(
        ...,
        description="List of allergens with severity levels"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "allergens": [
                        {"allergen_id": 1, "severity": "severe"},
                        {"allergen_id": 3, "severity": "avoid"},
                        {"allergen_id": 7, "severity": "trace_ok"}
                    ]
                }
            ]
        }
    }


class UserAllergenResponse(BaseModel):
    """User allergen with full allergen details."""

    user_id: int
    allergen_id: int
    severity: str
    allergen: AllergenResponse
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "allergen_id": 5,
                    "severity": "severe",
                    "allergen": {
                        "id": 5,
                        "name": "Peanuts",
                        "description": "Tree nuts and peanuts"
                    },
                    "created_at": "2026-01-20T10:00:00Z"
                }
            ]
        }
    )


class UserAllergenListResponse(BaseModel):
    """List of user allergens."""

    allergens: List[UserAllergenResponse] = Field(default_factory=list)
    count: int = Field(..., description="Total number of allergens")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "allergens": [
                        {
                            "user_id": 1,
                            "allergen_id": 5,
                            "severity": "severe",
                            "allergen": {"id": 5, "name": "Peanuts", "description": "Tree nuts"},
                            "created_at": "2026-01-20T10:00:00Z"
                        }
                    ],
                    "count": 1
                }
            ]
        }
    }


# ============================================================================
# DIETARY TAG SCHEMAS
# ============================================================================

class UserDietaryTagsUpdate(BaseModel):
    """Schema for updating user's dietary tags."""

    dietary_tag_ids: List[int] = Field(
        ...,
        description="List of dietary tag IDs to associate with user"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dietary_tag_ids": [1, 3, 5]
                }
            ]
        }
    }


class UserDietaryTagsResponse(BaseModel):
    """User's dietary tags response."""

    dietary_tags: List[DietaryTagResponse] = Field(default_factory=list)
    count: int = Field(..., description="Total number of dietary tags")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dietary_tags": [
                        {"id": 1, "name": "Vegan", "slug": "vegan", "description": "No animal products"},
                        {"id": 3, "name": "Gluten-Free", "slug": "gluten-free", "description": "No gluten"}
                    ],
                    "count": 2
                }
            ]
        }
    }
