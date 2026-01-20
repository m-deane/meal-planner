"""
Recipe endpoints for FastAPI.
Provides recipe listing, filtering, search, and detail views.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.api.services.recipe_service import RecipeService
from src.api.schemas import (
    RecipeListItem,
    RecipeResponse,
    RecipeFilters,
    NutritionResponse,
    IngredientResponse,
    PaginatedResponse,
    DifficultyLevel,
)
from src.database.models import Recipe, UserAllergen
from src.meal_planner.allergen_filter import AllergenFilter

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)


@router.get(
    "",
    response_model=PaginatedResponse[RecipeListItem],
    summary="List recipes with filtering and pagination"
)
def list_recipes(
    db: DatabaseSession,
    user: OptionalUser = None,
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    # Category and tag filters
    category_slugs: Optional[List[str]] = Query(None, description="Filter by category slugs"),
    dietary_tag_slugs: Optional[List[str]] = Query(None, description="Filter by dietary tag slugs"),
    exclude_allergen_names: Optional[List[str]] = Query(None, description="Exclude recipes with these allergens"),
    exclude_user_allergens: bool = Query(False, description="Exclude recipes based on user's allergen profile (requires authentication)"),
    # Time and difficulty filters
    max_cooking_time: Optional[int] = Query(None, ge=0, description="Maximum cooking time in minutes"),
    max_total_time: Optional[int] = Query(None, ge=0, description="Maximum total time in minutes"),
    difficulty: Optional[List[DifficultyLevel]] = Query(None, description="Filter by difficulty levels"),
    # Nutrition filters
    min_calories: Optional[int] = Query(None, ge=0, description="Minimum calories per serving"),
    max_calories: Optional[int] = Query(None, ge=0, description="Maximum calories per serving"),
    min_protein: Optional[float] = Query(None, ge=0, description="Minimum protein in grams"),
    max_carbs: Optional[float] = Query(None, ge=0, description="Maximum carbs in grams"),
    # Search
    search_query: Optional[str] = Query(None, min_length=1, description="Search in recipe name and description"),
):
    """
    Get a paginated list of recipes with optional filtering.

    Supports filtering by:
    - Categories and dietary tags
    - Allergen exclusions (manual or automatic via user profile)
    - Cooking time and difficulty
    - Nutritional values
    - Search query

    If authenticated, recipes will include is_favorite status.
    Use exclude_user_allergens=true to automatically filter based on your allergen profile.
    """
    service = RecipeService(db)

    # Extract user ID if authenticated
    user_id = int(user["sub"]) if user else None

    # Calculate offset from page
    offset = (page - 1) * page_size

    # Convert difficulty enums to strings
    difficulty_strs = [d.value for d in difficulty] if difficulty else None

    # Handle user allergen filtering
    if exclude_user_allergens:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to use exclude_user_allergens filter"
            )

        # Load user's allergen profile
        user_allergens = db.query(UserAllergen).filter(
            UserAllergen.user_id == user_id
        ).all()

        # Use allergen filter to get safe recipes
        allergen_filter = AllergenFilter(db, user_allergens)
        safe_recipes = allergen_filter.get_safe_recipes(
            user_id=user_id,
            max_cooking_time=max_cooking_time or max_total_time,
            difficulty=difficulty_strs[0] if difficulty_strs else None,
            category_slugs=category_slugs,
            dietary_tag_slugs=dietary_tag_slugs,
            min_protein=min_protein,
            max_carbs=max_carbs,
            limit=page_size,
            offset=offset
        )

        # Convert to service format
        result = {
            'recipes': [service._serialize_recipe_summary(r) for r in safe_recipes],
            'total': len(safe_recipes),
            'limit': page_size,
            'offset': offset
        }
    else:
        # Standard filtering
        result = service.get_recipes(
            categories=category_slugs,
            dietary_tags=dietary_tag_slugs,
            exclude_allergens=exclude_allergen_names,
            max_cooking_time=max_cooking_time or max_total_time,
            difficulty=difficulty_strs[0] if difficulty_strs else None,
            min_calories=min_calories,
            max_calories=max_calories,
            min_protein=min_protein,
            max_carbs=max_carbs,
            limit=page_size,
            offset=offset,
        )

        # If search query provided, use search instead
        if search_query:
            result = service.search_recipes(
                query=search_query,
                limit=page_size,
                offset=offset
            )

    # Enrich with favorite status if authenticated
    recipes_data = service.enrich_with_favorite_status(result['recipes'], user_id)

    # Convert to Pydantic models
    recipes = [RecipeListItem(**r) for r in recipes_data]
    total = result.get('total', result.get('count', len(recipes)))

    return PaginatedResponse.create(
        items=recipes,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/search",
    response_model=PaginatedResponse[RecipeListItem],
    summary="Search recipes by name or description"
)
def search_recipes(
    db: DatabaseSession,
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user: OptionalUser = None,
):
    """
    Search recipes by name or description.

    Returns recipes that match the search query in their name or description.
    If authenticated, includes is_favorite status for each recipe.
    """
    service = RecipeService(db)
    user_id = int(user["sub"]) if user else None
    offset = (page - 1) * page_size

    result = service.search_recipes(
        query=q,
        limit=page_size,
        offset=offset
    )

    # Enrich with favorite status if authenticated
    recipes_data = service.enrich_with_favorite_status(result['recipes'], user_id)

    recipes = [RecipeListItem(**r) for r in recipes_data]
    total = result.get('count', len(recipes))

    return PaginatedResponse.create(
        items=recipes,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe by ID",
    responses={
        404: {"description": "Recipe not found"}
    }
)
def get_recipe_by_id(
    recipe_id: int,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get complete recipe details by ID.

    Returns full recipe information including:
    - Ingredients with quantities and preparation notes
    - Step-by-step cooking instructions
    - Nutritional information
    - Images
    - Categories, dietary tags, and allergens
    """
    service = RecipeService(db)
    recipe = service.get_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    return RecipeResponse(**recipe)


