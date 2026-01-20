/**
 * Cost estimation TypeScript types for recipe and meal plan budgeting.
 */

// ============================================================================
// RECIPE COST TYPES
// ============================================================================

export interface IngredientCost {
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  estimated_cost: number;
  cost_per_unit: number;
  cost_confidence: 'high' | 'medium' | 'low';
  notes?: string;
}

export interface RecipeCost {
  recipe_id: number;
  recipe_name: string;
  servings: number;
  total_cost: number;
  cost_per_serving: number;
  ingredient_costs: IngredientCost[];
  last_updated: string;
}

// ============================================================================
// MEAL PLAN COST TYPES
// ============================================================================

export interface DayCostBreakdown {
  date: string;
  total_cost: number;
  breakfast_cost: number;
  lunch_cost: number;
  dinner_cost: number;
  snacks_cost: number;
  recipe_count: number;
}

export interface MealPlanCostBreakdown {
  total_cost: number;
  average_daily_cost: number;
  average_per_meal: number;
  days_covered: number;
  total_servings: number;
  cost_per_serving: number;
  daily_breakdown: DayCostBreakdown[];
  budget_comparison?: {
    budget_amount: number;
    under_over_budget: number;
    budget_utilization_percent: number;
  };
}

// ============================================================================
// BUDGET RECIPE TYPES
// ============================================================================

export interface BudgetRecipe {
  id: number;
  name: string;
  slug: string;
  estimated_cost: number;
  cost_per_serving: number;
  servings: number;
  cooking_time_minutes: number | null;
  difficulty: string | null;
  main_image_url: string | null;
  nutrition_summary: {
    calories?: number | null;
    protein_g?: number | null;
  } | null;
  savings_vs_average: number;
  cost_confidence: 'high' | 'medium' | 'low';
}

export interface BudgetRecipesResponse {
  recipes: BudgetRecipe[];
  average_cost_all_recipes: number;
  max_cost_filter: number;
  count: number;
}

// ============================================================================
// COST ALTERNATIVES TYPES
// ============================================================================

export interface CostAlternative {
  recipe: BudgetRecipe;
  cost_savings: number;
  savings_percent: number;
  similarity_score: number;
  matching_attributes: string[];
}

export interface CostAlternativesResponse {
  original_recipe_id: number;
  original_recipe_name: string;
  original_cost: number;
  alternatives: CostAlternative[];
  max_budget: number;
}

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
