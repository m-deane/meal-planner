-- ============================================================================
-- Recipe Database Schema - Normalized Design (3NF+)
-- Compatible with PostgreSQL and SQLite
-- Version: 1.0.0
-- ============================================================================

-- Enable UUID extension for PostgreSQL (no-op for SQLite)
-- For SQLite, use TEXT for UUID fields
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE ENTITIES
-- ============================================================================

-- Recipes: Main entity containing recipe metadata
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLite
    -- id SERIAL PRIMARY KEY, -- PostgreSQL alternative
    gousto_id VARCHAR(100) UNIQUE NOT NULL, -- External system ID
    slug VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    cooking_time_minutes INTEGER,
    prep_time_minutes INTEGER,
    difficulty VARCHAR(50), -- 'easy', 'medium', 'hard'
    servings INTEGER DEFAULT 2,
    source_url TEXT NOT NULL,
    date_scraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_cooking_time CHECK (cooking_time_minutes >= 0),
    CONSTRAINT chk_prep_time CHECK (prep_time_minutes >= 0),
    CONSTRAINT chk_servings CHECK (servings > 0),
    CONSTRAINT chk_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard', NULL))
);

-- Categories: Recipe classification (cuisine types, meal types)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    category_type VARCHAR(50) NOT NULL, -- 'cuisine', 'meal_type', 'occasion'
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_category_type CHECK (category_type IN ('cuisine', 'meal_type', 'occasion'))
);

-- Ingredients: Normalized ingredient master list
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    normalized_name VARCHAR(255) NOT NULL, -- Lowercase, trimmed for matching
    category VARCHAR(100), -- 'protein', 'vegetable', 'grain', 'spice', 'dairy', etc.
    is_allergen BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Units: Measurement units for ingredients
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL, -- 'g', 'ml', 'cup', 'tbsp', 'tsp', 'piece'
    abbreviation VARCHAR(20) UNIQUE NOT NULL,
    unit_type VARCHAR(50) NOT NULL, -- 'weight', 'volume', 'count'
    metric_equivalent DECIMAL(10, 4), -- Conversion to base metric unit (g or ml)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_unit_type CHECK (unit_type IN ('weight', 'volume', 'count'))
);

-- Allergens: Master allergen list
CREATE TABLE allergens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL, -- 'gluten', 'dairy', 'nuts', 'shellfish', etc.
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Dietary Tags: Vegetarian, vegan, keto, etc.
CREATE TABLE dietary_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Images: Recipe photos and images
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    image_type VARCHAR(50) DEFAULT 'main', -- 'main', 'step', 'thumbnail', 'hero'
    display_order INTEGER DEFAULT 0,
    alt_text TEXT,
    width INTEGER,
    height INTEGER,
    file_size_bytes INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_images_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT chk_display_order CHECK (display_order >= 0),
    CONSTRAINT chk_image_type CHECK (image_type IN ('main', 'step', 'thumbnail', 'hero'))
);

-- ============================================================================
-- RELATIONSHIP TABLES (Many-to-Many)
-- ============================================================================

-- Recipe-Category Relationship
CREATE TABLE recipe_categories (
    recipe_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (recipe_id, category_id),
    CONSTRAINT fk_recipe_categories_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_categories_category FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE CASCADE
);

-- Recipe-Ingredient Relationship with quantities
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity DECIMAL(10, 3),
    unit_id INTEGER,
    preparation_note TEXT, -- 'chopped', 'diced', 'minced', etc.
    is_optional BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recipe_ingredients_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_ingredients_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE RESTRICT,
    CONSTRAINT fk_recipe_ingredients_unit FOREIGN KEY (unit_id)
        REFERENCES units(id) ON DELETE RESTRICT,
    CONSTRAINT chk_quantity CHECK (quantity IS NULL OR quantity > 0),
    CONSTRAINT chk_ri_display_order CHECK (display_order >= 0)
);

