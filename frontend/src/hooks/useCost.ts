/**
 * React Query hooks for cost estimation data fetching.
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  getRecipeCost,
  getMealPlanCost,
  getBudgetRecipes,
  getCheaperAlternatives,
  getAverageCostsByCategory,
} from '../api/cost';
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
 * Query keys for cost data.
 */
export const costKeys = {
  all: ['costs'] as const,
  recipe: (recipeId: number, servings?: number) =>
    [...costKeys.all, 'recipe', recipeId, { servings }] as const,
  mealPlan: (data: MealPlanCostRequest) => [...costKeys.all, 'mealPlan', data] as const,
  budget: (params: BudgetRecipesRequest) => [...costKeys.all, 'budget', params] as const,
  alternatives: (recipeId: number, maxBudget: number) =>
    [...costKeys.all, 'alternatives', recipeId, maxBudget] as const,
  averages: () => [...costKeys.all, 'averages'] as const,
};

/**
 * Fetch cost estimate for a recipe.
 */
export const useRecipeCost = (
  recipeId: number,
  servings?: number
): UseQueryResult<RecipeCost> => {
  return useQuery({
    queryKey: costKeys.recipe(recipeId, servings),
    queryFn: () => getRecipeCost(recipeId, servings),
    enabled: !!recipeId && recipeId > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes - costs don't change frequently
    gcTime: 60 * 60 * 1000, // 1 hour
  });
};

/**
 * Fetch cost breakdown for a meal plan.
 */
export const useMealPlanCost = (
  data: MealPlanCostRequest,
  enabled: boolean = true
): UseQueryResult<MealPlanCostBreakdown> => {
  return useQuery({
    queryKey: costKeys.mealPlan(data),
    queryFn: () => getMealPlanCost(data),
    enabled: enabled && !!(data.meal_plan_id || data.recipe_ids?.length),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch recipes within a budget.
 */
export const useBudgetRecipes = (
  params: BudgetRecipesRequest
): UseQueryResult<BudgetRecipesResponse> => {
  return useQuery({
    queryKey: costKeys.budget(params),
    queryFn: () => getBudgetRecipes(params),
    enabled: !!params.max_cost && params.max_cost > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch cheaper recipe alternatives.
 */
export const useCheaperAlternatives = (
  recipeId: number,
  maxBudget: number,
  options?: Omit<CostAlternativesRequest, 'recipe_id' | 'max_budget'>,
  enabled: boolean = true
): UseQueryResult<CostAlternativesResponse> => {
  return useQuery({
    queryKey: costKeys.alternatives(recipeId, maxBudget),
    queryFn: () => getCheaperAlternatives(recipeId, maxBudget, options),
    enabled: enabled && !!recipeId && recipeId > 0 && !!maxBudget && maxBudget > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch average costs by category.
 */
export const useAverageCostsByCategory = (): UseQueryResult<
  Array<{ category: string; average_cost: number; recipe_count: number }>
> => {
  return useQuery({
    queryKey: costKeys.averages(),
    queryFn: getAverageCostsByCategory,
    staleTime: 60 * 60 * 1000, // 1 hour - category averages are stable
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
  });
};
