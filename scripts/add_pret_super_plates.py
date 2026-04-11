"""
Add Pret A Manger Super Plates recipes to the database.
Scraped from https://www.pret.co.uk/en-GB/super-plates-a-new-way-to-salad
"""

import sys
import os
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.connection import get_engine, get_session_factory
from src.database.models import (
    Recipe, RecipeIngredient, Ingredient, Unit,
    CookingInstruction, NutritionalInfo, Image,
    Category, Allergen, DietaryTag,
)


PRET_RECIPES = [
    {
        "gousto_id": "pret-UK020779",
        "slug": "pret-chipotle-chicken-super-plate",
        "name": "Chipotle Chicken Super Plate",
        "description": (
            "A Pret A Manger Super Plate with black bean mole, avocado, feta, "
            "chargrilled red pepper and brown rice & quinoa. High-protein, "
            "flavour-packed and satisfying enough to keep you fuller for longer."
        ),
        "cooking_time_minutes": 0,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 1,
        "source_url": "https://www.pret.co.uk/en-GB/products/UK020779/chipotle-chicken",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["high-protein", "gluten-free"],
        "allergens": ["Dairy"],
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 112, "unit": "g", "category": "protein"},
            {"name": "Black Beans", "quantity": 90, "unit": "g", "category": "legume"},
            {"name": "Avocado", "quantity": 75, "unit": "g", "category": "vegetable"},
            {"name": "Red Pepper", "quantity": 48, "unit": "g", "category": "vegetable"},
            {"name": "Brown Rice", "quantity": 40, "unit": "g", "category": "grain"},
            {"name": "Feta Cheese", "quantity": 24, "unit": "g", "category": "dairy"},
            {"name": "Mixed Salad Leaves", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Chipotle Ketchup", "quantity": 21, "unit": "g", "category": "condiment"},
            {"name": "Lime", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Pickled Red Onion", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Coriander", "quantity": None, "unit": None, "category": "herb"},
            {"name": "Red Quinoa", "quantity": None, "unit": None, "category": "grain"},
        ],
        "nutrition": {
            "serving_size_g": 533,
            "calories": 694,
            "protein_g": 49.3,
            "carbohydrates_g": 47.3,
            "fat_g": 31.4,
            "saturated_fat_g": 8.7,
            "fiber_g": 12.3,
            "sugar_g": 14.1,
            "sodium_mg": 1100,
        },
        "images": [
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/2oRHzBmzC1Lgw3PGjRqI4v/4789f4fa3aeecd9ea82856d9dd4b44f7/2001_SuperSalad_ChipotleSpicedChicken_NVBI_1080_01.png",
                "type": "main",
                "alt_text": "Pret Chipotle Chicken Super Plate",
            },
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/43ojUmQslInDMTUh95EwyG/54a1dce045d13851cbb9971f603d21e2/Product_2.jpg",
                "type": "thumbnail",
                "alt_text": "Pret Chipotle Chicken Super Plate thumbnail",
            },
        ],
    },
    {
        "gousto_id": "pret-UK020777",
        "slug": "pret-butternut-mezze-super-plate",
        "name": "Butternut Mezze Super Plate",
        "description": (
            "A Pret A Manger Super Plate with chilli aubergine, chargrilled "
            "chickpeas, massaged kale and a dollop of humous. Vegan, high in "
            "fibre, and bursting with Middle Eastern flavours."
        ),
        "cooking_time_minutes": 0,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 1,
        "source_url": "https://www.pret.co.uk/en-GB/products/UK020777/butternut-mezze",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["vegan", "dairy-free"],
        "allergens": [],
        "ingredients": [
            {"name": "Butternut Squash", "quantity": 78, "unit": "g", "category": "vegetable"},
            {"name": "Chickpeas", "quantity": 64, "unit": "g", "category": "legume"},
            {"name": "Humous", "quantity": 60, "unit": "g", "category": "condiment"},
            {"name": "Aubergine", "quantity": 60, "unit": "g", "category": "vegetable"},
            {"name": "Brown Rice", "quantity": 40, "unit": "g", "category": "grain"},
            {"name": "Mixed Salad Leaves", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Pickled Red Cabbage", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Kale", "quantity": 18, "unit": "g", "category": "vegetable"},
            {"name": "Pomegranate Seeds", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Lemon", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Red Quinoa", "quantity": None, "unit": None, "category": "grain"},
            {"name": "Mint", "quantity": None, "unit": None, "category": "herb"},
        ],
        "nutrition": {
            "serving_size_g": 460,
            "calories": 610,
            "protein_g": 18.0,
            "carbohydrates_g": 61.3,
            "fat_g": 28.5,
            "saturated_fat_g": 3.2,
            "fiber_g": 18.3,
            "sugar_g": 17.3,
            "sodium_mg": 1064,
        },
        "images": [
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/7EI8vN603jZUTVgBuilRIs/fe113e035463128e1cd8d02a8a5733cf/0000_Salad_SmokeyChickpeaMezze_NVBI_1080_000__3_.png",
                "type": "main",
                "alt_text": "Pret Butternut Mezze Super Plate",
            },
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/4dcquPwq9sWhLhfCrCPbgU/3e162ab42fd4e9b0ec702d2492b532ed/Product_3.jpg",
                "type": "thumbnail",
                "alt_text": "Pret Butternut Mezze Super Plate thumbnail",
            },
        ],
    },
    {
        "gousto_id": "pret-UK020778",
        "slug": "pret-shawarma-chicken-super-plate",
        "name": "Shawarma Chicken Super Plate",
        "description": (
            "A Pret A Manger Super Plate with chargrilled chickpeas, red peppers, "
            "massaged kale, pistachios and a dollop of humous. High-protein with "
            "bold Middle Eastern shawarma spices."
        ),
        "cooking_time_minutes": 0,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 1,
        "source_url": "https://www.pret.co.uk/en-GB/products/UK020778/shawarma-chicken",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["high-protein"],
        "allergens": ["Dairy", "Tree Nuts"],
        "ingredients": [
            {"name": "Chicken Breast", "quantity": 108, "unit": "g", "category": "protein"},
            {"name": "Chickpeas", "quantity": 68, "unit": "g", "category": "legume"},
            {"name": "Humous", "quantity": 63, "unit": "g", "category": "condiment"},
            {"name": "Cucumber", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Red Pepper", "quantity": 50, "unit": "g", "category": "vegetable"},
            {"name": "Spinach", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Kale", "quantity": 18, "unit": "g", "category": "vegetable"},
            {"name": "Pomegranate Seeds", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Pistachio Nuts", "quantity": None, "unit": None, "category": "nuts"},
            {"name": "Natural Yogurt", "quantity": None, "unit": None, "category": "dairy"},
            {"name": "Shawarma Spice Paste", "quantity": None, "unit": None, "category": "condiment"},
            {"name": "Lemon", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Mint", "quantity": None, "unit": None, "category": "herb"},
        ],
        "nutrition": {
            "serving_size_g": 452,
            "calories": 608,
            "protein_g": 49.7,
            "carbohydrates_g": 32.0,
            "fat_g": 28.3,
            "saturated_fat_g": 3.9,
            "fiber_g": 13.7,
            "sugar_g": 14.0,
            "sodium_mg": 996,
        },
        "images": [
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/6JxLFXTLMUTNtHclbpmNWJ/e95e1b62278e07fa8367c1b4acdba6fc/0000_Salad_SchwarmaChickenSalad_NVBI_1080_000__2_.png",
                "type": "main",
                "alt_text": "Pret Shawarma Chicken Super Plate",
            },
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/ih02ugpy2zX289TDzYyfB/5a39b53424e0a9f1dc47fec689cafba4/Product_4.jpg",
                "type": "thumbnail",
                "alt_text": "Pret Shawarma Chicken Super Plate thumbnail",
            },
        ],
    },
    {
        "gousto_id": "pret-UK020776",
        "slug": "pret-miso-salmon-super-plate",
        "name": "Miso Salmon Super Plate",
        "description": (
            "A Pret A Manger Super Plate with Tenderstem broccoli, avocado topped "
            "with Japanese togarashi spiced seeds, chilli aubergine, edamame soya "
            "beans and Pret's miso & orange dressing. High-protein and packed "
            "with omega-3."
        ),
        "cooking_time_minutes": 0,
        "prep_time_minutes": 10,
        "difficulty": "easy",
        "servings": 1,
        "source_url": "https://www.pret.co.uk/en-GB/products/UK020776/miso-salmon",
        "categories": ["Salad", "Lunch"],
        "dietary_tags": ["high-protein", "dairy-free"],
        "allergens": ["Fish"],
        "ingredients": [
            {"name": "Salmon", "quantity": 92, "unit": "g", "category": "protein"},
            {"name": "Black Rice", "quantity": 92, "unit": "g", "category": "grain"},
            {"name": "Avocado", "quantity": 71, "unit": "g", "category": "vegetable"},
            {"name": "Aubergine", "quantity": 51, "unit": "g", "category": "vegetable"},
            {"name": "Miso Dressing", "quantity": 46, "unit": "g", "category": "condiment"},
            {"name": "Tenderstem Broccoli", "quantity": 36, "unit": "g", "category": "vegetable"},
            {"name": "Edamame Beans", "quantity": 31, "unit": "g", "category": "legume"},
            {"name": "Pickled Red Cabbage", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Mixed Salad Leaves", "quantity": None, "unit": None, "category": "vegetable"},
            {"name": "Lime", "quantity": None, "unit": None, "category": "fruit"},
            {"name": "Togarashi Seeds", "quantity": None, "unit": None, "category": "condiment"},
            {"name": "White Quinoa", "quantity": None, "unit": None, "category": "grain"},
        ],
        "nutrition": {
            "serving_size_g": 510,
            "calories": 761,
            "protein_g": 36.0,
            "carbohydrates_g": 43.4,
            "fat_g": 47.1,
            "saturated_fat_g": 7.1,
            "fiber_g": 12.8,
            "sugar_g": 16.5,
            "sodium_mg": 1264,
        },
        "images": [
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/66GT9b8GLqzOw2WNYswnA2/85075b93bd920d86688d0fe32bb2acb2/0000_Salad_TogorashiSalmon_NVBI_1080_000__2_.png",
                "type": "main",
                "alt_text": "Pret Miso Salmon Super Plate",
            },
            {
                "url": "https://images.ctfassets.net/4zu8gvmtwqss/9uAGpin5PPczr66Yt2diL/c57c6f8236ae497ca196413232e7f597/Product_1.jpg",
                "type": "thumbnail",
                "alt_text": "Pret Miso Salmon Super Plate thumbnail",
            },
        ],
    },
]


def get_or_create_ingredient(session: Session, name: str, category: str = None) -> Ingredient:
    """Get existing ingredient or create a new one."""
    ingredient = session.query(Ingredient).filter_by(name=name).first()
    if not ingredient:
        ingredient = Ingredient(name=name, category=category)
        session.add(ingredient)
        session.flush()
    return ingredient


def get_or_create_category(session: Session, name: str) -> Category:
    """Get existing category or create a new one."""
    category = session.query(Category).filter_by(name=name).first()
    if not category:
        slug = name.lower().replace(" ", "-")
        category = Category(name=name, slug=slug, category_type="meal_type")
        session.add(category)
        session.flush()
    return category


def insert_recipe(session: Session, data: dict) -> Recipe:
    """Insert a single Pret Super Plate recipe with all relationships."""
    # Check if recipe already exists
    existing = session.query(Recipe).filter_by(slug=data["slug"]).first()
    if existing:
        print(f"  Skipping '{data['name']}' - already exists (id={existing.id})")
        return existing

    # Create recipe
    recipe = Recipe(
        gousto_id=data["gousto_id"],
        slug=data["slug"],
        name=data["name"],
        description=data["description"],
        cooking_time_minutes=data["cooking_time_minutes"],
        prep_time_minutes=data["prep_time_minutes"],
        difficulty=data["difficulty"],
        servings=data["servings"],
        source_url=data["source_url"],
    )

    # Add ingredients
    unit_cache = {}
    for i, ing_data in enumerate(data["ingredients"]):
        ingredient = get_or_create_ingredient(
            session, ing_data["name"], ing_data.get("category")
        )

        unit = None
        if ing_data.get("unit"):
            abbrev = ing_data["unit"]
            if abbrev not in unit_cache:
                unit_cache[abbrev] = session.query(Unit).filter_by(abbreviation=abbrev).first()
            unit = unit_cache[abbrev]

        recipe_ingredient = RecipeIngredient(
            ingredient=ingredient,
            quantity=ing_data.get("quantity"),
            unit=unit,
            is_optional=False,
            display_order=i,
        )
        recipe.ingredients_association.append(recipe_ingredient)

    # Add nutritional info
    nut = data["nutrition"]
    recipe.nutritional_info = NutritionalInfo(
        serving_size_g=nut.get("serving_size_g"),
        calories=nut["calories"],
        protein_g=nut["protein_g"],
        carbohydrates_g=nut["carbohydrates_g"],
        fat_g=nut["fat_g"],
        saturated_fat_g=nut.get("saturated_fat_g"),
        fiber_g=nut.get("fiber_g"),
        sugar_g=nut.get("sugar_g"),
        sodium_mg=nut.get("sodium_mg"),
    )

    # Add images
    for j, img_data in enumerate(data["images"]):
        image = Image(
            url=img_data["url"],
            image_type=img_data["type"],
            alt_text=img_data.get("alt_text"),
            display_order=j,
        )
        recipe.images.append(image)

    # Add categories
    for cat_name in data["categories"]:
        category = get_or_create_category(session, cat_name)
        recipe.categories.append(category)

    # Add dietary tags
    for tag_slug in data.get("dietary_tags", []):
        tag = session.query(DietaryTag).filter_by(slug=tag_slug).first()
        if tag:
            recipe.dietary_tags.append(tag)
        else:
            print(f"  Warning: dietary tag '{tag_slug}' not found in DB")

    # Add allergens
    for allergen_name in data.get("allergens", []):
        allergen = session.query(Allergen).filter_by(name=allergen_name).first()
        if allergen:
            recipe.allergens.append(allergen)
        else:
            print(f"  Warning: allergen '{allergen_name}' not found in DB")

    # Add a simple instruction (these are ready-to-eat salads)
    instruction = CookingInstruction(
        step_number=1,
        instruction="Open the packaging. This is a ready-to-eat Super Plate from Pret A Manger - enjoy as is, or recreate at home with the listed ingredients.",
    )
    recipe.cooking_instructions.append(instruction)

    session.add(recipe)
    return recipe


def main():
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "recipes.db",
    )
    db_url = f"sqlite:///{db_path}"

    print(f"Connecting to database: {db_url}")
    engine = get_engine(db_url)
    SessionFactory = get_session_factory(engine)

    with SessionFactory() as session:
        print(f"\nAdding {len(PRET_RECIPES)} Pret Super Plates recipes...\n")

        for data in PRET_RECIPES:
            print(f"  Adding: {data['name']}")
            recipe = insert_recipe(session, data)
            print(f"    -> id={recipe.id}, slug={recipe.slug}")

        session.commit()
        print("\nAll recipes committed successfully!")

        # Verify
        count = session.query(Recipe).filter(
            Recipe.slug.like("pret-%")
        ).count()
        print(f"\nTotal Pret recipes in database: {count}")


if __name__ == "__main__":
    main()
