"""
Database package initialization.
Provides database connection and session management.
"""

from .models import (
    Base, Recipe, Category, Ingredient, Unit, Allergen, DietaryTag, Image,
    RecipeCategory, RecipeIngredient, RecipeAllergen, RecipeDietaryTag,
    CookingInstruction, NutritionalInfo, ScrapingHistory, SchemaVersion
)
from .connection import (
    get_engine, get_session, get_db_session, session_scope, init_database, create_tables
)
from .queries import RecipeQuery

__all__ = [
    # Models
    'Base', 'Recipe', 'Category', 'Ingredient', 'Unit', 'Allergen',
    'DietaryTag', 'Image', 'RecipeCategory', 'RecipeIngredient',
    'RecipeAllergen', 'RecipeDietaryTag', 'CookingInstruction',
    'NutritionalInfo', 'ScrapingHistory', 'SchemaVersion',
    # Connection utilities
    'get_engine', 'get_session', 'get_db_session', 'session_scope', 'init_database', 'create_tables',
    # Query helpers
    'RecipeQuery',
]
