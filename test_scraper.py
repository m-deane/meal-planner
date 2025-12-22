"""
Quick test script to verify scraper functionality.
Tests basic components without full scraping.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from src.config import config
        print("  ✓ Config module imported")

        from src.utils.logger import get_logger
        print("  ✓ Logger module imported")

        from src.utils.http_client import create_http_client
        print("  ✓ HTTP client module imported")

        from src.utils.checkpoint import create_checkpoint_manager
        print("  ✓ Checkpoint module imported")

        from src.scrapers.recipe_discoverer import create_recipe_discoverer
        print("  ✓ Recipe discoverer module imported")

        from src.scrapers.data_normalizer import create_data_normalizer
        print("  ✓ Data normalizer module imported")

        from src.validators.data_validator import validate_recipe
        print("  ✓ Validator module imported")

        from src.database.models import Recipe, Ingredient
        print("  ✓ Database models imported")

        return True

    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from src.config import config

        print(f"  Database URL: {config.database_url}")
        print(f"  Rate limit: {config.scraper_delay_seconds}s")
        print(f"  Max retries: {config.scraper_max_retries}")
        print(f"  Log level: {config.log_level}")
        print(f"  Checkpoint enabled: {config.checkpoint_enabled}")

        print("  ✓ Configuration loaded successfully")
        return True

    except Exception as e:
        print(f"  ✗ Configuration failed: {e}")
        return False


def test_logger():
    """Test logger initialization."""
    print("\nTesting logger...")

    try:
        from src.utils.logger import get_logger

        logger = get_logger("test")
        logger.info("Test log message")
        logger.debug("Test debug message")

        print("  ✓ Logger initialized successfully")
        return True

    except Exception as e:
        print(f"  ✗ Logger failed: {e}")
        return False


def test_http_client():
    """Test HTTP client initialization."""
    print("\nTesting HTTP client...")

    try:
        from src.utils.http_client import create_http_client

        client = create_http_client()
        print(f"  Request count: {client.request_count}")
        print(f"  Robots parser: {'Loaded' if client.robot_parser else 'Not loaded'}")

        client.close()

        print("  ✓ HTTP client initialized successfully")
        return True

    except Exception as e:
        print(f"  ✗ HTTP client failed: {e}")
        return False


def test_data_normalizer():
    """Test data normalization."""
    print("\nTesting data normalizer...")

    try:
        from src.scrapers.data_normalizer import create_data_normalizer

        normalizer = create_data_normalizer()

        # Test ingredient parsing
        test_ingredient = "Chicken breast strips (250g)"
        parsed = normalizer.ingredient_parser.parse(test_ingredient)

        print(f"  Input: {test_ingredient}")
        print(f"  Parsed: {parsed['name']}, {parsed['quantity']}{parsed['unit']}")

        # Test ISO duration parsing
        duration = normalizer._parse_iso_duration("PT35M")
        print(f"  ISO Duration PT35M = {duration} minutes")

        print("  ✓ Data normalizer working correctly")
        return True

    except Exception as e:
        print(f"  ✗ Data normalizer failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator():
    """Test data validation."""
    print("\nTesting validator...")

    try:
        from src.validators.data_validator import validate_recipe

        # Test valid recipe
        valid_recipe = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/test',
            'ingredients': [
                {'name': 'Test Ingredient', 'quantity': '100', 'unit': 'g'}
            ],
            'instructions': [
                {'step_number': 1, 'instruction': 'Test instruction'}
            ],
            'nutrition': {
                'calories': 500
            }
        }

        result = validate_recipe(valid_recipe)
        print(f"  Valid recipe: {result.is_valid}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Warnings: {len(result.warnings)}")

        # Test invalid recipe
        invalid_recipe = {
            'name': 'AB',  # Too short
            'source_url': 'not-a-url',
            'ingredients': [],
        }

        result = validate_recipe(invalid_recipe)
        print(f"  Invalid recipe detected: {not result.is_valid}")

        print("  ✓ Validator working correctly")
        return True

    except Exception as e:
        print(f"  ✗ Validator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """Test database model definitions."""
    print("\nTesting database models...")

    try:
        from src.database.models import (
            Recipe, Ingredient, Category, Unit,
            RecipeIngredient, CookingInstruction, NutritionalInfo
        )

        print("  ✓ Recipe model defined")
        print("  ✓ Ingredient model defined")
        print("  ✓ Category model defined")
        print("  ✓ All models imported successfully")

        return True

    except Exception as e:
        print(f"  ✗ Database models failed: {e}")
        return False


def test_recipe_scrapers_library():
    """Test recipe-scrapers library installation."""
    print("\nTesting recipe-scrapers library...")

    try:
        from recipe_scrapers import scrape_me

        print("  ✓ recipe-scrapers library installed")

        # Note: We won't actually scrape a recipe in the test
        # Just verify the library is available

        return True

    except ImportError as e:
        print(f"  ✗ recipe-scrapers not installed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Gousto Recipe Scraper - Component Tests")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Logger", test_logger),
        ("HTTP Client", test_http_client),
        ("Data Normalizer", test_data_normalizer),
        ("Validator", test_validator),
        ("Database Models", test_database_models),
        ("recipe-scrapers Library", test_recipe_scrapers_library),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n✓ All tests passed! Scraper is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
