# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gousto Recipe Database Scraper** - A production-ready web scraping system that extracts recipes from Gousto's cookbook website and stores them in a normalized database. The system includes recipe discovery, data extraction using schema.org JSON-LD, validation, database storage, and meal planning features.

**Technology Stack**: Python 3.10+, SQLAlchemy ORM, Click CLI, Pydantic settings, pytest

## Common Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# CLI operations
python -m src.cli init-db              # Initialize database
python -m src.cli discover --save-to-db # Find all recipe URLs
python -m src.cli scrape --limit 10    # Scrape recipes (test run)
python -m src.cli scrape --resume      # Resume interrupted scrape
python -m src.cli stats --detailed     # View statistics
python -m src.cli export --format json --output recipes.json
python -m src.cli meal-plan --with-nutrition --output meal_plans/plan.md

# Testing
pytest                                  # Run all tests with coverage
pytest tests/unit/test_data_normalizer.py -v  # Single test file
pytest -k "test_normalize" -v          # Run tests matching pattern
pytest --cov=src --cov-report=html     # Generate HTML coverage report

# Linting
black src tests                         # Format code
mypy src                                # Type checking
```

## Architecture

### Core Data Flow

```
URL Discovery (sitemap/categories) → HTTP Client (rate-limited) → recipe-scrapers library
    → Data Normalizer → Validator → SQLAlchemy ORM → SQLite/PostgreSQL
```

### Key Components

- **`src/cli.py`**: Click-based CLI interface with commands: `discover`, `scrape`, `export`, `stats`, `init-db`, `meal-plan`
- **`src/scrapers/gousto_scraper.py`**: Main orchestrator coordinating discovery, scraping, and persistence
- **`src/scrapers/recipe_discoverer.py`**: URL discovery from sitemaps and category pages
- **`src/scrapers/data_normalizer.py`**: Converts raw recipe-scrapers output to normalized format
- **`src/validators/data_validator.py`**: Schema validation against Recipe specification
- **`src/utils/http_client.py`**: Rate-limited HTTP client with retry logic and exponential backoff
- **`src/utils/checkpoint.py`**: Resume functionality for long-running scrapes
- **`src/database/models.py`**: 15-table SQLAlchemy ORM model (3NF+ normalized)
- **`src/config.py`**: Pydantic-based configuration with environment variable support

### Database Schema

15 normalized tables organized as:
- **Core entities**: `recipes`, `ingredients`, `categories`, `dietary_tags`, `allergens`, `units`
- **Junction tables**: `recipe_ingredients`, `recipe_categories`, `recipe_allergens`, `recipe_dietary_tags`
- **Details**: `cooking_instructions`, `nutritional_info`, `images`
- **Metadata**: `scraping_history`, `schema_version`

Recipe is the central entity with relationships to all other tables via SQLAlchemy ORM.

### Configuration

All settings in `src/config.py` via Pydantic, loaded from `.env`:
- `DATABASE_URL`: SQLite (dev) or PostgreSQL (prod)
- `SCRAPER_DELAY_SECONDS`: Rate limiting (default 3s)
- `CHECKPOINT_ENABLED`: Resume support for interrupted scrapes

## Testing Conventions

- Tests in `tests/unit/` and `tests/integration/`
- pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.requires_network`
- Fixtures in `tests/conftest.py` - uses in-memory SQLite
- Coverage threshold: 80% (enforced via pytest.ini)
- Mock HTTP responses with `responses` library, time with `freezegun`

## File Organization

- `.claude_plans/`: Project planning documents and completion reports
- `.claude_research/`: Technical research artifacts
- `docs/`: Schema documentation, sample queries, index strategies
- `meal_plans/`: Generated meal plan outputs
- `data/`: Database files (SQLite)
- `logs/`: Application logs
