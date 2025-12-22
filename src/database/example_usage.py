"""
Example usage of the recipe database schema.
Demonstrates common operations and patterns.
"""

from datetime import datetime
from decimal import Decimal

from connection import init_database, session_scope
from models import (
    Recipe, Category, Ingredient, Unit, RecipeIngredient,
    NutritionalInfo, CookingInstruction, DietaryTag, Image
)
from queries import RecipeQuery


def example_1_initialize_database():
    """Initialize database with schema and seed data."""
    print("Example 1: Initializing database...")

    # Initialize with SQLite (development)
    engine = init_database(
        database_url='sqlite:///data/recipes.db',
        drop_existing=True,
        seed_data=True
    )

    print("Database initialized successfully!")
    print(f"Database URL: {engine.url}")


def example_2_create_recipe():
    """Create a complete recipe with all relationships."""
    print("\nExample 2: Creating a new recipe...")

    with session_scope() as session:
        # Create main recipe
        recipe = Recipe(
            gousto_id='example-chicken-curry-001',
            slug='easy-chicken-curry',
            name='Easy Chicken Curry',
            description='A quick and flavorful chicken curry perfect for weeknights',
            cooking_time_minutes=25,
            prep_time_minutes=10,
            difficulty='easy',
            servings=2,
            source_url='https://gousto.co.uk/example'
        )
        session.add(recipe)
        session.flush()  # Get the recipe ID

        # Add categories
        indian_category = session.query(Category).filter(
            Category.slug == 'indian'
        ).first()
        dinner_category = session.query(Category).filter(
            Category.slug == 'dinner'
        ).first()
        weeknight_category = session.query(Category).filter(
            Category.slug == 'weeknight'
        ).first()

        if indian_category and dinner_category and weeknight_category:
            recipe.categories.extend([indian_category, dinner_category, weeknight_category])

        # Add dietary tags
        high_protein_tag = session.query(DietaryTag).filter(
            DietaryTag.slug == 'high-protein'
        ).first()
        if high_protein_tag:
            recipe.dietary_tags.append(high_protein_tag)

        # Add ingredients
        ingredients_data = [
            ('chicken breast', 300, 'g', 'diced', False, 1),
            ('onion', 1, 'pc', 'chopped', False, 2),
            ('garlic', 2, 'clove', 'minced', False, 3),
            ('curry powder', 2, 'tbsp', None, False, 4),
            ('coconut milk', 400, 'ml', None, False, 5),
            ('rice', 150, 'g', None, False, 6),
        ]

        for ing_name, quantity, unit_abbr, prep_note, is_optional, order in ingredients_data:
            # Find or create ingredient
            ingredient = session.query(Ingredient).filter(
                Ingredient.normalized_name == ing_name.lower()
            ).first()

            if not ingredient:
                ingredient = Ingredient(
                    name=ing_name.title(),
                    normalized_name=ing_name.lower(),
                    category='other'
                )
                session.add(ingredient)
                session.flush()

            # Find unit
            unit = session.query(Unit).filter(
                Unit.abbreviation == unit_abbr
            ).first()

            # Add to recipe
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=Decimal(str(quantity)),
                unit_id=unit.id if unit else None,
                preparation_note=prep_note,
                is_optional=is_optional,
                display_order=order
            )
            session.add(recipe_ingredient)

        # Add cooking instructions
        instructions = [
            (1, 'Cook rice according to package directions', 15),
            (2, 'Heat oil in a large pan over medium-high heat', 2),
            (3, 'Add onion and garlic, cook until softened, about 3 minutes', 3),
            (4, 'Add chicken and curry powder, cook until chicken is browned', 8),
            (5, 'Pour in coconut milk, simmer until chicken is cooked through, about 10 minutes', 10),
            (6, 'Serve curry over rice', 1),
        ]

        for step_num, instruction_text, time_min in instructions:
            instruction = CookingInstruction(
                recipe_id=recipe.id,
                step_number=step_num,
                instruction=instruction_text,
                time_minutes=time_min
            )
            session.add(instruction)

        # Add nutritional information
        nutrition = NutritionalInfo(
            recipe_id=recipe.id,
            serving_size_g=450,
            calories=Decimal('520'),
            protein_g=Decimal('38.5'),
            carbohydrates_g=Decimal('52.0'),
            fat_g=Decimal('15.2'),
            saturated_fat_g=Decimal('8.5'),
            fiber_g=Decimal('3.2'),
            sugar_g=Decimal('4.5'),
            sodium_mg=Decimal('450')
        )
        session.add(nutrition)

        # Add main image
        image = Image(
            recipe_id=recipe.id,
            url='https://example.com/images/chicken-curry.jpg',
            image_type='main',
            display_order=0,
            alt_text='Bowl of chicken curry served over rice'
        )
        session.add(image)

        session.commit()
        print(f"Created recipe: {recipe.name} (ID: {recipe.id})")


