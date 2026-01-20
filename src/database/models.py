"""
SQLAlchemy ORM Models for Recipe Database
Supports both SQLite (development) and PostgreSQL (production)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Enum, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint, Index, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

Base = declarative_base()


# ============================================================================
# CORE ENTITIES
# ============================================================================

class Recipe(Base):
    """Main recipe entity with metadata and relationships."""

    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gousto_id = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    cooking_time_minutes = Column(Integer, CheckConstraint('cooking_time_minutes >= 0'))
    prep_time_minutes = Column(Integer, CheckConstraint('prep_time_minutes >= 0'))
    difficulty = Column(
        String(50),
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard') OR difficulty IS NULL")
    )
    servings = Column(Integer, CheckConstraint('servings > 0'), default=2)
    source_url = Column(Text, nullable=False)
    date_scraped = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    categories = relationship(
        'Category',
        secondary='recipe_categories',
        back_populates='recipes',
        lazy='selectin'
    )
    ingredients_association = relationship(
        'RecipeIngredient',
        back_populates='recipe',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    allergens = relationship(
        'Allergen',
        secondary='recipe_allergens',
        back_populates='recipes',
        lazy='selectin'
    )
    dietary_tags = relationship(
        'DietaryTag',
        secondary='recipe_dietary_tags',
        back_populates='recipes',
        lazy='selectin'
    )
    cooking_instructions = relationship(
        'CookingInstruction',
        back_populates='recipe',
        cascade='all, delete-orphan',
        order_by='CookingInstruction.step_number',
        lazy='selectin'
    )
    nutritional_info = relationship(
        'NutritionalInfo',
        back_populates='recipe',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    images = relationship(
        'Image',
        back_populates='recipe',
        cascade='all, delete-orphan',
        order_by='Image.display_order',
        lazy='selectin'
    )
    scraping_history = relationship(
        'ScrapingHistory',
        back_populates='recipe',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    favorited_by = relationship(
        'FavoriteRecipe',
        back_populates='recipe',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    # Indexes
    __table_args__ = (
        Index('idx_recipes_search', 'is_active', 'cooking_time_minutes', 'difficulty'),
    )

    @property
    def total_time_minutes(self) -> Optional[int]:
        """Calculate total cooking time."""
        if self.cooking_time_minutes and self.prep_time_minutes:
            return self.cooking_time_minutes + self.prep_time_minutes
        return self.cooking_time_minutes or self.prep_time_minutes

    @property
    def ingredients(self) -> List['Ingredient']:
        """Get list of ingredients (without association details)."""
        return [ri.ingredient for ri in self.ingredients_association]

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, name='{self.name}', gousto_id='{self.gousto_id}')>"


class Category(Base):
    """Recipe categories: cuisine types, meal types, occasions."""

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    category_type = Column(
        String(50),
        CheckConstraint("category_type IN ('cuisine', 'meal_type', 'occasion')"),
        nullable=False,
        index=True
    )
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipes = relationship(
        'Recipe',
        secondary='recipe_categories',
        back_populates='categories'
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', type='{self.category_type}')>"


class Ingredient(Base):
    """Normalized ingredient master list."""

    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), index=True)  # protein, vegetable, grain, etc.
    is_allergen = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipe_associations = relationship(
        'RecipeIngredient',
        back_populates='ingredient',
        lazy='dynamic'
    )

    @validates('name')
    def normalize_name(self, key, value):
        """Auto-populate normalized_name when name is set."""
        self.normalized_name = value.lower().strip()
        return value

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name='{self.name}')>"


class Unit(Base):
    """Measurement units for ingredients."""

    __tablename__ = 'units'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    abbreviation = Column(String(20), unique=True, nullable=False)
    unit_type = Column(
        String(50),
        CheckConstraint("unit_type IN ('weight', 'volume', 'count')"),
        nullable=False
    )
    metric_equivalent = Column(Numeric(10, 4))  # Conversion to grams or ml
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipe_ingredients = relationship('RecipeIngredient', back_populates='unit')

    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, name='{self.name}', abbr='{self.abbreviation}')>"


class Allergen(Base):
    """Master allergen list."""

    __tablename__ = 'allergens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipes = relationship(
        'Recipe',
        secondary='recipe_allergens',
        back_populates='allergens'
    )

    def __repr__(self) -> str:
        return f"<Allergen(id={self.id}, name='{self.name}')>"


class DietaryTag(Base):
    """Dietary classifications: vegan, vegetarian, keto, etc."""

    __tablename__ = 'dietary_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipes = relationship(
        'Recipe',
        secondary='recipe_dietary_tags',
        back_populates='dietary_tags'
    )

    def __repr__(self) -> str:
        return f"<DietaryTag(id={self.id}, name='{self.name}')>"


class Image(Base):
    """Recipe images and photos."""

    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True)
    url = Column(Text, nullable=False)
    image_type = Column(
        String(50),
        CheckConstraint("image_type IN ('main', 'step', 'thumbnail', 'hero')"),
        default='main',
        index=True
    )
    display_order = Column(Integer, CheckConstraint('display_order >= 0'), default=0)
    alt_text = Column(Text)
    width = Column(Integer)
    height = Column(Integer)
    file_size_bytes = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipe = relationship('Recipe', back_populates='images')

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, recipe_id={self.recipe_id}, type='{self.image_type}')>"


# ============================================================================
# RELATIONSHIP TABLES (Many-to-Many)
# ============================================================================

class RecipeCategory(Base):
    """Recipe-Category association."""

    __tablename__ = 'recipe_categories'

    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class RecipeIngredient(Base):
    """Recipe-Ingredient association with quantity and preparation notes."""

    __tablename__ = 'recipe_ingredients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = Column(Numeric(10, 3), CheckConstraint('quantity IS NULL OR quantity > 0'))
    unit_id = Column(Integer, ForeignKey('units.id', ondelete='RESTRICT'))
    preparation_note = Column(Text)  # 'chopped', 'diced', 'minced'
    is_optional = Column(Boolean, default=False)
    display_order = Column(Integer, CheckConstraint('display_order >= 0'), default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipe = relationship('Recipe', back_populates='ingredients_association')
    ingredient = relationship('Ingredient', back_populates='recipe_associations')
    unit = relationship('Unit', back_populates='recipe_ingredients')

    # Indexes
    __table_args__ = (
        Index('idx_recipe_ingredients_lookup', 'recipe_id', 'ingredient_id', 'display_order'),
    )

    @property
    def quantity_display(self) -> str:
        """Format quantity with unit for display."""
        if self.quantity and self.unit:
            return f"{self.quantity} {self.unit.abbreviation}"
        elif self.quantity:
            return str(self.quantity)
        return ""

    def __repr__(self) -> str:
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient='{self.ingredient.name}', qty={self.quantity})>"


class RecipeAllergen(Base):
    """Recipe-Allergen association."""

    __tablename__ = 'recipe_allergens'

    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    allergen_id = Column(Integer, ForeignKey('allergens.id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class RecipeDietaryTag(Base):
    """Recipe-DietaryTag association."""

    __tablename__ = 'recipe_dietary_tags'

    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    dietary_tag_id = Column(Integer, ForeignKey('dietary_tags.id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================================================
# RECIPE DETAILS
# ============================================================================

class CookingInstruction(Base):
    """Step-by-step cooking instructions."""

    __tablename__ = 'cooking_instructions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    step_number = Column(Integer, CheckConstraint('step_number > 0'), nullable=False)
    instruction = Column(Text, nullable=False)
    time_minutes = Column(Integer, CheckConstraint('time_minutes IS NULL OR time_minutes >= 0'))
    image_id = Column(Integer, ForeignKey('images.id', ondelete='SET NULL'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recipe = relationship('Recipe', back_populates='cooking_instructions')

    # Constraints
    __table_args__ = (
        UniqueConstraint('recipe_id', 'step_number', name='uq_recipe_step'),
        Index('idx_instructions_recipe', 'recipe_id', 'step_number'),
    )

    def __repr__(self) -> str:
        return f"<CookingInstruction(recipe_id={self.recipe_id}, step={self.step_number})>"


class NutritionalInfo(Base):
    """Nutritional information per serving."""

    __tablename__ = 'nutritional_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), unique=True, nullable=False)
    serving_size_g = Column(Integer)
    calories = Column(Numeric(10, 2), CheckConstraint('calories IS NULL OR calories >= 0'), index=True)
    protein_g = Column(Numeric(10, 2), CheckConstraint('protein_g IS NULL OR protein_g >= 0'), index=True)
    carbohydrates_g = Column(Numeric(10, 2), CheckConstraint('carbohydrates_g IS NULL OR carbohydrates_g >= 0'))
    fat_g = Column(Numeric(10, 2), CheckConstraint('fat_g IS NULL OR fat_g >= 0'))
    saturated_fat_g = Column(Numeric(10, 2))
    fiber_g = Column(Numeric(10, 2), CheckConstraint('fiber_g IS NULL OR fiber_g >= 0'))
    sugar_g = Column(Numeric(10, 2))
    sodium_mg = Column(Numeric(10, 2))
    cholesterol_mg = Column(Numeric(10, 2))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipe = relationship('Recipe', back_populates='nutritional_info')

    # Indexes
    __table_args__ = (
        Index('idx_nutrition_ranges', 'calories', 'protein_g', 'carbohydrates_g'),
    )

    @property
    def macros_ratio(self) -> Optional[dict]:
        """Calculate protein:carbs:fat ratio."""
        if self.protein_g and self.carbohydrates_g and self.fat_g:
            total = float(self.protein_g + self.carbohydrates_g + self.fat_g)
            return {
                'protein_pct': round((float(self.protein_g) / total) * 100, 1),
                'carbs_pct': round((float(self.carbohydrates_g) / total) * 100, 1),
                'fat_pct': round((float(self.fat_g) / total) * 100, 1)
            }
        return None

    def __repr__(self) -> str:
        return f"<NutritionalInfo(recipe_id={self.recipe_id}, calories={self.calories})>"


# ============================================================================
# AUDIT AND METADATA
# ============================================================================

class ScrapingHistory(Base):
    """Track scraping operations and their outcomes."""

    __tablename__ = 'scraping_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True)
    scrape_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(
        String(50),
        CheckConstraint("status IN ('success', 'failed', 'partial')"),
        nullable=False
    )
    recipes_scraped = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    error_message = Column(Text)
    scraper_version = Column(String(50))
    execution_time_seconds = Column(Numeric(10, 3))

    # Relationships
    recipe = relationship('Recipe', back_populates='scraping_history')

    def __repr__(self) -> str:
        return f"<ScrapingHistory(id={self.id}, recipe_id={self.recipe_id}, status='{self.status}')>"


class SchemaVersion(Base):
    """Track database schema migrations."""

    __tablename__ = 'schema_version'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    applied_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text)
    checksum = Column(String(64))

    def __repr__(self) -> str:
        return f"<SchemaVersion(version='{self.version}', applied={self.applied_at})>"


# ============================================================================
# USER ENTITIES (Phase 3 Advanced Features)
# ============================================================================

class User(Base):
    """User accounts for personalized meal planning."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    preferences = relationship(
        'UserPreference',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    favorites = relationship(
        'FavoriteRecipe',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    saved_meal_plans = relationship(
        'SavedMealPlan',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    allergen_profile = relationship(
        'UserAllergen',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    # Indexes
    __table_args__ = (
        Index('idx_users_active', 'is_active', 'is_verified'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserPreference(Base):
    """User dietary preferences and nutritional targets."""

    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    default_servings = Column(Integer, CheckConstraint('default_servings > 0'), default=2)
    calorie_target = Column(Integer, CheckConstraint('calorie_target IS NULL OR calorie_target > 0'))
    protein_target_g = Column(Numeric(10, 2), CheckConstraint('protein_target_g IS NULL OR protein_target_g >= 0'))
    carb_limit_g = Column(Numeric(10, 2), CheckConstraint('carb_limit_g IS NULL OR carb_limit_g >= 0'))
    fat_limit_g = Column(Numeric(10, 2), CheckConstraint('fat_limit_g IS NULL OR fat_limit_g >= 0'))
    preferred_cuisines = Column(Text)  # JSON array of cuisine types
    excluded_ingredients = Column(Text)  # JSON array of ingredient IDs or names
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='preferences')
    dietary_tags = relationship(
        'DietaryTag',
        secondary='user_dietary_preferences',
        lazy='selectin'
    )

    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, servings={self.default_servings})>"


class FavoriteRecipe(Base):
    """User's favorite recipes with optional notes."""

    __tablename__ = 'favorite_recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='favorites')
    recipe = relationship('Recipe', back_populates='favorited_by')

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'recipe_id', name='uq_user_favorite_recipe'),
        Index('idx_favorites_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<FavoriteRecipe(user_id={self.user_id}, recipe_id={self.recipe_id})>"


class SavedMealPlan(Base):
    """User's saved meal plans with metadata."""

    __tablename__ = 'saved_meal_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    plan_data = Column(Text, nullable=False)  # JSON structure containing meal plan details
    is_template = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='saved_meal_plans')

    # Indexes
    __table_args__ = (
        Index('idx_meal_plans_user_dates', 'user_id', 'start_date', 'end_date'),
        Index('idx_meal_plans_templates', 'is_template', 'user_id'),
    )

    def __repr__(self) -> str:
        return f"<SavedMealPlan(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class UserDietaryPreference(Base):
    """Junction table for user's dietary tag preferences."""

    __tablename__ = 'user_dietary_preferences'

    user_preference_id = Column(Integer, ForeignKey('user_preferences.id', ondelete='CASCADE'), primary_key=True)
    dietary_tag_id = Column(Integer, ForeignKey('dietary_tags.id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class UserAllergen(Base):
    """User's allergen profile with severity levels."""

    __tablename__ = 'user_allergens'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    allergen_id = Column(Integer, ForeignKey('allergens.id', ondelete='CASCADE'), primary_key=True)
    severity = Column(
        String(50),
        CheckConstraint("severity IN ('avoid', 'severe', 'trace_ok')"),
        default='avoid',
        nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='allergen_profile')
    allergen = relationship('Allergen')

    def __repr__(self) -> str:
        return f"<UserAllergen(user_id={self.user_id}, allergen_id={self.allergen_id}, severity='{self.severity}')>"


class IngredientPrice(Base):
    """Ingredient pricing data for cost estimation."""

    __tablename__ = 'ingredient_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), nullable=False, index=True)
    price_per_unit = Column(Numeric(10, 2), CheckConstraint('price_per_unit >= 0'), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id', ondelete='RESTRICT'))
    store = Column(String(100), default='average')
    currency = Column(String(3), default='GBP')
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ingredient = relationship('Ingredient')
    unit = relationship('Unit')

    # Indexes
    __table_args__ = (
        Index('idx_prices_ingredient_store', 'ingredient_id', 'store', 'last_updated'),
        Index('idx_prices_updated', 'last_updated'),
    )

    def __repr__(self) -> str:
        return f"<IngredientPrice(ingredient_id={self.ingredient_id}, price={self.price_per_unit} {self.currency})>"


# ============================================================================
# EVENT LISTENERS
# ============================================================================

@event.listens_for(Ingredient, 'before_insert')
@event.listens_for(Ingredient, 'before_update')
def auto_normalize_ingredient_name(mapper, connection, target):
    """Automatically set normalized_name when ingredient is created/updated."""
    if target.name:
        target.normalized_name = target.name.lower().strip()


@event.listens_for(Recipe, 'before_update')
def update_recipe_timestamp(mapper, connection, target):
    """Update last_updated timestamp on recipe changes."""
    target.last_updated = datetime.utcnow()
