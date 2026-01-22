"""
Main Gousto recipe scraper.
Coordinates URL discovery, data extraction, normalization, validation, and database storage.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

from recipe_scrapers import scrape_me
from recipe_scrapers._exceptions import WebsiteNotImplementedError, RecipeScrapersExceptions
from sqlalchemy.orm import Session

from src.config import config
from src.database.connection import get_db_session
from src.database.models import (
    Recipe, Category, Ingredient, Unit, CookingInstruction,
    NutritionalInfo, Image, RecipeIngredient, ScrapingHistory
)
from src.scrapers.data_normalizer import create_data_normalizer
from src.scrapers.recipe_discoverer import create_recipe_discoverer
from src.utils.checkpoint import CheckpointManager, create_checkpoint_manager
from src.utils.http_client import create_http_client
from src.utils.logger import get_logger
from src.validators.data_validator import validate_recipe

logger = get_logger("gousto_scraper")


class GoustoScraper:
    """Main scraper for Gousto recipes."""

    def __init__(
        self,
        session: Session,
        checkpoint_manager: Optional[CheckpointManager] = None
    ):
        """
        Initialize Gousto scraper.

        Args:
            session: Database session
            checkpoint_manager: Optional checkpoint manager for resume capability
        """
        self.session = session
        self.checkpoint_manager = checkpoint_manager or create_checkpoint_manager()
        self.http_client = create_http_client()
        self.discoverer = create_recipe_discoverer(self.http_client)
        self.normalizer = create_data_normalizer()

        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'validation_errors': 0
        }

    def discover_recipes(self, save_to_db: bool = False) -> List[str]:
        """
        Discover all recipe URLs.

        Args:
            save_to_db: Save discovered URLs to database

        Returns:
            List of recipe URLs
        """
        logger.info("Starting recipe discovery")

        urls = self.discoverer.discover_all(
            use_sitemap=True,
            use_categories=True
        )

        logger.info(f"Discovered {len(urls)} unique recipe URLs")

        if save_to_db:
            logger.info("Saving discovered URLs would require a URL tracking table")

        return urls

    def scrape_all(
        self,
        urls: Optional[List[str]] = None,
        limit: Optional[int] = None,
        resume: bool = False
    ) -> Dict[str, int]:
        """
        Scrape all recipes.

        Args:
            urls: List of URLs to scrape (discovers if None)
            limit: Maximum number of recipes to scrape
            resume: Resume from checkpoint

        Returns:
            Statistics dictionary
        """
        if resume and self.checkpoint_manager:
            checkpoint = self.checkpoint_manager.load()
            if checkpoint:
                logger.info("Resuming from checkpoint")
                urls = checkpoint.pending_urls
                self.stats['success'] = checkpoint.success_count
                self.stats['failed'] = checkpoint.failure_count
            else:
                logger.warning("No checkpoint found, starting fresh")
                resume = False

        if not urls:
            logger.info("No URLs provided, discovering recipes")
            urls = self.discover_recipes()

        if limit:
            urls = urls[:limit]

        self.stats['total'] = len(urls)

        if config.checkpoint_enabled and not resume:
            session_id = f"scrape_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            self.checkpoint_manager.create_session(
                session_id=session_id,
                urls=urls,
                metadata={
                    'started_at': datetime.utcnow().isoformat(),
                    'limit': str(limit) if limit else 'None'
                }
            )

        logger.info(f"Starting scrape of {len(urls)} recipes")

        for i, url in enumerate(urls, start=1):
            try:
                logger.info(f"[{i}/{len(urls)}] Scraping: {url}")

                if self._recipe_exists(url):
                    logger.info(f"Recipe already exists, skipping: {url}")
                    self.stats['skipped'] += 1
                    if self.checkpoint_manager:
                        self.checkpoint_manager.mark_success(url)
                    continue

                recipe_data = self.scrape_recipe(url)

                if recipe_data:
                    saved = self._save_recipe(recipe_data)
                    if saved:
                        self.stats['success'] += 1
                        if self.checkpoint_manager:
                            self.checkpoint_manager.mark_success(url)

                        logger.recipe_scraped(
                            recipe_name=recipe_data['name'],
                            recipe_url=url,
                            ingredients_count=len(recipe_data.get('ingredients', [])),
                            instructions_count=len(recipe_data.get('instructions', []))
                        )
                    else:
                        self.stats['failed'] += 1
                        if self.checkpoint_manager:
                            self.checkpoint_manager.mark_failure(url)
                else:
                    self.stats['failed'] += 1
                    if self.checkpoint_manager:
                        self.checkpoint_manager.mark_failure(url)

            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
                self.stats['failed'] += 1
                if self.checkpoint_manager:
                    self.checkpoint_manager.mark_failure(url)

            if i % 10 == 0:
                logger.scraping_progress(
                    current=i,
                    total=len(urls),
                    success=self.stats['success'],
                    failed=self.stats['failed']
                )

        logger.info(f"Scraping complete. Stats: {self.stats}")

        if config.checkpoint_enabled and self.checkpoint_manager:
            self.checkpoint_manager.save()
            if self.checkpoint_manager.is_complete():
                logger.info("All recipes processed, clearing checkpoint")
                self.checkpoint_manager.clear()

        return self.stats

    def scrape_recipe(self, url: str) -> Optional[Dict]:
        """
        Scrape single recipe.

        Args:
            url: Recipe URL

        Returns:
            Normalized recipe data or None if failed
        """
        start_time = time.time()

        try:
            scraper = scrape_me(url, wild_mode=True)

            # Helper to safely extract optional fields
            def safe_extract(method, default=''):
                try:
                    return method()
                except (NotImplementedError, AttributeError):
                    return default

            raw_data = {
                'url': url,
                'name': scraper.title(),
                'description': safe_extract(scraper.description, ''),
                'totalTime': safe_extract(scraper.total_time, None),
                'recipeYield': safe_extract(scraper.yields, None),
                'recipeIngredient': scraper.ingredients(),
                'recipeInstructions': scraper.instructions_list(),
                'nutrition': self._extract_nutrition(scraper),
                'recipeCategory': safe_extract(scraper.category, ''),
                'recipeCuisine': safe_extract(scraper.cuisine, ''),
                'aggregateRating': self._extract_rating(scraper),
                'image': scraper.image(),
            }

            normalized_data = self.normalizer.normalize_recipe_data(raw_data)

            validation_result = validate_recipe(normalized_data)

            if not validation_result.is_valid:
                logger.error(f"Validation failed for {url}")
                self.stats['validation_errors'] += 1
                if config.validation_strict:
                    return None

            execution_time = time.time() - start_time
            normalized_data['_scraping_metadata'] = {
                'execution_time': execution_time,
                'validation_errors': len(validation_result.errors),
                'validation_warnings': len(validation_result.warnings)
            }

            return normalized_data

        except (WebsiteNotImplementedError, RecipeScrapersExceptions) as e:
            logger.recipe_error(url, "RecipeScrapersException", str(e))
            return None

        except Exception as e:
            logger.recipe_error(url, "UnexpectedException", str(e))
            logger.error(f"Full traceback for {url}:", exc_info=True)
            return None

    def _extract_nutrition(self, scraper) -> Dict:
        """Extract nutrition data from scraper."""
        nutrition = {}

        try:
            nutrients = scraper.nutrients()
            nutrition = {
                'calories': nutrients.get('calories'),
                'carbohydrateContent': nutrients.get('carbohydrateContent'),
                'proteinContent': nutrients.get('proteinContent'),
                'fatContent': nutrients.get('fatContent'),
                'fiberContent': nutrients.get('fiberContent'),
                'sugarContent': nutrients.get('sugarContent'),
                'sodiumContent': nutrients.get('sodiumContent'),
                'saturatedFatContent': nutrients.get('saturatedFatContent'),
            }
        except (NotImplementedError, AttributeError, Exception) as e:
            logger.debug(f"Failed to extract nutrition: {e}")

        return nutrition

    def _extract_rating(self, scraper) -> Optional[Dict]:
        """Extract rating data from scraper."""
        try:
            if hasattr(scraper, 'ratings'):
                rating = scraper.ratings()
                if rating:
                    return {
                        'ratingValue': rating,
                        'reviewCount': 0
                    }
        except Exception:
            pass

        return None

    def _recipe_exists(self, url: str) -> bool:
        """
        Check if recipe already exists in database.

        Args:
            url: Recipe URL

        Returns:
            True if recipe exists
        """
        slug = self._extract_slug_from_url(url)
        existing = self.session.query(Recipe).filter_by(slug=slug).first()
        return existing is not None

    def _extract_slug_from_url(self, url: str) -> str:
        """Extract slug from URL."""
        path = urlparse(url).path
        slug = path.rstrip('/').split('/')[-1]
        return slug

    def _extract_gousto_id_from_url(self, url: str) -> str:
        """Extract Gousto ID from URL."""
        slug = self._extract_slug_from_url(url)
        return f"gousto_{slug}"

    def _save_recipe(self, recipe_data: Dict) -> bool:
        """
        Save recipe to database.

        Args:
            recipe_data: Normalized recipe data

        Returns:
            True if saved successfully
        """
        try:
            slug = self._extract_slug_from_url(recipe_data['source_url'])
            gousto_id = self._extract_gousto_id_from_url(recipe_data['source_url'])

            recipe = Recipe(
                gousto_id=gousto_id,
                slug=slug,
                name=recipe_data['name'],
                description=recipe_data.get('description'),
                cooking_time_minutes=recipe_data.get('total_time_minutes'),
                servings=recipe_data.get('servings'),
                source_url=recipe_data['source_url'],
                is_active=True
            )

            self.session.add(recipe)
            self.session.flush()

            if recipe_data.get('category'):
                category = self._get_or_create_category(
                    recipe_data['category'],
                    'cuisine'
                )
                if category:
                    recipe.categories.append(category)

            if recipe_data.get('ingredients'):
                for idx, ing_data in enumerate(recipe_data['ingredients']):
                    self._add_ingredient_to_recipe(recipe, ing_data, idx)

            if recipe_data.get('instructions'):
                for inst_data in recipe_data['instructions']:
                    self._add_instruction_to_recipe(recipe, inst_data)

            if recipe_data.get('nutrition'):
                self._add_nutrition_to_recipe(recipe, recipe_data['nutrition'])

            if recipe_data.get('image_url'):
                self._add_image_to_recipe(recipe, recipe_data['image_url'])

            metadata = recipe_data.get('_scraping_metadata', {})
            history = ScrapingHistory(
                recipe_id=recipe.id,
                status='success',
                recipes_scraped=1,
                errors_encountered=metadata.get('validation_errors', 0),
                execution_time_seconds=metadata.get('execution_time', 0)
            )
            self.session.add(history)

            self.session.commit()

            logger.debug(f"Saved recipe: {recipe.name} (ID: {recipe.id})")
            return True

        except Exception as e:
            logger.error(f"Failed to save recipe: {e}", exc_info=True)
            self.session.rollback()
            return False

    def _get_or_create_category(
        self,
        name: str,
        category_type: str
    ) -> Optional[Category]:
        """Get or create category."""
        slug = name.lower().replace(' ', '-')

        category = self.session.query(Category).filter_by(slug=slug).first()

        if not category:
            category = Category(
                name=name,
                slug=slug,
                category_type=category_type
            )
            self.session.add(category)
            self.session.flush()

        return category

    def _get_or_create_ingredient(self, name: str) -> Ingredient:
        """Get or create ingredient."""
        normalized_name = name.lower().strip()

        ingredient = self.session.query(Ingredient).filter_by(
            normalized_name=normalized_name
        ).first()

        if not ingredient:
            ingredient = Ingredient(
                name=name,
                normalized_name=normalized_name
            )
            self.session.add(ingredient)
            self.session.flush()

        return ingredient

    def _get_or_create_unit(self, abbreviation: str) -> Optional[Unit]:
        """Get or create unit."""
        if not abbreviation:
            return None

        unit = self.session.query(Unit).filter_by(abbreviation=abbreviation).first()

        if not unit:
            unit_types = {
                'g': ('weight', 'gram'),
                'kg': ('weight', 'kilogram'),
                'ml': ('volume', 'milliliter'),
                'l': ('volume', 'liter'),
                'tsp': ('volume', 'teaspoon'),
                'tbsp': ('volume', 'tablespoon'),
                'cup': ('volume', 'cup'),
                'oz': ('weight', 'ounce'),
                'lb': ('weight', 'pound'),
            }

            unit_info = unit_types.get(abbreviation.lower())
            if unit_info:
                unit = Unit(
                    name=unit_info[1],
                    abbreviation=abbreviation,
                    unit_type=unit_info[0]
                )
                self.session.add(unit)
                self.session.flush()

        return unit

    def _add_ingredient_to_recipe(
        self,
        recipe: Recipe,
        ing_data: Dict,
        display_order: int
    ) -> None:
        """Add ingredient to recipe."""
        ingredient = self._get_or_create_ingredient(ing_data['name'])

        unit = None
        if ing_data.get('unit'):
            unit = self._get_or_create_unit(ing_data['unit'])

        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=ing_data.get('quantity'),
            unit_id=unit.id if unit else None,
            preparation_note=ing_data.get('preparation'),
            is_optional=ing_data.get('is_optional', False),
            display_order=display_order
        )

        self.session.add(recipe_ingredient)

    def _add_instruction_to_recipe(
        self,
        recipe: Recipe,
        inst_data: Dict
    ) -> None:
        """Add cooking instruction to recipe."""
        if isinstance(inst_data, str):
            instruction_text = inst_data
            step_number = len(recipe.cooking_instructions) + 1
            time_minutes = None
        else:
            instruction_text = inst_data.get('instruction', '')
            step_number = inst_data.get('step_number', len(recipe.cooking_instructions) + 1)
            time_minutes = inst_data.get('time_minutes')

        instruction = CookingInstruction(
            recipe_id=recipe.id,
            step_number=step_number,
            instruction=instruction_text,
            time_minutes=time_minutes
        )

        # Use relationship to ensure proper ORM behavior
        recipe.cooking_instructions.append(instruction)

    def _add_nutrition_to_recipe(
        self,
        recipe: Recipe,
        nutrition_data: Dict
    ) -> None:
        """Add nutritional information to recipe."""
        nutrition = NutritionalInfo(
            recipe_id=recipe.id,
            calories=nutrition_data.get('calories'),
            protein_g=nutrition_data.get('protein_g'),
            carbohydrates_g=nutrition_data.get('carbohydrates_g'),
            fat_g=nutrition_data.get('fat_g'),
            fiber_g=nutrition_data.get('fiber_g'),
            sugar_g=nutrition_data.get('sugar_g'),
            sodium_mg=nutrition_data.get('sodium_mg'),
            saturated_fat_g=nutrition_data.get('saturated_fat_g')
        )

        self.session.add(nutrition)

    def _add_image_to_recipe(self, recipe: Recipe, image_url: str) -> None:
        """Add image to recipe."""
        image = Image(
            recipe_id=recipe.id,
            url=image_url,
            image_type='main',
            display_order=0
        )

        self.session.add(image)

    def close(self) -> None:
        """Close connections and cleanup."""
        self.http_client.close()
        logger.info("Scraper closed")


def create_gousto_scraper(
    session: Optional[Session] = None,
    checkpoint_manager: Optional[CheckpointManager] = None
) -> GoustoScraper:
    """
    Factory function to create Gousto scraper.

    Args:
        session: Database session (creates new if None)
        checkpoint_manager: Checkpoint manager

    Returns:
        GoustoScraper instance
    """
    if session is None:
        session = next(get_db_session())

    return GoustoScraper(session, checkpoint_manager)
