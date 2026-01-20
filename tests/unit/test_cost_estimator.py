"""
Unit tests for cost estimation functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.meal_planner.cost_estimator import CostEstimator, MealPlanCostBreakdown
from src.database.models import (
    Recipe, Ingredient, RecipeIngredient, IngredientPrice, Unit
)


@pytest.fixture
def sample_ingredients(db_session):
    """Create sample ingredients with prices."""
    # Create units
    unit_g = Unit(id=1, name='gram', abbreviation='g', unit_type='weight', metric_equivalent=Decimal('1.0'))
    unit_ml = Unit(id=2, name='milliliter', abbreviation='ml', unit_type='volume', metric_equivalent=Decimal('1.0'))
    unit_count = Unit(id=3, name='unit', abbreviation='unit', unit_type='count', metric_equivalent=None)

    db_session.add_all([unit_g, unit_ml, unit_count])

    # Create ingredients
    chicken = Ingredient(id=1, name='Chicken Breast', normalized_name='chicken breast', category='protein')
    pasta = Ingredient(id=2, name='Pasta', normalized_name='pasta', category='grain')
    tomato = Ingredient(id=3, name='Tomato', normalized_name='tomato', category='vegetable')
    onion = Ingredient(id=4, name='Onion', normalized_name='onion', category='vegetable')
    cheese = Ingredient(id=5, name='Cheese', normalized_name='cheese', category='dairy')

    db_session.add_all([chicken, pasta, tomato, onion, cheese])
    db_session.flush()

    # Create prices
    price1 = IngredientPrice(
        ingredient_id=1,
        price_per_unit=Decimal('3.50'),
        unit_id=1,
        store='average',
        currency='GBP',
        last_updated=datetime.utcnow()
    )
    price2 = IngredientPrice(
        ingredient_id=2,
        price_per_unit=Decimal('0.50'),
        unit_id=1,
        store='average',
        currency='GBP',
        last_updated=datetime.utcnow()
    )
    price3 = IngredientPrice(
        ingredient_id=3,
        price_per_unit=Decimal('0.80'),
        unit_id=1,
        store='average',
        currency='GBP',
        last_updated=datetime.utcnow()
    )

    db_session.add_all([price1, price2, price3])
    db_session.commit()

    return [chicken, pasta, tomato, onion, cheese]


@pytest.fixture
def sample_recipe(db_session, sample_ingredients):
    """Create a sample recipe with ingredients."""
    recipe = Recipe(
        id=1,
        gousto_id='TEST001',
        slug='chicken-pasta',
        name='Chicken Pasta',
        description='Delicious chicken pasta',
        cooking_time_minutes=25,
        servings=2,
        source_url='http://example.com/1',
        is_active=True
    )

    db_session.add(recipe)
    db_session.flush()

    # Add recipe ingredients
    ri1 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=1,  # Chicken
        quantity=Decimal('200'),
        unit_id=1,  # grams
        display_order=1
    )
    ri2 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=2,  # Pasta
        quantity=Decimal('300'),
        unit_id=1,  # grams
        display_order=2
    )
    ri3 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=3,  # Tomato
        quantity=Decimal('150'),
        unit_id=1,  # grams
        display_order=3
    )
    ri4 = RecipeIngredient(
        recipe_id=1,
        ingredient_id=4,  # Onion (no price in DB)
        quantity=Decimal('100'),
        unit_id=1,  # grams
        display_order=4
    )

    db_session.add_all([ri1, ri2, ri3, ri4])
    db_session.commit()

    return recipe


class TestCostEstimator:
    """Test cost estimator functionality."""

    def test_initialization(self, db_session):
        """Test cost estimator initialization."""
        estimator = CostEstimator(db_session)

        assert estimator.session == db_session
        assert isinstance(estimator._price_cache, dict)
        assert len(estimator._price_cache) == 0

    def test_estimate_recipe_cost_with_prices(self, db_session, sample_recipe):
        """Test recipe cost estimation with database prices."""
        estimator = CostEstimator(db_session)

        cost = estimator.estimate_recipe_cost(sample_recipe, servings=2)

        # Cost should be positive
        assert cost > Decimal('0.00')

        # Cost should include chicken, pasta, tomato prices plus estimated onion
        # Chicken: 200g * 3.50 = 700.0 (per 100g) = 7.00
        # Pasta: 300g * 0.50 = 150.0 (per 100g) = 1.50
        # Tomato: 150g * 0.80 = 120.0 (per 100g) = 1.20
        # Onion: estimated ~0.80 (100g * 0.80 = 0.80)
        # Total should be around 10.50

        assert 8.0 <= cost <= 15.0  # Reasonable range accounting for estimation

    def test_estimate_recipe_cost_scaling(self, db_session, sample_recipe):
        """Test recipe cost scaling by servings."""
        estimator = CostEstimator(db_session)

        cost_2_servings = estimator.estimate_recipe_cost(sample_recipe, servings=2)
        cost_4_servings = estimator.estimate_recipe_cost(sample_recipe, servings=4)

        # 4 servings should cost approximately twice as much as 2 servings
        assert cost_4_servings > cost_2_servings
        ratio = cost_4_servings / cost_2_servings
        assert 1.8 <= ratio <= 2.2  # Allow some tolerance

    def test_estimate_ingredient_price_with_db_price(self, db_session, sample_ingredients):
        """Test ingredient price estimation when price exists in database."""
        estimator = CostEstimator(db_session)

        chicken = sample_ingredients[0]
        cost = estimator._get_ingredient_cost(chicken, Decimal('100'), None)

        # Should use database price
        assert cost > Decimal('0.00')

    def test_estimate_ingredient_price_fallback(self, db_session, sample_ingredients):
        """Test ingredient price estimation fallback for missing prices."""
        estimator = CostEstimator(db_session)

        # Onion has no price in DB
        onion = sample_ingredients[3]
        cost = estimator.estimate_ingredient_price(onion, Decimal('100'), None)

        # Should return estimated price
        assert cost > Decimal('0.00')
        # Vegetable category default is 0.80 per 100g
        assert cost >= Decimal('0.40')  # At least some reasonable amount

    def test_estimate_quantity_grams_from_weight(self, db_session):
        """Test quantity conversion from weight units."""
        estimator = CostEstimator(db_session)

        unit = Unit(name='kilogram', abbreviation='kg', unit_type='weight', metric_equivalent=Decimal('1000.0'))

        grams = estimator._estimate_quantity_grams('chicken', Decimal('1'), unit)

        # 1 kg = 1000 grams
        assert grams == Decimal('1000.0')

    def test_estimate_quantity_grams_from_count(self, db_session):
        """Test quantity conversion from count units."""
        estimator = CostEstimator(db_session)

        unit = Unit(name='unit', abbreviation='unit', unit_type='count', metric_equivalent=None)

        grams = estimator._estimate_quantity_grams('tomato', Decimal('2'), unit)

        # 2 tomatoes * 120g each = 240g (from COMMON_WEIGHTS)
        assert grams == Decimal('240.0')

    def test_get_cheapest_recipes(self, db_session, sample_recipe):
        """Test finding cheapest recipes."""
        estimator = CostEstimator(db_session)

        # Create additional recipes
        recipe2 = Recipe(
            id=2,
            gousto_id='TEST002',
            slug='simple-pasta',
            name='Simple Pasta',
            cooking_time_minutes=15,
            servings=2,
            source_url='http://example.com/2',
            is_active=True
        )
        db_session.add(recipe2)
        db_session.flush()

        # Add cheap ingredient
        ri = RecipeIngredient(recipe_id=2, ingredient_id=2, quantity=Decimal('200'), unit_id=1, display_order=1)
        db_session.add(ri)
        db_session.commit()

        # Get cheapest recipes
        results = estimator.get_cheapest_recipes(limit=10)

        assert len(results) > 0
        # Results should be sorted by cost
        costs = [cost for _, cost in results]
        assert costs == sorted(costs)

    def test_get_budget_alternatives(self, db_session, sample_recipe):
        """Test finding budget alternatives to a recipe."""
        estimator = CostEstimator(db_session)

        # Create alternative recipe
        recipe2 = Recipe(
            id=2,
            gousto_id='TEST002',
            slug='budget-chicken',
            name='Budget Chicken',
            cooking_time_minutes=25,
            servings=2,
            source_url='http://example.com/2',
            is_active=True
        )
        db_session.add(recipe2)
        db_session.flush()

        # Add ingredients (less expensive)
        ri = RecipeIngredient(recipe_id=2, ingredient_id=1, quantity=Decimal('150'), unit_id=1, display_order=1)
        db_session.add(ri)
        db_session.commit()

        # Find alternatives
        alternatives = estimator.get_budget_alternatives(
            recipe=sample_recipe,
            max_budget=Decimal('10.00'),
            limit=5
        )

        # Should return some alternatives
        assert isinstance(alternatives, list)
        # All alternatives should be under budget
        for recipe, cost in alternatives:
            assert cost <= Decimal('10.00')

    def test_meal_plan_cost_breakdown_simple(self, db_session, sample_recipe):
        """Test meal plan cost estimation with simple plan."""
        estimator = CostEstimator(db_session)

        # Create simple meal plan
        meal_plan = {
            'weeks': [{
                'days': [
                    {
                        'day_number': 1,
                        'meals': {
                            'lunch': sample_recipe,
                            'dinner': sample_recipe
                        }
                    },
                    {
                        'day_number': 2,
                        'meals': {
                            'lunch': sample_recipe,
                            'dinner': sample_recipe
                        }
                    }
                ]
            }]
        }

        breakdown = estimator.estimate_meal_plan_cost(meal_plan, servings_per_meal=2)

        assert isinstance(breakdown, MealPlanCostBreakdown)
        assert breakdown.total > Decimal('0.00')
        assert breakdown.total_meals == 4
        assert breakdown.per_meal_average > Decimal('0.00')
        assert isinstance(breakdown.by_category, dict)
        assert isinstance(breakdown.by_day, dict)
        assert len(breakdown.by_day) == 2  # 2 days

    def test_meal_plan_cost_breakdown_to_dict(self, db_session, sample_recipe):
        """Test converting cost breakdown to dictionary."""
        estimator = CostEstimator(db_session)

        meal_plan = {
            'weeks': [{
                'days': [{
                    'day_number': 1,
                    'meals': {'lunch': sample_recipe}
                }]
            }]
        }

        breakdown = estimator.estimate_meal_plan_cost(meal_plan, servings_per_meal=2)
        result = breakdown.to_dict()

        assert isinstance(result, dict)
        assert 'total' in result
        assert 'by_category' in result
        assert 'by_day' in result
        assert 'per_meal_average' in result
        assert 'savings_suggestions' in result
        assert 'total_meals' in result
        assert 'ingredient_count' in result

        # All numeric values should be floats (not Decimal)
        assert isinstance(result['total'], float)
        assert isinstance(result['per_meal_average'], float)

    def test_savings_suggestions_high_protein_cost(self, db_session):
        """Test savings suggestions for high protein spending."""
        estimator = CostEstimator(db_session)

        by_category = {
            'protein': Decimal('50.00'),
            'vegetable': Decimal('10.00'),
            'grain': Decimal('5.00')
        }

        suggestions = estimator._generate_savings_suggestions(
            by_category=by_category,
            total_cost=Decimal('65.00'),
            meal_count=10
        )

        # Should suggest protein alternatives
        assert len(suggestions) > 0
        assert any('protein' in s.lower() for s in suggestions)

    def test_savings_suggestions_expensive_meals(self, db_session):
        """Test savings suggestions for expensive meals."""
        estimator = CostEstimator(db_session)

        by_category = {'protein': Decimal('40.00'), 'other': Decimal('40.00')}

        suggestions = estimator._generate_savings_suggestions(
            by_category=by_category,
            total_cost=Decimal('80.00'),
            meal_count=5  # £16 per meal
        )

        # Should suggest ways to reduce cost
        assert len(suggestions) > 0
        assert any('cost per meal' in s.lower() or 'average cost' in s.lower() for s in suggestions)

    def test_savings_suggestions_economical_plan(self, db_session):
        """Test savings suggestions for economical meal plan."""
        estimator = CostEstimator(db_session)

        by_category = {'protein': Decimal('20.00'), 'vegetable': Decimal('15.00')}

        suggestions = estimator._generate_savings_suggestions(
            by_category=by_category,
            total_cost=Decimal('35.00'),
            meal_count=10  # £3.50 per meal
        )

        # Should provide positive feedback
        assert len(suggestions) > 0
        assert any('great' in s.lower() or 'economical' in s.lower() for s in suggestions)

    def test_price_caching(self, db_session, sample_recipe):
        """Test that prices are cached for performance."""
        estimator = CostEstimator(db_session)

        # First call - cache should be empty
        assert len(estimator._price_cache) == 0

        # Estimate cost with caching
        estimator.estimate_recipe_cost(sample_recipe, servings=2, use_cache=True)

        # Cache should now have entries
        assert len(estimator._price_cache) > 0

        # Second call should use cache
        cache_size_before = len(estimator._price_cache)
        estimator.estimate_recipe_cost(sample_recipe, servings=2, use_cache=True)
        cache_size_after = len(estimator._price_cache)

        # Cache size should be same (reused cached values)
        assert cache_size_before == cache_size_after

    def test_recipe_without_ingredients(self, db_session):
        """Test cost estimation for recipe without ingredients."""
        estimator = CostEstimator(db_session)

        # Create recipe without ingredients
        recipe = Recipe(
            id=99,
            gousto_id='TEST099',
            slug='empty-recipe',
            name='Empty Recipe',
            cooking_time_minutes=10,
            servings=2,
            source_url='http://example.com/99',
            is_active=True
        )
        db_session.add(recipe)
        db_session.commit()

        cost = estimator.estimate_recipe_cost(recipe, servings=2)

        # Should return default estimate
        assert cost == Decimal('5.00')

    def test_estimate_with_no_quantity(self, db_session, sample_ingredients):
        """Test ingredient price estimation with no quantity."""
        estimator = CostEstimator(db_session)

        ingredient = sample_ingredients[0]
        cost = estimator.estimate_ingredient_price(ingredient, quantity=None, unit=None)

        # Should return small default amount
        assert cost == Decimal('0.50')


class TestMealPlanCostBreakdown:
    """Test MealPlanCostBreakdown class."""

    def test_initialization(self):
        """Test cost breakdown initialization."""
        breakdown = MealPlanCostBreakdown(
            total=Decimal('50.00'),
            by_category={'protein': Decimal('30.00'), 'vegetable': Decimal('20.00')},
            by_day={1: Decimal('25.00'), 2: Decimal('25.00')},
            per_meal_average=Decimal('10.00'),
            savings_suggestions=['Test suggestion'],
            total_meals=5,
            ingredient_count=15
        )

        assert breakdown.total == Decimal('50.00')
        assert breakdown.total_meals == 5
        assert breakdown.ingredient_count == 15
        assert len(breakdown.savings_suggestions) == 1

    def test_to_dict_conversion(self):
        """Test converting breakdown to dictionary."""
        breakdown = MealPlanCostBreakdown(
            total=Decimal('50.00'),
            by_category={'protein': Decimal('30.00')},
            by_day={1: Decimal('50.00')},
            per_meal_average=Decimal('10.00'),
            savings_suggestions=[],
            total_meals=5,
            ingredient_count=15
        )

        result = breakdown.to_dict()

        assert isinstance(result, dict)
        assert result['total'] == 50.00
        assert result['per_meal_average'] == 10.00
        assert result['total_meals'] == 5
        assert result['ingredient_count'] == 15
