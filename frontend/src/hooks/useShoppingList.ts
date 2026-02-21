/**
 * React Query hooks for shopping list generation and management.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  generateShoppingList,
  generateShoppingListFromMealPlan,
  getShoppingListById,
  getShoppingLists,
  saveShoppingList,
  deleteShoppingList,
  exportShoppingListMarkdown,
  exportShoppingListPDF,
} from '../api/shoppingLists';
import type {
  ShoppingListGenerateRequest,
  ShoppingListResponse,
  ShoppingListExportRequest,
} from '../types';

/**
 * Query keys for shopping lists.
 */
export const shoppingListKeys = {
  all: ['shoppingLists'] as const,
  lists: () => [...shoppingListKeys.all, 'list'] as const,
  list: () => [...shoppingListKeys.lists()] as const,
  details: () => [...shoppingListKeys.all, 'detail'] as const,
  detail: (id: number) => [...shoppingListKeys.details(), id] as const,
};

/**
 * Generate shopping list from recipe IDs.
 */
export const useGenerateShoppingList = (): UseMutationResult<
  ShoppingListResponse,
  Error,
  { recipeIds: number[]; options?: Partial<ShoppingListGenerateRequest> }
> => {
  return useMutation({
    mutationFn: ({ recipeIds, options }) => generateShoppingList(recipeIds, options),
  });
};

/**
 * Generate shopping list from a meal plan.
 */
export const useGenerateShoppingListFromMealPlan = (): UseMutationResult<
  ShoppingListResponse,
  Error,
  { mealPlan: Record<string, unknown>; options?: Partial<ShoppingListGenerateRequest> }
> => {
  return useMutation({
    mutationFn: ({ mealPlan, options }) =>
      generateShoppingListFromMealPlan(mealPlan, options),
  });
};

/**
 * Fetch a saved shopping list by ID.
 */
export const useShoppingList = (id: number): UseQueryResult<ShoppingListResponse> => {
  return useQuery({
    queryKey: shoppingListKeys.detail(id),
    queryFn: () => getShoppingListById(id),
    enabled: !!id && id > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch all saved shopping lists.
 */
export const useShoppingLists = (): UseQueryResult<ShoppingListResponse[]> => {
  return useQuery({
    queryKey: shoppingListKeys.list(),
    queryFn: getShoppingLists,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Save a generated shopping list.
 */
export const useSaveShoppingList = (): UseMutationResult<
  ShoppingListResponse,
  Error,
  ShoppingListResponse
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: saveShoppingList,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shoppingListKeys.lists() });
    },
  });
};

/**
 * Delete a saved shopping list.
 */
export const useDeleteShoppingList = (): UseMutationResult<void, Error, number> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteShoppingList,
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: shoppingListKeys.lists() });
      queryClient.removeQueries({ queryKey: shoppingListKeys.detail(deletedId) });
    },
  });
};

/**
 * Export shopping list to markdown.
 */
export const useExportShoppingListMarkdown = (): UseMutationResult<
  string,
  Error,
  { shoppingListId: number; options?: Partial<ShoppingListExportRequest> }
> => {
  return useMutation({
    mutationFn: ({ shoppingListId, options }) =>
      exportShoppingListMarkdown(shoppingListId, options),
  });
};

/**
 * Export shopping list to PDF.
 */
export const useExportShoppingListPDF = (): UseMutationResult<
  string,
  Error,
  { shoppingListId: number; options?: Partial<ShoppingListExportRequest> }
> => {
  return useMutation({
    mutationFn: ({ shoppingListId, options }) => exportShoppingListPDF(shoppingListId, options),
  });
};
