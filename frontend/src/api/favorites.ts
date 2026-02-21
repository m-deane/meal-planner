/**
 * Favorites API endpoints.
 */

import { apiClient } from './client';
import type {
  FavoriteRecipe,
  FavoritesResponse,
  AddFavoriteRequest,
  UpdateFavoriteRequest,
  PaginationParams,
} from '../types';
import { FavoritesSortBy } from '../types';

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
  const response = await apiClient.post<FavoriteRecipe>(`/favorites/${data.recipe_id}`, {
    notes: data.notes,
  });
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
  const response = await apiClient.put<FavoriteRecipe>(`/favorites/${recipeId}/notes`, data);
  return response.data;
};

/**
 * Check if a recipe is favorited.
 */
export const checkIsFavorite = async (recipeId: number): Promise<boolean> => {
  try {
    const response = await apiClient.get<{ is_favorite: boolean }>(
      `/favorites/${recipeId}/status`
    );
    return response.data.is_favorite;
  } catch {
    return false;
  }
};
