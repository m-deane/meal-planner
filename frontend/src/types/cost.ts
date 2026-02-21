/**
 * Cost estimation TypeScript types for recipe and meal plan budgeting.
 */

import type { RecipeListItem } from './recipe';

// ============================================================================
// RECIPE COST TYPES
// ============================================================================

/**
 * Cost estimate for a single recipe.
 * Matches backend RecipeCostResponse schema:
 * { recipe_id, recipe_name, total_cost, cost_per_serving, servings,
 *   estimated, cost_breakdown, missing_prices }
 */
export interface RecipeCost {
  recipe_id: number;
  recipe_name: string;
  total_cost: number;
  cost_per_serving: number;
  servings: number;
  estimated: boolean;
  cost_breakdown: Record<string, number> | null;
  missing_prices: number | null;
}

// ============================================================================
// MEAL PLAN COST TYPES
// ============================================================================

/**
 * Detailed cost breakdown for a meal plan.
 * Matches backend MealPlanCostBreakdown schema:
 * { total, by_category, by_day, per_meal_average, per_day_average,
 *   savings_suggestions, total_meals, ingredient_count }
 */
export interface MealPlanCostBreakdown {
  total: number;
  by_category: Record<string, number>;
  by_day: Record<number, number>;
  per_meal_average: number;
  per_day_average: number | null;
  savings_suggestions: string[];
  total_meals: number;
  ingredient_count: number;
}

// ============================================================================
// BUDGET RECIPE TYPES
// ============================================================================

/**
 * A recipe paired with its cost information.
 * Matches backend RecipeWithCost schema.
 */
export interface RecipeWithCost {
  recipe: RecipeListItem;
  cost: number;
  cost_per_serving: number;
}

/**
 * Response for budget recipe queries.
 * Matches backend BudgetRecipesResponse schema:
 * { recipes, total_count, max_cost, average_cost }
 */
export interface BudgetRecipesResponse {
  recipes: RecipeWithCost[];
  total_count: number;
  max_cost: number;
  average_cost: number | null;
}

// ============================================================================
// COST ALTERNATIVES TYPES
// ============================================================================

/**
 * Response for cheaper recipe alternatives.
 * The alternatives endpoint uses the same BudgetRecipesResponse shape:
 * { recipes, total_count, max_cost, average_cost }
 */
export type CostAlternativesResponse = BudgetRecipesResponse;

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface RecipeCostRequest {
  recipe_id: number;
  servings?: number;
}

export interface MealPlanCostRequest {
  meal_plan_id?: number;
  recipe_ids?: number[];
  start_date?: string;
  end_date?: string;
  budget?: number;
}

export interface BudgetRecipesRequest {
  max_cost: number;
  max_cost_per_serving?: number;
  servings?: number;
  limit?: number;
  offset?: number;
}

export interface CostAlternativesRequest {
  recipe_id: number;
  max_budget: number;
  max_results?: number;
  preserve_dietary_tags?: boolean;
  preserve_allergens?: boolean;
}
