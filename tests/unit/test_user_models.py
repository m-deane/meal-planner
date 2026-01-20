"""
Unit tests for Phase 3 user-related database models.

Tests cover User, UserPreference, FavoriteRecipe, SavedMealPlan,
UserAllergen, and IngredientPrice models.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.database.models import (
    Base, User, UserPreference, FavoriteRecipe, SavedMealPlan,
    UserAllergen, IngredientPrice, Recipe, Ingredient, Unit, Allergen
)


@pytest.fixture
def engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a new database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_user(session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password_123",
        is_active=True,
        is_verified=True
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def sample_recipe(session):
    """Create a sample recipe for testing."""
    recipe = Recipe(
        gousto_id="TEST001",
        slug="test-recipe",
        name="Test Recipe",
        description="A test recipe",
        cooking_time_minutes=30,
        prep_time_minutes=15,
        servings=2,
        source_url="https://test.com/recipe"
    )
    session.add(recipe)
    session.commit()
    return recipe


@pytest.fixture
def sample_ingredient(session):
    """Create a sample ingredient for testing."""
    ingredient = Ingredient(
        name="Chicken Breast",
        category="protein"
    )
    session.add(ingredient)
    session.commit()
    return ingredient


@pytest.fixture
def sample_unit(session):
    """Create a sample unit for testing."""
    unit = Unit(
        name="gram",
        abbreviation="g",
        unit_type="weight",
        metric_equivalent=Decimal("1.0")
    )
    session.add(unit)
    session.commit()
    return unit


@pytest.fixture
def sample_allergen(session):
    """Create a sample allergen for testing."""
    allergen = Allergen(
        name="Peanuts",
        description="Tree nuts and peanuts"
    )
    session.add(allergen)
    session.commit()
    return allergen


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, session):
        """Test creating a basic user."""
        user = User(
            email="user@test.com",
            username="newuser",
            password_hash="hashed123"
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.email == "user@test.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None

    def test_user_unique_email(self, session, sample_user):
        """Test that email must be unique."""
        duplicate_user = User(
            email=sample_user.email,
            username="different",
            password_hash="hash"
        )
        session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_user_unique_username(self, session, sample_user):
        """Test that username must be unique."""
        duplicate_user = User(
            email="different@test.com",
            username=sample_user.username,
            password_hash="hash"
        )
        session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_user_relationships(self, session, sample_user):
        """Test that user has all expected relationships."""
        assert hasattr(sample_user, 'preferences')
        assert hasattr(sample_user, 'favorites')
        assert hasattr(sample_user, 'saved_meal_plans')
        assert hasattr(sample_user, 'allergen_profile')


class TestUserPreferenceModel:
    """Tests for UserPreference model."""

    def test_create_user_preference(self, session, sample_user):
        """Test creating user preferences."""
        preference = UserPreference(
            user_id=sample_user.id,
            default_servings=4,
            calorie_target=2000,
            protein_target_g=Decimal("150.0"),
            carb_limit_g=Decimal("200.0"),
            fat_limit_g=Decimal("70.0"),
            preferred_cuisines='["Italian", "Japanese"]',
            excluded_ingredients='["peanuts"]'
        )
        session.add(preference)
        session.commit()

        assert preference.id is not None
        assert preference.user_id == sample_user.id
        assert preference.default_servings == 4
        assert preference.calorie_target == 2000
        assert preference.protein_target_g == Decimal("150.0")

    def test_user_preference_defaults(self, session, sample_user):
        """Test default values for user preferences."""
        preference = UserPreference(user_id=sample_user.id)
        session.add(preference)
        session.commit()

        assert preference.default_servings == 2
        assert preference.calorie_target is None

    def test_user_preference_unique_user(self, session, sample_user):
        """Test that each user can only have one preference record."""
        pref1 = UserPreference(user_id=sample_user.id, default_servings=2)
        session.add(pref1)
        session.commit()

        pref2 = UserPreference(user_id=sample_user.id, default_servings=4)
        session.add(pref2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_user_preference_relationship(self, session, sample_user):
        """Test bidirectional relationship between User and UserPreference."""
        preference = UserPreference(
            user_id=sample_user.id,
            default_servings=4
        )
        session.add(preference)
        session.commit()

        # Access from user
        assert sample_user.preferences.default_servings == 4

        # Access from preference
        assert preference.user.id == sample_user.id

    def test_user_preference_check_constraints(self, session, sample_user):
        """Test check constraints on nutritional values."""
        # Negative servings should fail
        invalid_pref = UserPreference(
            user_id=sample_user.id,
            default_servings=0
        )
        session.add(invalid_pref)

        with pytest.raises(IntegrityError):
            session.commit()


class TestFavoriteRecipeModel:
    """Tests for FavoriteRecipe model."""

    def test_create_favorite_recipe(self, session, sample_user, sample_recipe):
        """Test creating a favorite recipe."""
        favorite = FavoriteRecipe(
            user_id=sample_user.id,
            recipe_id=sample_recipe.id,
            notes="Great recipe!"
        )
        session.add(favorite)
        session.commit()

        assert favorite.id is not None
        assert favorite.user_id == sample_user.id
        assert favorite.recipe_id == sample_recipe.id
        assert favorite.notes == "Great recipe!"
        assert favorite.created_at is not None

    def test_favorite_recipe_unique_constraint(self, session, sample_user, sample_recipe):
        """Test that a user cannot favorite the same recipe twice."""
        fav1 = FavoriteRecipe(user_id=sample_user.id, recipe_id=sample_recipe.id)
        session.add(fav1)
        session.commit()

        fav2 = FavoriteRecipe(user_id=sample_user.id, recipe_id=sample_recipe.id)
        session.add(fav2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_favorite_recipe_relationships(self, session, sample_user, sample_recipe):
        """Test relationships between FavoriteRecipe, User, and Recipe."""
        favorite = FavoriteRecipe(
            user_id=sample_user.id,
            recipe_id=sample_recipe.id
        )
        session.add(favorite)
        session.commit()

        # Access from favorite
        assert favorite.user.id == sample_user.id
        assert favorite.recipe.id == sample_recipe.id

        # Access from user
        user_favorites = list(sample_user.favorites)
        assert len(user_favorites) == 1
        assert user_favorites[0].recipe_id == sample_recipe.id

        # Access from recipe (favorited_by)
        recipe_favorited = list(sample_recipe.favorited_by)
        assert len(recipe_favorited) == 1
        assert recipe_favorited[0].user_id == sample_user.id

    def test_favorite_recipe_cascade_delete_user(self, session, sample_user, sample_recipe):
        """Test that favorites are deleted when user is deleted."""
        favorite = FavoriteRecipe(
            user_id=sample_user.id,
            recipe_id=sample_recipe.id
        )
        session.add(favorite)
        session.commit()

        user_id = sample_user.id
        session.delete(sample_user)
        session.commit()

        # Favorite should be deleted
        remaining = session.query(FavoriteRecipe).filter_by(user_id=user_id).count()
        assert remaining == 0


class TestSavedMealPlanModel:
    """Tests for SavedMealPlan model."""

    def test_create_saved_meal_plan(self, session, sample_user):
        """Test creating a saved meal plan."""
        meal_plan = SavedMealPlan(
            user_id=sample_user.id,
            name="Weekly Plan",
            description="High protein week",
            plan_data='{"meals": [{"day": "Monday", "recipe_id": 1}]}',
            is_template=False
        )
        session.add(meal_plan)
        session.commit()

        assert meal_plan.id is not None
        assert meal_plan.name == "Weekly Plan"
        assert meal_plan.is_template is False
        assert meal_plan.created_at is not None
        assert meal_plan.updated_at is not None

    def test_saved_meal_plan_template(self, session, sample_user):
        """Test creating a meal plan template."""
        template = SavedMealPlan(
            user_id=sample_user.id,
            name="High Protein Template",
            plan_data='{"template": true}',
            is_template=True
        )
        session.add(template)
        session.commit()

        assert template.is_template is True

    def test_saved_meal_plan_relationships(self, session, sample_user):
        """Test relationship between SavedMealPlan and User."""
        plan1 = SavedMealPlan(
            user_id=sample_user.id,
            name="Plan 1",
            plan_data='{}'
        )
        plan2 = SavedMealPlan(
            user_id=sample_user.id,
            name="Plan 2",
            plan_data='{}'
        )
        session.add_all([plan1, plan2])
        session.commit()

        # Access from user
        user_plans = list(sample_user.saved_meal_plans)
        assert len(user_plans) == 2

        # Access from plan
        assert plan1.user.id == sample_user.id

    def test_saved_meal_plan_cascade_delete(self, session, sample_user):
        """Test that meal plans are deleted when user is deleted."""
        plan = SavedMealPlan(
            user_id=sample_user.id,
            name="Test Plan",
            plan_data='{}'
        )
        session.add(plan)
        session.commit()

        user_id = sample_user.id
        session.delete(sample_user)
        session.commit()

        remaining = session.query(SavedMealPlan).filter_by(user_id=user_id).count()
        assert remaining == 0


class TestUserAllergenModel:
    """Tests for UserAllergen model."""

    def test_create_user_allergen(self, session, sample_user, sample_allergen):
        """Test creating a user allergen profile entry."""
        user_allergen = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id,
            severity='severe'
        )
        session.add(user_allergen)
        session.commit()

        assert user_allergen.user_id == sample_user.id
        assert user_allergen.allergen_id == sample_allergen.id
        assert user_allergen.severity == 'severe'
        assert user_allergen.created_at is not None

    def test_user_allergen_default_severity(self, session, sample_user, sample_allergen):
        """Test default severity level."""
        user_allergen = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id
        )
        session.add(user_allergen)
        session.commit()

        assert user_allergen.severity == 'avoid'

    def test_user_allergen_severity_constraint(self, session, sample_user, sample_allergen):
        """Test severity check constraint."""
        invalid_allergen = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id,
            severity='invalid'
        )
        session.add(invalid_allergen)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_user_allergen_relationships(self, session, sample_user, sample_allergen):
        """Test relationships between UserAllergen, User, and Allergen."""
        user_allergen = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id,
            severity='trace_ok'
        )
        session.add(user_allergen)
        session.commit()

        # Access from user
        assert len(sample_user.allergen_profile) == 1
        assert sample_user.allergen_profile[0].severity == 'trace_ok'

        # Access from user_allergen
        assert user_allergen.user.id == sample_user.id
        assert user_allergen.allergen.id == sample_allergen.id

    def test_user_allergen_composite_key(self, session, sample_user, sample_allergen):
        """Test that user-allergen combination is unique."""
        ua1 = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id,
            severity='severe'
        )
        session.add(ua1)
        session.commit()

        # Try to add the same combination again
        ua2 = UserAllergen(
            user_id=sample_user.id,
            allergen_id=sample_allergen.id,
            severity='avoid'
        )
        session.add(ua2)

        with pytest.raises(IntegrityError):
            session.commit()


class TestIngredientPriceModel:
    """Tests for IngredientPrice model."""

    def test_create_ingredient_price(self, session, sample_ingredient, sample_unit):
        """Test creating an ingredient price entry."""
        price = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("5.99"),
            unit_id=sample_unit.id,
            store="Tesco",
            currency="GBP"
        )
        session.add(price)
        session.commit()

        assert price.id is not None
        assert price.price_per_unit == Decimal("5.99")
        assert price.store == "Tesco"
        assert price.currency == "GBP"
        assert price.last_updated is not None

    def test_ingredient_price_defaults(self, session, sample_ingredient):
        """Test default values for ingredient price."""
        price = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("3.50")
        )
        session.add(price)
        session.commit()

        assert price.store == "average"
        assert price.currency == "GBP"

    def test_ingredient_price_relationships(self, session, sample_ingredient, sample_unit):
        """Test relationships between IngredientPrice, Ingredient, and Unit."""
        price = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("4.25"),
            unit_id=sample_unit.id
        )
        session.add(price)
        session.commit()

        # Access from price
        assert price.ingredient.name == sample_ingredient.name
        assert price.unit.abbreviation == sample_unit.abbreviation

    def test_ingredient_price_multiple_stores(self, session, sample_ingredient, sample_unit):
        """Test that we can track prices from multiple stores."""
        price1 = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("5.99"),
            unit_id=sample_unit.id,
            store="Tesco"
        )
        price2 = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("5.49"),
            unit_id=sample_unit.id,
            store="Sainsbury's"
        )
        session.add_all([price1, price2])
        session.commit()

        prices = session.query(IngredientPrice).filter_by(
            ingredient_id=sample_ingredient.id
        ).all()
        assert len(prices) == 2

    def test_ingredient_price_check_constraint(self, session, sample_ingredient):
        """Test that price cannot be negative."""
        invalid_price = IngredientPrice(
            ingredient_id=sample_ingredient.id,
            price_per_unit=Decimal("-1.00")
        )
        session.add(invalid_price)

        with pytest.raises(IntegrityError):
            session.commit()


class TestUserModelIntegration:
    """Integration tests for user models working together."""

    def test_complete_user_profile(self, session):
        """Test creating a complete user profile with all related data."""
        # Create user
        user = User(
            email="complete@test.com",
            username="completeuser",
            password_hash="hash123"
        )
        session.add(user)
        session.commit()

        # Add preferences
        preference = UserPreference(
            user_id=user.id,
            default_servings=4,
            calorie_target=2500,
            protein_target_g=Decimal("180.0")
        )
        session.add(preference)

        # Add recipe and favorite
        recipe = Recipe(
            gousto_id="INT001",
            slug="integration-recipe",
            name="Integration Recipe",
            servings=2,
            source_url="https://test.com"
        )
        session.add(recipe)
        session.commit()

        favorite = FavoriteRecipe(
            user_id=user.id,
            recipe_id=recipe.id,
            notes="Favorite!"
        )
        session.add(favorite)

        # Add meal plan
        meal_plan = SavedMealPlan(
            user_id=user.id,
            name="My Plan",
            plan_data='{}'
        )
        session.add(meal_plan)

        # Add allergen
        allergen = Allergen(name="Shellfish")
        session.add(allergen)
        session.commit()

        user_allergen = UserAllergen(
            user_id=user.id,
            allergen_id=allergen.id,
            severity='severe'
        )
        session.add(user_allergen)
        session.commit()

        # Verify all relationships
        assert user.preferences.default_servings == 4
        assert list(user.favorites)[0].recipe.name == "Integration Recipe"
        assert list(user.saved_meal_plans)[0].name == "My Plan"
        assert user.allergen_profile[0].allergen.name == "Shellfish"

    def test_cascade_delete_complete(self, session):
        """Test that deleting a user cascades to all related tables."""
        # Create user with all related data
        user = User(
            email="cascade@test.com",
            username="cascadeuser",
            password_hash="hash123"
        )
        session.add(user)
        session.commit()

        preference = UserPreference(user_id=user.id)
        session.add(preference)

        recipe = Recipe(
            gousto_id="CAS001",
            slug="cascade-recipe",
            name="Cascade Recipe",
            servings=2,
            source_url="https://test.com"
        )
        session.add(recipe)
        session.commit()

        favorite = FavoriteRecipe(user_id=user.id, recipe_id=recipe.id)
        meal_plan = SavedMealPlan(user_id=user.id, name="Plan", plan_data='{}')

        allergen = Allergen(name="Test Allergen")
        session.add(allergen)
        session.commit()

        user_allergen = UserAllergen(user_id=user.id, allergen_id=allergen.id)

        session.add_all([favorite, meal_plan, user_allergen])
        session.commit()

        user_id = user.id

        # Delete user
        session.delete(user)
        session.commit()

        # Verify all related records are deleted
        assert session.query(UserPreference).filter_by(user_id=user_id).count() == 0
        assert session.query(FavoriteRecipe).filter_by(user_id=user_id).count() == 0
        assert session.query(SavedMealPlan).filter_by(user_id=user_id).count() == 0
        assert session.query(UserAllergen).filter_by(user_id=user_id).count() == 0

        # Recipe should still exist
        assert session.query(Recipe).filter_by(id=recipe.id).count() == 1
