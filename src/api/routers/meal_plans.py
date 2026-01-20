"""
Meal plan generation endpoints for FastAPI.
Provides meal plan generation with basic and nutrition-based constraints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.api.services.meal_plan_service import MealPlanService
from src.api.schemas import MealPlanGenerateRequest, MealPlanResponse

router = APIRouter(
    prefix="/meal-plans",
    tags=["meal-plans"],
)


@router.post(
    "/generate",
    response_model=dict,
    summary="Generate a basic meal plan",
    status_code=status.HTTP_201_CREATED
)
def generate_meal_plan(
    db: DatabaseSession,
    min_protein_score: float = 40.0,
    max_carb_score: float = 40.0,
    include_breakfast: bool = True,
    include_lunch: bool = True,
    include_dinner: bool = True,
    user: OptionalUser = None,
):
    """
    Generate a weekly meal plan using ingredient analysis.

    This endpoint uses ingredient-based scoring to select recipes.
    Scores are relative (0-100 scale) based on ingredient composition.

    Parameters:
    - min_protein_score: Minimum protein score (0-100, default 40)
    - max_carb_score: Maximum carb score (0-100, default 40)
    - include_breakfast: Include breakfast recipes (default true)
    - include_lunch: Include lunch recipes (default true)
    - include_dinner: Include dinner recipes (default true)

    Returns a 7-day meal plan with recipe details.
    """
    service = MealPlanService(db)

    try:
        meal_plan = service.generate_meal_plan(
            min_protein_score=min_protein_score,
            max_carb_score=max_carb_score,
            include_breakfast=include_breakfast,
            include_lunch=include_lunch,
            include_dinner=include_dinner,
            use_nutrition_data=False
        )

        return meal_plan

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate meal plan: {str(e)}"
        )


@router.post(
    "/generate-nutrition",
    response_model=dict,
    summary="Generate a meal plan with nutrition constraints",
    status_code=status.HTTP_201_CREATED
)
def generate_nutrition_meal_plan(
    db: DatabaseSession,
    min_protein_g: float = 25.0,
    max_carbs_g: float = 30.0,
    min_calories: Optional[float] = None,
    max_calories: Optional[float] = None,
    include_breakfast: bool = True,
    include_lunch: bool = True,
    include_dinner: bool = True,
    user: OptionalUser = None,
):
    """
    Generate a weekly meal plan using actual nutrition data.

    This endpoint filters recipes by their actual nutritional values
    (from the nutritional_info table) and generates a balanced meal plan.

    Parameters:
    - min_protein_g: Minimum protein per recipe in grams (default 25)
    - max_carbs_g: Maximum carbs per recipe in grams (default 30)
    - min_calories: Minimum calories per recipe (optional)
    - max_calories: Maximum calories per recipe (optional)
    - include_breakfast: Include breakfast recipes (default true)
    - include_lunch: Include lunch recipes (default true)
    - include_dinner: Include dinner recipes (default true)

    Returns a 7-day meal plan with detailed nutrition information.
    """
    service = MealPlanService(db)

    try:
        meal_plan = service.generate_nutrition_meal_plan(
            min_protein_g=min_protein_g,
            max_carbs_g=max_carbs_g,
            min_calories=min_calories,
            max_calories=max_calories,
            include_breakfast=include_breakfast,
            include_lunch=include_lunch,
            include_dinner=include_dinner
        )

        return meal_plan

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate nutrition meal plan: {str(e)}"
        )


@router.post(
    "/generate-advanced",
    response_model=dict,
    summary="Generate meal plan with advanced constraints (future)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    deprecated=True
)
def generate_advanced_meal_plan(
    request: MealPlanGenerateRequest,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Generate a meal plan with comprehensive constraints.

    This endpoint is planned for future implementation and will support:
    - Custom day ranges (1-30 days)
    - Start date specification
    - Detailed nutrition constraints per meal
    - Recipe variety settings
    - Shopping list optimization
    - Category and allergen filtering

    Currently returns 501 Not Implemented.
    Use /generate or /generate-nutrition for now.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Advanced meal plan generation coming soon. Use /generate or /generate-nutrition endpoints."
    )
