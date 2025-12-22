# Database Quick Reference

## Setup (One-Time)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Initialize database
python -c "from database import init_database; init_database(seed_data=True)"
```

## Common Imports

```python
# Connection
from database import get_session, session_scope, init_database

# Models
from database import (
    Recipe, Category, Ingredient, Unit, Allergen, DietaryTag,
    RecipeIngredient, NutritionalInfo, CookingInstruction, Image
)

# Query helpers
from database import RecipeQuery
```

## Quick Operations

### Get a Session

```python
# Simple session
session = get_session()

# Context manager (auto-commit/rollback)
with session_scope() as session:
    # Your code here
    pass
```

### Query Recipes

```python
session = get_session()
query = RecipeQuery(session)

# By ID/slug
recipe = query.get_by_id(1)
recipe = query.get_by_slug('chicken-curry')

# Search
results = query.search_by_name('pasta')

# Quick recipes (under 30 min)
quick = query.get_quick_recipes(max_time=30)

# High protein
high_protein = query.get_high_protein_recipes(min_protein=30)

# Advanced filtering
filtered = query.filter_recipes(
    categories=['italian'],
    dietary_tags=['vegetarian'],
    max_cooking_time=45,
    max_calories=600
)
```

### Create Recipe

```python
from decimal import Decimal

with session_scope() as session:
    recipe = Recipe(
        gousto_id='recipe-001',
        slug='my-recipe',
        name='My Recipe',
        cooking_time_minutes=30,
        difficulty='easy',
        servings=2,
        source_url='https://example.com'
    )
    session.add(recipe)
    session.flush()  # Get recipe.id

    # Add nutrition
    nutrition = NutritionalInfo(
        recipe_id=recipe.id,
        calories=Decimal('500'),
        protein_g=Decimal('30'),
        carbohydrates_g=Decimal('50'),
        fat_g=Decimal('15')
    )
    session.add(nutrition)
```

### Update Recipe

```python
with session_scope() as session:
    recipe = query.get_by_id(1)
    recipe.cooking_time_minutes = 25
    recipe.difficulty = 'easy'
    # Auto-commits on exit
```

### Delete Recipe

```python
with session_scope() as session:
    recipe = query.get_by_id(1)

    # Hard delete (CASCADE removes related records)
    session.delete(recipe)

    # OR soft delete (preferred)
    recipe.is_active = False
```

## Common SQL Queries

### Search Recipes

```sql
-- By name
SELECT * FROM recipes
WHERE name LIKE '%chicken%' AND is_active = TRUE;

-- By cooking time
SELECT * FROM recipes
WHERE cooking_time_minutes <= 30 AND is_active = TRUE
ORDER BY cooking_time_minutes;

-- With nutrition
SELECT r.name, n.calories, n.protein_g
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE n.calories BETWEEN 300 AND 500;
```

### Filter by Tags

```sql
-- Vegan recipes
SELECT DISTINCT r.*
FROM recipes r
JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
WHERE dt.slug = 'vegan' AND r.is_active = TRUE;

-- Multiple tags (AND logic)
SELECT r.*
FROM recipes r
WHERE r.is_active = TRUE
  AND EXISTS (
    SELECT 1 FROM recipe_dietary_tags rdt
    JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
    WHERE rdt.recipe_id = r.id AND dt.slug = 'vegan'
  )
  AND EXISTS (
    SELECT 1 FROM recipe_dietary_tags rdt
    JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
    WHERE rdt.recipe_id = r.id AND dt.slug = 'gluten-free'
  );
```

### Get Recipe Details

```sql
-- Ingredients
SELECT
    i.name,
    ri.quantity,
    u.abbreviation AS unit,
    ri.preparation_note
FROM recipe_ingredients ri
JOIN ingredients i ON ri.ingredient_id = i.id
LEFT JOIN units u ON ri.unit_id = u.id
WHERE ri.recipe_id = 1
ORDER BY ri.display_order;

-- Instructions
SELECT step_number, instruction, time_minutes
FROM cooking_instructions
WHERE recipe_id = 1
ORDER BY step_number;
```

## Environment Variables

```bash
# SQLite (development)
DB_TYPE=sqlite
DB_PATH=./data/recipes.db

