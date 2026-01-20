"""
Multi-week meal planning with variety enforcement and protein rotation.
Generates meal plans for 1-12 weeks with sophisticated variety constraints.
"""

import random
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import (
    Recipe, RecipeIngredient, Ingredient, Category,
    RecipeCategory, NutritionalInfo
)
from src.meal_planner.planner import MealPlanner
from src.utils.logger import get_logger

logger = get_logger("multi_week_planner")


class VarietyConfig:
    """Configuration for variety enforcement in meal planning."""

    def __init__(
        self,
        min_days_between_repeat: int = 7,
        max_same_cuisine_per_week: int = 3,
        protein_rotation: bool = True,
        max_same_protein_per_week: int = 3,
        enforce_ingredient_variety: bool = True,
        min_unique_ingredients_per_week: int = 30
    ):
        """
        Initialize variety configuration.

        Args:
            min_days_between_repeat: Minimum days before repeating a recipe
            max_same_cuisine_per_week: Maximum recipes from same cuisine per week
            protein_rotation: Whether to rotate protein sources
            max_same_protein_per_week: Maximum recipes with same protein per week
            enforce_ingredient_variety: Whether to enforce ingredient variety
            min_unique_ingredients_per_week: Minimum unique ingredients per week
        """
        self.min_days_between_repeat = min_days_between_repeat
        self.max_same_cuisine_per_week = max_same_cuisine_per_week
        self.protein_rotation = protein_rotation
        self.max_same_protein_per_week = max_same_protein_per_week
        self.enforce_ingredient_variety = enforce_ingredient_variety
        self.min_unique_ingredients_per_week = min_unique_ingredients_per_week


