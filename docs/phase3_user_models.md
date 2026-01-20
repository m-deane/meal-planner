# Phase 3 User Models Documentation

## Overview

Phase 3 introduces user-related database models to enable personalized meal planning features. These models support user authentication, preferences, favorites, saved meal plans, allergen profiles, and ingredient pricing.

## New Database Models

### 1. User (`users` table)

User accounts for personalized meal planning.

**Fields:**
- `id` (Integer, PK): Auto-incrementing user ID
- `email` (String(255), Unique, Indexed): User's email address
- `username` (String(100), Unique, Indexed): Username
- `password_hash` (String(255)): Hashed password (never store plain text)
- `is_active` (Boolean, default=True, Indexed): Account active status
- `is_verified` (Boolean, default=False): Email verification status
- `created_at` (DateTime): Account creation timestamp
- `last_login` (DateTime, Nullable): Last login timestamp

**Relationships:**
- `preferences`: One-to-one with UserPreference
- `favorites`: One-to-many with FavoriteRecipe
- `saved_meal_plans`: One-to-many with SavedMealPlan
- `allergen_profile`: One-to-many with UserAllergen

**Indexes:**
- `idx_users_active`: Composite index on (is_active, is_verified)

**Example:**
```python
user = User(
    email="user@example.com",
    username="healthyeater",
    password_hash="$2b$12$...",  # bcrypt hash
    is_verified=True
)
session.add(user)
session.commit()
```

---

### 2. UserPreference (`user_preferences` table)

User dietary preferences and nutritional targets.

**Fields:**
- `id` (Integer, PK): Auto-incrementing preference ID
- `user_id` (Integer, FK -> users.id, Unique): User reference
- `default_servings` (Integer, default=2): Default serving size
- `calorie_target` (Integer, Nullable): Daily calorie target
- `protein_target_g` (Numeric(10,2), Nullable): Daily protein target (grams)
- `carb_limit_g` (Numeric(10,2), Nullable): Daily carb limit (grams)
- `fat_limit_g` (Numeric(10,2), Nullable): Daily fat limit (grams)
- `preferred_cuisines` (Text): JSON array of cuisine types
- `excluded_ingredients` (Text): JSON array of ingredient IDs or names
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Constraints:**
- Check: `default_servings > 0`
- Check: `calorie_target IS NULL OR calorie_target > 0`
- Check: Nutritional values >= 0 when set

**JSON Format Examples:**
```python
# preferred_cuisines
'["Italian", "Japanese", "Mexican"]'

# excluded_ingredients
'["peanuts", "shellfish", "dairy"]'
```

**Example:**
```python
preference = UserPreference(
    user_id=user.id,
    default_servings=4,
    calorie_target=2000,
    protein_target_g=Decimal("150.0"),
    preferred_cuisines='["Italian", "Japanese"]',
    excluded_ingredients='["peanuts"]'
)
session.add(preference)
session.commit()
```

---

### 3. FavoriteRecipe (`favorite_recipes` table)

User's favorite recipes with optional notes.

**Fields:**
- `id` (Integer, PK): Auto-incrementing favorite ID
- `user_id` (Integer, FK -> users.id, Indexed): User reference
- `recipe_id` (Integer, FK -> recipes.id, Indexed): Recipe reference
- `notes` (Text, Nullable): Personal notes about the recipe
- `created_at` (DateTime): When recipe was favorited

**Constraints:**
- UniqueConstraint: (user_id, recipe_id) - User can favorite each recipe only once

**Indexes:**
- `idx_favorites_user_created`: Composite index on (user_id, created_at)

**Relationships:**
- `user`: Many-to-one with User
- `recipe`: Many-to-one with Recipe

**Recipe Relationship:**
- Added `favorited_by` relationship to Recipe model for reverse lookup

**Example:**
```python
favorite = FavoriteRecipe(
    user_id=user.id,
    recipe_id=recipe.id,
    notes="Family favorite! Add extra garlic."
)
session.add(favorite)
session.commit()

# Access from user
user_favorites = list(user.favorites)

# Access from recipe
recipe_fans = list(recipe.favorited_by)
```

---

### 4. SavedMealPlan (`saved_meal_plans` table)

User's saved meal plans with metadata.

**Fields:**
- `id` (Integer, PK): Auto-incrementing plan ID
- `user_id` (Integer, FK -> users.id, Indexed): User reference
- `name` (String(255)): Plan name
- `description` (Text, Nullable): Plan description
- `start_date` (DateTime, Nullable): Plan start date
- `end_date` (DateTime, Nullable): Plan end date
- `plan_data` (Text): JSON structure containing meal plan details
- `is_template` (Boolean, default=False, Indexed): Template flag
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Indexes:**
- `idx_meal_plans_user_dates`: Composite index on (user_id, start_date, end_date)
- `idx_meal_plans_templates`: Composite index on (is_template, user_id)

**Plan Data JSON Structure:**
```python
{
    "days": [
        {
            "date": "2026-01-20",
            "meals": [
                {
                    "meal_type": "breakfast",
                    "recipe_id": 123,
                    "servings": 2
                },
                {
                    "meal_type": "dinner",
                    "recipe_id": 456,
                    "servings": 4
                }
            ]
        }
    ],
    "nutritional_summary": {
        "total_calories": 2000,
        "protein_g": 150,
        "carbs_g": 180,
        "fat_g": 65
    },
    "shopping_list_ids": [789]
}
```

**Example:**
```python
meal_plan = SavedMealPlan(
    user_id=user.id,
    name="High Protein Week",
    description="Meal prep for the week",
    start_date=datetime(2026, 1, 20),
    end_date=datetime(2026, 1, 27),
    plan_data=json.dumps(plan_dict),
    is_template=False
)
session.add(meal_plan)
session.commit()
```

---

### 5. UserAllergen (`user_allergens` table)

User's allergen profile with severity levels.

**Fields:**
- `user_id` (Integer, FK -> users.id, PK): User reference
- `allergen_id` (Integer, FK -> allergens.id, PK): Allergen reference
- `severity` (String(50), default='avoid'): Severity level
- `created_at` (DateTime): When allergen was added

**Severity Levels:**
- `avoid`: General avoidance (default)
- `severe`: Severe allergy/intolerance
- `trace_ok`: Can tolerate trace amounts

**Constraints:**
- Check: `severity IN ('avoid', 'severe', 'trace_ok')`
- Composite primary key: (user_id, allergen_id)

**Relationships:**
- `user`: Many-to-one with User
- `allergen`: Many-to-one with Allergen

**Example:**
```python
# Add severe peanut allergy
user_allergen = UserAllergen(
    user_id=user.id,
    allergen_id=peanut_allergen.id,
    severity='severe'
)
session.add(user_allergen)
session.commit()

# Access user's allergen profile
for ua in user.allergen_profile:
    print(f"{ua.allergen.name}: {ua.severity}")
```

---

### 6. IngredientPrice (`ingredient_prices` table)

Ingredient pricing data for cost estimation.

**Fields:**
- `id` (Integer, PK): Auto-incrementing price ID
- `ingredient_id` (Integer, FK -> ingredients.id, Indexed): Ingredient reference
- `price_per_unit` (Numeric(10,2)): Price per unit
- `unit_id` (Integer, FK -> units.id): Unit reference
- `store` (String(100), default='average'): Store name
- `currency` (String(3), default='GBP'): Currency code
- `last_updated` (DateTime): Last update timestamp

**Constraints:**
- Check: `price_per_unit >= 0`

**Indexes:**
- `idx_prices_ingredient_store`: Composite index on (ingredient_id, store, last_updated)
- `idx_prices_updated`: Index on last_updated

**Relationships:**
- `ingredient`: Many-to-one with Ingredient
- `unit`: Many-to-one with Unit

**Example:**
```python
# Track chicken breast price at Tesco
price = IngredientPrice(
    ingredient_id=chicken_breast.id,
    price_per_unit=Decimal("5.99"),
    unit_id=gram_unit.id,
    store="Tesco",
    currency="GBP"
)
session.add(price)
session.commit()

# Query cheapest price for an ingredient
cheapest = session.query(IngredientPrice)\
    .filter_by(ingredient_id=ingredient_id)\
    .order_by(IngredientPrice.price_per_unit)\
    .first()
```

---

## Database Schema Updates

### Updated Recipe Model

Added relationship to support recipe favorites:

```python
favorited_by = relationship(
    'FavoriteRecipe',
    back_populates='recipe',
    cascade='all, delete-orphan',
    lazy='dynamic'
)
```

This enables querying which users have favorited a recipe:
```python
recipe = session.query(Recipe).get(recipe_id)
favorite_count = recipe.favorited_by.count()
favorited_users = [f.user for f in recipe.favorited_by]
```

---

## Cascade Delete Behavior

All user-related tables implement cascade delete:

**When a User is deleted:**
- UserPreference → Deleted
- FavoriteRecipe → Deleted
- SavedMealPlan → Deleted
- UserAllergen → Deleted

**When a Recipe is deleted:**
- FavoriteRecipe → Deleted (users' favorites are removed)

**When an Ingredient is deleted:**
- IngredientPrice → Deleted (prices are removed)

**Protected References:**
- Unit deletion is restricted if IngredientPrice references exist

---

## Common Query Patterns

### Get User's Complete Profile

```python
from sqlalchemy.orm import joinedload

user = session.query(User)\
    .options(
        joinedload(User.preferences),
        joinedload(User.allergen_profile)
    )\
    .filter_by(email='user@example.com')\
    .first()

# Access preferences
print(f"Target: {user.preferences.calorie_target} cal")

# Access allergens
for ua in user.allergen_profile:
    print(f"{ua.allergen.name}: {ua.severity}")
```

### Find User's Favorite Recipes

```python
favorites = session.query(FavoriteRecipe)\
    .join(Recipe)\
    .filter(FavoriteRecipe.user_id == user.id)\
    .order_by(FavoriteRecipe.created_at.desc())\
    .all()

for fav in favorites:
    print(f"{fav.recipe.name} - {fav.notes}")
```

### Get User's Meal Plans

```python
# Get active meal plans
plans = session.query(SavedMealPlan)\
    .filter(
        SavedMealPlan.user_id == user.id,
        SavedMealPlan.start_date <= datetime.utcnow(),
        SavedMealPlan.end_date >= datetime.utcnow()
    )\
    .all()

# Get templates
templates = session.query(SavedMealPlan)\
    .filter(
        SavedMealPlan.user_id == user.id,
        SavedMealPlan.is_template == True
    )\
    .all()
```

### Filter Recipes by User Preferences

```python
from sqlalchemy import and_, not_

# Get user's excluded ingredients
user_prefs = session.query(UserPreference).filter_by(user_id=user.id).first()
excluded = json.loads(user_prefs.excluded_ingredients) if user_prefs.excluded_ingredients else []

# Get user's allergens
user_allergens = session.query(UserAllergen)\
    .filter_by(user_id=user.id)\
    .all()
allergen_ids = [ua.allergen_id for ua in user_allergens]

# Query safe recipes
recipes = session.query(Recipe)\
    .outerjoin(RecipeIngredient)\
    .outerjoin(RecipeAllergen)\
    .filter(
        and_(
            ~RecipeIngredient.ingredient_id.in_(excluded),
            ~RecipeAllergen.allergen_id.in_(allergen_ids)
        )
    )\
    .distinct()\
    .all()
```

### Calculate Meal Plan Cost

```python
# Get ingredient prices for a recipe
recipe_cost = session.query(
    func.sum(
        RecipeIngredient.quantity * IngredientPrice.price_per_unit
    )
)\
    .join(IngredientPrice, RecipeIngredient.ingredient_id == IngredientPrice.ingredient_id)\
    .filter(
        RecipeIngredient.recipe_id == recipe_id,
        IngredientPrice.store == 'Tesco'
    )\
    .scalar()
```

---

## Migration Notes

To add these tables to an existing database:

```python
from src.database.models import Base
from sqlalchemy import create_engine

engine = create_engine('sqlite:///data/recipes.db')

# Create only new tables (existing tables are unaffected)
Base.metadata.create_all(engine)
```

For production PostgreSQL, use proper migrations (Alembic recommended).

---

## Testing

Comprehensive unit tests are provided in `/home/user/meal-planner/tests/unit/test_user_models.py`:

- 29 test cases covering all models
- Tests for constraints, relationships, and cascade deletes
- Integration tests for complete user profiles
- 100% test pass rate

Run tests:
```bash
pytest tests/unit/test_user_models.py -v
```

---

## Security Considerations

1. **Password Storage**: Always use strong hashing (bcrypt, argon2)
   ```python
   from bcrypt import hashpw, gensalt
   password_hash = hashpw(password.encode(), gensalt())
   ```

2. **Email Verification**: Use `is_verified` flag and verification tokens

3. **Input Validation**: Validate JSON data in `preferred_cuisines`, `excluded_ingredients`, `plan_data`

4. **SQL Injection**: SQLAlchemy ORM provides protection; avoid raw SQL

5. **Data Privacy**: Implement proper access controls (users can only access their own data)

---

## Next Steps (Phase 4 Recommendations)

1. Add `VerificationToken` table for email verification
2. Add `PasswordResetToken` table for password recovery
3. Add `UserSession` table for session management
4. Add `UserActivityLog` table for audit trail
5. Implement role-based access control (RBAC)
6. Add indexes for common query patterns as usage patterns emerge
7. Consider partitioning large tables (meal_plans, prices) by date
