# API Client Quick Reference

Common patterns and code snippets for the Meal Planner API client.

## Basic Recipe Queries

### Fetch Recipe List with Filters

```typescript
import { useRecipes } from '@/hooks';

const { data, isLoading, error } = useRecipes({
  category_slugs: ['italian', 'pasta'],
  dietary_tag_slugs: ['vegetarian'],
  max_total_time: 45,
  difficulty: ['easy', 'medium'],
  nutrition: {
    max_calories: 600,
    min_protein_g: 20,
  },
});
```

### Infinite Scroll Recipe List

```typescript
import { useInfiniteRecipes } from '@/hooks';

const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useInfiniteRecipes({ max_total_time: 30 }, undefined, 20);

// Render
{data?.pages.map((page) =>
  page.items.map((recipe) => <RecipeCard key={recipe.id} recipe={recipe} />)
)}

// Load more button
{hasNextPage && (
  <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
    {isFetchingNextPage ? 'Loading...' : 'Load More'}
  </button>
)}
```

### Search Recipes (Debounced)

```typescript
import { useRecipeSearch } from '@/hooks';
import { useState } from 'react';

const [query, setQuery] = useState('');
const { data, isLoading } = useRecipeSearch(query, 300); // 300ms debounce

<input
  value={query}
  onChange={(e) => setQuery(e.target.value)}
  placeholder="Search recipes..."
/>
```

### Single Recipe Detail

```typescript
import { useRecipe } from '@/hooks';

const { data: recipe, isLoading } = useRecipe(recipeId);

// By slug
const { data: recipe } = useRecipeBySlug('spaghetti-carbonara');
```

## Meal Plan Generation

### Basic Meal Plan

```typescript
import { useGenerateMealPlan } from '@/hooks';

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
    avoid_duplicate_recipes: true,
    max_recipe_reuse: 1,
    variety_score_weight: 0.3,
    optimize_shopping_list: true,
  });

  console.log(plan);
};
```

### Nutrition-Optimized Meal Plan

```typescript
import { useGenerateNutritionMealPlan } from '@/hooks';

const generatePlan = useGenerateNutritionMealPlan();

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
    min_protein_g: 120,
    max_protein_g: 180,
    max_carbs_g: 250,
    max_fat_g: 70,
    min_fiber_g: 25,
    max_sugar_g: 50,
  },
  dietary_tag_slugs: ['high-protein'],
  exclude_allergen_names: ['nuts', 'shellfish'],
  max_cooking_time: 45,
  difficulty_levels: ['easy', 'medium'],
  avoid_duplicate_recipes: true,
});
```

### List Saved Meal Plans

```typescript
import { useMealPlans } from '@/hooks';

const { data: mealPlans, isLoading } = useMealPlans();

{mealPlans?.map(plan => (
  <div key={plan.id}>
    <h3>{plan.total_days} Day Plan</h3>
    <p>Avg Calories: {plan.average_daily_nutrition?.calories}</p>
  </div>
))}
```

### Save Meal Plan

```typescript
import { useSaveMealPlan } from '@/hooks';

const savePlan = useSaveMealPlan();

const handleSave = async (plan: MealPlanResponse) => {
  await savePlan.mutateAsync(plan);
  // Cache automatically updated
};
```

### Delete Meal Plan

```typescript
import { useDeleteMealPlan } from '@/hooks';

const deletePlan = useDeleteMealPlan();

await deletePlan.mutateAsync(planId);
// Cache automatically invalidated
```

## Shopping Lists

### Generate from Recipes

```typescript
import { useGenerateShoppingList } from '@/hooks';

const generateList = useGenerateShoppingList();

const list = await generateList.mutateAsync({
  recipeIds: [1, 2, 3, 4, 5],
  options: {
    servings_multiplier: 1.5,
    group_by_category: true,
    combine_similar_ingredients: true,
    exclude_pantry_staples: true,
    pantry_staples: ['salt', 'pepper', 'olive oil'],
    round_quantities: true,
  },
});
```

### Generate from Meal Plan

```typescript
import { useGenerateShoppingListFromMealPlan } from '@/hooks';

const generateList = useGenerateShoppingListFromMealPlan();

const list = await generateList.mutateAsync({
  mealPlanId: 123,
  options: {
    exclude_pantry_staples: true,
    round_quantities: true,
  },
});
```

### Display Shopping List

