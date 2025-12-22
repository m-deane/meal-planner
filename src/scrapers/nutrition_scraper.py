"""
Nutrition data scraper using Playwright for JavaScript-rendered content.
Extracts nutrition information from Gousto recipe pages.
"""

import asyncio
import re
from typing import Dict, Optional, List
from decimal import Decimal

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from sqlalchemy.orm import Session

from src.database.models import Recipe, NutritionalInfo
from src.utils.logger import get_logger

logger = get_logger("nutrition_scraper")


class NutritionScraper:
    """Scrapes nutrition data from JavaScript-rendered Gousto pages."""

    def __init__(self, session: Session, headless: bool = True):
        """
        Initialize nutrition scraper.

        Args:
            session: Database session
            headless: Run browser in headless mode
        """
        self.session = session
        self.headless = headless
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def extract_nutrition_from_page(self, page: Page) -> Optional[Dict[str, Decimal]]:
        """
        Extract nutrition data from a loaded page.

        Args:
            page: Playwright page object

        Returns:
            Dictionary with nutrition data or None
        """
        try:
            # Wait for page to load
            await asyncio.sleep(3)

            # Try to click on nutrition section to expand it
            nutrition_selectors = [
                'text=/nutritional information/i',
                'button:has-text("Nutritional")',
                '[data-testid*="nutrition"]',
                'text=/nutrition/i >> visible=true'
            ]

            clicked = False
            for selector in nutrition_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        await elem.click()
                        await asyncio.sleep(2)
                        clicked = True
                        logger.debug(f"Clicked nutrition element: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Could not click {selector}: {e}")
                    continue

            # Get page text
            text = await page.evaluate('() => document.body.innerText')

            # Extract the nutrition table which has "per 100g" and "per serving" columns
            # We need to extract the "per serving" values (second column)

            # Split into lines for better parsing
            lines = text.split('\n')

            nutrition = {}

            # Find the nutrition table by looking for "per 100g" and "per serving" header
            table_start = -1
            for i, line in enumerate(lines):
                if 'per 100g' in line.lower() and 'per serving' in line.lower():
                    table_start = i
                    break

            if table_start == -1:
                logger.warning("Could not find nutrition table with 'per 100g' and 'per serving' columns")
                return None

            # Parse the nutrition values starting after the header
            # Format is typically: "Nutrient_Name   per100g_value   per_serving_value"
            # We want the per_serving_value (second number)

            for i in range(table_start + 1, min(table_start + 20, len(lines))):
                line = lines[i].strip()

                # Parse calories line: "143 kcal  597 kcal"
                if 'kcal' in line.lower():
                    # Extract both values
                    kcal_matches = re.findall(r'(\d+)\s*kcal', line)
                    if len(kcal_matches) >= 2:
                        nutrition['calories'] = Decimal(kcal_matches[1])  # Second value is per serving
                    elif len(kcal_matches) == 1:
                        nutrition['calories'] = Decimal(kcal_matches[0])

                # Parse fat line: "Fat   3.2 g   13.4 g"
                elif line.lower().startswith('fat'):
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['fat_g'] = Decimal(g_matches[1])  # Per serving
                    elif len(g_matches) == 1:
                        nutrition['fat_g'] = Decimal(g_matches[0])

                # Parse saturated fat line
                elif 'saturate' in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['saturated_fat_g'] = Decimal(g_matches[1])

                # Parse carbohydrate line: "Carbohydrate  18.6 g  77.5 g"
                elif 'carbohydrate' in line.lower() and 'of which' not in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['carbohydrates_g'] = Decimal(g_matches[1])  # Per serving
                    elif len(g_matches) == 1:
                        nutrition['carbohydrates_g'] = Decimal(g_matches[0])

                # Parse sugar line: "of which sugars  2.9 g  11.9 g"
                elif 'sugar' in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['sugar_g'] = Decimal(g_matches[1])

                # Parse fiber line
                elif 'fib' in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['fiber_g'] = Decimal(g_matches[1])
                    elif len(g_matches) == 1:
                        nutrition['fiber_g'] = Decimal(g_matches[0])

                # Parse protein line: "Protein  10.2 g  42.5 g"
                elif 'protein' in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['protein_g'] = Decimal(g_matches[1])  # Per serving
                    elif len(g_matches) == 1:
                        nutrition['protein_g'] = Decimal(g_matches[0])

                # Parse salt line: "Salt  1.31 g  5.45 g"
                elif 'salt' in line.lower():
                    g_matches = re.findall(r'(\d+(?:\.\d+)?)\s*g', line)
                    if len(g_matches) >= 2:
                        nutrition['sodium_mg'] = Decimal(g_matches[1]) * 1000  # Convert g to mg
                    elif len(g_matches) == 1:
                        nutrition['sodium_mg'] = Decimal(g_matches[0]) * 1000

            # Check if we got the minimum required fields
            required_fields = ['calories', 'protein_g', 'carbohydrates_g', 'fat_g']
            if all(field in nutrition for field in required_fields):
                logger.info(f"Extracted {len(nutrition)} nutrition values")
                return nutrition
            else:
                missing = [f for f in required_fields if f not in nutrition]
                logger.warning(f"Incomplete nutrition data. Missing: {missing}")
                return None

        except PlaywrightTimeout:
            logger.warning("Timeout waiting for nutrition data")
            return None
        except Exception as e:
            logger.error(f"Error extracting nutrition: {e}")
            return None

    async def scrape_recipe_nutrition(self, recipe_url: str) -> Optional[Dict[str, Decimal]]:
        """
        Scrape nutrition for a single recipe.

        Args:
            recipe_url: URL of recipe

        Returns:
            Nutrition dictionary or None
        """
        try:
            page = await self.context.new_page()
            await page.goto(recipe_url, wait_until='networkidle', timeout=30000)

            # Wait a bit for JavaScript to render
            await asyncio.sleep(2)

            nutrition = await self.extract_nutrition_from_page(page)
            await page.close()

            return nutrition

        except Exception as e:
            logger.error(f"Error scraping {recipe_url}: {e}")
            return None

    async def update_recipe_nutrition(self, recipe_id: int, recipe_url: str) -> bool:
        """
        Scrape and update nutrition for a recipe in the database.

        Args:
            recipe_id: Recipe ID
            recipe_url: Recipe URL

        Returns:
            True if successful
        """
        try:
            nutrition_data = await self.scrape_recipe_nutrition(recipe_url)

            if not nutrition_data:
                return False

            # Check if nutrition record exists
            existing = self.session.query(NutritionalInfo).filter_by(
                recipe_id=recipe_id
            ).first()

            if existing:
                # Update existing
                for key, value in nutrition_data.items():
                    setattr(existing, key, value)
            else:
                # Create new
                nutrition = NutritionalInfo(
                    recipe_id=recipe_id,
                    **nutrition_data
                )
                self.session.add(nutrition)

            self.session.commit()
            logger.info(f"Updated nutrition for recipe ID {recipe_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating nutrition for recipe ID {recipe_id}: {e}")
            self.session.rollback()
            return False

    async def batch_update_nutrition(
        self,
        limit: Optional[int] = None,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Update nutrition for multiple recipes.

        Args:
            limit: Maximum number of recipes to process
            skip_existing: Skip recipes that already have nutrition data

        Returns:
            Statistics dictionary
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        # Query recipes
        query = self.session.query(Recipe).filter(Recipe.is_active == True)

        if skip_existing:
            # Only get recipes without nutrition data
            query = query.outerjoin(NutritionalInfo).filter(
                NutritionalInfo.recipe_id.is_(None)
            )

        if limit:
            query = query.limit(limit)

        recipes = query.all()
        stats['total'] = len(recipes)

        logger.info(f"Processing {len(recipes)} recipes for nutrition data")

        for i, recipe in enumerate(recipes, 1):
            logger.info(f"[{i}/{len(recipes)}] Processing: {recipe.name}")

            success = await self.update_recipe_nutrition(recipe.id, recipe.source_url)

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

            # Rate limiting
            await asyncio.sleep(3)

            # Progress update every 10 recipes
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(recipes)} | Success: {stats['success']} | Failed: {stats['failed']}")

        logger.info(f"Nutrition scraping complete. Stats: {stats}")
        return stats


async def scrape_nutrition_for_recipes(
    session: Session,
    limit: Optional[int] = None,
    skip_existing: bool = True
) -> Dict[str, int]:
    """
    Main function to scrape nutrition data.

    Args:
        session: Database session
        limit: Maximum number of recipes to process
        skip_existing: Skip recipes with existing nutrition data

    Returns:
        Statistics dictionary
    """
    async with NutritionScraper(session) as scraper:
        stats = await scraper.batch_update_nutrition(limit, skip_existing)
        return stats


def sync_scrape_nutrition(
    session: Session,
    limit: Optional[int] = None,
    skip_existing: bool = True
) -> Dict[str, int]:
    """
    Synchronous wrapper for nutrition scraping.

    Args:
        session: Database session
        limit: Maximum number of recipes to process
        skip_existing: Skip recipes with existing nutrition data

    Returns:
        Statistics dictionary
    """
    return asyncio.run(scrape_nutrition_for_recipes(session, limit, skip_existing))
