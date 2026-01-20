"""
Meal planning schemas for API endpoints.
"""

from datetime import date as DateType
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .recipe import RecipeListItem, NutritionResponse


# ============================================================================
# ENUMS
# ============================================================================

class MealType(str, Enum):
    """Types of meals in a day."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class NutritionConstraints(BaseModel):
    """Daily nutrition targets and constraints."""

    target_calories: Optional[int] = Field(None, ge=0, description="Target daily calories")
    min_calories: Optional[int] = Field(None, ge=0, description="Minimum daily calories")
    max_calories: Optional[int] = Field(None, ge=0, description="Maximum daily calories")

    target_protein_g: Optional[Decimal] = Field(None, ge=0, description="Target daily protein in grams")
    min_protein_g: Optional[Decimal] = Field(None, ge=0, description="Minimum daily protein in grams")
    max_protein_g: Optional[Decimal] = Field(None, ge=0, description="Maximum daily protein in grams")

    target_carbs_g: Optional[Decimal] = Field(None, ge=0, description="Target daily carbs in grams")
    min_carbs_g: Optional[Decimal] = Field(None, ge=0, description="Minimum daily carbs in grams")
    max_carbs_g: Optional[Decimal] = Field(None, ge=0, description="Maximum daily carbs in grams")

    target_fat_g: Optional[Decimal] = Field(None, ge=0, description="Target daily fat in grams")
    min_fat_g: Optional[Decimal] = Field(None, ge=0, description="Minimum daily fat in grams")
    max_fat_g: Optional[Decimal] = Field(None, ge=0, description="Maximum daily fat in grams")

    max_sugar_g: Optional[Decimal] = Field(None, ge=0, description="Maximum daily sugar in grams")
    max_sodium_mg: Optional[Decimal] = Field(None, ge=0, description="Maximum daily sodium in milligrams")
    min_fiber_g: Optional[Decimal] = Field(None, ge=0, description="Minimum daily fiber in grams")

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
                    "target_calories": 2000,
                    "min_protein_g": 100,
                    "max_carbs_g": 250,
                    "max_sugar_g": 50,
                    "min_fiber_g": 25
                }
            ]
        }
    }


class MealPreferences(BaseModel):
    """User preferences for meal types."""

    include_breakfast: bool = Field(True, description="Include breakfast in meal plan")
    include_lunch: bool = Field(True, description="Include lunch in meal plan")
    include_dinner: bool = Field(True, description="Include dinner in meal plan")
    include_snacks: bool = Field(False, description="Include snacks in meal plan")

    # Meal-specific calorie distribution (as percentages)
    breakfast_calories_pct: Optional[int] = Field(
        25,
        ge=0,
        le=100,
        description="Percentage of daily calories for breakfast"
    )
    lunch_calories_pct: Optional[int] = Field(
        35,
        ge=0,
        le=100,
        description="Percentage of daily calories for lunch"
    )
    dinner_calories_pct: Optional[int] = Field(
        40,
        ge=0,
        le=100,
        description="Percentage of daily calories for dinner"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "include_breakfast": True,
                    "include_lunch": True,
                    "include_dinner": True,
                    "include_snacks": False,
                    "breakfast_calories_pct": 25,
                    "lunch_calories_pct": 35,
                    "dinner_calories_pct": 40
                }
            ]
        }
    }


class MealPlanGenerateRequest(BaseModel):
    """Request to generate a meal plan."""

    days: int = Field(7, ge=1, le=30, description="Number of days for the meal plan (1-30)")
    start_date: Optional[DateType] = Field(None, description="Start date for the meal plan")

    # Meal preferences
    meal_preferences: MealPreferences = Field(
        default_factory=MealPreferences,
        description="Meal type preferences"
    )

    # Nutrition constraints
    nutrition_constraints: Optional[NutritionConstraints] = Field(
        None,
        description="Daily nutrition targets and limits"
    )

    # Dietary preferences
    dietary_tag_ids: Optional[list[int]] = Field(None, description="Required dietary tags (e.g., vegan, keto)")
    dietary_tag_slugs: Optional[list[str]] = Field(None, description="Required dietary tag slugs")
    exclude_allergen_ids: Optional[list[int]] = Field(None, description="Allergens to exclude")
    exclude_allergen_names: Optional[list[str]] = Field(None, description="Allergen names to exclude")

    # Category preferences
    category_ids: Optional[list[int]] = Field(None, description="Preferred recipe categories")
    category_slugs: Optional[list[str]] = Field(None, description="Preferred category slugs")

    # Recipe constraints
    max_cooking_time: Optional[int] = Field(None, ge=0, description="Maximum cooking time per recipe")
    difficulty_levels: Optional[list[str]] = Field(None, description="Allowed difficulty levels")

    # Variety settings
    avoid_duplicate_recipes: bool = Field(True, description="Avoid repeating recipes in the plan")
    max_recipe_reuse: int = Field(1, ge=1, description="Maximum times a recipe can be reused")
    variety_score_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for recipe variety (0-1)")

    # Ingredient optimization
    optimize_shopping_list: bool = Field(
        True,
        description="Optimize for ingredient reuse across recipes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "days": 7,
                    "start_date": "2026-01-20",
                    "meal_preferences": {
                        "include_breakfast": True,
                        "include_lunch": True,
                        "include_dinner": True
                    },
                    "nutrition_constraints": {
                        "target_calories": 2000,
                        "min_protein_g": 100
                    },
                    "dietary_tag_slugs": ["vegetarian"],
                    "exclude_allergen_names": ["nuts"],
                    "max_cooking_time": 45,
                    "avoid_duplicate_recipes": True
                }
            ]
        }
    }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class MealSlot(BaseModel):
    """A single meal in the meal plan."""

    meal_type: MealType = Field(..., description="Type of meal")
    recipe: RecipeListItem = Field(..., description="Recipe for this meal")
    servings: int = Field(1, ge=1, description="Number of servings for this meal")
    nutrition: Optional[NutritionResponse] = Field(None, description="Nutrition for this meal")
    notes: Optional[str] = Field(None, description="Additional notes for this meal")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "meal_type": "dinner",
                    "recipe": {
                        "id": 1,
                        "name": "Spaghetti Carbonara",
                        "slug": "spaghetti-carbonara",
                        "cooking_time_minutes": 20,
                        "difficulty": "medium",
                        "servings": 2
                    },
                    "servings": 2,
                    "nutrition": {
                        "calories": 550,
                        "protein_g": 25,
                        "carbohydrates_g": 60,
                        "fat_g": 22
                    }
                }
            ]
        }
    )


class DayPlan(BaseModel):
    """Meal plan for a single day."""

    day: int = Field(..., ge=1, description="Day number in the plan")
    date: Optional[DateType] = Field(None, description="Actual date for this day")
    meals: list[MealSlot] = Field(..., description="Meals for this day")
    daily_nutrition: Optional[NutritionResponse] = Field(
        None,
        description="Total nutrition for the day"
    )
    notes: Optional[str] = Field(None, description="Notes for this day")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "day": 1,
                    "date": "2026-01-20",
                    "meals": [],
                    "daily_nutrition": {
                        "calories": 2000,
                        "protein_g": 120,
                        "carbohydrates_g": 220,
                        "fat_g": 70
                    }
                }
            ]
        }
    )


class ShoppingListPreview(BaseModel):
    """Preview of shopping list items."""

    total_items: int = Field(..., ge=0, description="Total number of unique ingredients")
    total_categories: int = Field(..., ge=0, description="Number of ingredient categories")
    sample_items: list[str] = Field(
        default_factory=list,
        description="Sample ingredients (first 10)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_items": 35,
                    "total_categories": 8,
                    "sample_items": [
                        "Chicken breast - 1.2 kg",
                        "Pasta - 600 g",
                        "Tomatoes - 10 units"
                    ]
                }
            ]
        }
    }


class MealPlanSummary(BaseModel):
    """Summary statistics for the meal plan."""

    total_recipes: int = Field(..., ge=0, description="Total number of recipes")
    unique_recipes: int = Field(..., ge=0, description="Number of unique recipes")
    total_meals: int = Field(..., ge=0, description="Total number of meals")
    average_cooking_time: Optional[float] = Field(None, description="Average cooking time in minutes")
    difficulty_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Count of recipes by difficulty"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_recipes": 21,
                    "unique_recipes": 18,
                    "total_meals": 21,
                    "average_cooking_time": 32.5,
                    "difficulty_distribution": {
                        "easy": 10,
                        "medium": 8,
                        "hard": 3
                    }
                }
            ]
        }
    }


class MealPlanResponse(BaseModel):
    """Complete meal plan response."""

    id: Optional[int] = Field(None, description="Meal plan ID if saved")
    days: list[DayPlan] = Field(..., description="Day-by-day meal plan")
    total_days: int = Field(..., ge=1, description="Total number of days")
    start_date: Optional[DateType] = Field(None, description="Start date of the plan")
    end_date: Optional[DateType] = Field(None, description="End date of the plan")

    # Aggregated nutrition
    average_daily_nutrition: Optional[NutritionResponse] = Field(
        None,
        description="Average daily nutrition"
    )
    total_nutrition: Optional[NutritionResponse] = Field(
        None,
        description="Total nutrition for entire plan"
    )

    # Additional information
    summary: MealPlanSummary = Field(..., description="Plan summary statistics")
    shopping_list_preview: Optional[ShoppingListPreview] = Field(
        None,
        description="Preview of shopping list"
    )

    # Metadata
    created_at: Optional[DateType] = Field(None, description="When the plan was created")
    constraints_used: Optional[dict] = Field(None, description="Constraints that were applied")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "days": [],
                    "total_days": 7,
                    "start_date": "2026-01-20",
                    "end_date": "2026-01-26",
                    "average_daily_nutrition": {
                        "calories": 2000,
                        "protein_g": 120,
                        "carbohydrates_g": 220,
                        "fat_g": 70
                    },
                    "summary": {
                        "total_recipes": 21,
                        "unique_recipes": 18,
                        "total_meals": 21,
                        "average_cooking_time": 32.5
                    }
                }
            ]
        }
    )
