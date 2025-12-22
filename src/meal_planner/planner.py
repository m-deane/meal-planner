"""
Meal planning system that generates weekly meal plans based on dietary criteria.
"""

import random
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.database.models import Recipe, RecipeIngredient, Ingredient
from src.utils.logger import get_logger

logger = get_logger("meal_planner")


class MealPlanner:
    """Generates meal plans based on dietary requirements."""

    # High-protein ingredients
    HIGH_PROTEIN_INGREDIENTS = {
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'cod', 'basa',
        'turkey', 'duck', 'lamb', 'prawns', 'shrimp', 'scallops',
        'eggs', 'egg whites', 'tofu', 'tempeh', 'seitan',
        'lentils', 'chickpeas', 'beans', 'quinoa',
        'cheese', 'cottage cheese', 'greek yogurt', 'halloumi', 'mozzarella',
        'nuts', 'peanut butter', 'protein'
    }

    # Low-carb compatible ingredients
    LOW_CARB_FRIENDLY = {
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'seafood', 'prawns',
        'eggs', 'cheese', 'butter', 'cream', 'olive oil',
        'spinach', 'kale', 'lettuce', 'broccoli', 'cauliflower', 'courgette',
        'zucchini', 'pepper', 'tomato', 'cucumber', 'mushroom', 'asparagus',
        'green beans', 'cabbage', 'brussels sprouts', 'avocado',
        'nuts', 'seeds', 'berries'
    }

    # High-carb ingredients to avoid
    HIGH_CARB_INGREDIENTS = {
        'pasta', 'spaghetti', 'noodles', 'rice', 'bread', 'tortilla', 'wrap',
        'potato', 'sweet potato', 'chips', 'fries',
        'couscous', 'bulgur', 'quinoa', 'barley',
        'flour', 'sugar', 'honey', 'syrup',
        'beans', 'lentils', 'chickpeas'  # Moderate carbs but included for strict low-carb
    }

    # Breakfast-suitable keywords
    BREAKFAST_KEYWORDS = {
        'egg', 'eggs', 'omelette', 'scrambled', 'fried egg', 'poached egg',
        'breakfast', 'morning', 'shakshuka', 'frittata',
        'smoked salmon', 'avocado toast', 'yogurt'
    }

    def __init__(self, session: Session):
        """
        Initialize meal planner.

        Args:
            session: Database session
        """
        self.session = session

    def _calculate_protein_score(self, recipe: Recipe) -> float:
        """
        Calculate protein likelihood score based on ingredients.

        Args:
            recipe: Recipe object

        Returns:
            Protein score (0-100)
        """
        ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()

        if not ingredients:
            return 0.0

        ingredient_names = ' '.join([ing.normalized_name for ing in ingredients]).lower()

        # Count protein ingredient matches
        protein_matches = sum(
            1 for protein in self.HIGH_PROTEIN_INGREDIENTS
            if protein in ingredient_names
        )

        # Weight by total ingredients
        score = (protein_matches / len(ingredients)) * 100

        # Bonus for multiple protein sources
        if protein_matches >= 2:
            score += 20

        # Check recipe name for protein indicators
        recipe_name_lower = recipe.name.lower()
        if any(protein in recipe_name_lower for protein in ['chicken', 'beef', 'fish', 'salmon', 'protein']):
            score += 15

        return min(score, 100.0)

    def _calculate_carb_score(self, recipe: Recipe) -> float:
        """
        Calculate carbohydrate score (lower is better for low-carb).

        Args:
            recipe: Recipe object

        Returns:
            Carb score (0-100, lower is better)
        """
        ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()

        if not ingredients:
            return 100.0  # Assume high carb if no data

        ingredient_names = ' '.join([ing.normalized_name for ing in ingredients]).lower()

        # Count high-carb ingredient matches
        carb_matches = sum(
            1 for carb in self.HIGH_CARB_INGREDIENTS
            if carb in ingredient_names
        )

        # Calculate carb score (higher = more carbs = worse for low-carb)
        carb_score = (carb_matches / len(ingredients)) * 100

        # Penalty for high-carb foods in recipe name
        recipe_name_lower = recipe.name.lower()
        if any(carb in recipe_name_lower for carb in ['pasta', 'rice', 'bread', 'potato', 'noodles']):
            carb_score += 30

        # Count low-carb friendly ingredients for inverse scoring
        low_carb_matches = sum(
            1 for item in self.LOW_CARB_FRIENDLY
            if item in ingredient_names
        )

        # Reduce score based on low-carb ingredients
        if low_carb_matches > 0:
            carb_score -= (low_carb_matches / len(ingredients)) * 50

        return max(0.0, min(carb_score, 100.0))

    def _is_breakfast_suitable(self, recipe: Recipe) -> bool:
        """
        Determine if recipe is suitable for breakfast.

        Args:
            recipe: Recipe object

        Returns:
            True if breakfast-suitable
        """
        recipe_name_lower = recipe.name.lower()
        recipe_desc_lower = (recipe.description or '').lower()

        # Check for breakfast keywords
        if any(kw in recipe_name_lower or kw in recipe_desc_lower for kw in self.BREAKFAST_KEYWORDS):
            return True

        # Quick recipes (<20 min) with eggs are likely breakfast
        if recipe.cooking_time_minutes and recipe.cooking_time_minutes <= 20:
            ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.id
            ).all()
            ingredient_text = ' '.join([ing.normalized_name for ing in ingredients]).lower()
            if 'egg' in ingredient_text:
                return True

        return False

    def find_high_protein_low_carb_recipes(
        self,
        min_protein_score: float = 40.0,
        max_carb_score: float = 40.0,
        limit: int = 200
    ) -> List[tuple]:
        """
        Find recipes likely to be high protein and low carb.

        Args:
            min_protein_score: Minimum protein score
            max_carb_score: Maximum carb score
            limit: Maximum number of recipes to return

        Returns:
            List of (recipe, protein_score, carb_score) tuples
        """
        # Get all active recipes
        recipes = self.session.query(Recipe).filter(
            Recipe.is_active == True
        ).all()

        scored_recipes = []

        for recipe in recipes:
            protein_score = self._calculate_protein_score(recipe)
            carb_score = self._calculate_carb_score(recipe)

            if protein_score >= min_protein_score and carb_score <= max_carb_score:
                scored_recipes.append((recipe, protein_score, carb_score))

        # Sort by protein score (high) and carb score (low)
        scored_recipes.sort(key=lambda x: (x[1], -x[2]), reverse=True)

        return scored_recipes[:limit]

    def generate_weekly_meal_plan(
        self,
        min_protein_score: float = 40.0,
        max_carb_score: float = 40.0,
        include_breakfast: bool = True,
        include_lunch: bool = True,
        include_dinner: bool = True
    ) -> Dict[str, Dict[str, Recipe]]:
        """
        Generate a 7-day meal plan.

        Args:
            min_protein_score: Minimum protein score
            max_carb_score: Maximum carb score
            include_breakfast: Include breakfast meals
            include_lunch: Include lunch meals
            include_dinner: Include dinner meals

        Returns:
            Dictionary with days and meals
        """
        logger.info(f"Generating meal plan (protein≥{min_protein_score}, carbs≤{max_carb_score})")

        # Find qualifying recipes
        candidates = self.find_high_protein_low_carb_recipes(
            min_protein_score=min_protein_score,
            max_carb_score=max_carb_score,
            limit=200
        )

        if len(candidates) < 21:
            logger.warning(f"Only found {len(candidates)} qualifying recipes, may have duplicates")

        # Separate breakfast and lunch/dinner recipes
        breakfast_recipes = []
        lunch_dinner_recipes = []

        for recipe, p_score, c_score in candidates:
            if self._is_breakfast_suitable(recipe):
                breakfast_recipes.append((recipe, p_score, c_score))
            else:
                lunch_dinner_recipes.append((recipe, p_score, c_score))

        logger.info(f"Found {len(breakfast_recipes)} breakfast and {len(lunch_dinner_recipes)} lunch/dinner candidates")

        # Generate meal plan
        meal_plan = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        used_recipes = set()

        for day in days:
            meal_plan[day] = {}

            # Breakfast
            if include_breakfast:
                if breakfast_recipes:
                    # Try to find unused breakfast recipe
                    available = [r for r in breakfast_recipes if r[0].id not in used_recipes]
                    if not available:
                        available = breakfast_recipes  # Allow reuse if necessary

                    recipe, _, _ = random.choice(available)
                    meal_plan[day]['breakfast'] = recipe
                    used_recipes.add(recipe.id)
                else:
                    # Use regular recipe if no breakfast found
                    if lunch_dinner_recipes:
                        recipe, _, _ = random.choice(lunch_dinner_recipes)
                        meal_plan[day]['breakfast'] = recipe

            # Lunch
            if include_lunch:
                available = [r for r in lunch_dinner_recipes if r[0].id not in used_recipes]
                if not available:
                    available = lunch_dinner_recipes

                if available:
                    recipe, _, _ = random.choice(available)
                    meal_plan[day]['lunch'] = recipe
                    used_recipes.add(recipe.id)

            # Dinner
            if include_dinner:
                available = [r for r in lunch_dinner_recipes if r[0].id not in used_recipes]
                if not available:
                    available = lunch_dinner_recipes

                if available:
                    recipe, _, _ = random.choice(available)
                    meal_plan[day]['dinner'] = recipe
                    used_recipes.add(recipe.id)

        return meal_plan

    def format_meal_plan(self, meal_plan: Dict[str, Dict[str, Recipe]]) -> str:
        """
        Format meal plan as readable text.

        Args:
            meal_plan: Meal plan dictionary

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 80)
        output.append("HIGH PROTEIN, LOW CARB MEAL PLAN - 7 DAYS")
        output.append("=" * 80)
        output.append("")

        for day, meals in meal_plan.items():
            output.append(f"\n{'=' * 80}")
            output.append(f"{day.upper()}")
            output.append('=' * 80)

            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in meals:
                    recipe = meals[meal_type]
                    output.append(f"\n{meal_type.upper()}:")
                    output.append(f"  {recipe.name}")
                    output.append(f"  Time: {recipe.cooking_time_minutes} minutes" if recipe.cooking_time_minutes else "  Time: Not specified")
                    output.append(f"  Servings: {recipe.servings}" if recipe.servings else "  Servings: Not specified")

                    # Get ingredients
                    ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
                        RecipeIngredient.recipe_id == recipe.id
                    ).all()

                    if ingredients:
                        output.append(f"  Key ingredients: {', '.join([ing.name for ing in ingredients[:5]])}")

                    output.append(f"  URL: {recipe.source_url}")

        output.append("\n" + "=" * 80)
        output.append("NOTE: This meal plan is based on ingredient analysis.")
        output.append("Actual nutrition values should be verified from the Gousto website.")
        output.append("=" * 80)

        return '\n'.join(output)


def create_meal_plan(
    session: Session,
    min_protein_score: float = 40.0,
    max_carb_score: float = 40.0
) -> str:
    """
    Create and format a weekly meal plan.

    Args:
        session: Database session
        min_protein_score: Minimum protein score
        max_carb_score: Maximum carb score

    Returns:
        Formatted meal plan string
    """
    planner = MealPlanner(session)
    meal_plan = planner.generate_weekly_meal_plan(
        min_protein_score=min_protein_score,
        max_carb_score=max_carb_score
    )
    return planner.format_meal_plan(meal_plan)
