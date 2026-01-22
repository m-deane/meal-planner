"""
Unit tests for database schema and ORM models.
Tests core functionality, relationships, and data integrity.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.database import (
    init_database, session_scope, get_session,
    Recipe, Category, Ingredient, Unit, Allergen, DietaryTag,
    RecipeIngredient, RecipeCategory, NutritionalInfo,
    CookingInstruction, Image, RecipeQuery
)


@pytest.fixture(scope='function')
def db_engine():
    """Create in-memory SQLite database for testing."""
    engine = init_database(
        database_url='sqlite:///:memory:',
        drop_existing=True,
        seed_data=True
    )
    yield engine


@pytest.fixture
def db_session(db_engine):
    """Provide a session for database operations."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    # Always rollback to ensure clean state for next test
    session.rollback()
    session.close()


@pytest.fixture
def sample_recipe(db_session):
    """Create a sample recipe for testing."""
    recipe = Recipe(
        gousto_id='test-recipe-001',
        slug='test-chicken-curry',
        name='Test Chicken Curry',
        description='A delicious test curry',
        cooking_time_minutes=30,
        prep_time_minutes=15,
        difficulty='medium',
        servings=2,
        source_url='https://test.com/recipe'
    )
    db_session.add(recipe)
    db_session.flush()
    return recipe


class TestDatabaseInitialization:
    """Test database initialization and seed data."""

    def test_database_creates_tables(self, db_engine):
        """Verify all tables are created."""
        from sqlalchemy import inspect
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'recipes', 'categories', 'ingredients', 'units',
            'allergens', 'dietary_tags', 'nutritional_info',
            'cooking_instructions', 'images', 'recipe_categories',
            'recipe_ingredients', 'recipe_allergens',
            'recipe_dietary_tags', 'scraping_history', 'schema_version'
        ]

        for table in expected_tables:
            assert table in tables, f"Table {table} not created"

    def test_seed_data_loaded(self, db_session):
        """Verify seed data is present."""
        unit_count = db_session.query(Unit).count()
        allergen_count = db_session.query(Allergen).count()
        dietary_tag_count = db_session.query(DietaryTag).count()
        category_count = db_session.query(Category).count()

        assert unit_count > 0, "Units not seeded"
        assert allergen_count > 0, "Allergens not seeded"
        assert dietary_tag_count > 0, "Dietary tags not seeded"
        assert category_count > 0, "Categories not seeded"


