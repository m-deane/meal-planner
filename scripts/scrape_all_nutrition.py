#!/usr/bin/env python3
"""
Batch nutrition scraper with progress tracking and checkpointing.
Run with: python scripts/scrape_all_nutrition.py
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import config
from src.scrapers.nutrition_scraper import NutritionScraper
from src.database.models import Recipe, NutritionalInfo

# Checkpoint file for resumability
CHECKPOINT_FILE = project_root / '.nutrition_scrape_checkpoint.json'
PROGRESS_FILE = project_root / '.nutrition_scrape_progress.txt'

def load_checkpoint() -> set:
    """Load completed recipe IDs from checkpoint."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('completed_ids', []))
    return set()

def save_checkpoint(completed_ids: set, stats: dict):
    """Save checkpoint with completed IDs."""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({
            'completed_ids': list(completed_ids),
            'stats': stats,
            'last_updated': datetime.now().isoformat()
        }, f)

def update_progress(msg: str):
    """Update progress file for monitoring."""
    with open(PROGRESS_FILE, 'w') as f:
        f.write(f"{datetime.now().isoformat()}\n{msg}\n")

async def run_batch_scrape():
    """Run batch nutrition scraping with checkpointing."""
    engine = create_engine(config.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Load checkpoint
        completed_ids = load_checkpoint()
        print(f"Loaded checkpoint with {len(completed_ids)} completed recipes")

        # Get all recipes needing nutrition data (NULL or 0 calories)
        all_recipes = session.query(Recipe).outerjoin(NutritionalInfo).filter(
            Recipe.is_active == True
        ).filter(
            (NutritionalInfo.calories.is_(None)) | (NutritionalInfo.calories == 0)
        ).all()

        # Filter out already completed
        recipes = [r for r in all_recipes if r.id not in completed_ids]
        total = len(recipes)

        print(f"Found {total} recipes needing nutrition data")
        update_progress(f"Starting: {total} recipes to process")

        if total == 0:
            print("All recipes already have nutrition data!")
            return

        stats = {
            'total': total,
            'success': 0,
            'failed': 0,
            'skipped': len(completed_ids)
        }

        async with NutritionScraper(session, headless=True) as scraper:
            for i, recipe in enumerate(recipes, 1):
                try:
                    success = await scraper.update_recipe_nutrition(recipe.id, recipe.source_url)

                    if success:
                        stats['success'] += 1
                        completed_ids.add(recipe.id)
                    else:
                        stats['failed'] += 1

                    # Progress update every 10 recipes
                    if i % 10 == 0 or i == total:
                        progress = f"[{i}/{total}] Success: {stats['success']}, Failed: {stats['failed']}"
                        print(progress)
                        update_progress(progress)
                        save_checkpoint(completed_ids, stats)

                    # Rate limiting (2 seconds between requests)
                    await asyncio.sleep(2)

                except Exception as e:
                    print(f"Error processing recipe {recipe.id}: {e}")
                    stats['failed'] += 1
                    continue

        # Final stats
        final_msg = f"""
========================================
Nutrition Scraping Complete!
========================================
Total processed: {stats['total']}
Success: {stats['success']}
Failed: {stats['failed']}
Success rate: {stats['success']/max(1, stats['success']+stats['failed'])*100:.1f}%
========================================
"""
        print(final_msg)
        update_progress(f"COMPLETE: Success={stats['success']}, Failed={stats['failed']}")
        save_checkpoint(completed_ids, stats)

    finally:
        session.close()

if __name__ == '__main__':
    print("=" * 50)
    print("Nutrition Data Scraper")
    print("=" * 50)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    asyncio.run(run_batch_scrape())

    print()
    print(f"Finished at: {datetime.now().isoformat()}")
