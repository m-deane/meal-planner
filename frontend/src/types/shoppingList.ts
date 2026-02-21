/**
 * Shopping list types matching backend schemas.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum IngredientCategory {
  PROTEIN = 'protein',
  DAIRY = 'dairy',
  VEGETABLES = 'vegetables',
  FRUITS = 'fruits',
  GRAINS = 'grains',
  PANTRY = 'pantry',
  SPICES = 'spices',
  CONDIMENTS = 'condiments',
  BEVERAGES = 'beverages',
  FROZEN = 'frozen',
  BAKERY = 'bakery',
  OTHER = 'other',
}

export enum ShoppingListFormat {
  JSON = 'json',
  MARKDOWN = 'markdown',
  TEXT = 'text',
  PDF = 'pdf',
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface ShoppingListGenerateRequest {
  recipe_ids?: number[];
  meal_plan_id?: number;
  servings_multiplier: number;
  group_by_category: boolean;
  combine_similar_ingredients: boolean;
  exclude_pantry_staples: boolean;
  pantry_staples?: string[];
  include_optional_ingredients: boolean;
  round_quantities: boolean;
}

export interface ShoppingListExportRequest {
  shopping_list_id: number;
  format: ShoppingListFormat;
  include_recipe_names: boolean;
  include_checkboxes: boolean;
  group_by_store_section: boolean;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

/**
 * A single quantity entry for a shopping list item.
 * Matches backend format: { unit, total, count }
 */
export interface ShoppingItemQuantity {
  unit: string;
  total: number | null;
  count: number | null;
}

/**
 * A single item in the shopping list.
 * Matches backend format returned by ShoppingListService.format_shopping_list_response:
 * { name, times_needed, quantities: [{unit, total, count}], preparations }
 */
export interface ShoppingItem {
  name: string;
  times_needed: number;
  quantities: ShoppingItemQuantity[];
  preparations: string[];
}

/**
 * A category grouping of shopping items.
 * Matches backend format: { name, items, item_count }
 */
export interface ShoppingCategory {
  name: string;
  items: ShoppingItem[];
  item_count: number;
}

/**
 * Summary statistics for the shopping list.
 * Matches backend format: { total_items, total_categories, recipes_count }
 */
export interface ShoppingListSummary {
  total_items: number;
  total_categories: number;
  recipes_count: number;
}

/**
 * Full shopping list response from the backend.
 * Matches backend format: { categories, summary, recipe_ids }
 */
export interface ShoppingListResponse {
  categories: ShoppingCategory[];
  summary: ShoppingListSummary;
  recipe_ids: number[];
}

export interface ShoppingListExportResponse {
  format: ShoppingListFormat;
  content: string | null;
  download_url: string | null;
  file_size_bytes: number | null;
  expires_at: string | null;
}