@router.get(
    "/slug/{slug}",
    response_model=RecipeResponse,
    summary="Get recipe by slug",
    responses={
        404: {"description": "Recipe not found"}
    }
)
def get_recipe_by_slug(
    slug: str,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get complete recipe details by URL slug.

    Same as getting by ID but uses the URL-friendly slug identifier.
    """
    service = RecipeService(db)
    recipe = service.get_recipe_by_slug(slug)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with slug '{slug}' not found"
        )

    return RecipeResponse(**recipe)


@router.get(
    "/{recipe_id}/nutrition",
    response_model=NutritionResponse,
    summary="Get recipe nutrition information",
    responses={
        404: {"description": "Recipe or nutrition data not found"}
    }
)
def get_recipe_nutrition(
    recipe_id: int,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get nutritional information for a recipe.

    Returns per-serving nutritional data including:
    - Calories
    - Macros (protein, carbs, fat)
    - Fiber and sugar
    - Sodium and cholesterol
    """
    service = RecipeService(db)
    nutrition = service.get_recipe_nutrition(recipe_id)

    if not nutrition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nutrition data not found for recipe {recipe_id}"
        )

    return NutritionResponse(**nutrition)


@router.get(
    "/{recipe_id}/ingredients",
    response_model=List[IngredientResponse],
    summary="Get recipe ingredients",
    responses={
        404: {"description": "Recipe not found"}
    }
)
def get_recipe_ingredients(
    recipe_id: int,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get ingredients list for a recipe.

    Returns all ingredients with:
    - Quantities and units
    - Preparation notes (chopped, diced, etc.)
    - Optional/required status
    - Display order
    """
    service = RecipeService(db)
    ingredients = service.get_recipe_ingredients(recipe_id)

    if ingredients is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    # Convert to schema format
    return [
        IngredientResponse(
            name=ing['name'],
            quantity=ing['quantity'],
            unit=ing['unit'],
            unit_name=ing['unit_name'],
            preparation_note=ing['preparation'],
            is_optional=ing['optional'],
            display_order=ing['display_order']
        )
        for ing in ingredients
    ]
