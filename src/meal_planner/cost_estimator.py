"""
Cost estimation for recipes and meal plans.
Calculates costs based on ingredient prices with intelligent fallback estimation.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.database.models import (
    Recipe, Ingredient, RecipeIngredient, IngredientPrice,
    Unit, NutritionalInfo
)
from src.utils.logger import get_logger

logger = get_logger("cost_estimator")


class MealPlanCostBreakdown:
    """Structured cost breakdown for a meal plan."""

    def __init__(
        self,
        total: Decimal,
        by_category: Dict[str, Decimal],
        by_day: Dict[int, Decimal],
        per_meal_average: Decimal,
        savings_suggestions: List[str],
        total_meals: int,
        ingredient_count: int
    ):
        """
        Initialize cost breakdown.

        Args:
            total: Total cost for the meal plan
            by_category: Cost breakdown by ingredient category
            by_day: Cost breakdown by day
            per_meal_average: Average cost per meal
            savings_suggestions: List of cost-saving suggestions
            total_meals: Total number of meals
            ingredient_count: Total number of unique ingredients
        """
        self.total = total
        self.by_category = by_category
        self.by_day = by_day
        self.per_meal_average = per_meal_average
        self.savings_suggestions = savings_suggestions
        self.total_meals = total_meals
        self.ingredient_count = ingredient_count

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response."""
        return {
            'total': float(self.total),
            'by_category': {k: float(v) for k, v in self.by_category.items()},
            'by_day': {k: float(v) for k, v in self.by_day.items()},
            'per_meal_average': float(self.per_meal_average),
            'savings_suggestions': self.savings_suggestions,
            'total_meals': self.total_meals,
            'ingredient_count': self.ingredient_count
        }


