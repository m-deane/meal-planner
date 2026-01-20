"""
Category, dietary tag, and allergen endpoints for FastAPI.
Provides lookup endpoints for recipe classification data.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, OptionalUser
from src.api.schemas import CategoryResponse, DietaryTagResponse, AllergenResponse
from src.database.models import Category, DietaryTag, Allergen

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="List all categories"
)
def list_categories(
    db: DatabaseSession,
    user: OptionalUser = None,
    category_type: str = Query(None, description="Filter by category type (cuisine, meal_type, occasion)"),
):
    """
    Get all recipe categories.

    Categories include:
    - Cuisine types (Italian, Mexican, Asian, etc.)
    - Meal types (breakfast, lunch, dinner, etc.)
    - Occasions (weeknight, special, quick, etc.)

    Optionally filter by category_type.
    """
    query = db.query(Category)

    if category_type:
        query = query.filter(Category.category_type == category_type)

    categories = query.order_by(Category.name).all()

    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            category_type=cat.category_type,
            description=cat.description
        )
        for cat in categories
    ]


@router.get(
    "/{slug}",
    response_model=CategoryResponse,
    summary="Get category by slug",
    responses={
        404: {"description": "Category not found"}
    }
)
def get_category_by_slug(
    slug: str,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get a specific category by its URL slug.
    """
    category = db.query(Category).filter(Category.slug == slug).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug '{slug}' not found"
        )

    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        category_type=category.category_type,
        description=category.description
    )


@router.get(
    "/dietary-tags",
    response_model=List[DietaryTagResponse],
    summary="List all dietary tags",
    deprecated=True,
    description="Use /dietary-tags endpoint instead"
)
def list_dietary_tags_deprecated(
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get all dietary tags (deprecated - use /dietary-tags instead).
    """
    tags = db.query(DietaryTag).order_by(DietaryTag.name).all()

    return [
        DietaryTagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description
        )
        for tag in tags
    ]


# Dietary tags router (separate from categories)
dietary_tags_router = APIRouter(
    prefix="/dietary-tags",
    tags=["dietary-tags"],
)


@dietary_tags_router.get(
    "",
    response_model=List[DietaryTagResponse],
    summary="List all dietary tags"
)
def list_dietary_tags(
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get all dietary tags.

    Dietary tags include:
    - Vegan
    - Vegetarian
    - Keto
    - Low-carb
    - High-protein
    - Gluten-free
    - Dairy-free
    - etc.
    """
    tags = db.query(DietaryTag).order_by(DietaryTag.name).all()

    return [
        DietaryTagResponse(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description
        )
        for tag in tags
    ]


@dietary_tags_router.get(
    "/{slug}",
    response_model=DietaryTagResponse,
    summary="Get dietary tag by slug",
    responses={
        404: {"description": "Dietary tag not found"}
    }
)
def get_dietary_tag_by_slug(
    slug: str,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get a specific dietary tag by its URL slug.
    """
    tag = db.query(DietaryTag).filter(DietaryTag.slug == slug).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dietary tag with slug '{slug}' not found"
        )

    return DietaryTagResponse(
        id=tag.id,
        name=tag.name,
        slug=tag.slug,
        description=tag.description
    )


# Allergens router
allergens_router = APIRouter(
    prefix="/allergens",
    tags=["allergens"],
)


@allergens_router.get(
    "",
    response_model=List[AllergenResponse],
    summary="List all allergens"
)
def list_allergens(
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get all allergens.

    Common allergens include:
    - Dairy
    - Eggs
    - Nuts
    - Peanuts
    - Shellfish
    - Soy
    - Wheat/Gluten
    - Fish
    - etc.
    """
    allergens = db.query(Allergen).order_by(Allergen.name).all()

    return [
        AllergenResponse(
            id=allergen.id,
            name=allergen.name,
            description=allergen.description
        )
        for allergen in allergens
    ]


@allergens_router.get(
    "/{allergen_id}",
    response_model=AllergenResponse,
    summary="Get allergen by ID",
    responses={
        404: {"description": "Allergen not found"}
    }
)
def get_allergen_by_id(
    allergen_id: int,
    db: DatabaseSession,
    user: OptionalUser = None,
):
    """
    Get a specific allergen by ID.
    """
    allergen = db.query(Allergen).filter(Allergen.id == allergen_id).first()

    if not allergen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allergen with ID {allergen_id} not found"
        )

    return AllergenResponse(
        id=allergen.id,
        name=allergen.name,
        description=allergen.description
    )
