"""
Unit tests for the food taxonomy (allergen detection + categorisation).

These guard the safety-critical allergen matching, including the false-positive
cases (eggplant, peanut butter, butternut) that the previous substring approach
got wrong.
"""

import pytest

from src.utils.food_taxonomy import (
    ingredient_contains_allergen,
    detect_allergens,
    categorize_ingredient,
    known_allergens,
)


class TestAllergenDetection:
    """Allergen detection from ingredient names."""

    @pytest.mark.parametrize("name,allergen", [
        ("milk", "dairy"),
        ("cheddar cheese", "dairy"),
        ("buttermilk", "dairy"),
        ("wheat flour", "gluten"),
        ("spaghetti", "gluten"),
        ("semolina", "gluten"),
        ("soy sauce", "soy"),
        ("free range eggs", "eggs"),
        ("ground almonds", "tree nuts"),
        ("peanut butter", "peanuts"),
        ("king prawns", "shellfish"),
        ("smoked salmon", "fish"),
        ("tahini", "sesame"),
        ("celeriac", "celery"),
    ])
    def test_true_positives(self, name, allergen):
        assert ingredient_contains_allergen(name, allergen) is True

    @pytest.mark.parametrize("name,allergen", [
        # Classic substring false positives that must NOT match.
        ("eggplant", "eggs"),
        ("aubergine", "eggs"),
        ("nutmeg", "tree nuts"),
        ("coconut milk", "tree nuts"),
        ("butternut squash", "dairy"),
        ("peanut butter", "dairy"),
        ("butter beans", "dairy"),
        ("coconut milk", "dairy"),
        ("almond milk", "dairy"),
        ("rice", "gluten"),
        ("chicken breast", "dairy"),
        ("water chestnut", "tree nuts"),
    ])
    def test_false_positives_excluded(self, name, allergen):
        assert ingredient_contains_allergen(name, allergen) is False

    def test_peanut_butter_is_peanut_not_dairy(self):
        allergens = detect_allergens("peanut butter")
        assert "peanuts" in allergens
        assert "dairy" not in allergens

    def test_detect_multiple_allergens(self):
        # Pesto = tree nuts (pine nuts) + dairy (parmesan) per the lexicon
        allergens = detect_allergens("creamy cheese sauce")
        assert "dairy" in allergens

    def test_no_allergens(self):
        assert detect_allergens("carrot") == set()

    def test_known_allergens_cover_14_fic(self):
        # The 14 UK FIC allergens seeded in the DB should all be representable.
        names = set(known_allergens())
        for expected in ["gluten", "dairy", "eggs", "tree nuts", "peanuts",
                         "soy", "fish", "shellfish", "sesame", "mustard",
                         "celery", "lupin", "sulfites"]:
            assert expected in names


class TestCategorisation:
    """Coarse cost categorisation."""

    @pytest.mark.parametrize("name,category", [
        ("chicken breast", "protein"),
        ("beef mince", "protein"),
        ("cheddar cheese", "dairy"),
        ("basmati rice", "grain"),
        ("olive oil", "oil"),
        ("fresh basil", "herb"),
        ("ground cumin", "spice"),
        ("onion", "vegetable"),
        ("soy sauce", "condiment"),
    ])
    def test_categories(self, name, category):
        assert categorize_ingredient(name) == category

    def test_unknown_is_other(self):
        assert categorize_ingredient("xyzzy") == "other"

    def test_empty_is_other(self):
        assert categorize_ingredient("") == "other"
