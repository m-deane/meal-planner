"""
Tests for meal-planner correctness fixes: nutrition plans built from actual
candidates, deterministic seeding, safe weekly summary formatting, and the
filtered recipe count.
"""

import pytest
from decimal import Decimal

from src.meal_planner.planner import MealPlanner
from src.meal_planner.nutrition_planner import NutritionMealPlanner
from src.database.queries import RecipeQuery
from src.database.models import Recipe, NutritionalInfo, Category


def _make_recipe(session, name, protein, carbs, calories, cooking_time=25):
    recipe = Recipe(
        gousto_id=f'gousto_{name}', slug=name.lower().replace(' ', '-'),
        name=name, source_url=f'https://www.gousto.co.uk/cookbook/recipes/{name}',
        is_active=True, servings=2, cooking_time_minutes=cooking_time,
    )
    session.add(recipe)
    session.flush()
    session.add(NutritionalInfo(
        recipe_id=recipe.id, calories=Decimal(str(calories)),
        protein_g=Decimal(str(protein)), carbohydrates_g=Decimal(str(carbs)),
        fat_g=Decimal('10'),
    ))
    session.commit()
    return recipe


class TestNutritionCandidatesPlan:
    def test_plan_built_from_candidates(self, db_session):
        for i in range(8):
            _make_recipe(db_session, f"High Protein {i}", protein=40, carbs=10, calories=500)

        planner = NutritionMealPlanner(db_session, seed=42)
        candidates = planner.filter_by_actual_nutrition(min_protein_g=25, max_carbs_g=30)
        assert len(candidates) == 8

        plan = planner.generate_weekly_meal_plan_from_candidates(candidates)
        assert len(plan) == 7
        # Every populated meal must be one of the nutrition-filtered candidates.
        candidate_ids = {r.id for r, _ in candidates}
        for day, meals in plan.items():
            for meal_type, recipe in meals.items():
                assert recipe.id in candidate_ids

    def test_deterministic_with_seed(self, db_session):
        for i in range(8):
            _make_recipe(db_session, f"R{i}", protein=40, carbs=10, calories=500)
        cands = NutritionMealPlanner(db_session).filter_by_actual_nutrition(min_protein_g=25, max_carbs_g=30)

        p1 = NutritionMealPlanner(db_session, seed=7).generate_weekly_meal_plan_from_candidates(cands)
        p2 = NutritionMealPlanner(db_session, seed=7).generate_weekly_meal_plan_from_candidates(cands)

        ids1 = {d: {m: r.id for m, r in meals.items()} for d, meals in p1.items()}
        ids2 = {d: {m: r.id for m, r in meals.items()} for d, meals in p2.items()}
        assert ids1 == ids2

    def test_format_handles_no_nutrition_without_crashing(self, db_session):
        """Weekly summary must not raise ZeroDivisionError when totals are 0."""
        recipe = Recipe(
            gousto_id='g_x', slug='x', name='No Nutrition',
            source_url='https://www.gousto.co.uk/cookbook/recipes/x',
            is_active=True, servings=2, cooking_time_minutes=20,
        )
        db_session.add(recipe)
        db_session.commit()

        planner = NutritionMealPlanner(db_session, seed=1)
        plan = {'Monday': {'lunch': recipe}}
        output = planner.format_nutrition_meal_plan(plan)  # must not raise
        assert 'Macro %: Not available' in output


class TestFilteredCount:
    def test_count_matches_filters(self, db_session):
        cat = Category(name='Quick', slug='quick', category_type='occasion')
        db_session.add(cat)
        db_session.flush()

        slow = _make_recipe(db_session, "Slow Stew", 30, 20, 600, cooking_time=90)
        fast = _make_recipe(db_session, "Fast Wrap", 30, 20, 400, cooking_time=15)

        query = RecipeQuery(db_session)
        total_all = query.count_filtered_recipes()
        total_quick = query.count_filtered_recipes(max_cooking_time=30)

        assert total_all == 2
        assert total_quick == 1