-- Recipe-Allergen Relationship
CREATE TABLE recipe_allergens (
    recipe_id INTEGER NOT NULL,
    allergen_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (recipe_id, allergen_id),
    CONSTRAINT fk_recipe_allergens_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_allergens_allergen FOREIGN KEY (allergen_id)
        REFERENCES allergens(id) ON DELETE CASCADE
);

-- Recipe-Dietary Tag Relationship
CREATE TABLE recipe_dietary_tags (
    recipe_id INTEGER NOT NULL,
    dietary_tag_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (recipe_id, dietary_tag_id),
    CONSTRAINT fk_recipe_dietary_tags_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_dietary_tags_tag FOREIGN KEY (dietary_tag_id)
        REFERENCES dietary_tags(id) ON DELETE CASCADE
);

-- ============================================================================
-- RECIPE DETAILS
-- ============================================================================

-- Cooking Instructions: Step-by-step ordered sequence
CREATE TABLE cooking_instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    instruction TEXT NOT NULL,
    time_minutes INTEGER, -- Time for this specific step
    image_id INTEGER, -- Optional image for this step
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_instructions_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT fk_instructions_image FOREIGN KEY (image_id)
        REFERENCES images(id) ON DELETE SET NULL,
    CONSTRAINT chk_step_number CHECK (step_number > 0),
    CONSTRAINT chk_step_time CHECK (time_minutes IS NULL OR time_minutes >= 0),
    CONSTRAINT uq_recipe_step UNIQUE (recipe_id, step_number)
);

-- Nutritional Information: Per serving data
CREATE TABLE nutritional_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER UNIQUE NOT NULL,
    serving_size_g INTEGER,
    calories DECIMAL(10, 2),
    protein_g DECIMAL(10, 2),
    carbohydrates_g DECIMAL(10, 2),
    fat_g DECIMAL(10, 2),
    saturated_fat_g DECIMAL(10, 2),
    fiber_g DECIMAL(10, 2),
    sugar_g DECIMAL(10, 2),
    sodium_mg DECIMAL(10, 2),
    cholesterol_mg DECIMAL(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_nutrition_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT chk_calories CHECK (calories IS NULL OR calories >= 0),
    CONSTRAINT chk_protein CHECK (protein_g IS NULL OR protein_g >= 0),
    CONSTRAINT chk_carbs CHECK (carbohydrates_g IS NULL OR carbohydrates_g >= 0),
    CONSTRAINT chk_fat CHECK (fat_g IS NULL OR fat_g >= 0),
    CONSTRAINT chk_fiber CHECK (fiber_g IS NULL OR fiber_g >= 0)
);

-- ============================================================================
-- AUDIT AND METADATA
-- ============================================================================

-- Scraping History: Track scraping operations
CREATE TABLE scraping_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    scrape_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- 'success', 'failed', 'partial'
    recipes_scraped INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    error_message TEXT,
    scraper_version VARCHAR(50),
    execution_time_seconds DECIMAL(10, 3),

    CONSTRAINT fk_scraping_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(id) ON DELETE CASCADE,
    CONSTRAINT chk_status CHECK (status IN ('success', 'failed', 'partial'))
);

-- Schema Version: Migration tracking
CREATE TABLE schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version VARCHAR(50) UNIQUE NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    checksum VARCHAR(64)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Recipe indexes
CREATE INDEX idx_recipes_gousto_id ON recipes(gousto_id);
CREATE INDEX idx_recipes_slug ON recipes(slug);
CREATE INDEX idx_recipes_name ON recipes(name);
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX idx_recipes_cooking_time ON recipes(cooking_time_minutes);
CREATE INDEX idx_recipes_date_scraped ON recipes(date_scraped DESC);
CREATE INDEX idx_recipes_is_active ON recipes(is_active);

-- Category indexes
CREATE INDEX idx_categories_type ON categories(category_type);
CREATE INDEX idx_categories_slug ON categories(slug);

