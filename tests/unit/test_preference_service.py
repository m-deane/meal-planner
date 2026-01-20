"""
Unit tests for PreferenceService.
Tests user preference and allergen profile management.
"""

import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from src.api.services.preference_service import PreferenceService
from src.api.services.user_service import UserService
from src.database.models import (
    User, UserPreference, UserAllergen, Allergen, DietaryTag
)


class TestPreferenceService:
    """Test suite for PreferenceService operations."""

    @pytest.fixture
    def user(self, db_session: Session) -> User:
        """Create a test user."""
        return UserService.create_user(
            db=db_session,
            email="preftest@example.com",
            username="preftest",
            password="TestPass123"
        )

    @pytest.fixture
    def allergens(self, db_session: Session) -> list[Allergen]:
        """Create test allergens."""
        allergen_names = ["Peanuts", "Shellfish", "Dairy", "Gluten"]
        allergens = []

        for name in allergen_names:
            allergen = Allergen(name=name, description=f"{name} allergy")
            db_session.add(allergen)
            allergens.append(allergen)

        db_session.commit()

        for allergen in allergens:
            db_session.refresh(allergen)

        return allergens

    @pytest.fixture
    def dietary_tags(self, db_session: Session) -> list[DietaryTag]:
        """Create test dietary tags."""
        tag_data = [
            ("Vegan", "vegan", "No animal products"),
            ("Vegetarian", "vegetarian", "No meat"),
            ("Keto", "keto", "Low carb, high fat"),
            ("Gluten-Free", "gluten-free", "No gluten")
        ]
        tags = []

        for name, slug, desc in tag_data:
            tag = DietaryTag(name=name, slug=slug, description=desc)
            db_session.add(tag)
            tags.append(tag)

        db_session.commit()

        for tag in tags:
            db_session.refresh(tag)

        return tags

    def test_get_preferences_exists(self, db_session: Session, user: User):
        """Test getting existing preferences."""
        prefs = PreferenceService.get_preferences(db_session, user.id)

        assert prefs is not None
        assert prefs.user_id == user.id
        assert prefs.default_servings == 2

    def test_get_preferences_not_found(self, db_session: Session):
        """Test getting preferences for non-existent user."""
        prefs = PreferenceService.get_preferences(db_session, 99999)
        assert prefs is None

    def test_create_preferences(self, db_session: Session):
        """Test creating new preferences."""
        # Create user without auto-creating preferences
        user = User(
            email="createpref@example.com",
            username="createpref",
            password_hash="hash123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        prefs = PreferenceService.create_preferences(
            db=db_session,
            user_id=user.id,
            default_servings=4,
            calorie_target=2000,
            protein_target_g=Decimal("150.5"),
            carb_limit_g=Decimal("200.0"),
            fat_limit_g=Decimal("70.0")
        )

        assert prefs is not None
        assert prefs.user_id == user.id
        assert prefs.default_servings == 4
        assert prefs.calorie_target == 2000
        assert prefs.protein_target_g == Decimal("150.5")
        assert prefs.carb_limit_g == Decimal("200.0")
        assert prefs.fat_limit_g == Decimal("70.0")

    def test_create_preferences_already_exist(self, db_session: Session, user: User):
        """Test creating preferences when they already exist."""
        existing = PreferenceService.get_preferences(db_session, user.id)
        assert existing is not None

        # Try to create again
        prefs = PreferenceService.create_preferences(
            db=db_session,
            user_id=user.id,
            default_servings=4
        )

        # Should return existing
        assert prefs.id == existing.id

    def test_update_preferences(self, db_session: Session, user: User):
        """Test updating user preferences."""
        update_data = {
            "default_servings": 6,
            "calorie_target": 2500,
            "protein_target_g": Decimal("180.0")
        }

        prefs = PreferenceService.update_preferences(db_session, user.id, update_data)

        assert prefs is not None
        assert prefs.default_servings == 6
        assert prefs.calorie_target == 2500
        assert prefs.protein_target_g == Decimal("180.0")

    def test_update_preferences_creates_if_not_exist(self, db_session: Session):
        """Test updating preferences creates them if they don't exist."""
        # Create user without preferences
        user = User(
            email="updatecreate@example.com",
            username="updatecreate",
            password_hash="hash123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        update_data = {
            "default_servings": 3,
            "calorie_target": 1800
        }

        prefs = PreferenceService.update_preferences(db_session, user.id, update_data)

        assert prefs is not None
        assert prefs.default_servings == 3
        assert prefs.calorie_target == 1800

    def test_get_user_allergens_empty(self, db_session: Session, user: User):
        """Test getting allergens when user has none."""
        allergens = PreferenceService.get_user_allergens(db_session, user.id)
        assert allergens == []

    def test_set_user_allergen(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test adding a single allergen."""
        allergen = allergens[0]

        user_allergen = PreferenceService.set_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=allergen.id,
            severity="severe"
        )

        assert user_allergen is not None
        assert user_allergen.user_id == user.id
        assert user_allergen.allergen_id == allergen.id
        assert user_allergen.severity == "severe"

    def test_set_user_allergen_update_existing(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test updating an existing allergen severity."""
        allergen = allergens[0]

        # Add allergen
        PreferenceService.set_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=allergen.id,
            severity="avoid"
        )

        # Update severity
        updated = PreferenceService.set_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=allergen.id,
            severity="trace_ok"
        )

        assert updated.severity == "trace_ok"

        # Verify only one entry exists
        all_allergens = PreferenceService.get_user_allergens(db_session, user.id)
        assert len(all_allergens) == 1

    def test_set_user_allergen_invalid_severity(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test adding allergen with invalid severity."""
        with pytest.raises(ValueError, match="Severity must be one of"):
            PreferenceService.set_user_allergen(
                db=db_session,
                user_id=user.id,
                allergen_id=allergens[0].id,
                severity="invalid"
            )

    def test_set_user_allergen_invalid_allergen_id(
        self, db_session: Session, user: User
    ):
        """Test adding non-existent allergen."""
        with pytest.raises(ValueError, match="Allergen with ID .* not found"):
            PreferenceService.set_user_allergen(
                db=db_session,
                user_id=user.id,
                allergen_id=99999,
                severity="avoid"
            )

    def test_set_user_allergens_bulk(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test setting multiple allergens at once."""
        allergen_data = [
            {"allergen_id": allergens[0].id, "severity": "severe"},
            {"allergen_id": allergens[1].id, "severity": "avoid"},
            {"allergen_id": allergens[2].id, "severity": "trace_ok"}
        ]

        result = PreferenceService.set_user_allergens(
            db=db_session,
            user_id=user.id,
            allergen_data=allergen_data
        )

        assert len(result) == 3
        assert result[0].severity == "severe"
        assert result[1].severity == "avoid"
        assert result[2].severity == "trace_ok"

    def test_set_user_allergens_replaces_existing(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test that setting allergens replaces existing ones."""
        # Set initial allergens
        initial_data = [
            {"allergen_id": allergens[0].id, "severity": "severe"},
            {"allergen_id": allergens[1].id, "severity": "avoid"}
        ]
        PreferenceService.set_user_allergens(db_session, user.id, initial_data)

        # Replace with new set
        new_data = [
            {"allergen_id": allergens[2].id, "severity": "trace_ok"}
        ]
        result = PreferenceService.set_user_allergens(db_session, user.id, new_data)

        assert len(result) == 1
        assert result[0].allergen_id == allergens[2].id

        # Verify old allergens are gone
        all_allergens = PreferenceService.get_user_allergens(db_session, user.id)
        assert len(all_allergens) == 1

    def test_remove_user_allergen(
        self, db_session: Session, user: User, allergens: list[Allergen]
    ):
        """Test removing an allergen."""
        # Add allergen
        PreferenceService.set_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=allergens[0].id,
            severity="avoid"
        )

        # Remove it
        success = PreferenceService.remove_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=allergens[0].id
        )

        assert success is True

        # Verify it's gone
        remaining = PreferenceService.get_user_allergens(db_session, user.id)
        assert len(remaining) == 0

    def test_remove_user_allergen_not_found(
        self, db_session: Session, user: User
    ):
        """Test removing non-existent allergen."""
        success = PreferenceService.remove_user_allergen(
            db=db_session,
            user_id=user.id,
            allergen_id=99999
        )

        assert success is False

    def test_get_user_dietary_tags_empty(self, db_session: Session, user: User):
        """Test getting dietary tags when user has none."""
        tags = PreferenceService.get_user_dietary_tags(db_session, user.id)
        assert tags == []

    def test_get_user_dietary_tags_no_preferences(self, db_session: Session):
        """Test getting dietary tags when user has no preferences."""
        # Create user without preferences
        user = User(
            email="notags@example.com",
            username="notags",
            password_hash="hash123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        tags = PreferenceService.get_user_dietary_tags(db_session, user.id)
        assert tags == []

    def test_set_user_dietary_tags(
        self, db_session: Session, user: User, dietary_tags: list[DietaryTag]
    ):
        """Test setting dietary tags for user."""
        tag_ids = [dietary_tags[0].id, dietary_tags[2].id]

        result = PreferenceService.set_user_dietary_tags(
            db=db_session,
            user_id=user.id,
            dietary_tag_ids=tag_ids
        )

        assert len(result) == 2
        assert result[0].id in tag_ids
        assert result[1].id in tag_ids

    def test_set_user_dietary_tags_replaces_existing(
        self, db_session: Session, user: User, dietary_tags: list[DietaryTag]
    ):
        """Test that setting tags replaces existing ones."""
        # Set initial tags
        initial_ids = [dietary_tags[0].id, dietary_tags[1].id]
        PreferenceService.set_user_dietary_tags(db_session, user.id, initial_ids)

        # Replace with new tags
        new_ids = [dietary_tags[2].id]
        result = PreferenceService.set_user_dietary_tags(db_session, user.id, new_ids)

        assert len(result) == 1
        assert result[0].id == dietary_tags[2].id

    def test_set_user_dietary_tags_creates_preferences(
        self, db_session: Session, dietary_tags: list[DietaryTag]
    ):
        """Test setting dietary tags creates preferences if they don't exist."""
        # Create user without preferences
        user = User(
            email="createtags@example.com",
            username="createtags",
            password_hash="hash123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        tag_ids = [dietary_tags[0].id]
        result = PreferenceService.set_user_dietary_tags(db_session, user.id, tag_ids)

        assert len(result) == 1

        # Verify preferences were created
        prefs = PreferenceService.get_preferences(db_session, user.id)
        assert prefs is not None
