"""
Command-line interface for recipe scraper.
Provides commands for discovery, scraping, export, and statistics.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import click
from sqlalchemy import func

from src.config import config
from src.database.connection import engine, get_db_session, init_database
from src.database.models import Recipe, Ingredient, Category, NutritionalInfo
from src.scrapers.gousto_scraper import create_gousto_scraper
from src.utils.checkpoint import create_checkpoint_manager
from src.utils.logger import get_logger

logger = get_logger("cli")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Gousto Recipe Scraper CLI."""
    pass


@cli.command()
@click.option(
    '--save-to-db',
    is_flag=True,
    help='Save discovered URLs to database'
)
def discover(save_to_db: bool):
    """Discover all recipe URLs from sitemap and categories."""
    logger.info("Starting recipe URL discovery")

    try:
        session = next(get_db_session())
        scraper = create_gousto_scraper(session)

        urls = scraper.discover_recipes(save_to_db=save_to_db)

        click.echo(f"\nDiscovered {len(urls)} recipe URLs")
        click.echo("\nSample URLs:")
        for url in urls[:10]:
            click.echo(f"  - {url}")

        if len(urls) > 10:
            click.echo(f"  ... and {len(urls) - 10} more")

        scraper.close()
        session.close()

        click.echo("\n✓ Discovery complete")

    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    '--limit',
    type=int,
    default=None,
    help='Maximum number of recipes to scrape'
)
@click.option(
    '--delay',
    type=float,
    default=None,
    help='Delay between requests in seconds'
)
@click.option(
    '--resume',
    is_flag=True,
    help='Resume from last checkpoint'
)
@click.option(
    '--urls-file',
    type=click.Path(exists=True),
    help='File containing URLs to scrape (one per line)'
)
def scrape(
    limit: Optional[int],
    delay: Optional[float],
    resume: bool,
    urls_file: Optional[str]
):
    """Scrape recipes from Gousto."""
    logger.info("Starting recipe scraping")

    if delay:
        config.scraper_delay_seconds = delay

    try:
        init_database(engine)

        session = next(get_db_session())
        checkpoint_manager = create_checkpoint_manager()
        scraper = create_gousto_scraper(session, checkpoint_manager)

        urls = None
        if urls_file:
            urls = _load_urls_from_file(urls_file)
            click.echo(f"Loaded {len(urls)} URLs from {urls_file}")

        click.echo(f"\nConfiguration:")
        click.echo(f"  Rate limit: {config.scraper_delay_seconds}s")
        click.echo(f"  Max retries: {config.scraper_max_retries}")
        click.echo(f"  Limit: {limit or 'None'}")
        click.echo(f"  Resume: {resume}")

        stats = scraper.scrape_all(urls=urls, limit=limit, resume=resume)

        click.echo(f"\n{'='*50}")
        click.echo("Scraping Statistics:")
        click.echo(f"{'='*50}")
        click.echo(f"  Total:              {stats['total']}")
        click.echo(f"  Success:            {stats['success']}")
        click.echo(f"  Failed:             {stats['failed']}")
        click.echo(f"  Skipped (existing): {stats['skipped']}")
        click.echo(f"  Validation errors:  {stats['validation_errors']}")

        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        click.echo(f"  Success rate:       {success_rate:.1f}%")
        click.echo(f"{'='*50}")

        scraper.close()
        session.close()

        click.echo("\n✓ Scraping complete")

    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    '--format',
    type=click.Choice(['json', 'csv'], case_sensitive=False),
    default='json',
    help='Export format'
)
@click.option(
    '--output',
    type=click.Path(),
    required=True,
    help='Output file path'
)
@click.option(
    '--include-inactive',
    is_flag=True,
    help='Include inactive recipes'
)
@click.option(
    '--limit',
    type=int,
    default=None,
    help='Maximum number of recipes to export'
)
def export(
    format: str,
    output: str,
    include_inactive: bool,
    limit: Optional[int]
):
    """Export recipes to JSON or CSV."""
    logger.info(f"Exporting recipes to {format.upper()}")

    try:
        session = next(get_db_session())

        query = session.query(Recipe)
        if not include_inactive:
            query = query.filter(Recipe.is_active == True)

        if limit:
            query = query.limit(limit)

        recipes = query.all()

        click.echo(f"\nExporting {len(recipes)} recipes to {output}")

        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'json':
            _export_json(recipes, output_path)
        else:
            _export_csv(recipes, output_path)

        session.close()

        click.echo(f"✓ Export complete: {output}")

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    '--detailed',
    is_flag=True,
    help='Show detailed statistics'
)
def stats(detailed: bool):
    """Show database statistics."""
    logger.info("Generating statistics")

    try:
        session = next(get_db_session())

        total_recipes = session.query(func.count(Recipe.id)).scalar()
        active_recipes = session.query(func.count(Recipe.id)).filter(
            Recipe.is_active == True
        ).scalar()
        total_ingredients = session.query(func.count(Ingredient.id)).scalar()
        total_categories = session.query(func.count(Category.id)).scalar()

        click.echo(f"\n{'='*50}")
        click.echo("Database Statistics:")
        click.echo(f"{'='*50}")
        click.echo(f"  Total recipes:      {total_recipes}")
        click.echo(f"  Active recipes:     {active_recipes}")
        click.echo(f"  Total ingredients:  {total_ingredients}")
        click.echo(f"  Total categories:   {total_categories}")

        if detailed and total_recipes > 0:
            click.echo(f"\n{'-'*50}")
            click.echo("Category Breakdown:")
            click.echo(f"{'-'*50}")

            categories = session.query(
                Category.name,
                func.count(Recipe.id).label('recipe_count')
            ).join(
                Recipe.categories
            ).group_by(
                Category.id, Category.name
            ).order_by(
                func.count(Recipe.id).desc()
            ).limit(10).all()

            for cat_name, count in categories:
                click.echo(f"  {cat_name:<30} {count:>5} recipes")

            click.echo(f"\n{'-'*50}")
            click.echo("Nutrition Availability:")
            click.echo(f"{'-'*50}")

            recipes_with_nutrition = session.query(
                func.count(Recipe.id)
            ).join(NutritionalInfo).scalar()

            nutrition_pct = (recipes_with_nutrition / total_recipes * 100) if total_recipes > 0 else 0
            click.echo(f"  Recipes with nutrition: {recipes_with_nutrition} ({nutrition_pct:.1f}%)")

            avg_calories = session.query(
                func.avg(NutritionalInfo.calories)
            ).scalar()
            if avg_calories:
                click.echo(f"  Average calories:       {avg_calories:.0f}")

        click.echo(f"{'='*50}\n")

        session.close()

    except Exception as e:
        logger.error(f"Stats generation failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def init_db():
    """Initialize database schema."""
    logger.info("Initializing database")

    try:
        click.echo("Initializing database schema...")
        init_database(engine)
        click.echo("✓ Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def clear_checkpoint():
    """Clear checkpoint file to start fresh."""
    try:
        checkpoint_manager = create_checkpoint_manager()
        checkpoint_manager.clear()
        click.echo("✓ Checkpoint cleared")

    except Exception as e:
        logger.error(f"Failed to clear checkpoint: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


def _load_urls_from_file(file_path: str) -> list:
    """Load URLs from text file."""
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls


def _export_json(recipes: list, output_path: Path) -> None:
    """Export recipes to JSON."""
    data = []

    for recipe in recipes:
        recipe_dict = {
            'id': recipe.id,
            'gousto_id': recipe.gousto_id,
            'name': recipe.name,
            'slug': recipe.slug,
            'description': recipe.description,
            'cooking_time_minutes': recipe.cooking_time_minutes,
            'servings': recipe.servings,
            'source_url': recipe.source_url,
            'categories': [cat.name for cat in recipe.categories],
            'ingredients': [
                {
                    'name': ri.ingredient.name,
                    'quantity': str(ri.quantity) if ri.quantity else None,
                    'unit': ri.unit.abbreviation if ri.unit else None,
                    'preparation': ri.preparation_note
                }
                for ri in recipe.ingredients_association
            ],
            'instructions': [
                {
                    'step': inst.step_number,
                    'instruction': inst.instruction
                }
                for inst in recipe.cooking_instructions
            ],
            'nutrition': {
                'calories': str(recipe.nutritional_info.calories) if recipe.nutritional_info and recipe.nutritional_info.calories else None,
                'protein_g': str(recipe.nutritional_info.protein_g) if recipe.nutritional_info and recipe.nutritional_info.protein_g else None,
                'carbohydrates_g': str(recipe.nutritional_info.carbohydrates_g) if recipe.nutritional_info and recipe.nutritional_info.carbohydrates_g else None,
                'fat_g': str(recipe.nutritional_info.fat_g) if recipe.nutritional_info and recipe.nutritional_info.fat_g else None,
            } if recipe.nutritional_info else None,
            'images': [img.url for img in recipe.images],
            'is_active': recipe.is_active,
            'date_scraped': recipe.date_scraped.isoformat() if recipe.date_scraped else None
        }

        data.append(recipe_dict)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            data,
            f,
            indent=2 if config.export_pretty_json else None,
            ensure_ascii=False
        )


def _export_csv(recipes: list, output_path: Path) -> None:
    """Export recipes to CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        writer.writerow([
            'ID',
            'Name',
            'Slug',
            'Description',
            'Cooking Time (min)',
            'Servings',
            'Categories',
            'Ingredient Count',
            'Instruction Count',
            'Calories',
            'URL',
            'Active'
        ])

        for recipe in recipes:
            categories = ', '.join([cat.name for cat in recipe.categories])
            ingredient_count = len(recipe.ingredients_association)
            instruction_count = len(recipe.cooking_instructions)
            calories = recipe.nutritional_info.calories if recipe.nutritional_info else None

            writer.writerow([
                recipe.id,
                recipe.name,
                recipe.slug,
                recipe.description[:100] if recipe.description else '',
                recipe.cooking_time_minutes,
                recipe.servings,
                categories,
                ingredient_count,
                instruction_count,
                calories,
                recipe.source_url,
                recipe.is_active
            ])


@cli.command()
@click.option(
    '--min-protein',
    type=float,
    default=25.0,
    help='Minimum protein in grams per serving'
)
@click.option(
    '--max-carbs',
    type=float,
    default=30.0,
    help='Maximum carbs in grams per serving'
)
@click.option(
    '--output',
    type=click.Path(),
    default='meal_plans/meal_plan.md',
    help='Output file path'
)
@click.option(
    '--with-nutrition',
    is_flag=True,
    help='Use actual nutrition data (requires nutrition scraping)'
)
def meal_plan(
    min_protein: float,
    max_carbs: float,
    output: str,
    with_nutrition: bool
):
    """Generate a 7-day meal plan based on dietary criteria."""
    logger.info(f"Generating meal plan (protein≥{min_protein}g, carbs≤{max_carbs}g)")

    try:
        session = next(get_db_session())

        if with_nutrition:
            # Use actual nutrition data
            from src.meal_planner.nutrition_planner import NutritionMealPlanner
            import json
            from datetime import datetime
            from src.database.models import Recipe

            planner = NutritionMealPlanner(session)

            click.echo(f"Filtering recipes with actual nutrition data...")
            click.echo(f"  Min protein: {min_protein}g")
            click.echo(f"  Max carbs: {max_carbs}g\n")

            # Get recipes that match nutrition criteria
            candidates = planner.filter_by_actual_nutrition(
                min_protein_g=min_protein,
                max_carbs_g=max_carbs,
                limit=100
            )

            if len(candidates) < 21:
                click.echo(f"⚠️  Warning: Only {len(candidates)} recipes match criteria.")
                click.echo("    Meal plan may have duplicate recipes.\n")

            # Build meal plan
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            meal_plan_dict = {}

            recipe_index = 0
            for day in days:
                meal_plan_dict[day] = {}
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    if recipe_index < len(candidates):
                        meal_plan_dict[day][meal_type] = candidates[recipe_index][0]
                        recipe_index += 1

            # Format
            formatted = planner.format_nutrition_meal_plan(meal_plan_dict)

            # Save
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write("# High Protein, Low Carb Meal Plan\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
                f.write("**Data Source:** Actual nutrition values from Gousto recipes\n\n")
                f.write("---\n\n")
                f.write(formatted)

            click.echo(f"✓ Meal plan saved to: {output_path}")

        else:
            # Use ingredient-based scoring
            from src.meal_planner import create_meal_plan

            click.echo(f"Generating meal plan using ingredient analysis...")
            click.echo(f"  Protein score: ≥40/100")
            click.echo(f"  Carb score: ≤40/100\n")

            meal_plan_text = create_meal_plan(
                session=session,
                min_protein_score=40.0,
                max_carb_score=40.0
            )

            # Save
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write(meal_plan_text)

            click.echo(f"✓ Meal plan saved to: {output_path}")
            click.echo("\n⚠️  This meal plan uses ingredient-based estimates.")
            click.echo("    Use --with-nutrition for actual nutrition values.")

        session.close()

    except Exception as e:
        logger.error(f"Meal plan generation failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
