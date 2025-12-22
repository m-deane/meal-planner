# Recipe Database Schema Documentation

## Overview

This database schema is designed for storing recipe data scraped from Gousto in a normalized structure (3NF+) that eliminates data duplication while maintaining query performance through strategic indexing.

## Database Support

- **Development**: SQLite 3.x (file-based, zero configuration)
- **Production**: PostgreSQL 12+ (recommended for concurrent access and full-text search)

## Entity Relationship Diagram

```
┌─────────────────┐
│    recipes      │◄────────┐
├─────────────────┤         │
│ id (PK)         │         │
│ gousto_id (UQ)  │         │
│ slug (UQ)       │         │
│ name            │         │
│ description     │         │
│ cooking_time    │         │
│ prep_time       │         │
│ difficulty      │         │
│ servings        │         │
│ source_url      │         │
│ date_scraped    │         │
│ last_updated    │         │
│ is_active       │         │
└────┬────────────┘         │
     │                      │
     │ 1:1                  │ 1:N
     ▼                      │
┌─────────────────┐         │
│ nutritional_    │         │
│     info        │         │
├─────────────────┤         │
│ id (PK)         │         │
│ recipe_id (FK)  │─────────┘
│ calories        │
│ protein_g       │
│ carbohydrates_g │
│ fat_g           │
│ fiber_g         │
│ ...             │
└─────────────────┘

     recipes
        │ 1:N
        ▼
┌─────────────────┐
│ cooking_        │
│ instructions    │
├─────────────────┤
│ id (PK)         │
│ recipe_id (FK)  │
│ step_number     │
│ instruction     │
│ time_minutes    │
└─────────────────┘

     recipes
        │ 1:N
        ▼
┌─────────────────┐
│    images       │
├─────────────────┤
│ id (PK)         │
│ recipe_id (FK)  │
│ url             │
│ image_type      │
│ display_order   │
│ alt_text        │
└─────────────────┘

     recipes ◄──────┐
        │ M:N       │
        ▼           │
┌─────────────────┐ │
│ recipe_         │ │
│ categories      │ │
├─────────────────┤ │
│ recipe_id (FK)  │─┘
│ category_id(FK) │─┐
└─────────────────┘ │
                    │
                    ▼
              ┌─────────────┐
              │ categories  │
              ├─────────────┤
              │ id (PK)     │
              │ name        │
              │ slug        │
              │ type        │
              └─────────────┘

     recipes ◄──────┐
        │ M:N       │
        ▼           │
┌─────────────────┐ │
│ recipe_         │ │
│ ingredients     │ │
├─────────────────┤ │
│ id (PK)         │ │
│ recipe_id (FK)  │─┘
│ ingredient_id   │─┐
│ quantity        │ │
│ unit_id (FK)    │─┼─┐
│ preparation     │ │ │
│ is_optional     │ │ │
│ display_order   │ │ │
└─────────────────┘ │ │
                    │ │
                    ▼ │
              ┌─────────────┐
              │ ingredients │
              ├─────────────┤
              │ id (PK)     │
              │ name        │
              │ normalized  │
              │ category    │
              └─────────────┘
                              │
                              ▼
                        ┌─────────┐
                        │  units  │
                        ├─────────┤
                        │ id (PK) │
                        │ name    │
                        │ abbr    │
                        │ type    │
                        └─────────┘

     recipes ◄──────┐
        │ M:N       │
        ▼           │
┌─────────────────┐ │
│ recipe_         │ │
│ dietary_tags    │ │
├─────────────────┤ │
│ recipe_id (FK)  │─┘
│ tag_id (FK)     │─┐
└─────────────────┘ │
                    ▼
              ┌──────────────┐
              │dietary_tags  │
              ├──────────────┤
              │ id (PK)      │
              │ name         │
              │ slug         │
              └──────────────┘

     recipes ◄──────┐
        │ M:N       │
        ▼           │
┌─────────────────┐ │
│ recipe_         │ │
│ allergens       │ │
├─────────────────┤ │
│ recipe_id (FK)  │─┘
│ allergen_id(FK) │─┐
└─────────────────┘ │
                    ▼
              ┌─────────────┐
              │  allergens  │
              ├─────────────┤
              │ id (PK)     │
              │ name        │
              │ description │
              └─────────────┘
```

## Core Tables

### recipes
Main entity containing recipe metadata.

**Columns:**
- `id`: Primary key (auto-increment)
- `gousto_id`: External Gousto system ID (unique, indexed)
- `slug`: URL-friendly identifier (unique, indexed)
- `name`: Recipe name (indexed for search)
- `description`: Full recipe description
- `cooking_time_minutes`: Active cooking time
- `prep_time_minutes`: Preparation time
- `difficulty`: Enum ('easy', 'medium', 'hard')
- `servings`: Number of servings (default: 2)
- `source_url`: Original Gousto URL
- `date_scraped`: When recipe was first scraped
- `last_updated`: Last modification timestamp
- `is_active`: Soft delete flag
- `created_at`: Record creation timestamp

