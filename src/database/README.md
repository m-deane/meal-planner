# Recipe Database Module

A production-ready, normalized database schema for storing recipe data from Gousto with SQLAlchemy ORM support.

## Features

- Normalized schema (3NF+) to eliminate data duplication
- Support for SQLite (development) and PostgreSQL (production)
- Comprehensive relationship modeling (many-to-many)
- Strategic indexing for query performance
- Full SQLAlchemy ORM with type hints
- Migration support via schema versioning
- Pre-seeded reference data (units, allergens, dietary tags)
- Advanced query helpers and filtering
- Complete audit trail for scraping operations

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your database configuration
```

### Initialize Database

```python
from database import init_database

# SQLite (development)
engine = init_database(
    database_url='sqlite:///data/recipes.db',
    drop_existing=False,
    seed_data=True
)

# PostgreSQL (production)
engine = init_database(
    database_url='postgresql://user:password@localhost/recipes',
    drop_existing=False,
    seed_data=True
)
```

### Basic Usage

```python
from database import get_session, Recipe, RecipeQuery

# Get a session
session = get_session()

# Query using ORM
recipe = session.query(Recipe).filter(Recipe.slug == 'chicken-curry').first()
print(f"Recipe: {recipe.name}")
print(f"Time: {recipe.cooking_time_minutes} minutes")

# Use query helpers
query = RecipeQuery(session)
quick_recipes = query.get_quick_recipes(max_time=30)
high_protein = query.get_high_protein_recipes(min_protein=30)

# Advanced filtering
vegan_recipes = query.filter_recipes(
    dietary_tags=['vegan'],
    max_cooking_time=30,
    max_calories=500
)

# Export recipe data
recipe_data = query.export_recipe_data(recipe_id=1)
```

## Database Schema

### Core Tables

- **recipes**: Main recipe entity with metadata
- **categories**: Cuisine types, meal types, occasions
- **ingredients**: Normalized ingredient master list
- **units**: Measurement units (g, ml, cups, etc.)
- **allergens**: Allergen master list
- **dietary_tags**: Dietary classifications (vegan, keto, etc.)
- **nutritional_info**: Nutritional data per serving
- **cooking_instructions**: Step-by-step instructions
- **images**: Recipe photos and media

### Relationship Tables

- **recipe_categories**: Many-to-many recipe↔category
- **recipe_ingredients**: Many-to-many recipe↔ingredient with quantities
- **recipe_allergens**: Many-to-many recipe↔allergen
- **recipe_dietary_tags**: Many-to-many recipe↔dietary tag

### Audit Tables

- **scraping_history**: Track scraping operations
- **schema_version**: Migration tracking

## API Reference

### Connection Management

```python
from database import get_engine, get_session, session_scope

# Get engine
engine = get_engine(database_url='sqlite:///recipes.db')

# Get session
session = get_session(engine)

# Context manager (auto-commit/rollback)
with session_scope() as session:
    recipe = session.query(Recipe).first()
    # Session automatically commits on success or rolls back on error
```

### Models

All models inherit from SQLAlchemy's declarative base:

```python
from database import Recipe, Ingredient, Category, NutritionalInfo

# Create new recipe
recipe = Recipe(
    gousto_id='recipe-123',
    slug='chicken-curry',
    name='Chicken Curry',
    cooking_time_minutes=30,
    difficulty='easy',
    servings=2
)
session.add(recipe)
session.commit()

# Access relationships
for ingredient in recipe.ingredients_association:
    print(f"{ingredient.quantity} {ingredient.unit.name} {ingredient.ingredient.name}")

# Computed properties
total_time = recipe.total_time_minutes  # prep + cooking
macro_ratio = recipe.nutritional_info.macros_ratio  # protein/carbs/fat %
```

### Query Helpers

```python
from database import RecipeQuery

query = RecipeQuery(session)

# Get by ID or slug
recipe = query.get_by_id(1)
recipe = query.get_by_slug('chicken-curry')
recipe = query.get_by_gousto_id('gousto-123')

