"""
Recipe-related Pydantic schemas for API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# ENUMS
# ============================================================================

class DifficultyLevel(str, Enum):
    """Recipe difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ImageType(str, Enum):
    """Image type classifications."""
    MAIN = "main"
    STEP = "step"
    THUMBNAIL = "thumbnail"
    HERO = "hero"


class CategoryType(str, Enum):
    """Category type classifications."""
    CUISINE = "cuisine"
    MEAL_TYPE = "meal_type"
    OCCASION = "occasion"


# ============================================================================
# NESTED RESPONSE SCHEMAS
# ============================================================================

class UnitResponse(BaseModel):
    """Unit information for ingredients."""

    id: int
    name: str
    abbreviation: str
    unit_type: str

    model_config = ConfigDict(from_attributes=True)


class IngredientResponse(BaseModel):
    """Ingredient with quantity information for a recipe."""

    name: str = Field(..., description="Ingredient name")
    quantity: Optional[Decimal] = Field(None, description="Quantity amount")
    unit: Optional[str] = Field(None, description="Unit abbreviation (e.g., 'g', 'ml', 'cups')")
    unit_name: Optional[str] = Field(None, description="Full unit name")
    preparation_note: Optional[str] = Field(None, description="Preparation instructions (e.g., 'chopped', 'diced')")
    is_optional: bool = Field(False, description="Whether ingredient is optional")
    category: Optional[str] = Field(None, description="Ingredient category")
    display_order: int = Field(0, description="Display order in ingredient list")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Chicken Breast",
                    "quantity": 300,
                    "unit": "g",
                    "unit_name": "grams",
                    "preparation_note": "diced",
                    "is_optional": False,
                    "category": "protein",
                    "display_order": 1
                }
            ]
        }
    )


class InstructionResponse(BaseModel):
    """Cooking instruction step."""

    step_number: int = Field(..., ge=1, description="Step number in sequence")
    instruction: str = Field(..., description="Step instruction text")
    time_minutes: Optional[int] = Field(None, ge=0, description="Time required for this step")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "step_number": 1,
                    "instruction": "Preheat oven to 200°C",
                    "time_minutes": 10
                }
            ]
        }
    )


class ImageResponse(BaseModel):
    """Recipe image information."""

    id: int
    url: str = Field(..., description="Image URL")
    image_type: ImageType = Field(..., description="Image type classification")
    display_order: int = Field(0, description="Display order")
    alt_text: Optional[str] = Field(None, description="Alternative text for accessibility")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "url": "https://example.com/image.jpg",
                    "image_type": "hero",
                    "display_order": 0,
                    "alt_text": "Delicious pasta dish",
                    "width": 1920,
                    "height": 1080
                }
            ]
        }
    )


class NutritionResponse(BaseModel):
    """Nutritional information per serving."""

    calories: Optional[Decimal] = Field(None, ge=0, description="Calories per serving")
    protein_g: Optional[Decimal] = Field(None, ge=0, description="Protein in grams")
    carbohydrates_g: Optional[Decimal] = Field(None, ge=0, description="Carbohydrates in grams (also called carbs_g)")
    fat_g: Optional[Decimal] = Field(None, ge=0, description="Fat in grams")
    saturated_fat_g: Optional[Decimal] = Field(None, ge=0, description="Saturated fat in grams")
    fiber_g: Optional[Decimal] = Field(None, ge=0, description="Fiber in grams")
    sugar_g: Optional[Decimal] = Field(None, ge=0, description="Sugar in grams")
    sodium_mg: Optional[Decimal] = Field(None, ge=0, description="Sodium in milligrams")
    cholesterol_mg: Optional[Decimal] = Field(None, ge=0, description="Cholesterol in milligrams")
    serving_size_g: Optional[int] = Field(None, description="Serving size in grams")

    @property
    def carbs_g(self) -> Optional[Decimal]:
        """Alias for carbohydrates_g for backward compatibility."""
        return self.carbohydrates_g

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "calories": 450,
                    "protein_g": 35,
                    "carbohydrates_g": 40,
                    "fat_g": 15,
                    "fiber_g": 8,
                    "sugar_g": 6,
                    "sodium_mg": 600
                }
            ]
        }
    )


class CategoryResponse(BaseModel):
    """Recipe category information."""

    id: int
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    category_type: CategoryType = Field(..., description="Category type")
    description: Optional[str] = Field(None, description="Category description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Italian",
                    "slug": "italian",
                    "category_type": "cuisine",
                    "description": "Traditional Italian cuisine"
                }
            ]
        }
    )