class TestRecipeModel:
    """Test Recipe model and its properties."""

    def test_create_recipe(self, db_session):
        """Test basic recipe creation."""
        recipe = Recipe(
            gousto_id='test-001',
            slug='test-recipe',
            name='Test Recipe',
            cooking_time_minutes=20,
            prep_time_minutes=10,
            difficulty='easy',
            servings=2,
            source_url='https://test.com'
        )
        db_session.add(recipe)
        db_session.flush()

        assert recipe.id is not None
        assert recipe.name == 'Test Recipe'
        assert recipe.is_active is True

    def test_recipe_unique_constraints(self, db_session):
        """Test unique constraints on gousto_id and slug."""
        recipe1 = Recipe(
            gousto_id='unique-001',
            slug='unique-slug',
            name='Recipe 1',
            servings=2,
            source_url='https://test.com'
        )
        db_session.add(recipe1)
        db_session.flush()

        # Duplicate gousto_id should fail
        recipe2 = Recipe(
            gousto_id='unique-001',  # Duplicate
            slug='different-slug',
            name='Recipe 2',
            servings=2,
            source_url='https://test.com'
        )
        db_session.add(recipe2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()

    def test_recipe_total_time_property(self, sample_recipe):
        """Test total_time_minutes computed property."""
        assert sample_recipe.total_time_minutes == 45  # 30 + 15

    def test_recipe_check_constraints(self, db_session):
        """Test check constraints on recipe fields."""
        # Negative cooking time should fail
        recipe = Recipe(
            gousto_id='test-002',
            slug='test-negative',
            name='Invalid Recipe',
            cooking_time_minutes=-10,  # Invalid
            servings=2,
            source_url='https://test.com'
        )
        db_session.add(recipe)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()


class TestRelationships:
    """Test relationship mappings between models."""

    def test_recipe_categories_relationship(self, db_session, sample_recipe):
        """Test many-to-many recipe-category relationship."""
        category = db_session.query(Category).filter(
            Category.slug == 'indian'
        ).first()

        sample_recipe.categories.append(category)
        db_session.flush()

        assert len(sample_recipe.categories) == 1
        assert sample_recipe.categories[0].name == 'Italian' or sample_recipe.categories[0].slug == 'indian'

    def test_recipe_ingredients_relationship(self, db_session, sample_recipe):
        """Test recipe-ingredient relationship with quantities."""
        # Get or create ingredient
        chicken = db_session.query(Ingredient).filter(
            Ingredient.normalized_name == 'chicken breast'
        ).first()

        if not chicken:
            chicken = Ingredient(
                name='Chicken Breast',
                normalized_name='chicken breast',
                category='protein'
            )
            db_session.add(chicken)
            db_session.flush()

        # Get unit
        gram = db_session.query(Unit).filter(Unit.abbreviation == 'g').first()

        # Add to recipe
        recipe_ing = RecipeIngredient(
            recipe_id=sample_recipe.id,
            ingredient_id=chicken.id,
            quantity=Decimal('300'),
            unit_id=gram.id,
            preparation_note='diced',
            display_order=1
        )
        db_session.add(recipe_ing)
        db_session.flush()

        assert len(sample_recipe.ingredients_association) == 1
        assert sample_recipe.ingredients_association[0].ingredient.name == 'Chicken Breast'
        assert sample_recipe.ingredients_association[0].quantity == Decimal('300')

    def test_recipe_nutrition_relationship(self, db_session, sample_recipe):
        """Test one-to-one recipe-nutrition relationship."""
        nutrition = NutritionalInfo(
            recipe_id=sample_recipe.id,
            calories=Decimal('520'),
            protein_g=Decimal('38.5'),
            carbohydrates_g=Decimal('52'),
            fat_g=Decimal('15.2')
        )
        db_session.add(nutrition)
        db_session.flush()

        assert sample_recipe.nutritional_info is not None
        assert sample_recipe.nutritional_info.calories == Decimal('520')

    def test_recipe_instructions_relationship(self, db_session, sample_recipe):
        """Test one-to-many recipe-instructions relationship."""
        instruction1 = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=1,
            instruction='Heat oil in pan',
            time_minutes=2
        )
        instruction2 = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=2,
            instruction='Add ingredients',
            time_minutes=5
        )
        db_session.add_all([instruction1, instruction2])
        db_session.flush()

        assert len(sample_recipe.cooking_instructions) == 2
        assert sample_recipe.cooking_instructions[0].step_number == 1

    def test_cascade_delete(self, db_session, sample_recipe):
        """Test that deleting recipe cascades to related records."""
        # Add nutrition
        nutrition = NutritionalInfo(
            recipe_id=sample_recipe.id,
            calories=Decimal('500')
        )
        db_session.add(nutrition)

        # Add instruction
        instruction = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=1,
            instruction='Test instruction'
        )
        db_session.add(instruction)
        db_session.flush()

        recipe_id = sample_recipe.id

        # Delete recipe
        db_session.delete(sample_recipe)
        db_session.flush()

        # Verify cascaded deletes
        nutrition_exists = db_session.query(NutritionalInfo).filter(
            NutritionalInfo.recipe_id == recipe_id
        ).first()
        instruction_exists = db_session.query(CookingInstruction).filter(
            CookingInstruction.recipe_id == recipe_id
        ).first()

        assert nutrition_exists is None
        assert instruction_exists is None


