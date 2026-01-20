"""
Unit tests for Pydantic schemas.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from pydantic import ValidationError

from src.api.schemas import (
    # Common
    ErrorResponse,
    SuccessResponse,
    MessageResponse,

    # Pagination
    PaginationParams,
    SortParams,
    SortOrder,
    PaginatedResponse,

    # Recipe
    DifficultyLevel,
    IngredientResponse,
    InstructionResponse,
    NutritionResponse,
    RecipeBase,
    RecipeListItem,
    RecipeResponse,
    RecipeFilters,
    NutritionFilters,

    # Meal Plan
    MealType,
    NutritionConstraints,
    MealPreferences,
    MealPlanGenerateRequest,
    MealSlot,
    DayPlan,

    # Shopping List
    ShoppingListGenerateRequest,
    ShoppingItem,
    ShoppingCategory,
    IngredientCategory,

    # Auth
    LoginRequest,
    UserCreate,
    TokenResponse,
    PasswordChangeRequest,
)


# ============================================================================
# COMMON SCHEMA TESTS
# ============================================================================

class TestCommonSchemas:
    """Test common response schemas."""

    def test_error_response_valid(self):
        """Test valid error response."""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input",
            details={"field": "email"},
            path="/api/v1/users"
        )
        assert error.error == "ValidationError"
        assert error.message == "Invalid input"
        assert error.details["field"] == "email"

    def test_success_response_valid(self):
        """Test valid success response."""
        success = SuccessResponse(
            message="Operation completed",
            data={"id": 123}
        )
        assert success.success is True
        assert success.message == "Operation completed"
        assert success.data["id"] == 123

    def test_message_response_valid(self):
        """Test valid message response."""
        msg = MessageResponse(message="Hello")
        assert msg.message == "Hello"


# ============================================================================
# PAGINATION SCHEMA TESTS
# ============================================================================

class TestPaginationSchemas:
    """Test pagination and sorting schemas."""

    def test_pagination_params_valid(self):
        """Test valid pagination parameters."""
        params = PaginationParams(page=2, page_size=50)
        assert params.page == 2
        assert params.page_size == 50
        assert params.offset == 50
        assert params.limit == 50

    def test_pagination_params_defaults(self):
        """Test pagination parameter defaults."""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_pagination_params_invalid_page(self):
        """Test invalid page number."""
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(page=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_pagination_params_max_page_size(self):
        """Test page size validation (max 100)."""
        params = PaginationParams(page=1, page_size=150)
        assert params.page_size == 100  # Should be clamped to 100

    def test_sort_params_valid(self):
        """Test valid sort parameters."""
        sort = SortParams(sort_by="name", sort_order=SortOrder.DESC)
        assert sort.sort_by == "name"
        assert sort.sort_order == SortOrder.DESC

    def test_paginated_response_factory(self):
        """Test paginated response factory method."""
        items = [1, 2, 3, 4, 5]
        response = PaginatedResponse[int].create(
            items=items,
            total=23,
            page=2,
            page_size=5
        )
        assert response.items == items
        assert response.total == 23
        assert response.page == 2
        assert response.page_size == 5
        assert response.total_pages == 5
        assert response.has_next is True
        assert response.has_previous is True


# ============================================================================
# RECIPE SCHEMA TESTS
# ============================================================================

class TestRecipeSchemas:
    """Test recipe-related schemas."""

    def test_ingredient_response_valid(self):
        """Test valid ingredient response."""
        ingredient = IngredientResponse(
            name="Chicken Breast",
            quantity=Decimal("300"),
            unit="g",
            unit_name="grams",
            preparation_note="diced",
            is_optional=False,
            category="protein",
            display_order=1
        )
        assert ingredient.name == "Chicken Breast"
        assert ingredient.quantity == Decimal("300")
        assert ingredient.unit == "g"

    def test_instruction_response_valid(self):
        """Test valid instruction response."""
        instruction = InstructionResponse(
            step_number=1,
            instruction="Preheat oven to 200°C",
            time_minutes=10
        )
        assert instruction.step_number == 1
        assert instruction.time_minutes == 10

    def test_instruction_invalid_step_number(self):
        """Test instruction with invalid step number."""
        with pytest.raises(ValidationError) as exc_info:
            InstructionResponse(
                step_number=0,
                instruction="Invalid step"
            )
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_nutrition_response_valid(self):
        """Test valid nutrition response."""
        nutrition = NutritionResponse(
            calories=Decimal("450"),
            protein_g=Decimal("35"),
            carbohydrates_g=Decimal("40"),
            fat_g=Decimal("15"),
            fiber_g=Decimal("8"),
            sugar_g=Decimal("6"),
            sodium_mg=Decimal("600")
        )
        assert nutrition.calories == Decimal("450")
        assert nutrition.protein_g == Decimal("35")
        assert nutrition.carbs_g == Decimal("40")  # Test alias

    def test_nutrition_response_negative_values(self):
        """Test nutrition response rejects negative values."""
        with pytest.raises(ValidationError) as exc_info:
            NutritionResponse(
                calories=Decimal("-100"),
                protein_g=Decimal("35")
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_recipe_base_valid(self):
        """Test valid recipe base."""
        recipe = RecipeBase(
            name="Spaghetti Carbonara",
            description="Classic Italian pasta",
            cooking_time_minutes=20,
            prep_time_minutes=10,
            difficulty=DifficultyLevel.MEDIUM,
            servings=2
        )
        assert recipe.name == "Spaghetti Carbonara"
        assert recipe.difficulty == DifficultyLevel.MEDIUM

    def test_recipe_base_invalid_servings(self):
        """Test recipe with invalid servings."""
        with pytest.raises(ValidationError) as exc_info:
            RecipeBase(
                name="Test Recipe",
                servings=0
            )
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_nutrition_filters_valid(self):
        """Test valid nutrition filters."""
        filters = NutritionFilters(
            min_calories=300,
            max_calories=600,
            min_protein_g=Decimal("20"),
            max_carbs_g=Decimal("50")
        )
        assert filters.min_calories == 300
        assert filters.max_calories == 600

    def test_nutrition_filters_invalid_range(self):
        """Test nutrition filters with invalid range."""
        with pytest.raises(ValidationError) as exc_info:
            NutritionFilters(
                min_calories=600,
                max_calories=300
            )
        assert "max_calories must be greater than or equal to min_calories" in str(exc_info.value)

    def test_recipe_filters_valid(self):
        """Test valid recipe filters."""
        filters = RecipeFilters(
            category_slugs=["italian", "pasta"],
            dietary_tag_slugs=["vegetarian"],
            exclude_allergen_names=["nuts"],
            max_total_time=45,
            difficulty=[DifficultyLevel.EASY, DifficultyLevel.MEDIUM],
            search_query="carbonara"
        )
        assert "italian" in filters.category_slugs
        assert filters.max_total_time == 45


# ============================================================================
# MEAL PLAN SCHEMA TESTS
# ============================================================================

class TestMealPlanSchemas:
    """Test meal planning schemas."""

    def test_nutrition_constraints_valid(self):
        """Test valid nutrition constraints."""
        constraints = NutritionConstraints(
            target_calories=2000,
            min_protein_g=Decimal("100"),
            max_carbs_g=Decimal("250"),
            max_sugar_g=Decimal("50")
        )
        assert constraints.target_calories == 2000
        assert constraints.min_protein_g == Decimal("100")

    def test_nutrition_constraints_invalid_range(self):
        """Test nutrition constraints with invalid range."""
        with pytest.raises(ValidationError) as exc_info:
            NutritionConstraints(
                min_calories=2500,
                max_calories=2000
            )
        assert "max_calories must be greater than or equal to min_calories" in str(exc_info.value)

    def test_meal_preferences_valid(self):
        """Test valid meal preferences."""
        prefs = MealPreferences(
            include_breakfast=True,
            include_lunch=True,
            include_dinner=True,
            breakfast_calories_pct=25,
            lunch_calories_pct=35,
            dinner_calories_pct=40
        )
        assert prefs.include_breakfast is True
        assert prefs.breakfast_calories_pct == 25

    def test_meal_plan_generate_request_valid(self):
        """Test valid meal plan generation request."""
        request = MealPlanGenerateRequest(
            days=7,
            start_date=date(2026, 1, 20),
            meal_preferences=MealPreferences(),
            dietary_tag_slugs=["vegetarian"],
            exclude_allergen_names=["nuts"],
            max_cooking_time=45,
            avoid_duplicate_recipes=True
        )
        assert request.days == 7
        assert request.start_date == date(2026, 1, 20)
        assert "vegetarian" in request.dietary_tag_slugs

    def test_meal_plan_generate_request_invalid_days(self):
        """Test meal plan request with invalid days."""
        with pytest.raises(ValidationError) as exc_info:
            MealPlanGenerateRequest(days=0)
        assert "greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            MealPlanGenerateRequest(days=31)
        assert "less than or equal to 30" in str(exc_info.value)


# ============================================================================
# SHOPPING LIST SCHEMA TESTS
# ============================================================================

class TestShoppingListSchemas:
    """Test shopping list schemas."""

    def test_shopping_list_generate_request_with_recipes(self):
        """Test shopping list request with recipe IDs."""
        request = ShoppingListGenerateRequest(
            recipe_ids=[1, 2, 3],
            servings_multiplier=1.5,
            group_by_category=True,
            combine_similar_ingredients=True
        )
        assert request.recipe_ids == [1, 2, 3]
        assert request.servings_multiplier == 1.5

    def test_shopping_list_generate_request_with_meal_plan(self):
        """Test shopping list request with meal plan ID."""
        request = ShoppingListGenerateRequest(
            meal_plan_id=5,
            group_by_category=True
        )
        assert request.meal_plan_id == 5

    def test_shopping_item_valid(self):
        """Test valid shopping item."""
        item = ShoppingItem(
            ingredient_name="Chicken Breast",
            quantity=Decimal("1.2"),
            unit="kg",
            category=IngredientCategory.PROTEIN,
            is_optional=False,
            recipe_count=3
        )
        assert item.ingredient_name == "Chicken Breast"
        assert item.category == IngredientCategory.PROTEIN
        assert item.display_quantity == "1.2 kg"

    def test_shopping_category_valid(self):
        """Test valid shopping category."""
        items = [
            ShoppingItem(
                ingredient_name="Chicken",
                quantity=Decimal("1"),
                unit="kg",
                category=IngredientCategory.PROTEIN,
                recipe_count=1
            )
        ]
        category = ShoppingCategory(
            name=IngredientCategory.PROTEIN,
            display_name="Protein",
            items=items,
            item_count=1
        )
        assert category.name == IngredientCategory.PROTEIN
        assert category.item_count == 1


# ============================================================================
# AUTH SCHEMA TESTS
# ============================================================================

class TestAuthSchemas:
    """Test authentication schemas."""

    def test_login_request_valid(self):
        """Test valid login request."""
        login = LoginRequest(
            username="john.doe@example.com",
            password="SecureP@ssw0rd"
        )
        assert login.username == "john.doe@example.com"

    def test_login_request_invalid_short_username(self):
        """Test login with too short username."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="ab", password="SecureP@ssw0rd")
        assert "at least 3 characters" in str(exc_info.value)

    def test_login_request_invalid_short_password(self):
        """Test login with too short password."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="john.doe", password="short")
        assert "at least 8 characters" in str(exc_info.value)

    def test_user_create_valid(self):
        """Test valid user creation."""
        user = UserCreate(
            username="john_doe",
            email="john.doe@example.com",
            password="SecureP@ssw0rd123",
            full_name="John Doe"
        )
        assert user.username == "john_doe"
        assert user.email == "john.doe@example.com"

    def test_user_create_invalid_username(self):
        """Test user creation with invalid username."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john doe",  # spaces not allowed
                email="john@example.com",
                password="SecureP@ssw0rd123"
            )
        assert "alphanumeric" in str(exc_info.value)

    def test_user_create_weak_password(self):
        """Test user creation with weak password."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="john@example.com",
                password="password"  # no uppercase or numbers
            )
        assert "uppercase" in str(exc_info.value) or "number" in str(exc_info.value)

    def test_user_create_invalid_email(self):
        """Test user creation with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="invalid-email",
                password="SecureP@ssw0rd123"
            )
        assert "email" in str(exc_info.value).lower()

    def test_password_change_request_valid(self):
        """Test valid password change request."""
        request = PasswordChangeRequest(
            current_password="OldP@ssw0rd123",
            new_password="NewSecureP@ssw0rd456"
        )
        assert request.current_password == "OldP@ssw0rd123"
        assert request.new_password == "NewSecureP@ssw0rd456"

    def test_password_change_request_weak_new_password(self):
        """Test password change with weak new password."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeRequest(
                current_password="OldP@ssw0rd123",
                new_password="weakpassword"  # Long enough but no uppercase or number
            )
        assert "uppercase" in str(exc_info.value).lower() or "number" in str(exc_info.value).lower()

    def test_token_response_valid(self):
        """Test valid token response."""
        token = TokenResponse(
            access_token="abc123",
            token_type="bearer",
            expires_in=3600,
            refresh_token="def456"
        )
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"
        assert token.expires_in == 3600


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSchemaIntegration:
    """Test schema integration and edge cases."""

    def test_recipe_list_item_serialization(self):
        """Test recipe list item can be serialized to dict."""
        from src.api.schemas import RecipeListItem

        recipe = RecipeListItem(
            id=1,
            slug="test-recipe",
            name="Test Recipe",
            cooking_time_minutes=20,
            servings=2,
            categories=[],
            dietary_tags=[],
            allergens=[],
            is_active=True
        )
        data = recipe.model_dump()
        assert data["id"] == 1
        assert data["name"] == "Test Recipe"

    def test_paginated_response_with_recipe_items(self):
        """Test paginated response with recipe items."""
        from src.api.schemas import RecipeListItem, PaginatedResponse

        recipes = [
            RecipeListItem(
                id=i,
                slug=f"recipe-{i}",
                name=f"Recipe {i}",
                servings=2,
                categories=[],
                dietary_tags=[],
                allergens=[],
                is_active=True
            )
            for i in range(1, 6)
        ]

        response = PaginatedResponse[RecipeListItem].create(
            items=recipes,
            total=25,
            page=1,
            page_size=5
        )

        assert len(response.items) == 5
        assert response.total_pages == 5
        assert response.has_next is True
        assert response.has_previous is False

    def test_meal_plan_response_complex(self):
        """Test complex meal plan response structure."""
        from src.api.schemas import (
            MealPlanResponse,
            DayPlan,
            MealSlot,
            RecipeListItem,
            MealPlanSummary,
            MealType
        )

        recipe = RecipeListItem(
            id=1,
            slug="test-recipe",
            name="Test Recipe",
            servings=2,
            categories=[],
            dietary_tags=[],
            allergens=[],
            is_active=True
        )

        meal_slot = MealSlot(
            meal_type=MealType.DINNER,
            recipe=recipe,
            servings=2
        )

        day_plan = DayPlan(
            day=1,
            date=date(2026, 1, 20),
            meals=[meal_slot]
        )

        summary = MealPlanSummary(
            total_recipes=7,
            unique_recipes=7,
            total_meals=21,
            difficulty_distribution={"easy": 5, "medium": 2}
        )

        meal_plan = MealPlanResponse(
            days=[day_plan],
            total_days=7,
            summary=summary
        )

        assert len(meal_plan.days) == 1
        assert meal_plan.total_days == 7
        assert meal_plan.summary.total_recipes == 7