class CostEstimator:
    """
    Estimates costs for recipes and meal plans.
    Handles missing price data with intelligent estimation.
    """

    # Default price estimates by category (GBP per 100g or unit)
    DEFAULT_PRICES = {
        'protein': Decimal('2.50'),
        'vegetable': Decimal('0.80'),
        'fruit': Decimal('1.20'),
        'grain': Decimal('0.40'),
        'dairy': Decimal('1.50'),
        'spice': Decimal('0.20'),
        'condiment': Decimal('0.30'),
        'herb': Decimal('0.15'),
        'oil': Decimal('0.50'),
        'other': Decimal('1.00')
    }

    # Common ingredient weights for estimation (grams)
    COMMON_WEIGHTS = {
        'onion': 150,
        'garlic': 5,
        'tomato': 120,
        'potato': 180,
        'carrot': 80,
        'chicken breast': 150,
        'beef': 150,
        'fish': 150,
        'egg': 50,
        'cheese': 30
    }

    def __init__(self, session: Session):
        """
        Initialize cost estimator.

        Args:
            session: Database session
        """
        self.session = session
        self._price_cache: Dict[int, Decimal] = {}

    def estimate_recipe_cost(
        self,
        recipe: Recipe,
        servings: int = 2,
        use_cache: bool = True
    ) -> Decimal:
        """
        Calculate estimated cost for a recipe.

        Args:
            recipe: Recipe object
            servings: Number of servings (for scaling)
            use_cache: Whether to use cached prices

        Returns:
            Estimated cost in GBP
        """
        # Get recipe ingredients
        recipe_ingredients = self.session.query(
            RecipeIngredient, Ingredient, Unit
        ).join(
            Ingredient, RecipeIngredient.ingredient_id == Ingredient.id
        ).outerjoin(
            Unit, RecipeIngredient.unit_id == Unit.id
        ).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()

        if not recipe_ingredients:
            logger.warning(f"No ingredients found for recipe {recipe.id}, using base estimate")
            return Decimal('5.00')

        total_cost = Decimal('0.00')

        for recipe_ing, ingredient, unit in recipe_ingredients:
            # Get ingredient price
            if use_cache and ingredient.id in self._price_cache:
                ingredient_cost = self._price_cache[ingredient.id]
            else:
                ingredient_cost = self._get_ingredient_cost(
                    ingredient=ingredient,
                    quantity=recipe_ing.quantity,
                    unit=unit
                )
                if use_cache:
                    self._price_cache[ingredient.id] = ingredient_cost

            total_cost += ingredient_cost

        # Scale by servings
        if recipe.servings and recipe.servings > 0:
            cost_per_serving = total_cost / Decimal(str(recipe.servings))
            total_cost = cost_per_serving * Decimal(str(servings))

        return total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _get_ingredient_cost(
        self,
        ingredient: Ingredient,
        quantity: Optional[Decimal],
        unit: Optional[Unit]
    ) -> Decimal:
        """
        Get cost for a single ingredient.

        Args:
            ingredient: Ingredient object
            quantity: Quantity needed
            unit: Unit of measurement

        Returns:
            Cost in GBP
        """
        # Try to get actual price from database
        price_record = self.session.query(IngredientPrice).filter(
            IngredientPrice.ingredient_id == ingredient.id,
            IngredientPrice.store == 'average'
        ).order_by(
            IngredientPrice.last_updated.desc()
        ).first()

        if price_record:
            price_per_unit = price_record.price_per_unit

            # Convert quantity to price unit
            if quantity and unit:
                # Get quantity in grams for standardization
                quantity_grams = self._estimate_quantity_grams(
                    ingredient_name=ingredient.normalized_name,
                    quantity=quantity,
                    unit=unit
                )
                # Price is typically per 100g, so divide by 100
                total_cost = price_per_unit * (quantity_grams / Decimal('100.0'))
            else:
                # Use price as-is if no quantity specified
                total_cost = price_per_unit

            return total_cost

        # Fallback to estimation
        return self.estimate_ingredient_price(ingredient, quantity, unit)

    def estimate_ingredient_price(
        self,
        ingredient: Ingredient,
        quantity: Optional[Decimal] = None,
        unit: Optional[Unit] = None
    ) -> Decimal:
        """
        Estimate ingredient price when not in database.

        Args:
            ingredient: Ingredient object
            quantity: Quantity needed
            unit: Unit of measurement

        Returns:
            Estimated price in GBP
        """
        # Get base price from category
        category = ingredient.category or 'other'
        base_price = self.DEFAULT_PRICES.get(category, self.DEFAULT_PRICES['other'])

        if not quantity:
            # Return a small default amount
            return Decimal('0.50')

        # Estimate weight if needed
        quantity_grams = self._estimate_quantity_grams(
            ingredient_name=ingredient.normalized_name,
            quantity=quantity,
            unit=unit
        )

        # Calculate cost (base_price is per 100g)
        cost = (quantity_grams / Decimal('100.0')) * base_price

        return cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _estimate_quantity_grams(
        self,
        ingredient_name: str,
        quantity: Decimal,
        unit: Optional[Unit]
    ) -> Decimal:
        """
        Estimate quantity in grams for price calculation.

        Args:
            ingredient_name: Name of ingredient
            quantity: Quantity value
            unit: Unit of measurement

        Returns:
            Estimated weight in grams
        """
        if unit and unit.unit_type == 'weight':
            # Already in weight units
            if unit.metric_equivalent:
                return quantity * unit.metric_equivalent
            # Assume grams if no conversion
            return quantity

        # Check for common ingredient weights
        for common_ing, weight in self.COMMON_WEIGHTS.items():
            if common_ing in ingredient_name:
                return Decimal(str(weight)) * quantity

        # Default estimation
        if unit and unit.unit_type == 'count':
            # Assume 100g per unit for count-based
            return quantity * Decimal('100.0')
        elif unit and unit.unit_type == 'volume':
            # Assume 1ml = 1g for volume (rough approximation)
            if unit.metric_equivalent:
                return quantity * unit.metric_equivalent
            return quantity

        # Last resort - assume small amount
        return quantity * Decimal('50.0')

    def estimate_meal_plan_cost(
        self,
        meal_plan: Dict,
        servings_per_meal: int = 2
    ) -> MealPlanCostBreakdown:
        """
        Estimate total cost for a meal plan.

        Args:
            meal_plan: Meal plan dictionary (from planner)
            servings_per_meal: Servings per meal

        Returns:
            MealPlanCostBreakdown object
        """
        total_cost = Decimal('0.00')
        by_category: Dict[str, Decimal] = defaultdict(lambda: Decimal('0.00'))
        by_day: Dict[int, Decimal] = defaultdict(lambda: Decimal('0.00'))
        meal_count = 0
        all_ingredients: set = set()

        # Handle both single-week and multi-week plans
        weeks = meal_plan.get('weeks', [])
        if not weeks:
            # Single week plan (old format)
            weeks = [{'days': [
                {'day_number': i + 1, 'meals': meal_plan.get(day, {})}
                for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            ]}]

        for week in weeks:
            for day in week['days']:
                day_cost = Decimal('0.00')
                day_num = day.get('day_number', 0)

                for meal_type, recipe in day.get('meals', {}).items():
                    # Calculate recipe cost
                    recipe_cost = self.estimate_recipe_cost(recipe, servings=servings_per_meal)
                    total_cost += recipe_cost
                    day_cost += recipe_cost
                    meal_count += 1

                    # Track by category
                    ingredients = self.session.query(Ingredient).join(RecipeIngredient).filter(
                        RecipeIngredient.recipe_id == recipe.id
                    ).all()

                    for ing in ingredients:
                        all_ingredients.add(ing.id)
                        category = ing.category or 'other'
                        # Distribute recipe cost proportionally to ingredients
                        by_category[category] += recipe_cost / Decimal(str(len(ingredients)))

                by_day[day_num] = day_cost

        # Calculate average
        per_meal_average = total_cost / Decimal(str(meal_count)) if meal_count > 0 else Decimal('0.00')

        # Generate savings suggestions
        suggestions = self._generate_savings_suggestions(
            by_category=dict(by_category),
            total_cost=total_cost,
            meal_count=meal_count
        )

        return MealPlanCostBreakdown(
            total=total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            by_category=dict(by_category),
            by_day=dict(by_day),
            per_meal_average=per_meal_average.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            savings_suggestions=suggestions,
            total_meals=meal_count,
            ingredient_count=len(all_ingredients)
        )

    def _generate_savings_suggestions(
        self,
        by_category: Dict[str, Decimal],
        total_cost: Decimal,
        meal_count: int
    ) -> List[str]:
        """
        Generate cost-saving suggestions based on spending patterns.

        Args:
            by_category: Cost breakdown by category
            total_cost: Total cost
            meal_count: Number of meals

        Returns:
            List of suggestion strings
        """
        suggestions = []

        if not by_category or total_cost == 0:
            return suggestions

        # Check protein spending
        protein_cost = by_category.get('protein', Decimal('0.00'))
        protein_pct = (protein_cost / total_cost) * 100 if total_cost > 0 else 0

        if protein_pct > 50:
            suggestions.append(
                f"Protein accounts for {protein_pct:.0f}% of costs. "
                "Consider cheaper protein sources like chicken, eggs, or plant-based options."
            )

        # Check per-meal cost
        per_meal = total_cost / Decimal(str(meal_count)) if meal_count > 0 else Decimal('0.00')

        if per_meal > Decimal('8.00'):
            suggestions.append(
                f"Average cost per meal is £{per_meal:.2f}. "
                "Look for recipes with seasonal vegetables and bulk grains to reduce costs."
            )
        elif per_meal < Decimal('4.00'):
            suggestions.append(
                f"Great job! Your average cost per meal (£{per_meal:.2f}) is very economical."
            )

        # Check vegetable spending
        veg_cost = by_category.get('vegetable', Decimal('0.00'))
        if veg_cost < total_cost * Decimal('0.15'):
            suggestions.append(
                "Consider adding more vegetables for nutritional variety without significantly increasing cost."
            )

        return suggestions

    def get_budget_alternatives(
        self,
        recipe: Recipe,
        max_budget: Decimal,
        limit: int = 10
    ) -> List[Tuple[Recipe, Decimal]]:
        """
        Find similar recipes under a budget constraint.

        Args:
            recipe: Original recipe
            max_budget: Maximum budget per serving
            limit: Number of alternatives to return

        Returns:
            List of (recipe, cost) tuples
        """
        # Get recipes with similar characteristics
        candidates = self.session.query(Recipe).filter(
            Recipe.is_active == True,
            Recipe.id != recipe.id
        )

        # Filter by similar cooking time (±15 minutes)
        if recipe.cooking_time_minutes:
            candidates = candidates.filter(
                and_(
                    Recipe.cooking_time_minutes >= recipe.cooking_time_minutes - 15,
                    Recipe.cooking_time_minutes <= recipe.cooking_time_minutes + 15
                )
            )

        # Filter by similar servings
        if recipe.servings:
            candidates = candidates.filter(Recipe.servings == recipe.servings)

        alternatives = []

        for candidate in candidates.limit(200):  # Check first 200 candidates
            cost = self.estimate_recipe_cost(candidate, servings=2)
            cost_per_serving = cost / Decimal('2.0')

            if cost_per_serving <= max_budget:
                alternatives.append((candidate, cost_per_serving))

            if len(alternatives) >= limit:
                break

        # Sort by cost
        alternatives.sort(key=lambda x: x[1])

        return alternatives[:limit]

    def get_cheapest_recipes(
        self,
        limit: int = 20,
        max_cost_per_serving: Optional[Decimal] = None
    ) -> List[Tuple[Recipe, Decimal]]:
        """
        Get cheapest recipes sorted by cost.

        Args:
            limit: Number of recipes to return
            max_cost_per_serving: Maximum cost per serving filter

        Returns:
            List of (recipe, cost_per_serving) tuples sorted by cost
        """
        recipes = self.session.query(Recipe).filter(
            Recipe.is_active == True
        ).limit(500).all()  # Sample to avoid processing entire database

        recipe_costs = []

        for recipe in recipes:
            cost = self.estimate_recipe_cost(recipe, servings=2)
            cost_per_serving = cost / Decimal('2.0')

            if max_cost_per_serving is None or cost_per_serving <= max_cost_per_serving:
                recipe_costs.append((recipe, cost_per_serving))

        # Sort by cost
        recipe_costs.sort(key=lambda x: x[1])

        return recipe_costs[:limit]
