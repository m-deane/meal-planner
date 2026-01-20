# Multi-Week Meal Planning & Cost Estimation API Guide

## Overview

This guide covers the new multi-week meal planning and cost estimation endpoints.

## Multi-Week Planning Endpoints

### Generate Multi-Week Meal Plan

Generate a meal plan spanning 1-12 weeks with sophisticated variety enforcement.

**Endpoint**: `POST /meal-plans/generate-multi-week`

**Query Parameters**:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `weeks` | int | 4 | 1-12 | Number of weeks to plan |
| `min_protein_score` | float | 40.0 | 0-100 | Minimum protein score |
| `max_carb_score` | float | 40.0 | 0-100 | Maximum carb score |
| `include_breakfast` | bool | true | - | Include breakfast meals |
| `include_lunch` | bool | true | - | Include lunch meals |
| `include_dinner` | bool | true | - | Include dinner meals |
| `min_days_between_repeat` | int | 7 | 1-30 | Min days before repeating recipe |
| `max_same_cuisine_per_week` | int | 3 | 1-21 | Max same cuisine recipes per week |
| `max_same_protein_per_week` | int | 3 | 1-21 | Max same protein recipes per week |
| `protein_rotation` | bool | true | - | Enable protein rotation |
| `include_cost_estimate` | bool | false | - | Include cost breakdown |

**Example Request**:
```bash
curl -X POST "http://localhost:8000/meal-plans/generate-multi-week?weeks=4&min_days_between_repeat=10&max_same_cuisine_per_week=2&include_cost_estimate=true"
```

**Response Structure**:
```json
{
  "success": true,
  "weeks": [
    {
      "week_number": 1,
      "days": [
        {
          "day_name": "Monday",
          "day_number": 1,
          "meals": {
            "breakfast": {...},
            "lunch": {...},
            "dinner": {...}
          }
        }
      ],
      "protein_distribution": {
        "chicken": 3,
        "beef": 2,
        "fish": 2
      },
      "cuisine_distribution": {
        "italian": 2,
        "asian": 3,
        "mexican": 2
      }
    }
  ],
  "total_weeks": 4,
  "total_days": 28,
  "variety_score": 82.5,
  "summary": {
    "total_meals": 84,
    "unique_recipes": 76,
    "recipe_reuse_count": 8,
    "average_cooking_time": 28.5,
    "total_cooking_time": 2394
  },
  "constraints": {
    "min_protein_score": 40.0,
    "max_carb_score": 40.0,
    "min_days_between_repeat": 10,
    "max_same_cuisine_per_week": 2,
    "max_same_protein_per_week": 2,
    "protein_rotation": true
  },
  "cost_breakdown": {
    "total": 285.50,
    "by_category": {
      "protein": 125.00,
      "vegetable": 80.00,
      "grain": 35.50,
      "dairy": 30.00,
      "other": 15.00
    },
    "by_day": {...},
    "per_meal_average": 3.40,
    "savings_suggestions": [
      "Consider cheaper protein sources...",
      "Add more seasonal vegetables..."
    ],
    "total_meals": 84,
    "ingredient_count": 156
  }
}
```

### Calculate Variety Score

Analyze an existing meal plan and get variety metrics.

**Endpoint**: `POST /meal-plans/calculate-variety-score`

**Request Body**:
```json
{
  "weeks": [
    {
      "days": [
        {
          "day_number": 1,
          "meals": {
            "lunch": {"id": 123},
            "dinner": {"id": 456}
          }
        }
      ]
    }
  ]
}
```

**Response**:
```json
{
  "variety_score": 78.5,
  "breakdown": {
    "total_meals": 21,
    "unique_recipes": 18,
    "repetition_rate": 14.3
  },
  "recommendations": [
    "Good variety! Consider rotating protein sources more.",
    "Try adding recipes from different cuisines."
  ],
  "grade": "B+"
}
```

### Get Variety Guidelines

Get recommended settings for different planning durations.

**Endpoint**: `GET /meal-plans/variety-guidelines`

