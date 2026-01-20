"""
Recipe service layer for FastAPI.
Wraps database queries and provides data in API-friendly formats.
"""

from typing import List, Dict, Optional, Any, Set
from decimal import Decimal

from sqlalchemy.orm import Session

from src.database.models import Recipe, NutritionalInfo, FavoriteRecipe
from src.database.queries import RecipeQuery


class RecipeService:
    """Service for recipe operations."""

    def __init__(self, db: Session):
        """
        Initialize recipe service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.query = RecipeQuery(db)

    def get_recipes(
        self,
        categories: Optional[List[str]] = None,
        dietary_tags: Optional[List[str]] = None,
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
    ) -> Dict[str, Any]:
        """
        Get recipes with filtering and pagination.

        Args:
            categories: Category slugs to filter by
            dietary_tags: Dietary tag slugs
            exclude_allergens: Allergen names to exclude
            max_cooking_time: Maximum cooking time in minutes
            difficulty: Recipe difficulty level
            min_calories: Minimum calories per serving
            max_calories: Maximum calories per serving
            min_protein: Minimum protein in grams
            max_carbs: Maximum carbs in grams
            limit: Maximum results
            offset: Pagination offset
            order_by: Sort field

        Returns:
            Dictionary with recipes list and pagination info
        """
        recipes = self.query.filter_recipes(
            categories=categories,
            dietary_tags=dietary_tags,
            exclude_allergens=exclude_allergens,
            max_cooking_time=max_cooking_time,
            difficulty=difficulty,
            min_calories=min_calories,
            max_calories=max_calories,
            min_protein=min_protein,
            max_carbs=max_carbs,
            limit=limit,
            offset=offset,
            order_by=order_by
        )

        total_count = self.query.get_recipe_count()

        return {
            'recipes': [self._serialize_recipe_summary(r) for r in recipes],
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + len(recipes)) < total_count
        }

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Get single recipe by ID with all relations.

        Args:
            recipe_id: Recipe ID

        Returns:
            Complete recipe data or None if not found
        """
        recipe = self.query.get_by_id(recipe_id)
        if not recipe:
            return None

        return self._serialize_recipe_full(recipe)

    def get_recipe_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get recipe by URL slug.

        Args:
            slug: Recipe slug

        Returns:
            Complete recipe data or None if not found
        """
        recipe = self.query.get_by_slug(slug)
        if not recipe:
            return None

        return self._serialize_recipe_full(recipe)

    def search_recipes(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search recipes by name.

        Args:
            query: Search term
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Dictionary with search results and pagination
        """
        recipes = self.query.search_by_name(query, limit=limit, offset=offset)

        return {
            'recipes': [self._serialize_recipe_summary(r) for r in recipes],
            'query': query,
            'limit': limit,
            'offset': offset,
            'count': len(recipes)
        }

    def get_recipe_nutrition(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Get nutrition info for a recipe.

        Args:
            recipe_id: Recipe ID

        Returns:
            Nutrition data or None if not found
        """
        nutrition = self.db.query(NutritionalInfo).filter_by(
            recipe_id=recipe_id
        ).first()

        if not nutrition:
            return None

        return self._serialize_nutrition(nutrition)

    def get_recipe_ingredients(self, recipe_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get ingredients for a recipe.

        Args:
            recipe_id: Recipe ID

        Returns:
            List of ingredients or None if recipe not found
        """
        recipe = self.query.get_by_id(recipe_id)
        if not recipe:
            return None

        return [
            {
                'name': ri.ingredient.name,
                'quantity': float(ri.quantity) if ri.quantity else None,
                'unit': ri.unit.abbreviation if ri.unit else None,
                'unit_name': ri.unit.name if ri.unit else None,
                'preparation': ri.preparation_note,
                'optional': ri.is_optional,
                'display_order': ri.display_order
            }
            for ri in sorted(recipe.ingredients_association, key=lambda x: x.display_order)
        ]

    def get_quick_recipes(
        self,
        max_time: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get quick recipes under specified time.

        Args:
            max_time: Maximum cooking time in minutes
            limit: Maximum results

        Returns:
            List of quick recipes
        """
        recipes = self.query.get_quick_recipes(max_time=max_time, limit=limit)
        return [self._serialize_recipe_summary(r) for r in recipes]

    def get_high_protein_recipes(
        self,
        min_protein: float = 30.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get high-protein recipes.

        Args:
            min_protein: Minimum protein in grams
            limit: Maximum results

        Returns:
            List of high-protein recipes
        """
        recipes = self.query.get_high_protein_recipes(
            min_protein=min_protein,
            limit=limit
        )
        return [self._serialize_recipe_summary(r) for r in recipes]

    def get_low_carb_recipes(
        self,
        max_carbs: float = 20.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get low-carb recipes.

        Args:
            max_carbs: Maximum carbs in grams
            limit: Maximum results

        Returns:
            List of low-carb recipes
        """
        recipes = self.query.get_low_carb_recipes(max_carbs=max_carbs, limit=limit)
        return [self._serialize_recipe_summary(r) for r in recipes]

    def _serialize_recipe_summary(self, recipe: Recipe) -> Dict[str, Any]:
        """
        Serialize recipe to summary format (for lists).

        Args:
            recipe: Recipe model

        Returns:
            Recipe summary dictionary
        """
        main_image = next(
            (img for img in recipe.images if img.image_type in ['main', 'hero']),
            recipe.images[0] if recipe.images else None
        )

        return {
            'id': recipe.id,
            'slug': recipe.slug,
            'name': recipe.name,
            'description': recipe.description,
            'cooking_time_minutes': recipe.cooking_time_minutes,
            'prep_time_minutes': recipe.prep_time_minutes,
            'total_time_minutes': recipe.total_time_minutes,
            'difficulty': recipe.difficulty,
            'servings': recipe.servings,
            'categories': [
                {'name': cat.name, 'slug': cat.slug, 'type': cat.category_type}
                for cat in recipe.categories
            ],
            'dietary_tags': [
                {'name': tag.name, 'slug': tag.slug}
                for tag in recipe.dietary_tags
            ],
            'image': {
                'url': main_image.url,
                'alt_text': main_image.alt_text
            } if main_image else None,
            'nutrition_summary': self._get_nutrition_summary(recipe)
        }

    def _serialize_recipe_full(self, recipe: Recipe) -> Dict[str, Any]:
        """
        Serialize recipe to full format (for detail view).

        Args:
            recipe: Recipe model

        Returns:
            Complete recipe dictionary
        """
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
                {'name': cat.name, 'slug': cat.slug, 'type': cat.category_type}
                for cat in recipe.categories
            ],
            'dietary_tags': [
                {'name': tag.name, 'slug': tag.slug}
                for tag in recipe.dietary_tags
            ],
            'allergens': [
                {'name': allergen.name}
                for allergen in recipe.allergens
            ],
            'ingredients': [
                {
                    'name': ri.ingredient.name,
                    'quantity': float(ri.quantity) if ri.quantity else None,
                    'unit': ri.unit.abbreviation if ri.unit else None,
                    'unit_name': ri.unit.name if ri.unit else None,
                    'preparation': ri.preparation_note,
                    'optional': ri.is_optional,
                    'display_order': ri.display_order
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
            'nutrition': self._serialize_nutrition(recipe.nutritional_info) if recipe.nutritional_info else None,
            'images': [
                {
                    'url': img.url,
                    'type': img.image_type,
                    'alt_text': img.alt_text,
                    'width': img.width,
                    'height': img.height
                }
                for img in recipe.images
            ]
        }

    def _serialize_nutrition(self, nutrition: NutritionalInfo) -> Dict[str, Any]:
        """
        Serialize nutrition info.

        Args:
            nutrition: NutritionalInfo model

        Returns:
            Nutrition dictionary
        """
        return {
            'serving_size_g': nutrition.serving_size_g,
            'calories': float(nutrition.calories) if nutrition.calories else None,
            'protein_g': float(nutrition.protein_g) if nutrition.protein_g else None,
            'carbohydrates_g': float(nutrition.carbohydrates_g) if nutrition.carbohydrates_g else None,
            'fat_g': float(nutrition.fat_g) if nutrition.fat_g else None,
            'saturated_fat_g': float(nutrition.saturated_fat_g) if nutrition.saturated_fat_g else None,
            'fiber_g': float(nutrition.fiber_g) if nutrition.fiber_g else None,
            'sugar_g': float(nutrition.sugar_g) if nutrition.sugar_g else None,
            'sodium_mg': float(nutrition.sodium_mg) if nutrition.sodium_mg else None,
            'cholesterol_mg': float(nutrition.cholesterol_mg) if nutrition.cholesterol_mg else None,
            'macros_ratio': nutrition.macros_ratio
        }

    def _get_nutrition_summary(self, recipe: Recipe) -> Optional[Dict[str, Any]]:
        """
        Get nutrition summary (key values only).

        Args:
            recipe: Recipe model

        Returns:
            Nutrition summary or None
        """
        if not recipe.nutritional_info:
            return None

        nutrition = recipe.nutritional_info
        return {
            'calories': float(nutrition.calories) if nutrition.calories else None,
            'protein_g': float(nutrition.protein_g) if nutrition.protein_g else None,
            'carbohydrates_g': float(nutrition.carbohydrates_g) if nutrition.carbohydrates_g else None,
            'fat_g': float(nutrition.fat_g) if nutrition.fat_g else None,
        }

    def get_user_favorite_recipe_ids(self, user_id: int) -> Set[int]:
        """
        Get set of recipe IDs that are in user's favorites.

        Args:
            user_id: User ID

        Returns:
            Set of recipe IDs
        """
        favorites = self.db.query(FavoriteRecipe.recipe_id).filter(
            FavoriteRecipe.user_id == user_id
        ).all()

        return {fav.recipe_id for fav in favorites}

    def enrich_with_favorite_status(
        self,
        recipes: List[Dict[str, Any]],
        user_id: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Add is_favorite field to recipe dictionaries.

        Args:
            recipes: List of recipe dictionaries
            user_id: User ID (None if not authenticated)

        Returns:
            Enriched recipe dictionaries
        """
        if user_id is None:
            # Not authenticated - set all to None
            for recipe in recipes:
                recipe['is_favorite'] = None
            return recipes

        # Get user's favorite recipe IDs
        favorite_ids = self.get_user_favorite_recipe_ids(user_id)

        # Enrich each recipe
        for recipe in recipes:
            recipe['is_favorite'] = recipe['id'] in favorite_ids

        return recipes
