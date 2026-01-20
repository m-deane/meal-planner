/**
 * React Query hooks for multi-week meal planning.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  generateMultiWeekPlan,
  getMultiWeekPlan,
  getMultiWeekPlans,
  updateMultiWeekPlan,
  deleteMultiWeekPlan,
  getVarietyAnalysis,
  getVarietyScore,
} from '../api/multiWeek';
import type {
  MultiWeekPlan,
  MultiWeekGenerateRequest,
  MultiWeekUpdateRequest,
  VarietyBreakdown,
  PaginationParams,
  PaginatedResponse,
  APIError,
} from '../types';

/**
 * Query keys for multi-week plans.
 */
export const multiWeekKeys = {
  all: ['multiWeekPlans'] as const,
  lists: () => [...multiWeekKeys.all, 'list'] as const,
  list: (page?: number) => [...multiWeekKeys.lists(), { page }] as const,
  details: () => [...multiWeekKeys.all, 'detail'] as const,
  detail: (id: number) => [...multiWeekKeys.details(), id] as const,
  variety: (recipeIds: number[]) => [...multiWeekKeys.all, 'variety', recipeIds] as const,
  varietyScore: (recipeIds: number[]) =>
    [...multiWeekKeys.all, 'varietyScore', recipeIds] as const,
};

/**
 * Fetch all user's multi-week plans.
 */
export const useMultiWeekPlans = (
  pagination: PaginationParams = { page: 1, page_size: 10 }
): UseQueryResult<PaginatedResponse<MultiWeekPlan>> => {
  return useQuery({
    queryKey: multiWeekKeys.list(pagination.page),
    queryFn: () => getMultiWeekPlans(pagination),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Fetch a specific multi-week plan.
 */
export const useMultiWeekPlan = (id: number): UseQueryResult<MultiWeekPlan> => {
  return useQuery({
    queryKey: multiWeekKeys.detail(id),
    queryFn: () => getMultiWeekPlan(id),
    enabled: !!id && id > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Generate a multi-week meal plan.
 */
export const useGenerateMultiWeekPlan = (): UseMutationResult<
  MultiWeekPlan,
  APIError,
  MultiWeekGenerateRequest
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: generateMultiWeekPlan,
    onSuccess: () => {
      // Invalidate the list to refresh
      queryClient.invalidateQueries({ queryKey: multiWeekKeys.lists() });
    },
  });
};

/**
 * Update a multi-week plan.
 */
export const useUpdateMultiWeekPlan = (): UseMutationResult<
  MultiWeekPlan,
  APIError,
  { id: number; data: MultiWeekUpdateRequest }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => updateMultiWeekPlan(id, data),
    onSuccess: (data) => {
      // Update the cached detail
      queryClient.setQueryData(multiWeekKeys.detail(data.id), data);
      // Invalidate the list
      queryClient.invalidateQueries({ queryKey: multiWeekKeys.lists() });
    },
  });
};

/**
 * Delete a multi-week plan.
 */
export const useDeleteMultiWeekPlan = (): UseMutationResult<void, APIError, number> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteMultiWeekPlan,
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: multiWeekKeys.detail(id) });
      // Invalidate the list
      queryClient.invalidateQueries({ queryKey: multiWeekKeys.lists() });
    },
  });
};

/**
 * Get variety analysis for a set of recipes.
 */
export const useVarietyAnalysis = (
  recipeIds: number[],
  enabled: boolean = true
): UseQueryResult<VarietyBreakdown> => {
  return useQuery({
    queryKey: multiWeekKeys.variety(recipeIds),
    queryFn: () => getVarietyAnalysis(recipeIds),
    enabled: enabled && recipeIds.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
};

/**
 * Get variety score for a set of recipes.
 */
export const useVarietyScore = (
  recipeIds: number[],
  enabled: boolean = true
): UseQueryResult<number> => {
  return useQuery({
    queryKey: multiWeekKeys.varietyScore(recipeIds),
    queryFn: () => getVarietyScore(recipeIds),
    enabled: enabled && recipeIds.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
};
