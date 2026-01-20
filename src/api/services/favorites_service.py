"""
Favorites service layer for FastAPI.
Handles user favorite recipes operations.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from src.database.models import FavoriteRecipe, Recipe, User


class FavoritesService:
    """Service for managing user favorite recipes."""

    def __init__(self, db: Session):
        """
        Initialize favorites service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_user_favorites(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at"
    ) -> List[Dict[str, Any]]:
        """
        Get user's favorite recipes with pagination.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by (created_at, recipe.name)

        Returns:
            List of favorite recipes with recipe details
        """
        query = self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id
        )

        # Apply ordering
        if order_by == "recipe.name":
            query = query.join(Recipe).order_by(Recipe.name)
        else:
            query = query.order_by(FavoriteRecipe.created_at.desc())

        favorites = query.offset(skip).limit(limit).all()

        return [self._serialize_favorite(fav) for fav in favorites]

    def add_favorite(
        self,
        user_id: int,
        recipe_id: int,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a recipe to user's favorites.

        Args:
            user_id: User ID
            recipe_id: Recipe ID to favorite
            notes: Optional notes about the recipe

        Returns:
            Created favorite record

        Raises:
            HTTPException: If recipe doesn't exist or already favorited
        """
        # Verify recipe exists
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with ID {recipe_id} not found"
            )

        # Check if already favorited
        existing = self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Recipe is already in favorites"
            )

        # Create favorite
        favorite = FavoriteRecipe(
            user_id=user_id,
            recipe_id=recipe_id,
            notes=notes,
            created_at=datetime.utcnow()
        )

        try:
            self.db.add(favorite)
            self.db.commit()
            self.db.refresh(favorite)
            return self._serialize_favorite(favorite)
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add favorite: {str(e)}"
            )

    def remove_favorite(self, user_id: int, recipe_id: int) -> bool:
        """
        Remove a recipe from user's favorites.

        Args:
            user_id: User ID
            recipe_id: Recipe ID to unfavorite

        Returns:
            True if removed, False if not found

        Raises:
            HTTPException: If favorite not found
        """
        favorite = self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe_id
        ).first()

        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found in favorites"
            )

        self.db.delete(favorite)
        self.db.commit()
        return True

    def update_favorite_notes(
        self,
        user_id: int,
        recipe_id: int,
        notes: Optional[str]
    ) -> Dict[str, Any]:
        """
        Update notes for a favorited recipe.

        Args:
            user_id: User ID
            recipe_id: Recipe ID
            notes: New notes (can be None to clear)

        Returns:
            Updated favorite record

        Raises:
            HTTPException: If favorite not found
        """
        favorite = self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe_id
        ).first()

        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found in favorites"
            )

        favorite.notes = notes
        self.db.commit()
        self.db.refresh(favorite)

        return self._serialize_favorite(favorite)

    def is_favorite(self, user_id: int, recipe_id: int) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a recipe is in user's favorites.

        Args:
            user_id: User ID
            recipe_id: Recipe ID

        Returns:
            Tuple of (is_favorite, favorite_data)
        """
        favorite = self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id,
            FavoriteRecipe.recipe_id == recipe_id
        ).first()

        if favorite:
            return True, {
                'notes': favorite.notes,
                'created_at': favorite.created_at
            }
        return False, None

    def get_favorite_count(self, user_id: int) -> int:
        """
        Get total count of user's favorites.

        Args:
            user_id: User ID

        Returns:
            Number of favorited recipes
        """
        return self.db.query(FavoriteRecipe).filter(
            FavoriteRecipe.user_id == user_id
        ).count()

    def _serialize_favorite(self, favorite: FavoriteRecipe) -> Dict[str, Any]:
        """
        Serialize favorite recipe to dictionary.

        Args:
            favorite: FavoriteRecipe model

        Returns:
            Dictionary with favorite data and recipe summary
        """
        recipe = favorite.recipe

        # Get main image
        main_image = next(
            (img for img in recipe.images if img.image_type in ['main', 'hero']),
            recipe.images[0] if recipe.images else None
        )

        return {
            'id': favorite.id,
            'recipe': {
                'id': recipe.id,
                'slug': recipe.slug,
                'name': recipe.name,
                'description': recipe.description,
                'cooking_time_minutes': recipe.cooking_time_minutes,
                'difficulty': recipe.difficulty,
                'image_url': main_image.url if main_image else None
            },
            'notes': favorite.notes,
            'created_at': favorite.created_at
        }
