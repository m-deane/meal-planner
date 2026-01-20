/**
 * Meal plan API endpoints.
 */

import { apiClient } from './client';
import type { MealPlanGenerateRequest, MealPlanResponse } from '../types';

/**
 * Generate a meal plan based on preferences and constraints.
 */
export const generateMealPlan = async (
  options: MealPlanGenerateRequest
): Promise<MealPlanResponse> => {
  const response = await apiClient.post<MealPlanResponse>('/meal-plans/generate', options);
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
  const response = await apiClient.get(`/meal-plans/${id}/export/pdf`, {
    responseType: 'blob',
  });
  return response.data;
};
