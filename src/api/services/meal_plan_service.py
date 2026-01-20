"""
Meal plan service layer for FastAPI.
Wraps meal planning logic and provides API-friendly responses.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session

from src.meal_planner.planner import MealPlanner
from src.meal_planner.nutrition_planner import NutritionMealPlanner
from src.database.models import Recipe


class MealPlanService:
    """Service for meal plan operations."""

    def __init__(self, db: Session):
        """
        Initialize meal plan service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.planner = MealPlanner(db)
        self.nutrition_planner = NutritionMealPlanner(db)

    def generate_meal_plan(
        self,
        min_protein_score: float = 40.0,
        max_carb_score: float = 40.0,
        include_breakfast: bool = True,
        include_lunch: bool = True,
        include_dinner: bool = True,
        use_nutrition_data: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a weekly meal plan.

        Args:
            min_protein_score: Minimum protein score (0-100)
            max_carb_score: Maximum carb score (0-100)
            include_breakfast: Include breakfast meals
            include_lunch: Include lunch meals
            include_dinner: Include dinner meals
            use_nutrition_data: Use actual nutrition data instead of ingredient analysis

        Returns:
            Meal plan dictionary with metadata
        """
        planner = self.nutrition_planner if use_nutrition_data else self.planner

        meal_plan = planner.generate_weekly_meal_plan(
            min_protein_score=min_protein_score,
            max_carb_score=max_carb_score,
            include_breakfast=include_breakfast,
            include_lunch=include_lunch,
            include_dinner=include_dinner
        )

        return self.format_meal_plan_response(
            meal_plan,
            use_nutrition_data=use_nutrition_data
        )

    def generate_nutrition_meal_plan(
        self,
        min_protein_g: float = 25.0,
        max_carbs_g: float = 30.0,
        min_calories: Optional[float] = None,
        max_calories: Optional[float] = None,
        include_breakfast: bool = True,
        include_lunch: bool = True,
        include_dinner: bool = True
    ) -> Dict[str, Any]:
        """
        Generate meal plan using actual nutrition data.

        Args:
            min_protein_g: Minimum protein in grams
            max_carbs_g: Maximum carbs in grams
            min_calories: Minimum calories
            max_calories: Maximum calories
            include_breakfast: Include breakfast meals
            include_lunch: Include lunch meals
            include_dinner: Include dinner meals

        Returns:
            Meal plan with nutrition analysis
        """
        # Get filtered recipes
        candidates = self.nutrition_planner.filter_by_actual_nutrition(
            min_protein_g=min_protein_g,
            max_carbs_g=max_carbs_g,
            min_calories=min_calories,
            max_calories=max_calories,
            limit=200
        )

        # Generate meal plan
        meal_plan = self.nutrition_planner.generate_weekly_meal_plan(
            min_protein_score=40.0,  # Use default scores for now
            max_carb_score=30.0,
            include_breakfast=include_breakfast,
            include_lunch=include_lunch,
            include_dinner=include_dinner
        )

        return self.format_meal_plan_response(
            meal_plan,
            use_nutrition_data=True
        )

    def format_meal_plan_response(
        self,
        meal_plan: Dict[str, Dict[str, Recipe]],
        use_nutrition_data: bool = False
    ) -> Dict[str, Any]:
        """
        Format meal plan for API response.

        Args:
            meal_plan: Raw meal plan from planner
            use_nutrition_data: Include detailed nutrition data

        Returns:
            Formatted meal plan dictionary
        """
        formatted_days = {}
        weekly_totals = {
            'calories': 0,
            'protein_g': 0,
            'carbohydrates_g': 0,
            'fat_g': 0,
        }

        for day, meals in meal_plan.items():
            formatted_meals = {}
            daily_totals = {
                'calories': 0,
                'protein_g': 0,
                'carbohydrates_g': 0,
                'fat_g': 0,
            }

            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type not in meals:
                    continue

                recipe = meals[meal_type]

                meal_data = {
                    'id': recipe.id,
                    'slug': recipe.slug,
                    'name': recipe.name,
                    'cooking_time_minutes': recipe.cooking_time_minutes,
                    'servings': recipe.servings,
                    'source_url': recipe.source_url,
                    'difficulty': recipe.difficulty,
                }

                # Add nutrition if available
                if use_nutrition_data and recipe.nutritional_info:
                    nutrition = recipe.nutritional_info
                    meal_data['nutrition'] = {
                        'calories': float(nutrition.calories) if nutrition.calories else 0,
                        'protein_g': float(nutrition.protein_g) if nutrition.protein_g else 0,
                        'carbohydrates_g': float(nutrition.carbohydrates_g) if nutrition.carbohydrates_g else 0,
                        'fat_g': float(nutrition.fat_g) if nutrition.fat_g else 0,
                        'fiber_g': float(nutrition.fiber_g) if nutrition.fiber_g else 0,
                        'sugar_g': float(nutrition.sugar_g) if nutrition.sugar_g else 0,
                    }

                    # Update daily totals
                    for key in daily_totals.keys():
                        daily_totals[key] += meal_data['nutrition'][key]

                # Add main image
                main_image = next(
                    (img for img in recipe.images if img.image_type in ['main', 'hero']),
                    recipe.images[0] if recipe.images else None
                )
                if main_image:
                    meal_data['image_url'] = main_image.url

                formatted_meals[meal_type] = meal_data

            formatted_days[day] = {
                'meals': formatted_meals,
                'daily_totals': daily_totals if use_nutrition_data else None
            }

            # Update weekly totals
            if use_nutrition_data:
                for key in weekly_totals.keys():
                    weekly_totals[key] += daily_totals[key]

        # Calculate weekly averages
        weekly_averages = None
        if use_nutrition_data:
            num_days = len(formatted_days)
            weekly_averages = {
                key: round(value / num_days, 1) if num_days > 0 else 0
                for key, value in weekly_totals.items()
            }

            # Calculate macro percentages
            total_cals = weekly_totals['calories']
            if total_cals > 0:
                weekly_averages['protein_pct'] = round(
                    (weekly_totals['protein_g'] * 4 / total_cals) * 100, 1
                )
                weekly_averages['carbs_pct'] = round(
                    (weekly_totals['carbohydrates_g'] * 4 / total_cals) * 100, 1
                )
                weekly_averages['fat_pct'] = round(
                    (weekly_totals['fat_g'] * 9 / total_cals) * 100, 1
                )

        return {
            'plan': formatted_days,
            'weekly_totals': weekly_totals if use_nutrition_data else None,
            'weekly_averages': weekly_averages,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_days': len(formatted_days),
                'total_meals': sum(
                    len(day['meals']) for day in formatted_days.values()
                ),
                'uses_nutrition_data': use_nutrition_data
            }
        }

    def get_meal_plan_text_format(
        self,
        meal_plan: Dict[str, Dict[str, Recipe]],
        use_nutrition_data: bool = False
    ) -> str:
        """
        Get meal plan in text format (for markdown export).

        Args:
            meal_plan: Meal plan dictionary
            use_nutrition_data: Use nutrition-enhanced format

        Returns:
            Formatted text string
        """
        if use_nutrition_data:
            return self.nutrition_planner.format_nutrition_meal_plan(meal_plan)
        else:
            return self.planner.format_meal_plan(meal_plan)

    def get_recipe_ids_from_plan(
        self,
        meal_plan: Dict[str, Dict[str, Recipe]]
    ) -> List[int]:
        """
        Extract all recipe IDs from a meal plan.

        Args:
            meal_plan: Meal plan dictionary

        Returns:
            List of unique recipe IDs
        """
        recipe_ids = set()
        for day, meals in meal_plan.items():
            for meal_type, recipe in meals.items():
                recipe_ids.add(recipe.id)

        return list(recipe_ids)
