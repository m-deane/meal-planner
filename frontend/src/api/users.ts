/**
 * User preferences, allergens, and favorites API functions.
 */

import { apiClient } from './client';
import type {
  UserPreference,
  UserAllergen,
  PreferenceUpdateRequest,
  AllergenUpdateRequest,
  FavoriteAddRequest,
} from '../types/user';
import type { RecipeListItem, PaginatedResponse, PaginationParams } from '../types';

/**
 * Get user preferences.
 */
export const getPreferences = async (): Promise<UserPreference> => {
  const { data } = await apiClient.get<UserPreference>('/users/preferences');
  return data;
};

/**
 * Update user preferences.
 */
export const updatePreferences = async (
  preferences: PreferenceUpdateRequest
): Promise<UserPreference> => {
  const { data } = await apiClient.patch<UserPreference>(
    '/users/preferences',
    preferences
  );
  return data;
};

/**
 * Get user allergens.
 */
export const getAllergens = async (): Promise<UserAllergen[]> => {
  const { data } = await apiClient.get<UserAllergen[]>('/users/allergens');
  return data;
};

/**
 * Update user allergens (replaces all).
 */
export const updateAllergens = async (
  allergenData: AllergenUpdateRequest
): Promise<UserAllergen[]> => {
  const { data } = await apiClient.put<UserAllergen[]>(
    '/users/allergens',
    allergenData
  );
  return data;
};

/**
 * Get user favorite recipes with pagination.
 */
export const getFavorites = async (
  pagination?: PaginationParams
): Promise<PaginatedResponse<RecipeListItem>> => {
  const params = new URLSearchParams();

  if (pagination) {
    params.append('page', String(pagination.page));
    params.append('page_size', String(pagination.page_size));
  }

  const { data } = await apiClient.get<PaginatedResponse<RecipeListItem>>(
    '/users/favorites',
    { params }
  );
  return data;
};

/**
 * Add recipe to favorites.
 */
export const addFavorite = async (favoriteData: FavoriteAddRequest): Promise<void> => {
  await apiClient.post('/users/favorites', favoriteData);
};

/**
 * Remove recipe from favorites.
 */
export const removeFavorite = async (recipeId: number): Promise<void> => {
  await apiClient.delete(`/users/favorites/${recipeId}`);
};

/**
 * Check if recipe is favorited.
 */
export const isFavorite = async (recipeId: number): Promise<boolean> => {
  try {
    const { data } = await apiClient.get<{ is_favorite: boolean }>(
      `/users/favorites/${recipeId}/check`
    );
    return data.is_favorite;
  } catch {
    return false;
  }
};