class TestNutritionalInfo:
    """Test nutritional info model and calculations."""

    def test_create_nutrition(self, db_session, sample_recipe):
        """Test creating nutritional information."""
        nutrition = NutritionalInfo(
            recipe_id=sample_recipe.id,
            serving_size_g=450,
            calories=Decimal('520'),
            protein_g=Decimal('38.5'),
            carbohydrates_g=Decimal('52'),
            fat_g=Decimal('15.2'),
            fiber_g=Decimal('3.2')
        )
        db_session.add(nutrition)
        db_session.flush()

        assert nutrition.id is not None
        assert nutrition.calories == Decimal('520')

    def test_macros_ratio_property(self, db_session, sample_recipe):
        """Test macros ratio calculation."""
        nutrition = NutritionalInfo(
            recipe_id=sample_recipe.id,
            protein_g=Decimal('30'),
            carbohydrates_g=Decimal('50'),
            fat_g=Decimal('20')
        )
        db_session.add(nutrition)
        db_session.flush()

        ratio = nutrition.macros_ratio
        assert ratio is not None
        assert 'protein_pct' in ratio
        assert 'carbs_pct' in ratio
        assert 'fat_pct' in ratio
        # Sum should be 100%
        assert abs(sum(ratio.values()) - 100.0) < 0.1