class DietaryTagResponse(BaseModel):
    """Dietary tag information."""

    id: int
    name: str = Field(..., description="Tag name (e.g., 'Vegan', 'Keto')")
    slug: str = Field(..., description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Tag description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Vegan",
                    "slug": "vegan",
                    "description": "Contains no animal products"
                }
            ]
        }
    )


class AllergenResponse(BaseModel):
    """Allergen information."""

    id: int
    name: str = Field(..., description="Allergen name (e.g., 'Nuts', 'Dairy')")
    description: Optional[str] = Field(None, description="Allergen description")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Dairy",
                    "description": "Contains milk or milk products"
                }
            ]
        }
    )


# ============================================================================
# MAIN RECIPE SCHEMAS
# ============================================================================

class RecipeBase(BaseModel):
    """Base recipe information shared across schemas."""

    name: str = Field(..., min_length=1, max_length=500, description="Recipe name")
    description: Optional[str] = Field(None, description="Recipe description")
    cooking_time_minutes: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    prep_time_minutes: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Difficulty level")
    servings: int = Field(2, ge=1, description="Number of servings")

    model_config = ConfigDict(from_attributes=True)


class RecipeListItem(RecipeBase):
    """Lightweight recipe information for list views."""

    id: int
    slug: str = Field(..., description="URL-friendly slug")
    total_time_minutes: Optional[int] = Field(None, description="Total time (prep + cooking)")
    categories: list[CategoryResponse] = Field(default_factory=list, description="Recipe categories")
    dietary_tags: list[DietaryTagResponse] = Field(default_factory=list, description="Dietary tags")
    allergens: list[AllergenResponse] = Field(default_factory=list, description="Allergens")
    main_image: Optional[ImageResponse] = Field(None, description="Main recipe image")
    nutrition_summary: Optional[dict[str, Optional[Decimal]]] = Field(
        None,
        description="Basic nutrition (calories, protein, carbs, fat)"
    )
    is_active: bool = Field(True, description="Whether recipe is active")
    is_favorite: Optional[bool] = Field(None, description="Whether recipe is in user's favorites (null if not authenticated)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Spaghetti Carbonara",
                    "slug": "spaghetti-carbonara",
                    "description": "Classic Italian pasta dish",
                    "cooking_time_minutes": 20,
                    "prep_time_minutes": 10,
                    "total_time_minutes": 30,
                    "difficulty": "medium",
                    "servings": 2,
                    "categories": [{"id": 1, "name": "Italian", "slug": "italian", "category_type": "cuisine"}],
                    "dietary_tags": [],
                    "allergens": [{"id": 1, "name": "Dairy"}],
                    "nutrition_summary": {
                        "calories": 550,
                        "protein_g": 25,
                        "carbohydrates_g": 60,
                        "fat_g": 22
                    },
                    "is_active": True
                }
            ]
        }
    )


