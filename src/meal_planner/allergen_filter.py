"""
Allergen filtering system for meal planning.
Filters recipes based on user allergen profiles and provides warnings/substitutions.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Recipe, Allergen, UserAllergen, RecipeAllergen, RecipeIngredient


@dataclass
class AllergenWarning:
    """Data class for allergen warnings."""
    allergen_name: str
    severity: str
    ingredient_name: str
    message: str


class AllergenFilter:
    """Filter recipes based on user allergen profiles."""

    # Common allergen substitutions
    SUBSTITUTIONS = {
        'peanuts': {
            'peanut butter': ['sunflower seed butter', 'almond butter', 'tahini', 'soy nut butter'],
            'peanuts': ['almonds', 'cashews', 'sunflower seeds'],
            'peanut oil': ['vegetable oil', 'canola oil', 'sunflower oil']
        },
        'tree nuts': {
            'almonds': ['sunflower seeds', 'pumpkin seeds'],
            'walnuts': ['sunflower seeds', 'pumpkin seeds'],
            'cashews': ['sunflower seeds', 'white beans (for creamy texture)'],
            'almond milk': ['oat milk', 'soy milk', 'rice milk']
        },
        'dairy': {
            'milk': ['oat milk', 'soy milk', 'almond milk', 'coconut milk'],
            'butter': ['margarine', 'coconut oil', 'olive oil'],
            'cheese': ['nutritional yeast', 'vegan cheese', 'cashew cheese'],
            'cream': ['coconut cream', 'cashew cream', 'oat cream'],
            'yogurt': ['coconut yogurt', 'soy yogurt', 'almond yogurt']
        },
        'eggs': {
            'eggs': ['flax eggs (1 tbsp ground flax + 3 tbsp water)', 'chia eggs', 'applesauce (1/4 cup per egg)', 'mashed banana'],
            'egg whites': ['aquafaba (chickpea liquid)']
        },
        'gluten': {
            'wheat flour': ['rice flour', 'almond flour', 'coconut flour', 'gluten-free flour blend'],
            'pasta': ['rice pasta', 'quinoa pasta', 'chickpea pasta', 'zucchini noodles'],
            'bread': ['gluten-free bread', 'corn tortillas', 'rice cakes'],
            'soy sauce': ['tamari (gluten-free)', 'coconut aminos']
        },
        'soy': {
            'soy sauce': ['coconut aminos', 'tamari (check label)'],
            'tofu': ['chickpeas', 'white beans', 'tempeh (if allowed)'],
            'soy milk': ['oat milk', 'almond milk', 'rice milk']
        },
        'fish': {
            'fish sauce': ['soy sauce', 'tamari', 'coconut aminos'],
            'anchovies': ['capers', 'olives', 'miso paste'],
            'fish': ['chicken', 'tofu', 'mushrooms']
        },
        'shellfish': {
            'shrimp': ['chicken', 'firm white fish', 'mushrooms'],
            'crab': ['hearts of palm', 'jackfruit'],
            'oyster sauce': ['hoisin sauce', 'mushroom sauce']
        },
        'sesame': {
            'sesame oil': ['olive oil', 'avocado oil'],
            'sesame seeds': ['sunflower seeds', 'pumpkin seeds'],
            'tahini': ['sunflower seed butter', 'almond butter']
        }
    }

    def __init__(self, session: Session, user_allergens: Optional[List[UserAllergen]] = None):
        """
        Initialize allergen filter.

        Args:
            session: SQLAlchemy database session
            user_allergens: List of UserAllergen records for the user
        """
        self.session = session
        self.user_allergens = user_allergens or []

        # Build allergen lookup for quick access
        self.allergen_map = {
            ua.allergen_id: {
                'name': ua.allergen.name,
                'severity': ua.severity
            }
            for ua in self.user_allergens
        } if self.user_allergens else {}

    def filter_recipes(self, recipes: List[Recipe]) -> List[Recipe]:
        """
        Filter out recipes containing user's allergens based on severity.

        Args:
            recipes: List of Recipe objects

        Returns:
            List of safe recipes (allergens removed based on severity)
        """
        if not self.user_allergens:
            return recipes

        safe_recipes = []

        for recipe in recipes:
            if self._is_recipe_safe(recipe):
                safe_recipes.append(recipe)

        return safe_recipes

    def _is_recipe_safe(self, recipe: Recipe) -> bool:
        """
        Check if recipe is safe for user's allergen profile.

        Args:
            recipe: Recipe object

        Returns:
            True if recipe is safe to eat
        """
        if not self.user_allergens:
            return True

        recipe_allergen_ids = {allergen.id for allergen in recipe.allergens}

        for user_allergen in self.user_allergens:
            if user_allergen.allergen_id in recipe_allergen_ids:
                # If severity is 'severe' or 'avoid', recipe is not safe
                if user_allergen.severity in ['severe', 'avoid']:
                    return False
                # If severity is 'trace_ok', recipe might still be acceptable
                # (for trace amounts that might be present)

        return True

    def get_warnings(self, recipe: Recipe) -> List[AllergenWarning]:
        """
        Get allergen warnings for a recipe based on user's profile.

        Args:
            recipe: Recipe object

        Returns:
            List of AllergenWarning objects
        """
        if not self.user_allergens:
            return []

        warnings = []
        recipe_allergen_ids = {allergen.id for allergen in recipe.allergens}

        for user_allergen in self.user_allergens:
            if user_allergen.allergen_id in recipe_allergen_ids:
                allergen = user_allergen.allergen

                # Find ingredients containing this allergen
                ingredient_names = self._find_allergen_ingredients(recipe, allergen)
                ingredient_list = ", ".join(ingredient_names[:3])  # Limit to first 3
                if len(ingredient_names) > 3:
                    ingredient_list += f" and {len(ingredient_names) - 3} more"

                # Create appropriate message based on severity
                if user_allergen.severity == 'severe':
                    message = f"SEVERE ALLERGY: This recipe contains {ingredient_list} which contains {allergen.name}"
                elif user_allergen.severity == 'avoid':
                    message = f"WARNING: This recipe contains {ingredient_list} which contains {allergen.name}"
                else:  # trace_ok
                    message = f"INFO: This recipe contains {ingredient_list} which may contain trace amounts of {allergen.name}"

                warnings.append(AllergenWarning(
                    allergen_name=allergen.name,
                    severity=user_allergen.severity,
                    ingredient_name=ingredient_names[0] if ingredient_names else "Unknown",
                    message=message
                ))

        return warnings

    def _find_allergen_ingredients(self, recipe: Recipe, allergen: Allergen) -> List[str]:
        """
        Find which ingredients in a recipe contain a specific allergen.

        Args:
            recipe: Recipe object
            allergen: Allergen object

        Returns:
            List of ingredient names
        """
        ingredient_names = []
        allergen_name_lower = allergen.name.lower()

        for recipe_ingredient in recipe.ingredients_association:
            ingredient_name = recipe_ingredient.ingredient.name.lower()

            # Simple check - see if allergen name is in ingredient name
            # This is basic; a production system would use a more sophisticated mapping
            if (allergen_name_lower in ingredient_name or
                self._is_related_ingredient(allergen_name_lower, ingredient_name)):
                ingredient_names.append(recipe_ingredient.ingredient.name)

        return ingredient_names

    def _is_related_ingredient(self, allergen: str, ingredient: str) -> bool:
        """
        Check if an ingredient is related to an allergen.

        Args:
            allergen: Allergen name (lowercase)
            ingredient: Ingredient name (lowercase)

        Returns:
            True if ingredient likely contains allergen
        """
        # Common mappings
        mappings = {
            'dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'whey', 'casein', 'lactose'],
            'gluten': ['wheat', 'flour', 'bread', 'pasta', 'barley', 'rye', 'seitan'],
            'tree nuts': ['almond', 'walnut', 'cashew', 'pecan', 'pistachio', 'hazelnut', 'macadamia'],
            'shellfish': ['shrimp', 'crab', 'lobster', 'prawn', 'crayfish', 'oyster', 'mussel', 'clam'],
            'fish': ['salmon', 'tuna', 'cod', 'halibut', 'sardine', 'anchovy', 'bass', 'trout'],
            'eggs': ['egg', 'mayonnaise', 'meringue'],
            'soy': ['soy', 'tofu', 'tempeh', 'edamame', 'miso'],
            'peanuts': ['peanut'],
            'sesame': ['sesame', 'tahini']
        }

        if allergen in mappings:
            return any(term in ingredient for term in mappings[allergen])

        return False

    def suggest_substitutions(self, recipe: Recipe, allergen: Allergen) -> List[Dict[str, Any]]:
        """
        Suggest ingredient substitutions for a recipe to avoid an allergen.

        Args:
            recipe: Recipe object
            allergen: Allergen to avoid

        Returns:
            List of substitution suggestions
        """
        suggestions = []
        allergen_name_lower = allergen.name.lower()

        # Find ingredients containing the allergen
        ingredient_names = self._find_allergen_ingredients(recipe, allergen)

        for ingredient_name in ingredient_names:
            ingredient_lower = ingredient_name.lower()

            # Look up substitutions
            if allergen_name_lower in self.SUBSTITUTIONS:
                allergen_subs = self.SUBSTITUTIONS[allergen_name_lower]

                # Find matching substitution
                for key, subs in allergen_subs.items():
                    if key in ingredient_lower:
                        suggestions.append({
                            'original_ingredient': ingredient_name,
                            'allergen': allergen.name,
                            'substitutes': subs,
                            'notes': f"Use equal amounts unless otherwise specified. Taste and texture may vary."
                        })
                        break

        return suggestions

    def get_safe_recipes(
        self,
        user_id: int,
        max_cooking_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        category_slugs: Optional[List[str]] = None,
        dietary_tag_slugs: Optional[List[str]] = None,
        min_protein: Optional[float] = None,
        max_carbs: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Recipe]:
        """
        Get recipes that are safe for user's allergen profile with additional filters.

        Args:
            user_id: User ID
            max_cooking_time: Maximum cooking time in minutes
            difficulty: Recipe difficulty level
            category_slugs: Category slugs to filter by
            dietary_tag_slugs: Dietary tag slugs to filter by
            min_protein: Minimum protein in grams
            max_carbs: Maximum carbs in grams
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of safe Recipe objects
        """
        # Start with base query
        query = self.session.query(Recipe).filter(Recipe.is_active == True)

        # Exclude recipes with user's allergens (severe and avoid only)
        if self.user_allergens:
            exclude_allergen_ids = [
                ua.allergen_id
                for ua in self.user_allergens
                if ua.severity in ['severe', 'avoid']
            ]

            if exclude_allergen_ids:
                # Subquery to find recipes with these allergens
                allergen_recipes = self.session.query(RecipeAllergen.recipe_id).filter(
                    RecipeAllergen.allergen_id.in_(exclude_allergen_ids)
                ).subquery()

                # Exclude those recipes
                query = query.filter(~Recipe.id.in_(allergen_recipes))

        # Apply filters
        if max_cooking_time:
            query = query.filter(Recipe.cooking_time_minutes <= max_cooking_time)

        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)

        if category_slugs:
            from src.database.models import Category, RecipeCategory
            query = query.join(RecipeCategory).join(Category).filter(
                Category.slug.in_(category_slugs)
            )

        if dietary_tag_slugs:
            from src.database.models import DietaryTag, RecipeDietaryTag
            query = query.join(RecipeDietaryTag).join(DietaryTag).filter(
                DietaryTag.slug.in_(dietary_tag_slugs)
            )

        if min_protein or max_carbs:
            from src.database.models import NutritionalInfo
            query = query.join(NutritionalInfo)

            if min_protein:
                query = query.filter(NutritionalInfo.protein_g >= min_protein)
            if max_carbs:
                query = query.filter(NutritionalInfo.carbohydrates_g <= max_carbs)

        # Apply pagination and return
        recipes = query.offset(offset).limit(limit).all()
        return recipes