class TestIngredientModel:
    """Test ingredient model and normalization."""

    def test_ingredient_normalization(self, db_session):
        """Test automatic name normalization."""
        ingredient = Ingredient(
            name='Chicken Breast',
            category='protein'
        )
        db_session.add(ingredient)
        db_session.flush()

        # normalized_name should be auto-set
        assert ingredient.normalized_name == 'chicken breast'

    def test_ingredient_unique_name(self, db_session):
        """Test ingredient name uniqueness."""
        ing1 = Ingredient(name='Onion', category='vegetable')
        db_session.add(ing1)
        db_session.flush()

        ing2 = Ingredient(name='Onion', category='vegetable')
        db_session.add(ing2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()


class TestRecipeQuery:
    """Test RecipeQuery helper class."""

    @pytest.fixture
    def query_helper(self, db_session):
        """Provide RecipeQuery instance."""
        return RecipeQuery(db_session)

    @pytest.fixture
    def populated_db(self, db_session):
        """Create multiple recipes for testing queries."""
        # Recipe 1: Quick vegan pasta
        recipe1 = Recipe(
            gousto_id='query-001',
            slug='vegan-pasta',
            name='Quick Vegan Pasta',
            cooking_time_minutes=20,
            difficulty='easy',
            servings=2,
            source_url='https://test.com/1'
        )
        db_session.add(recipe1)
        db_session.flush()

        # Add nutrition
        nutrition1 = NutritionalInfo(
            recipe_id=recipe1.id,
            calories=Decimal('450'),
            protein_g=Decimal('15'),
            carbohydrates_g=Decimal('70'),
            fat_g=Decimal('10')
        )
        db_session.add(nutrition1)

        # Add vegan tag
        vegan_tag = db_session.query(DietaryTag).filter(
            DietaryTag.slug == 'vegan'
        ).first()
        if vegan_tag:
            recipe1.dietary_tags.append(vegan_tag)

        # Recipe 2: High-protein chicken
        recipe2 = Recipe(
            gousto_id='query-002',
            slug='chicken-protein',
            name='High Protein Chicken',
            cooking_time_minutes=35,
            difficulty='medium',
            servings=2,
            source_url='https://test.com/2'
        )
        db_session.add(recipe2)
        db_session.flush()

        nutrition2 = NutritionalInfo(
            recipe_id=recipe2.id,
            calories=Decimal('550'),
            protein_g=Decimal('45'),
            carbohydrates_g=Decimal('30'),
            fat_g=Decimal('20')
        )
        db_session.add(nutrition2)

        high_protein_tag = db_session.query(DietaryTag).filter(
            DietaryTag.slug == 'high-protein'
        ).first()
        if high_protein_tag:
            recipe2.dietary_tags.append(high_protein_tag)

        db_session.flush()
        return recipe1, recipe2

    def test_get_by_id(self, query_helper, sample_recipe):
        """Test getting recipe by ID."""
        recipe = query_helper.get_by_id(sample_recipe.id)
        assert recipe is not None
        assert recipe.id == sample_recipe.id

    def test_get_by_slug(self, query_helper, sample_recipe):
        """Test getting recipe by slug."""
        recipe = query_helper.get_by_slug('test-chicken-curry')
        assert recipe is not None
        assert recipe.slug == 'test-chicken-curry'

    def test_search_by_name(self, query_helper, sample_recipe):
        """Test name search."""
        results = query_helper.search_by_name('curry')
        assert len(results) > 0
        assert any('curry' in r.name.lower() for r in results)

    def test_get_quick_recipes(self, query_helper, populated_db):
        """Test quick recipes query."""
        quick = query_helper.get_quick_recipes(max_time=25)
        assert len(quick) > 0
        for recipe in quick:
            assert recipe.cooking_time_minutes <= 25

    def test_get_high_protein_recipes(self, query_helper, populated_db):
        """Test high-protein recipes query."""
        high_protein = query_helper.get_high_protein_recipes(min_protein=40)
        assert len(high_protein) > 0
        for recipe in high_protein:
            assert recipe.nutritional_info.protein_g >= 40

    def test_filter_recipes_by_dietary_tags(self, query_helper, populated_db):
        """Test filtering by dietary tags."""
        vegan_recipes = query_helper.filter_recipes(
            dietary_tags=['vegan']
        )
        assert len(vegan_recipes) > 0

    def test_filter_recipes_by_nutrition(self, query_helper, populated_db):
        """Test filtering by nutritional criteria."""
        filtered = query_helper.filter_recipes(
            max_calories=500,
            min_protein=10
        )
        assert len(filtered) > 0
        for recipe in filtered:
            if recipe.nutritional_info:
                assert recipe.nutritional_info.calories <= 500

    def test_get_recipe_count(self, query_helper, populated_db):
        """Test recipe count query."""
        count = query_helper.get_recipe_count()
        assert count >= 2  # At least our test recipes

    def test_export_recipe_data(self, query_helper, sample_recipe):
        """Test recipe data export."""
        # Add some data first
        nutrition = NutritionalInfo(
            recipe_id=sample_recipe.id,
            calories=Decimal('500')
        )
        query_helper.session.add(nutrition)

        instruction = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=1,
            instruction='Test instruction'
        )
        query_helper.session.add(instruction)
        query_helper.session.flush()

        data = query_helper.export_recipe_data(sample_recipe.id)

        assert data is not None
        assert data['name'] == sample_recipe.name
        assert 'ingredients' in data
        assert 'instructions' in data
        assert 'nutrition' in data


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_foreign_key_constraint(self, db_session):
        """Test foreign key constraints are enforced."""
        # Try to create instruction for non-existent recipe
        instruction = CookingInstruction(
            recipe_id=99999,  # Doesn't exist
            step_number=1,
            instruction='Invalid'
        )
        db_session.add(instruction)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()

    def test_unique_step_number_per_recipe(self, db_session, sample_recipe):
        """Test step number uniqueness within a recipe."""
        inst1 = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=1,
            instruction='Step 1'
        )
        inst2 = CookingInstruction(
            recipe_id=sample_recipe.id,
            step_number=1,  # Duplicate
            instruction='Step 1 duplicate'
        )
        db_session.add_all([inst1, inst2])

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()

    def test_check_constraint_validation(self, db_session, sample_recipe):
        """Test check constraints are enforced."""
        # Invalid difficulty
        recipe = Recipe(
            gousto_id='test-003',
            slug='invalid-difficulty',
            name='Invalid',
            difficulty='invalid',  # Not in (easy, medium, hard)
            servings=2,
            source_url='https://test.com'
        )
        db_session.add(recipe)

        with pytest.raises(Exception):  # IntegrityError
            db_session.flush()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
