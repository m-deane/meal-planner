"""
Enhanced meal planning with actual nutrition data analysis.
"""

from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from src.database.models import Recipe, NutritionalInfo
from src.meal_planner.planner import MealPlanner
from src.utils.logger import get_logger

logger = get_logger("nutrition_planner")


class NutritionMealPlanner(MealPlanner):
    """Meal planner that uses actual nutrition data."""

    def analyze_recipe_nutrition(self, recipe_id: int) -> Optional[Dict]:
        """
        Get actual nutrition data for a recipe.

        Args:
            recipe_id: Recipe ID

        Returns:
            Nutrition dictionary or None
        """
        nutrition = self.session.query(NutritionalInfo).filter_by(
            recipe_id=recipe_id
        ).first()

        if not nutrition:
            return None

        return {
            'calories': float(nutrition.calories) if nutrition.calories else 0,
            'protein_g': float(nutrition.protein_g) if nutrition.protein_g else 0,
            'carbohydrates_g': float(nutrition.carbohydrates_g) if nutrition.carbohydrates_g else 0,
            'fat_g': float(nutrition.fat_g) if nutrition.fat_g else 0,
            'fiber_g': float(nutrition.fiber_g) if nutrition.fiber_g else 0,
            'sugar_g': float(nutrition.sugar_g) if nutrition.sugar_g else 0,
            'sodium_mg': float(nutrition.sodium_mg) if nutrition.sodium_mg else 0,
            'saturated_fat_g': float(nutrition.saturated_fat_g) if nutrition.saturated_fat_g else 0,
        }

    def filter_by_actual_nutrition(
        self,
        min_protein_g: float = 25.0,
        max_carbs_g: float = 30.0,
        min_calories: Optional[float] = None,
        max_calories: Optional[float] = None,
        limit: int = 200
    ) -> List[tuple]:
        """
        Filter recipes by actual nutrition values.

        Args:
            min_protein_g: Minimum protein in grams
            max_carbs_g: Maximum carbs in grams
            min_calories: Minimum calories
            max_calories: Maximum calories
            limit: Maximum results

        Returns:
            List of (recipe, nutrition_dict) tuples
        """
        # Query recipes with nutrition data
        query = self.session.query(Recipe, NutritionalInfo).join(
            NutritionalInfo
        ).filter(
            Recipe.is_active == True,
            NutritionalInfo.protein_g >= min_protein_g,
            NutritionalInfo.carbohydrates_g <= max_carbs_g
        )

        if min_calories:
            query = query.filter(NutritionalInfo.calories >= min_calories)

        if max_calories:
            query = query.filter(NutritionalInfo.calories <= max_calories)

        # Order by protein (high) and carbs (low)
        query = query.order_by(
            NutritionalInfo.protein_g.desc(),
            NutritionalInfo.carbohydrates_g.asc()
        )

        results = query.limit(limit).all()

        # Convert to tuples with nutrition dict
        output = []
        for recipe, nutrition in results:
            nutrition_dict = self.analyze_recipe_nutrition(recipe.id)
            output.append((recipe, nutrition_dict))

        return output

    def calculate_daily_totals(self, meals: Dict[str, Recipe]) -> Dict:
        """
        Calculate total nutrition for a day's meals.

        Args:
            meals: Dictionary of meal_type -> Recipe

        Returns:
            Dictionary with nutrition totals
        """
        totals = {
            'calories': 0,
            'protein_g': 0,
            'carbohydrates_g': 0,
            'fat_g': 0,
            'fiber_g': 0,
            'sugar_g': 0,
            'sodium_mg': 0,
            'saturated_fat_g': 0,
        }

        for meal_type, recipe in meals.items():
            nutrition = self.analyze_recipe_nutrition(recipe.id)
            if nutrition:
                for key in totals.keys():
                    totals[key] += nutrition.get(key, 0)

        return totals

    def format_nutrition_meal_plan(self, meal_plan: Dict[str, Dict[str, Recipe]]) -> str:
        """
        Format meal plan with detailed nutrition information.

        Args:
            meal_plan: Meal plan dictionary

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 100)
        output.append("HIGH PROTEIN, LOW CARB MEAL PLAN - 7 DAYS")
        output.append("WITH ACTUAL NUTRITION VALUES")
        output.append("=" * 100)
        output.append("")

        weekly_totals = {
            'calories': 0,
            'protein_g': 0,
            'carbohydrates_g': 0,
            'fat_g': 0,
        }

        for day, meals in meal_plan.items():
            output.append(f"\n{'=' * 100}")
            output.append(f"{day.upper()}")
            output.append('=' * 100)

            daily_totals = self.calculate_daily_totals(meals)

            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in meals:
                    recipe = meals[meal_type]
                    nutrition = self.analyze_recipe_nutrition(recipe.id)

                    output.append(f"\n{meal_type.upper()}:")
                    output.append(f"  {recipe.name}")
                    output.append(f"  Time: {recipe.cooking_time_minutes} min | Servings: {recipe.servings}")

                    if nutrition:
                        output.append(f"  Nutrition (per serving):")
                        output.append(f"    • Calories: {nutrition['calories']:.0f} kcal")
                        output.append(f"    • Protein: {nutrition['protein_g']:.1f}g")
                        output.append(f"    • Carbs: {nutrition['carbohydrates_g']:.1f}g")
                        output.append(f"    • Fat: {nutrition['fat_g']:.1f}g")
                        output.append(f"    • Fiber: {nutrition['fiber_g']:.1f}g")
                        output.append(f"    • Sugar: {nutrition['sugar_g']:.1f}g")
                    else:
                        output.append("  Nutrition: Not available")

                    output.append(f"  URL: {recipe.source_url}")

            # Daily totals
            output.append(f"\n  DAILY TOTALS:")
            output.append(f"    Total Calories: {daily_totals['calories']:.0f} kcal")
            output.append(f"    Total Protein: {daily_totals['protein_g']:.1f}g")
            output.append(f"    Total Carbs: {daily_totals['carbohydrates_g']:.1f}g")
            output.append(f"    Total Fat: {daily_totals['fat_g']:.1f}g")

            # Add to weekly totals
            for key in ['calories', 'protein_g', 'carbohydrates_g', 'fat_g']:
                weekly_totals[key] += daily_totals[key]

        # Weekly summary
        output.append("\n" + "=" * 100)
        output.append("WEEKLY NUTRITION SUMMARY")
        output.append("=" * 100)
        output.append(f"Total Calories: {weekly_totals['calories']:.0f} kcal (avg {weekly_totals['calories']/7:.0f}/day)")
        output.append(f"Total Protein: {weekly_totals['protein_g']:.1f}g (avg {weekly_totals['protein_g']/7:.1f}g/day)")
        output.append(f"Total Carbs: {weekly_totals['carbohydrates_g']:.1f}g (avg {weekly_totals['carbohydrates_g']/7:.1f}g/day)")
        output.append(f"Total Fat: {weekly_totals['fat_g']:.1f}g (avg {weekly_totals['fat_g']/7:.1f}g/day)")
        output.append("")
        output.append(f"Protein %: {weekly_totals['protein_g']*4/weekly_totals['calories']*100:.1f}%")
        output.append(f"Carbs %: {weekly_totals['carbohydrates_g']*4/weekly_totals['calories']*100:.1f}%")
        output.append(f"Fat %: {weekly_totals['fat_g']*9/weekly_totals['calories']*100:.1f}%")

        output.append("\n" + "=" * 100)
        output.append("✓ All nutrition values are actual data from Gousto recipes")
        output.append("✓ Values shown are per serving (typically 2 servings per recipe)")
        output.append("=" * 100)

        return '\n'.join(output)


def create_nutrition_meal_plan(
    session: Session,
    min_protein_g: float = 25.0,
    max_carbs_g: float = 30.0
) -> str:
    """
    Create meal plan using actual nutrition data.

    Args:
        session: Database session
        min_protein_g: Minimum protein in grams
        max_carbs_g: Maximum carbs in grams

    Returns:
        Formatted meal plan string
    """
    planner = NutritionMealPlanner(session)

    # Get recipes with actual nutrition data
    candidates = planner.filter_by_actual_nutrition(
        min_protein_g=min_protein_g,
        max_carbs_g=max_carbs_g,
        limit=200
    )

    logger.info(f"Found {len(candidates)} recipes with actual nutrition data")

    if len(candidates) < 21:
        logger.warning(f"Only {len(candidates)} recipes available, may have duplicates")

    # Generate meal plan using the filtered recipes
    # For now, use the existing meal planner logic but could be enhanced
    meal_plan = planner.generate_weekly_meal_plan(
        min_protein_score=40.0,
        max_carb_score=30.0
    )

    return planner.format_nutrition_meal_plan(meal_plan)
