# API Client Implementation Summary

Complete TypeScript API client, types, and React Query hooks for the Meal Planner frontend.

## Files Created

### Type Definitions (`/home/user/meal-planner/frontend/src/types/`)

1. **recipe.ts** - Recipe types matching backend schemas
   - Enums: `DifficultyLevel`, `ImageType`, `CategoryType`
   - Types: `Recipe`, `RecipeListItem`, `Ingredient`, `Instruction`, `Nutrition`, `Category`, `DietaryTag`, `Allergen`
   - Filters: `RecipeFilters`, `NutritionFilters`

2. **mealPlan.ts** - Meal plan types
   - Enum: `MealType`
   - Request: `MealPlanGenerateRequest`, `NutritionConstraints`, `MealPreferences`
   - Response: `MealPlanResponse`, `DayPlan`, `MealSlot`, `MealPlanSummary`

3. **shoppingList.ts** - Shopping list types
   - Enums: `IngredientCategory`, `ShoppingListFormat`
   - Request: `ShoppingListGenerateRequest`, `ShoppingListExportRequest`
   - Response: `ShoppingListResponse`, `ShoppingItem`, `ShoppingCategory`

4. **pagination.ts** - Pagination and sorting types
   - Enum: `SortOrder`
   - Types: `PaginationParams`, `SortParams`, `PaginatedResponse<T>`

5. **index.ts** - Central type exports including `APIError` interface

### API Functions (`/home/user/meal-planner/frontend/src/api/`)

1. **client.ts** - Axios instance with interceptors
   - Auto-injects auth token from localStorage
   - Handles 401 redirects to login
   - Transforms API errors to `APIError` type
   - Utility functions: `isAPIError()`, `formatAPIError()`

2. **recipes.ts** - Recipe endpoints
   - `getRecipes()` - Paginated list with filters
   - `getRecipeById()` - Single recipe by ID
   - `getRecipeBySlug()` - Single recipe by slug
   - `searchRecipes()` - Search with query
   - `getRandomRecipes()` - Random recipes
   - `getFeaturedRecipes()` - Featured recipes

3. **mealPlans.ts** - Meal plan endpoints
   - `generateMealPlan()` - Generate standard meal plan
   - `generateNutritionMealPlan()` - Generate nutrition-optimized plan
   - `getMealPlanById()` - Get saved plan
   - `getMealPlans()` - List all saved plans
   - `saveMealPlan()` - Save a plan
   - `deleteMealPlan()` - Delete a plan
   - `exportMealPlanMarkdown()` - Export to markdown
   - `exportMealPlanPDF()` - Export to PDF

4. **shoppingLists.ts** - Shopping list endpoints
   - `generateShoppingList()` - From recipe IDs
   - `generateShoppingListFromMealPlan()` - From meal plan
   - `getShoppingListById()` - Get saved list
   - `getShoppingLists()` - List all saved lists
   - `saveShoppingList()` - Save a list
   - `deleteShoppingList()` - Delete a list
   - `exportShoppingList()` - Export in various formats
   - `exportShoppingListMarkdown()` - Export to markdown
   - `exportShoppingListPDF()` - Export to PDF

5. **categories.ts** - Category, tag, and allergen endpoints
   - `getCategories()` - All categories
   - `getDietaryTags()` - All dietary tags
   - `getAllergens()` - All allergens
   - `getCategoryBySlug()` - Single category
   - `getDietaryTagBySlug()` - Single tag

6. **index.ts** - Central API exports

### React Query Hooks (`/home/user/meal-planner/frontend/src/hooks/`)

1. **useRecipes.ts** - Recipe data fetching hooks
   - `useRecipes()` - Basic paginated query
   - `useInfiniteRecipes()` - Infinite scroll query
   - `useRecipe()` - Single recipe by ID
   - `useRecipeBySlug()` - Single recipe by slug
   - `useRecipeSearch()` - Debounced search (300ms)
   - `useRandomRecipes()` - Random recipes
   - `useFeaturedRecipes()` - Featured recipes
   - `recipeKeys` - Query key factory

2. **useMealPlan.ts** - Meal plan hooks
   - `useGenerateMealPlan()` - Generate mutation
   - `useGenerateNutritionMealPlan()` - Nutrition-optimized mutation
   - `useMealPlan()` - Get single plan
   - `useMealPlans()` - List all plans
   - `useSaveMealPlan()` - Save mutation
   - `useDeleteMealPlan()` - Delete mutation
   - `useExportMealPlanMarkdown()` - Export markdown mutation
   - `useExportMealPlanPDF()` - Export PDF mutation
   - `mealPlanKeys` - Query key factory

3. **useShoppingList.ts** - Shopping list hooks
   - `useGenerateShoppingList()` - Generate from recipes mutation
   - `useGenerateShoppingListFromMealPlan()` - Generate from meal plan mutation
   - `useShoppingList()` - Get single list
   - `useShoppingLists()` - List all lists
   - `useSaveShoppingList()` - Save mutation
   - `useDeleteShoppingList()` - Delete mutation
   - `useExportShoppingListMarkdown()` - Export markdown mutation
   - `useExportShoppingListPDF()` - Export PDF mutation
   - `shoppingListKeys` - Query key factory

