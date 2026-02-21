"""
Cost estimation endpoints for recipes and meal plans.
"""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.api.schemas.cost import (
    RecipeCostResponse,
    MealPlanCostBreakdown,
    CostEstimateRequest,
    BudgetRecipesResponse,
    RecipeWithCost,
)
from src.api.schemas.recipe import RecipeListItem
from src.database.models import Recipe
from src.meal_planner.cost_estimator import CostEstimator
from src.utils.logger import get_logger

logger = get_logger("api.cost")

router = APIRouter(
    prefix="/cost",
    tags=["cost-estimation"],
)


@router.get(
    "/recipes/budget",
    response_model=BudgetRecipesResponse,
    summary="Get recipes within budget"
)
def get_recipes_within_budget(
    max_cost: float = Query(..., ge=0, description="Maximum cost per serving (GBP)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recipes to return"),
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Find recipes that fit within a specified budget.

    Returns recipes sorted by cost (cheapest first) that are under
    the specified maximum cost per serving.

    Parameters:
    - max_cost: Maximum cost per serving in GBP
    - limit: Maximum number of recipes to return (1-100)

    Returns list of recipes with cost information.
    """
    estimator = CostEstimator(db)

    try:
        max_cost_decimal = Decimal(str(max_cost))

        # Get cheapest recipes
        recipe_costs = estimator.get_cheapest_recipes(
            limit=limit * 2,  # Get extra to filter
            max_cost_per_serving=max_cost_decimal
        )

        # Convert to response format
        recipes_with_cost = []
        for recipe, cost_per_serving in recipe_costs[:limit]:
            recipes_with_cost.append(
                RecipeWithCost(
                    recipe=RecipeListItem(
                        id=recipe.id,
                        name=recipe.name,
                        slug=recipe.slug,
                        cooking_time_minutes=recipe.cooking_time_minutes,
                        difficulty=recipe.difficulty,
                        servings=recipe.servings,
                        source_url=recipe.source_url,
                        description=recipe.description
                    ),
                    cost=float(cost_per_serving * Decimal('2.0')),  # Assume 2 servings
                    cost_per_serving=float(cost_per_serving)
                )
            )

        # Calculate average
        avg_cost = None
        if recipes_with_cost:
            avg_cost = sum(r.cost_per_serving for r in recipes_with_cost) / len(recipes_with_cost)

        return BudgetRecipesResponse(
            recipes=recipes_with_cost,
            total_count=len(recipes_with_cost),
            max_cost=max_cost,
            average_cost=avg_cost
        )

    except Exception as e:
        logger.error(f"Error finding budget recipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find budget recipes: {str(e)}"
        )


@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeCostResponse,
    summary="Get cost estimate for a recipe"
)
def get_recipe_cost(
    recipe_id: int,
    servings: int = Query(2, ge=1, le=12, description="Number of servings"),
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Get cost estimate for a specific recipe.

    Calculates the cost based on ingredient prices in the database,
    with intelligent fallback estimation for missing price data.

    Parameters:
    - recipe_id: Recipe ID to estimate cost for
    - servings: Number of servings (default 2)

    Returns detailed cost breakdown including:
    - Total cost
    - Cost per serving
    - Breakdown by ingredient category
    - Number of ingredients with estimated prices
    """
    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    # Estimate cost
    estimator = CostEstimator(db)

    try:
        total_cost = estimator.estimate_recipe_cost(recipe, servings=servings)
        cost_per_serving = total_cost / Decimal(str(servings))

        # Get breakdown by category (simplified - would need more detailed tracking)
        return RecipeCostResponse(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            total_cost=float(total_cost),
            cost_per_serving=float(cost_per_serving),
            servings=servings,
            estimated=True,  # Most will be estimated unless we have full price DB
            cost_breakdown={},  # Could be enhanced with detailed tracking
            missing_prices=None
        )

    except Exception as e:
        logger.error(f"Error estimating cost for recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to estimate recipe cost: {str(e)}"
        )


@router.post(
    "/meal-plans/estimate",
    response_model=MealPlanCostBreakdown,
    summary="Estimate cost for a meal plan",
    status_code=status.HTTP_200_OK
)
def estimate_meal_plan_cost(
    request: CostEstimateRequest,
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Estimate total cost for a meal plan.

    Accepts either a list of recipe IDs or a full meal plan structure.
    Returns comprehensive cost breakdown including:
    - Total cost
    - Cost by ingredient category
    - Cost by day
    - Average cost per meal
    - Cost-saving suggestions

    Parameters:
    - recipe_ids: List of recipe IDs (for simple estimation)
    - meal_plan_data: Full meal plan structure (for detailed estimation)
    - servings_per_meal: Servings per meal (default 2)
    """
    estimator = CostEstimator(db)

    try:
        if request.meal_plan_data:
            # Use meal plan structure
            breakdown = estimator.estimate_meal_plan_cost(
                meal_plan=request.meal_plan_data,
                servings_per_meal=request.servings_per_meal
            )
            return MealPlanCostBreakdown(**breakdown.to_dict())

        elif request.recipe_ids:
            # Build simple meal plan from recipe IDs
            recipes = db.query(Recipe).filter(
                Recipe.id.in_(request.recipe_ids)
            ).all()

            if not recipes:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No recipes found with provided IDs"
                )

            # Create simple plan structure
            simple_plan = {
                'weeks': [{
                    'days': [{
                        'day_number': i + 1,
                        'meals': {'meal': recipe}
                    } for i, recipe in enumerate(recipes)]
                }]
            }

            breakdown = estimator.estimate_meal_plan_cost(
                meal_plan=simple_plan,
                servings_per_meal=request.servings_per_meal
            )

            # Add per-day average
            result_dict = breakdown.to_dict()
            if breakdown.total_meals > 0:
                # Estimate days (3 meals per day)
                estimated_days = max(1, breakdown.total_meals // 3)
                result_dict['per_day_average'] = float(breakdown.total) / estimated_days

            return MealPlanCostBreakdown(**result_dict)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either recipe_ids or meal_plan_data"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating meal plan cost: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to estimate meal plan cost: {str(e)}"
        )


@router.get(
    "/recipes/{recipe_id}/alternatives",
    response_model=BudgetRecipesResponse,
    summary="Get cheaper alternatives to a recipe"
)
def get_budget_alternatives(
    recipe_id: int,
    max_budget: Optional[float] = Query(None, ge=0, description="Maximum budget per serving (GBP)"),
    limit: int = Query(10, ge=1, le=50, description="Number of alternatives to return"),
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Find cheaper alternative recipes similar to the specified recipe.

    Searches for recipes with similar characteristics (cooking time, servings)
    but at a lower cost point.

    Parameters:
    - recipe_id: Original recipe ID
    - max_budget: Maximum budget per serving (optional, defaults to 80% of original cost)
    - limit: Number of alternatives to return (1-50)

    Returns list of alternative recipes sorted by cost.
    """
    # Get original recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    estimator = CostEstimator(db)

    try:
        # If no budget specified, use 80% of original recipe cost
        if max_budget is None:
            original_cost = estimator.estimate_recipe_cost(recipe, servings=2)
            max_budget_decimal = (original_cost / Decimal('2.0')) * Decimal('0.8')
        else:
            max_budget_decimal = Decimal(str(max_budget))

        # Get alternatives
        alternatives = estimator.get_budget_alternatives(
            recipe=recipe,
            max_budget=max_budget_decimal,
            limit=limit
        )

        # Convert to response format
        recipes_with_cost = []
        for alt_recipe, cost_per_serving in alternatives:
            recipes_with_cost.append(
                RecipeWithCost(
                    recipe=RecipeListItem(
                        id=alt_recipe.id,
                        name=alt_recipe.name,
                        slug=alt_recipe.slug,
                        cooking_time_minutes=alt_recipe.cooking_time_minutes,
                        difficulty=alt_recipe.difficulty,
                        servings=alt_recipe.servings,
                        source_url=alt_recipe.source_url,
                        description=alt_recipe.description
                    ),
                    cost=float(cost_per_serving * Decimal('2.0')),
                    cost_per_serving=float(cost_per_serving)
                )
            )

        # Calculate average
        avg_cost = None
        if recipes_with_cost:
            avg_cost = sum(r.cost_per_serving for r in recipes_with_cost) / len(recipes_with_cost)

        return BudgetRecipesResponse(
            recipes=recipes_with_cost,
            total_count=len(recipes_with_cost),
            max_cost=float(max_budget_decimal),
            average_cost=avg_cost
        )

    except Exception as e:
        logger.error(f"Error finding budget alternatives for recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find budget alternatives: {str(e)}"
        )
