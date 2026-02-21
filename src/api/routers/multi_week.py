"""
Multi-week meal planning endpoints with variety enforcement.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from pydantic import BaseModel

from src.api.dependencies import DatabaseSession, OptionalUser
from src.database.models import Recipe, Ingredient, RecipeIngredient
from src.meal_planner.multi_week_planner import MultiWeekPlanner, VarietyConfig
from src.meal_planner.cost_estimator import CostEstimator
from src.utils.logger import get_logger

logger = get_logger("api.multi_week")

router = APIRouter(
    prefix="/meal-plans",
    tags=["multi-week-planning"],
)


def _serialize_recipe(recipe) -> dict:
    """Convert a Recipe ORM object to a serializable dict."""
    return {
        'id': recipe.id,
        'name': recipe.name,
        'slug': recipe.slug,
        'description': recipe.description,
        'cooking_time': recipe.cooking_time_minutes,
        'prep_time': recipe.prep_time_minutes,
        'difficulty': recipe.difficulty,
        'servings': recipe.servings,
        'image_url': recipe.images[0].url if recipe.images else None,
    }


def _serialize_plan_weeks(weeks: list) -> list:
    """Convert all Recipe ORM objects in a plan's weeks to serializable dicts."""
    serialized_weeks = []
    for week in weeks:
        serialized_week = {
            'week_number': week['week_number'],
            'days': [],
            'protein_distribution': dict(week.get('protein_distribution', {})),
            'cuisine_distribution': dict(week.get('cuisine_distribution', {})),
        }
        for day in week['days']:
            serialized_day = {
                'day_name': day['day_name'],
                'day_number': day['day_number'],
                'meals': {}
            }
            for meal_type, recipe in day['meals'].items():
                if hasattr(recipe, 'id'):
                    serialized_day['meals'][meal_type] = _serialize_recipe(recipe)
                else:
                    serialized_day['meals'][meal_type] = recipe
            serialized_week['days'].append(serialized_day)
        serialized_weeks.append(serialized_week)
    return serialized_weeks


