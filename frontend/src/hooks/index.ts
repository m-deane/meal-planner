/**
 * Central export point for all custom hooks.
 */

// Recipe hooks
export {
  useRecipes,
  useInfiniteRecipes,
  useRecipe,
  useRecipeBySlug,
  useRecipeSearch,
  useRandomRecipes,
  useFeaturedRecipes,
  recipeKeys,
} from './useRecipes';

// Meal plan hooks
export {
  useGenerateMealPlan,
  useGenerateNutritionMealPlan,
  useMealPlan,
  useMealPlans,
  useSaveMealPlan,
  useDeleteMealPlan,
  useExportMealPlanMarkdown,
  useExportMealPlanPDF,
  mealPlanKeys,
} from './useMealPlan';

// Shopping list hooks
export {
  useGenerateShoppingList,
  useGenerateShoppingListFromMealPlan,
  useShoppingList,
  useShoppingLists,
  useSaveShoppingList,
  useDeleteShoppingList,
  useExportShoppingListMarkdown,
  useExportShoppingListPDF,
  shoppingListKeys,
} from './useShoppingList';

// Category hooks
export {
  useCategories,
  useDietaryTags,
  useAllergens,
  useCategoryBySlug,
  useDietaryTagBySlug,
  categoryKeys,
  dietaryTagKeys,
  allergenKeys,
} from './useCategories';

// Authentication hooks
export {
  useLogin,
  useRegister,
  useLogout,
  useCurrentUser,
  useIsAuthenticated,
  useUpdateProfile,
  useChangePassword,
  useVerifyToken,
  authKeys,
} from './useAuth';

// User hooks
export {
  usePreferences,
  useUpdatePreferences,
  useAllergens as useUserAllergens,
  useUpdateAllergens,
  useFavorites,
  useInfiniteFavorites,
  useAddFavorite,
  useRemoveFavorite,
  useIsFavorite,
  useToggleFavorite,
  userKeys,
} from './useUser';

// Cost estimation hooks
export {
  useRecipeCost,
  useMealPlanCost,
  useBudgetRecipes,
  useCheaperAlternatives,
  useAverageCostsByCategory,
  costKeys,
} from './useCost';

// Multi-week planning hooks
export {
  useMultiWeekPlans,
  useMultiWeekPlan,
  useGenerateMultiWeekPlan,
  useUpdateMultiWeekPlan,
  useDeleteMultiWeekPlan,
  useVarietyAnalysis,
  useVarietyScore,
  multiWeekKeys,
} from './useMultiWeek';

// Utility hooks
export { useDebounce } from './useDebounce';
