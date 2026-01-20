"""
Shared pytest fixtures and configuration for all tests.
Provides database, HTTP client, and data fixtures.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import config
from src.database.models import (
    Base, Recipe, Ingredient, Unit, Category, User, UserPreference,
    Allergen, DietaryTag
)
from src.utils.checkpoint import CheckpointManager
from src.utils.http_client import RateLimitedHTTPClient


@pytest.fixture(scope="session")
def test_config():
    """Override config for testing."""
    original_values = {}

    test_overrides = {
        'database_url': 'sqlite:///:memory:',
        'log_level': 'ERROR',
        'scraper_delay_seconds': 0.1,
        'scraper_max_retries': 1,
        'checkpoint_enabled': False,
        'validation_strict': False,
    }

    for key, value in test_overrides.items():
        original_values[key] = getattr(config, key)
        setattr(config, key, value)

    yield config

    for key, value in original_values.items():
        setattr(config, key, value)


@pytest.fixture(scope="function")
def db_engine(test_config):
    """Create in-memory SQLite database engine for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create database session for each test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture
def sample_recipe_data() -> Dict:
    """Sample normalized recipe data for testing."""
    return {
        'name': 'Test Recipe',
        'description': 'A delicious test recipe',
        'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test-recipe',
        'total_time_minutes': 30,
        'servings': 2,
        'category': 'Italian',
        'cuisine': 'Italian',
        'image_url': 'https://example.com/image.jpg',
        'ingredients': [
            {
                'name': 'Tomato',
                'quantity': '250',
                'unit': 'g',
                'preparation': 'chopped',
                'is_optional': False,
                'original': 'Tomato (250g)'
            },
            {
                'name': 'Onion',
                'quantity': '1',
                'unit': None,
                'preparation': 'diced',
                'is_optional': False,
                'original': 'Onion, diced'
            }
        ],
        'instructions': [
            {
                'step_number': 1,
                'instruction': 'Chop the tomatoes',
                'time_minutes': 5,
                'serving_variants': None,
                'original': 'Chop the tomatoes'
            },
            {
                'step_number': 2,
                'instruction': 'Cook for 20 minutes',
                'time_minutes': 20,
                'serving_variants': None,
                'original': 'Cook for 20 minutes'
            }
        ],
        'nutrition': {
            'calories': 350,
            'protein_g': 12,
            'carbohydrates_g': 45,
            'fat_g': 10,
            'fiber_g': 5,
            'sugar_g': 8,
            'sodium_mg': 500,
            'saturated_fat_g': 3
        },
        'rating': {
            'value': 4.5,
            'count': 100
        }
    }


@pytest.fixture
def sample_raw_recipe() -> Dict:
    """Sample raw recipe data from recipe-scrapers."""
    return {
        'url': 'https://www.gousto.co.uk/cookbook/recipes/test-recipe',
        'name': 'Test Recipe',
        'description': 'A delicious test recipe',
        'totalTime': 'PT30M',
        'recipeYield': '2 servings',
        'recipeIngredient': [
            'Tomato (250g)',
            'Onion, diced x2',
            'Salt x0'
        ],
        'recipeInstructions': [
            'Chop the tomatoes',
            'Cook for 20 minutes'
        ],
        'nutrition': {
            'calories': '350',
            'carbohydrateContent': '45g',
            'proteinContent': '12g',
            'fatContent': '10g',
            'fiberContent': '5g',
            'sugarContent': '8g',
            'sodiumContent': '500mg',
            'saturatedFatContent': '3g'
        },
        'recipeCategory': 'Italian',
        'recipeCuisine': 'Italian',
        'aggregateRating': {
            'ratingValue': 4.5,
            'reviewCount': 100
        },
        'image': 'https://example.com/image.jpg'
    }


@pytest.fixture
def sample_sitemap_xml() -> str:
    """Sample sitemap XML for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.gousto.co.uk/cookbook/recipes/chicken-pasta</loc>
        <lastmod>2023-12-01</lastmod>
    </url>
    <url>
        <loc>https://www.gousto.co.uk/cookbook/recipes/beef-stir-fry</loc>
        <lastmod>2023-12-02</lastmod>
    </url>
    <url>
        <loc>https://www.gousto.co.uk/cookbook/categories/vegetarian</loc>
        <lastmod>2023-12-03</lastmod>
    </url>
    <url>
        <loc>https://www.gousto.co.uk/cookbook/recipes/vegan-curry</loc>
        <lastmod>2023-12-04</lastmod>
    </url>
</urlset>'''


@pytest.fixture
def sample_sitemap_index_xml() -> str:
    """Sample sitemap index XML for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://www.gousto.co.uk/sitemap-recipes-1.xml</loc>
        <lastmod>2023-12-01</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.gousto.co.uk/sitemap-recipes-2.xml</loc>
        <lastmod>2023-12-02</lastmod>
    </sitemap>
