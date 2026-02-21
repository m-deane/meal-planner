/**
 * React Query hooks for user preferences and allergens.
 *
 * Note: Favorites hooks are in hooks/useFavorites.ts (canonical source).
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from '@tanstack/react-query';
import {
  getPreferences,
  updatePreferences,
  getAllergens,
  updateAllergens,
} from '../api/users';
import { useIsAuthenticated } from './useAuth';
import type {
  UserPreference,
  UserAllergen,
  PreferenceUpdateRequest,
  AllergenUpdateRequest,
} from '../types/user';
import type { APIError } from '../types';

/**
 * Query keys for user data.
 */
export const userKeys = {
  all: ['user'] as const,
  preferences: () => [...userKeys.all, 'preferences'] as const,
  allergens: () => [...userKeys.all, 'allergens'] as const,
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

