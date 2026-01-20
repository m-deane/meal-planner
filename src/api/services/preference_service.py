"""
User preference and allergen profile service.
Manages dietary preferences, nutritional targets, and allergen profiles.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from src.database.models import (
    UserPreference, UserAllergen, Allergen, DietaryTag, UserDietaryPreference
)
from src.utils.logger import get_logger

logger = get_logger("api.services.preference")


class PreferenceService:
    """Service for managing user preferences and allergen profiles."""

    @staticmethod
    def get_preferences(db: Session, user_id: int) -> Optional[UserPreference]:
        """
        Get user preferences by user ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            UserPreference instance or None if not found

        Example:
            prefs = PreferenceService.get_preferences(db, 1)
        """
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

    @staticmethod
    def create_preferences(
        db: Session,
        user_id: int,
        default_servings: int = 2,
        calorie_target: Optional[int] = None,
        protein_target_g: Optional[Decimal] = None,
        carb_limit_g: Optional[Decimal] = None,
        fat_limit_g: Optional[Decimal] = None,
        preferred_cuisines: Optional[str] = None,
        excluded_ingredients: Optional[str] = None
    ) -> UserPreference:
        """
        Create user preferences (if they don't exist).

        Args:
            db: Database session
            user_id: User ID
            default_servings: Default number of servings
            calorie_target: Daily calorie target
            protein_target_g: Protein target in grams
            carb_limit_g: Carbohydrate limit in grams
            fat_limit_g: Fat limit in grams
            preferred_cuisines: JSON string of preferred cuisines
            excluded_ingredients: JSON string of excluded ingredients

        Returns:
            Created or existing UserPreference instance

        Example:
            prefs = PreferenceService.create_preferences(
                db, user_id=1, default_servings=4, calorie_target=2000
            )
        """
        # Check if preferences already exist
        existing = PreferenceService.get_preferences(db, user_id)
        if existing:
            logger.warning(f"Preferences already exist for user {user_id}")
            return existing

        preferences = UserPreference(
            user_id=user_id,
            default_servings=default_servings,
            calorie_target=calorie_target,
            protein_target_g=protein_target_g,
            carb_limit_g=carb_limit_g,
            fat_limit_g=fat_limit_g,
            preferred_cuisines=preferred_cuisines,
            excluded_ingredients=excluded_ingredients
        )

        db.add(preferences)
        db.commit()
        db.refresh(preferences)

        logger.info(f"Created preferences for user {user_id}")
        return preferences

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: int,
        data: Dict[str, Any]
    ) -> Optional[UserPreference]:
        """
        Update user preferences.

        Args:
            db: Database session
            user_id: User ID
            data: Dictionary of fields to update

        Returns:
            Updated UserPreference instance or None if not found

        Example:
            prefs = PreferenceService.update_preferences(
                db, 1, {"default_servings": 4, "calorie_target": 2000}
            )
        """
        preferences = PreferenceService.get_preferences(db, user_id)
        if not preferences:
            logger.warning(f"Preferences not found for user {user_id}, creating new")
            # Create if doesn't exist
            return PreferenceService.create_preferences(db, user_id, **data)

        # Update fields
        allowed_fields = {
            'default_servings', 'calorie_target', 'protein_target_g',
            'carb_limit_g', 'fat_limit_g', 'preferred_cuisines',
            'excluded_ingredients'
        }

        for key, value in data.items():
            if key in allowed_fields and value is not None:
                setattr(preferences, key, value)

        db.commit()
        db.refresh(preferences)

        logger.info(f"Updated preferences for user {user_id}")
        return preferences

    @staticmethod
    def get_user_allergens(db: Session, user_id: int) -> List[UserAllergen]:
        """
        Get all allergens for a user with severity levels.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of UserAllergen instances

        Example:
            allergens = PreferenceService.get_user_allergens(db, 1)
            for ua in allergens:
                print(f"{ua.allergen.name}: {ua.severity}")
        """
        return db.query(UserAllergen).filter(
            UserAllergen.user_id == user_id
        ).all()

    @staticmethod
    def set_user_allergen(
        db: Session,
        user_id: int,
        allergen_id: int,
        severity: str = 'avoid'
    ) -> UserAllergen:
        """
        Set or update a single allergen for a user.

        Args:
            db: Database session
            user_id: User ID
            allergen_id: Allergen ID
            severity: Severity level ('avoid', 'severe', 'trace_ok')

        Returns:
            Created or updated UserAllergen instance

        Raises:
            ValueError: If allergen_id doesn't exist or severity is invalid

        Example:
            ua = PreferenceService.set_user_allergen(db, 1, 5, 'severe')
        """
        # Validate severity
        valid_severities = ['avoid', 'severe', 'trace_ok']
        if severity not in valid_severities:
            raise ValueError(f"Severity must be one of {valid_severities}")

        # Check if allergen exists
        allergen = db.query(Allergen).filter(Allergen.id == allergen_id).first()
        if not allergen:
            raise ValueError(f"Allergen with ID {allergen_id} not found")

        # Check if user allergen already exists
        user_allergen = db.query(UserAllergen).filter(
            UserAllergen.user_id == user_id,
            UserAllergen.allergen_id == allergen_id
        ).first()

        if user_allergen:
            # Update existing
            user_allergen.severity = severity
            logger.info(f"Updated allergen {allergen_id} for user {user_id}: {severity}")
        else:
            # Create new
            user_allergen = UserAllergen(
                user_id=user_id,
                allergen_id=allergen_id,
                severity=severity
            )
            db.add(user_allergen)
            logger.info(f"Added allergen {allergen_id} for user {user_id}: {severity}")

        db.commit()
        db.refresh(user_allergen)

        return user_allergen

    @staticmethod
    def set_user_allergens(
        db: Session,
        user_id: int,
        allergen_data: List[Dict[str, Any]]
    ) -> List[UserAllergen]:
        """
        Set multiple allergens for a user (replaces existing).

        Args:
            db: Database session
            user_id: User ID
            allergen_data: List of dicts with 'allergen_id' and 'severity'

        Returns:
            List of created UserAllergen instances

        Example:
            allergens = PreferenceService.set_user_allergens(
                db, 1,
                [
                    {"allergen_id": 1, "severity": "severe"},
                    {"allergen_id": 3, "severity": "avoid"}
                ]
            )
        """
        # Remove existing allergens
        db.query(UserAllergen).filter(UserAllergen.user_id == user_id).delete()

        # Add new allergens
        user_allergens = []
        for data in allergen_data:
            allergen_id = data.get('allergen_id')
            severity = data.get('severity', 'avoid')

            user_allergen = UserAllergen(
                user_id=user_id,
                allergen_id=allergen_id,
                severity=severity
            )
            db.add(user_allergen)
            user_allergens.append(user_allergen)

        db.commit()

        # Refresh all instances
        for ua in user_allergens:
            db.refresh(ua)

        logger.info(f"Set {len(user_allergens)} allergens for user {user_id}")
        return user_allergens

    @staticmethod
    def remove_user_allergen(
        db: Session,
        user_id: int,
        allergen_id: int
    ) -> bool:
        """
        Remove an allergen from user's profile.

        Args:
            db: Database session
            user_id: User ID
            allergen_id: Allergen ID

        Returns:
            True if removed, False if not found

        Example:
            removed = PreferenceService.remove_user_allergen(db, 1, 5)
        """
        result = db.query(UserAllergen).filter(
            UserAllergen.user_id == user_id,
            UserAllergen.allergen_id == allergen_id
        ).delete()

        db.commit()

        if result > 0:
            logger.info(f"Removed allergen {allergen_id} from user {user_id}")
            return True

        logger.warning(f"Allergen {allergen_id} not found for user {user_id}")
        return False

    @staticmethod
    def get_user_dietary_tags(db: Session, user_id: int) -> List[DietaryTag]:
        """
        Get dietary tags associated with user preferences.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of DietaryTag instances

        Example:
            tags = PreferenceService.get_user_dietary_tags(db, 1)
            for tag in tags:
                print(tag.name)  # e.g., "vegan", "keto"
        """
        preferences = PreferenceService.get_preferences(db, user_id)
        if not preferences:
            return []

        return preferences.dietary_tags

    @staticmethod
    def set_user_dietary_tags(
        db: Session,
        user_id: int,
        dietary_tag_ids: List[int]
    ) -> List[DietaryTag]:
        """
        Set dietary tags for user (replaces existing).

        Args:
            db: Database session
            user_id: User ID
            dietary_tag_ids: List of dietary tag IDs

        Returns:
            List of associated DietaryTag instances

        Example:
            tags = PreferenceService.set_user_dietary_tags(db, 1, [1, 3, 5])
        """
        preferences = PreferenceService.get_preferences(db, user_id)
        if not preferences:
            # Create preferences if they don't exist
            preferences = PreferenceService.create_preferences(db, user_id)

        # Clear existing associations
        db.query(UserDietaryPreference).filter(
            UserDietaryPreference.user_preference_id == preferences.id
        ).delete()

        # Add new associations
        for tag_id in dietary_tag_ids:
            assoc = UserDietaryPreference(
                user_preference_id=preferences.id,
                dietary_tag_id=tag_id
            )
            db.add(assoc)

        db.commit()
        db.refresh(preferences)

        logger.info(f"Set {len(dietary_tag_ids)} dietary tags for user {user_id}")
        return preferences.dietary_tags