```typescript
import { useShoppingList } from '@/hooks';

const { data: shoppingList } = useShoppingList(listId);

{shoppingList?.categories.map(category => (
  <div key={category.name}>
    <h3>{category.display_name}</h3>
    <ul>
      {category.items.map((item, idx) => (
        <li key={idx}>
          {item.quantity} {item.unit} {item.ingredient_name}
          {item.notes && <span> - {item.notes}</span>}
        </li>
      ))}
    </ul>
  </div>
))}
```

### Export Shopping List

```typescript
import { useExportShoppingListMarkdown, useExportShoppingListPDF } from '@/hooks';

const exportMarkdown = useExportShoppingListMarkdown();
const exportPDF = useExportShoppingListPDF();

// Markdown
const markdown = await exportMarkdown.mutateAsync({
  shoppingListId: 123,
  options: {
    include_recipe_names: true,
    include_checkboxes: true,
  },
});

// PDF
const pdfUrl = await exportPDF.mutateAsync({
  shoppingListId: 123,
});
```

## Categories and Tags

### Fetch All Categories, Tags, Allergens

```typescript
import { useCategories, useDietaryTags, useAllergens } from '@/hooks';

const { data: categories } = useCategories();
const { data: dietaryTags } = useDietaryTags();
const { data: allergens } = useAllergens();

// Render category filter
<select>
  {categories?.map(cat => (
    <option key={cat.id} value={cat.slug}>{cat.name}</option>
  ))}
</select>
```

### Filter Component Example

```typescript
import { useCategories, useDietaryTags } from '@/hooks';
import { useState } from 'react';

function RecipeFilters() {
  const { data: categories } = useCategories();
  const { data: tags } = useDietaryTags();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const toggleCategory = (slug: string) => {
    setSelectedCategories(prev =>
      prev.includes(slug)
        ? prev.filter(s => s !== slug)
        : [...prev, slug]
    );
  };

  return (
    <div>
      <h3>Categories</h3>
      {categories?.map(cat => (
        <label key={cat.id}>
          <input
            type="checkbox"
            checked={selectedCategories.includes(cat.slug)}
            onChange={() => toggleCategory(cat.slug)}
          />
          {cat.name}
        </label>
      ))}

      <h3>Dietary Tags</h3>
      {tags?.map(tag => (
        <label key={tag.id}>
          <input
            type="checkbox"
            checked={selectedTags.includes(tag.slug)}
            onChange={() => toggleTag(tag.slug)}
          />
          {tag.name}
        </label>
      ))}
    </div>
  );
}
```

## Error Handling

### Component Error Display

```typescript
import { formatAPIError } from '@/api/client';

const { data, error, isLoading } = useRecipes();

if (error) {
  return <div className="error">{formatAPIError(error)}</div>;
}
```

### Mutation Error Handling

```typescript
import { isAPIError, formatAPIError } from '@/api/client';

const generatePlan = useGenerateMealPlan();

const handleGenerate = async () => {
  try {
    const plan = await generatePlan.mutateAsync(options);
    toast.success('Meal plan generated!');
  } catch (error) {
    if (isAPIError(error)) {
      if (error.errors) {
        // Show validation errors
        error.errors.forEach(err => {
          toast.error(`${err.field}: ${err.message}`);
        });
      } else {
        toast.error(error.message);
      }
    }
  }
};
```

### Error Boundary Example

```typescript
import { Component, ReactNode } from 'react';
import { formatAPIError } from '@/api/client';

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{formatAPIError(this.state.error)}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Loading States

### Skeleton Loading

```typescript
const { data, isLoading, isFetching } = useRecipes();

if (isLoading) {
  return <RecipeListSkeleton />;
}

return (
  <div className={isFetching ? 'loading-overlay' : ''}>
    {data?.items.map(recipe => <RecipeCard key={recipe.id} recipe={recipe} />)}
  </div>
);
```

### Mutation Loading

```typescript
const generatePlan = useGenerateMealPlan();

<button
  onClick={handleGenerate}
  disabled={generatePlan.isPending}
  className={generatePlan.isPending ? 'loading' : ''}
>
  {generatePlan.isPending ? (
    <>
      <Spinner /> Generating...
    </>
  ) : (
    'Generate Meal Plan'
  )}