**Constraints:**
- cooking_time >= 0
- prep_time >= 0
- servings > 0

**Indexes:**
- Single: gousto_id, slug, name, difficulty, cooking_time_minutes, is_active
- Composite: (is_active, cooking_time_minutes, difficulty)

---

### categories
Recipe classification by cuisine, meal type, or occasion.

**Columns:**
- `id`: Primary key
- `name`: Category name (unique)
- `slug`: URL-friendly identifier (unique, indexed)
- `category_type`: Enum ('cuisine', 'meal_type', 'occasion')
- `description`: Category description

**Examples:**
- Cuisine: Italian, Thai, Mexican
- Meal Type: Breakfast, Dinner, Dessert
- Occasion: Weeknight, Party, Meal Prep

---

### ingredients
Normalized master list of ingredients to avoid duplication.

**Columns:**
- `id`: Primary key
- `name`: Ingredient name (unique)
- `normalized_name`: Lowercase, trimmed version (indexed)
- `category`: Ingredient type (protein, vegetable, grain, etc.)
- `is_allergen`: Quick allergen flag

**Purpose**: Single source of truth for ingredients across all recipes.

---

### units
Measurement units for ingredient quantities.

**Columns:**
- `id`: Primary key
- `name`: Full unit name (unique)
- `abbreviation`: Short form (unique)
- `unit_type`: Enum ('weight', 'volume', 'count')
- `metric_equivalent`: Conversion factor to grams or ml

**Examples:**
- Weight: gram (g), kilogram (kg), ounce (oz)
- Volume: milliliter (ml), cup, tablespoon (tbsp)
- Count: piece, clove, pinch

---

### allergens
Master allergen list for filtering and warnings.

**Columns:**
- `id`: Primary key
- `name`: Allergen name (unique)
- `description`: Detailed description

**Common Values**: gluten, dairy, eggs, tree nuts, peanuts, soy, fish, shellfish

---

### dietary_tags
Dietary classifications and restrictions.

**Columns:**
- `id`: Primary key
- `name`: Display name (unique)
- `slug`: URL-friendly identifier (unique)
- `description`: Tag description

**Examples**: Vegetarian, Vegan, Gluten-Free, Keto, Paleo, High-Protein

---

### nutritional_info
Nutritional data per serving (1:1 with recipes).

**Columns:**
- `id`: Primary key
- `recipe_id`: Foreign key to recipes (unique)
- `serving_size_g`: Serving size in grams
- `calories`: Calories per serving
- `protein_g`: Protein in grams
- `carbohydrates_g`: Carbs in grams
- `fat_g`: Total fat in grams
- `saturated_fat_g`: Saturated fat
- `fiber_g`: Dietary fiber
- `sugar_g`: Sugar content
- `sodium_mg`: Sodium in milligrams
- `cholesterol_mg`: Cholesterol

**Indexes:**
- Single: calories, protein_g
- Composite: (calories, protein_g, carbohydrates_g)

---

### cooking_instructions
Ordered step-by-step instructions.

**Columns:**
- `id`: Primary key
- `recipe_id`: Foreign key to recipes
- `step_number`: Order of step (must be unique per recipe)
- `instruction`: Step text
- `time_minutes`: Time for this specific step
- `image_id`: Optional reference to step image

**Constraints:**
- Unique (recipe_id, step_number)

---

### images
Recipe photos and media.

**Columns:**
- `id`: Primary key
- `recipe_id`: Foreign key to recipes
- `url`: Image URL
- `image_type`: Enum ('main', 'step', 'thumbnail', 'hero')
- `display_order`: Sort order
- `alt_text`: Accessibility text
- `width`, `height`: Dimensions in pixels
- `file_size_bytes`: File size

---

## Relationship Tables (Many-to-Many)

### recipe_categories
Links recipes to categories (many-to-many).

**Primary Key**: (recipe_id, category_id)

---

### recipe_ingredients
Links recipes to ingredients with quantity details.

**Columns:**
- `id`: Primary key
- `recipe_id`, `ingredient_id`: Foreign keys
- `quantity`: Amount (decimal)
- `unit_id`: Foreign key to units
- `preparation_note`: e.g., "chopped", "diced"
- `is_optional`: Boolean flag
- `display_order`: Presentation order

**Index**: (recipe_id, ingredient_id, display_order)

---

### recipe_allergens
Links recipes to allergens (many-to-many).

**Primary Key**: (recipe_id, allergen_id)

---

