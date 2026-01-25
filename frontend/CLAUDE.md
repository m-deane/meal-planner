# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Meal Planner Frontend** - React + TypeScript + Vite application for meal planning with the Gousto Recipe Database. Features recipe browsing, drag-and-drop meal planning, nutrition tracking, shopping list generation, and favorites management.

**Backend API**: Runs on `http://localhost:8000` (FastAPI)

## Common Commands

```bash
# Development
npm run dev              # Start dev server (http://localhost:3000)
npm run build            # Build for production (runs tsc first)
npm run preview          # Preview production build

# Testing
npm run test             # Run tests
npm run test -- --watch  # Watch mode
npm run test:ui          # Tests with UI
npm run test:coverage    # Coverage report

# Code Quality
npm run lint             # ESLint
npm run type-check       # TypeScript check (tsc --noEmit)
```

## Architecture

### Data Flow Pattern

```
Pages → Hooks (useRecipes, useMealPlan) → API functions → Backend
         ↓
      TanStack Query (server state cache)
         ↓
      Zustand Stores (client state: mealPlan, shortlist, auth)
         ↓
      Components
```

### Key Architectural Patterns

**TanStack Query for Server State**: All API data uses React Query hooks with query keys pattern:
```typescript
// src/hooks/useRecipes.ts
export const recipeKeys = {
  all: ['recipes'] as const,
  lists: () => [...recipeKeys.all, 'list'] as const,
  list: (filters?, sort?) => [...recipeKeys.lists(), { filters, sort }] as const,
  detail: (id: number) => [...recipeKeys.details(), id] as const,
};
```

**Zustand for Client State**: Stores in `src/store/`:
- `mealPlanStore.ts` - Current meal plan being built (days, slots, recipes)
- `shortlistStore.ts` - Saved recipes for later (persists to localStorage)
- `shoppingListStore.ts` - Shopping list state
- `authStore.ts` - Authentication state
- `nutritionGoalsStore.ts` - User's nutrition targets

**API Layer Pattern**: `src/api/` exports functions by domain:
```typescript
// src/api/index.ts re-exports all
import { getRecipes, getRecipeBySlug } from './recipes';
import { generateMealPlan, saveMealPlan } from './mealPlans';
```

### Component Organization

Components are grouped by feature with barrel exports:
```
src/components/
├── common/          # Button, Card, Badge, Modal, Spinner, etc.
├── meal-planner/    # MealPlannerBoard, DayColumn, MealSlot, DraggableRecipe
├── recipes/         # RecipeCard, RecipeFilters, RecipeList, ShortlistButton
├── nutrition/       # Charts and nutrition displays
├── shopping-list/   # Shopping list components
├── planner/         # Multi-week planning (CostEstimate, VarietyIndicator)
├── favorites/       # FavoriteButton, FavoritesList
└── layout/          # Layout, Navigation
```

Each feature folder has an `index.ts` barrel file exporting components and types.

### Drag and Drop

Uses `@dnd-kit/core` for meal planning. Key concepts:
- `DraggableRecipe` - Wraps recipes with drag functionality
- `MealSlot` - Drop zones for each meal (breakfast/lunch/dinner per day)
- `parseDragId` / `parseDropId` - Parse IDs to identify source/target

### Routing

React Router v6 routes defined in `src/App.tsx`:
- `/dashboard` - Main dashboard
- `/recipes` - Recipe browser with filters
- `/recipes/:slug` - Recipe detail
- `/meal-planner` - Drag-and-drop meal planning
- `/nutrition` - Nutrition dashboard
- `/shopping-list` - Shopping list management
- `/favorites` - Saved favorites

### TypeScript Configuration

Strict mode with additional checks enabled:
- `noUncheckedIndexedAccess: true` - Array access may be undefined
- `exactOptionalPropertyTypes: true` - Optional props can't be `undefined`
- `noPropertyAccessFromIndexSignature: true` - Forces bracket notation for dynamic keys

Path aliases configured: `@/`, `@components/`, `@hooks/`, `@api/`, `@store/`, `@types/`, `@utils/`

## Testing

Tests use Vitest + Testing Library. Tests live alongside components in `__tests__/` folders:
```
src/components/common/__tests__/Button.test.tsx
src/store/__tests__/mealPlanStore.test.ts
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Meal Planner
VITE_APP_VERSION=1.0.0
```
