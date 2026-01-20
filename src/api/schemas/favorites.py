"""
Favorites and allergen-related Pydantic schemas for API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# ENUMS
# ============================================================================

class AllergenSeverity(str, Enum):
    """Allergen severity levels."""
    AVOID = "avoid"  # Completely avoid this allergen
    SEVERE = "severe"  # Severe allergy - complete avoidance required
    TRACE_OK = "trace_ok"  # Can tolerate trace amounts


# ============================================================================
# FAVORITE RECIPE SCHEMAS
# ============================================================================

class FavoriteRequest(BaseModel):
    """Request to add a recipe to favorites."""

    notes: Optional[str] = Field(None, max_length=1000, description="Personal notes about this recipe")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "notes": "Kids love this! Make extra sauce next time."
                }
            ]
        }
    }


class FavoriteNotesUpdate(BaseModel):
    """Update notes for a favorited recipe."""

    notes: Optional[str] = Field(None, max_length=1000, description="Updated notes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "notes": "Updated: Use less salt, add more garlic"
                }
            ]
        }
    }


class FavoriteStatusResponse(BaseModel):
    """Response indicating if a recipe is favorited."""

    is_favorite: bool = Field(..., description="Whether the recipe is in user's favorites")
    notes: Optional[str] = Field(None, description="User's notes if favorited")
    created_at: Optional[datetime] = Field(None, description="When it was favorited")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_favorite": True,
                    "notes": "Family favorite!",
                    "created_at": "2026-01-15T14:30:00"
                }
            ]
        }
    }


class RecipeSummary(BaseModel):
    """Minimal recipe information for favorites list."""

    id: int = Field(..., description="Recipe ID")
    slug: str = Field(..., description="URL-friendly slug")
    name: str = Field(..., description="Recipe name")
    description: Optional[str] = Field(None, description="Brief description")
    cooking_time_minutes: Optional[int] = Field(None, description="Cooking time in minutes")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    image_url: Optional[str] = Field(None, description="Main recipe image URL")

    model_config = ConfigDict(from_attributes=True)


class FavoriteRecipeResponse(BaseModel):
    """Complete favorite recipe response with notes and metadata."""

    id: int = Field(..., description="Favorite record ID")
    recipe: RecipeSummary = Field(..., description="Recipe summary information")
    notes: Optional[str] = Field(None, description="User's personal notes")
    created_at: datetime = Field(..., description="When recipe was favorited")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "recipe": {
                        "id": 42,
                        "slug": "chicken-tikka-masala",
                        "name": "Chicken Tikka Masala",
                        "description": "Creamy Indian curry with tender chicken",
                        "cooking_time_minutes": 45,
                        "difficulty": "medium",
                        "image_url": "https://example.com/images/chicken-tikka.jpg"
                    },
                    "notes": "Best curry ever! Kids love it with naan.",
                    "created_at": "2026-01-15T14:30:00"
                }
            ]
        }
    )


class FavoriteCountResponse(BaseModel):
    """Response with count of user's favorites."""

    count: int = Field(..., ge=0, description="Number of favorited recipes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"count": 15}
            ]
        }
    }


# ============================================================================
# ALLERGEN WARNING SCHEMAS
# ============================================================================

class AllergenWarning(BaseModel):
    """Warning about an allergen present in a recipe."""

    allergen_name: str = Field(..., description="Name of the allergen")
    severity: AllergenSeverity = Field(..., description="User's severity level for this allergen")
    ingredient_name: str = Field(..., description="Which ingredient contains this allergen")
    message: str = Field(..., description="Human-readable warning message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "allergen_name": "Peanuts",
                    "severity": "severe",
                    "ingredient_name": "Peanut butter",
                    "message": "SEVERE ALLERGY: This recipe contains peanut butter which contains Peanuts"
                }
            ]
        }
    }


class AllergenWarningsResponse(BaseModel):
    """Complete allergen warnings for a recipe."""

    recipe_id: int = Field(..., description="Recipe ID")
    recipe_name: str = Field(..., description="Recipe name")
    warnings: List[AllergenWarning] = Field(default_factory=list, description="List of allergen warnings")
    is_safe: bool = Field(..., description="Whether recipe is safe for user's allergen profile")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipe_id": 42,
                    "recipe_name": "Thai Peanut Noodles",
                    "warnings": [
                        {
                            "allergen_name": "Peanuts",
                            "severity": "severe",
                            "ingredient_name": "Peanut butter",
                            "message": "SEVERE ALLERGY: This recipe contains peanut butter which contains Peanuts"
                        }
                    ],
                    "is_safe": False
                }
            ]
        }
    }


class IngredientSubstitution(BaseModel):
    """Suggested ingredient substitution for allergen avoidance."""

    original_ingredient: str = Field(..., description="Original ingredient containing allergen")
    allergen: str = Field(..., description="Allergen to avoid")
    substitutes: List[str] = Field(..., description="List of safe substitute ingredients")
    notes: Optional[str] = Field(None, description="Additional substitution notes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "original_ingredient": "Peanut butter",
                    "allergen": "Peanuts",
                    "substitutes": ["Sunflower seed butter", "Almond butter", "Tahini"],
                    "notes": "Use same quantity. Flavor will be slightly different."
                }
            ]
        }
    }


class SafeRecipesFilters(BaseModel):
    """Filters for getting safe recipes based on allergen profile."""

    max_cooking_time: Optional[int] = Field(None, ge=0, le=300, description="Maximum cooking time in minutes")
    difficulty: Optional[str] = Field(None, description="Difficulty level (easy, medium, hard)")
    category_slugs: Optional[List[str]] = Field(None, description="Filter by category slugs")
    dietary_tag_slugs: Optional[List[str]] = Field(None, description="Filter by dietary tag slugs")
    min_protein: Optional[float] = Field(None, ge=0, description="Minimum protein in grams")
    max_carbs: Optional[float] = Field(None, ge=0, description="Maximum carbs in grams")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "max_cooking_time": 30,
                    "difficulty": "easy",
                    "category_slugs": ["quick-meals", "weeknight-dinners"],
                    "min_protein": 20
                }
            ]
        }
    }
