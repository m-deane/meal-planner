# Multi-Week Meal Planning & Cost Estimation Implementation

**Date**: 2026-01-20
**Status**: ✅ Complete
**Test Coverage**: 33/33 tests passing

## Overview

Implemented comprehensive multi-week meal planning with variety enforcement and cost estimation features for the meal-planner project.

## Features Implemented

### 1. Multi-Week Meal Planning (`src/meal_planner/multi_week_planner.py`)

#### VarietyConfig Class
Configuration object for variety enforcement with customizable parameters:
- `min_days_between_repeat`: Minimum days before repeating recipes (default: 7)
- `max_same_cuisine_per_week`: Max recipes from same cuisine per week (default: 3)
- `protein_rotation`: Enable protein source rotation (default: True)
- `max_same_protein_per_week`: Max recipes with same protein per week (default: 3)
- `enforce_ingredient_variety`: Track ingredient diversity (default: True)

#### MultiWeekPlanner Class
Extends base `MealPlanner` with advanced variety features:

**Key Methods**:
- `generate_multi_week_plan()`: Generate 1-12 week meal plans with variety constraints
- `_get_protein_type()`: Detect protein sources (chicken, beef, fish, vegetarian, etc.)
- `_get_cuisine()`: Identify cuisine types from categories and keywords
- `_calculate_variety_score()`: Score plans 0-100 based on diversity
- `_enforce_variety_constraints()`: Filter recipes based on variety rules

**Variety Scoring Breakdown**:
- Recipe variety: 0-40 points (unique vs repeated recipes)
- Protein variety: 0-25 points (8+ protein types = max score)
- Cuisine variety: 0-20 points (6+ cuisines = max score)
- Ingredient variety: 0-15 points (50+ ingredients = max score)

**Protein Detection**:
- Chicken, beef, pork, fish, seafood, lamb, turkey, duck
- Vegetarian (tofu, tempeh, seitan)
- Legumes (lentils, chickpeas, beans)

**Cuisine Detection**:
- Italian, Asian, Mexican, Indian, Mediterranean
- American, French, British, Thai, Chinese, Japanese
- Middle Eastern

### 2. Cost Estimation (`src/meal_planner/cost_estimator.py`)

#### CostEstimator Class
Intelligent cost estimation with database prices and fallback estimation:

**Key Methods**:
- `estimate_recipe_cost()`: Calculate recipe cost with serving scaling
- `estimate_meal_plan_cost()`: Comprehensive meal plan cost breakdown
- `get_budget_alternatives()`: Find cheaper similar recipes
- `get_cheapest_recipes()`: Get recipes sorted by cost
- `estimate_ingredient_price()`: Fallback estimation for missing prices

**Cost Breakdown Features**:
- Total cost calculation
- Cost by ingredient category (protein, vegetables, grains, dairy)
- Cost by day tracking
- Per-meal average cost
- Savings suggestions based on spending patterns

**Default Price Estimates** (GBP per 100g):
- Protein: £2.50
- Vegetable: £0.80
- Fruit: £1.20
- Grain: £0.40
- Dairy: £1.50
- Spices/Herbs: £0.15-0.20
- Other: £1.00

#### MealPlanCostBreakdown Class
Structured cost breakdown with:
- Total cost
- Category breakdown
- Daily breakdown
- Per-meal average
- Savings suggestions
- Ingredient count

### 3. API Endpoints

#### Cost Router (`src/api/routers/cost.py`)
**Endpoints**:

1. `GET /cost/recipes/{recipe_id}`
   - Get cost estimate for specific recipe
   - Supports serving scaling
   - Returns breakdown by category

2. `POST /cost/meal-plans/estimate`
   - Estimate total meal plan cost
   - Accepts recipe IDs or full meal plan structure
   - Returns comprehensive breakdown with savings suggestions

3. `GET /cost/recipes/budget`
   - Find recipes within budget constraint
   - Sort by cost (cheapest first)
   - Configurable limit

4. `GET /cost/recipes/{recipe_id}/alternatives`
   - Get cheaper alternatives to a recipe
   - Similar characteristics (cooking time, servings)
   - Budget-based filtering

#### Multi-Week Router (`src/api/routers/multi_week.py`)
**Endpoints**:

1. `POST /meal-plans/generate-multi-week`
   - Generate 1-12 week meal plans
   - Variety enforcement parameters
   - Optional cost estimation
   - Returns variety score and summary

2. `POST /meal-plans/calculate-variety-score`
   - Analyze existing meal plan
   - Detailed variety breakdown
   - Improvement recommendations
   - Letter grade (A+ to F)

3. `GET /meal-plans/variety-guidelines`
   - Best practice recommendations
   - Settings for different durations
   - Variety score interpretation
   - Tips for maximizing diversity

### 4. API Schemas (`src/api/schemas/cost.py`)

**Request Schemas**:
- `CostEstimateRequest`: Request cost estimation
- `BudgetConstraint`: Budget constraints for planning

**Response Schemas**:
- `RecipeCostResponse`: Recipe cost with breakdown
- `MealPlanCostBreakdown`: Comprehensive cost analysis
- `RecipeWithCost`: Recipe with cost information
- `BudgetRecipesResponse`: Budget-filtered recipes
- `CostComparisonResponse`: Cost comparison between options

## Testing

### Test Coverage: 33/33 tests (100% passing)

#### Multi-Week Planner Tests (`tests/unit/test_multi_week_planner.py`)
- VarietyConfig initialization and defaults
- MultiWeekPlanner initialization and validation
- Protein type detection (chicken, beef, fish, vegetarian)
- Cuisine type detection (Italian, Asian, Mexican)
- Single and multi-week plan generation
- Variety score calculation
- Recipe exclusion functionality
- Summary statistics generation
- Protein rotation enforcement
- Cuisine variety enforcement
- Recipe repetition minimization

