/**
 * React Query hooks for user preferences, allergens, and favorites.
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryResult,
  UseMutationResult,
  useInfiniteQuery,
  UseInfiniteQueryResult,
} from '@tanstack/react-query';
import {
  getPreferences,
  updatePreferences,
  getAllergens,
  updateAllergens,
  getFavorites,
  addFavorite,
  removeFavorite,
  isFavorite,
} from '../api/users';
import { useIsAuthenticated } from './useAuth';
import type {
  UserPreference,
  UserAllergen,
  PreferenceUpdateRequest,
  AllergenUpdateRequest,
  FavoriteAddRequest,
} from '../types/user';
import type { RecipeListItem, PaginatedResponse, APIError } from '../types';

/**
 * Query keys for user data.
 */
export const userKeys = {
  all: ['user'] as const,
  preferences: () => [...userKeys.all, 'preferences'] as const,
  allergens: () => [...userKeys.all, 'allergens'] as const,
  favorites: () => [...userKeys.all, 'favorites'] as const,
  favorite: (recipeId: number) => [...userKeys.favorites(), recipeId] as const,
};

// ============================================================================
// PREFERENCES
// ============================================================================

/**
 * Hook to get user preferences.
 */
export const usePreferences = (): UseQueryResult<UserPreference> => {
  const isAuthenticated = useIsAuthenticated();

  return useQuery({
    queryKey: userKeys.preferences(),
    queryFn: getPreferences,
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000,
  });
};

/**
 * Hook to update user preferences.
 */
export const useUpdatePreferences = (): UseMutationResult<
  UserPreference,
  APIError,
  PreferenceUpdateRequest
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updatePreferences,
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.preferences(), data);
    },
  });
};

// ============================================================================
// ALLERGENS
// ============================================================================

/**
 * Hook to get user allergens.
 */
export const useAllergens = (): UseQueryResult<UserAllergen[]> => {
  const isAuthenticated = useIsAuthenticated();

  return useQuery({
    queryKey: userKeys.allergens(),
    queryFn: getAllergens,
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
};

/**
 * Hook to update user allergens.
 */
export const useUpdateAllergens = (): UseMutationResult<
  UserAllergen[],
  APIError,
  AllergenUpdateRequest
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateAllergens,
    onSuccess: (data) => {
      queryClient.setQueryData(userKeys.allergens(), data);
    },
  });
};

// ============================================================================
// FAVORITES
// ============================================================================

/**
 * Hook to get user favorites with pagination.
 */
export const useFavorites = (
  page: number = 1,
  pageSize: number = 20
): UseQueryResult<PaginatedResponse<RecipeListItem>> => {
  const isAuthenticated = useIsAuthenticated();

  return useQuery({
    queryKey: [...userKeys.favorites(), { page, pageSize }],
    queryFn: () => getFavorites({ page, page_size: pageSize }),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Hook to get user favorites with infinite scroll.
 */
export const useInfiniteFavorites = (
  pageSize: number = 20
): UseInfiniteQueryResult<PaginatedResponse<RecipeListItem>> => {
  const isAuthenticated = useIsAuthenticated();

  return useInfiniteQuery({
    queryKey: userKeys.favorites(),
    queryFn: ({ pageParam = 1 }) =>
      getFavorites({ page: pageParam as number, page_size: pageSize }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      return lastPage.has_next ? lastPage.page + 1 : undefined;
    },
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Hook to add recipe to favorites.
 */
export const useAddFavorite = (): UseMutationResult<
  void,
  APIError,
  FavoriteAddRequest
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addFavorite,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.favorites() });
      queryClient.invalidateQueries({
        queryKey: userKeys.favorite(variables.recipe_id),
      });
    },
  });
};

/**
 * Hook to remove recipe from favorites.
 */
export const useRemoveFavorite = (): UseMutationResult<void, APIError, number> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeFavorite,
    onSuccess: (_, recipeId) => {
      queryClient.invalidateQueries({ queryKey: userKeys.favorites() });
      queryClient.invalidateQueries({ queryKey: userKeys.favorite(recipeId) });
    },
  });
};

/**
 * Hook to check if recipe is favorited.
 */
export const useIsFavorite = (recipeId: number): UseQueryResult<boolean> => {
  const isAuthenticated = useIsAuthenticated();

  return useQuery({
    queryKey: userKeys.favorite(recipeId),
    queryFn: () => isFavorite(recipeId),
    enabled: isAuthenticated && !!recipeId && recipeId > 0,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Hook to toggle favorite status.
 */
export const useToggleFavorite = (
  recipeId: number
): {
  isFavorite: boolean;
  isLoading: boolean;
  toggle: () => void;
} => {
  const { data: isFavorited = false, isLoading } = useIsFavorite(recipeId);
  const addMutation = useAddFavorite();
  const removeMutation = useRemoveFavorite();

  const toggle = (): void => {
    if (isFavorited) {
      removeMutation.mutate(recipeId);
    } else {
      addMutation.mutate({ recipe_id: recipeId });
    }
  };

  return {
    isFavorite: isFavorited,
    isLoading: isLoading || addMutation.isPending || removeMutation.isPending,
    toggle,
  };
};