**Response**:
```json
{
  "recommendations": {
    "1_week": {
      "min_days_between_repeat": 7,
      "max_same_cuisine_per_week": 3,
      "max_same_protein_per_week": 3,
      "target_variety_score": 60
    },
    "4_weeks": {
      "min_days_between_repeat": 10,
      "max_same_cuisine_per_week": 2,
      "max_same_protein_per_week": 2,
      "target_variety_score": 80
    }
  },
  "variety_score_interpretation": {
    "90-100": "Excellent - Outstanding variety",
    "80-89": "Very Good - Strong variety",
    "70-79": "Good - Adequate variety"
  },
  "protein_rotation_tips": [...],
  "cuisine_variety_tips": [...],
  "ingredient_diversity_tips": [...]
}
```

## Cost Estimation Endpoints

### Get Recipe Cost

Get cost estimate for a specific recipe.

**Endpoint**: `GET /cost/recipes/{recipe_id}`

**Query Parameters**:
- `servings` (int, default: 2): Number of servings

**Example**:
```bash
curl "http://localhost:8000/cost/recipes/123?servings=4"
```

**Response**:
```json
{
  "recipe_id": 123,
  "recipe_name": "Chicken Stir Fry",
  "total_cost": 8.50,
  "cost_per_serving": 2.13,
  "servings": 4,
  "estimated": true,
  "cost_breakdown": {
    "protein": 4.00,
    "vegetable": 2.50,
    "grain": 1.00,
    "other": 1.00
  },
  "missing_prices": 2
}
```

### Estimate Meal Plan Cost

Get comprehensive cost breakdown for a meal plan.

**Endpoint**: `POST /cost/meal-plans/estimate`

**Request Body**:
```json
{
  "recipe_ids": [123, 456, 789],
  "servings_per_meal": 2
}
```

Or with full meal plan data:
```json
{
  "meal_plan_data": {
    "weeks": [...]
  },
  "servings_per_meal": 2
}
```

**Response**:
```json
{
  "total": 125.50,
  "by_category": {
    "protein": 55.00,
    "vegetable": 30.00,
    "grain": 15.50,
    "dairy": 18.00,
    "other": 7.00
  },
  "by_day": {
    "1": 18.50,
    "2": 17.25,
    "3": 19.00
  },
  "per_meal_average": 5.98,
  "per_day_average": 17.93,
  "savings_suggestions": [
    "Protein accounts for 44% of costs. Consider cheaper proteins.",
    "Add more seasonal vegetables for variety."
  ],
  "total_meals": 21,
  "ingredient_count": 45
}
```

### Get Budget Recipes

Find recipes within a budget constraint.

**Endpoint**: `GET /cost/recipes/budget`

**Query Parameters**:
- `max_cost` (float, required): Maximum cost per serving (GBP)
- `limit` (int, default: 20, range: 1-100): Max recipes to return

**Example**:
```bash
curl "http://localhost:8000/cost/recipes/budget?max_cost=5.00&limit=20"
```

**Response**:
```json
{
  "recipes": [
    {
      "recipe": {
        "id": 1,
        "name": "Budget Pasta",
        "slug": "budget-pasta",
        "cooking_time_minutes": 20,
        "difficulty": "easy",
        "servings": 2
      },
      "cost": 4.50,
      "cost_per_serving": 2.25
    }
  ],
  "total_count": 15,
  "max_cost": 5.00,
  "average_cost": 3.75
}
```

### Get Budget Alternatives

Find cheaper alternatives to a recipe.

**Endpoint**: `GET /cost/recipes/{recipe_id}/alternatives`

**Query Parameters**:
- `max_budget` (float, optional): Max budget per serving (defaults to 80% of original)
- `limit` (int, default: 10, range: 1-50): Number of alternatives

**Example**:
```bash
curl "http://localhost:8000/cost/recipes/123/alternatives?max_budget=4.00&limit=10"
```

**Response**:
```json
{
  "recipes": [
    {
      "recipe": {...},
      "cost": 6.00,
      "cost_per_serving": 3.00
    }
  ],
  "total_count": 8,
  "max_cost": 4.00,
  "average_cost": 3.25
}
```

