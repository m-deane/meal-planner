/**
 * Favorites TypeScript types for user favorite recipes.
 */

import type { RecipeListItem } from './recipe';

// ============================================================================
// FAVORITE TYPES
// ============================================================================

export interface FavoriteRecipe {
  id: number;
  user_id: number;
  recipe_id: number;
  notes: string | null;
  date_added: string;
  recipe: RecipeListItem;
}

export interface FavoritesResponse {
  favorites: FavoriteRecipe[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AddFavoriteRequest {
  recipe_id: number;
  notes?: string;
}

export interface UpdateFavoriteRequest {
  notes?: string;
}

export enum FavoritesSortBy {
  DATE_ADDED_DESC = 'date_added_desc',
  DATE_ADDED_ASC = 'date_added_asc',
  NAME_ASC = 'name_asc',
  NAME_DESC = 'name_desc',
}