-- Ingredient indexes
CREATE INDEX idx_ingredients_normalized ON ingredients(normalized_name);
CREATE INDEX idx_ingredients_category ON ingredients(category);
CREATE INDEX idx_ingredients_allergen ON ingredients(is_allergen);

-- Recipe relationship indexes
CREATE INDEX idx_recipe_categories_category ON recipe_categories(category_id);
CREATE INDEX idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_allergens_allergen ON recipe_allergens(allergen_id);
CREATE INDEX idx_recipe_dietary_tags_tag ON recipe_dietary_tags(dietary_tag_id);

-- Cooking instructions indexes
CREATE INDEX idx_instructions_recipe ON cooking_instructions(recipe_id, step_number);

-- Image indexes
CREATE INDEX idx_images_recipe ON images(recipe_id);
CREATE INDEX idx_images_type ON images(image_type);

-- Nutritional info indexes
CREATE INDEX idx_nutrition_calories ON nutritional_info(calories);
CREATE INDEX idx_nutrition_protein ON nutritional_info(protein_g);

-- Scraping history indexes
CREATE INDEX idx_scraping_history_timestamp ON scraping_history(scrape_timestamp DESC);
CREATE INDEX idx_scraping_history_recipe ON scraping_history(recipe_id);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERIES
-- ============================================================================

-- Search recipes by multiple criteria
CREATE INDEX idx_recipes_search ON recipes(is_active, cooking_time_minutes, difficulty);

-- Filter by nutrition ranges
CREATE INDEX idx_nutrition_ranges ON nutritional_info(calories, protein_g, carbohydrates_g);

-- Ingredient lookup optimization
CREATE INDEX idx_recipe_ingredients_lookup ON recipe_ingredients(recipe_id, ingredient_id, display_order);

-- ============================================================================
-- INITIAL DATA SEEDS
-- ============================================================================

-- Insert common units
INSERT INTO units (name, abbreviation, unit_type, metric_equivalent) VALUES
('gram', 'g', 'weight', 1.0),
('kilogram', 'kg', 'weight', 1000.0),
('milliliter', 'ml', 'volume', 1.0),
('liter', 'l', 'volume', 1000.0),
('tablespoon', 'tbsp', 'volume', 15.0),
('teaspoon', 'tsp', 'volume', 5.0),
('cup', 'cup', 'volume', 240.0),
('piece', 'pc', 'count', NULL),
('pinch', 'pinch', 'count', NULL),
('clove', 'clove', 'count', NULL);

-- Insert common allergens
INSERT INTO allergens (name, description) VALUES
('gluten', 'Found in wheat, barley, rye'),
('dairy', 'Milk and milk-derived products'),
('eggs', 'Eggs and egg-containing products'),
('tree nuts', 'Almonds, walnuts, cashews, etc.'),
('peanuts', 'Peanuts and peanut products'),
('soy', 'Soybeans and soy products'),
('fish', 'Fish and fish products'),
('shellfish', 'Crustaceans and mollusks'),
('sesame', 'Sesame seeds and products'),
('mustard', 'Mustard seeds and products'),
('celery', 'Celery and celeriac'),
('lupin', 'Lupin beans and flour'),
('sulfites', 'Sulfur dioxide and sulphites');

-- Insert common dietary tags
INSERT INTO dietary_tags (name, slug, description) VALUES
('Vegetarian', 'vegetarian', 'No meat or fish'),
('Vegan', 'vegan', 'No animal products'),
('Gluten-Free', 'gluten-free', 'No gluten-containing ingredients'),
('Dairy-Free', 'dairy-free', 'No dairy products'),
('Low-Carb', 'low-carb', 'Reduced carbohydrate content'),
('Keto', 'keto', 'Ketogenic diet compatible'),
('Paleo', 'paleo', 'Paleolithic diet compatible'),
('Pescatarian', 'pescatarian', 'Fish but no meat'),
('Nut-Free', 'nut-free', 'No tree nuts or peanuts'),
('High-Protein', 'high-protein', 'High protein content');

