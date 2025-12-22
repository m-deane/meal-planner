"""
Unit tests for Gousto scraper module.
Tests recipe scraping, normalization, and database integration.
"""

from unittest.mock import Mock, patch, MagicMock

import pytest

# Skip this module if imports fail
pytest.importorskip("src.scrapers.gousto_scraper")

from src.scrapers.gousto_scraper import GoustoScraper, create_gousto_scraper
from src.database.models import Recipe


class TestGoustoScraper:
    """Test GoustoScraper class."""

    @pytest.fixture
    def scraper(self, db_session, checkpoint_manager):
        """Create scraper instance."""
        return GoustoScraper(db_session, checkpoint_manager)

    def test_initialization(self, scraper, db_session, checkpoint_manager):
        """Test scraper initialization."""
        assert scraper.session == db_session
        assert scraper.checkpoint_manager == checkpoint_manager
        assert scraper.http_client is not None
        assert scraper.discoverer is not None
        assert scraper.normalizer is not None

    def test_stats_initialization(self, scraper):
        """Test stats initialization."""
        assert scraper.stats['total'] == 0
        assert scraper.stats['success'] == 0
        assert scraper.stats['failed'] == 0
        assert scraper.stats['skipped'] == 0
        assert scraper.stats['validation_errors'] == 0

    @patch('src.scrapers.gousto_scraper.create_recipe_discoverer')
    def test_discover_recipes(self, mock_create_discoverer, scraper):
        """Test recipe URL discovery."""
        mock_discoverer = Mock()
        mock_discoverer.discover_all.return_value = ['url1', 'url2', 'url3']
        mock_create_discoverer.return_value = mock_discoverer
        scraper.discoverer = mock_discoverer

        urls = scraper.discover_recipes()

        assert len(urls) == 3
        mock_discoverer.discover_all.assert_called_once()

    def test_scrape_recipe_success(self, scraper, mock_recipe_scraper, sample_recipe_data):
        """Test successful recipe scraping."""
        with patch('src.scrapers.gousto_scraper.scrape_me') as mock_scrape:
            mock_scrape.return_value = mock_recipe_scraper

            result = scraper.scrape_recipe('https://www.gousto.co.uk/cookbook/recipes/test')

            assert result is not None
            assert 'name' in result
            assert 'ingredients' in result
            assert 'instructions' in result

    def test_scrape_recipe_failure(self, scraper):
        """Test recipe scraping failure."""
        with patch('src.scrapers.gousto_scraper.scrape_me') as mock_scrape:
            mock_scrape.side_effect = Exception('Scraping failed')

            result = scraper.scrape_recipe('https://www.gousto.co.uk/cookbook/recipes/test')

            assert result is None

    def test_scrape_recipe_validation_failure_strict(self, scraper, test_config):
        """Test recipe scraping with validation failure in strict mode."""
        test_config.validation_strict = True

        with patch('src.scrapers.gousto_scraper.scrape_me') as mock_scrape:
            mock_scraper = Mock()
            mock_scraper.title.return_value = "AB"
            mock_scraper.description.return_value = ""
            mock_scraper.ingredients.return_value = []
            mock_scraper.instructions_list.return_value = []
            mock_scrape.return_value = mock_scraper

            result = scraper.scrape_recipe('https://www.gousto.co.uk/cookbook/recipes/test')

            assert result is None

    def test_extract_slug_from_url(self, scraper):
        """Test extracting slug from URL."""
        url = 'https://www.gousto.co.uk/cookbook/recipes/chicken-tikka-masala'
        slug = scraper._extract_slug_from_url(url)

        assert slug == 'chicken-tikka-masala'

    def test_extract_slug_from_url_with_trailing_slash(self, scraper):
        """Test extracting slug with trailing slash."""
        url = 'https://www.gousto.co.uk/cookbook/recipes/chicken-tikka/'
        slug = scraper._extract_slug_from_url(url)

        assert slug == 'chicken-tikka'

    def test_extract_gousto_id_from_url(self, scraper):
        """Test extracting Gousto ID from URL."""
        url = 'https://www.gousto.co.uk/cookbook/recipes/chicken-tikka'
        gousto_id = scraper._extract_gousto_id_from_url(url)

        assert gousto_id == 'gousto_chicken-tikka'

    def test_recipe_exists_true(self, scraper, populated_db_session):
        """Test checking if recipe exists."""
        url = 'https://www.gousto.co.uk/cookbook/recipes/test-recipe'

        exists = scraper._recipe_exists(url)

        assert exists is True

    def test_recipe_exists_false(self, scraper, db_session):
        """Test checking if recipe doesn't exist."""
        url = 'https://www.gousto.co.uk/cookbook/recipes/nonexistent'

        exists = scraper._recipe_exists(url)

        assert exists is False

    def test_save_recipe_success(self, scraper, db_session, sample_recipe_data):
        """Test successful recipe saving."""
        result = scraper._save_recipe(sample_recipe_data)

        assert result is True

        recipe = db_session.query(Recipe).first()
        assert recipe is not None
        assert recipe.name == sample_recipe_data['name']

    def test_save_recipe_failure(self, scraper, db_session):
        """Test recipe saving handles errors."""
        invalid_data = {'name': 'Test'}

        result = scraper._save_recipe(invalid_data)

        assert result is False

    def test_get_or_create_category(self, scraper, db_session):
        """Test getting or creating category."""
        category1 = scraper._get_or_create_category('Italian', 'cuisine')
        db_session.flush()

        assert category1 is not None
        assert category1.name == 'Italian'

        category2 = scraper._get_or_create_category('Italian', 'cuisine')

        assert category1.id == category2.id

    def test_get_or_create_ingredient(self, scraper, db_session):
        """Test getting or creating ingredient."""
        ingredient1 = scraper._get_or_create_ingredient('Tomato')
        db_session.flush()

        assert ingredient1 is not None
        assert ingredient1.name == 'Tomato'

        ingredient2 = scraper._get_or_create_ingredient('Tomato')

        assert ingredient1.id == ingredient2.id

    def test_get_or_create_unit(self, scraper, db_session):
        """Test getting or creating unit."""
        unit1 = scraper._get_or_create_unit('g')
        db_session.flush()

        assert unit1 is not None
        assert unit1.abbreviation == 'g'

        unit2 = scraper._get_or_create_unit('g')

        assert unit1.id == unit2.id

    def test_get_or_create_unit_none(self, scraper):
        """Test getting unit with None abbreviation."""
        unit = scraper._get_or_create_unit(None)

        assert unit is None

    def test_add_ingredient_to_recipe(self, scraper, db_session):
        """Test adding ingredient to recipe."""
        from src.database.models import Recipe

        recipe = Recipe(
            gousto_id='test',
            slug='test',
            name='Test',
            source_url='https://example.com',
            is_active=True
        )
        db_session.add(recipe)
        db_session.flush()

        ing_data = {
            'name': 'Tomato',
            'quantity': '250',
            'unit': 'g',
            'preparation': 'chopped',
            'is_optional': False
        }

        scraper._add_ingredient_to_recipe(recipe, ing_data, 0)
        db_session.flush()

        assert len(recipe.ingredients_association) > 0

    def test_add_instruction_to_recipe(self, scraper, db_session):
        """Test adding instruction to recipe."""
        from src.database.models import Recipe

        recipe = Recipe(
            gousto_id='test',
            slug='test',
            name='Test',
            source_url='https://example.com',
            is_active=True
        )
        db_session.add(recipe)
        db_session.flush()

        inst_data = {
            'step_number': 1,
            'instruction': 'Cook the food',
            'time_minutes': 10
        }

        scraper._add_instruction_to_recipe(recipe, inst_data)
        db_session.flush()

        assert len(recipe.cooking_instructions) > 0

    def test_add_instruction_to_recipe_string(self, scraper, db_session):
        """Test adding instruction as string."""
        from src.database.models import Recipe

        recipe = Recipe(
            gousto_id='test',
            slug='test',
            name='Test',
            source_url='https://example.com',
            is_active=True
        )
        db_session.add(recipe)
        db_session.flush()

        scraper._add_instruction_to_recipe(recipe, 'Cook the food')
        db_session.flush()

        assert len(recipe.cooking_instructions) > 0

    def test_add_nutrition_to_recipe(self, scraper, db_session):
        """Test adding nutrition info to recipe."""
        from src.database.models import Recipe

        recipe = Recipe(
            gousto_id='test',
            slug='test',
            name='Test',
            source_url='https://example.com',
            is_active=True
        )
        db_session.add(recipe)
        db_session.flush()

        nutrition_data = {
            'calories': 350,
            'protein_g': 15,
            'carbohydrates_g': 40,
            'fat_g': 12
        }

        scraper._add_nutrition_to_recipe(recipe, nutrition_data)
        db_session.flush()

        assert recipe.nutritional_info is not None

    def test_add_image_to_recipe(self, scraper, db_session):
        """Test adding image to recipe."""
        from src.database.models import Recipe

        recipe = Recipe(
            gousto_id='test',
            slug='test',
            name='Test',
            source_url='https://example.com',
            is_active=True
        )
        db_session.add(recipe)
        db_session.flush()

        scraper._add_image_to_recipe(recipe, 'https://example.com/image.jpg')
        db_session.flush()

        assert len(recipe.images) > 0

    def test_extract_nutrition(self, scraper, mock_recipe_scraper):
        """Test nutrition extraction."""
        nutrition = scraper._extract_nutrition(mock_recipe_scraper)

        assert nutrition is not None
        assert 'calories' in nutrition

    def test_extract_nutrition_failure(self, scraper):
        """Test nutrition extraction handles errors."""
        mock_scraper = Mock()
        mock_scraper.nutrients.side_effect = Exception('Error')

        nutrition = scraper._extract_nutrition(mock_scraper)

        assert nutrition == {}

    def test_extract_rating(self, scraper, mock_recipe_scraper):
        """Test rating extraction."""
        rating = scraper._extract_rating(mock_recipe_scraper)

        assert rating is not None
        assert 'ratingValue' in rating

    def test_extract_rating_none(self, scraper):
        """Test rating extraction with no rating."""
        mock_scraper = Mock()
        mock_scraper.ratings.return_value = None

        rating = scraper._extract_rating(mock_scraper)

        assert rating is None

    def test_scrape_all_with_limit(self, scraper, sample_urls):
        """Test scraping with limit."""
        with patch.object(scraper, 'scrape_recipe') as mock_scrape:
            mock_scrape.return_value = None

            stats = scraper.scrape_all(urls=sample_urls, limit=2)

            assert stats['total'] == 2
            assert mock_scrape.call_count == 2

    def test_scrape_all_skips_existing(self, scraper, sample_urls):
        """Test scraping skips existing recipes."""
        with patch.object(scraper, '_recipe_exists') as mock_exists:
            mock_exists.return_value = True

            stats = scraper.scrape_all(urls=sample_urls[:1])

            assert stats['skipped'] == 1

    def test_close(self, scraper):
        """Test scraper cleanup."""
        with patch.object(scraper.http_client, 'close') as mock_close:
            scraper.close()

            mock_close.assert_called_once()


def test_create_gousto_scraper(db_session):
    """Test factory function creates scraper."""
    scraper = create_gousto_scraper(session=db_session)

    assert isinstance(scraper, GoustoScraper)
    assert scraper.session == db_session


def test_create_gousto_scraper_no_session():
    """Test factory function creates scraper with new session."""
    with patch('src.scrapers.gousto_scraper.get_db_session'):
        scraper = create_gousto_scraper()

        assert isinstance(scraper, GoustoScraper)
