/**
 * Central export point for all API functions.
 */

// Client and error handling
export { apiClient, isAPIError, formatAPIError } from './client';

// Recipe API
export {
  getRecipes,
  getRecipeById,
  getRecipeBySlug,
  searchRecipes,
  getRandomRecipes,
  getFeaturedRecipes,
} from './recipes';

// Meal plan API
export {
  generateMealPlan,
  generateNutritionMealPlan,
  getMealPlanById,
  getMealPlans,
  saveMealPlan,
  deleteMealPlan,
  exportMealPlanMarkdown,
  exportMealPlanPDF,
} from './mealPlans';

// Shopping list API
export {
  generateShoppingList,
  generateShoppingListFromMealPlan,
  getShoppingListById,
  getShoppingLists,
  saveShoppingList,
  deleteShoppingList,
  exportShoppingList,
  exportShoppingListMarkdown,
  exportShoppingListPDF,
} from './shoppingLists';

// Category API
export {
  getCategories,
  getDietaryTags,
  getAllergens,
  getCategoryBySlug,
  getDietaryTagBySlug,
} from './categories';

// Favorites API
export {
  getFavorites,
  addFavorite,
  removeFavorite,
  updateFavorite,
  checkIsFavorite,
} from './favorites';

// Cost API
export {
  getRecipeCost,
  getMealPlanCost,
  getBudgetRecipes,
  getCheaperAlternatives,
} from './cost';

// Multi-week planning API
export {
  generateMultiWeekPlan,
  getMultiWeekPlan,
  getMultiWeekPlans,
  updateMultiWeekPlan,
  deleteMultiWeekPlan,
  getVarietyAnalysis,
  getVarietyScore,
} from './multiWeek';
