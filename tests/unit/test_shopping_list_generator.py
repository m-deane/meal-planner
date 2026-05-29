"""
DB-backed tests for shopping list aggregation, focusing on cross-recipe
ingredient merging and unit conversion (previously fragmented by raw unit
string).
"""

import pytest
from decimal import Decimal

from src.meal_planner.shopping_list import ShoppingListGenerator
from src.database.models import Recipe, Ingredient, RecipeIngredient, Unit


@pytest.fixture
def units(db_session):
    g = Unit(name='gram', abbreviation='g', unit_type='weight', metric_equivalent=Decimal('1.0'))
    kg = Unit(name='kilogram', abbreviation='kg', unit_type='weight', metric_equivalent=Decimal('1000.0'))
    ml = Unit(name='milliliter', abbreviation='ml', unit_type='volume', metric_equivalent=Decimal('1.0'))
    clove = Unit(name='clove', abbreviation='clove', unit_type='count', metric_equivalent=None)
    db_session.add_all([g, kg, ml, clove])
    db_session.commit()
    return {'g': g, 'kg': kg, 'ml': ml, 'clove': clove}


def _recipe_with(session, slug, items):
    """items: list of (ingredient_name, quantity, unit)"""
    recipe = Recipe(
        gousto_id=f'gousto_{slug}', slug=slug, name=slug.title(),
        source_url=f'https://www.gousto.co.uk/cookbook/recipes/{slug}',
        is_active=True, servings=2,
    )
    session.add(recipe)
    session.flush()
    for i, (name, qty, unit) in enumerate(items):
        ing = session.query(Ingredient).filter_by(normalized_name=name.lower()).first()
        if not ing:
            ing = Ingredient(name=name, normalized_name=name.lower())
            session.add(ing)
            session.flush()
        session.add(RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ing.id,
            quantity=Decimal(str(qty)) if qty is not None else None,
            unit_id=unit.id if unit else None, display_order=i,
        ))
    session.commit()
    return recipe


class TestShoppingListAggregation:
    def test_weights_converted_and_summed(self, db_session, units):
        """200 g + 1 kg of the same ingredient -> a single 1.2 kg line."""
        r1 = _recipe_with(db_session, 'r1', [('Chicken', 200, units['g'])])
        r2 = _recipe_with(db_session, 'r2', [('Chicken', 1, units['kg'])])

        gen = ShoppingListGenerator(db_session)
        result = gen.generate_from_recipes([r1.id, r2.id])

        chicken = next(i for items in result.values() for i in items if i['name'] == 'Chicken')
        # 200g + 1000g = 1200g -> rolled up to kg
        assert 'kg' in chicken['quantities']
        assert chicken['quantities']['kg']['total'] == pytest.approx(1.2)
        # Not fragmented into separate g and kg buckets
        assert 'g' not in chicken['quantities']

    def test_count_units_kept_separate_from_weight(self, db_session, units):
        r1 = _recipe_with(db_session, 'r1', [('Garlic', 2, units['clove'])])
        r2 = _recipe_with(db_session, 'r2', [('Garlic', 1, units['clove'])])

        gen = ShoppingListGenerator(db_session)
        result = gen.generate_from_recipes([r1.id, r2.id])
        garlic = next(i for items in result.values() for i in items if i['name'] == 'Garlic')
        assert garlic['quantities']['clove']['total'] == pytest.approx(3)

    def test_volume_summed_in_ml(self, db_session, units):
        r1 = _recipe_with(db_session, 'r1', [('Milk', 200, units['ml'])])
        r2 = _recipe_with(db_session, 'r2', [('Milk', 300, units['ml'])])
        gen = ShoppingListGenerator(db_session)
        result = gen.generate_from_recipes([r1.id, r2.id])
        milk = next(i for items in result.values() for i in items if i['name'] == 'Milk')
        assert milk['quantities']['ml']['total'] == pytest.approx(500)

    def test_categorisation(self, db_session, units):
        r = _recipe_with(db_session, 'r', [('Chicken', 200, units['g'])])
        gen = ShoppingListGenerator(db_session)
        result = gen.generate_from_recipes([r.id])
        assert 'Proteins' in result
