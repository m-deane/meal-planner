/**
 * Cost estimation API endpoints.
 */

import { apiClient } from './client';
import type {
  RecipeCost,
  MealPlanCostBreakdown,
  BudgetRecipesResponse,
  CostAlternativesResponse,
  MealPlanCostRequest,
  BudgetRecipesRequest,
  CostAlternativesRequest,
} from '../types';

/**
 * Get cost estimate for a recipe.
 */
export const getRecipeCost = async (
  recipeId: number,
  servings?: number
): Promise<RecipeCost> => {
  const params = servings ? { servings } : {};

  const response = await apiClient.get<RecipeCost>(`/cost/recipes/${recipeId}`, {
    params,
  });

  return response.data;
};

/**
 * Get cost breakdown for a meal plan.
 */
export const getMealPlanCost = async (
  data: MealPlanCostRequest
): Promise<MealPlanCostBreakdown> => {
  const response = await apiClient.post<MealPlanCostBreakdown>('/cost/meal-plans/estimate', data);
  return response.data;
};

/**
 * Get recipes within a budget.
 */
export const getBudgetRecipes = async (
  params: BudgetRecipesRequest
): Promise<BudgetRecipesResponse> => {
  const response = await apiClient.get<BudgetRecipesResponse>('/cost/recipes/budget', {
    params,
  });

  return response.data;
};

/**
 * Get cheaper recipe alternatives.
 */
export const getCheaperAlternatives = async (
  recipeId: number,
  maxBudget: number,
  options?: Omit<CostAlternativesRequest, 'recipe_id' | 'max_budget'>
): Promise<CostAlternativesResponse> => {
  const params: CostAlternativesRequest = {
    recipe_id: recipeId,
    max_budget: maxBudget,
    ...options,
  };

  const response = await apiClient.get<CostAlternativesResponse>(
    `/cost/recipes/${recipeId}/alternatives`,
    { params }
  );

  return response.data;
};
