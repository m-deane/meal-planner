"""
Favorites endpoints for FastAPI.
Allows users to manage their favorite recipes.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, CurrentUser, PaginationParams
from src.api.services.favorites_service import FavoritesService
from src.api.schemas.favorites import (
    FavoriteRecipeResponse,
    FavoriteRequest,
    FavoriteNotesUpdate,
    FavoriteStatusResponse,
    FavoriteCountResponse,
)
from src.api.schemas.pagination import PaginatedResponse
from src.api.schemas.common import MessageResponse

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
)


@router.get(
    "",
    response_model=PaginatedResponse[FavoriteRecipeResponse],
    summary="List user's favorite recipes"
)
def list_favorites(
    db: DatabaseSession,
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    order_by: str = Query("created_at", description="Order by: created_at or recipe.name"),
):
    """
    Get a paginated list of the current user's favorite recipes.

    Returns:
    - Recipe summary information
    - User's personal notes
    - When it was favorited

    Results are ordered by date favorited (newest first) by default.
    """
    service = FavoritesService(db)

    # Extract user ID from token
    user_id = int(user["sub"])

    # Calculate offset
    offset = (page - 1) * page_size

    # Get favorites
    favorites = service.get_user_favorites(
        user_id=user_id,
        skip=offset,
        limit=page_size,
        order_by=order_by
    )

    # Get total count
    total = service.get_favorite_count(user_id)

    # Convert to Pydantic models
    items = [FavoriteRecipeResponse(**fav) for fav in favorites]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post(
    "/{recipe_id}",
    response_model=FavoriteRecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add recipe to favorites",
    responses={
        409: {"description": "Recipe already in favorites"},
        404: {"description": "Recipe not found"}
    }
)
def add_favorite(
    recipe_id: int,
    request: FavoriteRequest,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Add a recipe to the current user's favorites.

    Can optionally include personal notes about the recipe.
    """
    service = FavoritesService(db)
    user_id = int(user["sub"])

    favorite = service.add_favorite(
        user_id=user_id,
        recipe_id=recipe_id,
        notes=request.notes
    )

    return FavoriteRecipeResponse(**favorite)


@router.delete(
    "/{recipe_id}",
    response_model=MessageResponse,
    summary="Remove recipe from favorites",
    responses={
        404: {"description": "Recipe not in favorites"}
    }
)
def remove_favorite(
    recipe_id: int,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Remove a recipe from the current user's favorites.
    """
    service = FavoritesService(db)
    user_id = int(user["sub"])

    service.remove_favorite(user_id=user_id, recipe_id=recipe_id)

    return MessageResponse(message="Recipe removed from favorites")


@router.put(
    "/{recipe_id}/notes",
    response_model=FavoriteRecipeResponse,
    summary="Update favorite recipe notes",
    responses={
        404: {"description": "Recipe not in favorites"}
    }
)
def update_favorite_notes(
    recipe_id: int,
    request: FavoriteNotesUpdate,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Update the personal notes for a favorited recipe.

    Set notes to null/empty to clear existing notes.
    """
    service = FavoritesService(db)
    user_id = int(user["sub"])

    favorite = service.update_favorite_notes(
        user_id=user_id,
        recipe_id=recipe_id,
        notes=request.notes
    )

    return FavoriteRecipeResponse(**favorite)


@router.get(
    "/{recipe_id}/status",
    response_model=FavoriteStatusResponse,
    summary="Check if recipe is favorited"
)
def get_favorite_status(
    recipe_id: int,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Check if a specific recipe is in the current user's favorites.

    Returns favorite status, notes, and date favorited if applicable.
    """
    service = FavoritesService(db)
    user_id = int(user["sub"])

    is_fav, data = service.is_favorite(user_id=user_id, recipe_id=recipe_id)

    if is_fav and data:
        return FavoriteStatusResponse(
            is_favorite=True,
            notes=data['notes'],
            created_at=data['created_at']
        )

    return FavoriteStatusResponse(
        is_favorite=False,
        notes=None,
        created_at=None
    )


@router.get(
    "/count",
    response_model=FavoriteCountResponse,
    summary="Get count of favorites"
)
def get_favorites_count(
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Get the total number of recipes in the current user's favorites.
    """
    service = FavoritesService(db)
    user_id = int(user["sub"])

    count = service.get_favorite_count(user_id)

    return FavoriteCountResponse(count=count)
