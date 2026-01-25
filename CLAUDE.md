# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gousto Meal Planner** - A full-stack meal planning application built on a recipe database scraped from Gousto's cookbook. The system includes web scraping, a REST API, and a React frontend for meal planning, nutrition tracking, and shopping list generation.

**Technology Stack**:
- Backend: Python 3.10+, FastAPI, SQLAlchemy ORM, Click CLI, Pydantic
- Frontend: React 18, TypeScript, Vite, TanStack Query, Zustand, Tailwind CSS
- Testing: pytest (backend), Vitest (frontend)

## Common Commands

```bash
# Backend Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Frontend Setup
cd frontend && npm install && cp .env.example .env

# Run Full Stack
uvicorn src.api.main:app --reload --port 8000  # API at localhost:8000
cd frontend && npm run dev                      # Frontend at localhost:3000

# CLI Operations (Scraper & Database)
python -m src.cli init-db                       # Initialize database
python -m src.cli discover --save-to-db         # Find all recipe URLs
python -m src.cli scrape --limit 10             # Scrape recipes (test run)
python -m src.cli scrape --resume               # Resume interrupted scrape
python -m src.cli stats --detailed              # View statistics
python -m src.cli export --format json --output recipes.json
python -m src.cli meal-plan --with-nutrition --output meal_plans/plan.md

# Backend Testing
pytest                                          # Run all tests with coverage
pytest tests/unit/test_data_normalizer.py -v   # Single test file
pytest -k "test_normalize" -v                   # Run tests matching pattern

# Frontend Testing
cd frontend && npm run test                     # Run tests
cd frontend && npm run test:coverage            # With coverage
cd frontend && npm run lint                     # ESLint
cd frontend && npm run type-check               # TypeScript checking

# Linting
black src tests                                 # Format Python code
mypy src                                        # Type checking

# Debug Mode
LOG_LEVEL=DEBUG python -m src.cli scrape --limit 5
```

## Architecture

### Core Data Flow

```
Scraping Pipeline:
URL Discovery (sitemap) → HTTP Client (rate-limited) → recipe-scrapers library
    → Data Normalizer → Validator → SQLAlchemy ORM → SQLite/PostgreSQL

Application Stack:
SQLite/PostgreSQL ← SQLAlchemy ORM ← FastAPI REST API ← React Frontend
```

### Backend Components (`src/`)

**API Layer (`src/api/`)**:
- `main.py`: FastAPI app with CORS, middleware, router mounting
- `routers/`: REST endpoints - recipes, meal_plans, shopping_lists, users, favorites, categories, cost
- `services/`: Business logic - recipe_service, meal_plan_service, shopping_list_service, favorites_service
- `schemas/`: Pydantic request/response models
- `middleware/`: Rate limiting, error handling, logging

**Scraper Layer (`src/scrapers/`)**:
- `gousto_scraper.py`: Main orchestrator coordinating discovery, scraping, persistence
- `recipe_discoverer.py`: URL discovery from sitemaps and category pages
- `data_normalizer.py`: Converts raw recipe-scrapers output to normalized format

**Meal Planning (`src/meal_planner/`)**:
- `planner.py`: Core meal plan generation
- `nutrition_planner.py`: Nutrition-based planning with macro targets
- `shopping_list.py`: Aggregate ingredients across meal plans
- `cost_estimator.py`: Ingredient cost estimation
- `allergen_filter.py`: Filter recipes by allergens
- `multi_week_planner.py`: Extended planning with variety scoring

**Database (`src/database/`)**:
- `models.py`: 15-table SQLAlchemy ORM model (3NF+ normalized)
- `queries.py`: Common query helpers
- `connection.py`: Session management

**Utilities (`src/utils/`)**:
- `http_client.py`: Rate-limited HTTP client with retry logic
- `checkpoint.py`: Resume functionality for long-running scrapes

### Frontend Components (`frontend/src/`)

**State Management**:
- `store/`: Zustand stores for client state
- `hooks/`: TanStack Query hooks wrapping API calls (useRecipes, useMealPlan, useFavorites, etc.)
- `api/`: Axios client and typed API functions

**Component Organization**:
- `components/recipes/`: RecipeCard, RecipeList, RecipeFilters, RecipeDetail
- `components/meal-planner/`: MealPlannerBoard, DayColumn, MealSlot, DraggableRecipe (DnD Kit)
- `components/nutrition/`: NutritionDashboard, MacroChart, WeeklyTrends (Recharts)
- `components/shopping-list/`: ShoppingList, CategorySection, ExportOptions
- `components/common/`: Button, Card, Modal, SearchBar, Pagination

**Pages**: RecipeBrowserPage, MealPlannerPage, NutritionDashboardPage, ShoppingListPage, ProfilePage

### Database Schema

15 normalized tables:
- **Core entities**: `recipes`, `ingredients`, `categories`, `dietary_tags`, `allergens`, `units`
- **Junction tables**: `recipe_ingredients`, `recipe_categories`, `recipe_allergens`, `recipe_dietary_tags`
- **Details**: `cooking_instructions`, `nutritional_info`, `images`
- **User data**: `users`, `user_preferences`, `favorites`, `meal_plans`
- **Metadata**: `scraping_history`, `schema_version`

### Configuration

Backend settings in `src/config.py` via Pydantic, loaded from `.env`:
- `DATABASE_URL`: SQLite (dev) or PostgreSQL (prod)
- `SCRAPER_DELAY_SECONDS`: Rate limiting (default 3s)
- `CHECKPOINT_ENABLED`: Resume support for interrupted scrapes

Frontend settings in `frontend/.env`:
- `VITE_API_URL`: Backend API URL (default http://localhost:8000)

## Testing Conventions

**Backend**:
- Tests in `tests/unit/` and `tests/integration/`
- pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Fixtures in `tests/conftest.py` - uses in-memory SQLite
- Coverage threshold: 80%
- Mock HTTP with `responses` library, time with `freezegun`

**Frontend**:
- Tests colocated with components (`__tests__/` folders)
- Vitest + Testing Library
- Test utilities in `src/test/`

## Workflow Guidelines

- Never use mock data, results, or workarounds - implement complete working code
- Implement tests after code changes and verify all tests pass
- Write all tests to `tests/` (backend) or colocate with components (frontend)
- Only create progress files and project plans in `.claude_plans/`
- Update `.claude_plans/projectplan.md` after completing stages
- Keep files organized - regularly clean up orphan or unneeded files

## File Boundaries

**Safe to modify**: `src/`, `frontend/src/`, `tests/`, `frontend/src/components/`

**Never modify**: `node_modules/`, `.git/`, `dist/`, `build/`, `venv/`, `.env` files

## Code Style

**Python**: snake_case variables/functions, PascalCase classes, SCREAMING_SNAKE_CASE constants

**TypeScript**: camelCase variables/functions, PascalCase classes/components, SCREAMING_SNAKE_CASE constants
