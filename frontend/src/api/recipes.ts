/**
 * Recipe API endpoints.
 */

import { apiClient } from './client';
import type {
  Recipe,
  RecipeListItem,
  RecipeFilters,
  PaginatedResponse,
  PaginationParams,
  SortParams,
} from '../types';

/**
 * Remove empty string values from an object to avoid API validation errors.
 */
const cleanParams = <T extends Record<string, unknown>>(obj: T): Partial<T> => {
  return Object.fromEntries(
    Object.entries(obj).filter(([, value]) => value !== '' && value !== undefined && value !== null)
  ) as Partial<T>;
};

/**
 * Fetch paginated list of recipes with optional filters.
 */
export const getRecipes = async (
  filters?: RecipeFilters,
  pagination: PaginationParams = { page: 1, page_size: 20 },
  sort?: SortParams
): Promise<PaginatedResponse<RecipeListItem>> => {
  const params = cleanParams({
    page: pagination.page,
    page_size: pagination.page_size,
    ...sort,
    ...filters,
  });

  const response = await apiClient.get<PaginatedResponse<RecipeListItem>>('/recipes', {
    params,
  });

  return response.data;
};

/**
 * Fetch a single recipe by ID.
 */
export const getRecipeById = async (id: number): Promise<Recipe> => {
  const response = await apiClient.get<Recipe>(`/recipes/${id}`);
  return response.data;
};

/**
 * Fetch a single recipe by slug.
 */
export const getRecipeBySlug = async (slug: string): Promise<Recipe> => {
  const response = await apiClient.get<Recipe>(`/recipes/slug/${slug}`);
  return response.data;
};

/**
 * Search recipes by query string.
 */
export const searchRecipes = async (
  query: string,
  pagination?: PaginationParams
): Promise<PaginatedResponse<RecipeListItem>> => {
  const params = {
    q: query,
    page: pagination?.page ?? 1,
    page_size: pagination?.page_size ?? 20,
  };

  const response = await apiClient.get<PaginatedResponse<RecipeListItem>>('/recipes/search', {
    params,
  });

  return response.data;
};

/**
 * Get random recipes.
 */
export const getRandomRecipes = async (count = 10): Promise<RecipeListItem[]> => {
  const response = await apiClient.get<RecipeListItem[]>('/recipes/random', {
    params: { count },
  });

  return response.data;
};

/**
 * Get featured/popular recipes.
 */
export const getFeaturedRecipes = async (): Promise<RecipeListItem[]> => {
  const response = await apiClient.get<RecipeListItem[]>('/recipes/featured');
  return response.data;
};
