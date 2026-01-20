/**
 * Multi-week meal planning API endpoints.
 */

import { apiClient } from './client';
import type {
  MultiWeekPlan,
  MultiWeekGenerateRequest,
  MultiWeekUpdateRequest,
  VarietyBreakdown,
  PaginationParams,
  PaginatedResponse,
} from '../types';

/**
 * Generate a multi-week meal plan.
 */
export const generateMultiWeekPlan = async (
  data: MultiWeekGenerateRequest
): Promise<MultiWeekPlan> => {
  const response = await apiClient.post<MultiWeekPlan>('/meal-plans/multi-week/generate', data);
  return response.data;
};

/**
 * Get a multi-week meal plan by ID.
 */
export const getMultiWeekPlan = async (id: number): Promise<MultiWeekPlan> => {
  const response = await apiClient.get<MultiWeekPlan>(`/meal-plans/multi-week/${id}`);
  return response.data;
};

/**
 * Get all user's multi-week plans.
 */
export const getMultiWeekPlans = async (
  pagination: PaginationParams = { page: 1, page_size: 10 }
): Promise<PaginatedResponse<MultiWeekPlan>> => {
  const params = {
    page: pagination.page,
    page_size: pagination.page_size,
  };

  const response = await apiClient.get<PaginatedResponse<MultiWeekPlan>>(
    '/meal-plans/multi-week',
    { params }
  );

  return response.data;
};

/**
 * Update a multi-week plan.
 */
export const updateMultiWeekPlan = async (
  id: number,
  data: MultiWeekUpdateRequest
): Promise<MultiWeekPlan> => {
  const response = await apiClient.patch<MultiWeekPlan>(`/meal-plans/multi-week/${id}`, data);
  return response.data;
};

/**
 * Delete a multi-week plan.
 */
export const deleteMultiWeekPlan = async (id: number): Promise<void> => {
  await apiClient.delete(`/meal-plans/multi-week/${id}`);
};

/**
 * Get variety analysis for a multi-week plan.
 */
export const getVarietyAnalysis = async (
  recipeIds: number[]
): Promise<VarietyBreakdown> => {
  const response = await apiClient.post<VarietyBreakdown>('/meal-plans/variety-analysis', {
    recipe_ids: recipeIds,
  });

  return response.data;
};

/**
 * Get variety score for a set of recipes.
 */
export const getVarietyScore = async (recipeIds: number[]): Promise<number> => {
  const response = await apiClient.post<{ variety_score: number }>(
    '/meal-plans/variety-score',
    {
      recipe_ids: recipeIds,
    }
  );

  return response.data.variety_score;
};
