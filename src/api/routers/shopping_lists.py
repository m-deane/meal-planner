"""
Shopping list generation endpoints for FastAPI.
Provides shopping list generation from recipes and meal plans.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.api.services.shopping_list_service import ShoppingListService
from src.api.schemas import ShoppingListGenerateRequest
from src.database.models import Recipe

router = APIRouter(
    prefix="/shopping-lists",
    tags=["shopping-lists"],
)


@router.post(
    "/generate",
    response_model=dict,
    summary="Generate shopping list from recipe IDs",
    status_code=status.HTTP_201_CREATED
)
def generate_shopping_list(
    db: DatabaseSession,
    recipe_ids: List[int] = Body(..., description="List of recipe IDs to generate shopping list from"),
    combine_similar: bool = Body(True, description="Combine similar ingredients"),
    user: OptionalUser = None,
):
    """
    Generate a shopping list from a list of recipe IDs.

    Takes a list of recipe IDs and generates a consolidated shopping list
    with ingredients grouped by category.

    Features:
    - Combines similar ingredients across recipes
    - Groups by category (Proteins, Vegetables, Dairy, etc.)
    - Shows quantity totals per ingredient
    - Tracks which recipes use each ingredient

    Parameters:
    - recipe_ids: List of recipe IDs to include
    - combine_similar: Whether to combine similar ingredients (default true)

    Returns:
    - Categorized shopping list with quantities and recipe references
    """
    if not recipe_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipe_ids list cannot be empty"
        )

    service = ShoppingListService(db)

    try:
        shopping_list = service.generate_from_recipes(
            recipe_ids=recipe_ids,
            combine_similar=combine_similar
        )

        return shopping_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate shopping list: {str(e)}"
        )


@router.post(
    "/from-meal-plan",
    response_model=dict,
    summary="Generate shopping list from meal plan data",
    status_code=status.HTTP_201_CREATED
)
def generate_shopping_list_from_meal_plan(
    db: DatabaseSession,
    meal_plan: dict = Body(
        ...,
        description="Meal plan dictionary from /meal-plans/generate endpoint"
    ),
    combine_similar: bool = Body(True, description="Combine similar ingredients"),
    user: OptionalUser = None,
):
    """
    Generate a shopping list from a meal plan response.

    Takes the full meal plan dictionary returned from the meal plan generation
    endpoints and creates a consolidated shopping list for the entire week.

    This is useful for:
    - Getting a complete shopping list for a weekly meal plan
    - Batch grocery shopping preparation
    - Meal prep planning

    Parameters:
    - meal_plan: Full meal plan object from /meal-plans/generate
    - combine_similar: Whether to combine similar ingredients (default true)

    Returns:
    - Categorized shopping list for all recipes in the meal plan
    """
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid meal plan format. Must be a non-empty dictionary."
        )

    service = ShoppingListService(db)

    try:
        # Support both formats:
        # 1) {"plan": {"Monday": {"meals": {...}}}} (from /generate endpoint)
        # 2) {"Monday": {"meals": {...}}} (direct format)
        plan_source = meal_plan.get('plan', meal_plan)

        # Convert meal plan API response format to service format
        plan_data = {}
        for day, day_data in plan_source.items():
            plan_data[day] = {}
            meals = day_data.get('meals', day_data)
            for meal_type, meal_info in meals.items():
                if isinstance(meal_info, dict) and 'id' in meal_info:
                    # Fetch recipe from DB
                    recipe = db.query(Recipe).filter_by(id=meal_info['id']).first()
                    if recipe:
                        plan_data[day][meal_type] = recipe

        shopping_list = service.generate_from_meal_plan(
            meal_plan=plan_data,
            combine_similar=combine_similar
        )

        return shopping_list

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid meal plan structure: missing {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate shopping list from meal plan: {str(e)}"
        )


@router.post(
    "/generate-compact",
    response_model=dict,
    summary="Generate compact shopping list (names only)",
    status_code=status.HTTP_201_CREATED
)
def generate_compact_shopping_list(
    db: DatabaseSession,
    recipe_ids: List[int] = Body(..., description="List of recipe IDs"),
    user: OptionalUser = None,
):
    """
    Generate a simplified shopping list with just ingredient names.

    This endpoint returns a compact shopping list format suitable for:
    - Quick reference
    - Mobile displays
    - Printable checklists

    Does not include quantities, just ingredient names grouped by category.

    Parameters:
    - recipe_ids: List of recipe IDs to include

    Returns:
    - Simplified shopping list with checkboxes (unchecked by default)
    """
    if not recipe_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipe_ids list cannot be empty"
        )

    service = ShoppingListService(db)

    try:
        shopping_list = service.generate_compact_shopping_list(recipe_ids=recipe_ids)

        return shopping_list

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compact shopping list: {str(e)}"
        )


@router.post(
    "/generate-advanced",
    response_model=dict,
    summary="Generate shopping list with advanced options (future)",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    deprecated=True
)
def generate_advanced_shopping_list(
    request: ShoppingListGenerateRequest,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Generate shopping list with advanced customization options.

    This endpoint is planned for future implementation and will support:
    - Servings multiplier
    - Pantry staples exclusion
    - Optional ingredients toggle
    - Quantity rounding preferences
    - Export to multiple formats (markdown, PDF, etc.)

    Currently returns 501 Not Implemented.
    Use /generate or /generate-compact for now.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Advanced shopping list generation coming soon. Use /generate or /generate-compact endpoints."
    )
