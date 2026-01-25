/**
 * Shopping list API endpoints.
 */

import { apiClient } from './client';
import type {
  ShoppingListGenerateRequest,
  ShoppingListResponse,
  ShoppingListExportRequest,
  ShoppingListExportResponse,
} from '../types';
import { ShoppingListFormat } from '../types';

/**
 * Generate shopping list from recipe IDs.
 */
export const generateShoppingList = async (
  recipeIds: number[],
  options?: Partial<ShoppingListGenerateRequest>
): Promise<ShoppingListResponse> => {
  const request: ShoppingListGenerateRequest = {
    recipe_ids: recipeIds,
    servings_multiplier: options?.servings_multiplier ?? 1.0,
    group_by_category: options?.group_by_category ?? true,
    combine_similar_ingredients: options?.combine_similar_ingredients ?? true,
    exclude_pantry_staples: options?.exclude_pantry_staples ?? false,
    include_optional_ingredients: options?.include_optional_ingredients ?? true,
    round_quantities: options?.round_quantities ?? true,
    ...options,
  };

  const response = await apiClient.post<ShoppingListResponse>('/shopping-lists/generate', request);
  return response.data;
};

/**
 * Generate shopping list from a meal plan.
 */
export const generateShoppingListFromMealPlan = async (
  mealPlanId: number,
  options?: Partial<ShoppingListGenerateRequest>
): Promise<ShoppingListResponse> => {
  const request: ShoppingListGenerateRequest = {
    meal_plan_id: mealPlanId,
    servings_multiplier: options?.servings_multiplier ?? 1.0,
    group_by_category: options?.group_by_category ?? true,
    combine_similar_ingredients: options?.combine_similar_ingredients ?? true,
    exclude_pantry_staples: options?.exclude_pantry_staples ?? false,
    include_optional_ingredients: options?.include_optional_ingredients ?? true,
    round_quantities: options?.round_quantities ?? true,
    ...options,
  };

  const response = await apiClient.post<ShoppingListResponse>('/shopping-lists/generate', request);
  return response.data;
};

/**
 * Get a saved shopping list by ID.
 */
export const getShoppingListById = async (id: number): Promise<ShoppingListResponse> => {
  const response = await apiClient.get<ShoppingListResponse>(`/shopping-lists/${id}`);
  return response.data;
};

/**
 * Get all saved shopping lists for the current user.
 */
export const getShoppingLists = async (): Promise<ShoppingListResponse[]> => {
  const response = await apiClient.get<ShoppingListResponse[]>('/shopping-lists');
  return response.data;
};

/**
 * Save a generated shopping list.
 */
export const saveShoppingList = async (
  shoppingList: ShoppingListResponse
): Promise<ShoppingListResponse> => {
  const response = await apiClient.post<ShoppingListResponse>('/shopping-lists', shoppingList);
  return response.data;
};

/**
 * Delete a saved shopping list.
 */
export const deleteShoppingList = async (id: number): Promise<void> => {
  await apiClient.delete(`/shopping-lists/${id}`);
};

/**
 * Export shopping list in various formats.
 */
export const exportShoppingList = async (
  request: ShoppingListExportRequest
): Promise<ShoppingListExportResponse> => {
  const response = await apiClient.post<ShoppingListExportResponse>(
    '/shopping-lists/export',
    request
  );
  return response.data;
};

/**
 * Export shopping list to markdown.
 */
export const exportShoppingListMarkdown = async (
  shoppingListId: number,
  options?: Partial<ShoppingListExportRequest>
): Promise<string> => {
  const response = await exportShoppingList({
    shopping_list_id: shoppingListId,
    format: ShoppingListFormat.MARKDOWN,
    include_recipe_names: options?.include_recipe_names ?? true,
    include_checkboxes: options?.include_checkboxes ?? true,
    group_by_store_section: options?.group_by_store_section ?? false,
  });

  return response.content ?? '';
};

/**
 * Export shopping list to PDF.
 */
export const exportShoppingListPDF = async (
  shoppingListId: number,
  options?: Partial<ShoppingListExportRequest>
): Promise<string> => {
  const response = await exportShoppingList({
    shopping_list_id: shoppingListId,
    format: ShoppingListFormat.PDF,
    include_recipe_names: options?.include_recipe_names ?? true,
    include_checkboxes: options?.include_checkboxes ?? true,
    group_by_store_section: options?.group_by_store_section ?? false,
  });

  return response.download_url ?? '';
};
