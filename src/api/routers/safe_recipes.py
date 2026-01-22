"""
Safe recipes endpoints for FastAPI.
Provides allergen-safe recipe filtering and warnings based on user allergen profiles.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, CurrentUser
from src.api.schemas.favorites import (
    AllergenWarningsResponse,
    AllergenWarning as AllergenWarningSchema,
    IngredientSubstitution,
)
from src.api.schemas.recipe import RecipeListItem
from src.api.schemas.pagination import PaginatedResponse
from src.database.models import Recipe, UserAllergen, Allergen
from src.meal_planner.allergen_filter import AllergenFilter

router = APIRouter(
    prefix="/recipes",
    tags=["safe-recipes", "allergens"],
)


@router.get(
    "/safe",
    response_model=PaginatedResponse[RecipeListItem],
    summary="Get recipes safe for user's allergen profile"
)
def get_safe_recipes(
    db: DatabaseSession,
    user: CurrentUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    max_cooking_time: Optional[int] = Query(None, ge=0, le=300, description="Maximum cooking time in minutes"),
    difficulty: Optional[str] = Query(None, description="Difficulty level (easy, medium, hard)"),
    category_slugs: Optional[List[str]] = Query(None, description="Filter by category slugs"),
    dietary_tag_slugs: Optional[List[str]] = Query(None, description="Filter by dietary tag slugs"),
    min_protein: Optional[float] = Query(None, ge=0, description="Minimum protein in grams"),
    max_carbs: Optional[float] = Query(None, ge=0, description="Maximum carbs in grams"),
):
    """
    Get recipes that are safe for the current user's allergen profile.

    Automatically excludes recipes containing allergens marked as 'severe' or 'avoid'
    in the user's allergen profile. Recipes with allergens marked as 'trace_ok' are included.

    Supports additional filtering by:
    - Cooking time and difficulty
    - Categories and dietary tags
    - Nutritional requirements
    """
    user_id = int(user["sub"])

    # Load user's allergen profile
    user_allergens = db.query(UserAllergen).filter(
        UserAllergen.user_id == user_id
    ).all()

    # Initialize allergen filter
    allergen_filter = AllergenFilter(db, user_allergens)

    # Calculate offset
    offset = (page - 1) * page_size

    # Get safe recipes with filters
    recipes = allergen_filter.get_safe_recipes(
        user_id=user_id,
        max_cooking_time=max_cooking_time,
        difficulty=difficulty,
        category_slugs=category_slugs,
        dietary_tag_slugs=dietary_tag_slugs,
        min_protein=min_protein,
        max_carbs=max_carbs,
        limit=page_size,
        offset=offset
    )

    # Count total safe recipes (for pagination)
    # Note: In production, you'd want to optimize this with a count query
    all_safe_recipes = allergen_filter.get_safe_recipes(
        user_id=user_id,
        max_cooking_time=max_cooking_time,
        difficulty=difficulty,
        category_slugs=category_slugs,
        dietary_tag_slugs=dietary_tag_slugs,
        min_protein=min_protein,
        max_carbs=max_carbs,
        limit=10000,  # High limit to count all
        offset=0
    )
    total = len(all_safe_recipes)

    # Convert to response format
    items = [_serialize_recipe_summary(recipe) for recipe in recipes]
    recipe_items = [RecipeListItem(**item) for item in items]

    return PaginatedResponse.create(
        items=recipe_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{recipe_id}/allergen-warnings",
    response_model=AllergenWarningsResponse,
    summary="Get allergen warnings for a recipe"
)
def get_allergen_warnings(
    recipe_id: int,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Get allergen warnings for a specific recipe based on the user's allergen profile.

    Returns:
    - List of allergens in the recipe that match user's profile
    - Severity level for each allergen
    - Which ingredients contain the allergen
    - Whether the recipe is safe overall

    Useful for showing warnings before a user views or saves a recipe.
    """
    user_id = int(user["sub"])

    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    # Load user's allergen profile
    user_allergens = db.query(UserAllergen).filter(
        UserAllergen.user_id == user_id
    ).all()

    if not user_allergens:
        # No allergen profile - recipe is safe
        return AllergenWarningsResponse(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            warnings=[],
            is_safe=True
        )

    # Initialize allergen filter
    allergen_filter = AllergenFilter(db, user_allergens)

    # Get warnings
    warnings = allergen_filter.get_warnings(recipe)

    # Check if safe
    is_safe = allergen_filter._is_recipe_safe(recipe)

    # Convert warnings to schema format
    warning_schemas = [
        AllergenWarningSchema(
            allergen_name=w.allergen_name,
            severity=w.severity,
            ingredient_name=w.ingredient_name,
            message=w.message
        )
        for w in warnings
    ]

    return AllergenWarningsResponse(
        recipe_id=recipe.id,
        recipe_name=recipe.name,
        warnings=warning_schemas,
        is_safe=is_safe
    )


