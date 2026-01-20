"""
User preferences and allergen profile endpoints.
Manage dietary preferences, nutritional targets, and allergen profiles.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import DatabaseSession, CurrentUser
from src.api.schemas.user import (
    UserPreferenceResponse, UserPreferenceUpdate,
    UserAllergenCreate, UserAllergenBulkCreate,
    UserAllergenListResponse, UserAllergenResponse,
    UserDietaryTagsUpdate, UserDietaryTagsResponse,
    DietaryTagResponse
)
from src.api.services.preference_service import PreferenceService
from src.utils.logger import get_logger

logger = get_logger("api.routers.users")

router = APIRouter(prefix="/users", tags=["user-preferences"])


# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================

@router.get(
    "/me/preferences",
    response_model=UserPreferenceResponse,
    summary="Get user preferences",
    description="Get authenticated user's dietary preferences and settings"
)
def get_user_preferences(
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserPreferenceResponse:
    """
    Get current user's preferences.

    Includes dietary restrictions, nutritional targets, and meal planning settings.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        User preferences with dietary tags

    Raises:
        401: If not authenticated
        404: If preferences not found

    Example:
        GET /users/me/preferences
        Authorization: Bearer <token>

        Response:
        {
            "id": 1,
            "user_id": 1,
            "default_servings": 4,
            "calorie_target": 2000,
            "protein_target_g": 150,
            "carb_limit_g": 200,
            "fat_limit_g": 70,
            "dietary_tags": [...],
            "created_at": "2026-01-20T10:00:00Z",
            "updated_at": "2026-01-20T15:30:00Z"
        }
    """
    user_id = int(current_user.get("sub"))
    preferences = PreferenceService.get_preferences(db, user_id)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    return UserPreferenceResponse.model_validate(preferences)


@router.put(
    "/me/preferences",
    response_model=UserPreferenceResponse,
    summary="Update user preferences",
    description="Update authenticated user's dietary preferences and settings"
)
def update_user_preferences(
    preferences_update: UserPreferenceUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserPreferenceResponse:
    """
    Update current user's preferences.

    Args:
        preferences_update: Updated preference values
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Updated user preferences

    Raises:
        401: If not authenticated

    Example:
        PUT /users/me/preferences
        Authorization: Bearer <token>
        {
            "default_servings": 2,
            "calorie_target": 1800,
            "protein_target_g": 120,
            "carb_limit_g": 150
        }
    """
    user_id = int(current_user.get("sub"))

    # Convert to dict, excluding None values
    update_data = preferences_update.model_dump(exclude_none=True)

    preferences = PreferenceService.update_preferences(db, user_id, update_data)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

    logger.info(f"Updated preferences for user {user_id}")

    return UserPreferenceResponse.model_validate(preferences)


# ============================================================================
# ALLERGEN PROFILE ENDPOINTS
# ============================================================================

@router.get(
    "/me/allergens",
    response_model=UserAllergenListResponse,
    summary="Get allergen profile",
    description="Get authenticated user's allergen profile with severity levels"
)
def get_user_allergens(
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserAllergenListResponse:
    """
    Get current user's allergen profile.

    Returns all allergens with severity levels (avoid, severe, trace_ok).

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of user allergens with details

    Raises:
        401: If not authenticated

    Example:
        GET /users/me/allergens
        Authorization: Bearer <token>

        Response:
        {
            "allergens": [
                {
                    "user_id": 1,
                    "allergen_id": 5,
                    "severity": "severe",
                    "allergen": {
                        "id": 5,
                        "name": "Peanuts",
                        "description": "Tree nuts and peanuts"
                    },
                    "created_at": "2026-01-20T10:00:00Z"
                }
            ],
            "count": 1
        }
    """
    user_id = int(current_user.get("sub"))
    allergens = PreferenceService.get_user_allergens(db, user_id)

    allergen_responses = [
        UserAllergenResponse.model_validate(ua) for ua in allergens
    ]

    return UserAllergenListResponse(
        allergens=allergen_responses,
        count=len(allergen_responses)
    )


@router.put(
    "/me/allergens",
    response_model=UserAllergenListResponse,
    summary="Update allergen profile",
    description="Replace user's entire allergen profile with new list"
)
def update_user_allergens(
    allergen_data: UserAllergenBulkCreate,
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserAllergenListResponse:
    """
    Replace user's allergen profile.

    Removes all existing allergens and sets new ones.

    Args:
        allergen_data: List of allergens with severity levels
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Updated allergen profile

    Raises:
        401: If not authenticated
        400: If invalid allergen ID or severity

    Example:
        PUT /users/me/allergens
        Authorization: Bearer <token>
        {
            "allergens": [
                {"allergen_id": 1, "severity": "severe"},
                {"allergen_id": 3, "severity": "avoid"}
            ]
        }
    """
    user_id = int(current_user.get("sub"))

    try:
        # Convert to list of dicts
        allergen_list = [
            {"allergen_id": a.allergen_id, "severity": a.severity}
            for a in allergen_data.allergens
        ]

        allergens = PreferenceService.set_user_allergens(db, user_id, allergen_list)

        allergen_responses = [
            UserAllergenResponse.model_validate(ua) for ua in allergens
        ]

        logger.info(f"Updated allergen profile for user {user_id}: {len(allergens)} allergens")

        return UserAllergenListResponse(
            allergens=allergen_responses,
            count=len(allergen_responses)
        )

    except ValueError as e:
        logger.warning(f"Failed to update allergens for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/me/allergens",
    response_model=UserAllergenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add single allergen",
    description="Add or update a single allergen in user's profile"
)
def add_user_allergen(
    allergen: UserAllergenCreate,
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserAllergenResponse:
    """
    Add or update a single allergen.

    If allergen already exists, updates the severity level.

    Args:
        allergen: Allergen ID and severity level
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Created/updated allergen entry

    Raises:
        401: If not authenticated
        400: If invalid allergen ID or severity

    Example:
        POST /users/me/allergens
        Authorization: Bearer <token>
        {
            "allergen_id": 5,
            "severity": "severe"
        }
    """
    user_id = int(current_user.get("sub"))

    try:
        user_allergen = PreferenceService.set_user_allergen(
            db=db,
            user_id=user_id,
            allergen_id=allergen.allergen_id,
            severity=allergen.severity
        )

        logger.info(f"Added allergen {allergen.allergen_id} for user {user_id}")

        return UserAllergenResponse.model_validate(user_allergen)

    except ValueError as e:
        logger.warning(f"Failed to add allergen for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/me/allergens/{allergen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove allergen",
    description="Remove an allergen from user's profile"
)
def remove_user_allergen(
    allergen_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
) -> None:
    """
    Remove an allergen from user's profile.

    Args:
        allergen_id: Allergen ID to remove
        current_user: Current authenticated user from token
        db: Database session

    Raises:
        401: If not authenticated
        404: If allergen not in user's profile

    Example:
        DELETE /users/me/allergens/5
        Authorization: Bearer <token>
    """
    user_id = int(current_user.get("sub"))

    success = PreferenceService.remove_user_allergen(db, user_id, allergen_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergen not found in user profile"
        )

    logger.info(f"Removed allergen {allergen_id} from user {user_id}")


# ============================================================================
# DIETARY TAGS ENDPOINTS
# ============================================================================

@router.get(
    "/me/dietary-tags",
    response_model=UserDietaryTagsResponse,
    summary="Get dietary tags",
    description="Get user's dietary preference tags (vegan, keto, etc.)"
)
def get_user_dietary_tags(
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserDietaryTagsResponse:
    """
    Get user's dietary tags.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of dietary tags

    Raises:
        401: If not authenticated

    Example:
        GET /users/me/dietary-tags
        Authorization: Bearer <token>

        Response:
        {
            "dietary_tags": [
                {"id": 1, "name": "Vegan", "slug": "vegan"},
                {"id": 3, "name": "Gluten-Free", "slug": "gluten-free"}
            ],
            "count": 2
        }
    """
    user_id = int(current_user.get("sub"))
    tags = PreferenceService.get_user_dietary_tags(db, user_id)

    tag_responses = [DietaryTagResponse.model_validate(tag) for tag in tags]

    return UserDietaryTagsResponse(
        dietary_tags=tag_responses,
        count=len(tag_responses)
    )


@router.put(
    "/me/dietary-tags",
    response_model=UserDietaryTagsResponse,
    summary="Update dietary tags",
    description="Replace user's dietary tags with new list"
)
def update_user_dietary_tags(
    tags_update: UserDietaryTagsUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
) -> UserDietaryTagsResponse:
    """
    Update user's dietary tags.

    Replaces all existing tags with the provided list.

    Args:
        tags_update: List of dietary tag IDs
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Updated dietary tags

    Raises:
        401: If not authenticated

    Example:
        PUT /users/me/dietary-tags
        Authorization: Bearer <token>
        {
            "dietary_tag_ids": [1, 3, 5]
        }
    """
    user_id = int(current_user.get("sub"))

    tags = PreferenceService.set_user_dietary_tags(
        db=db,
        user_id=user_id,
        dietary_tag_ids=tags_update.dietary_tag_ids
    )

    tag_responses = [DietaryTagResponse.model_validate(tag) for tag in tags]

    logger.info(f"Updated dietary tags for user {user_id}: {len(tags)} tags")

    return UserDietaryTagsResponse(
        dietary_tags=tag_responses,
        count=len(tag_responses)
    )


# Export router
users_router = router
