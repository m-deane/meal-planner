# API Client Documentation

Complete TypeScript API client, types, and React Query hooks for the Meal Planner frontend.

## Table of Contents

- [Setup](#setup)
- [Architecture](#architecture)
- [Types](#types)
- [API Client](#api-client)
- [React Query Hooks](#react-query-hooks)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Setup

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Install Dependencies

```bash
npm install @tanstack/react-query axios
```

### Configure React Query

In your `main.tsx` or `App.tsx`:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app components */}
    </QueryClientProvider>
  );
}
```

## Architecture

### Directory Structure

```
src/
├── types/
│   ├── recipe.ts          # Recipe-related types
│   ├── mealPlan.ts        # Meal plan types
│   ├── shoppingList.ts    # Shopping list types
│   ├── pagination.ts      # Pagination types
│   └── index.ts           # Type exports
├── api/
│   ├── client.ts          # Axios instance with interceptors
│   ├── recipes.ts         # Recipe API functions
│   ├── mealPlans.ts       # Meal plan API functions
│   ├── shoppingLists.ts   # Shopping list API functions
│   ├── categories.ts      # Categories/tags API functions
│   └── index.ts           # API exports
└── hooks/
    ├── useRecipes.ts      # Recipe query hooks
    ├── useMealPlan.ts     # Meal plan hooks
    ├── useShoppingList.ts # Shopping list hooks
    ├── useCategories.ts   # Category hooks
    ├── useDebounce.ts     # Utility hook
    └── index.ts           # Hook exports
```

## Types

All types are fully typed to match the backend Pydantic schemas.

### Recipe Types

```typescript
import type { Recipe, RecipeListItem, RecipeFilters } from '@/types';

// Full recipe with all details
const recipe: Recipe = { ... };

// Lightweight recipe for lists
const listItem: RecipeListItem = { ... };

// Filter criteria
const filters: RecipeFilters = {
  category_slugs: ['italian'],
  dietary_tag_slugs: ['vegetarian'],
  max_total_time: 45,
  nutrition: {
    max_calories: 600,
    min_protein_g: 20,
  },
};
```

### Meal Plan Types

```typescript
import type { MealPlanGenerateRequest, MealPlanResponse } from '@/types';

const request: MealPlanGenerateRequest = {
  days: 7,
  start_date: '2026-01-20',
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
};
```

## API Client

### Base Configuration

The API client includes:
- Automatic authorization header injection
- Global error handling
- Request/response interceptors
- Type-safe responses

```typescript
import { apiClient } from '@/api/client';

// All API calls use this pre-configured client
const response = await apiClient.get('/recipes');
```

### Error Handling

```typescript
import { isAPIError, formatAPIError } from '@/api/client';

try {
  const recipe = await getRecipeById(123);
} catch (error) {
  if (isAPIError(error)) {
    console.error(error.message);
    console.error(error.status);
    console.error(error.errors); // Validation errors
  }
}
```

## React Query Hooks

### Recipe Hooks

#### Basic Recipe List

```typescript
import { useRecipes } from '@/hooks';

function RecipeList() {
  const { data, isLoading, error } = useRecipes(
    {
      category_slugs: ['italian'],
      max_total_time: 45,
    },
    { page: 1, page_size: 20 }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.items.map(recipe => (
        <div key={recipe.id}>{recipe.name}</div>
      ))}
    </div>
  );
}
```

#### Infinite Scroll Recipes

```typescript
import { useInfiniteRecipes } from '@/hooks';

function InfiniteRecipeList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteRecipes({ max_total_time: 30 });

  return (
    <div>
      {data?.pages.map((page) =>
        page.items.map((recipe) => (
          <div key={recipe.id}>{recipe.name}</div>
        ))
      )}
      {hasNextPage && (
        <button onClick={() => fetchNextPage()}>
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

#### Recipe Search with Debouncing

```typescript
import { useRecipeSearch } from '@/hooks';
import { useState } from 'react';

function RecipeSearch() {
  const [query, setQuery] = useState('');
  const { data, isLoading } = useRecipeSearch(query, 300); // 300ms debounce

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search recipes..."
      />
      {isLoading && <div>Searching...</div>}
      {data?.items.map(recipe => (
        <div key={recipe.id}>{recipe.name}</div>
      ))}
    </div>
  );
}
```

#### Single Recipe

```typescript
import { useRecipe } from '@/hooks';

function RecipeDetail({ id }: { id: number }) {
  const { data: recipe, isLoading } = useRecipe(id);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{recipe?.name}</h1>
      <p>{recipe?.description}</p>
      <h2>Ingredients</h2>
      <ul>
        {recipe?.ingredients.map((ing, idx) => (
          <li key={idx}>
            {ing.quantity} {ing.unit} {ing.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Meal Plan Hooks

#### Generate Meal Plan

```typescript
import { useGenerateMealPlan } from '@/hooks';

function MealPlanGenerator() {
  const generateMealPlan = useGenerateMealPlan();

  const handleGenerate = async () => {
    const mealPlan = await generateMealPlan.mutateAsync({
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
      max_recipe_reuse: 1,
      variety_score_weight: 0.3,
      optimize_shopping_list: true,
    });

    console.log('Generated meal plan:', mealPlan);
  };

  return (
    <button
      onClick={handleGenerate}
      disabled={generateMealPlan.isPending}
    >
      {generateMealPlan.isPending ? 'Generating...' : 'Generate Meal Plan'}
    </button>
  );
}
```

#### Nutrition-Optimized Meal Plan

```typescript
import { useGenerateNutritionMealPlan } from '@/hooks';

function NutritionMealPlanGenerator() {
  const generatePlan = useGenerateNutritionMealPlan();

  const handleGenerate = async () => {
    const plan = await generatePlan.mutateAsync({
      days: 7,
      meal_preferences: {
        include_breakfast: true,
        include_lunch: true,
        include_dinner: true,
        include_snacks: false,
        breakfast_calories_pct: 25,
        lunch_calories_pct: 35,
        dinner_calories_pct: 40,
      },
      nutrition_constraints: {
        target_calories: 2000,
        target_protein_g: 150,
        max_carbs_g: 250,
        max_fat_g: 70,
        min_fiber_g: 25,
      },
      dietary_tag_slugs: ['high-protein'],
      avoid_duplicate_recipes: true,
    });

    console.log('Nutrition plan:', plan);
  };

  return (
    <button onClick={handleGenerate} disabled={generatePlan.isPending}>
      Generate Nutrition Plan
    </button>
  );
}
```

#### Save and Manage Meal Plans

```typescript
import {
  useMealPlans,
  useSaveMealPlan,
  useDeleteMealPlan,
} from '@/hooks';

function SavedMealPlans() {
  const { data: mealPlans } = useMealPlans();
  const saveMealPlan = useSaveMealPlan();
  const deleteMealPlan = useDeleteMealPlan();

  const handleSave = async (plan: MealPlanResponse) => {
    await saveMealPlan.mutateAsync(plan);
  };

  const handleDelete = async (id: number) => {
    await deleteMealPlan.mutateAsync(id);
  };

  return (
    <div>
      {mealPlans?.map(plan => (
        <div key={plan.id}>
          <h3>{plan.total_days} Day Plan</h3>
          <button onClick={() => handleDelete(plan.id!)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

### Shopping List Hooks

#### Generate Shopping List from Recipes

```typescript
import { useGenerateShoppingList } from '@/hooks';

function ShoppingListGenerator() {
  const generateList = useGenerateShoppingList();

  const handleGenerate = async (recipeIds: number[]) => {
    const shoppingList = await generateList.mutateAsync({
      recipeIds,
      options: {
        group_by_category: true,
        combine_similar_ingredients: true,
        exclude_pantry_staples: true,
        servings_multiplier: 1.5,
      },
    });

    console.log('Shopping list:', shoppingList);
  };

  return (
    <button onClick={() => handleGenerate([1, 2, 3])}>
      Generate Shopping List
    </button>
  );
}
```

#### Generate from Meal Plan

```typescript
import { useGenerateShoppingListFromMealPlan } from '@/hooks';

function MealPlanShoppingList({ mealPlanId }: { mealPlanId: number }) {
  const generateList = useGenerateShoppingListFromMealPlan();

  const handleGenerate = async () => {
    const shoppingList = await generateList.mutateAsync({
      mealPlanId,
      options: {
        exclude_pantry_staples: true,
        round_quantities: true,
      },
    });

    console.log('Shopping list:', shoppingList);
  };

  return <button onClick={handleGenerate}>Generate Shopping List</button>;
}
```

### Category Hooks

#### Fetch Categories, Tags, and Allergens

```typescript
import { useCategories, useDietaryTags, useAllergens } from '@/hooks';

function FilterOptions() {
  const { data: categories } = useCategories();
  const { data: dietaryTags } = useDietaryTags();
  const { data: allergens } = useAllergens();

  return (
    <div>
      <h3>Categories</h3>
      {categories?.map(cat => (
        <div key={cat.id}>{cat.name}</div>
      ))}

      <h3>Dietary Tags</h3>
      {dietaryTags?.map(tag => (
        <div key={tag.id}>{tag.name}</div>
      ))}

      <h3>Allergens</h3>
      {allergens?.map(allergen => (
        <div key={allergen.id}>{allergen.name}</div>
      ))}
    </div>
  );
}
```

## Error Handling

### Global Error Handling

The API client automatically handles errors and transforms them into `APIError` objects.

```typescript
interface APIError {
  message: string;
  status?: number;
  errors?: Array<{
    field?: string;
    message: string;
  }>;
}
```

### Component-Level Error Handling

```typescript
import { formatAPIError } from '@/api/client';

function RecipeList() {
  const { data, error } = useRecipes();

  if (error) {
    return <div className="error">{formatAPIError(error)}</div>;
  }

  // ... rest of component
}
```

### Mutation Error Handling

```typescript
function MealPlanGenerator() {
  const generatePlan = useGenerateMealPlan();

  const handleGenerate = async () => {
    try {
      const plan = await generatePlan.mutateAsync({...});
      // Success
    } catch (error) {
      if (isAPIError(error)) {
        console.error('Validation errors:', error.errors);
        alert(formatAPIError(error));
      }
    }
  };
}
```

## Best Practices

### 1. Use Query Keys Consistently

```typescript
import { recipeKeys } from '@/hooks';

// Invalidate queries
queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });

// Prefetch data
queryClient.prefetchQuery({
  queryKey: recipeKeys.detail(123),
  queryFn: () => getRecipeById(123),
});
```

### 2. Leverage Stale Time

```typescript
// Categories rarely change, use longer stale time
const { data: categories } = useCategories(); // 30 min stale time

// Search results change frequently, use shorter stale time
const { data: results } = useRecipeSearch(query); // 2 min stale time
```

### 3. Optimistic Updates

```typescript
const deleteMealPlan = useDeleteMealPlan();

const handleDelete = async (id: number) => {
  // Optimistically remove from cache
  queryClient.setQueryData(
    mealPlanKeys.list(),
    (old) => old?.filter(plan => plan.id !== id)
  );

  try {
    await deleteMealPlan.mutateAsync(id);
  } catch (error) {
    // Revert on error
    queryClient.invalidateQueries({ queryKey: mealPlanKeys.list() });
  }
};
```

### 4. Debounce User Input

```typescript
// useDebounce automatically included
const { data } = useRecipeSearch(query, 300); // 300ms debounce
```

### 5. Handle Loading and Error States

```typescript
function RecipeList() {
  const { data, isLoading, error, isFetching } = useRecipes();

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {isFetching && <LoadingOverlay />}
      {data?.items.map(recipe => <RecipeCard key={recipe.id} recipe={recipe} />)}
    </div>
  );
}
```

### 6. Type Safety

All hooks and API functions are fully typed. Always leverage TypeScript's type system:

```typescript
// Type inference works automatically
const { data } = useRecipe(123); // data is Recipe | undefined

// Explicit typing when needed
const filters: RecipeFilters = {
  max_total_time: 30,
  difficulty: [DifficultyLevel.EASY, DifficultyLevel.MEDIUM],
};
```

## Query Configuration

Default configurations are optimized for the meal planner use case:

- **Stale Time**: 5 minutes (recipes), 30 minutes (categories)
- **Cache Time**: 10-60 minutes depending on data type
- **Retry**: 1 attempt
- **Refetch on Window Focus**: Disabled

Override as needed:

```typescript
const { data } = useRecipes(filters, pagination, sort, {
  staleTime: 10 * 60 * 1000,
  refetchOnWindowFocus: true,
});
```

## Authentication

The API client automatically includes the auth token from localStorage:

```typescript
// Set token (usually after login)
localStorage.setItem('auth_token', 'your-jwt-token');

// Remove token (logout)
localStorage.removeItem('auth_token');

// Client automatically handles 401 responses and redirects to /login
```

## Type Exports

All types are exported from a central location:

```typescript
import type {
  Recipe,
  RecipeListItem,
  RecipeFilters,
  MealPlanGenerateRequest,
  MealPlanResponse,
  ShoppingListResponse,
  Category,
  DietaryTag,
  Allergen,
  PaginatedResponse,
} from '@/types';
```

## Files Reference

- **Types**: `/home/user/meal-planner/frontend/src/types/`
- **API Functions**: `/home/user/meal-planner/frontend/src/api/`
- **React Query Hooks**: `/home/user/meal-planner/frontend/src/hooks/`

All files use strict TypeScript configuration with comprehensive type safety.
