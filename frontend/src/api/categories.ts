/**
 * Categories, dietary tags, and allergens API endpoints.
 */

import { apiClient } from './client';
import type { Category, DietaryTag, Allergen } from '../types';

/**
 * Fetch all recipe categories.
 */
export const getCategories = async (): Promise<Category[]> => {
  const response = await apiClient.get<Category[]>('/categories');
  return response.data;
};

/**
 * Fetch all dietary tags.
 */
export const getDietaryTags = async (): Promise<DietaryTag[]> => {
  const response = await apiClient.get<DietaryTag[]>('/dietary-tags');
  return response.data;
};

/**
 * Fetch all allergens.
 */
export const getAllergens = async (): Promise<Allergen[]> => {
  const response = await apiClient.get<Allergen[]>('/allergens');
  return response.data;
};

/**
 * Fetch category by slug.
 */
export const getCategoryBySlug = async (slug: string): Promise<Category> => {
  const response = await apiClient.get<Category>(`/categories/${slug}`);
  return response.data;
};

/**
 * Fetch dietary tag by slug.
 */
export const getDietaryTagBySlug = async (slug: string): Promise<DietaryTag> => {
  const response = await apiClient.get<DietaryTag>(`/dietary-tags/${slug}`);
  return response.data;
};
