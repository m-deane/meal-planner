/**
 * Central export point for all TypeScript types.
 */

// Recipe types
export type {
  Unit,
  Ingredient,
  Instruction,
  Image,
  Nutrition,
  Category,
  DietaryTag,
  Allergen,
  RecipeBase,
  RecipeListItem,
  Recipe,
  NutritionFilters,
  RecipeFilters,
} from './recipe';

export { DifficultyLevel, ImageType, CategoryType } from './recipe';

// Pagination types
export type {
  PaginationParams,
  SortParams,
  PaginatedResponse,
} from './pagination';

export { SortOrder } from './pagination';

// Meal plan types
export type {
  NutritionConstraints,
  MealPreferences,
  MealPlanGenerateRequest,
  MealSlot,
  DayPlan,
  ShoppingListPreview,
  MealPlanSummary,
  MealPlanResponse,
} from './mealPlan';

export { MealType } from './mealPlan';

// Shopping list types
export type {
  ShoppingListGenerateRequest,
  ShoppingListExportRequest,
  ShoppingItem,
  ShoppingCategory,
  ShoppingListSummary,
  ShoppingListResponse,
  ShoppingListExportResponse,
} from './shoppingList';

export { IngredientCategory, ShoppingListFormat } from './shoppingList';

// Favorites types
export type {
  FavoriteRecipe,
  FavoritesResponse,
  AddFavoriteRequest,
  UpdateFavoriteRequest,
} from './favorites';

export { FavoritesSortBy } from './favorites';

// Cost estimation types
export type {
  IngredientCost,
  RecipeCost,
  DayCostBreakdown,
  MealPlanCostBreakdown,
  BudgetRecipe,
  BudgetRecipesResponse,
  CostAlternative,
  CostAlternativesResponse,
  RecipeCostRequest,
  MealPlanCostRequest,
  BudgetRecipesRequest,
  CostAlternativesRequest,
} from './cost';

// Multi-week planning types
export type {
  WeekPlanSummary,
  MultiWeekPlan,
  VarietyMetrics,
  VarietyBreakdown,
  VarietySuggestion,
  MultiWeekGenerateRequest,
  MultiWeekUpdateRequest,
} from './multiWeek';

// User and authentication types
export type {
  User,
  UserPreference,
  UserAllergen,
  UserFavorite,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  PasswordChangeRequest,
  UserUpdateRequest,
  PreferenceUpdateRequest,
  AllergenUpdateRequest,
  FavoriteAddRequest,
} from './user';

export { AllergenSeverity, UserRole } from './user';

// API error types
export interface APIError {
  message: string;
  status?: number;
  errors?: Array<{
    field?: string;
    message: string;
  }>;
}
