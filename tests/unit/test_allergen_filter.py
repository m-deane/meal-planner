"""
Unit tests for AllergenFilter.
Tests allergen filtering and warning functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock

from src.meal_planner.allergen_filter import AllergenFilter, AllergenWarning
from src.database.models import Recipe, Allergen, UserAllergen, RecipeIngredient, Ingredient


class TestAllergenFilter:
    """Test suite for AllergenFilter."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def peanut_allergen(self):
        """Create peanut allergen."""
        allergen = Mock(spec=Allergen)
        allergen.id = 1
        allergen.name = "Peanuts"
        return allergen

    @pytest.fixture
    def dairy_allergen(self):
        """Create dairy allergen."""
        allergen = Mock(spec=Allergen)
        allergen.id = 2
        allergen.name = "Dairy"
        return allergen

    @pytest.fixture
    def user_allergen_severe(self, peanut_allergen):
        """Create user allergen with severe severity."""
        ua = Mock(spec=UserAllergen)
        ua.user_id = 1
        ua.allergen_id = 1
        ua.allergen = peanut_allergen
        ua.severity = "severe"
        return ua

    @pytest.fixture
    def user_allergen_trace_ok(self, dairy_allergen):
        """Create user allergen with trace_ok severity."""
        ua = Mock(spec=UserAllergen)
        ua.user_id = 1
        ua.allergen_id = 2
        ua.allergen = dairy_allergen
        ua.severity = "trace_ok"
        return ua

    @pytest.fixture
    def recipe_with_peanuts(self, peanut_allergen):
        """Create recipe containing peanuts."""
        recipe = Mock(spec=Recipe)
        recipe.id = 1
        recipe.name = "Peanut Butter Cookies"
        recipe.allergens = [peanut_allergen]

        ingredient = Mock(spec=Ingredient)
        ingredient.id = 1
        ingredient.name = "Peanut Butter"

        recipe_ingredient = Mock(spec=RecipeIngredient)
        recipe_ingredient.ingredient = ingredient

        recipe.ingredients_association = [recipe_ingredient]
        return recipe

    @pytest.fixture
    def safe_recipe(self):
        """Create recipe without allergens."""
        recipe = Mock(spec=Recipe)
        recipe.id = 2
        recipe.name = "Vegetable Stir Fry"
        recipe.allergens = []
        recipe.ingredients_association = []
        return recipe

    def test_filter_recipes_empty_allergens(self, mock_session):
        """Test filtering with no user allergens."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])
        recipes = [Mock(spec=Recipe), Mock(spec=Recipe)]

        # Execute
        result = allergen_filter.filter_recipes(recipes)

        # Assert
        assert len(result) == 2

    def test_filter_recipes_severe_allergen(self, mock_session, user_allergen_severe, recipe_with_peanuts, safe_recipe):
        """Test filtering removes recipes with severe allergen."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])
        recipes = [recipe_with_peanuts, safe_recipe]

        # Execute
        result = allergen_filter.filter_recipes(recipes)

        # Assert
        assert len(result) == 1
        assert result[0].name == "Vegetable Stir Fry"

    def test_filter_recipes_trace_ok_allergen(self, mock_session, user_allergen_trace_ok, safe_recipe):
        """Test filtering allows recipes with trace_ok allergen."""
        # Setup
        dairy_recipe = Mock(spec=Recipe)
        dairy_recipe.id = 3
        dairy_recipe.name = "Cheese Pizza"
        dairy_recipe.allergens = [user_allergen_trace_ok.allergen]

        allergen_filter = AllergenFilter(mock_session, [user_allergen_trace_ok])
        recipes = [dairy_recipe, safe_recipe]

        # Execute
        result = allergen_filter.filter_recipes(recipes)

        # Assert - trace_ok should allow the recipe through
        assert len(result) == 2

    def test_is_recipe_safe_with_severe_allergen(self, mock_session, user_allergen_severe, recipe_with_peanuts):
        """Test recipe safety check with severe allergen."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Execute
        is_safe = allergen_filter._is_recipe_safe(recipe_with_peanuts)

        # Assert
        assert is_safe is False

    def test_is_recipe_safe_without_allergens(self, mock_session, user_allergen_severe, safe_recipe):
        """Test recipe safety check for safe recipe."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Execute
        is_safe = allergen_filter._is_recipe_safe(safe_recipe)

        # Assert
        assert is_safe is True

    def test_get_warnings_severe_allergen(self, mock_session, user_allergen_severe, recipe_with_peanuts):
        """Test getting warnings for recipe with severe allergen."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Execute
        warnings = allergen_filter.get_warnings(recipe_with_peanuts)

        # Assert
        assert len(warnings) == 1
        assert warnings[0].allergen_name == "Peanuts"
        assert warnings[0].severity == "severe"
        assert "SEVERE ALLERGY" in warnings[0].message

    def test_get_warnings_avoid_allergen(self, mock_session, peanut_allergen, recipe_with_peanuts):
        """Test getting warnings for recipe with avoid allergen."""
        # Setup
        user_allergen = Mock(spec=UserAllergen)
        user_allergen.allergen_id = 1
        user_allergen.allergen = peanut_allergen
        user_allergen.severity = "avoid"

        allergen_filter = AllergenFilter(mock_session, [user_allergen])

        # Execute
        warnings = allergen_filter.get_warnings(recipe_with_peanuts)

        # Assert
        assert len(warnings) == 1
        assert "WARNING" in warnings[0].message

    def test_get_warnings_trace_ok_allergen(self, mock_session, peanut_allergen, recipe_with_peanuts):
        """Test getting warnings for recipe with trace_ok allergen."""
        # Setup
        user_allergen = Mock(spec=UserAllergen)
        user_allergen.allergen_id = 1
        user_allergen.allergen = peanut_allergen
        user_allergen.severity = "trace_ok"

        allergen_filter = AllergenFilter(mock_session, [user_allergen])

        # Execute
        warnings = allergen_filter.get_warnings(recipe_with_peanuts)

        # Assert
        assert len(warnings) == 1
        assert "INFO" in warnings[0].message
        assert "trace amounts" in warnings[0].message

    def test_get_warnings_no_allergens(self, mock_session, user_allergen_severe, safe_recipe):
        """Test getting warnings for safe recipe."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Execute
        warnings = allergen_filter.get_warnings(safe_recipe)

        # Assert
        assert len(warnings) == 0

    def test_find_allergen_ingredients(self, mock_session, peanut_allergen, recipe_with_peanuts):
        """Test finding ingredients containing allergen."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])

        # Execute
        ingredients = allergen_filter._find_allergen_ingredients(recipe_with_peanuts, peanut_allergen)

        # Assert
        assert len(ingredients) > 0
        assert "Peanut Butter" in ingredients

    def test_is_related_ingredient_dairy(self, mock_session):
        """Test ingredient relation checking for dairy."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])

        # Execute & Assert
        assert allergen_filter._is_related_ingredient("dairy", "milk")
        assert allergen_filter._is_related_ingredient("dairy", "cheese")
        assert allergen_filter._is_related_ingredient("dairy", "yogurt")
        assert not allergen_filter._is_related_ingredient("dairy", "chicken")

    def test_is_related_ingredient_gluten(self, mock_session):
        """Test ingredient relation checking for gluten."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])

        # Execute & Assert
        assert allergen_filter._is_related_ingredient("gluten", "wheat flour")
        assert allergen_filter._is_related_ingredient("gluten", "bread")
        assert not allergen_filter._is_related_ingredient("gluten", "rice")

    def test_suggest_substitutions_peanuts(self, mock_session, peanut_allergen, recipe_with_peanuts):
        """Test suggesting substitutions for peanuts."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])

        # Execute
        substitutions = allergen_filter.suggest_substitutions(recipe_with_peanuts, peanut_allergen)

        # Assert
        assert len(substitutions) > 0
        assert substitutions[0]['original_ingredient'] == "Peanut Butter"
        assert "sunflower seed butter" in substitutions[0]['substitutes']
        assert "almond butter" in substitutions[0]['substitutes']

    def test_suggest_substitutions_no_match(self, mock_session, safe_recipe):
        """Test suggesting substitutions when no allergen found."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [])
        allergen = Mock(spec=Allergen)
        allergen.id = 99
        allergen.name = "Unknown"

        # Execute
        substitutions = allergen_filter.suggest_substitutions(safe_recipe, allergen)

        # Assert
        assert len(substitutions) == 0

    def test_get_safe_recipes_excludes_allergens(self, mock_session, user_allergen_severe):
        """Test getting safe recipes excludes user's allergens."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Mock the query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Execute
        recipes = allergen_filter.get_safe_recipes(
            user_id=1,
            limit=10,
            offset=0
        )

        # Assert
        assert isinstance(recipes, list)
        mock_session.query.assert_called()

    def test_get_safe_recipes_with_filters(self, mock_session, user_allergen_severe):
        """Test getting safe recipes with additional filters."""
        # Setup
        allergen_filter = AllergenFilter(mock_session, [user_allergen_severe])

        # Mock the query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Execute
        recipes = allergen_filter.get_safe_recipes(
            user_id=1,
            max_cooking_time=30,
            difficulty="easy",
            min_protein=20.0,
            limit=10,
            offset=0
        )

        # Assert
        assert isinstance(recipes, list)
