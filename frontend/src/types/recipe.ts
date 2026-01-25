/**
 * Recipe-related TypeScript types matching backend Pydantic schemas.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum DifficultyLevel {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum ImageType {
  MAIN = 'main',
  STEP = 'step',
  THUMBNAIL = 'thumbnail',
  HERO = 'hero',
}

export enum CategoryType {
  CUISINE = 'cuisine',
  MEAL_TYPE = 'meal_type',
  OCCASION = 'occasion',
}

// ============================================================================
// NESTED TYPES
// ============================================================================

export interface Unit {
  id: number;
  name: string;
  abbreviation: string;
  unit_type: string;
}

export interface Ingredient {
  name: string;
  quantity: number | null;
  unit: string | null;
  unit_name: string | null;
  preparation_note: string | null;
  is_optional: boolean;
  category: string | null;
  display_order: number;
}

export interface Instruction {
  // API may return these as either step_number/instruction or step/text
  step_number?: number | null;
  step?: number | null;  // Alias from API
  instruction?: string | null;
  text?: string | null;  // Alias from API
  time_minutes: number | null;
}

export interface Image {
  id: number;
  url: string;
  image_type: ImageType;
  display_order: number;
  alt_text: string | null;
  width: number | null;
  height: number | null;
}

export interface Nutrition {
  calories: number | null;
  protein_g: number | null;
  carbohydrates_g: number | null;
  fat_g: number | null;
  saturated_fat_g: number | null;
  fiber_g: number | null;
  sugar_g: number | null;
  sodium_mg: number | null;
  cholesterol_mg: number | null;
  serving_size_g: number | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  category_type: CategoryType;
  description: string | null;
}

export interface DietaryTag {
  id: number;
  name: string;
  slug: string;
  description: string | null;
}

export interface Allergen {
  id: number;
  name: string;
  description: string | null;
}

// ============================================================================
// MAIN RECIPE TYPES
// ============================================================================

export interface RecipeBase {
  name: string;
  description: string | null;
  cooking_time_minutes: number | null;
  prep_time_minutes: number | null;
  difficulty: DifficultyLevel | null;
  servings: number;
}

export interface RecipeListItem extends RecipeBase {
  id: number;
  slug: string;
  total_time_minutes: number | null;
  categories: Category[];
  dietary_tags: DietaryTag[];
  allergens: Allergen[];
  main_image: Image | null;
  nutrition_summary: {
    calories?: number | null;
    protein_g?: number | null;
    carbohydrates_g?: number | null;
    fat_g?: number | null;
  } | null;
  is_active: boolean;
}

export interface Recipe extends RecipeBase {
  id: number;
  gousto_id: string;
  slug: string;
  total_time_minutes: number | null;
  source_url: string;
  date_scraped: string;
  last_updated: string;
  is_active: boolean;
  ingredients: Ingredient[];
  instructions: Instruction[];
  categories: Category[];
  dietary_tags: DietaryTag[];
  allergens: Allergen[];
  images: Image[];
  nutritional_info: Nutrition | null;
}

// ============================================================================
// FILTER TYPES
// ============================================================================

export interface NutritionFilters {
  min_calories?: number;
  max_calories?: number;
  min_protein_g?: number;
  max_protein_g?: number;
  min_carbs_g?: number;
  max_carbs_g?: number;
  min_fat_g?: number;
  max_fat_g?: number;
  min_fiber_g?: number;
  max_sugar_g?: number;
}

export interface RecipeFilters {
  category_ids?: number[];
  category_slugs?: string[];
  dietary_tag_ids?: number[];
  dietary_tag_slugs?: string[];
  exclude_allergen_ids?: number[];
  exclude_allergen_names?: string[];
  max_cooking_time?: number;
  max_prep_time?: number;
  max_total_time?: number;
  difficulty?: DifficultyLevel[];
  min_servings?: number;
  max_servings?: number;
  search_query?: string;
  include_ingredients?: string[];
  exclude_ingredients?: string[];
  nutrition?: NutritionFilters;
  only_active?: boolean;
}
