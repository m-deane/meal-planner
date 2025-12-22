# Database Index Strategy

## Overview

This document outlines the indexing strategy for the recipe database, explaining the rationale behind each index and providing guidance for optimization.

## Index Design Principles

1. **Query Pattern Driven**: Indexes based on actual query patterns
2. **Selectivity First**: Index columns with high cardinality (many unique values)
3. **Composite Indexes**: Multi-column indexes for common filter combinations
4. **Balance Write Performance**: Avoid over-indexing to maintain insert/update speed
5. **Monitor and Adjust**: Regular analysis of index usage and query performance

## Primary Indexes

### recipes Table

```sql
-- Primary key (automatic index)
id (PK)

-- Unique constraints (automatic indexes)
gousto_id (UNIQUE)
slug (UNIQUE)

-- Search and filtering
CREATE INDEX idx_recipes_name ON recipes(name);
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX idx_recipes_cooking_time ON recipes(cooking_time_minutes);
CREATE INDEX idx_recipes_date_scraped ON recipes(date_scraped DESC);
CREATE INDEX idx_recipes_is_active ON recipes(is_active);

-- Composite index for common multi-filter queries
CREATE INDEX idx_recipes_search ON recipes(is_active, cooking_time_minutes, difficulty);
```

**Rationale:**
- `gousto_id` and `slug`: Unique lookups from external sources
- `name`: Text search queries (consider full-text index for PostgreSQL)
- `difficulty`: Common filter criteria (low cardinality but frequently used)
- `cooking_time_minutes`: Range queries and sorting
- `is_active`: Filter for soft-deleted records
- Composite `idx_recipes_search`: Covers common query pattern (active recipes filtered by time/difficulty)

**Query Patterns Supported:**
```sql
-- Single column
WHERE slug = 'chicken-tikka-masala'
WHERE is_active = TRUE
WHERE cooking_time_minutes <= 30

-- Multi-column (uses composite index)
WHERE is_active = TRUE AND cooking_time_minutes <= 30 AND difficulty = 'easy'
```

---

### nutritional_info Table

```sql
-- Single column indexes
CREATE INDEX idx_nutrition_calories ON nutritional_info(calories);
CREATE INDEX idx_nutrition_protein ON nutritional_info(protein_g);

-- Composite index for range filtering
CREATE INDEX idx_nutrition_ranges ON nutritional_info(calories, protein_g, carbohydrates_g);
```

**Rationale:**
- Nutritional filters are commonly used together
- Range queries benefit from sorted indexes
- Composite index enables multi-criteria nutrition searches

**Query Patterns:**
```sql
-- Calorie range
WHERE calories BETWEEN 300 AND 500

-- High-protein, low-carb
WHERE protein_g >= 30 AND carbohydrates_g <= 20

-- Multi-criteria (uses composite)
WHERE calories BETWEEN 300 AND 500 AND protein_g >= 25
```

---

### ingredients Table

```sql
CREATE INDEX idx_ingredients_normalized ON ingredients(normalized_name);
CREATE INDEX idx_ingredients_category ON ingredients(category);
CREATE INDEX idx_ingredients_allergen ON ingredients(is_allergen);
```

**Rationale:**
- `normalized_name`: Case-insensitive ingredient searches
- `category`: Filter by ingredient type
- `is_allergen`: Quick allergen checks

---

### recipe_ingredients Table

```sql
CREATE INDEX idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);

-- Composite for lookup optimization
CREATE INDEX idx_recipe_ingredients_lookup ON recipe_ingredients(recipe_id, ingredient_id, display_order);
```

**Rationale:**
- Foreign key indexes for JOIN performance
- Composite index optimizes recipe ingredient list retrieval with correct ordering

**Query Pattern:**
```sql
-- Get ingredients for recipe (uses composite)
SELECT i.name, ri.quantity, ri.display_order
FROM recipe_ingredients ri
JOIN ingredients i ON ri.ingredient_id = i.id
WHERE ri.recipe_id = 123
ORDER BY ri.display_order;
```

---

### categories Table

```sql
CREATE INDEX idx_categories_type ON categories(category_type);
CREATE INDEX idx_categories_slug ON categories(slug);
```

