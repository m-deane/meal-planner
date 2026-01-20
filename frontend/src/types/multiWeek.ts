/**
 * Multi-week meal planning TypeScript types.
 */

import type { MealPlanResponse, NutritionConstraints, MealPreferences } from './mealPlan';

// ============================================================================
// MULTI-WEEK PLAN TYPES
// ============================================================================

export interface WeekPlanSummary {
  week_number: number;
  start_date: string;
  end_date: string;
  total_recipes: number;
  unique_recipes: number;
  total_cost: number;
  variety_score: number;
}

export interface MultiWeekPlan {
  id: number;
  user_id: number;
  name: string;
  weeks_count: number;
  start_date: string;
  end_date: string;
  weeks: MealPlanResponse[];
  week_summaries: WeekPlanSummary[];
  overall_variety_score: number;
  total_cost: number;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// VARIETY ANALYSIS TYPES
// ============================================================================

export interface VarietyMetrics {
  unique_recipes_count: number;
  total_recipes_count: number;
  recipe_repetition_rate: number;
  unique_proteins: string[];
  protein_diversity_score: number;
  unique_cuisines: string[];
  cuisine_diversity_score: number;
  unique_cooking_methods: string[];
  cooking_method_diversity: number;
  overall_variety_score: number;
}

export interface VarietyBreakdown {
  metrics: VarietyMetrics;
  suggestions: VarietySuggestion[];
  score_interpretation: 'excellent' | 'good' | 'fair' | 'poor';
  score_color: 'green' | 'yellow' | 'orange' | 'red';
}

export interface VarietySuggestion {
  category: 'recipe' | 'protein' | 'cuisine' | 'method';
  message: string;
  priority: 'high' | 'medium' | 'low';
}

// ============================================================================
// MULTI-WEEK GENERATION REQUEST
// ============================================================================

export interface MultiWeekGenerateRequest {
  weeks_count: number;
  start_date: string;
  name?: string;
  nutrition_constraints?: NutritionConstraints;
  meal_preferences?: MealPreferences;
  budget_per_week?: number;
  variety_preferences?: {
    minimize_repetition: boolean;
    protein_variety_weight: number;
    cuisine_variety_weight: number;
    max_recipe_repeat_frequency: number;
  };
  exclude_recipe_ids?: number[];
}

export interface MultiWeekUpdateRequest {
  name?: string;
  weeks?: MealPlanResponse[];
}
