"""
Unit tests for ShoppingListService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal

from src.api.services.shopping_list_service import ShoppingListService
from src.database.models import Recipe


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def shopping_list_service(mock_db):
    """Create ShoppingListService instance."""
    return ShoppingListService(mock_db)


@pytest.fixture
def sample_categorized_ingredients():
    """Create sample categorized ingredients."""
    return {
        'Proteins': [
            {
                'name': 'Chicken Breast',
                'quantities': {
                    'g': {'total': 500.0, 'count': 2}
                },
                'preparations': ['diced', 'sliced'],
                'times_needed': 2
            }
        ],
        'Vegetables': [
            {
                'name': 'Tomato',
                'quantities': {
                    'piece': {'total': None, 'count': 4}
                },
                'preparations': ['chopped'],
                'times_needed': 4
            },
            {
                'name': 'Onion',
                'quantities': {
                    'piece': {'total': None, 'count': 2}
                },
                'preparations': ['diced'],
                'times_needed': 2
            }
        ],
        'Herbs & Spices': [
            {
                'name': 'Garlic',
                'quantities': {
                    'clove': {'total': None, 'count': 6}
                },
                'preparations': ['minced'],
                'times_needed': 3
            }
        ]
    }


class TestShoppingListService:
    """Test ShoppingListService class."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = ShoppingListService(mock_db)
        assert service.db == mock_db
        assert service.generator is not None

    def test_generate_from_recipes(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test shopping list generation from recipe IDs."""
        shopping_list_service.generator.generate_from_recipes = Mock(
            return_value=sample_categorized_ingredients
        )

        result = shopping_list_service.generate_from_recipes(
            recipe_ids=[1, 2, 3]
        )

        assert result is not None
        assert 'categories' in result
        assert 'summary' in result
        assert 'recipe_ids' in result
        assert result['summary']['total_items'] == 4
        assert result['summary']['recipes_count'] == 3

    def test_generate_from_meal_plan(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test shopping list generation from meal plan."""
        recipe1 = Recipe(id=1, slug='r1', name='R1', source_url='url1')
        recipe2 = Recipe(id=2, slug='r2', name='R2', source_url='url2')

        meal_plan = {
            'Monday': {
                'breakfast': recipe1,
                'lunch': recipe2
            }
        }

        shopping_list_service.generator.generate_from_recipes = Mock(
            return_value=sample_categorized_ingredients
        )

        result = shopping_list_service.generate_from_meal_plan(meal_plan)

        assert result is not None
        assert 'categories' in result
        shopping_list_service.generator.generate_from_recipes.assert_called_once()

    def test_format_shopping_list_response(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test shopping list response formatting."""
        result = shopping_list_service.format_shopping_list_response(
            sample_categorized_ingredients,
            recipe_ids=[1, 2, 3]
        )

        assert result is not None
        assert 'categories' in result
        assert 'summary' in result

        # Check category ordering
        category_names = [cat['name'] for cat in result['categories']]
        assert 'Proteins' in category_names
        assert 'Vegetables' in category_names
        assert 'Herbs & Spices' in category_names

        # Proteins should come before vegetables
        assert category_names.index('Proteins') < category_names.index('Vegetables')

    def test_format_shopping_list_response_items(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test formatted items structure."""
        result = shopping_list_service.format_shopping_list_response(
            sample_categorized_ingredients,
            recipe_ids=[1, 2]
        )

        # Check protein category
        proteins_cat = next(
            cat for cat in result['categories']
            if cat['name'] == 'Proteins'
        )
        assert proteins_cat['item_count'] == 1
        assert len(proteins_cat['items']) == 1

        item = proteins_cat['items'][0]
        assert item['name'] == 'Chicken Breast'
        assert item['times_needed'] == 2
        assert 'quantities' in item
        assert len(item['preparations']) == 2

    def test_format_quantities(self, shopping_list_service):
        """Test quantity formatting."""
        quantities = {
            'g': {'total': 500.0, 'count': 2},
            'piece': {'total': None, 'count': 3}
        }

        result = shopping_list_service._format_quantities(quantities)

        assert len(result) == 2
        assert any(q['unit'] == 'g' and q['total'] == 500.0 for q in result)
        assert any(q['unit'] == 'piece' and q['count'] == 3 for q in result)

    def test_generate_compact_shopping_list(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test compact shopping list generation."""
        shopping_list_service.generator.generate_from_recipes = Mock(
            return_value=sample_categorized_ingredients
        )

        result = shopping_list_service.generate_compact_shopping_list([1, 2])

        assert result is not None
        assert 'categories' in result
        assert 'summary' in result

        # Check simplified structure
        proteins = result['categories']['Proteins']
        assert len(proteins) == 1
        assert proteins[0]['name'] == 'Chicken Breast'
        assert proteins[0]['checked'] is False

    def test_get_shopping_list_text_format_detailed(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test detailed text format generation."""
        shopping_list_service.generator.format_shopping_list = Mock(
            return_value="Detailed Shopping List"
        )

        result = shopping_list_service.get_shopping_list_text_format(
            sample_categorized_ingredients,
            format_type='detailed'
        )

        assert result == "Detailed Shopping List"
        shopping_list_service.generator.format_shopping_list.assert_called_once_with(
            sample_categorized_ingredients,
            show_quantities=True,
            show_preparations=True
        )

    def test_get_shopping_list_text_format_compact(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test compact text format generation."""
        shopping_list_service.generator.generate_compact_list = Mock(
            return_value="Compact List"
        )

        result = shopping_list_service.get_shopping_list_text_format(
            sample_categorized_ingredients,
            format_type='compact'
        )

        assert result == "Compact List"
        shopping_list_service.generator.generate_compact_list.assert_called_once()

    def test_summary_calculations(
        self,
        shopping_list_service,
        sample_categorized_ingredients
    ):
        """Test summary statistics calculations."""
        result = shopping_list_service.format_shopping_list_response(
            sample_categorized_ingredients,
            recipe_ids=[1, 2, 3, 1]  # Include duplicate
        )

        summary = result['summary']
        assert summary['total_items'] == 4  # 1 protein + 2 veg + 1 spice
        assert summary['total_categories'] == 3
        assert summary['recipes_count'] == 3  # Duplicates removed

    def test_empty_categories_excluded(self, shopping_list_service):
        """Test that empty categories are excluded from response."""
        categorized = {
            'Proteins': [
                {
                    'name': 'Chicken',
                    'quantities': {},
                    'preparations': [],
                    'times_needed': 1
                }
            ],
            'Vegetables': [],  # Empty
            'Dairy': []  # Empty
        }

        result = shopping_list_service.format_shopping_list_response(
            categorized,
            recipe_ids=[1]
        )

        category_names = [cat['name'] for cat in result['categories']]
        assert 'Proteins' in category_names
        assert 'Vegetables' not in category_names
        assert 'Dairy' not in category_names
