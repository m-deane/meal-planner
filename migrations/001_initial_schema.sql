-- Migration: 001_initial_schema
-- Description: Create initial database schema for recipe storage
-- Author: Database Schema Generator
-- Date: 2024-12-20

-- ============================================================================
-- UP MIGRATION
-- ============================================================================

-- This migration creates the complete normalized schema for recipe storage
-- See schema.sql for the complete implementation

-- Execute the main schema file
-- In practice, copy the contents of src/database/schema.sql here
-- or execute it separately during migration

-- Track this migration
INSERT INTO schema_version (version, description)
VALUES ('1.0.0', 'Initial schema creation with normalized recipe structure');

-- ============================================================================
-- DOWN MIGRATION
-- ============================================================================

-- To rollback this migration, drop all tables in reverse dependency order

/*
DROP VIEW IF EXISTS vw_recipes_complete;

DROP TABLE IF EXISTS scraping_history;
DROP TABLE IF EXISTS nutritional_info;
DROP TABLE IF EXISTS cooking_instructions;
DROP TABLE IF EXISTS recipe_dietary_tags;
DROP TABLE IF EXISTS recipe_allergens;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS recipe_categories;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS dietary_tags;
DROP TABLE IF EXISTS allergens;
DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS schema_version;
*/
