#!/usr/bin/env python3
"""
Database Schema Verification Script
Validates all components are properly installed and functional.
"""

import sys
import os

def check_imports():
    """Verify all required modules can be imported."""
    print("Checking imports...")
    try:
        from src.database import (
            init_database, get_session, session_scope,
            Recipe, Category, Ingredient, Unit, Allergen, DietaryTag,
            RecipeIngredient, NutritionalInfo, CookingInstruction,
            RecipeQuery
        )
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def check_database_creation():
    """Verify database can be created."""
    print("\nChecking database creation...")
    try:
        from src.database import init_database
        engine = init_database(
            database_url='sqlite:///:memory:',
            drop_existing=True,
            seed_data=True
        )
        print("✓ Database created successfully")
        return True, engine
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False, None


def check_seed_data(engine):
    """Verify seed data is loaded."""
    print("\nChecking seed data...")
    try:
        from src.database import get_session, Unit, Allergen, DietaryTag, Category
        session = get_session(engine)

        unit_count = session.query(Unit).count()
        allergen_count = session.query(Allergen).count()
        tag_count = session.query(DietaryTag).count()
        category_count = session.query(Category).count()

        print(f"  Units: {unit_count}")
        print(f"  Allergens: {allergen_count}")
        print(f"  Dietary Tags: {tag_count}")
        print(f"  Categories: {category_count}")

        if all([unit_count > 0, allergen_count > 0, tag_count > 0, category_count > 0]):
            print("✓ Seed data loaded")
            return True
        else:
            print("✗ Seed data incomplete")
            return False
    except Exception as e:
        print(f"✗ Seed data check failed: {e}")
        return False


def check_recipe_creation(engine):
    """Verify recipe can be created with relationships."""
    print("\nChecking recipe creation...")
    try:
        from decimal import Decimal
        from src.database import (
            session_scope, Recipe, NutritionalInfo,
            CookingInstruction, Category
        )

        with session_scope(engine) as session:
            # Create recipe
            recipe = Recipe(
                gousto_id='verify-001',
                slug='verification-recipe',
                name='Verification Recipe',
                cooking_time_minutes=30,
                difficulty='easy',
                servings=2,
                source_url='https://test.com'
            )
            session.add(recipe)
            session.flush()

            # Add nutrition
            nutrition = NutritionalInfo(
                recipe_id=recipe.id,
                calories=Decimal('500'),
                protein_g=Decimal('30')
            )
            session.add(nutrition)

            # Add instruction
            instruction = CookingInstruction(
                recipe_id=recipe.id,
                step_number=1,
                instruction='Test instruction'
            )
            session.add(instruction)

            # Add category
            category = session.query(Category).first()
            if category:
                recipe.categories.append(category)

            session.commit()

        print("✓ Recipe created with relationships")
        return True
    except Exception as e:
        print(f"✗ Recipe creation failed: {e}")
        return False


def check_query_helpers(engine):
    """Verify query helpers work."""
    print("\nChecking query helpers...")
    try:
        from src.database import get_session, RecipeQuery

        session = get_session(engine)
        query = RecipeQuery(session)

        # Test count
        count = query.get_recipe_count()

        # Test search
        results = query.search_by_name('verification')

        print(f"  Recipe count: {count}")
        print(f"  Search results: {len(results)}")

        if count > 0 and len(results) > 0:
            print("✓ Query helpers working")
            return True
        else:
            print("✗ Query helpers not working as expected")
            return False
    except Exception as e:
        print(f"✗ Query helper check failed: {e}")
        return False


def check_files():
    """Verify all required files exist."""
    print("\nChecking file structure...")
    required_files = [
        'src/database/__init__.py',
        'src/database/models.py',
        'src/database/schema.sql',
        'src/database/connection.py',
        'src/database/queries.py',
        'src/database/seed.py',
        'docs/DATABASE_SCHEMA.md',
        'docs/SAMPLE_QUERIES.md',
        'docs/INDEX_STRATEGY.md',
        'docs/QUICK_REFERENCE.md',
        'requirements.txt',
        '.env.example'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")

    if missing:
        print(f"\n✗ {len(missing)} files missing")
        return False
    else:
        print("\n✓ All required files present")
        return True


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 70)

    results = []

    # File structure
    results.append(check_files())

    # Imports
    results.append(check_imports())

    # Database creation
    success, engine = check_database_creation()
    results.append(success)

    if engine:
        # Seed data
        results.append(check_seed_data(engine))

        # Recipe creation
        results.append(check_recipe_creation(engine))

        # Query helpers
        results.append(check_query_helpers(engine))

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"Checks passed: {passed}/{total}")

    if all(results):
        print("\n✓ ALL CHECKS PASSED - Database schema is ready to use!")
        return 0
    else:
        print("\n✗ SOME CHECKS FAILED - Please review errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