@router.post(
    "/generate-multi-week",
    response_model=dict,
    summary="Generate multi-week meal plan with variety enforcement",
    status_code=status.HTTP_201_CREATED
)
def generate_multi_week_plan(
    weeks: int = Query(4, ge=1, le=12, description="Number of weeks to plan (1-12)"),
    min_protein_score: float = Query(40.0, ge=0, le=100, description="Minimum protein score"),
    max_carb_score: float = Query(40.0, ge=0, le=100, description="Maximum carb score"),
    include_breakfast: bool = Query(True, description="Include breakfast meals"),
    include_lunch: bool = Query(True, description="Include lunch meals"),
    include_dinner: bool = Query(True, description="Include dinner meals"),
    min_days_between_repeat: int = Query(7, ge=1, le=30, description="Minimum days before repeating recipe"),
    max_same_cuisine_per_week: int = Query(3, ge=1, le=21, description="Max recipes from same cuisine per week"),
    max_same_protein_per_week: int = Query(3, ge=1, le=21, description="Max recipes with same protein per week"),
    protein_rotation: bool = Query(True, description="Enable protein source rotation"),
    include_cost_estimate: bool = Query(False, description="Include cost estimation"),
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Generate a multi-week meal plan with sophisticated variety enforcement.

    This endpoint creates meal plans spanning 1-12 weeks with advanced features:
    - Recipe variety enforcement (no repetition within specified days)
    - Protein source rotation (chicken, beef, fish, vegetarian, etc.)
    - Cuisine variety (limits recipes from same cuisine per week)
    - Ingredient diversity tracking
    - Optional cost estimation

    **Variety Features:**
    - Minimum days between recipe repeats (default 7 days)
    - Maximum same cuisine recipes per week (default 3)
    - Maximum same protein type per week (default 3)
    - Automatic protein rotation for balanced nutrition

    **Parameters:**
    - weeks: Number of weeks to plan (1-12)
    - min_protein_score: Minimum protein score for recipes (0-100)
    - max_carb_score: Maximum carb score for recipes (0-100)
    - include_breakfast/lunch/dinner: Meal types to include
    - min_days_between_repeat: Minimum days before repeating a recipe
    - max_same_cuisine_per_week: Max recipes from same cuisine per week
    - max_same_protein_per_week: Max recipes with same protein per week
    - protein_rotation: Whether to rotate protein sources
    - include_cost_estimate: Include cost breakdown in response

    **Returns:**
    - Multi-week meal plan with variety scores and summary statistics
    - Optional cost breakdown if requested
    """
    try:
        # Create variety configuration
        variety_config = VarietyConfig(
            min_days_between_repeat=min_days_between_repeat,
            max_same_cuisine_per_week=max_same_cuisine_per_week,
            protein_rotation=protein_rotation,
            max_same_protein_per_week=max_same_protein_per_week,
            enforce_ingredient_variety=True
        )

        # Initialize planner
        planner = MultiWeekPlanner(
            session=db,
            weeks=weeks,
            variety_config=variety_config
        )

        logger.info(f"Generating {weeks}-week meal plan with variety enforcement")

        # Generate plan
        meal_plan = planner.generate_multi_week_plan(
            min_protein_score=min_protein_score,
            max_carb_score=max_carb_score,
            include_breakfast=include_breakfast,
            include_lunch=include_lunch,
            include_dinner=include_dinner
        )

        # Add cost estimate if requested
        if include_cost_estimate:
            estimator = CostEstimator(db)
            cost_breakdown = estimator.estimate_meal_plan_cost(meal_plan, servings_per_meal=2)
            meal_plan['cost_breakdown'] = cost_breakdown.to_dict()

        # Serialize Recipe ORM objects to dicts before returning
        serialized_weeks = _serialize_plan_weeks(meal_plan['weeks'])

        # Format response
        response = {
            'success': True,
            'weeks': serialized_weeks,
            'total_weeks': meal_plan['total_weeks'],
            'total_days': meal_plan['total_days'],
            'variety_score': meal_plan['variety_scores']['overall'],
            'summary': meal_plan['summary'],
            'constraints': {
                'min_protein_score': min_protein_score,
                'max_carb_score': max_carb_score,
                'min_days_between_repeat': min_days_between_repeat,
                'max_same_cuisine_per_week': max_same_cuisine_per_week,
                'max_same_protein_per_week': max_same_protein_per_week,
                'protein_rotation': protein_rotation
            }
        }

        if include_cost_estimate:
            response['cost_breakdown'] = meal_plan.get('cost_breakdown')

        logger.info(f"Successfully generated {weeks}-week plan with variety score {meal_plan['variety_scores']['overall']:.1f}")

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating multi-week plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate multi-week meal plan: {str(e)}"
        )


class VarietyScoreRequest(BaseModel):
    """Request body for variety score calculation. Accepts recipe_ids or a full plan."""
    recipe_ids: Optional[list[int]] = None
    weeks: Optional[list] = None


@router.post(
    "/calculate-variety-score",
    response_model=dict,
    summary="Calculate variety score for a meal plan"
)
def calculate_variety_score(
    request: VarietyScoreRequest,
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Calculate variety score for an existing meal plan or list of recipe IDs.

    Analyzes recipes and provides a variety score (0-100) based on:
    - Recipe diversity (unique vs repeated recipes)
    - Protein variety (different protein sources)
    - Cuisine variety (different cuisine types)
    - Ingredient diversity (number of unique ingredients)

    **Scoring:**
    - Recipe variety: 0-40 points
    - Protein variety: 0-25 points
    - Cuisine variety: 0-20 points
    - Ingredient variety: 0-15 points

    **Parameters:**
    - recipe_ids: List of recipe IDs to analyze
    - weeks: (Alternative) Full meal plan weeks structure

    **Returns:**
    - Overall variety score (0-100)
    - Detailed breakdown by category
    - Recommendations for improving variety
    """
    try:
        all_recipe_ids = []

        if request.recipe_ids:
            # Simple mode: calculate from recipe IDs directly
            all_recipe_ids = request.recipe_ids
        elif request.weeks:
            # Full plan mode: extract recipe IDs from plan structure
            for week in request.weeks:
                for day in week.get('days', []):
                    for meal_type, recipe_data in day.get('meals', {}).items():
                        if isinstance(recipe_data, int):
                            all_recipe_ids.append(recipe_data)
                        elif isinstance(recipe_data, dict):
                            rid = recipe_data.get('id')
                            if rid:
                                all_recipe_ids.append(rid)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either recipe_ids or weeks"
            )

        if not all_recipe_ids:
            return {
                'variety_score': 0.0,
                'breakdown': {
                    'total_meals': 0,
                    'unique_recipes': 0,
                    'repetition_rate': 0
                },
                'recommendations': ["No recipes provided."],
                'grade': 'F'
            }

        # Fetch recipes from DB
        recipes = db.query(Recipe).filter(Recipe.id.in_(all_recipe_ids)).all()
        recipe_map = {r.id: r for r in recipes}

        total_meals = len(all_recipe_ids)
        unique_recipe_ids = set(all_recipe_ids)
        unique_recipes = len(unique_recipe_ids)

        # Initialize planner for protein/cuisine detection
        planner = MultiWeekPlanner(session=db, weeks=1)

        # Detect protein and cuisine types for each unique recipe
        all_proteins = []
        all_cuisines = []
        all_ingredient_ids = set()

        for rid in all_recipe_ids:
            recipe = recipe_map.get(rid)
            if recipe:
                all_proteins.append(planner._get_protein_type(recipe))
                all_cuisines.append(planner._get_cuisine(recipe))

                # Get ingredient IDs
                ingredients = db.query(Ingredient).join(RecipeIngredient).filter(
                    RecipeIngredient.recipe_id == rid
                ).all()
                all_ingredient_ids.update(ing.id for ing in ingredients)

        unique_proteins = len(set(all_proteins))
        unique_cuisines = len(set(all_cuisines))
        unique_ingredients = len(all_ingredient_ids)

        # Calculate scores (same formula as _calculate_variety_score)
        recipe_variety = (unique_recipes / total_meals) * 40 if total_meals > 0 else 0
        protein_variety = min(unique_proteins / 8, 1.0) * 25
        cuisine_variety = min(unique_cuisines / 6, 1.0) * 20
        ingredient_variety = min(unique_ingredients / 50, 1.0) * 15

        variety_score = round(recipe_variety + protein_variety + cuisine_variety + ingredient_variety, 1)

        # Generate recommendations
        recommendations = []
        if variety_score < 50:
            recommendations.append("Low variety detected. Consider rotating protein sources and cuisines more frequently.")
        if total_meals > 0 and (unique_recipes / total_meals) < 0.7:
            recommendations.append("Many repeated recipes. Try to use more unique recipes to increase variety.")
        if variety_score >= 80:
            recommendations.append("Excellent variety! Your meal plan has great diversity.")

        return {
            'variety_score': variety_score,
            'breakdown': {
                'total_meals': total_meals,
                'unique_recipes': unique_recipes,
                'unique_proteins': unique_proteins,
                'unique_cuisines': unique_cuisines,
                'unique_ingredients': unique_ingredients,
                'repetition_rate': round((1 - unique_recipes / total_meals) * 100, 1) if total_meals > 0 else 0
            },
            'recommendations': recommendations,
            'grade': _get_variety_grade(variety_score)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating variety score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate variety score: {str(e)}"
        )