@router.get(
    "/{recipe_id}/allergen-substitutions",
    response_model=List[IngredientSubstitution],
    summary="Get ingredient substitutions for allergens"
)
def get_allergen_substitutions(
    recipe_id: int,
    db: DatabaseSession,
    user: CurrentUser,
):
    """
    Get suggested ingredient substitutions to make a recipe safe for user's allergen profile.

    Returns specific ingredient substitutions that can be used to avoid allergens
    while maintaining the recipe's integrity.

    Example: For a peanut allergy, suggests replacing peanut butter with
    sunflower seed butter or almond butter.
    """
    user_id = int(user["sub"])

    # Get recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )

    # Load user's allergen profile
    user_allergens = db.query(UserAllergen).filter(
        UserAllergen.user_id == user_id
    ).all()

    if not user_allergens:
        return []

    # Initialize allergen filter
    allergen_filter = AllergenFilter(db, user_allergens)

    # Get substitutions for each allergen
    all_substitutions = []
    for user_allergen in user_allergens:
        allergen = user_allergen.allergen
        substitutions = allergen_filter.suggest_substitutions(recipe, allergen)
        all_substitutions.extend(substitutions)

    # Convert to schema format
    return [IngredientSubstitution(**sub) for sub in all_substitutions]


def _serialize_recipe_summary(recipe: Recipe) -> dict:
    """
    Serialize recipe to summary format matching RecipeListItem schema.

    Args:
        recipe: Recipe model

    Returns:
        Recipe summary dictionary
    """
    main_image = next(
        (img for img in recipe.images if img.image_type in ['main', 'hero']),
        recipe.images[0] if recipe.images else None
    )

    nutrition_summary = None
    if recipe.nutritional_info:
        nutrition = recipe.nutritional_info
        nutrition_summary = {
            'calories': float(nutrition.calories) if nutrition.calories else None,
            'protein_g': float(nutrition.protein_g) if nutrition.protein_g else None,
            'carbohydrates_g': float(nutrition.carbohydrates_g) if nutrition.carbohydrates_g else None,
            'fat_g': float(nutrition.fat_g) if nutrition.fat_g else None,
        }

    main_image_data = None
    if main_image:
        main_image_data = {
            'id': main_image.id,
            'url': main_image.url,
            'image_type': main_image.image_type or 'main',
            'display_order': main_image.display_order or 0,
            'alt_text': main_image.alt_text,
            'width': main_image.width,
            'height': main_image.height,
        }

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
            {'id': cat.id, 'name': cat.name, 'slug': cat.slug, 'category_type': cat.category_type}
            for cat in recipe.categories
        ],
        'dietary_tags': [
            {'id': tag.id, 'name': tag.name, 'slug': tag.slug}
            for tag in recipe.dietary_tags
        ],
        'allergens': [
            {'id': allergen.id, 'name': allergen.name, 'description': allergen.description}
            for allergen in recipe.allergens
        ],
        'main_image': main_image_data,
        'nutrition_summary': nutrition_summary,
        'is_active': recipe.is_active,
    }