# PostgreSQL (production)
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost/recipes
# OR individual components
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=recipes
```

## Database Schema Cheat Sheet

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `recipes` | Main recipe data | id, gousto_id, slug, name, cooking_time, difficulty |
| `categories` | Cuisine/meal types | id, name, slug, category_type |
| `ingredients` | Ingredient master list | id, name, normalized_name |
| `units` | Measurement units | id, name, abbreviation, unit_type |
| `dietary_tags` | Vegan, keto, etc. | id, name, slug |
| `allergens` | Allergen list | id, name |
| `nutritional_info` | Per-serving nutrition | recipe_id, calories, protein_g, carbs_g, fat_g |
| `cooking_instructions` | Step-by-step | recipe_id, step_number, instruction |

### Relationship Tables

| Table | Links | Additional Columns |
|-------|-------|-------------------|
| `recipe_categories` | recipes ↔ categories | - |
| `recipe_ingredients` | recipes ↔ ingredients | quantity, unit_id, preparation_note |
| `recipe_allergens` | recipes ↔ allergens | - |
| `recipe_dietary_tags` | recipes ↔ dietary_tags | - |

## Common Filters

```python
# RecipeQuery filter_recipes() parameters:

categories=['italian', 'dinner']          # Category slugs (OR)
dietary_tags=['vegan', 'high-protein']    # Tags (AND)
exclude_allergens=['dairy', 'gluten']     # Exclude allergens
max_cooking_time=30                       # Max minutes
difficulty='easy'                         # easy/medium/hard
min_calories=300                          # Min calories
max_calories=600                          # Max calories
min_protein=20                            # Min protein (g)
max_carbs=50                              # Max carbs (g)
limit=50                                  # Max results
offset=0                                  # Pagination offset
order_by='name'                           # name/cooking_time/calories
```

## Index Reference

### Primary Indexes

```sql
-- recipes
idx_recipes_name                          -- Search by name
idx_recipes_slug                          -- Lookup by slug
idx_recipes_cooking_time                  -- Filter by time
idx_recipes_search                        -- Composite (is_active, cooking_time, difficulty)

-- nutritional_info
idx_nutrition_calories                    -- Filter by calories
idx_nutrition_ranges                      -- Composite (calories, protein, carbs)

-- ingredients
idx_ingredients_normalized                -- Case-insensitive search

-- recipe_ingredients
idx_recipe_ingredients_lookup             -- Composite (recipe_id, ingredient_id, order)
```

## Performance Tips

1. **Use composite indexes** for multi-column filters
2. **Avoid SELECT *** - specify columns
3. **Use EXPLAIN** to check query plans
4. **Batch inserts** for multiple records
5. **Use session_scope()** for auto-commit/rollback
6. **Index foreign keys** (already done)
7. **Monitor slow queries** regularly

## Troubleshooting

### Connection Issues

```python
from database import check_connection
if not check_connection():
    print("Database connection failed")
```

### View Queries

```python
# SQLite
session.execute("SELECT * FROM sqlite_master WHERE type='table'")

# PostgreSQL
session.execute("SELECT * FROM information_schema.tables WHERE table_schema='public'")
```

### Check Index Usage (PostgreSQL)

```sql
SELECT
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Reset Database

```python
from database import init_database
engine = init_database(
    database_url='sqlite:///data/recipes.db',
    drop_existing=True,  # CAUTION: Deletes all data
    seed_data=True
)
```

## Useful Snippets

### Get Recipe Count

```python
query = RecipeQuery(session)
count = query.get_recipe_count()
```

### Export Recipe Data

```python
recipe_dict = query.export_recipe_data(recipe_id=1)
# Returns complete dict with ingredients, instructions, nutrition
```

### Bulk Update

```python
session.query(Recipe).filter(
    Recipe.difficulty == 'easy'
).update({'cooking_time_minutes': Recipe.cooking_time_minutes - 5})
session.commit()
```

### Statistics

```python
# Category stats
stats = query.get_category_stats()

# Ingredient usage
top_ingredients = query.get_ingredient_usage(limit=20)
```

## Files Location

```
src/database/
├── schema.sql           # Complete DDL
├── models.py            # ORM models
├── connection.py        # Connection management
├── queries.py           # Query helpers
├── seed.py              # Reference data
└── example_usage.py     # Examples

docs/
├── DATABASE_SCHEMA.md   # Full schema docs
├── SAMPLE_QUERIES.md    # Query examples
├── INDEX_STRATEGY.md    # Index optimization
└── QUICK_REFERENCE.md   # This file

migrations/
└── 001_initial_schema.sql
```

## Documentation Links

- [Full Schema Documentation](DATABASE_SCHEMA.md)
- [100+ Sample Queries](SAMPLE_QUERIES.md)
- [Index Strategy Guide](INDEX_STRATEGY.md)
- [Module README](../src/database/README.md)
- [Implementation Summary](../DATABASE_IMPLEMENTATION_SUMMARY.md)