@router.get(
    "/variety-guidelines",
    response_model=dict,
    summary="Get variety enforcement guidelines"
)
def get_variety_guidelines():
    """
    Get recommended variety enforcement guidelines.

    Returns best practices and recommended settings for variety enforcement
    in multi-week meal planning.

    **Guidelines include:**
    - Recommended minimum days between recipe repeats
    - Optimal cuisine distribution per week
    - Protein rotation strategies
    - Ingredient diversity targets

    **Returns:**
    - Recommended settings for different planning durations
    - Variety score interpretation guide
    - Tips for maximizing variety
    """
    return {
        'recommendations': {
            '1_week': {
                'min_days_between_repeat': 7,
                'max_same_cuisine_per_week': 3,
                'max_same_protein_per_week': 3,
                'target_variety_score': 60
            },
            '2_weeks': {
                'min_days_between_repeat': 7,
                'max_same_cuisine_per_week': 3,
                'max_same_protein_per_week': 3,
                'target_variety_score': 70
            },
            '4_weeks': {
                'min_days_between_repeat': 10,
                'max_same_cuisine_per_week': 2,
                'max_same_protein_per_week': 2,
                'target_variety_score': 80
            },
            '8_plus_weeks': {
                'min_days_between_repeat': 14,
                'max_same_cuisine_per_week': 2,
                'max_same_protein_per_week': 2,
                'target_variety_score': 85
            }
        },
        'variety_score_interpretation': {
            '90-100': 'Excellent - Outstanding variety and diversity',
            '80-89': 'Very Good - Strong variety with minimal repetition',
            '70-79': 'Good - Adequate variety with some repetition',
            '60-69': 'Fair - Moderate variety, consider more diversity',
            '0-59': 'Poor - Low variety, significant repetition'
        },
        'protein_rotation_tips': [
            'Rotate between chicken, beef, fish, and plant-based proteins',
            'Include seafood at least 2-3 times per week',
            'Try vegetarian meals 1-2 times per week for variety and cost savings',
            'Mix different cuts and preparations of the same protein'
        ],
        'cuisine_variety_tips': [
            'Alternate between different cuisine types (Italian, Asian, Mexican, etc.)',
            'Avoid more than 2-3 recipes from the same cuisine in one week',
            'Explore fusion dishes for unique flavor combinations',
            'Use spices and herbs to add variety without changing base ingredients'
        ],
        'ingredient_diversity_tips': [
            'Aim for 30-50 unique ingredients per week',
            'Include seasonal vegetables for variety and cost benefits',
            'Try one new ingredient or recipe each week',
            'Reuse ingredients across recipes to reduce waste and cost'
        ]
    }


def _get_variety_grade(score: float) -> str:
    """
    Convert variety score to letter grade.

    Args:
        score: Variety score (0-100)

    Returns:
        Letter grade (A+ to F)
    """
    if score >= 95:
        return 'A+'
    elif score >= 90:
        return 'A'
    elif score >= 85:
        return 'A-'
    elif score >= 80:
        return 'B+'
    elif score >= 75:
        return 'B'
    elif score >= 70:
        return 'B-'
    elif score >= 65:
        return 'C+'
    elif score >= 60:
        return 'C'
    elif score >= 55:
        return 'C-'
    elif score >= 50:
        return 'D'
    else:
        return 'F'
