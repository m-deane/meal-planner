"""
Seed data for initial database setup.
Populates units, allergens, dietary tags, and categories.
"""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .models import Unit, Allergen, DietaryTag, Category, SchemaVersion


def seed_initial_data(engine: Engine) -> None:
    """
    Insert initial seed data into database.

    Args:
        engine: SQLAlchemy engine
    """
    session = Session(engine)

    try:
        # Check if already seeded
        if session.query(Unit).count() > 0:
            print("Database already contains seed data, skipping...")
            return

        # Insert units
        units_data = [
            ('gram', 'g', 'weight', 1.0),
            ('kilogram', 'kg', 'weight', 1000.0),
            ('milligram', 'mg', 'weight', 0.001),
            ('milliliter', 'ml', 'volume', 1.0),
            ('liter', 'l', 'volume', 1000.0),
            ('tablespoon', 'tbsp', 'volume', 15.0),
            ('teaspoon', 'tsp', 'volume', 5.0),
            ('cup', 'cup', 'volume', 240.0),
            ('fluid ounce', 'fl oz', 'volume', 30.0),
            ('pint', 'pt', 'volume', 473.0),
            ('ounce', 'oz', 'weight', 28.35),
            ('pound', 'lb', 'weight', 453.59),
            ('piece', 'pc', 'count', None),
            ('pinch', 'pinch', 'count', None),
            ('clove', 'clove', 'count', None),
            ('bunch', 'bunch', 'count', None),
            ('sprig', 'sprig', 'count', None),
            ('can', 'can', 'count', None),
            ('package', 'pkg', 'count', None),
            ('slice', 'slice', 'count', None),
        ]

        for name, abbr, unit_type, metric_equiv in units_data:
            unit = Unit(
                name=name,
                abbreviation=abbr,
                unit_type=unit_type,
                metric_equivalent=metric_equiv
            )
            session.add(unit)

        # Insert allergens
        allergens_data = [
            ('gluten', 'Found in wheat, barley, rye, and related grains'),
            ('dairy', 'Milk and milk-derived products including cheese, butter, cream'),
            ('eggs', 'Eggs and egg-containing products'),
            ('tree nuts', 'Almonds, walnuts, cashews, pecans, pistachios, etc.'),
            ('peanuts', 'Peanuts and peanut-derived products'),
            ('soy', 'Soybeans and soy-derived products'),
            ('fish', 'Fish and fish-derived products'),
            ('shellfish', 'Crustaceans (shrimp, crab, lobster) and mollusks (clams, mussels)'),
            ('sesame', 'Sesame seeds and sesame-derived products'),
            ('mustard', 'Mustard seeds and mustard-based products'),
            ('celery', 'Celery and celeriac'),
            ('lupin', 'Lupin beans and lupin flour'),
            ('sulfites', 'Sulfur dioxide and sulphites (often in wine and dried fruits)'),
        ]

        for name, description in allergens_data:
            allergen = Allergen(name=name, description=description)
            session.add(allergen)

        # Insert dietary tags
        dietary_tags_data = [
            ('Vegetarian', 'vegetarian', 'No meat or fish, may include dairy and eggs'),
            ('Vegan', 'vegan', 'No animal products whatsoever'),
            ('Gluten-Free', 'gluten-free', 'No gluten-containing ingredients'),
            ('Dairy-Free', 'dairy-free', 'No dairy products or lactose'),
            ('Low-Carb', 'low-carb', 'Reduced carbohydrate content (typically under 50g per serving)'),
            ('Keto', 'keto', 'Ketogenic diet compatible (very low carb, high fat)'),
            ('Paleo', 'paleo', 'Paleolithic diet compatible (no grains, legumes, dairy)'),
            ('Pescatarian', 'pescatarian', 'Fish and seafood allowed, but no other meat'),
            ('Nut-Free', 'nut-free', 'No tree nuts or peanuts'),
            ('High-Protein', 'high-protein', 'High protein content (typically 30g+ per serving)'),
            ('Low-Sodium', 'low-sodium', 'Reduced sodium content'),
            ('Sugar-Free', 'sugar-free', 'No added sugars'),
            ('Whole30', 'whole30', 'Whole30 program compatible'),
            ('Mediterranean', 'mediterranean', 'Mediterranean diet style'),
            ('Low-Fat', 'low-fat', 'Reduced fat content'),
        ]

        for name, slug, description in dietary_tags_data:
            tag = DietaryTag(name=name, slug=slug, description=description)
            session.add(tag)

        # Insert categories
        categories_data = [
            # Cuisines
            ('Italian', 'italian', 'cuisine', 'Traditional Italian cuisine'),
            ('Asian', 'asian', 'cuisine', 'Pan-Asian cuisine'),
            ('Chinese', 'chinese', 'cuisine', 'Traditional Chinese cuisine'),
            ('Japanese', 'japanese', 'cuisine', 'Traditional Japanese cuisine'),
            ('Thai', 'thai', 'cuisine', 'Traditional Thai cuisine'),
            ('Indian', 'indian', 'cuisine', 'Traditional Indian cuisine'),
            ('Mexican', 'mexican', 'cuisine', 'Traditional Mexican cuisine'),
            ('Mediterranean', 'mediterranean', 'cuisine', 'Mediterranean regional cuisine'),
            ('Greek', 'greek', 'cuisine', 'Traditional Greek cuisine'),
            ('French', 'french', 'cuisine', 'Traditional French cuisine'),
            ('Spanish', 'spanish', 'cuisine', 'Traditional Spanish cuisine'),
            ('Middle Eastern', 'middle-eastern', 'cuisine', 'Middle Eastern regional cuisine'),
            ('Caribbean', 'caribbean', 'cuisine', 'Caribbean regional cuisine'),
            ('British', 'british', 'cuisine', 'Traditional British cuisine'),
            ('American', 'american', 'cuisine', 'American comfort food and classics'),
            ('Korean', 'korean', 'cuisine', 'Traditional Korean cuisine'),
            ('Vietnamese', 'vietnamese', 'cuisine', 'Traditional Vietnamese cuisine'),

            # Meal types
            ('Breakfast', 'breakfast', 'meal_type', 'Morning meals and brunch'),
            ('Lunch', 'lunch', 'meal_type', 'Midday meals'),
            ('Dinner', 'dinner', 'meal_type', 'Evening meals'),
            ('Dessert', 'dessert', 'meal_type', 'Sweet dishes and treats'),
            ('Snack', 'snack', 'meal_type', 'Light snacks and appetizers'),
            ('Appetizer', 'appetizer', 'meal_type', 'Starters and small plates'),
            ('Side Dish', 'side-dish', 'meal_type', 'Accompaniments to main dishes'),
            ('Salad', 'salad', 'meal_type', 'Fresh salads and greens'),
            ('Soup', 'soup', 'meal_type', 'Soups and broths'),
            ('Main Course', 'main-course', 'meal_type', 'Main dishes'),

            # Occasions
            ('Weeknight', 'weeknight', 'occasion', 'Quick and easy weeknight meals'),
            ('Weekend', 'weekend', 'occasion', 'Weekend cooking projects'),
            ('Party', 'party', 'occasion', 'Party and entertaining recipes'),
            ('Holiday', 'holiday', 'occasion', 'Special occasion and holiday meals'),
            ('Meal Prep', 'meal-prep', 'occasion', 'Batch cooking and meal prep friendly'),
            ('Date Night', 'date-night', 'occasion', 'Romantic dinner recipes'),
            ('Family Friendly', 'family-friendly', 'occasion', 'Kid-approved family meals'),
            ('Budget Friendly', 'budget-friendly', 'occasion', 'Economical recipes'),
            ('One Pot', 'one-pot', 'occasion', 'Single pot or pan recipes'),
            ('Sheet Pan', 'sheet-pan', 'occasion', 'Sheet pan dinners'),
        ]

        for name, slug, cat_type, description in categories_data:
            category = Category(
                name=name,
                slug=slug,
                category_type=cat_type,
                description=description
            )
            session.add(category)

        # Insert schema version
        version = SchemaVersion(
            version='1.0.0',
            description='Initial schema with seed data'
        )
        session.add(version)

        session.commit()
        print("Successfully seeded initial database data")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()