### recipe_dietary_tags
Links recipes to dietary tags (many-to-many).

**Primary Key**: (recipe_id, dietary_tag_id)

---

## Audit Tables

### scraping_history
Tracks scraping operations for debugging and monitoring.

**Columns:**
- `id`: Primary key
- `recipe_id`: Foreign key to recipes
- `scrape_timestamp`: When scrape occurred
- `status`: Enum ('success', 'failed', 'partial')
- `recipes_scraped`: Count of recipes
- `errors_encountered`: Error count
- `error_message`: Detailed error
- `scraper_version`: Version tag
- `execution_time_seconds`: Performance metric

---

### schema_version
Migration tracking table.

**Columns:**
- `id`: Primary key
- `version`: Version string (unique)
- `applied_at`: Migration timestamp
- `description`: Change description
- `checksum`: Migration file hash

---

## Index Strategy

### Search Optimization
- Full-text indexes on recipe name and description (PostgreSQL)
- Normalized ingredient names for case-insensitive matching
- Composite indexes for common filter combinations

### Common Query Patterns

**1. Search by Name**
```sql
SELECT * FROM recipes
WHERE is_active = TRUE AND name LIKE '%pasta%';
-- Uses: idx_recipes_name
```

**2. Filter by Multiple Criteria**
```sql
SELECT r.* FROM recipes r
JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
WHERE r.cooking_time_minutes <= 30
  AND dt.slug = 'vegetarian'
  AND r.is_active = TRUE;
-- Uses: idx_recipes_search, idx_recipe_dietary_tags_tag
```

**3. Nutrition Range Queries**
```sql
SELECT r.* FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE n.calories BETWEEN 300 AND 500
  AND n.protein_g >= 25;
-- Uses: idx_nutrition_ranges
```

**4. Find by Ingredient**
```sql
SELECT DISTINCT r.* FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
WHERE i.normalized_name LIKE '%chicken%';
-- Uses: idx_ingredients_normalized, idx_recipe_ingredients_ingredient
```

---

## Data Normalization

### 3NF Compliance

**1NF**: All columns contain atomic values (no arrays or nested structures)

**2NF**: No partial dependencies on composite keys

**3NF**: No transitive dependencies
- Ingredient details stored in separate `ingredients` table
- Unit definitions in separate `units` table
- Categories, tags, allergens in dedicated tables

### Denormalization Considerations

**View: vw_recipes_complete**
Denormalized view for read-heavy operations, joining all related data.

---

## Migration Strategy

### Version Control
All schema changes tracked in `schema_version` table.

### Migration Files
Located in `/migrations/` directory:
```
migrations/
├── 001_initial_schema.sql
├── 002_add_nutrition_table.sql
└── 003_add_fulltext_indexes.sql
```

### Best Practices
1. Always include UP and DOWN migrations
2. Test migrations on copy of production data
3. Backup database before applying
4. Include version in migration filename
5. Document breaking changes

---

## Performance Tuning

### PostgreSQL Specific

**Enable Extensions:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- UUID generation
```

**Full-Text Search:**
```sql
CREATE INDEX idx_recipes_name_fts
ON recipes USING gin(to_tsvector('english', name));
```

**Partial Indexes:**
```sql
CREATE INDEX idx_recipes_active_only
ON recipes(cooking_time_minutes, difficulty)
WHERE is_active = TRUE;
```

### SQLite Specific

**Enable Foreign Keys:**
```sql
PRAGMA foreign_keys = ON;
```

**Analyze Tables:**
```sql
ANALYZE;
```

---

## Backup and Recovery

### SQLite
```bash
# Backup
sqlite3 recipes.db ".backup recipes_backup.db"

# Export to SQL
sqlite3 recipes.db .dump > backup.sql
```

### PostgreSQL
```bash
# Full backup
pg_dump -U postgres recipes > backup.sql

# Restore
psql -U postgres recipes < backup.sql
```

---

## Security Considerations

1. **SQL Injection Prevention**: Use parameterized queries via SQLAlchemy ORM
2. **Access Control**: Limit database user permissions to necessary operations only
3. **Sensitive Data**: Never store API keys or credentials in database
4. **Connection Strings**: Use environment variables for database URLs
5. **Audit Logging**: Track all scraping operations in `scraping_history`

---

## Future Enhancements

### Potential Additions
1. User accounts and saved recipes
2. Recipe ratings and reviews
3. Shopping list generation
4. Meal planning tables
5. Ingredient substitution suggestions
6. Cost tracking per recipe
7. Seasonal availability flags
8. Equipment requirements table

### Scalability Considerations
1. Partition large tables by date_scraped
2. Archive old scraping_history records
3. Implement read replicas for heavy query loads
4. Consider materialized views for analytics
5. Add caching layer (Redis) for frequently accessed recipes