4. **useCategories.ts** - Category and tag hooks
   - `useCategories()` - All categories (30 min cache)
   - `useDietaryTags()` - All dietary tags (30 min cache)
   - `useAllergens()` - All allergens (30 min cache)
   - `useCategoryBySlug()` - Single category
   - `useDietaryTagBySlug()` - Single tag
   - Query key factories for each

5. **useDebounce.ts** - Utility hook for debouncing
   - Generic debounce hook used by search

6. **index.ts** - Central hook exports

### Documentation

1. **API_DOCUMENTATION.md** - Complete usage guide
   - Setup instructions
   - Architecture overview
   - Type examples
   - Hook usage examples
   - Error handling patterns
   - Best practices

2. **API_CLIENT_SUMMARY.md** (this file) - Quick reference

## Key Features

### Type Safety
- All types match backend Pydantic schemas exactly
- Full TypeScript strict mode compliance
- Comprehensive type inference
- Generic types for reusable components (`PaginatedResponse<T>`)

### Error Handling
- Automatic error transformation to `APIError` type
- FastAPI validation error parsing
- HTTP status code handling (401, 403, 404, 422, 429, 500, 503)
- Auto-redirect to login on 401
- Type guards: `isAPIError()`
- Formatting utilities: `formatAPIError()`

### Caching Strategy
- Recipes: 5 min stale time, 10 min cache
- Categories/Tags: 30 min stale time, 60 min cache
- Search: 2 min stale time, 5 min cache
- Details: 10-30 min based on data type
- Automatic cache invalidation on mutations

### React Query Patterns
- Query key factories for organized invalidation
- Infinite scroll support with `useInfiniteQuery`
- Optimistic updates on mutations
- Automatic cache updates after mutations
- Debounced search queries
- Enabled/disabled queries based on parameters

### Authentication
- Auto-inject Bearer token from localStorage
- Auto-redirect on 401 responses
- Token management utilities built-in

## Quick Start

### 1. Environment Setup

```bash
# Copy example env
cp .env.example .env

# Edit .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 2. Install Dependencies

```bash
npm install @tanstack/react-query axios
```

### 3. Configure React Query Provider

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app */}
    </QueryClientProvider>
  );
}
```

### 4. Use Hooks in Components

```typescript
import { useRecipes, useGenerateMealPlan } from '@/hooks';

function RecipeList() {
  const { data, isLoading } = useRecipes({
    max_total_time: 45,
    dietary_tag_slugs: ['vegetarian'],
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {data?.items.map(recipe => (
        <div key={recipe.id}>{recipe.name}</div>
      ))}
    </div>
  );
}

function MealPlanGenerator() {
  const generatePlan = useGenerateMealPlan();

  const handleGenerate = async () => {
    const plan = await generatePlan.mutateAsync({
      days: 7,
      meal_preferences: {
        include_breakfast: true,
        include_lunch: true,
        include_dinner: true,
        include_snacks: false,
      },
      nutrition_constraints: {
        target_calories: 2000,
        min_protein_g: 100,
      },
      avoid_duplicate_recipes: true,
    });

    console.log('Generated plan:', plan);
  };

  return (
    <button onClick={handleGenerate} disabled={generatePlan.isPending}>
      Generate Meal Plan
    </button>
  );
}
```

## Import Patterns

```typescript
// Types
import type { Recipe, RecipeFilters, MealPlanResponse } from '@/types';

// API Functions (direct use, rare)
import { getRecipeById } from '@/api';

// Hooks (primary usage)
import { useRecipes, useGenerateMealPlan } from '@/hooks';

// Error handling
import { isAPIError, formatAPIError } from '@/api/client';
```

## Testing Considerations

All functions and hooks are designed for easy testing:

- Pure functions for API calls
- No side effects in hooks
- Mockable axios instance
- Query key factories for test setup
- Type-safe mocks with TypeScript

## Performance Optimizations

- Debounced search (300ms default)
- Infinite scroll for large lists
- Optimized stale times per data type
- Query key factories prevent unnecessary refetches
- Automatic cache invalidation
- Request deduplication via React Query

## Next Steps

1. Read `API_DOCUMENTATION.md` for detailed usage examples
2. Configure environment variables
3. Set up React Query provider
4. Import and use hooks in components
5. Implement error boundaries for error handling
6. Add loading states and skeletons
7. Implement optimistic updates where needed

## File Paths

All files are located in:
- Types: `/home/user/meal-planner/frontend/src/types/`
- API: `/home/user/meal-planner/frontend/src/api/`
- Hooks: `/home/user/meal-planner/frontend/src/hooks/`

## Support

For detailed examples and patterns, see `API_DOCUMENTATION.md`.
