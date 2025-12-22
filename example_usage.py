"""
Example usage of the Gousto recipe scraper.
Demonstrates basic scraping workflow.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.connection import engine, get_db_session, init_database
from src.scrapers.gousto_scraper import create_gousto_scraper
from src.utils.logger import get_logger

logger = get_logger("example")


def example_discover_recipes():
    """Example: Discover recipe URLs."""
    print("\n" + "="*60)
    print("Example 1: Discover Recipe URLs")
    print("="*60)

    session = next(get_db_session())
    scraper = create_gousto_scraper(session)

    print("\nDiscovering recipes from sitemap and categories...")
    urls = scraper.discover_recipes(save_to_db=False)

    print(f"\nTotal URLs discovered: {len(urls)}")
    print("\nFirst 5 URLs:")
    for url in urls[:5]:
        print(f"  - {url}")

    scraper.close()
    session.close()


def example_scrape_single_recipe():
    """Example: Scrape a single recipe."""
    print("\n" + "="*60)
    print("Example 2: Scrape Single Recipe")
    print("="*60)

    # Initialize database
    init_database(engine)

    session = next(get_db_session())
    scraper = create_gousto_scraper(session)

    test_url = "https://www.gousto.co.uk/cookbook/chicken-recipes/butter-chicken-with-coriander-rice"

    print(f"\nScraping: {test_url}")

    recipe_data = scraper.scrape_recipe(test_url)

    if recipe_data:
        print("\n✓ Successfully scraped recipe:")
        print(f"  Name: {recipe_data['name']}")
        print(f"  Description: {recipe_data.get('description', '')[:100]}...")
        print(f"  Ingredients: {len(recipe_data.get('ingredients', []))}")
        print(f"  Instructions: {len(recipe_data.get('instructions', []))}")
        print(f"  Total time: {recipe_data.get('total_time_minutes')} minutes")
        print(f"  Servings: {recipe_data.get('servings')}")

        if recipe_data.get('nutrition'):
            nutrition = recipe_data['nutrition']
            print(f"\n  Nutrition (per serving):")
            print(f"    Calories: {nutrition.get('calories')}")
            print(f"    Protein: {nutrition.get('protein_g')}g")
            print(f"    Carbs: {nutrition.get('carbohydrates_g')}g")
            print(f"    Fat: {nutrition.get('fat_g')}g")

        print("\n  Sample ingredients:")
        for i, ing in enumerate(recipe_data.get('ingredients', [])[:3], 1):
            qty = f"{ing['quantity']} {ing['unit']}" if ing['quantity'] and ing['unit'] else ing['quantity'] or ""
            print(f"    {i}. {ing['name']} ({qty})")

    else:
        print("\n✗ Failed to scrape recipe")

    scraper.close()
    session.close()


def example_scrape_multiple():
    """Example: Scrape multiple recipes with limit."""
    print("\n" + "="*60)
    print("Example 3: Scrape Multiple Recipes (Limited)")
    print("="*60)

    init_database(engine)

    session = next(get_db_session())
    scraper = create_gousto_scraper(session)

    print("\nScraping first 3 recipes...")

    stats = scraper.scrape_all(limit=3)

    print("\n" + "-"*60)
    print("Scraping Results:")
    print("-"*60)
    print(f"  Total recipes attempted: {stats['total']}")
    print(f"  Successfully scraped:    {stats['success']}")
    print(f"  Failed:                  {stats['failed']}")
    print(f"  Skipped (duplicates):    {stats['skipped']}")
    print(f"  Validation errors:       {stats['validation_errors']}")

    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Success rate:            {success_rate:.1f}%")

    scraper.close()
    session.close()


def main():
    """Run examples."""
    print("\n" + "="*60)
    print("Gousto Recipe Scraper - Usage Examples")
    print("="*60)

    print("\nNOTE: These examples will make real HTTP requests to Gousto.")
    print("      Press Ctrl+C to cancel at any time.")

    try:
        # Example 1: Discover URLs (fast, no scraping)
        example_discover_recipes()

        # Example 2: Scrape single recipe (demonstrates data extraction)
        example_scrape_single_recipe()

        # Example 3: Scrape multiple recipes (demonstrates batch processing)
        # Uncomment to run:
        # example_scrape_multiple()

        print("\n" + "="*60)
        print("Examples complete!")
        print("="*60)

        print("\nNext steps:")
        print("  1. Run: python -m src.cli init-db")
        print("  2. Run: python -m src.cli scrape --limit 10")
        print("  3. Run: python -m src.cli stats --detailed")
        print("  4. Run: python -m src.cli export --format json --output recipes.json")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