class RecipeResponse(RecipeBase):
    """Complete recipe information with all details."""

    id: int
    gousto_id: str = Field(..., description="Original Gousto recipe ID")
    slug: str = Field(..., description="URL-friendly slug")
    total_time_minutes: Optional[int] = Field(None, description="Total time (prep + cooking)")
    source_url: str = Field(..., description="Original recipe URL")
    date_scraped: datetime = Field(..., description="When recipe was scraped")
    last_updated: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(True, description="Whether recipe is active")

    # Related entities
    ingredients: list[IngredientResponse] = Field(default_factory=list, description="Recipe ingredients")
    instructions: list[InstructionResponse] = Field(default_factory=list, description="Cooking instructions")
    categories: list[CategoryResponse] = Field(default_factory=list, description="Recipe categories")
    dietary_tags: list[DietaryTagResponse] = Field(default_factory=list, description="Dietary tags")
    allergens: list[AllergenResponse] = Field(default_factory=list, description="Allergens")
    images: list[ImageResponse] = Field(default_factory=list, description="Recipe images")
    nutritional_info: Optional[NutritionResponse] = Field(None, description="Nutritional information")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "gousto_id": "gousto-123",
                    "slug": "spaghetti-carbonara",
                    "name": "Spaghetti Carbonara",
                    "description": "Classic Italian pasta dish with eggs, cheese, and pancetta",
                    "cooking_time_minutes": 20,
                    "prep_time_minutes": 10,
                    "total_time_minutes": 30,
                    "difficulty": "medium",
                    "servings": 2,
                    "source_url": "https://www.gousto.co.uk/cookbook/pasta-recipes/spaghetti-carbonara",
                    "date_scraped": "2026-01-20T10:00:00Z",
                    "last_updated": "2026-01-20T10:00:00Z",
                    "is_active": True,
                    "ingredients": [],
                    "instructions": [],
                    "categories": [],
                    "dietary_tags": [],
                    "allergens": [],
                    "images": [],
                    "nutritional_info": None
                }
            ]
        }
    )


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class NutritionFilters(BaseModel):
    """Nutrition-based filtering criteria."""

    min_calories: Optional[int] = Field(None, ge=0, description="Minimum calories")
    max_calories: Optional[int] = Field(None, ge=0, description="Maximum calories")
    min_protein_g: Optional[Decimal] = Field(None, ge=0, description="Minimum protein in grams")
    max_protein_g: Optional[Decimal] = Field(None, ge=0, description="Maximum protein in grams")
    min_carbs_g: Optional[Decimal] = Field(None, ge=0, description="Minimum carbohydrates in grams")
    max_carbs_g: Optional[Decimal] = Field(None, ge=0, description="Maximum carbohydrates in grams")
    min_fat_g: Optional[Decimal] = Field(None, ge=0, description="Minimum fat in grams")
    max_fat_g: Optional[Decimal] = Field(None, ge=0, description="Maximum fat in grams")
    min_fiber_g: Optional[Decimal] = Field(None, ge=0, description="Minimum fiber in grams")
    max_sugar_g: Optional[Decimal] = Field(None, ge=0, description="Maximum sugar in grams")

    @field_validator('max_calories')
    @classmethod
    def validate_max_calories(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure max_calories is greater than min_calories."""
        if v is not None and info.data.get('min_calories') is not None:
            if v < info.data['min_calories']:
                raise ValueError('max_calories must be greater than or equal to min_calories')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "min_calories": 300,
                    "max_calories": 600,
                    "min_protein_g": 20,
                    "max_carbs_g": 50
                }
            ]
        }
    }


class RecipeFilters(BaseModel):
    """Comprehensive recipe filtering criteria."""

    # Category and tag filters
    category_ids: Optional[list[int]] = Field(None, description="Filter by category IDs")
    category_slugs: Optional[list[str]] = Field(None, description="Filter by category slugs")
    dietary_tag_ids: Optional[list[int]] = Field(None, description="Filter by dietary tag IDs")
    dietary_tag_slugs: Optional[list[str]] = Field(None, description="Filter by dietary tag slugs")
    exclude_allergen_ids: Optional[list[int]] = Field(None, description="Exclude recipes with these allergens")
    exclude_allergen_names: Optional[list[str]] = Field(None, description="Exclude recipes with these allergen names")

    # Time and difficulty filters
    max_cooking_time: Optional[int] = Field(None, ge=0, description="Maximum cooking time in minutes")
    max_prep_time: Optional[int] = Field(None, ge=0, description="Maximum prep time in minutes")
    max_total_time: Optional[int] = Field(None, ge=0, description="Maximum total time in minutes")
    difficulty: Optional[list[DifficultyLevel]] = Field(None, description="Filter by difficulty levels")

    # Servings filter
    min_servings: Optional[int] = Field(None, ge=1, description="Minimum number of servings")
    max_servings: Optional[int] = Field(None, ge=1, description="Maximum number of servings")

    # Search
    search_query: Optional[str] = Field(None, min_length=1, description="Search in recipe name and description")

    # Ingredient filters
    include_ingredients: Optional[list[str]] = Field(None, description="Must include these ingredients")
    exclude_ingredients: Optional[list[str]] = Field(None, description="Must not include these ingredients")

    # Nutrition filters (embedded)
    nutrition: Optional[NutritionFilters] = Field(None, description="Nutrition-based filters")

    # Active status
    only_active: bool = Field(True, description="Only show active recipes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "category_slugs": ["italian", "pasta"],
                    "dietary_tag_slugs": ["vegetarian"],
                    "exclude_allergen_names": ["nuts", "shellfish"],
                    "max_total_time": 45,
                    "difficulty": ["easy", "medium"],
                    "nutrition": {
                        "max_calories": 600,
                        "min_protein_g": 20
                    },
                    "only_active": True
                }
            ]
        }
    }
