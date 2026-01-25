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
 */
export const generateMealPlan = async (
  options: ExtendedMealPlanRequest
): Promise<MealPlanResponse> => {
  // Determine which endpoint to use
  const useNutritionEndpoint = options.useNutritionEndpoint ?? true;
  const endpoint = useNutritionEndpoint ? '/meal-plans/generate-nutrition' : '/meal-plans/generate';

  // Build query params based on endpoint
  const params = new URLSearchParams();

  // Extract meal preferences
  const includeBreakfast = options.include_breakfast ?? options.meal_preferences?.include_breakfast ?? true;
  const includeLunch = options.include_lunch ?? options.meal_preferences?.include_lunch ?? true;
  const includeDinner = options.include_dinner ?? options.meal_preferences?.include_dinner ?? true;

  params.append('include_breakfast', String(includeBreakfast));
  params.append('include_lunch', String(includeLunch));
  params.append('include_dinner', String(includeDinner));

  if (useNutritionEndpoint) {
    // Nutrition endpoint uses min_protein_g and max_carbs_g
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
    // Basic endpoint uses min_protein_score and max_carb_score
    if (options.nutrition_goals?.daily_protein_g) {
      params.append('min_protein_score', String(options.nutrition_goals.daily_protein_g));
    }
    if (options.nutrition_goals?.daily_carbs_g) {
      params.append('max_carb_score', String(options.nutrition_goals.daily_carbs_g));
    }
  }

  const response = await apiClient.post<MealPlanResponse>(`${endpoint}?${params.toString()}`);
  return response.data;
};

/**
 * Generate a nutrition-optimized meal plan.
 */
export const generateNutritionMealPlan = async (
  options: MealPlanGenerateRequest
): Promise<MealPlanResponse> => {
  const response = await apiClient.post<MealPlanResponse>(
    '/meal-plans/generate/nutrition',
    options
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
