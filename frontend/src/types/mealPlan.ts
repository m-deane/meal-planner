/**
 * Meal plan types matching backend schemas.
 */

import { RecipeListItem, Nutrition } from './recipe';

// ============================================================================
// ENUMS
// ============================================================================

export enum MealType {
  BREAKFAST = 'breakfast',
  LUNCH = 'lunch',
  DINNER = 'dinner',
  SNACK = 'snack',
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface NutritionConstraints {
  target_calories?: number;
  min_calories?: number;
  max_calories?: number;
  target_protein_g?: number;
  min_protein_g?: number;
  max_protein_g?: number;
  target_carbs_g?: number;
  min_carbs_g?: number;
  max_carbs_g?: number;
  target_fat_g?: number;
  min_fat_g?: number;
  max_fat_g?: number;
  max_sugar_g?: number;
  max_sodium_mg?: number;
  min_fiber_g?: number;
}

export interface MealPreferences {
  include_breakfast: boolean;
  include_lunch: boolean;
  include_dinner: boolean;
  include_snacks: boolean;
  breakfast_calories_pct?: number;
  lunch_calories_pct?: number;
  dinner_calories_pct?: number;
}

export interface MealPlanGenerateRequest {
  days: number;
  start_date?: string;
  meal_preferences: MealPreferences;
  nutrition_constraints?: NutritionConstraints;
  dietary_tag_ids?: number[];
  dietary_tag_slugs?: string[];
  exclude_allergen_ids?: number[];
  exclude_allergen_names?: string[];
  category_ids?: number[];
  category_slugs?: string[];
  max_cooking_time?: number;
  difficulty_levels?: string[];
  avoid_duplicate_recipes: boolean;
  max_recipe_reuse: number;
  variety_score_weight: number;
  optimize_shopping_list: boolean;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface MealSlot {
  meal_type: MealType;
  recipe: RecipeListItem;
  servings: number;
  nutrition: Nutrition | null;
  notes: string | null;
}

export interface DayPlan {
  day: number;
  date: string | null;
  meals: MealSlot[];
  daily_nutrition: Nutrition | null;
  notes: string | null;
}

export interface ShoppingListPreview {
  total_items: number;
  total_categories: number;
  sample_items: string[];
}

export interface MealPlanSummary {
  total_recipes: number;
  unique_recipes: number;
  total_meals: number;
  average_cooking_time: number | null;
  difficulty_distribution: Record<string, number>;
}

export interface MealPlanResponse {
  id: number | null;
  days: DayPlan[];
  total_days: number;
  start_date: string | null;
  end_date: string | null;
  average_daily_nutrition: Nutrition | null;
  total_nutrition: Nutrition | null;
  summary: MealPlanSummary;
  shopping_list_preview: ShoppingListPreview | null;
  created_at: string | null;
  constraints_used: Record<string, unknown> | null;
}