-- Insert common categories
INSERT INTO categories (name, slug, category_type, description) VALUES
('Italian', 'italian', 'cuisine', 'Italian cuisine'),
('Asian', 'asian', 'cuisine', 'Asian cuisine'),
('Mexican', 'mexican', 'cuisine', 'Mexican cuisine'),
('Mediterranean', 'mediterranean', 'cuisine', 'Mediterranean cuisine'),
('Indian', 'indian', 'cuisine', 'Indian cuisine'),
('Breakfast', 'breakfast', 'meal_type', 'Morning meals'),
('Lunch', 'lunch', 'meal_type', 'Midday meals'),
('Dinner', 'dinner', 'meal_type', 'Evening meals'),
('Dessert', 'dessert', 'meal_type', 'Sweet dishes'),
('Weeknight', 'weeknight', 'occasion', 'Quick weeknight meals'),
('Weekend', 'weekend', 'occasion', 'Weekend cooking projects'),
('Party', 'party', 'occasion', 'Party and entertaining');

-- Insert schema version
INSERT INTO schema_version (version, description) VALUES
('1.0.0', 'Initial schema creation with normalized recipe structure');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete recipe view with all related data
CREATE VIEW vw_recipes_complete AS
SELECT
    r.id,
    r.gousto_id,
    r.slug,
    r.name,
    r.description,
    r.cooking_time_minutes,
    r.prep_time_minutes,
    r.difficulty,
    r.servings,
    r.source_url,
    r.date_scraped,
    r.last_updated,
    n.calories,
    n.protein_g,
    n.carbohydrates_g,
    n.fat_g,
    n.fiber_g,
    GROUP_CONCAT(DISTINCT c.name) AS categories,
    GROUP_CONCAT(DISTINCT dt.name) AS dietary_tags,
    GROUP_CONCAT(DISTINCT a.name) AS allergens
FROM recipes r
LEFT JOIN nutritional_info n ON r.id = n.recipe_id
LEFT JOIN recipe_categories rc ON r.id = rc.recipe_id
LEFT JOIN categories c ON rc.category_id = c.id
LEFT JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
LEFT JOIN dietary_tags dt ON rdt.dietary_tag_id = dt.id
LEFT JOIN recipe_allergens ra ON r.id = ra.recipe_id
LEFT JOIN allergens a ON ra.allergen_id = a.id
WHERE r.is_active = TRUE
GROUP BY r.id;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================================

-- SQLite trigger for updated_at on recipes
CREATE TRIGGER trg_recipes_updated_at
AFTER UPDATE ON recipes
FOR EACH ROW
BEGIN
    UPDATE recipes SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- SQLite trigger for updated_at on nutritional_info
CREATE TRIGGER trg_nutrition_updated_at
AFTER UPDATE ON nutritional_info
FOR EACH ROW
BEGIN
    UPDATE nutritional_info SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- PostgreSQL SPECIFIC ADDITIONS (Comment out for SQLite)
-- ============================================================================

/*
-- PostgreSQL function for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- PostgreSQL triggers
CREATE TRIGGER trg_recipes_updated_at
    BEFORE UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_nutrition_updated_at
    BEFORE UPDATE ON nutritional_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Full-text search indexes (PostgreSQL only)
CREATE INDEX idx_recipes_name_fts ON recipes USING gin(to_tsvector('english', name));
CREATE INDEX idx_recipes_description_fts ON recipes USING gin(to_tsvector('english', description));
CREATE INDEX idx_ingredients_name_fts ON ingredients USING gin(to_tsvector('english', name));

-- Partial indexes for active recipes (PostgreSQL optimization)
CREATE INDEX idx_recipes_active_only ON recipes(cooking_time_minutes, difficulty)
    WHERE is_active = TRUE;
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
