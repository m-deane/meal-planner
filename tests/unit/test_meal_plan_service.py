"""
Unit tests for MealPlanService.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from src.api.services.meal_plan_service import MealPlanService
from src.database.models import Recipe, NutritionalInfo


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def meal_plan_service(mock_db):
    """Create MealPlanService instance."""
    return MealPlanService(mock_db)


@pytest.fixture
def sample_recipe_with_nutrition():
    """Create sample recipe with nutrition."""
    recipe = Recipe(
        id=1,
        gousto_id='test-1',
        slug='test-recipe-1',
        name='Chicken Salad',
        cooking_time_minutes=20,
        servings=2,
        source_url='https://example.com/1',
        difficulty='easy'
    )

    recipe.nutritional_info = NutritionalInfo(
        recipe_id=1,
        calories=Decimal('400'),
        protein_g=Decimal('30'),
        carbohydrates_g=Decimal('20'),
        fat_g=Decimal('15'),
        fiber_g=Decimal('5'),
        sugar_g=Decimal('3')
    )

    recipe.images = []
    return recipe


@pytest.fixture
def sample_meal_plan(sample_recipe_with_nutrition):
    """Create sample meal plan."""
    return {
        'Monday': {
            'breakfast': sample_recipe_with_nutrition,
            'lunch': sample_recipe_with_nutrition,
            'dinner': sample_recipe_with_nutrition
        },
        'Tuesday': {
            'breakfast': sample_recipe_with_nutrition,
            'lunch': sample_recipe_with_nutrition,
            'dinner': sample_recipe_with_nutrition
        }
    }


class TestMealPlanService:
    """Test MealPlanService class."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = MealPlanService(mock_db)
        assert service.db == mock_db
        assert service.planner is not None
        assert service.nutrition_planner is not None

    def test_generate_meal_plan_basic(self, meal_plan_service, sample_meal_plan):
        """Test basic meal plan generation."""
        meal_plan_service.planner.generate_weekly_meal_plan = Mock(
            return_value=sample_meal_plan
        )

        result = meal_plan_service.generate_meal_plan(
            min_protein_score=40.0,
            max_carb_score=40.0
        )

        assert result is not None
        assert 'plan' in result
        assert 'metadata' in result
        assert result['metadata']['total_days'] == 2
        assert result['metadata']['total_meals'] == 6

    def test_generate_meal_plan_with_nutrition(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test meal plan generation with nutrition data."""
        meal_plan_service.nutrition_planner.generate_weekly_meal_plan = Mock(
            return_value=sample_meal_plan
        )

        result = meal_plan_service.generate_meal_plan(
            min_protein_score=40.0,
            max_carb_score=30.0,
            use_nutrition_data=True
        )

        assert result is not None
        assert result['metadata']['uses_nutrition_data'] is True

    def test_generate_nutrition_meal_plan(
        self,
        meal_plan_service,
        sample_meal_plan,
        sample_recipe_with_nutrition
    ):
        """Test nutrition-based meal plan generation."""
        meal_plan_service.nutrition_planner.filter_by_actual_nutrition = Mock(
            return_value=[(sample_recipe_with_nutrition, {})]
        )
        meal_plan_service.nutrition_planner.generate_weekly_meal_plan = Mock(
            return_value=sample_meal_plan
        )

        result = meal_plan_service.generate_nutrition_meal_plan(
            min_protein_g=25.0,
            max_carbs_g=30.0
        )

        assert result is not None
        assert 'plan' in result
        assert 'weekly_totals' in result

    def test_format_meal_plan_response_without_nutrition(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test meal plan formatting without nutrition data."""
        result = meal_plan_service.format_meal_plan_response(
            sample_meal_plan,
            use_nutrition_data=False
        )

        assert result is not None
        assert 'plan' in result
        assert 'metadata' in result
        assert result['weekly_totals'] is None
        assert result['weekly_averages'] is None

    def test_format_meal_plan_response_with_nutrition(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test meal plan formatting with nutrition data."""
        result = meal_plan_service.format_meal_plan_response(
            sample_meal_plan,
            use_nutrition_data=True
        )

        assert result is not None
        assert result['weekly_totals'] is not None
        assert result['weekly_averages'] is not None
        assert 'calories' in result['weekly_totals']
        assert 'protein_g' in result['weekly_totals']

        # Check daily totals in each day
        for day, day_data in result['plan'].items():
            assert 'daily_totals' in day_data
            assert day_data['daily_totals']['calories'] > 0

    def test_format_meal_plan_response_calculates_macros(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test macro percentage calculations."""
        result = meal_plan_service.format_meal_plan_response(
            sample_meal_plan,
            use_nutrition_data=True
        )

        averages = result['weekly_averages']
        assert 'protein_pct' in averages
        assert 'carbs_pct' in averages
        assert 'fat_pct' in averages

        # Verify percentages are reasonable (may not add to 100% due to fiber, alcohol, etc.)
        assert 0 <= averages['protein_pct'] <= 100
        assert 0 <= averages['carbs_pct'] <= 100
        assert 0 <= averages['fat_pct'] <= 100

        # Total should be less than or equal to 100%
        total_pct = (
            averages['protein_pct'] +
            averages['carbs_pct'] +
            averages['fat_pct']
        )
        assert 0 <= total_pct <= 100

    def test_get_recipe_ids_from_plan(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test extracting recipe IDs from meal plan."""
        result = meal_plan_service.get_recipe_ids_from_plan(sample_meal_plan)

        assert result is not None
        assert isinstance(result, list)
        # All recipes in fixture have same ID, so should have 1 unique
        assert len(result) == 1
        assert 1 in result

    def test_get_recipe_ids_from_plan_unique(self, meal_plan_service):
        """Test recipe ID extraction with multiple unique recipes."""
        recipe1 = Recipe(id=1, slug='r1', name='R1', source_url='url1', servings=2)
        recipe2 = Recipe(id=2, slug='r2', name='R2', source_url='url2', servings=2)
        recipe3 = Recipe(id=3, slug='r3', name='R3', source_url='url3', servings=2)

        recipe1.images = []
        recipe2.images = []
        recipe3.images = []
        recipe1.nutritional_info = None
        recipe2.nutritional_info = None
        recipe3.nutritional_info = None

        meal_plan = {
            'Monday': {
                'breakfast': recipe1,
                'lunch': recipe2,
                'dinner': recipe3
            },
            'Tuesday': {
                'breakfast': recipe1,  # Duplicate
                'lunch': recipe2,  # Duplicate
                'dinner': recipe3  # Duplicate
            }
        }

        result = meal_plan_service.get_recipe_ids_from_plan(meal_plan)

        assert len(result) == 3
        assert set(result) == {1, 2, 3}

    def test_get_meal_plan_text_format_basic(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test text format generation."""
        meal_plan_service.planner.format_meal_plan = Mock(
            return_value="Meal Plan Text"
        )

        result = meal_plan_service.get_meal_plan_text_format(
            sample_meal_plan,
            use_nutrition_data=False
        )

        assert result == "Meal Plan Text"
        meal_plan_service.planner.format_meal_plan.assert_called_once()

    def test_get_meal_plan_text_format_nutrition(
        self,
        meal_plan_service,
        sample_meal_plan
    ):
        """Test nutrition text format generation."""
        meal_plan_service.nutrition_planner.format_nutrition_meal_plan = Mock(
            return_value="Nutrition Meal Plan Text"
        )

        result = meal_plan_service.get_meal_plan_text_format(
            sample_meal_plan,
            use_nutrition_data=True
        )

        assert result == "Nutrition Meal Plan Text"
        meal_plan_service.nutrition_planner.format_nutrition_meal_plan.assert_called_once()

    def test_metadata_fields(self, meal_plan_service, sample_meal_plan):
        """Test metadata fields in response."""
        result = meal_plan_service.format_meal_plan_response(
            sample_meal_plan,
            use_nutrition_data=True
        )

        metadata = result['metadata']
        assert 'generated_at' in metadata
        assert 'total_days' in metadata
        assert 'total_meals' in metadata
        assert 'uses_nutrition_data' in metadata
        assert metadata['total_days'] == 2
        assert metadata['total_meals'] == 6
