"""
Cost estimation schemas for API endpoints.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from .recipe import RecipeListItem


class CostBreakdownByCategory(BaseModel):
    """Cost breakdown by ingredient category."""

    protein: Optional[float] = Field(None, description="Cost of protein ingredients")
    vegetable: Optional[float] = Field(None, description="Cost of vegetables")
    grain: Optional[float] = Field(None, description="Cost of grains")
    dairy: Optional[float] = Field(None, description="Cost of dairy products")
    other: Optional[float] = Field(None, description="Cost of other ingredients")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "protein": 15.50,
                    "vegetable": 8.20,
                    "grain": 3.50,
                    "dairy": 6.00,
                    "other": 4.30
                }
            ]
        }
    }


class RecipeCostResponse(BaseModel):
    """Cost estimate for a single recipe."""

    recipe_id: int = Field(..., description="Recipe ID")
    recipe_name: str = Field(..., description="Recipe name")
    total_cost: float = Field(..., ge=0, description="Total cost for recipe (GBP)")
    cost_per_serving: float = Field(..., ge=0, description="Cost per serving (GBP)")
    servings: int = Field(..., ge=1, description="Number of servings")
    estimated: bool = Field(
        True,
        description="Whether cost is estimated (true) or from actual prices (false)"
    )
    cost_breakdown: Optional[Dict[str, float]] = Field(
        None,
        description="Cost breakdown by ingredient category"
    )
    missing_prices: Optional[int] = Field(
        None,
        description="Number of ingredients with estimated prices"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "recipe_id": 123,
                    "recipe_name": "Chicken Stir Fry",
                    "total_cost": 8.50,
                    "cost_per_serving": 4.25,
                    "servings": 2,
                    "estimated": True,
                    "cost_breakdown": {
                        "protein": 4.00,
                        "vegetable": 2.50,
                        "other": 2.00
                    },
                    "missing_prices": 3
                }
            ]
        }
    )


class MealPlanCostBreakdown(BaseModel):
    """Detailed cost breakdown for a meal plan."""

    total: float = Field(..., ge=0, description="Total cost for entire meal plan (GBP)")
    by_category: Dict[str, float] = Field(
        ...,
        description="Cost breakdown by ingredient category"
    )
    by_day: Dict[int, float] = Field(
        ...,
        description="Cost breakdown by day number"
    )
    per_meal_average: float = Field(..., ge=0, description="Average cost per meal (GBP)")
    per_day_average: Optional[float] = Field(None, ge=0, description="Average cost per day (GBP)")
    savings_suggestions: List[str] = Field(
        default_factory=list,
        description="Cost-saving suggestions"
    )
    total_meals: int = Field(..., ge=0, description="Total number of meals")
    ingredient_count: int = Field(..., ge=0, description="Total unique ingredients")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
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
                        "Consider cheaper protein sources like chicken or eggs",
                        "Add more seasonal vegetables for variety"
                    ],
                    "total_meals": 21,
                    "ingredient_count": 45
                }
            ]
        }
    )


class CostEstimateRequest(BaseModel):
    """Request for cost estimation."""

    recipe_ids: Optional[List[int]] = Field(
        None,
        description="List of recipe IDs to estimate cost for"
    )
    meal_plan_data: Optional[Dict] = Field(
        None,
        description="Meal plan data structure"
    )
    servings_per_meal: int = Field(
        2,
        ge=1,
        le=12,
        description="Number of servings per meal"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipe_ids": [1, 5, 12, 18],
                    "servings_per_meal": 2
                }
            ]
        }
    }


class BudgetConstraint(BaseModel):
    """Budget constraints for meal planning."""

    max_total_budget: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum total budget (GBP)"
    )
    max_per_meal: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum cost per meal (GBP)"
    )
    max_per_day: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum cost per day (GBP)"
    )
    preferred_protein_budget_pct: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Target percentage of budget for protein (0-100)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "max_total_budget": 100.00,
                    "max_per_meal": 5.00,
                    "max_per_day": 15.00,
                    "preferred_protein_budget_pct": 40.0
                }
            ]
        }
    }


class RecipeWithCost(BaseModel):
    """Recipe with cost information."""

    recipe: RecipeListItem = Field(..., description="Recipe details")
    cost: float = Field(..., ge=0, description="Estimated cost (GBP)")
    cost_per_serving: float = Field(..., ge=0, description="Cost per serving (GBP)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
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
            ]
        }
    )


class BudgetRecipesResponse(BaseModel):
    """Response for budget recipe queries."""

    recipes: List[RecipeWithCost] = Field(..., description="Recipes sorted by cost")
    total_count: int = Field(..., ge=0, description="Total number of matching recipes")
    max_cost: float = Field(..., ge=0, description="Maximum cost filter applied")
    average_cost: Optional[float] = Field(None, description="Average cost across results")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipes": [],
                    "total_count": 15,
                    "max_cost": 5.00,
                    "average_cost": 3.75
                }
            ]
        }
    }


class CostComparisonResponse(BaseModel):
    """Cost comparison between recipes or meal plans."""

    original_cost: float = Field(..., ge=0, description="Cost of original item")
    alternative_cost: float = Field(..., ge=0, description="Cost of alternative")
    savings: float = Field(..., description="Savings amount (can be negative)")
    savings_percentage: float = Field(..., description="Savings as percentage")
    recommendation: str = Field(..., description="Recommendation text")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "original_cost": 8.50,
                    "alternative_cost": 6.25,
                    "savings": 2.25,
                    "savings_percentage": 26.5,
                    "recommendation": "Switch to alternative to save £2.25 (26.5%)"
                }
            ]
        }
    }