class MultiWeekPlanner(MealPlanner):
    """
    Generates multi-week meal plans with variety enforcement.
    Extends base MealPlanner with advanced variety and rotation logic.
    """

    # Protein type detection keywords
    PROTEIN_TYPES = {
        'chicken': ['chicken', 'poultry'],
        'beef': ['beef', 'steak', 'mince', 'ground beef'],
        'pork': ['pork', 'bacon', 'ham', 'sausage'],
        'fish': ['fish', 'salmon', 'cod', 'tuna', 'basa', 'haddock', 'trout'],
        'seafood': ['prawn', 'shrimp', 'scallop', 'lobster', 'crab', 'mussel'],
        'lamb': ['lamb'],
        'turkey': ['turkey'],
        'duck': ['duck'],
        'vegetarian': ['tofu', 'tempeh', 'seitan', 'halloumi', 'paneer'],
        'legumes': ['lentil', 'chickpea', 'bean', 'pulse']
    }

    # Cuisine detection keywords
    CUISINE_TYPES = {
        'italian': ['italian', 'pasta', 'risotto', 'pizza', 'carbonara', 'pesto'],
        'asian': ['asian', 'stir fry', 'wok', 'noodle', 'ramen', 'curry'],
        'mexican': ['mexican', 'taco', 'burrito', 'fajita', 'enchilada', 'quesadilla'],
        'indian': ['indian', 'curry', 'tikka', 'masala', 'biryani', 'tandoori'],
        'mediterranean': ['mediterranean', 'greek', 'hummus', 'falafel', 'tzatziki'],
        'american': ['american', 'burger', 'bbq', 'grill'],
        'french': ['french', 'coq au vin', 'ratatouille', 'bouillabaisse'],
        'british': ['british', 'pie', 'roast', 'yorkshire'],
        'thai': ['thai', 'pad thai', 'tom yum', 'green curry'],
        'chinese': ['chinese', 'szechuan', 'canton'],
        'japanese': ['japanese', 'teriyaki', 'sushi', 'ramen'],
        'middle_eastern': ['middle eastern', 'shawarma', 'kebab', 'tagine']
    }

    def __init__(
        self,
        session: Session,
        weeks: int = 4,
        variety_config: Optional[VarietyConfig] = None
    ):
        """
        Initialize multi-week planner.

        Args:
            session: Database session
            weeks: Number of weeks to plan (1-12)
            variety_config: Variety enforcement configuration
        """
        super().__init__(session)

        if not 1 <= weeks <= 12:
            raise ValueError("weeks must be between 1 and 12")

        self.weeks = weeks
        self.variety_config = variety_config or VarietyConfig()
        self.recipe_cache: Dict[int, Recipe] = {}
        self.protein_cache: Dict[int, str] = {}
        self.cuisine_cache: Dict[int, str] = {}

    def generate_multi_week_plan(
        self,
        min_protein_score: float = 40.0,
        max_carb_score: float = 40.0,
        include_breakfast: bool = True,
        include_lunch: bool = True,
        include_dinner: bool = True,
        exclude_recent: Optional[List[int]] = None
    ) -> Dict:
        """
        Generate multi-week meal plan with variety enforcement.

        Args:
            min_protein_score: Minimum protein score for recipes
            max_carb_score: Maximum carb score for recipes
            include_breakfast: Include breakfast meals
            include_lunch: Include lunch meals
            include_dinner: Include dinner meals
            exclude_recent: Recipe IDs to exclude (recently used)

        Returns:
            Dictionary with weeks, days, meals, and variety scores
        """
        logger.info(f"Generating {self.weeks}-week meal plan with variety enforcement")

        # Get candidate recipes
        candidates = self.find_high_protein_low_carb_recipes(
            min_protein_score=min_protein_score,
            max_carb_score=max_carb_score,
            limit=500  # Get more candidates for variety
        )

        if len(candidates) < 21:
            logger.warning(f"Only {len(candidates)} candidates found, variety may be limited")

        # Separate breakfast and lunch/dinner recipes
        breakfast_recipes = []
        lunch_dinner_recipes = []

        for recipe, p_score, c_score in candidates:
            if exclude_recent and recipe.id in exclude_recent:
                continue

            if self._is_breakfast_suitable(recipe):
                breakfast_recipes.append((recipe, p_score, c_score))
            else:
                lunch_dinner_recipes.append((recipe, p_score, c_score))

        # Pre-cache protein and cuisine types
        for recipe, _, _ in candidates:
            self.protein_cache[recipe.id] = self._get_protein_type(recipe)
            self.cuisine_cache[recipe.id] = self._get_cuisine(recipe)

        # Generate plan week by week
        plan = {
            'weeks': [],
            'total_weeks': self.weeks,
            'total_days': self.weeks * 7,
            'variety_scores': {},
            'summary': {}
        }

        recipe_history: List[Tuple[int, int]] = []  # (recipe_id, day_index)

        for week_num in range(1, self.weeks + 1):
            week_plan = self._generate_single_week(
                week_num=week_num,
                breakfast_recipes=breakfast_recipes,
                lunch_dinner_recipes=lunch_dinner_recipes,
                recipe_history=recipe_history,
                include_breakfast=include_breakfast,
                include_lunch=include_lunch,
                include_dinner=include_dinner
            )

            plan['weeks'].append(week_plan)

        # Calculate overall variety score
        plan['variety_scores']['overall'] = self._calculate_variety_score(plan)

        # Generate summary statistics
        plan['summary'] = self._generate_summary(plan)

        logger.info(f"Multi-week plan generated successfully with variety score: {plan['variety_scores']['overall']:.1f}")

        return plan

    def _generate_single_week(
        self,
        week_num: int,
        breakfast_recipes: List[Tuple],
        lunch_dinner_recipes: List[Tuple],
        recipe_history: List[Tuple[int, int]],
        include_breakfast: bool,
        include_lunch: bool,
        include_dinner: bool
    ) -> Dict:
        """
        Generate a single week with variety constraints.

        Args:
            week_num: Week number (1-indexed)
            breakfast_recipes: Available breakfast recipes
            lunch_dinner_recipes: Available lunch/dinner recipes
            recipe_history: History of used recipes with day indices
            include_breakfast: Include breakfast meals
            include_lunch: Include lunch meals
            include_dinner: Include dinner meals

        Returns:
            Week plan dictionary
        """
        week_plan = {
            'week_number': week_num,
            'days': [],
            'protein_distribution': Counter(),
            'cuisine_distribution': Counter()
        }

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        start_day_index = (week_num - 1) * 7

        for day_idx, day_name in enumerate(days):
            day_plan = {
                'day_name': day_name,
                'day_number': start_day_index + day_idx + 1,
                'meals': {}
            }

            # Breakfast
            if include_breakfast and breakfast_recipes:
                recipe = self._select_recipe_with_variety(
                    candidates=breakfast_recipes,
                    day_index=start_day_index + day_idx,
                    recipe_history=recipe_history,
                    week_plan=week_plan
                )
                if recipe:
                    day_plan['meals']['breakfast'] = recipe
                    recipe_history.append((recipe.id, start_day_index + day_idx))

            # Lunch
            if include_lunch and lunch_dinner_recipes:
                recipe = self._select_recipe_with_variety(
                    candidates=lunch_dinner_recipes,
                    day_index=start_day_index + day_idx,
                    recipe_history=recipe_history,
                    week_plan=week_plan
                )
                if recipe:
                    day_plan['meals']['lunch'] = recipe
                    recipe_history.append((recipe.id, start_day_index + day_idx))

            # Dinner
            if include_dinner and lunch_dinner_recipes:
                recipe = self._select_recipe_with_variety(
                    candidates=lunch_dinner_recipes,
                    day_index=start_day_index + day_idx,
                    recipe_history=recipe_history,
                    week_plan=week_plan
                )
                if recipe:
                    day_plan['meals']['dinner'] = recipe
                    recipe_history.append((recipe.id, start_day_index + day_idx))

            week_plan['days'].append(day_plan)

        return week_plan

    def _select_recipe_with_variety(
        self,
        candidates: List[Tuple],
        day_index: int,
        recipe_history: List[Tuple[int, int]],
        week_plan: Dict
    ) -> Optional[Recipe]:
        """
        Select a recipe with variety constraints enforced.

        Args:
            candidates: List of (recipe, protein_score, carb_score) tuples
            day_index: Current day index (0-indexed across all weeks)
            recipe_history: History of used recipes
            week_plan: Current week plan for tracking protein/cuisine

        Returns:
            Selected recipe or None
        """
        # Filter candidates based on variety constraints
        filtered = self._enforce_variety_constraints(
            candidates=candidates,
            day_index=day_index,
            recipe_history=recipe_history,
            week_plan=week_plan
        )

        if not filtered:
            logger.warning(f"No recipes passed variety constraints on day {day_index}, relaxing constraints")
            # Fall back to less strict filtering
            filtered = [r for r in candidates if r[0].id not in [h[0] for h in recipe_history[-7:]]]
            if not filtered:
                filtered = candidates

        if not filtered:
            return None

        # Select from top candidates with some randomness
        top_n = min(10, len(filtered))
        recipe, _, _ = random.choice(filtered[:top_n])

        # Update week tracking
        protein = self.protein_cache.get(recipe.id, 'unknown')
        cuisine = self.cuisine_cache.get(recipe.id, 'unknown')

        week_plan['protein_distribution'][protein] += 1
        week_plan['cuisine_distribution'][cuisine] += 1

        return recipe

    def _enforce_variety_constraints(
        self,
        candidates: List[Tuple],
        day_index: int,
        recipe_history: List[Tuple[int, int]],
        week_plan: Dict
    ) -> List[Tuple]:
        """
        Filter candidates based on variety constraints.

        Args:
            candidates: Available candidates
            day_index: Current day index
            recipe_history: Recipe usage history
            week_plan: Current week plan

        Returns:
            Filtered list of candidates
        """
        filtered = []

        # Get recently used recipe IDs
        recent_recipe_ids = set()
        for recipe_id, used_day in recipe_history:
            if day_index - used_day < self.variety_config.min_days_between_repeat:
                recent_recipe_ids.add(recipe_id)

        for recipe, p_score, c_score in candidates:
            # Check recipe repetition
            if recipe.id in recent_recipe_ids:
                continue

            # Check protein variety
            if self.variety_config.protein_rotation:
                protein = self.protein_cache.get(recipe.id, 'unknown')
                if week_plan['protein_distribution'][protein] >= self.variety_config.max_same_protein_per_week:
                    continue

            # Check cuisine variety
            cuisine = self.cuisine_cache.get(recipe.id, 'unknown')
            if week_plan['cuisine_distribution'][cuisine] >= self.variety_config.max_same_cuisine_per_week:
                continue

            filtered.append((recipe, p_score, c_score))

        return filtered

    def _get_protein_type(self, recipe: Recipe) -> str:
        """
        Detect main protein type from recipe.

        Args:
            recipe: Recipe object

        Returns:
            Protein type string
        """
        recipe_text = f"{recipe.name} {recipe.description or ''}".lower()

        # Get ingredients
        ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()

        ingredient_text = ' '.join([ing.normalized_name for ing in ingredients]).lower()
        combined_text = f"{recipe_text} {ingredient_text}"

        # Check each protein type
        for protein_type, keywords in self.PROTEIN_TYPES.items():
            if any(kw in combined_text for kw in keywords):
                return protein_type

        return 'other'

    def _get_cuisine(self, recipe: Recipe) -> str:
        """
        Detect cuisine type from recipe categories and name.

        Args:
            recipe: Recipe object

        Returns:
            Cuisine type string
        """
        # Check categories first
        categories = self.session.query(Category).join(RecipeCategory).filter(
            RecipeCategory.recipe_id == recipe.id,
            Category.category_type == 'cuisine'
        ).all()

        if categories:
            # Use the first cuisine category
            return categories[0].slug

        # Fall back to keyword matching
        recipe_text = f"{recipe.name} {recipe.description or ''}".lower()

        for cuisine_type, keywords in self.CUISINE_TYPES.items():
            if any(kw in recipe_text for kw in keywords):
                return cuisine_type

        return 'other'

    def _calculate_variety_score(self, plan: Dict) -> float:
        """
        Calculate variety score for the entire plan (0-100).

        Args:
            plan: Complete meal plan

        Returns:
            Variety score (higher is better)
        """
        if not plan['weeks']:
            return 0.0

        all_recipe_ids = []
        all_proteins = []
        all_cuisines = []
        all_ingredients: Set[int] = set()

        for week in plan['weeks']:
            for day in week['days']:
                for meal_type, recipe in day['meals'].items():
                    all_recipe_ids.append(recipe.id)
                    all_proteins.append(self.protein_cache.get(recipe.id, 'other'))
                    all_cuisines.append(self.cuisine_cache.get(recipe.id, 'other'))

                    # Get ingredients
                    ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
                        RecipeIngredient.recipe_id == recipe.id
                    ).all()
                    all_ingredients.update([ing.id for ing in ingredients])

        if not all_recipe_ids:
            return 0.0

        # Calculate metrics
        total_meals = len(all_recipe_ids)
        unique_recipes = len(set(all_recipe_ids))
        unique_proteins = len(set(all_proteins))
        unique_cuisines = len(set(all_cuisines))
        unique_ingredients = len(all_ingredients)

        # Recipe variety score (0-40 points)
        recipe_variety = (unique_recipes / total_meals) * 40

        # Protein variety score (0-25 points)
        protein_variety = min(unique_proteins / 8, 1.0) * 25  # 8+ protein types = max score

        # Cuisine variety score (0-20 points)
        cuisine_variety = min(unique_cuisines / 6, 1.0) * 20  # 6+ cuisines = max score

        # Ingredient variety score (0-15 points)
        ingredient_variety = min(unique_ingredients / 50, 1.0) * 15  # 50+ ingredients = max score

        total_score = recipe_variety + protein_variety + cuisine_variety + ingredient_variety

        return round(total_score, 1)

    def _generate_summary(self, plan: Dict) -> Dict:
        """
        Generate summary statistics for the plan.

        Args:
            plan: Complete meal plan

        Returns:
            Summary dictionary
        """
        all_recipe_ids = []
        cooking_times = []

        for week in plan['weeks']:
            for day in week['days']:
                for meal_type, recipe in day['meals'].items():
                    all_recipe_ids.append(recipe.id)
                    if recipe.cooking_time_minutes:
                        cooking_times.append(recipe.cooking_time_minutes)

        return {
            'total_meals': len(all_recipe_ids),
            'unique_recipes': len(set(all_recipe_ids)),
            'recipe_reuse_count': len(all_recipe_ids) - len(set(all_recipe_ids)),
            'average_cooking_time': round(sum(cooking_times) / len(cooking_times), 1) if cooking_times else None,
            'total_cooking_time': sum(cooking_times) if cooking_times else None
        }
