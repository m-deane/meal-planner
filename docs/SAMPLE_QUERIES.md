# Sample Database Queries

This document provides practical SQL queries and Python ORM examples for common operations.

## Table of Contents
1. [Basic Queries](#basic-queries)
2. [Advanced Filtering](#advanced-filtering)
3. [Aggregations and Statistics](#aggregations-and-statistics)
4. [Recipe Search](#recipe-search)
5. [ORM Examples (SQLAlchemy)](#orm-examples)
6. [Performance Queries](#performance-queries)

---

## Basic Queries

### Get All Active Recipes
```sql
SELECT id, name, cooking_time_minutes, difficulty
FROM recipes
WHERE is_active = TRUE
ORDER BY name;
```

### Get Recipe with All Details
```sql
SELECT
    r.*,
    n.calories,
    n.protein_g,
    n.carbohydrates_g,
    n.fat_g
FROM recipes r
LEFT JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.slug = 'chicken-tikka-masala';
```

### Get Recipe Ingredients
```sql
SELECT
    i.name AS ingredient,
    ri.quantity,
    u.abbreviation AS unit,
    ri.preparation_note
FROM recipe_ingredients ri
JOIN ingredients i ON ri.ingredient_id = i.id
LEFT JOIN units u ON ri.unit_id = u.id
WHERE ri.recipe_id = 1
ORDER BY ri.display_order;
```

### Get Cooking Instructions
```sql
SELECT
    step_number,
    instruction,
    time_minutes
FROM cooking_instructions
WHERE recipe_id = 1
ORDER BY step_number;
```

---

## Advanced Filtering

### Vegetarian Recipes Under 30 Minutes
```sql
SELECT DISTINCT r.id, r.name, r.cooking_time_minutes
FROM recipes r
JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
WHERE r.is_active = TRUE
  AND r.cooking_time_minutes <= 30
  AND dt.slug = 'vegetarian'
ORDER BY r.cooking_time_minutes;
```

### High-Protein, Low-Carb Recipes
```sql
SELECT
    r.name,
    n.calories,
    n.protein_g,
    n.carbohydrates_g,
    ROUND(n.protein_g * 4.0 / NULLIF(n.calories, 0) * 100, 1) AS protein_pct
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.is_active = TRUE
  AND n.protein_g >= 30
  AND n.carbohydrates_g <= 20
ORDER BY n.protein_g DESC;
```

### Recipes Without Specific Allergens
```sql
-- Find recipes without dairy or gluten
SELECT DISTINCT r.id, r.name
FROM recipes r
WHERE r.is_active = TRUE
  AND r.id NOT IN (
    SELECT ra.recipe_id
    FROM recipe_allergens ra
    JOIN allergens a ON ra.allergen_id = a.id
    WHERE a.name IN ('dairy', 'gluten')
  )
ORDER BY r.name;
```

### Italian Dinner Recipes
```sql
SELECT DISTINCT r.name, r.cooking_time_minutes
FROM recipes r
JOIN recipe_categories rc ON r.id = rc.recipe_id
JOIN categories c ON rc.category_id = c.id
WHERE r.is_active = TRUE
  AND c.slug IN ('italian', 'dinner')
GROUP BY r.id
HAVING COUNT(DISTINCT c.id) = 2  -- Must have BOTH categories
ORDER BY r.name;
```

### Recipes by Multiple Dietary Tags (AND logic)
```sql
-- Recipes that are BOTH vegan AND gluten-free
SELECT r.id, r.name
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
  )
ORDER BY r.name;
```

---

## Aggregations and Statistics

### Recipe Count by Category
```sql
SELECT
    c.name AS category,
    c.category_type,
    COUNT(DISTINCT r.id) AS recipe_count
FROM categories c
LEFT JOIN recipe_categories rc ON c.id = rc.category_id
LEFT JOIN recipes r ON rc.recipe_id = r.id AND r.is_active = TRUE
GROUP BY c.id, c.name, c.category_type
ORDER BY recipe_count DESC;
```

### Most Common Ingredients
```sql
SELECT
    i.name,
    COUNT(DISTINCT ri.recipe_id) AS usage_count,
    ROUND(COUNT(DISTINCT ri.recipe_id) * 100.0 / (
        SELECT COUNT(*) FROM recipes WHERE is_active = TRUE
    ), 1) AS usage_percentage
FROM ingredients i
JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
JOIN recipes r ON ri.recipe_id = r.id AND r.is_active = TRUE
GROUP BY i.id, i.name
ORDER BY usage_count DESC
LIMIT 50;
```

### Average Cooking Time by Difficulty
```sql
SELECT
    difficulty,
    COUNT(*) AS recipe_count,
    ROUND(AVG(cooking_time_minutes), 1) AS avg_cooking_time,
    MIN(cooking_time_minutes) AS min_time,
    MAX(cooking_time_minutes) AS max_time
FROM recipes
WHERE is_active = TRUE
  AND difficulty IS NOT NULL
GROUP BY difficulty
ORDER BY avg_cooking_time;
```

### Nutritional Averages by Category
```sql
SELECT
    c.name AS category,
    COUNT(DISTINCT r.id) AS recipe_count,
    ROUND(AVG(n.calories), 0) AS avg_calories,
    ROUND(AVG(n.protein_g), 1) AS avg_protein,
    ROUND(AVG(n.carbohydrates_g), 1) AS avg_carbs,
    ROUND(AVG(n.fat_g), 1) AS avg_fat
FROM categories c
JOIN recipe_categories rc ON c.id = rc.category_id
JOIN recipes r ON rc.recipe_id = r.id
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.is_active = TRUE
  AND c.category_type = 'cuisine'
GROUP BY c.id, c.name
HAVING COUNT(DISTINCT r.id) >= 5
ORDER BY avg_calories DESC;
```

### Recipes with Highest Protein-to-Calorie Ratio
```sql
SELECT
    r.name,
    n.calories,
    n.protein_g,
    ROUND(n.protein_g * 4.0 / NULLIF(n.calories, 0) * 100, 1) AS protein_calorie_pct
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.is_active = TRUE
  AND n.calories > 0
  AND n.protein_g > 0
ORDER BY protein_calorie_pct DESC
LIMIT 20;
```

---

## Recipe Search

### Search by Name (Case-Insensitive)
```sql
-- SQLite
SELECT id, name, cooking_time_minutes
FROM recipes
WHERE is_active = TRUE
  AND LOWER(name) LIKE LOWER('%chicken%')
ORDER BY name;

-- PostgreSQL (with trigram similarity)
SELECT id, name, cooking_time_minutes,
       similarity(name, 'chicken tikka') AS similarity_score
FROM recipes
WHERE is_active = TRUE
  AND name % 'chicken tikka'  -- Trigram operator
ORDER BY similarity_score DESC, name
LIMIT 20;
```

### Search by Ingredient
```sql
SELECT DISTINCT
    r.id,
    r.name,
    r.cooking_time_minutes,
    GROUP_CONCAT(DISTINCT i.name) AS matching_ingredients
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
WHERE r.is_active = TRUE
  AND i.normalized_name IN ('chicken', 'rice', 'tomato')
GROUP BY r.id
ORDER BY COUNT(DISTINCT i.id) DESC, r.name
LIMIT 20;
```

### Multi-Criteria Search
```sql
WITH filtered_recipes AS (
    SELECT DISTINCT r.id
    FROM recipes r
    JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
    JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
    JOIN nutritional_info n ON r.id = n.recipe_id
    WHERE r.is_active = TRUE
      AND r.cooking_time_minutes <= 45
      AND dt.slug IN ('vegetarian', 'high-protein')
      AND n.calories BETWEEN 300 AND 600
)
SELECT
    r.name,
    r.cooking_time_minutes,
    r.difficulty,
    n.calories,
    n.protein_g,
    GROUP_CONCAT(DISTINCT dt.name) AS dietary_tags
FROM recipes r
JOIN filtered_recipes fr ON r.id = fr.id
JOIN nutritional_info n ON r.id = n.recipe_id
LEFT JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
LEFT JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
GROUP BY r.id
ORDER BY n.protein_g DESC;
```

---

## ORM Examples (SQLAlchemy)

### Get Recipe by ID
```python
from database import get_session, Recipe

session = get_session()
recipe = session.query(Recipe).filter(Recipe.id == 1).first()

print(f"Recipe: {recipe.name}")
print(f"Cooking Time: {recipe.cooking_time_minutes} minutes")
print(f"Difficulty: {recipe.difficulty}")

# Access relationships
for ingredient in recipe.ingredients_association:
    print(f"  - {ingredient.quantity} {ingredient.unit.abbreviation} {ingredient.ingredient.name}")
```

### Search Recipes with Filters
```python
from database import get_session, Recipe, NutritionalInfo, DietaryTag
from sqlalchemy import and_

session = get_session()

# High-protein recipes under 30 minutes
recipes = session.query(Recipe).join(
    Recipe.nutritional_info
).join(
    Recipe.dietary_tags
).filter(
    and_(
        Recipe.is_active == True,
        Recipe.cooking_time_minutes <= 30,
        NutritionalInfo.protein_g >= 25,
        DietaryTag.slug == 'high-protein'
    )
).all()

for recipe in recipes:
    print(f"{recipe.name}: {recipe.nutritional_info.protein_g}g protein")
```

### Using the RecipeQuery Helper
```python
from database import get_session, RecipeQuery

session = get_session()
query = RecipeQuery(session)

# Find quick vegan recipes
recipes = query.filter_recipes(
    dietary_tags=['vegan'],
    max_cooking_time=30,
    limit=10
)

# Search by ingredient
pasta_recipes = query.get_recipes_by_ingredient(['pasta', 'tomato'])

# Get high-protein recipes
high_protein = query.get_high_protein_recipes(min_protein=30, limit=20)

# Export recipe data
recipe_data = query.export_recipe_data(recipe_id=1)
print(recipe_data)
```

### Create New Recipe
```python
from database import (
    get_session, Recipe, Ingredient, RecipeIngredient,
    Unit, NutritionalInfo, CookingInstruction
)

session = get_session()

# Create recipe
recipe = Recipe(
    gousto_id='new-recipe-001',
    slug='homemade-pasta',
    name='Homemade Pasta',
    description='Fresh handmade pasta',
    cooking_time_minutes=20,
    prep_time_minutes=30,
    difficulty='medium',
    servings=4,
    source_url='https://gousto.co.uk/recipe/homemade-pasta'
)
session.add(recipe)
session.flush()  # Get recipe.id

# Add ingredients
flour = session.query(Ingredient).filter(
    Ingredient.normalized_name == 'flour'
).first()
gram_unit = session.query(Unit).filter(Unit.abbreviation == 'g').first()

recipe_ingredient = RecipeIngredient(
    recipe_id=recipe.id,
    ingredient_id=flour.id,
    quantity=400,
    unit_id=gram_unit.id,
    display_order=1
)
session.add(recipe_ingredient)

# Add nutrition
nutrition = NutritionalInfo(
    recipe_id=recipe.id,
    calories=350,
    protein_g=12.5,
    carbohydrates_g=68.0,
    fat_g=2.5,
    fiber_g=3.0
)
session.add(nutrition)

# Add cooking instructions
step1 = CookingInstruction(
    recipe_id=recipe.id,
    step_number=1,
    instruction='Mix flour and eggs to form dough',
    time_minutes=10
)
session.add(step1)

session.commit()
```

### Bulk Operations
```python
from database import get_session, Recipe

session = get_session()

# Bulk update cooking times
session.query(Recipe).filter(
    Recipe.difficulty == 'easy'
).update({'cooking_time_minutes': Recipe.cooking_time_minutes - 5})

# Soft delete recipes
session.query(Recipe).filter(
    Recipe.date_scraped < '2020-01-01'
).update({'is_active': False})

session.commit()
```

---

## Performance Queries

### Find Recipes Missing Nutritional Data
```sql
SELECT r.id, r.name, r.gousto_id
FROM recipes r
LEFT JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.is_active = TRUE
  AND n.id IS NULL;
```

### Analyze Index Usage (PostgreSQL)
```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey';
```

### Query Execution Plan (PostgreSQL)
```sql
EXPLAIN ANALYZE
SELECT r.name, n.calories
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.cooking_time_minutes <= 30
  AND n.calories BETWEEN 300 AND 500
ORDER BY n.calories;
```

### Database Statistics
```sql
-- Table sizes
SELECT
    'recipes' AS table_name,
    COUNT(*) AS row_count,
    COUNT(*) FILTER (WHERE is_active = TRUE) AS active_count
FROM recipes
UNION ALL
SELECT 'ingredients', COUNT(*), COUNT(*) FROM ingredients
UNION ALL
SELECT 'categories', COUNT(*), COUNT(*) FROM categories;

-- Scraping success rate
SELECT
    status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM scraping_history
GROUP BY status;
```

### Identify Duplicate Ingredients
```sql
SELECT
    normalized_name,
    COUNT(*) AS duplicate_count,
    GROUP_CONCAT(name) AS variations
FROM ingredients
GROUP BY normalized_name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

---

## Complex Analytical Queries

### Recipe Similarity (Based on Shared Ingredients)
```sql
WITH recipe_ingredients_count AS (
    SELECT
        recipe_id,
        COUNT(*) AS total_ingredients
    FROM recipe_ingredients
    GROUP BY recipe_id
),
shared_ingredients AS (
    SELECT
        ri1.recipe_id AS recipe1_id,
        ri2.recipe_id AS recipe2_id,
        COUNT(DISTINCT ri1.ingredient_id) AS shared_count
    FROM recipe_ingredients ri1
    JOIN recipe_ingredients ri2
        ON ri1.ingredient_id = ri2.ingredient_id
        AND ri1.recipe_id < ri2.recipe_id
    GROUP BY ri1.recipe_id, ri2.recipe_id
)
SELECT
    r1.name AS recipe1,
    r2.name AS recipe2,
    si.shared_count,
    ROUND(
        si.shared_count * 100.0 / LEAST(ric1.total_ingredients, ric2.total_ingredients),
        1
    ) AS similarity_pct
FROM shared_ingredients si
JOIN recipes r1 ON si.recipe1_id = r1.id
JOIN recipes r2 ON si.recipe2_id = r2.id
JOIN recipe_ingredients_count ric1 ON si.recipe1_id = ric1.recipe_id
JOIN recipe_ingredients_count ric2 ON si.recipe2_id = ric2.recipe_id
WHERE r1.is_active = TRUE AND r2.is_active = TRUE
  AND si.shared_count >= 5
ORDER BY similarity_pct DESC, si.shared_count DESC
LIMIT 50;
```

### Weekly Meal Plan Generator
```sql
-- Generate balanced 7-day meal plan with variety
WITH ranked_recipes AS (
    SELECT
        r.*,
        c.category_type,
        c.slug AS category_slug,
        n.calories,
        n.protein_g,
        ROW_NUMBER() OVER (
            PARTITION BY c.slug
            ORDER BY RANDOM()
        ) AS rn
    FROM recipes r
    JOIN recipe_categories rc ON r.id = rc.recipe_id
    JOIN categories c ON rc.category_id = c.id
    JOIN nutritional_info n ON r.id = n.recipe_id
    WHERE r.is_active = TRUE
      AND r.cooking_time_minutes <= 45
      AND c.category_type = 'cuisine'
)
SELECT
    rn AS day_number,
    name AS recipe_name,
    category_slug AS cuisine,
    cooking_time_minutes,
    calories,
    protein_g
FROM ranked_recipes
WHERE rn <= 7
ORDER BY day_number;
```

---

## Export Queries

### Export Recipe to JSON Format (PostgreSQL)
```sql
SELECT json_build_object(
    'id', r.id,
    'name', r.name,
    'cooking_time', r.cooking_time_minutes,
    'ingredients', (
        SELECT json_agg(json_build_object(
            'name', i.name,
            'quantity', ri.quantity,
            'unit', u.abbreviation
        ))
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        LEFT JOIN units u ON ri.unit_id = u.id
        WHERE ri.recipe_id = r.id
        ORDER BY ri.display_order
    ),
    'instructions', (
        SELECT json_agg(json_build_object(
            'step', ci.step_number,
            'instruction', ci.instruction
        ))
        FROM cooking_instructions ci
        WHERE ci.recipe_id = r.id
        ORDER BY ci.step_number
    )
) AS recipe_json
FROM recipes r
WHERE r.id = 1;
```

### Export All Recipes to CSV Format
```sql
-- Recipe summary CSV
SELECT
    r.gousto_id,
    r.name,
    r.cooking_time_minutes,
    r.difficulty,
    n.calories,
    n.protein_g,
    GROUP_CONCAT(DISTINCT c.name) AS categories,
    GROUP_CONCAT(DISTINCT dt.name) AS dietary_tags
FROM recipes r
LEFT JOIN nutritional_info n ON r.id = n.recipe_id
LEFT JOIN recipe_categories rc ON r.id = rc.recipe_id
LEFT JOIN categories c ON rc.category_id = c.id
LEFT JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
LEFT JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
WHERE r.is_active = TRUE
GROUP BY r.id
ORDER BY r.name;
```
