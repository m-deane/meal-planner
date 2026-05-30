"""
Tests for SEED-1: backfilling recipe_allergens links and ingredient metadata
for recipes loaded outside the scraper (e.g. raw SQL seed dumps), where
recipe_allergens would otherwise be empty.
"""

from decimal import Decimal

from src.database.seed import backfill_allergens_and_categories
from src.database.models import (
    Recipe, Ingredient, RecipeIngredient, Allergen, RecipeAllergen,
)


def _seed_recipe_without_allergens(session):
    # Allergen lookup table (as the real seed provides).
    for name in ('peanuts', 'gluten', 'dairy'):
        session.add(Allergen(name=name))
    session.flush()

    recipe = Recipe(
        gousto_id='gousto_satay', slug='satay-noodles', name='Satay Noodles',
        source_url='https://www.gousto.co.uk/cookbook/recipes/satay-noodles',
        is_active=True, servings=2,
    )
    session.add(recipe)
    session.flush()

    # Ingredients with NULL category / is_allergen and NO recipe_allergens link.
    for i, name in enumerate(['Peanut Butter', 'Spaghetti', 'Carrot']):
        ing = Ingredient(name=name, normalized_name=name.lower())
        session.add(ing)
        session.flush()
        session.add(RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ing.id,
            quantity=Decimal('100'), display_order=i,
        ))
    session.commit()
    return recipe


class TestAllergenBackfill:
    def test_backfill_links_allergens_from_ingredient_names(self, db_session):
        recipe = _seed_recipe_without_allergens(db_session)
        assert db_session.query(RecipeAllergen).count() == 0  # precondition

        stats = backfill_allergens_and_categories(db_session)

        db_session.refresh(recipe)
        linked = {a.name for a in recipe.allergens}
        assert 'peanuts' in linked   # Peanut Butter
        assert 'gluten' in linked    # Spaghetti
        assert stats['recipe_allergen_links_added'] >= 2
        assert stats['recipes_linked'] == 1

    def test_backfill_sets_ingredient_category_and_flag(self, db_session):
        _seed_recipe_without_allergens(db_session)
        backfill_allergens_and_categories(db_session)

        carrot = db_session.query(Ingredient).filter_by(normalized_name='carrot').one()
        peanut = db_session.query(Ingredient).filter_by(normalized_name='peanut butter').one()
        assert carrot.category == 'vegetable'
        assert carrot.is_allergen is False
        assert peanut.is_allergen is True

    def test_backfill_is_idempotent(self, db_session):
        _seed_recipe_without_allergens(db_session)
        first = backfill_allergens_and_categories(db_session)
        assert first['recipe_allergen_links_added'] >= 2

        second = backfill_allergens_and_categories(db_session)
        assert second['recipe_allergen_links_added'] == 0
        assert second['ingredients_updated'] == 0

    def test_backfill_skips_recipe_with_no_detectable_allergens(self, db_session):
        for name in ('peanuts', 'gluten'):
            db_session.add(Allergen(name=name))
        db_session.flush()
        recipe = Recipe(
            gousto_id='g_veg', slug='veg', name='Veg Bowl',
            source_url='https://www.gousto.co.uk/cookbook/recipes/veg',
            is_active=True, servings=2,
        )
        db_session.add(recipe)
        db_session.flush()
        ing = Ingredient(name='Carrot', normalized_name='carrot')
        db_session.add(ing)
        db_session.flush()
        db_session.add(RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=Decimal('1'), display_order=0))
        db_session.commit()

        stats = backfill_allergens_and_categories(db_session)
        assert stats['recipes_linked'] == 0
        assert db_session.query(RecipeAllergen).count() == 0
