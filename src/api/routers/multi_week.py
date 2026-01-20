"""
Multi-week meal planning endpoints with variety enforcement.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.meal_planner.multi_week_planner import MultiWeekPlanner, VarietyConfig
from src.meal_planner.cost_estimator import CostEstimator
from src.utils.logger import get_logger

logger = get_logger("api.multi_week")

router = APIRouter(
    prefix="/meal-plans",
    tags=["multi-week-planning"],
)


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

        # Format response
        response = {
            'success': True,
            'weeks': meal_plan['weeks'],
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


@router.post(
    "/calculate-variety-score",
    response_model=dict,
    summary="Calculate variety score for a meal plan"
)
def calculate_variety_score(
    meal_plan_data: dict,
    db: DatabaseSession = None,
    user: OptionalUser = None,
):
    """
    Calculate variety score for an existing meal plan.

    Analyzes a meal plan and provides a variety score (0-100) based on:
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
    - meal_plan_data: Meal plan structure to analyze

    **Returns:**
    - Overall variety score (0-100)
    - Detailed breakdown by category
    - Recommendations for improving variety
    """
    try:
        # Initialize planner for analysis
        planner = MultiWeekPlanner(session=db, weeks=1)

        # Calculate variety score
        variety_score = planner._calculate_variety_score(meal_plan_data)

        # Generate detailed breakdown
        all_recipe_ids = []
        all_proteins = []
        all_cuisines = []

        weeks = meal_plan_data.get('weeks', [])
        for week in weeks:
            for day in week.get('days', []):
                for meal_type, recipe_id in day.get('meals', {}).items():
                    if isinstance(recipe_id, int):
                        all_recipe_ids.append(recipe_id)
                    elif isinstance(recipe_id, dict):
                        all_recipe_ids.append(recipe_id.get('id'))

        unique_recipes = len(set(all_recipe_ids))
        total_meals = len(all_recipe_ids)

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
                'repetition_rate': round((1 - unique_recipes / total_meals) * 100, 1) if total_meals > 0 else 0
            },
            'recommendations': recommendations,
            'grade': _get_variety_grade(variety_score)
        }

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