## Variety Score Interpretation

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 95-100 | A+ | Outstanding diversity |
| 90-94 | A | Excellent variety |
| 85-89 | A- | Very strong variety |
| 80-84 | B+ | Strong variety |
| 75-79 | B | Good variety |
| 70-74 | B- | Adequate variety |
| 65-69 | C+ | Fair variety |
| 60-64 | C | Moderate variety |
| 55-59 | C- | Limited variety |
| 50-54 | D | Poor variety |
| 0-49 | F | Very poor variety |

## Variety Score Components

- **Recipe Variety** (40 points): Unique vs repeated recipes
- **Protein Variety** (25 points): Different protein sources (8+ types = max)
- **Cuisine Variety** (20 points): Different cuisine types (6+ = max)
- **Ingredient Variety** (15 points): Unique ingredients (50+ = max)

## Cost Estimation Notes

### Price Sources
1. **Database Prices**: Actual prices from `ingredient_prices` table (preferred)
2. **Fallback Estimation**: Category-based defaults when prices missing

### Default Price Estimates (GBP per 100g)
- Protein: £2.50
- Vegetables: £0.80
- Fruits: £1.20
- Grains: £0.40
- Dairy: £1.50
- Spices/Herbs: £0.15-0.20
- Other: £1.00

### Savings Suggestions Triggers
- **High Protein Cost**: >50% of total budget → suggest alternatives
- **Expensive Meals**: >£8 per meal → suggest seasonal/bulk options
- **Low Vegetable Cost**: <15% of budget → suggest adding more vegetables
- **Economical Plan**: <£4 per meal → positive feedback

## Best Practices

### For 1-Week Plans
```
min_days_between_repeat: 7
max_same_cuisine_per_week: 3
max_same_protein_per_week: 3
target_variety_score: 60+
```

### For 4-Week Plans
```
min_days_between_repeat: 10
max_same_cuisine_per_week: 2
max_same_protein_per_week: 2
target_variety_score: 80+
```

### For 8+ Week Plans
```
min_days_between_repeat: 14
max_same_cuisine_per_week: 2
max_same_protein_per_week: 2
target_variety_score: 85+
```

## Error Handling

### Common Error Codes

**400 Bad Request**:
```json
{
  "detail": "weeks must be between 1 and 12"
}
```

**404 Not Found**:
```json
{
  "detail": "Recipe with ID 999 not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to generate multi-week meal plan: <error details>"
}
```

## Performance Tips

1. **Cost Estimation**: Set `include_cost_estimate=false` if not needed
2. **Limit Recipe Pool**: Use appropriate score thresholds
3. **Caching**: Cost prices are cached during estimation
4. **Batch Requests**: Generate longer plans (4+ weeks) instead of multiple short plans

## Integration Examples

### Python Client
```python
import requests

# Generate 4-week plan with cost
response = requests.post(
    "http://localhost:8000/meal-plans/generate-multi-week",
    params={
        "weeks": 4,
        "min_days_between_repeat": 10,
        "include_cost_estimate": True
    }
)

plan = response.json()
print(f"Variety Score: {plan['variety_score']}")
print(f"Total Cost: £{plan['cost_breakdown']['total']:.2f}")
```

### JavaScript/TypeScript
```javascript
const response = await fetch(
  'http://localhost:8000/meal-plans/generate-multi-week?' +
  new URLSearchParams({
    weeks: '4',
    min_days_between_repeat: '10',
    include_cost_estimate: 'true'
  }),
  { method: 'POST' }
);

const plan = await response.json();
console.log(`Variety Score: ${plan.variety_score}`);
console.log(`Total Cost: £${plan.cost_breakdown.total.toFixed(2)}`);
```

## Rate Limiting

Standard API rate limits apply:
- Default: 100 requests per minute
- Multi-week generation: CPU-intensive, recommend max 10/minute
- Cost estimation: Moderate usage, 50/minute

## Support

For issues or questions:
- API Documentation: `/docs` (when in debug mode)
- GitHub Issues: [repository link]
- Email: support@example.com
