# Recipe Components

Type-safe, production-ready React components for displaying and interacting with recipes.

## Components

### NutritionBadge
Small inline badge showing nutrition values with automatic color coding.

```tsx
import { NutritionBadge } from './components/recipes';

<NutritionBadge type="calories" value={450} />
<NutritionBadge type="protein" value={32} showIcon />
```

### IngredientList
Interactive ingredient list with checkboxes, preparation notes, and serving scaling.

```tsx
import { IngredientList } from './components/recipes';

<IngredientList
  ingredients={recipe.ingredients}
  servingsMultiplier={2}
  showCheckboxes
  onIngredientToggle={(name, checked) => console.log(name, checked)}
/>
```

### InstructionSteps
Numbered cooking steps with completion tracking and time estimates.

```tsx
import { InstructionSteps } from './components/recipes';

<InstructionSteps
  instructions={recipe.instructions}
  showCheckboxes
  expandable
  onStepToggle={(stepNumber, completed) => console.log(stepNumber, completed)}
/>
```

### RecipeCard
Compact recipe card for grid/list views with hover effects.

```tsx
import { RecipeCard } from './components/recipes';

<RecipeCard
  recipe={recipe}
  onAddToMealPlan={(recipe) => handleAddToMealPlan(recipe)}
  showNutrition
  showCategories
/>
```

### RecipeList
Responsive grid layout with loading states and empty state handling.

```tsx
import { RecipeList } from './components/recipes';

<RecipeList
  recipes={recipes}
  loading={isLoading}
  error={error}
  onAddToMealPlan={handleAddToMealPlan}
  columns={{ sm: 1, md: 2, lg: 3, xl: 4 }}
/>
```

### RecipeFilters
Comprehensive filtering UI with categories, dietary tags, allergens, and nutrition ranges.

```tsx
import { RecipeFilters } from './components/recipes';

<RecipeFilters
  filters={currentFilters}
  onFiltersChange={setFilters}
  categories={categories}
  dietaryTags={dietaryTags}
  allergens={allergens}
  showApplyButton
  onApply={() => refetch()}
/>
```

### RecipeDetail
Full recipe view with all details, actions, and interactive elements.

```tsx
import { RecipeDetail } from './components/recipes';

<RecipeDetail
  recipe={recipe}
  onAddToMealPlan={handleAddToMealPlan}
  onPrint={() => window.print()}
  onShare={handleShare}
/>
```

## Pages

### RecipeBrowserPage
Complete recipe browsing experience with search, filters, and infinite scroll.

```tsx
import { RecipeBrowserPage } from './pages';

<RecipeBrowserPage
  onAddToMealPlan={handleAddToMealPlan}
/>
```

### RecipeDetailPage
Recipe detail page with routing, breadcrumbs, and loading/error states.

```tsx
import { RecipeDetailPage } from './pages';

<RecipeDetailPage
  onAddToMealPlan={handleAddToMealPlan}
/>
```

## Features

- **Type-safe**: Full TypeScript support with exported types
- **Responsive**: Mobile-first design with Tailwind breakpoints
- **Accessible**: ARIA labels, keyboard navigation, semantic HTML
- **Interactive**: Checkboxes, serving adjusters, collapsible sections
- **Performant**: React Query caching, lazy loading, skeleton states
- **Print-friendly**: Optimized print styles for recipes

## Usage Example

```tsx
import { RecipeBrowserPage, RecipeDetailPage } from './pages';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  const handleAddToMealPlan = (recipe) => {
    console.log('Adding to meal plan:', recipe);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/recipes"
          element={<RecipeBrowserPage onAddToMealPlan={handleAddToMealPlan} />}
        />
        <Route
          path="/recipes/:slug"
          element={<RecipeDetailPage onAddToMealPlan={handleAddToMealPlan} />}
        />
      </Routes>
    </BrowserRouter>
  );
}
```

## Dependencies

- React 18+
- React Router v6
- React Query (@tanstack/react-query)
- Tailwind CSS
- Heroicons
- Common components from `/components/common`

## File Structure

```
components/recipes/
├── NutritionBadge.tsx       # Nutrition value badge
├── IngredientList.tsx       # Ingredient list with checkboxes
├── InstructionSteps.tsx     # Cooking steps with tracking
├── RecipeCard.tsx           # Recipe card for grids
├── RecipeList.tsx           # Recipe grid layout
├── RecipeFilters.tsx        # Filter panel
├── RecipeDetail.tsx         # Full recipe view
└── index.ts                 # Export all components

pages/
├── RecipeBrowserPage.tsx    # Browse recipes page
├── RecipeDetailPage.tsx     # Recipe detail page
└── index.ts                 # Export all pages
```

## Type Exports

All component props are exported for testing and documentation:

```tsx
import type {
  NutritionBadgeProps,
  IngredientListProps,
  InstructionStepsProps,
  RecipeCardProps,
  RecipeListProps,
  RecipeFiltersProps,
  RecipeDetailProps,
  RecipeBrowserPageProps,
  RecipeDetailPageProps,
} from './components/recipes';
```
