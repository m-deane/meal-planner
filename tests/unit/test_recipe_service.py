"""
Unit tests for RecipeService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from src.api.services.recipe_service import RecipeService
from src.database.models import (
    Recipe, Category, DietaryTag, Allergen, NutritionalInfo,
    RecipeIngredient, Ingredient, Unit, CookingInstruction, Image
)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def recipe_service(mock_db):
    """Create RecipeService instance with mock db."""
    return RecipeService(mock_db)


@pytest.fixture
def sample_recipe():
    """Create sample recipe with relationships."""
    recipe = Recipe(
        id=1,
        gousto_id='test-123',
        slug='test-recipe',
        name='Test Recipe',
        description='A test recipe',
        cooking_time_minutes=30,
        prep_time_minutes=10,
        difficulty='easy',
        servings=2,
        source_url='https://example.com/recipe'
    )

    # Add categories
    recipe.categories = [
        Category(id=1, name='Italian', slug='italian', category_type='cuisine')
    ]

    # Add dietary tags
    recipe.dietary_tags = [
        DietaryTag(id=1, name='Vegetarian', slug='vegetarian')
    ]

    # Add allergens
    recipe.allergens = [
        Allergen(id=1, name='Dairy')
    ]

    # Add nutrition info
    recipe.nutritional_info = NutritionalInfo(
        id=1,
        recipe_id=1,
        calories=Decimal('500'),
        protein_g=Decimal('25'),
        carbohydrates_g=Decimal('50'),
        fat_g=Decimal('20'),
        fiber_g=Decimal('5'),
        sugar_g=Decimal('10')
    )

    # Add ingredients
    ingredient = Ingredient(id=1, name='Tomato', normalized_name='tomato')
    unit = Unit(id=1, name='gram', abbreviation='g', unit_type='weight')
    recipe_ingredient = RecipeIngredient(
        id=1,
        recipe_id=1,
        ingredient_id=1,
        quantity=Decimal('200'),
        unit_id=1,
        display_order=0
    )
    recipe_ingredient.ingredient = ingredient
    recipe_ingredient.unit = unit
    recipe.ingredients_association = [recipe_ingredient]

    # Add instructions
    recipe.cooking_instructions = [
        CookingInstruction(
            id=1,
            recipe_id=1,
            step_number=1,
            instruction='Chop the tomatoes'
        )
    ]

    # Add images
    recipe.images = [
        Image(
            id=1,
            recipe_id=1,
            url='https://example.com/image.jpg',
            image_type='main',
            alt_text='Test recipe image'
        )
    ]

    return recipe


class TestRecipeService:
    """Test RecipeService class."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = RecipeService(mock_db)
        assert service.db == mock_db
        assert service.query is not None

    def test_get_recipe_by_id_success(self, recipe_service, sample_recipe):
        """Test getting recipe by ID successfully."""
        recipe_service.query.get_by_id = Mock(return_value=sample_recipe)

        result = recipe_service.get_recipe_by_id(1)

        assert result is not None
        assert result['id'] == 1
        assert result['name'] == 'Test Recipe'
        assert result['slug'] == 'test-recipe'
        assert result['cooking_time_minutes'] == 30
        assert result['total_time_minutes'] == 40
        assert len(result['categories']) == 1
        assert len(result['dietary_tags']) == 1
        assert len(result['allergens']) == 1
        assert len(result['ingredients']) == 1
        assert len(result['instructions']) == 1
        assert result['nutrition'] is not None

    def test_get_recipe_by_id_not_found(self, recipe_service):
        """Test getting non-existent recipe."""
        recipe_service.query.get_by_id = Mock(return_value=None)

        result = recipe_service.get_recipe_by_id(999)

        assert result is None

    def test_get_recipe_by_slug_success(self, recipe_service, sample_recipe):
        """Test getting recipe by slug."""
        recipe_service.query.get_by_slug = Mock(return_value=sample_recipe)

        result = recipe_service.get_recipe_by_slug('test-recipe')

        assert result is not None
        assert result['slug'] == 'test-recipe'

    def test_search_recipes(self, recipe_service, sample_recipe):
        """Test recipe search."""
        recipe_service.query.search_by_name = Mock(return_value=[sample_recipe])

        result = recipe_service.search_recipes('test', limit=10)

        assert result is not None
        assert result['query'] == 'test'
        assert result['count'] == 1
        assert len(result['recipes']) == 1
        assert result['recipes'][0]['name'] == 'Test Recipe'

    def test_get_recipe_nutrition_success(self, recipe_service, sample_recipe):
        """Test getting recipe nutrition."""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = sample_recipe.nutritional_info
        recipe_service.db.query = Mock(return_value=mock_query)

        result = recipe_service.get_recipe_nutrition(1)

        assert result is not None
        assert result['calories'] == 500.0
        assert result['protein_g'] == 25.0
        assert result['carbohydrates_g'] == 50.0
        assert result['fat_g'] == 20.0

    def test_get_recipe_nutrition_not_found(self, recipe_service):
        """Test getting nutrition for recipe without nutrition data."""
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        recipe_service.db.query = Mock(return_value=mock_query)

        result = recipe_service.get_recipe_nutrition(999)

        assert result is None

    def test_get_recipe_ingredients_success(self, recipe_service, sample_recipe):
        """Test getting recipe ingredients."""
        recipe_service.query.get_by_id = Mock(return_value=sample_recipe)

        result = recipe_service.get_recipe_ingredients(1)

        assert result is not None
        assert len(result) == 1
        assert result[0]['name'] == 'Tomato'
        assert result[0]['quantity'] == 200.0
        assert result[0]['unit'] == 'g'

    def test_get_recipe_ingredients_not_found(self, recipe_service):
        """Test getting ingredients for non-existent recipe."""
        recipe_service.query.get_by_id = Mock(return_value=None)

        result = recipe_service.get_recipe_ingredients(999)

        assert result is None

    def test_get_recipes_with_filters(self, recipe_service, sample_recipe):
        """Test getting recipes with filters and pagination."""
        recipe_service.query.filter_recipes = Mock(return_value=[sample_recipe])
        recipe_service.query.get_recipe_count = Mock(return_value=1)

        result = recipe_service.get_recipes(
            categories=['italian'],
            max_cooking_time=60,
            limit=20,
            offset=0
        )

        assert result is not None
        assert result['total'] == 1
        assert result['limit'] == 20
        assert result['offset'] == 0
        assert len(result['recipes']) == 1
        assert result['has_more'] is False

    def test_get_quick_recipes(self, recipe_service, sample_recipe):
        """Test getting quick recipes."""
        recipe_service.query.get_quick_recipes = Mock(return_value=[sample_recipe])

        result = recipe_service.get_quick_recipes(max_time=30, limit=10)

        assert result is not None
        assert len(result) == 1
        assert result[0]['cooking_time_minutes'] == 30

    def test_get_high_protein_recipes(self, recipe_service, sample_recipe):
        """Test getting high protein recipes."""
        recipe_service.query.get_high_protein_recipes = Mock(return_value=[sample_recipe])

        result = recipe_service.get_high_protein_recipes(min_protein=20.0)

        assert result is not None
        assert len(result) == 1

    def test_get_low_carb_recipes(self, recipe_service, sample_recipe):
        """Test getting low carb recipes."""
        recipe_service.query.get_low_carb_recipes = Mock(return_value=[sample_recipe])

        result = recipe_service.get_low_carb_recipes(max_carbs=30.0)

        assert result is not None
        assert len(result) == 1

    def test_serialize_recipe_summary(self, recipe_service, sample_recipe):
        """Test recipe summary serialization."""
        result = recipe_service._serialize_recipe_summary(sample_recipe)

        assert result['id'] == 1
        assert result['name'] == 'Test Recipe'
        assert result['slug'] == 'test-recipe'
        assert result['difficulty'] == 'easy'
        assert 'categories' in result
        assert 'dietary_tags' in result
        assert 'image' in result
        assert 'nutrition_summary' in result

    def test_serialize_recipe_full(self, recipe_service, sample_recipe):
        """Test full recipe serialization."""
        result = recipe_service._serialize_recipe_full(sample_recipe)

        assert result['id'] == 1
        assert result['gousto_id'] == 'test-123'
        assert 'ingredients' in result
        assert 'instructions' in result
        assert 'nutrition' in result
        assert 'allergens' in result
        assert len(result['ingredients']) == 1
        assert len(result['instructions']) == 1

    def test_serialize_nutrition(self, recipe_service, sample_recipe):
        """Test nutrition serialization."""
        result = recipe_service._serialize_nutrition(sample_recipe.nutritional_info)

        assert result['calories'] == 500.0
        assert result['protein_g'] == 25.0
        assert result['carbohydrates_g'] == 50.0
        assert result['fat_g'] == 20.0
        assert result['fiber_g'] == 5.0
        assert result['sugar_g'] == 10.0
        assert 'macros_ratio' in result

    def test_get_nutrition_summary(self, recipe_service, sample_recipe):
        """Test nutrition summary extraction."""
        result = recipe_service._get_nutrition_summary(sample_recipe)

        assert result is not None
        assert result['calories'] == 500.0
        assert result['protein_g'] == 25.0
        assert len(result) == 4  # Only key values

    def test_get_nutrition_summary_no_nutrition(self, recipe_service):
        """Test nutrition summary for recipe without nutrition."""
        recipe = Recipe(id=1, name='Test')
        recipe.nutritional_info = None

        result = recipe_service._get_nutrition_summary(recipe)

        assert result is None