# Search
results = query.search_by_name('chicken', limit=10)

# Filter by multiple criteria
results = query.filter_recipes(
    categories=['italian', 'dinner'],
    dietary_tags=['vegetarian'],
    exclude_allergens=['dairy', 'gluten'],
    max_cooking_time=45,
    difficulty='easy',
    min_calories=300,
    max_calories=600,
    min_protein=20,
    order_by='calories',
    limit=50
)

# Specialized queries
quick_recipes = query.get_quick_recipes(max_time=30)
high_protein = query.get_high_protein_recipes(min_protein=30)
low_carb = query.get_low_carb_recipes(max_carbs=20)

# Find by ingredients
pasta_recipes = query.get_recipes_by_ingredient(
    ['pasta', 'tomato'],
    match_all=False  # OR logic
)

# Statistics
count = query.get_recipe_count()
category_stats = query.get_category_stats()
ingredient_usage = query.get_ingredient_usage(limit=50)

# Export
recipe_dict = query.export_recipe_data(recipe_id=1)
```

## Database Operations

### Create Recipe

```python
from decimal import Decimal
from database import (
    Recipe, Ingredient, RecipeIngredient, Unit,
    NutritionalInfo, CookingInstruction, Category
)

with session_scope() as session:
    # Create recipe
    recipe = Recipe(
        gousto_id='new-001',
        slug='pasta-carbonara',
        name='Pasta Carbonara',
        cooking_time_minutes=20,
        prep_time_minutes=10,
        difficulty='medium',
        servings=2,
        source_url='https://gousto.co.uk/recipe'
    )
    session.add(recipe)
    session.flush()  # Get recipe.id

    # Add ingredient
    pasta = session.query(Ingredient).filter(
        Ingredient.normalized_name == 'pasta'
    ).first()
    gram = session.query(Unit).filter(Unit.abbreviation == 'g').first()

    recipe_ing = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_id=pasta.id,
        quantity=Decimal('200'),
        unit_id=gram.id,
        display_order=1
    )
    session.add(recipe_ing)

    # Add nutrition
    nutrition = NutritionalInfo(
        recipe_id=recipe.id,
        calories=Decimal('650'),
        protein_g=Decimal('25'),
        carbohydrates_g=Decimal('75'),
        fat_g=Decimal('28')
    )
    session.add(nutrition)

    # Add instructions
    step = CookingInstruction(
        recipe_id=recipe.id,
        step_number=1,
        instruction='Boil pasta according to package directions',
        time_minutes=10
    )
    session.add(step)
```

### Update Recipe

```python
with session_scope() as session:
    recipe = session.query(Recipe).filter(Recipe.id == 1).first()
    recipe.cooking_time_minutes = 25
    recipe.difficulty = 'easy'
    # Automatically commits on context exit
```

### Delete Recipe

```python
with session_scope() as session:
    recipe = session.query(Recipe).filter(Recipe.id == 1).first()
    session.delete(recipe)  # CASCADE deletes related records
    # or soft delete:
    recipe.is_active = False
```

## Query Examples

### Find Vegan Recipes Under 30 Minutes

```python
query = RecipeQuery(session)
recipes = query.filter_recipes(
    dietary_tags=['vegan'],
    max_cooking_time=30,
    order_by='cooking_time'
)
```

### High-Protein, Low-Carb Recipes

```python
recipes = query.filter_recipes(
    min_protein=30,
    max_carbs=20,
    order_by='protein'
)
```

### Recipes Without Allergens

```python
recipes = query.filter_recipes(
    exclude_allergens=['dairy', 'gluten', 'nuts']
)
```

### Italian Dinner Recipes

```python
recipes = query.filter_recipes(
    categories=['italian', 'dinner']
)
```

### Complex Multi-Criteria Search

```python
recipes = query.filter_recipes(
    categories=['mediterranean'],
    dietary_tags=['vegetarian', 'high-protein'],
    max_cooking_time=45,
    max_calories=600,
    exclude_allergens=['nuts'],
    order_by='calories',
    limit=20
)
```

## Performance Optimization

### Index Usage

The schema includes strategic indexes for common queries:

- Single-column: `name`, `slug`, `cooking_time`, `calories`
- Composite: `(is_active, cooking_time, difficulty)`
- Full-text (PostgreSQL): `name`, `description`, `ingredients`

### Query Performance

```python
# Use EXPLAIN to analyze queries
from sqlalchemy import text

