/**
 * Favorites TypeScript types for user favorite recipes.
 */

// ============================================================================
// FAVORITE TYPES
// ============================================================================

/**
 * Minimal recipe summary returned inside a FavoriteRecipe.
 * Matches backend RecipeSummary schema.
 */
export interface FavoriteRecipeSummary {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  cooking_time_minutes: number | null;
  difficulty: string | null;
  image_url: string | null;
}

/**
 * A single favorite record as returned by the backend.
 * Matches backend FavoriteRecipeResponse schema:
 * { id, recipe: RecipeSummary, notes, created_at }
 */
export interface FavoriteRecipe {
  id: number;
  recipe: FavoriteRecipeSummary;
  notes: string | null;
  created_at: string;
}

/**
 * Paginated favorites response.
 * Matches backend PaginatedResponse[FavoriteRecipeResponse]:
 * { items, total, page, page_size, total_pages, has_next, has_previous }
 */
export interface FavoritesResponse {
  items: FavoriteRecipe[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
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
