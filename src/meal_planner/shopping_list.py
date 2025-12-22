"""
Shopping list generator for meal plans.
Creates aggregated ingredient lists from recipes.
"""

from collections import defaultdict
from typing import List, Dict, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from src.database.models import Recipe, RecipeIngredient, Ingredient, Unit
from src.utils.logger import get_logger

logger = get_logger("shopping_list")


class ShoppingListGenerator:
    """Generates shopping lists from recipes."""

    # Ingredient categories for organization
    CATEGORIES = {
        'Proteins': [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'basa', 'cod', 'tuna',
            'prawns', 'shrimp', 'turkey', 'duck', 'lamb', 'bacon', 'sausage',
            'tofu', 'tempeh', 'seitan', 'eggs', 'egg'
        ],
        'Dairy': [
            'cheese', 'milk', 'cream', 'butter', 'yogurt', 'yoghurt',
            'mozzarella', 'cheddar', 'parmesan', 'feta', 'halloumi',
            'soft cheese', 'cottage cheese', 'cream cheese'
        ],
        'Vegetables': [
            'onion', 'garlic', 'tomato', 'pepper', 'carrot', 'broccoli',
            'spinach', 'kale', 'lettuce', 'cucumber', 'courgette', 'zucchini',
            'mushroom', 'celery', 'leek', 'cabbage', 'cauliflower',
            'green beans', 'peas', 'corn', 'potato', 'sweet potato',
            'beetroot', 'radish', 'spring onion', 'chilli', 'ginger'
        ],
        'Grains & Pasta': [
            'rice', 'pasta', 'noodles', 'spaghetti', 'couscous', 'bulgur',
            'quinoa', 'oats', 'bread', 'tortilla', 'wrap', 'orzo'
        ],
        'Legumes': [
            'lentils', 'chickpeas', 'beans', 'black beans', 'kidney beans',
            'butter beans', 'cannellini beans'
        ],
        'Herbs & Spices': [
            'cumin', 'paprika', 'curry', 'oregano', 'basil', 'thyme',
            'rosemary', 'coriander', 'parsley', 'mint', 'chilli flakes',
            'turmeric', 'cinnamon', 'nutmeg', 'sage'
        ],
        'Sauces & Condiments': [
            'soy sauce', 'vinegar', 'oil', 'olive oil', 'sesame oil',
            'stock', 'paste', 'tomato paste', 'mustard', 'mayo', 'mayonnaise',
            'ketchup', 'hot sauce', 'harissa', 'pesto', 'tamarind'
        ],
        'Nuts & Seeds': [
            'almonds', 'walnuts', 'cashews', 'peanuts', 'peanut butter',
            'pine nuts', 'sesame seeds', 'sunflower seeds', 'chia seeds'
        ],
        'Other': []  # Catch-all for uncategorized items
    }

    def __init__(self, session: Session):
        """
        Initialize shopping list generator.

        Args:
            session: Database session
        """
        self.session = session

    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """
        Categorize an ingredient based on its name.

        Args:
            ingredient_name: Ingredient name

        Returns:
            Category name
        """
        name_lower = ingredient_name.lower()

        for category, keywords in self.CATEGORIES.items():
            if category == 'Other':
                continue
            if any(keyword in name_lower for keyword in keywords):
                return category

        return 'Other'

    def generate_from_recipes(
        self,
        recipe_ids: List[int],
        combine_similar: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Generate shopping list from recipe IDs.

        Args:
            recipe_ids: List of recipe IDs
            combine_similar: Combine similar ingredients

        Returns:
            Dictionary of categorized ingredients
        """
        # Collect all ingredients with quantities
        ingredient_data = defaultdict(list)

        for recipe_id in recipe_ids:
            recipe_ingredients = self.session.query(RecipeIngredient).filter_by(
                recipe_id=recipe_id
            ).all()

            for ri in recipe_ingredients:
                ingredient_data[ri.ingredient.normalized_name].append({
                    'name': ri.ingredient.name,
                    'quantity': float(ri.quantity) if ri.quantity else None,
                    'unit': ri.unit.abbreviation if ri.unit else None,
                    'preparation': ri.preparation_note,
                    'recipe_id': recipe_id,
                    'original_name': ri.ingredient.name
                })

        # Aggregate quantities
        aggregated = {}

        for normalized_name, items in ingredient_data.items():
            # Use the most common name variant
            display_name = max(set(item['original_name'] for item in items),
                             key=lambda x: sum(1 for item in items if item['original_name'] == x))

            # Group by unit
            by_unit = defaultdict(list)
            for item in items:
                unit = item['unit'] or 'piece'
                by_unit[unit].append(item)

            # Sum quantities by unit
            quantities = {}
            for unit, unit_items in by_unit.items():
                total = sum(item['quantity'] for item in unit_items if item['quantity'])
                count = len(unit_items)
                quantities[unit] = {
                    'total': total if total > 0 else None,
                    'count': count
                }

            # Get all preparation notes
            prep_notes = set(item['preparation'] for item in items if item['preparation'])

            aggregated[normalized_name] = {
                'name': display_name,
                'quantities': quantities,
                'preparations': list(prep_notes),
                'times_needed': len(items)
            }

        # Categorize
        categorized = defaultdict(list)

        for normalized_name, data in aggregated.items():
            category = self._categorize_ingredient(data['name'])
            categorized[category].append({
                'name': data['name'],
                'quantities': data['quantities'],
                'preparations': data['preparations'],
                'times_needed': data['times_needed']
            })

        # Sort each category alphabetically
        for category in categorized:
            categorized[category].sort(key=lambda x: x['name'].lower())

        return dict(categorized)

    def format_shopping_list(
        self,
        categorized_ingredients: Dict[str, List[Dict]],
        show_quantities: bool = True,
        show_preparations: bool = True
    ) -> str:
        """
        Format shopping list as readable text.

        Args:
            categorized_ingredients: Categorized ingredients
            show_quantities: Show quantities
            show_preparations: Show preparation notes

        Returns:
            Formatted shopping list
        """
        output = []
        output.append("=" * 100)
        output.append("SHOPPING LIST - WEEKLY MEAL PLAN")
        output.append("=" * 100)
        output.append("")

        # Summary
        total_items = sum(len(items) for items in categorized_ingredients.values())
        output.append(f"Total unique ingredients: {total_items}")
        output.append("")

        # Category order
        category_order = [
            'Proteins', 'Vegetables', 'Dairy', 'Grains & Pasta',
            'Legumes', 'Herbs & Spices', 'Sauces & Condiments',
            'Nuts & Seeds', 'Other'
        ]

        for category in category_order:
            if category not in categorized_ingredients:
                continue

            items = categorized_ingredients[category]
            if not items:
                continue

            output.append(f"\n{category.upper()}")
            output.append("-" * 100)

            for item in items:
                name = item['name']
                quantities = item['quantities']
                times_needed = item['times_needed']

                # Build quantity string
                qty_parts = []
                if show_quantities and quantities:
                    for unit, data in quantities.items():
                        if data['total'] and data['total'] > 0:
                            qty_parts.append(f"{data['total']:.1f} {unit}")
                        elif data['count'] > 0:
                            qty_parts.append(f"{data['count']}x")

                if qty_parts:
                    qty_str = " + ".join(qty_parts)
                    line = f"  ☐ {name} - {qty_str}"
                else:
                    line = f"  ☐ {name} - {times_needed} recipe(s)"

                output.append(line)

                # Add preparation notes
                if show_preparations and item['preparations']:
                    for prep in item['preparations']:
                        output.append(f"      → {prep}")

        output.append("\n" + "=" * 100)
        output.append("NOTE: Check your pantry for common items before shopping!")
        output.append("=" * 100)

        return '\n'.join(output)

    def generate_compact_list(
        self,
        categorized_ingredients: Dict[str, List[Dict]]
    ) -> str:
        """
        Generate compact checklist format.

        Args:
            categorized_ingredients: Categorized ingredients

        Returns:
            Compact shopping list
        """
        output = []
        output.append("SHOPPING LIST (Compact)")
        output.append("=" * 50)

        category_order = [
            'Proteins', 'Vegetables', 'Dairy', 'Grains & Pasta',
            'Legumes', 'Herbs & Spices', 'Sauces & Condiments',
            'Nuts & Seeds', 'Other'
        ]

        for category in category_order:
            if category not in categorized_ingredients:
                continue

            items = categorized_ingredients[category]
            if not items:
                continue

            output.append(f"\n{category}:")
            for item in items:
                output.append(f"  ☐ {item['name']}")

        return '\n'.join(output)


def create_shopping_list_for_recipes(
    session: Session,
    recipe_ids: List[int],
    output_path: Optional[str] = None,
    format_type: str = 'detailed'
) -> str:
    """
    Create shopping list for given recipes.

    Args:
        session: Database session
        recipe_ids: List of recipe IDs
        output_path: Optional file path to save
        format_type: 'detailed' or 'compact'

    Returns:
        Formatted shopping list
    """
    generator = ShoppingListGenerator(session)
    categorized = generator.generate_from_recipes(recipe_ids)

    if format_type == 'compact':
        shopping_list = generator.generate_compact_list(categorized)
    else:
        shopping_list = generator.format_shopping_list(categorized)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(shopping_list)
        logger.info(f"Shopping list saved to: {output_path}")

    return shopping_list
