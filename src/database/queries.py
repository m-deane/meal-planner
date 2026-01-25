"""
Common database queries and search functionality.
Provides high-level API for recipe operations.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from .models import (
    Recipe, Category, Ingredient, RecipeIngredient, DietaryTag,
    Allergen, NutritionalInfo
)


def escape_like_pattern(text: str) -> str:
    """
    Escape special characters in LIKE patterns to prevent SQL injection.

    Args:
        text: User input string

    Returns:
        Escaped string safe for LIKE patterns
    """
    # Escape backslash first, then other special chars
    return text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


class RecipeQuery:
    """High-level query interface for recipe operations."""

    def __init__(self, session: Session):
        """
        Initialize query interface.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by ID with all relationships loaded."""
        return self.session.query(Recipe).filter(
            Recipe.id == recipe_id
        ).first()

    def get_by_gousto_id(self, gousto_id: str) -> Optional[Recipe]:
        """Get recipe by Gousto ID."""
        return self.session.query(Recipe).filter(
            Recipe.gousto_id == gousto_id
        ).first()

    def get_by_slug(self, slug: str) -> Optional[Recipe]:
        """Get recipe by URL slug."""
        return self.session.query(Recipe).filter(
            Recipe.slug == slug
        ).first()

    def search_by_name(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Recipe]:
        """
        Search recipes by name (case-insensitive partial match).

        Args:
            query: Search term
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching recipes
        """
        escaped_query = escape_like_pattern(query)
        return self.session.query(Recipe).filter(
            and_(
                Recipe.is_active == True,
                Recipe.name.ilike(f'%{escaped_query}%', escape='\\')
            )
        ).limit(limit).offset(offset).all()

    def filter_recipes(
        self,
        category_ids: Optional[List[int]] = None,
        categories: Optional[List[str]] = None,
        dietary_tag_ids: Optional[List[int]] = None,
        dietary_tags: Optional[List[str]] = None,
        exclude_allergen_ids: Optional[List[int]] = None,
        exclude_allergens: Optional[List[str]] = None,
        max_cooking_time: Optional[int] = None,
        difficulty: Optional[str] = None,
        min_calories: Optional[int] = None,
        max_calories: Optional[int] = None,
        min_protein: Optional[float] = None,
        max_carbs: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = 'name'
    ) -> List[Recipe]:
        """
        Advanced recipe filtering with multiple criteria.

        Args:
            category_ids: Category IDs to filter by (OR logic)
            categories: Category slugs to filter by (OR logic)
            dietary_tag_ids: Dietary tag IDs (AND logic)
            dietary_tags: Dietary tag slugs (AND logic)
            exclude_allergen_ids: Allergen IDs to exclude
            exclude_allergens: Allergen names to exclude
            max_cooking_time: Maximum cooking time in minutes
            difficulty: Recipe difficulty level
            min_calories: Minimum calories per serving
            max_calories: Maximum calories per serving
            min_protein: Minimum protein in grams
            max_carbs: Maximum carbs in grams
            limit: Maximum results
            offset: Pagination offset
            order_by: Sort field (name, cooking_time, calories, protein). Prefix with '-' for descending.

        Returns:
            List of filtered recipes
        """
        query = self.session.query(Recipe).filter(Recipe.is_active == True)

        # Category filter by ID (OR - match any category)
        if category_ids:
            query = query.join(Recipe.categories).filter(
                Category.id.in_(category_ids)
            )
        # Category filter by slug (OR - match any category)
        elif categories:
            query = query.join(Recipe.categories).filter(
                Category.slug.in_(categories)
            )

        # Dietary tags filter by ID (AND - must have all tags)
        if dietary_tag_ids:
            for tag_id in dietary_tag_ids:
                query = query.join(Recipe.dietary_tags).filter(
                    DietaryTag.id == tag_id
                )
        # Dietary tags filter by slug (AND - must have all tags)
        elif dietary_tags:
            for tag_slug in dietary_tags:
                query = query.join(Recipe.dietary_tags).filter(
                    DietaryTag.slug == tag_slug
                )

        # Allergen exclusion by ID (must NOT have any excluded allergens)
        if exclude_allergen_ids:
            allergen_recipes = self.session.query(Recipe.id).join(
                Recipe.allergens
            ).filter(
                Allergen.id.in_(exclude_allergen_ids)
            ).subquery()

            query = query.filter(~Recipe.id.in_(allergen_recipes))
        # Allergen exclusion by name (must NOT have any excluded allergens)
        elif exclude_allergens:
            allergen_recipes = self.session.query(Recipe.id).join(
                Recipe.allergens
            ).filter(
                Allergen.name.in_(exclude_allergens)
            ).subquery()

            query = query.filter(~Recipe.id.in_(allergen_recipes))

        # Time constraint
        if max_cooking_time is not None:
            query = query.filter(Recipe.cooking_time_minutes <= max_cooking_time)

        # Difficulty filter
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)

        # Nutritional filters
        if any([min_calories, max_calories, min_protein, max_carbs]):
            query = query.join(Recipe.nutritional_info)

            if min_calories is not None:
                query = query.filter(NutritionalInfo.calories >= min_calories)
            if max_calories is not None:
                query = query.filter(NutritionalInfo.calories <= max_calories)
            if min_protein is not None:
                query = query.filter(NutritionalInfo.protein_g >= min_protein)
            if max_carbs is not None:
                query = query.filter(NutritionalInfo.carbohydrates_g <= max_carbs)

        # Ordering - supports descending with '-' prefix (e.g., '-calories')
        descending = order_by.startswith('-') if order_by else False
        sort_field = order_by.lstrip('-') if order_by else 'name'

        if sort_field == 'cooking_time':
            sort_col = Recipe.cooking_time_minutes
            if descending:
                query = query.order_by(sort_col.desc())
            else:
                query = query.order_by(sort_col)
        elif sort_field == 'calories':
            # Only join if not already joined for nutrition filters
            if not any([min_calories, max_calories, min_protein, max_carbs]):
                query = query.join(Recipe.nutritional_info)
            if descending:
                query = query.order_by(NutritionalInfo.calories.desc())
            else:
                query = query.order_by(NutritionalInfo.calories)
        elif sort_field == 'protein':
            # Only join if not already joined for nutrition filters
            if not any([min_calories, max_calories, min_protein, max_carbs]):
                query = query.join(Recipe.nutritional_info)
            if descending:
                query = query.order_by(NutritionalInfo.protein_g.desc())
            else:
                query = query.order_by(NutritionalInfo.protein_g)
        else:  # Default to name
            if descending:
                query = query.order_by(Recipe.name.desc())
            else:
                query = query.order_by(Recipe.name)

        return query.limit(limit).offset(offset).all()

    def get_recipes_by_ingredient(
        self,
        ingredient_names: List[str],
        match_all: bool = False
    ) -> List[Recipe]:
        """
        Find recipes containing specific ingredients.

        Args:
            ingredient_names: List of ingredient names
            match_all: If True, recipe must contain ALL ingredients (AND logic)
                      If False, recipe must contain ANY ingredient (OR logic)

        Returns:
            List of matching recipes
        """
        query = self.session.query(Recipe).filter(Recipe.is_active == True)

        if match_all:
            # Must have ALL ingredients
            for ing_name in ingredient_names:
                escaped_name = escape_like_pattern(ing_name.lower())
                query = query.join(Recipe.ingredients_association).join(
                    RecipeIngredient.ingredient
                ).filter(
                    Ingredient.normalized_name.like(f'%{escaped_name}%', escape='\\')
                )
        else:
            # Must have ANY ingredient
            query = query.join(Recipe.ingredients_association).join(
                RecipeIngredient.ingredient
            ).filter(
                or_(*[
                    Ingredient.normalized_name.like(f'%{escape_like_pattern(name.lower())}%', escape='\\')
                    for name in ingredient_names
                ])
            )

        return query.distinct().all()

    def get_quick_recipes(self, max_time: int = 30, limit: int = 20) -> List[Recipe]:
        """Get quick recipes under specified cooking time."""
        return self.session.query(Recipe).filter(
            and_(
                Recipe.is_active == True,
                Recipe.cooking_time_minutes <= max_time
            )
        ).order_by(Recipe.cooking_time_minutes).limit(limit).all()

    def get_high_protein_recipes(
        self,
        min_protein: float = 30.0,
        limit: int = 20
    ) -> List[Recipe]:
        """Get high-protein recipes."""
        return self.session.query(Recipe).join(
            Recipe.nutritional_info
        ).filter(
            and_(
                Recipe.is_active == True,
                NutritionalInfo.protein_g >= min_protein
            )
        ).order_by(
            NutritionalInfo.protein_g.desc()
        ).limit(limit).all()

    def get_low_carb_recipes(
        self,
        max_carbs: float = 20.0,
        limit: int = 20
    ) -> List[Recipe]:
        """Get low-carb recipes."""
        return self.session.query(Recipe).join(
            Recipe.nutritional_info
        ).filter(
            and_(
                Recipe.is_active == True,
                NutritionalInfo.carbohydrates_g <= max_carbs
            )
        ).order_by(
            NutritionalInfo.carbohydrates_g
        ).limit(limit).all()

    def get_recipe_count(self) -> int:
        """Get total count of active recipes."""
        return self.session.query(Recipe).filter(
            Recipe.is_active == True
        ).count()

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Get recipe count by category."""
        return self.session.query(
            Category.name,
            Category.category_type,
            func.count(Recipe.id).label('recipe_count')
        ).join(
            Category.recipes
        ).filter(
            Recipe.is_active == True
        ).group_by(
            Category.id
        ).order_by(
            func.count(Recipe.id).desc()
        ).all()

    def get_ingredient_usage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most commonly used ingredients."""
        return self.session.query(
            Ingredient.name,
            func.count(RecipeIngredient.recipe_id).label('usage_count')
        ).join(
            RecipeIngredient.ingredient
        ).group_by(
            Ingredient.id
        ).order_by(
            func.count(RecipeIngredient.recipe_id).desc()
        ).limit(limit).all()

    def export_recipe_data(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Export complete recipe data as dictionary.

        Args:
            recipe_id: Recipe ID

        Returns:
            Complete recipe data dictionary
        """
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return None

        return {
            'id': recipe.id,
            'gousto_id': recipe.gousto_id,
            'slug': recipe.slug,
            'name': recipe.name,
            'description': recipe.description,
            'cooking_time_minutes': recipe.cooking_time_minutes,
            'prep_time_minutes': recipe.prep_time_minutes,
            'total_time_minutes': recipe.total_time_minutes,
            'difficulty': recipe.difficulty,
            'servings': recipe.servings,
            'source_url': recipe.source_url,
            'categories': [
                {'name': cat.name, 'type': cat.category_type}
                for cat in recipe.categories
            ],
            'dietary_tags': [tag.name for tag in recipe.dietary_tags],
            'allergens': [allergen.name for allergen in recipe.allergens],
            'ingredients': [
                {
                    'name': ri.ingredient.name,
                    'quantity': float(ri.quantity) if ri.quantity else None,
                    'unit': ri.unit.abbreviation if ri.unit else None,
                    'preparation': ri.preparation_note,
                    'optional': ri.is_optional
                }
                for ri in sorted(recipe.ingredients_association, key=lambda x: x.display_order)
            ],
            'instructions': [
                {
                    'step': inst.step_number,
                    'text': inst.instruction,
                    'time_minutes': inst.time_minutes
                }
                for inst in recipe.cooking_instructions
            ],
            'nutrition': {
                'calories': float(recipe.nutritional_info.calories) if recipe.nutritional_info and recipe.nutritional_info.calories else None,
                'protein_g': float(recipe.nutritional_info.protein_g) if recipe.nutritional_info and recipe.nutritional_info.protein_g else None,
                'carbohydrates_g': float(recipe.nutritional_info.carbohydrates_g) if recipe.nutritional_info and recipe.nutritional_info.carbohydrates_g else None,
                'fat_g': float(recipe.nutritional_info.fat_g) if recipe.nutritional_info and recipe.nutritional_info.fat_g else None,
                'fiber_g': float(recipe.nutritional_info.fiber_g) if recipe.nutritional_info and recipe.nutritional_info.fiber_g else None,
            } if recipe.nutritional_info else None,
            'images': [
                {
                    'url': img.url,
                    'type': img.image_type,
                    'alt_text': img.alt_text
                }
                for img in recipe.images
            ]
        }