**Rationale:**
- `category_type`: Group by cuisine/meal_type/occasion
- `slug`: URL routing and lookups

---

### Relationship Tables

```sql
-- recipe_categories
CREATE INDEX idx_recipe_categories_category ON recipe_categories(category_id);

-- recipe_allergens
CREATE INDEX idx_recipe_allergens_allergen ON recipe_allergens(allergen_id);

-- recipe_dietary_tags
CREATE INDEX idx_recipe_dietary_tags_tag ON recipe_dietary_tags(dietary_tag_id);
```

**Rationale:**
- Primary key covers (recipe_id, X) lookups
- Additional index on second column for reverse lookups (e.g., "all recipes with tag X")

---

## PostgreSQL-Specific Optimizations

### Full-Text Search Indexes

```sql
-- Full-text search on recipe names
CREATE INDEX idx_recipes_name_fts
ON recipes USING gin(to_tsvector('english', name));

-- Full-text search on descriptions
CREATE INDEX idx_recipes_description_fts
ON recipes USING gin(to_tsvector('english', description));

-- Full-text search on ingredients
CREATE INDEX idx_ingredients_name_fts
ON ingredients USING gin(to_tsvector('english', name));
```

**Usage:**
```sql
-- Full-text search
SELECT * FROM recipes
WHERE to_tsvector('english', name) @@ to_tsquery('english', 'chicken & curry');

-- With ranking
SELECT *, ts_rank(to_tsvector('english', name), query) AS rank
FROM recipes, to_tsquery('english', 'chicken & curry') query
WHERE to_tsvector('english', name) @@ query
ORDER BY rank DESC;
```

### Trigram Indexes (Fuzzy Matching)

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Trigram index for fuzzy search
CREATE INDEX idx_recipes_name_trgm
ON recipes USING gin(name gin_trgm_ops);
```

**Usage:**
```sql
-- Similarity search
SELECT name, similarity(name, 'tikka masala') AS sim
FROM recipes
WHERE name % 'tikka masala'  -- Similarity operator
ORDER BY sim DESC;
```

### Partial Indexes

```sql
-- Index only active recipes (reduces index size)
CREATE INDEX idx_recipes_active_only
ON recipes(cooking_time_minutes, difficulty)
WHERE is_active = TRUE;
```

**Benefits:**
- Smaller index size
- Faster queries when condition matches
- Reduced maintenance overhead

---

## SQLite-Specific Considerations

### Expression Indexes

SQLite supports indexes on expressions:

```sql
-- Index on lowercase name for case-insensitive search
CREATE INDEX idx_recipes_name_lower
ON recipes(LOWER(name));
```

**Usage:**
```sql
SELECT * FROM recipes WHERE LOWER(name) LIKE LOWER('%chicken%');
```

### Covering Indexes

```sql
-- Include additional columns to avoid table lookup
CREATE INDEX idx_recipes_list
ON recipes(is_active, cooking_time_minutes, name, difficulty);
```

**Benefit:** Query can be satisfied entirely from index (index-only scan).

---

## Index Maintenance

### PostgreSQL Monitoring

```sql
-- Check index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes (candidates for removal)
SELECT
    schemaname || '.' || tablename AS table,
    indexname AS index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Index Rebuild (PostgreSQL)

```sql
-- Rebuild single index
REINDEX INDEX idx_recipes_name;

-- Rebuild all indexes on table
REINDEX TABLE recipes;

-- Rebuild all indexes in database (requires exclusive lock)
REINDEX DATABASE recipes;
```

### SQLite Optimization

```sql
-- Analyze database for query planner
ANALYZE;

-- Rebuild all indexes
REINDEX;
```

---

## Query Performance Analysis

### PostgreSQL EXPLAIN ANALYZE

```sql
-- Basic execution plan
EXPLAIN
SELECT r.name, n.calories
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.cooking_time_minutes <= 30
  AND n.calories BETWEEN 300 AND 500;

-- Detailed execution with actual timings
EXPLAIN ANALYZE
SELECT r.name, n.calories
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.cooking_time_minutes <= 30
  AND n.calories BETWEEN 300 AND 500;

-- Visual format
EXPLAIN (FORMAT JSON)
SELECT ...;
```

