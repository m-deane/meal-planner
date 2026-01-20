/**
 * React Query hooks for meal plan generation and management.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  generateMealPlan,
  generateNutritionMealPlan,
  getMealPlanById,
  getMealPlans,
  saveMealPlan,
  deleteMealPlan,
  exportMealPlanMarkdown,
  exportMealPlanPDF,
} from '../api/mealPlans';
import type { MealPlanGenerateRequest, MealPlanResponse } from '../types';

/**
 * Query keys for meal plans.
 */
export const mealPlanKeys = {
  all: ['mealPlans'] as const,
  lists: () => [...mealPlanKeys.all, 'list'] as const,
  list: () => [...mealPlanKeys.lists()] as const,
  details: () => [...mealPlanKeys.all, 'detail'] as const,
  detail: (id: number) => [...mealPlanKeys.details(), id] as const,
};

/**
 * Generate a standard meal plan.
 */
export const useGenerateMealPlan = (): UseMutationResult<
  MealPlanResponse,
  Error,
  MealPlanGenerateRequest
> => {
  return useMutation({
    mutationFn: generateMealPlan,
  });
};

/**
 * Generate a nutrition-optimized meal plan.
 */
export const useGenerateNutritionMealPlan = (): UseMutationResult<
  MealPlanResponse,
  Error,
  MealPlanGenerateRequest
> => {
  return useMutation({
    mutationFn: generateNutritionMealPlan,
  });
};

/**
 * Fetch a saved meal plan by ID.
 */
export const useMealPlan = (id: number): UseQueryResult<MealPlanResponse> => {
  return useQuery({
    queryKey: mealPlanKeys.detail(id),
    queryFn: () => getMealPlanById(id),
    enabled: !!id && id > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch all saved meal plans.
 */
export const useMealPlans = (): UseQueryResult<MealPlanResponse[]> => {
  return useQuery({
    queryKey: mealPlanKeys.list(),
    queryFn: getMealPlans,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Save a generated meal plan.
 */
export const useSaveMealPlan = (): UseMutationResult<
  MealPlanResponse,
  Error,
  MealPlanResponse
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: saveMealPlan,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() });
      if (data.id) {
        queryClient.setQueryData(mealPlanKeys.detail(data.id), data);
      }
    },
  });
};

/**
 * Delete a saved meal plan.
 */
export const useDeleteMealPlan = (): UseMutationResult<void, Error, number> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteMealPlan,
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() });
      queryClient.removeQueries({ queryKey: mealPlanKeys.detail(deletedId) });
    },
  });
};

/**
 * Export meal plan to markdown.
 */
export const useExportMealPlanMarkdown = (): UseMutationResult<string, Error, number> => {
  return useMutation({
    mutationFn: exportMealPlanMarkdown,
  });
};

/**
 * Export meal plan to PDF.
 */
export const useExportMealPlanPDF = (): UseMutationResult<Blob, Error, number> => {
  return useMutation({
    mutationFn: exportMealPlanPDF,
  });
};
