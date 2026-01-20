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

export interface ShoppingItem {
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  category: IngredientCategory;
  is_optional: boolean;
  notes: string | null;
  recipe_count: number;
  recipe_names: string[];
}

export interface ShoppingCategory {
  name: IngredientCategory;
  display_name: string;
  items: ShoppingItem[];
  item_count: number;
}

export interface ShoppingListSummary {
  total_items: number;
  total_categories: number;
  total_recipes: number;
  estimated_cost: number | null;
}

export interface ShoppingListResponse {
  id: number | null;
  categories: ShoppingCategory[];
  uncategorized_items: ShoppingItem[];
  summary: ShoppingListSummary;
  source_recipe_ids: number[];
  source_meal_plan_id: number | null;
  servings_multiplier: number;
  pantry_staples_excluded: string[];
  optional_items: ShoppingItem[];
  markdown_url: string | null;
  pdf_url: string | null;
}

export interface ShoppingListExportResponse {
  format: ShoppingListFormat;
  content: string | null;
  download_url: string | null;
  file_size_bytes: number | null;
  expires_at: string | null;
}