**Key Metrics:**
- **Seq Scan**: Full table scan (bad for large tables)
- **Index Scan**: Using index (good)
- **Index Only Scan**: Query satisfied from index alone (best)
- **Nested Loop**: JOIN method for small datasets
- **Hash Join**: JOIN method for larger datasets
- **Bitmap Index Scan**: Combined index usage

### SQLite EXPLAIN QUERY PLAN

```sql
EXPLAIN QUERY PLAN
SELECT r.name, n.calories
FROM recipes r
JOIN nutritional_info n ON r.id = n.recipe_id
WHERE r.cooking_time_minutes <= 30
  AND n.calories BETWEEN 300 AND 500;
```

**Look for:**
- `USING INDEX`: Good, index is being used
- `SCAN TABLE`: Full table scan (consider adding index)
- `SEARCH TABLE`: Using index with search condition

---

## Index Decision Checklist

Before adding a new index:

- [ ] Is this query pattern common and performance-critical?
- [ ] Does EXPLAIN show a full table scan?
- [ ] Is the column selective (high cardinality)?
- [ ] Will this index be used for JOINs, WHERE, or ORDER BY?
- [ ] Consider composite index if multiple columns are always used together
- [ ] Is write performance acceptable with additional index?
- [ ] Monitor index usage after creation

---

## Common Anti-Patterns

### Over-Indexing
**Problem:** Index on every column
**Impact:** Slow INSERT/UPDATE, wasted space
**Solution:** Index only frequently queried columns

### Redundant Indexes
**Problem:** Index on (A) and (A, B) where (A, B) covers all use cases
**Impact:** Wasted space and maintenance
**Solution:** Remove (A) if (A, B) can serve all queries

### Indexing Low-Cardinality Columns
**Problem:** Index on boolean or enum with few values
**Impact:** Poor selectivity, may not be used
**Exception:** Partial indexes or when combined in composite index

### Function Calls on Indexed Columns
**Problem:** `WHERE LOWER(name) = 'value'` doesn't use `name` index
**Solution:** Use expression index: `CREATE INDEX ON recipes(LOWER(name))`

### Ignoring NULL Handling
**Problem:** Indexes may not include NULL values (database dependent)
**Solution:** Use partial indexes or IS NOT NULL conditions

---

## Recommended Index Strategy by Query Type

### 1. Simple Lookups
**Query:** `SELECT * FROM recipes WHERE slug = 'X'`
**Index:** Single-column unique index on `slug`

### 2. Range Queries
**Query:** `SELECT * FROM recipes WHERE cooking_time BETWEEN X AND Y`
**Index:** Single-column index on `cooking_time_minutes`

### 3. Multi-Criteria Filters
**Query:** `WHERE is_active = TRUE AND cooking_time <= 30 AND difficulty = 'easy'`
**Index:** Composite index `(is_active, cooking_time_minutes, difficulty)`

### 4. JOINs
**Query:** `JOIN nutritional_info n ON r.id = n.recipe_id`
**Index:** Foreign key `recipe_id` in nutritional_info

### 5. Sorting
**Query:** `ORDER BY created_at DESC`
**Index:** Index on `created_at DESC` for reverse order

### 6. Aggregations
**Query:** `GROUP BY category_id`
**Index:** Index on `category_id`

### 7. Text Search
**Query:** `WHERE name LIKE '%chicken%'`
**Index:** Full-text index (PostgreSQL) or expression index (SQLite)

---

## Monitoring Recommendations

1. **Weekly**: Review slow query logs
2. **Monthly**: Analyze index usage statistics
3. **Quarterly**: Check for index bloat and rebuild if necessary
4. **Annually**: Full index strategy review based on query patterns

## Resources

- [PostgreSQL Index Documentation](https://www.postgresql.org/docs/current/indexes.html)
- [SQLite Index Documentation](https://www.sqlite.org/lang_createindex.html)
- [Use The Index, Luke](https://use-the-index-luke.com/) - Excellent indexing guide
