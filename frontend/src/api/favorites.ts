/**
 * Favorites API endpoints.
 */

import { apiClient } from './client';
import type {
  FavoriteRecipe,
  FavoritesResponse,
  AddFavoriteRequest,
  UpdateFavoriteRequest,
  FavoritesSortBy,
  PaginationParams,
} from '../types';

/**
 * Get user's favorite recipes with pagination.
 */
export const getFavorites = async (
  pagination: PaginationParams = { page: 1, page_size: 20 },
  sortBy: FavoritesSortBy = FavoritesSortBy.DATE_ADDED_DESC
): Promise<FavoritesResponse> => {
  const params = {
    page: pagination.page,
    page_size: pagination.page_size,
    sort_by: sortBy,
  };

  const response = await apiClient.get<FavoritesResponse>('/favorites', {
    params,
  });

  return response.data;
};

/**
 * Add a recipe to favorites.
 */
export const addFavorite = async (data: AddFavoriteRequest): Promise<FavoriteRecipe> => {
  const response = await apiClient.post<FavoriteRecipe>('/favorites', data);
  return response.data;
};

/**
 * Remove a recipe from favorites.
 */
export const removeFavorite = async (recipeId: number): Promise<void> => {
  await apiClient.delete(`/favorites/${recipeId}`);
};

/**
 * Update favorite notes.
 */
export const updateFavorite = async (
  recipeId: number,
  data: UpdateFavoriteRequest
): Promise<FavoriteRecipe> => {
  const response = await apiClient.patch<FavoriteRecipe>(`/favorites/${recipeId}`, data);
  return response.data;
};

/**
 * Check if a recipe is favorited.
 */
export const checkIsFavorite = async (recipeId: number): Promise<boolean> => {
  try {
    const response = await apiClient.get<{ is_favorite: boolean }>(
      `/favorites/check/${recipeId}`
    );
    return response.data.is_favorite;
  } catch {
    return false;
  }
};

/**
 * Get all favorite recipe IDs (for quick lookup).
 */
export const getFavoriteIds = async (): Promise<number[]> => {
  const response = await apiClient.get<{ recipe_ids: number[] }>('/favorites/ids');
  return response.data.recipe_ids;
};
