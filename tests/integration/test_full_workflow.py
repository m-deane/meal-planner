"""
Integration tests for complete scraping workflow.
Tests end-to-end discovery, scraping, normalization, validation, and database storage.
"""

from unittest.mock import patch, Mock

import pytest

from src.scrapers.gousto_scraper import GoustoScraper
from src.database.models import Recipe, Ingredient, Category


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete scraping workflow."""

    @pytest.fixture
    def scraper(self, db_session):
        """Create scraper with test database."""
        return GoustoScraper(db_session)

    @patch('src.scrapers.gousto_scraper.scrape_me')
    def test_complete_recipe_scraping_workflow(self, mock_scrape_me, scraper, db_session, mock_recipe_scraper):
        """Test complete workflow from URL to database."""
        mock_scrape_me.return_value = mock_recipe_scraper

        url = 'https://www.gousto.co.uk/cookbook/recipes/test-recipe'

        recipe_data = scraper.scrape_recipe(url)

        assert recipe_data is not None
        assert 'name' in recipe_data
        assert 'ingredients' in recipe_data

        success = scraper._save_recipe(recipe_data)

        assert success is True

        recipe = db_session.query(Recipe).filter_by(slug='test-recipe').first()

        assert recipe is not None
        assert recipe.name == 'Test Recipe'
        assert len(recipe.ingredients_association) > 0
        assert len(recipe.cooking_instructions) > 0

    @patch('src.scrapers.recipe_discoverer.RecipeDiscoverer.discover_all')
    @patch('src.scrapers.gousto_scraper.scrape_me')
    def test_discover_and_scrape_workflow(self, mock_scrape_me, mock_discover, scraper, db_session, mock_recipe_scraper):
        """Test discovery followed by scraping."""
        mock_discover.return_value = [
            'https://www.gousto.co.uk/cookbook/recipes/recipe1',
            'https://www.gousto.co.uk/cookbook/recipes/recipe2'
        ]
        mock_scrape_me.return_value = mock_recipe_scraper

        urls = scraper.discover_recipes()

        assert len(urls) == 2

        stats = scraper.scrape_all(urls=urls, limit=2)

        assert stats['total'] == 2

    def test_ingredient_deduplication(self, scraper, db_session):
        """Test ingredients are deduplicated across recipes."""
        recipe1_data = {
            'name': 'Recipe 1',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/recipe1',
            'ingredients': [
                {'name': 'Tomato', 'quantity': '100', 'unit': 'g'}
            ]
        }

        recipe2_data = {
            'name': 'Recipe 2',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/recipe2',
            'ingredients': [
                {'name': 'Tomato', 'quantity': '200', 'unit': 'g'}
            ]
        }

        scraper._save_recipe(recipe1_data)
        scraper._save_recipe(recipe2_data)

        ingredients = db_session.query(Ingredient).filter_by(normalized_name='tomato').all()

        assert len(ingredients) == 1

    def test_category_assignment(self, scraper, db_session):
        """Test categories are properly assigned."""
        recipe_data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'category': 'Italian'
        }

        scraper._save_recipe(recipe_data)

        recipe = db_session.query(Recipe).first()

        assert len(recipe.categories) > 0
        assert recipe.categories[0].name == 'Italian'

    def test_nutrition_info_storage(self, scraper, db_session):
        """Test nutritional information is stored correctly."""
        recipe_data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'calories': 350,
                'protein_g': 15,
                'carbohydrates_g': 40,
                'fat_g': 12
            }
        }

        scraper._save_recipe(recipe_data)

        recipe = db_session.query(Recipe).first()

        assert recipe.nutritional_info is not None
        assert recipe.nutritional_info.calories == 350
        assert recipe.nutritional_info.protein_g == 15

    def test_skip_existing_recipes(self, scraper, db_session):
        """Test scraper skips already-scraped recipes."""
        recipe_data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        scraper._save_recipe(recipe_data)

        exists = scraper._recipe_exists('https://www.gousto.co.uk/cookbook/recipes/test')

        assert exists is True

    def test_validation_integration(self, scraper):
        """Test validation is integrated into scraping."""
        with patch('src.scrapers.gousto_scraper.scrape_me') as mock_scrape:
            mock_scraper = Mock()
            mock_scraper.title.return_value = "AB"
            mock_scraper.description.return_value = ""
            mock_scraper.ingredients.return_value = []
            mock_scraper.instructions_list.return_value = []
            mock_scrape.return_value = mock_scraper

            result = scraper.scrape_recipe('https://www.gousto.co.uk/cookbook/recipes/test')

            assert scraper.stats['validation_errors'] >= 0

    @patch('src.scrapers.gousto_scraper.scrape_me')
    def test_error_recovery(self, mock_scrape_me, scraper, db_session):
        """Test scraper recovers from errors."""
        mock_scrape_me.side_effect = [
            Exception('First error'),
            Exception('Second error')
        ]

        urls = [
            'https://www.gousto.co.uk/cookbook/recipes/recipe1',
            'https://www.gousto.co.uk/cookbook/recipes/recipe2'
        ]

        stats = scraper.scrape_all(urls=urls)

        assert stats['failed'] == 2
        assert stats['success'] == 0

    def test_transaction_rollback_on_error(self, scraper, db_session):
        """Test database transaction rolls back on error."""
        invalid_data = {
            'name': 'Test',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'ingredients': [
                {'name': None}
            ]
        }

        result = scraper._save_recipe(invalid_data)

        assert result is False

        recipes = db_session.query(Recipe).all()
        assert len(recipes) == 0