def example_3_query_recipes():
    """Demonstrate various query patterns."""
    print("\nExample 3: Querying recipes...")

    with session_scope() as session:
        query = RecipeQuery(session)

        # Search by name
        print("\n--- Search for 'curry' ---")
        curry_recipes = query.search_by_name('curry', limit=5)
        for recipe in curry_recipes:
            print(f"  - {recipe.name} ({recipe.cooking_time_minutes} min)")

        # Filter by criteria
        print("\n--- Quick weeknight recipes (under 30 min) ---")
        quick_recipes = query.filter_recipes(
            categories=['weeknight'],
            max_cooking_time=30,
            limit=5
        )
        for recipe in quick_recipes:
            print(f"  - {recipe.name} ({recipe.cooking_time_minutes} min, {recipe.difficulty})")

        # High protein recipes
        print("\n--- High-protein recipes ---")
        high_protein = query.get_high_protein_recipes(min_protein=30, limit=5)
        for recipe in high_protein:
            protein = recipe.nutritional_info.protein_g if recipe.nutritional_info else 0
            print(f"  - {recipe.name} ({protein}g protein)")

        # Low carb recipes
        print("\n--- Low-carb recipes ---")
        low_carb = query.get_low_carb_recipes(max_carbs=20, limit=5)
        for recipe in low_carb:
            carbs = recipe.nutritional_info.carbohydrates_g if recipe.nutritional_info else 0
            print(f"  - {recipe.name} ({carbs}g carbs)")

        # Category statistics
        print("\n--- Recipe count by category ---")
        stats = query.get_category_stats()
        for category_name, category_type, count in stats[:10]:
            print(f"  - {category_name} ({category_type}): {count} recipes")


def example_4_export_recipe():
    """Export recipe data to dictionary format."""
    print("\nExample 4: Exporting recipe data...")

    with session_scope() as session:
        query = RecipeQuery(session)

        # Get first recipe
        recipe = session.query(Recipe).filter(Recipe.is_active == True).first()

        if recipe:
            recipe_data = query.export_recipe_data(recipe.id)
            print(f"\nExported: {recipe_data['name']}")
            print(f"Cooking time: {recipe_data['total_time_minutes']} minutes")
            print(f"Difficulty: {recipe_data['difficulty']}")
            print(f"Servings: {recipe_data['servings']}")

            print("\nIngredients:")
            for ing in recipe_data['ingredients']:
                qty = f"{ing['quantity']} {ing['unit']}" if ing['quantity'] else ""
                prep = f" ({ing['preparation']})" if ing['preparation'] else ""
                print(f"  - {qty} {ing['name']}{prep}")

            print("\nInstructions:")
            for step in recipe_data['instructions']:
                time_info = f" ({step['time_minutes']} min)" if step['time_minutes'] else ""
                print(f"  {step['step']}. {step['text']}{time_info}")

            if recipe_data['nutrition']:
                print("\nNutrition per serving:")
                print(f"  Calories: {recipe_data['nutrition']['calories']}")
                print(f"  Protein: {recipe_data['nutrition']['protein_g']}g")
                print(f"  Carbs: {recipe_data['nutrition']['carbohydrates_g']}g")
                print(f"  Fat: {recipe_data['nutrition']['fat_g']}g")


def example_5_advanced_filtering():
    """Demonstrate advanced filtering with multiple criteria."""
    print("\nExample 5: Advanced filtering...")

    with session_scope() as session:
        query = RecipeQuery(session)

        # Vegan recipes under 30 minutes with less than 500 calories
        print("\n--- Vegan, quick, low-calorie recipes ---")
        recipes = query.filter_recipes(
            dietary_tags=['vegan'],
            max_cooking_time=30,
            max_calories=500,
            limit=5,
            order_by='calories'
        )

        for recipe in recipes:
            cal = recipe.nutritional_info.calories if recipe.nutritional_info else 'N/A'
            print(f"  - {recipe.name}")
            print(f"    Time: {recipe.cooking_time_minutes} min, Calories: {cal}")

        # Find recipes by ingredients
        print("\n--- Recipes with chicken and rice ---")
        recipes = query.get_recipes_by_ingredient(
            ['chicken', 'rice'],
            match_all=True
        )

        for recipe in recipes[:5]:
            print(f"  - {recipe.name}")


def example_6_update_recipe():
    """Update existing recipe data."""
    print("\nExample 6: Updating recipe...")

    with session_scope() as session:
        # Find recipe
        recipe = session.query(Recipe).filter(
            Recipe.slug == 'easy-chicken-curry'
        ).first()

        if recipe:
            # Update basic info
            recipe.cooking_time_minutes = 20  # Reduced from 25
            recipe.last_updated = datetime.utcnow()

            # Update nutrition
            if recipe.nutritional_info:
                recipe.nutritional_info.calories = Decimal('495')  # Adjusted

            session.commit()
            print(f"Updated recipe: {recipe.name}")
            print(f"New cooking time: {recipe.cooking_time_minutes} minutes")


def example_7_statistics():
    """Get database statistics."""
    print("\nExample 7: Database statistics...")

    with session_scope() as session:
        query = RecipeQuery(session)

        # Total recipe count
        total = query.get_recipe_count()
        print(f"Total active recipes: {total}")

        # Most used ingredients
        print("\n--- Top 10 ingredients ---")
        ingredients = query.get_ingredient_usage(limit=10)
        for name, count in ingredients:
            print(f"  - {name}: used in {count} recipes")


def main():
    """Run all examples."""
    print("=" * 70)
    print("Recipe Database Examples")
    print("=" * 70)

    # Run examples in sequence
    example_1_initialize_database()
    example_2_create_recipe()
    example_3_query_recipes()
    example_4_export_recipe()
    example_5_advanced_filtering()
    example_6_update_recipe()
    example_7_statistics()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