#### Cost Estimator Tests (`tests/unit/test_cost_estimator.py`)
- CostEstimator initialization
- Recipe cost estimation with database prices
- Cost scaling by servings
- Ingredient price estimation (database + fallback)
- Quantity conversion (weight, volume, count)
- Cheapest recipe queries
- Budget alternative finding
- Meal plan cost breakdown
- Savings suggestions generation
- Price caching for performance
- Edge cases (missing data, no ingredients)

## File Structure

```
meal-planner/
├── src/
│   ├── meal_planner/
│   │   ├── multi_week_planner.py      # Multi-week planning with variety
│   │   └── cost_estimator.py          # Cost estimation logic
│   └── api/
│       ├── routers/
│       │   ├── cost.py                # Cost estimation endpoints
│       │   ├── multi_week.py          # Multi-week planning endpoints
│       │   └── __init__.py            # Updated with new routers
│       ├── schemas/
│       │   ├── cost.py                # Cost schemas
│       │   └── __init__.py            # Updated with cost schemas
│       └── main.py                    # Updated to register routers
└── tests/
    └── unit/
        ├── test_multi_week_planner.py # Multi-week tests (14 tests)
        └── test_cost_estimator.py     # Cost estimator tests (19 tests)
```

## Key Design Decisions

### 1. Variety Enforcement Strategy
- **Configurable constraints**: Allow customization for different use cases
- **Multi-dimensional variety**: Track proteins, cuisines, and ingredients
- **Graceful degradation**: Relax constraints when recipe pool is limited
- **Intelligent caching**: Pre-cache protein/cuisine types for performance

### 2. Cost Estimation Approach
- **Database-first**: Use actual prices when available
- **Intelligent fallback**: Category-based estimation for missing prices
- **Unit conversion**: Standardize to grams for consistent pricing
- **Savings suggestions**: Provide actionable cost-reduction advice

### 3. API Design
- **RESTful endpoints**: Clear, resource-oriented URLs
- **Flexible input**: Support both simple and complex meal plan structures
- **Comprehensive responses**: Include variety scores, costs, and suggestions
- **Query parameters**: Fine-tune variety and cost constraints

## Usage Examples

### Generate 4-Week Plan with Cost Estimate

```python
from src.database.connection import get_session
from src.meal_planner.multi_week_planner import MultiWeekPlanner, VarietyConfig
from src.meal_planner.cost_estimator import CostEstimator

session = get_session()

# Configure variety
config = VarietyConfig(
    min_days_between_repeat=10,
    max_same_cuisine_per_week=2,
    max_same_protein_per_week=2
)

# Generate plan
planner = MultiWeekPlanner(session, weeks=4, variety_config=config)
plan = planner.generate_multi_week_plan(
    min_protein_score=40.0,
    max_carb_score=40.0
)

# Estimate cost
estimator = CostEstimator(session)
cost_breakdown = estimator.estimate_meal_plan_cost(plan)

print(f"Variety Score: {plan['variety_scores']['overall']:.1f}/100")
print(f"Total Cost: £{cost_breakdown.total:.2f}")
print(f"Per Meal: £{cost_breakdown.per_meal_average:.2f}")
```

### API Request Examples

**Generate Multi-Week Plan**:
```bash
POST /meal-plans/generate-multi-week?weeks=4&min_days_between_repeat=10&include_cost_estimate=true
```

**Get Budget Recipes**:
```bash
GET /cost/recipes/budget?max_cost=5.00&limit=20
```

**Find Cheaper Alternatives**:
```bash
GET /cost/recipes/123/alternatives?max_budget=4.50&limit=10
```

## Performance Optimizations

1. **Price Caching**: Cache ingredient prices during meal plan generation
2. **Pre-computation**: Calculate protein/cuisine types upfront
3. **Batch Processing**: Process recipes in bulk for variety checking
4. **Lazy Loading**: Use SQLAlchemy selectin loading for relationships

## Future Enhancements

### Potential Improvements
1. **Machine Learning**: Learn user preferences over time
2. **Seasonal Pricing**: Adjust cost estimates based on seasonal availability
3. **Nutritional Optimization**: Balance variety with nutritional targets
4. **Shopping List Integration**: Generate optimized shopping lists from plans
5. **Recipe Substitution**: Smart swapping based on cost/variety constraints
6. **User Feedback**: Track which recipes are actually cooked
7. **Waste Reduction**: Optimize ingredient reuse across meals

### Database Enhancements
1. **Price History**: Track price trends over time
2. **Regional Pricing**: Support different locations
3. **Store Integration**: Pull real-time prices from grocery APIs
4. **Allergen Costs**: Track pricing for allergen-free alternatives

## Maintenance Notes

### Regular Updates Required
- **Ingredient Prices**: Update price database monthly
- **Default Estimates**: Review and adjust category defaults quarterly
- **Variety Thresholds**: Monitor variety scores and adjust constraints
- **Test Data**: Keep test fixtures updated with realistic data

### Monitoring Recommendations
- Track variety scores across generated plans
- Monitor cost estimation accuracy
- Log variety constraint violations
- Measure API response times

## Conclusion

Successfully implemented comprehensive multi-week meal planning with:
- ✅ Sophisticated variety enforcement (recipe, protein, cuisine, ingredient)
- ✅ Intelligent cost estimation with fallback logic
- ✅ RESTful API endpoints with comprehensive documentation
- ✅ Pydantic schemas for validation
- ✅ 33 passing unit tests with edge case coverage
- ✅ Production-ready error handling

The implementation provides a solid foundation for advanced meal planning features while maintaining flexibility and performance.
