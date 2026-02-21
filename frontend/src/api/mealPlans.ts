/**
 * Meal plan API endpoints.
 */

import { apiClient } from './client';
import type { MealPlanGenerateRequest, MealPlanResponse } from '../types';

/**
 * Extended request type with additional options.
 */
interface ExtendedMealPlanRequest extends MealPlanGenerateRequest {
  useNutritionEndpoint?: boolean;
  mealCounts?: {
    breakfasts: number;
    lunches: number;
    dinners: number;
  };
  nutrition_goals?: {
    daily_calories?: number;
    daily_protein_g?: number;
    daily_carbs_g?: number;
    daily_fat_g?: number;
  };
  include_breakfast?: boolean;
  include_lunch?: boolean;
  include_dinner?: boolean;
}

/**
 * Generate a meal plan based on preferences and constraints.
 * Uses nutrition endpoint when useNutritionEndpoint is true for accurate nutrition data.
 *
 * Both backend endpoints (/generate and /generate-nutrition) accept only query parameters -
 * they have no request body. This function maps the frontend request object to the
 * appropriate query params for each endpoint.
 */
export const generateMealPlan = async (
  options: ExtendedMealPlanRequest
): Promise<MealPlanResponse> => {
  // Determine which endpoint to use
  const useNutritionEndpoint = options.useNutritionEndpoint ?? true;
  const endpoint = useNutritionEndpoint ? '/meal-plans/generate-nutrition' : '/meal-plans/generate';

  // Build query params - both endpoints accept only query params, no request body
  const params = new URLSearchParams();

  // Extract meal preferences (from either top-level convenience fields or nested meal_preferences)
  const includeBreakfast = options.include_breakfast ?? options.meal_preferences?.include_breakfast ?? true;
  const includeLunch = options.include_lunch ?? options.meal_preferences?.include_lunch ?? true;
  const includeDinner = options.include_dinner ?? options.meal_preferences?.include_dinner ?? true;

  params.append('include_breakfast', String(includeBreakfast));
  params.append('include_lunch', String(includeLunch));
  params.append('include_dinner', String(includeDinner));

  if (useNutritionEndpoint) {
    // /generate-nutrition accepts: min_protein_g, max_carbs_g, min_calories, max_calories
    if (options.nutrition_goals?.daily_protein_g) {
      params.append('min_protein_g', String(options.nutrition_goals.daily_protein_g));
    }
    if (options.nutrition_goals?.daily_carbs_g) {
      params.append('max_carbs_g', String(options.nutrition_goals.daily_carbs_g));
    }
    if (options.nutrition_constraints?.target_calories) {
      params.append('min_calories', String(options.nutrition_constraints.target_calories * 0.8));
      params.append('max_calories', String(options.nutrition_constraints.target_calories * 1.2));
    }
  } else {
    // /generate accepts: min_protein_score, max_carb_score
    if (options.nutrition_goals?.daily_protein_g) {
      params.append('min_protein_score', String(options.nutrition_goals.daily_protein_g));
    }
    if (options.nutrition_goals?.daily_carbs_g) {
      params.append('max_carb_score', String(options.nutrition_goals.daily_carbs_g));
    }
  }

  // POST with no body - both endpoints read only from query params
  const response = await apiClient.post<MealPlanResponse>(`${endpoint}?${params.toString()}`);
  return response.data;
};

/**
 * Generate a nutrition-optimized meal plan.
 * Backend /generate-nutrition accepts only query params, no request body.
 * Query params: min_protein_g, max_carbs_g, min_calories, max_calories,
 *               include_breakfast, include_lunch, include_dinner
 */
export const generateNutritionMealPlan = async (
  options: MealPlanGenerateRequest
): Promise<MealPlanResponse> => {
  const params = new URLSearchParams();

  // Map nutrition constraints to backend query params
  if (options.nutrition_constraints?.target_protein_g) {
    params.append('min_protein_g', String(options.nutrition_constraints.target_protein_g));
  }
  if (options.nutrition_constraints?.max_carbs_g) {
    params.append('max_carbs_g', String(options.nutrition_constraints.max_carbs_g));
  }
  if (options.nutrition_constraints?.target_calories) {
    params.append('min_calories', String(options.nutrition_constraints.target_calories * 0.8));
    params.append('max_calories', String(options.nutrition_constraints.target_calories * 1.2));
  }

  // Map meal preferences
  const includeBreakfast = options.meal_preferences?.include_breakfast ?? true;
  const includeLunch = options.meal_preferences?.include_lunch ?? true;
  const includeDinner = options.meal_preferences?.include_dinner ?? true;
  params.append('include_breakfast', String(includeBreakfast));
  params.append('include_lunch', String(includeLunch));
  params.append('include_dinner', String(includeDinner));

  // POST with no body - endpoint reads only from query params
  const response = await apiClient.post<MealPlanResponse>(
    `/meal-plans/generate-nutrition?${params.toString()}`
  );
  return response.data;
};

/**
 * Get a saved meal plan by ID.
 */
export const getMealPlanById = async (id: number): Promise<MealPlanResponse> => {
  const response = await apiClient.get<MealPlanResponse>(`/meal-plans/${id}`);
  return response.data;
};

/**
 * Get all saved meal plans for the current user.
 */
export const getMealPlans = async (): Promise<MealPlanResponse[]> => {
  const response = await apiClient.get<MealPlanResponse[]>('/meal-plans');
  return response.data;
};

/**
 * Save a generated meal plan.
 */
export const saveMealPlan = async (mealPlan: MealPlanResponse): Promise<MealPlanResponse> => {
  const response = await apiClient.post<MealPlanResponse>('/meal-plans', mealPlan);
  return response.data;
};

/**
 * Delete a saved meal plan.
 */
export const deleteMealPlan = async (id: number): Promise<void> => {
  await apiClient.delete(`/meal-plans/${id}`);
};

/**
 * Export meal plan to markdown.
 */
export const exportMealPlanMarkdown = async (id: number): Promise<string> => {
  const response = await apiClient.get<string>(`/meal-plans/${id}/export/markdown`);
  return response.data;
};

/**
 * Export meal plan to PDF.
 */
export const exportMealPlanPDF = async (id: number): Promise<Blob> => {
  const response = await apiClient.get<Blob>(`/meal-plans/${id}/export/pdf`, {
    responseType: 'blob',
  });
  return response.data;
};
