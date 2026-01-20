/**
 * React Query hooks for favorites data fetching and mutations.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
} from '@tanstack/react-query';
import {
  getFavorites,
  addFavorite,
  removeFavorite,
  updateFavorite,
  checkIsFavorite,
  getFavoriteIds,
} from '../api/favorites';
import type {
  FavoriteRecipe,
  FavoritesResponse,
  AddFavoriteRequest,
  UpdateFavoriteRequest,
  FavoritesSortBy,
  PaginationParams,
  APIError,
} from '../types';

/**
 * Query keys for favorites.
 */
export const favoriteKeys = {
  all: ['favorites'] as const,
  lists: () => [...favoriteKeys.all, 'list'] as const,
  list: (page?: number, sortBy?: FavoritesSortBy) =>
    [...favoriteKeys.lists(), { page, sortBy }] as const,
  ids: () => [...favoriteKeys.all, 'ids'] as const,
  check: (recipeId: number) => [...favoriteKeys.all, 'check', recipeId] as const,
};

/**
 * Fetch user's favorite recipes with pagination.
 */
export const useFavorites = (
  pagination: PaginationParams = { page: 1, page_size: 20 },
  sortBy: FavoritesSortBy = FavoritesSortBy.DATE_ADDED_DESC
): UseQueryResult<FavoritesResponse> => {
  return useQuery({
    queryKey: favoriteKeys.list(pagination.page, sortBy),
    queryFn: () => getFavorites(pagination, sortBy),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Get all favorite recipe IDs for quick lookup.
 */
export const useFavoriteIds = (): UseQueryResult<number[]> => {
  return useQuery({
    queryKey: favoriteKeys.ids(),
    queryFn: getFavoriteIds,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Check if a specific recipe is favorited.
 */
export const useIsFavorite = (recipeId: number): UseQueryResult<boolean> => {
  return useQuery({
    queryKey: favoriteKeys.check(recipeId),
    queryFn: () => checkIsFavorite(recipeId),
    enabled: !!recipeId && recipeId > 0,
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Add a recipe to favorites.
 */
export const useAddFavorite = (): UseMutationResult<
  FavoriteRecipe,
  APIError,
  AddFavoriteRequest
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addFavorite,
    onSuccess: (data) => {
      // Invalidate favorites lists
      queryClient.invalidateQueries({ queryKey: favoriteKeys.lists() });
      queryClient.invalidateQueries({ queryKey: favoriteKeys.ids() });

      // Update the check query for this specific recipe
      queryClient.setQueryData(favoriteKeys.check(data.recipe_id), true);
    },
  });
};

/**
 * Remove a recipe from favorites.
 */
export const useRemoveFavorite = (): UseMutationResult<void, APIError, number> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeFavorite,
    onSuccess: (_, recipeId) => {
      // Invalidate favorites lists
      queryClient.invalidateQueries({ queryKey: favoriteKeys.lists() });
      queryClient.invalidateQueries({ queryKey: favoriteKeys.ids() });

      // Update the check query for this specific recipe
      queryClient.setQueryData(favoriteKeys.check(recipeId), false);
    },
  });
};

/**
 * Update favorite notes.
 */
export const useUpdateFavorite = (): UseMutationResult<
  FavoriteRecipe,
  APIError,
  { recipeId: number; data: UpdateFavoriteRequest }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recipeId, data }) => updateFavorite(recipeId, data),
    onSuccess: () => {
      // Invalidate favorites lists to refresh the data
      queryClient.invalidateQueries({ queryKey: favoriteKeys.lists() });
    },
  });
};

/**
 * Toggle favorite status (add if not favorited, remove if favorited).
 */
export const useToggleFavorite = (): {
  toggleFavorite: (recipeId: number, notes?: string) => Promise<void>;
  isLoading: boolean;
} => {
  const queryClient = useQueryClient();
  const addMutation = useAddFavorite();
  const removeMutation = useRemoveFavorite();

  const toggleFavorite = async (recipeId: number, notes?: string): Promise<void> => {
    // Check current favorite status
    const isFavorite = queryClient.getQueryData<boolean>(favoriteKeys.check(recipeId));

    if (isFavorite) {
      await removeMutation.mutateAsync(recipeId);
    } else {
      await addMutation.mutateAsync({ recipe_id: recipeId, notes });
    }
  };

  return {
    toggleFavorite,
    isLoading: addMutation.isPending || removeMutation.isPending,
  };
};
