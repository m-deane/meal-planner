"""
DB-backed allergen safety tests.

Unlike the mock-based tests, these build real recipes/ingredients and verify
that the filter excludes allergenic recipes even when the recipe_allergens
table link is missing (the production failure mode), via ingredient-name
analysis.
"""

import pytest

from src.meal_planner.allergen_filter import AllergenFilter
from src.database.models import (
    Recipe, Ingredient, RecipeIngredient, Unit, Allergen, UserAllergen,
)


def _make_recipe(session, name, ingredient_names, link_allergens=None):
    recipe = Recipe(
        gousto_id=f'gousto_{name}',
        slug=name.lower().replace(' ', '-'),
        name=name,
        source_url=f'https://www.gousto.co.uk/cookbook/recipes/{name}',
        is_active=True,
        servings=2,
    )
    session.add(recipe)
    session.flush()

    for i, ing_name in enumerate(ingredient_names):
        ing = Ingredient(name=ing_name, normalized_name=ing_name.lower())
        session.add(ing)
        session.flush()
        session.add(RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ing.id, quantity=1, display_order=i
        ))

    for allergen in (link_allergens or []):
        from src.database.models import RecipeAllergen
        session.add(RecipeAllergen(recipe_id=recipe.id, allergen_id=allergen.id))

    session.commit()
    session.refresh(recipe)
    return recipe


@pytest.fixture
def peanut_allergen(db_session):
    allergen = Allergen(name='peanuts', description='Peanuts')
    db_session.add(allergen)
    db_session.commit()
    db_session.refresh(allergen)
    return allergen


@pytest.fixture
def severe_peanut_profile(db_session, peanut_allergen):
    ua = UserAllergen(user_id=1, allergen_id=peanut_allergen.id, severity='severe')
    # Attach the allergen object for the filter's convenience.
    ua.allergen = peanut_allergen
    return [ua]


class TestAllergenSafetyDBBacked:
    def test_excludes_recipe_via_ingredient_name_without_table_link(
        self, db_session, peanut_allergen, severe_peanut_profile
    ):
        """The key production fix: no recipe_allergens row, but the ingredient
        name reveals the allergen -> recipe must be excluded."""
        recipe = _make_recipe(
            db_session, "Satay Noodles", ["Peanut Butter", "Noodles"],
            link_allergens=[],  # deliberately NOT linked
        )

        f = AllergenFilter(db_session, severe_peanut_profile)
        assert f._is_recipe_safe(recipe) is False
        assert f.filter_recipes([recipe]) == []

    def test_excludes_recipe_via_table_link(
        self, db_session, peanut_allergen, severe_peanut_profile
    ):
        recipe = _make_recipe(
            db_session, "Mystery Bar", ["Secret Ingredient"],
            link_allergens=[peanut_allergen],
        )
        f = AllergenFilter(db_session, severe_peanut_profile)
        assert f._is_recipe_safe(recipe) is False

    def test_safe_recipe_passes(self, db_session, severe_peanut_profile):
        recipe = _make_recipe(db_session, "Veg Stir Fry", ["Carrot", "Broccoli"])
        f = AllergenFilter(db_session, severe_peanut_profile)
        assert f._is_recipe_safe(recipe) is True

    def test_get_safe_recipes_post_filters_unlinked_allergen(
        self, db_session, peanut_allergen, severe_peanut_profile
    ):
        """get_safe_recipes must also drop a page result whose allergen is only
        detectable by ingredient name."""
        _make_recipe(db_session, "Peanut Stew", ["Peanuts", "Tomato"], link_allergens=[])
        _make_recipe(db_session, "Plain Rice", ["Rice"])

        f = AllergenFilter(db_session, severe_peanut_profile)
        results = f.get_safe_recipes(user_id=1, limit=50)
        names = {r.name for r in results}
        assert "Peanut Stew" not in names
        assert "Plain Rice" in names

    def test_eggplant_not_flagged_as_egg(self, db_session):
        """Regression: eggplant must not be treated as containing eggs."""
        egg_allergen = Allergen(name='eggs', description='Eggs')
        db_session.add(egg_allergen)
        db_session.commit()
        db_session.refresh(egg_allergen)

        ua = UserAllergen(user_id=1, allergen_id=egg_allergen.id, severity='severe')
        ua.allergen = egg_allergen

        recipe = _make_recipe(db_session, "Eggplant Curry", ["Eggplant", "Tomato"])
        f = AllergenFilter(db_session, [ua])
        assert f._is_recipe_safe(recipe) is True