</sitemapindex>'''


@pytest.fixture
def sample_category_html() -> str:
    """Sample category page HTML for testing."""
    return '''<!DOCTYPE html>
<html>
<head><title>Chicken Recipes</title></head>
<body>
    <div class="recipe-list">
        <a href="/cookbook/recipes/chicken-tikka">Chicken Tikka</a>
        <a href="/cookbook/recipes/chicken-curry">Chicken Curry</a>
        <a href="/cookbook/categories/indian">Indian Category</a>
        <a href="https://www.gousto.co.uk/cookbook/recipes/chicken-pasta">Chicken Pasta</a>
    </div>
</body>
</html>'''


@pytest.fixture
def sample_robots_txt() -> str:
    """Sample robots.txt for testing."""
    return '''User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /cookbook/
Crawl-delay: 1
'''


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    client = Mock(spec=RateLimitedHTTPClient)
    client.request_count = 0
    client.last_request_time = 0.0
    return client


@pytest.fixture
def mock_recipe_scraper():
    """Mock recipe-scrapers scraper instance."""
    scraper = Mock()
    scraper.title.return_value = "Test Recipe"
    scraper.description.return_value = "A test recipe"
    scraper.total_time.return_value = 30
    scraper.yields.return_value = "2 servings"
    scraper.ingredients.return_value = ["Tomato (250g)", "Onion, diced"]
    scraper.instructions_list.return_value = ["Step 1", "Step 2"]
    scraper.category.return_value = "Italian"
    scraper.cuisine.return_value = "Italian"
    scraper.image.return_value = "https://example.com/image.jpg"
    scraper.nutrients.return_value = {
        'calories': '350',
        'proteinContent': '12g',
        'carbohydrateContent': '45g',
        'fatContent': '10g'
    }
    scraper.ratings.return_value = 4.5
    return scraper


@pytest.fixture
def temp_checkpoint_file(tmp_path):
    """Create temporary checkpoint file path."""
    checkpoint_file = tmp_path / "test_checkpoint.json"
    yield checkpoint_file
    if checkpoint_file.exists():
        checkpoint_file.unlink()


@pytest.fixture
def checkpoint_manager(temp_checkpoint_file):
    """Create checkpoint manager with temporary file."""
    manager = CheckpointManager(checkpoint_file=temp_checkpoint_file)
    yield manager
    if temp_checkpoint_file.exists():
        temp_checkpoint_file.unlink()


@pytest.fixture
def populated_db_session(db_session):
    """Database session with pre-populated test data."""
    category = Category(
        name="Italian",
        slug="italian",
        category_type="cuisine"
    )
    db_session.add(category)

    tomato = Ingredient(
        name="Tomato",
        normalized_name="tomato"
    )
    db_session.add(tomato)

    gram_unit = Unit(
        name="gram",
        abbreviation="g",
        unit_type="weight"
    )
    db_session.add(gram_unit)

    recipe = Recipe(
        gousto_id="gousto_test-recipe",
        slug="test-recipe",
        name="Test Recipe",
        description="A test recipe",
        cooking_time_minutes=30,
        servings=2,
        source_url="https://www.gousto.co.uk/cookbook/recipes/test-recipe",
        is_active=True
    )
    db_session.add(recipe)

    db_session.commit()

    return db_session


@pytest.fixture
def fixtures_dir() -> Path:
    """Get fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture(fixtures_dir):
    """Factory fixture to load JSON fixtures."""
    def _load(filename: str) -> Dict:
        fixture_path = fixtures_dir / filename
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture not found: {fixture_path}")
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return _load


# Session-scoped fixtures for performance

@pytest.fixture(scope="session")
def sample_urls() -> List[str]:
    """Sample recipe URLs for testing."""
    return [
        "https://www.gousto.co.uk/cookbook/recipes/chicken-tikka",
        "https://www.gousto.co.uk/cookbook/recipes/beef-stir-fry",
        "https://www.gousto.co.uk/cookbook/recipes/vegan-curry",
        "https://www.gousto.co.uk/cookbook/recipes/pasta-carbonara",
        "https://www.gousto.co.uk/cookbook/recipes/fish-tacos",
    ]


# Utility functions for tests

def create_recipe_in_db(session: Session, **kwargs) -> Recipe:
    """Helper to create recipe in database."""
    defaults = {
        'gousto_id': 'gousto_test',
        'slug': 'test',
        'name': 'Test Recipe',
        'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
        'is_active': True
    }
    defaults.update(kwargs)

    recipe = Recipe(**defaults)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe


def create_ingredient_in_db(session: Session, name: str) -> Ingredient:
    """Helper to create ingredient in database."""
    ingredient = Ingredient(
        name=name,
        normalized_name=name.lower()
    )
    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient
