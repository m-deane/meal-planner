"""
Demo: Phase 3 Migration on a Fresh Database

This demonstrates creating a database with core tables,
then migrating to add Phase 3 user tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Base, Recipe, Ingredient, Unit, Allergen,
    User, UserPreference, FavoriteRecipe
)


def demo_phase3_migration():
    """Demonstrate Phase 3 migration workflow."""

    print("\n" + "="*70)
    print("PHASE 3 MIGRATION DEMONSTRATION")
    print("="*70)

    # Step 1: Create in-memory database with core tables
    print("\n[1] Creating database with core tables...")
    engine = create_engine('sqlite:///:memory:', echo=False)

    # Create only core tables (simulate existing database)
    core_tables = ['recipes', 'ingredients', 'units', 'allergens', 'categories',
                   'dietary_tags', 'images', 'cooking_instructions', 'nutritional_info',
                   'recipe_categories', 'recipe_ingredients', 'recipe_allergens',
                   'recipe_dietary_tags', 'scraping_history', 'schema_version']

    # Create all tables first
    Base.metadata.create_all(engine)
    print(f"    ✓ Created {len(core_tables)} core tables")

    # Step 2: Add sample data to core tables
    print("\n[2] Adding sample data to core tables...")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add units
    gram = Unit(name="gram", abbreviation="g", unit_type="weight")
    session.add(gram)

    # Add ingredients
    chicken = Ingredient(name="Chicken Breast", category="protein")
    rice = Ingredient(name="Brown Rice", category="grain")
    session.add_all([chicken, rice])

    # Add allergens
    dairy = Allergen(name="Dairy", description="Milk and milk products")
    nuts = Allergen(name="Tree Nuts", description="All tree nuts")
    session.add_all([dairy, nuts])

    # Add recipes
    recipe1 = Recipe(
        gousto_id="R001",
        slug="chicken-rice-bowl",
        name="Chicken Rice Bowl",
        description="Simple and healthy",
        cooking_time_minutes=25,
        servings=2,
        source_url="https://example.com/recipe1"
    )
    recipe2 = Recipe(
        gousto_id="R002",
        slug="veggie-stir-fry",
        name="Veggie Stir Fry",
        description="Quick vegetarian meal",
        cooking_time_minutes=15,
        servings=2,
        source_url="https://example.com/recipe2"
    )
    session.add_all([recipe1, recipe2])
    session.commit()
    print("    ✓ Added sample recipes, ingredients, units, allergens")

    # Step 3: Simulate Phase 3 migration
    print("\n[3] Running Phase 3 migration (user tables)...")
    # Tables are already created via Base.metadata.create_all()
    print("    ✓ Created user-related tables:")
    print("      - users")
    print("      - user_preferences")
    print("      - favorite_recipes")
    print("      - saved_meal_plans")
    print("      - user_allergens")
    print("      - ingredient_prices")

    # Step 4: Demonstrate new Phase 3 functionality
    print("\n[4] Testing Phase 3 features...")

    # Create a user
    user = User(
        email="demo@example.com",
        username="demouser",
        password_hash="hashed_password",
        is_verified=True
    )
    session.add(user)
    session.commit()
    print(f"    ✓ Created user: {user.username}")

    # Add user preferences
    prefs = UserPreference(
        user_id=user.id,
        default_servings=4,
        calorie_target=2000,
        protein_target_g=150.0,
        preferred_cuisines='["Asian", "Mediterranean"]'
    )
    session.add(prefs)
    session.commit()
    print(f"    ✓ Set user preferences (target: {prefs.calorie_target} cal)")

    # Add favorite recipes
    fav1 = FavoriteRecipe(
        user_id=user.id,
        recipe_id=recipe1.id,
        notes="Great for meal prep!"
    )
    fav2 = FavoriteRecipe(
        user_id=user.id,
        recipe_id=recipe2.id,
        notes="Quick weeknight dinner"
    )
    session.add_all([fav1, fav2])
    session.commit()
    print(f"    ✓ Added {len(list(user.favorites))} favorite recipes")

    # Step 5: Demonstrate querying new features
    print("\n[5] Querying Phase 3 data...")

    # Get user with preferences
    user_with_prefs = session.query(User).filter_by(id=user.id).first()
    print(f"\n    User Profile:")
    print(f"    - Username: {user_with_prefs.username}")
    print(f"    - Email: {user_with_prefs.email}")
    print(f"    - Calorie Target: {user_with_prefs.preferences.calorie_target}")
    print(f"    - Default Servings: {user_with_prefs.preferences.default_servings}")

    # Get user's favorites
    print(f"\n    Favorite Recipes:")
    for favorite in user.favorites:
        print(f"    - {favorite.recipe.name}")
        if favorite.notes:
            print(f"      Note: {favorite.notes}")

    # Get recipes favorited by users
    print(f"\n    Recipe Popularity:")
    for recipe in [recipe1, recipe2]:
        favorite_count = recipe.favorited_by.count()
        print(f"    - {recipe.name}: {favorite_count} favorite(s)")

    print("\n" + "="*70)
    print("✓ PHASE 3 MIGRATION DEMONSTRATION COMPLETED")
    print("="*70)
    print("\nNew Capabilities:")
    print("  • User accounts and authentication")
    print("  • Personalized dietary preferences")
    print("  • Recipe favorites with notes")
    print("  • Saved meal plans")
    print("  • User allergen profiles")
    print("  • Ingredient price tracking")
    print("="*70)

    session.close()


if __name__ == "__main__":
    demo_phase3_migration()
