"""
Shopping list service layer for FastAPI.
Wraps shopping list generation and provides API-friendly responses.
"""

from typing import List, Dict, Optional, Any
from collections import defaultdict

from sqlalchemy.orm import Session

from src.meal_planner.shopping_list import ShoppingListGenerator
from src.database.models import Recipe


class ShoppingListService:
    """Service for shopping list operations."""

    def __init__(self, db: Session):
        """
        Initialize shopping list service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.generator = ShoppingListGenerator(db)

    def generate_from_recipes(
        self,
        recipe_ids: List[int],
        combine_similar: bool = True
    ) -> Dict[str, Any]:
        """
        Generate shopping list from recipe IDs.

        Args:
            recipe_ids: List of recipe IDs
            combine_similar: Combine similar ingredients

        Returns:
            Formatted shopping list dictionary
        """
        categorized = self.generator.generate_from_recipes(
            recipe_ids=recipe_ids,
            combine_similar=combine_similar
        )

        return self.format_shopping_list_response(categorized, recipe_ids)

    def generate_from_meal_plan(
        self,
        meal_plan: Dict[str, Dict[str, Recipe]],
        combine_similar: bool = True
    ) -> Dict[str, Any]:
        """
        Generate shopping list from meal plan dictionary.

        Args:
            meal_plan: Meal plan dictionary from MealPlanService
            combine_similar: Combine similar ingredients

        Returns:
            Formatted shopping list dictionary
        """
        # Extract recipe IDs from meal plan
        recipe_ids = []
        for day, meals in meal_plan.items():
            for meal_type, recipe in meals.items():
                recipe_ids.append(recipe.id)

        return self.generate_from_recipes(
            recipe_ids=recipe_ids,
            combine_similar=combine_similar
        )

    def format_shopping_list_response(
        self,
        categorized_ingredients: Dict[str, List[Dict]],
        recipe_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Format shopping list for API response.

        Args:
            categorized_ingredients: Categorized ingredients from generator
            recipe_ids: Recipe IDs used

        Returns:
            Shopping list dictionary
        """
        # Calculate totals
        total_items = sum(len(items) for items in categorized_ingredients.values())
        total_categories = len(categorized_ingredients)

        # Format categories with consistent ordering
        category_order = [
            'Proteins',
            'Vegetables',
            'Dairy',
            'Grains & Pasta',
            'Legumes',
            'Herbs & Spices',
            'Sauces & Condiments',
            'Nuts & Seeds',
            'Other'
        ]

        formatted_categories = []
        for category_name in category_order:
            if category_name not in categorized_ingredients:
                continue

            items = categorized_ingredients[category_name]
            if not items:
                continue

            formatted_items = []
            for item in items:
                formatted_item = {
                    'name': item['name'],
                    'times_needed': item['times_needed'],
                    'quantities': self._format_quantities(item['quantities']),
                    'preparations': item.get('preparations', [])
                }
                formatted_items.append(formatted_item)

            formatted_categories.append({
                'name': category_name,
                'items': formatted_items,
                'item_count': len(formatted_items)
            })

        return {
            'categories': formatted_categories,
            'summary': {
                'total_items': total_items,
                'total_categories': total_categories,
                'recipes_count': len(set(recipe_ids))
            },
            'recipe_ids': list(set(recipe_ids))
        }

    def get_shopping_list_text_format(
        self,
        categorized_ingredients: Dict[str, List[Dict]],
        format_type: str = 'detailed'
    ) -> str:
        """
        Get shopping list in text format.

        Args:
            categorized_ingredients: Categorized ingredients
            format_type: 'detailed' or 'compact'

        Returns:
            Formatted text string
        """
        if format_type == 'compact':
            return self.generator.generate_compact_list(categorized_ingredients)
        else:
            return self.generator.format_shopping_list(
                categorized_ingredients,
                show_quantities=True,
                show_preparations=True
            )

    def _format_quantities(self, quantities: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Format quantities for API response.

        Args:
            quantities: Quantities by unit

        Returns:
            List of formatted quantity dictionaries
        """
        formatted = []
        for unit, data in quantities.items():
            quantity_item = {
                'unit': unit,
                'total': data.get('total'),
                'count': data.get('count')
            }
            formatted.append(quantity_item)

        return formatted

    def generate_compact_shopping_list(
        self,
        recipe_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Generate simplified shopping list (names only).

        Args:
            recipe_ids: List of recipe IDs

        Returns:
            Compact shopping list
        """
        categorized = self.generator.generate_from_recipes(recipe_ids)

        # Simplify to just category -> list of names
        simplified = {}
        category_order = [
            'Proteins', 'Vegetables', 'Dairy', 'Grains & Pasta',
            'Legumes', 'Herbs & Spices', 'Sauces & Condiments',
            'Nuts & Seeds', 'Other'
        ]

        for category in category_order:
            if category not in categorized:
                continue

            items = categorized[category]
            if not items:
                continue

            simplified[category] = [
                {'name': item['name'], 'checked': False}
                for item in items
            ]

        return {
            'categories': simplified,
            'summary': {
                'total_items': sum(len(items) for items in simplified.values()),
                'total_categories': len(simplified)
            }
        }