result = session.execute(text("""
    EXPLAIN ANALYZE
    SELECT * FROM recipes
    WHERE cooking_time_minutes <= 30
    AND is_active = TRUE
"""))
print(result.fetchall())
```

### Batch Operations

```python
# Bulk insert
recipes = [
    Recipe(gousto_id=f'recipe-{i}', slug=f'slug-{i}', name=f'Recipe {i}')
    for i in range(1000)
]
session.bulk_save_objects(recipes)
session.commit()

# Bulk update
session.query(Recipe).filter(
    Recipe.difficulty == 'easy'
).update({'cooking_time_minutes': Recipe.cooking_time_minutes - 5})
session.commit()
```

## Testing

### Run Example Usage

```bash
cd src/database
python example_usage.py
```

### Unit Tests

```python
import pytest
from database import init_database, Recipe, session_scope

@pytest.fixture
def db_session():
    engine = init_database('sqlite:///:memory:', seed_data=True)
    with session_scope(engine) as session:
        yield session

def test_create_recipe(db_session):
    recipe = Recipe(
        gousto_id='test-001',
        slug='test-recipe',
        name='Test Recipe',
        cooking_time_minutes=20,
        servings=2,
        source_url='http://test.com'
    )
    db_session.add(recipe)
    db_session.commit()

    assert recipe.id is not None
    assert recipe.name == 'Test Recipe'
```

## Migration Management

### Schema Versions

Track schema changes in `schema_version` table:

```python
from database import SchemaVersion

with session_scope() as session:
    version = SchemaVersion(
        version='1.1.0',
        description='Add recipe rating table',
        checksum='abc123...'
    )
    session.add(version)
```

### Apply Migration

```bash
# Execute SQL migration file
sqlite3 data/recipes.db < migrations/002_add_ratings.sql

# Or for PostgreSQL
psql -U postgres recipes < migrations/002_add_ratings.sql
```

## Production Deployment

### PostgreSQL Setup

```bash
# Create database
createdb recipes

# Create user
createuser -P recipe_user

# Grant permissions
psql recipes
GRANT ALL PRIVILEGES ON DATABASE recipes TO recipe_user;
```

### Environment Variables

```bash
export DATABASE_URL="postgresql://recipe_user:password@localhost/recipes"
export DB_TYPE="postgresql"
```

### Connection Pooling

```python
# Configured automatically in get_engine()
engine = get_engine()  # pool_size=10, max_overflow=20
```

### Backup

```bash
# PostgreSQL
pg_dump -U recipe_user recipes > backup.sql

# SQLite
sqlite3 data/recipes.db ".backup data/backup.db"
```

## Troubleshooting

### Foreign Key Violations

```python
# Ensure foreign keys are enabled (SQLite)
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### Slow Queries

1. Check EXPLAIN plan
2. Verify indexes are being used
3. Consider adding composite indexes
4. Review query patterns and adjust schema

### Connection Issues

```python
from database import check_connection

if not check_connection():
    print("Database connection failed!")
```

## Documentation

- [Database Schema](../../docs/DATABASE_SCHEMA.md) - Complete schema documentation
- [Sample Queries](../../docs/SAMPLE_QUERIES.md) - SQL and ORM examples
- [Index Strategy](../../docs/INDEX_STRATEGY.md) - Index design and optimization

## License

This database schema is part of the Recipe Scraper project.