</button>
```

## Cache Management

### Invalidate Queries

```typescript
import { useQueryClient } from '@tanstack/react-query';
import { recipeKeys, mealPlanKeys } from '@/hooks';

const queryClient = useQueryClient();

// Invalidate all recipe queries
queryClient.invalidateQueries({ queryKey: recipeKeys.all });

// Invalidate specific recipe list
queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });

// Invalidate meal plans
queryClient.invalidateQueries({ queryKey: mealPlanKeys.all });
```

### Prefetch Data

```typescript
import { useQueryClient } from '@tanstack/react-query';
import { recipeKeys } from '@/hooks';
import { getRecipeById } from '@/api';

const queryClient = useQueryClient();

// Prefetch on hover
const handleHover = (recipeId: number) => {
  queryClient.prefetchQuery({
    queryKey: recipeKeys.detail(recipeId),
    queryFn: () => getRecipeById(recipeId),
  });
};
```

### Optimistic Updates

```typescript
import { useQueryClient } from '@tanstack/react-query';
import { useDeleteMealPlan, mealPlanKeys } from '@/hooks';

const queryClient = useQueryClient();
const deletePlan = useDeleteMealPlan();

const handleDelete = async (id: number) => {
  // Optimistically update cache
  queryClient.setQueryData<MealPlanResponse[]>(
    mealPlanKeys.list(),
    (old) => old?.filter(plan => plan.id !== id) || []
  );

  try {
    await deletePlan.mutateAsync(id);
  } catch (error) {
    // Revert on error
    queryClient.invalidateQueries({ queryKey: mealPlanKeys.list() });
    toast.error('Failed to delete meal plan');
  }
};
```

## Type Usage

### Type Imports

```typescript
import type {
  Recipe,
  RecipeListItem,
  RecipeFilters,
  MealPlanGenerateRequest,
  MealPlanResponse,
  ShoppingListResponse,
  Nutrition,
  DietaryTag,
  Category,
} from '@/types';

import { DifficultyLevel, MealType, SortOrder } from '@/types';
```

### Type Guards

```typescript
import { isAPIError } from '@/api/client';

function handleError(error: unknown) {
  if (isAPIError(error)) {
    // TypeScript knows error is APIError
    console.log(error.message);
    console.log(error.status);
    console.log(error.errors);
  }
}
```

### Generic Types

```typescript
import type { PaginatedResponse } from '@/types';

// Custom hook with typed response
function useCustomRecipes(): PaginatedResponse<RecipeListItem> | undefined {
  const { data } = useRecipes();
  return data;
}
```

## Environment Setup

### .env File

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### TypeScript Config (tsconfig.json)

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Vite Config (vite.config.ts)

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

## Common Patterns

### Recipe List Page

```typescript
function RecipesPage() {
  const [filters, setFilters] = useState<RecipeFilters>({});
  const { data, isLoading } = useRecipes(filters);

  return (
    <div>
      <RecipeFilters filters={filters} onChange={setFilters} />
      {isLoading ? (
        <RecipeListSkeleton />
      ) : (
        <RecipeList recipes={data?.items || []} />
      )}
      <Pagination
        page={data?.page || 1}
        totalPages={data?.total_pages || 0}
        onChange={(page) => setFilters({ ...filters, page })}
      />
    </div>
  );
}
```

### Meal Plan Wizard

```typescript
function MealPlanWizard() {
  const [options, setOptions] = useState<MealPlanGenerateRequest>({
    days: 7,
    meal_preferences: {
      include_breakfast: true,
      include_lunch: true,
      include_dinner: true,
      include_snacks: false,
    },
    avoid_duplicate_recipes: true,
    max_recipe_reuse: 1,
    variety_score_weight: 0.3,
    optimize_shopping_list: true,
  });

  const generatePlan = useGenerateMealPlan();

  const handleSubmit = async () => {
    const plan = await generatePlan.mutateAsync(options);
    navigate(`/meal-plans/${plan.id}`);
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      {/* Form fields to update options */}
      <button type="submit" disabled={generatePlan.isPending}>
        Generate Plan
      </button>
    </form>
  );
}
```

## File Paths Reference

- Types: `/home/user/meal-planner/frontend/src/types/`
- API: `/home/user/meal-planner/frontend/src/api/`
- Hooks: `/home/user/meal-planner/frontend/src/hooks/`
- Documentation: `/home/user/meal-planner/frontend/API_DOCUMENTATION.md`
