# Frontend Code Quality Report

**Date**: 2026-02-19
**Scope**: `/frontend/src/` - State management, API layer, components, styling
**Reviewer**: Claude Code (claude-sonnet-4-6)

---

## Summary

The frontend is well-structured with a clean separation between server state (TanStack Query) and client state (Zustand). The API layer is consistently typed and the query key factory pattern is applied correctly across all domains. Several meaningful issues exist that warrant attention, particularly a React rules violation in `useCurrentUser`, duplicated favorites functionality across two hook files, heavy use of `any` casts in `MealPlannerPage`, and widespread use of browser-native `alert`/`confirm`/`prompt` dialogs.

---

## Critical Issues (Must Fix)

### 1. Side Effect Executed During Render in `useCurrentUser`

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useAuth.ts` — lines 120–128

**Problem**: `setUser` and `clearAuth` are called unconditionally inside the hook body during render. This violates the React rules for side effects — state mutations triggered during render cause double invocations in Strict Mode, can create infinite re-render loops, and produce unpredictable behaviour when the hook is called from multiple components.

```typescript
// CURRENT — Illegal side effect in render body
const query = useQuery({ ... });

if (query.data && query.isSuccess) {
  setUser(query.data);   // state mutation during render
}

if (query.isError) {
  clearAuth();           // state mutation during render
}
```

**Fix**: Move these side effects into a `useEffect` with proper dependencies.

```typescript
const query = useQuery({ ... });

useEffect(() => {
  if (query.data && query.isSuccess) {
    setUser(query.data);
  }
}, [query.data, query.isSuccess, setUser]);

useEffect(() => {
  if (query.isError) {
    clearAuth();
  }
}, [query.isError, clearAuth]);
```

The same pattern applies to `useVerifyToken` at lines 188–192 of the same file.

---

### 2. Duplicated Favorites Domain — Two Conflicting Implementations

**Files**:
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useFavorites.ts`
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useUser.ts` (lines 126–241)
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/api/favorites.ts`
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/api/users.ts` (lines 60–103)

**Problem**: Favorites functionality is implemented twice with diverging query keys, different API endpoints, and different return types for the same conceptual operation.

| Aspect | `useFavorites.ts` / `api/favorites.ts` | `useUser.ts` / `api/users.ts` |
|---|---|---|
| List query key | `['favorites', 'list', ...]` | `['user', 'favorites', ...]` |
| List API endpoint | `GET /favorites` | `GET /users/favorites` |
| Check endpoint | `GET /favorites/check/:id` | `GET /users/favorites/:id/check` |
| `addFavorite` return type | `FavoriteRecipe` | `void` |
| `toggleFavorite` signature | `(recipeId, notes?)` async | `(recipeId)` sync |

This means invalidating one set of queries never affects the other. Adding a favorite via `useFavorites` will not update UI components consuming `useUser.useFavorites`, and vice versa. It also means cache for the same data is stored under two different keys, wasting memory.

**Fix**: Choose one implementation and delete the other. The `useFavorites.ts` / `api/favorites.ts` pair is more complete (it includes `FavoritesSortBy`, `updateFavorite`, and `getFavoriteIds`). Remove the favorites-related functions from `useUser.ts` and `api/users.ts`, and update all consumers to use the canonical hooks.

---

### 3. Pervasive `any` Casts in `MealPlannerPage` — Type Safety Completely Bypassed

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/pages/MealPlannerPage.tsx`

Lines 157, 171, 179, 231, 233, 247 all cast to `any`. The root cause is that `MealPlanResponse` (from `../types/mealPlan.ts`) does not model the actual API response shape — the runtime response has `plan.Monday.meals.breakfast` but the type does not capture this structure.

```typescript
// Lines 157, 171, 179 — accessing untyped API response
const planData = (result as any).plan;
const mealCounts = (request as any).mealCounts;
Object.entries(planData).forEach(([dayName, dayData]: [string, any]) => {
```

```typescript
// Lines 231, 233 — suppressing type errors on function calls
addRecipe(dayOfWeek as any, mealType, recipe as any, mealData.servings || 2);
```

**Fix**: Define proper types for the API response shape and the extended request type. The `ExtendedMealPlanRequest` type already exists in `api/mealPlans.ts` but is not exported to the page. The API response structure should be typed in `types/mealPlan.ts`.

```typescript
// Add to types/mealPlan.ts
interface GeneratedMealData {
  id: number;
  slug: string;
  name: string;
  cooking_time_minutes: number | null;
  difficulty: DifficultyLevel | null;
  servings: number;
  image_url: string | null;
  nutrition?: Partial<Nutrition>;
}

interface GeneratedDayPlan {
  meals: {
    breakfast?: GeneratedMealData;
    lunch?: GeneratedMealData;
    dinner?: GeneratedMealData;
  };
}

interface GeneratedMealPlanResponse extends MealPlanResponse {
  plan: Record<string, GeneratedDayPlan>;
}
```

---

## Warnings (Should Fix)

### 4. `localStorage` Directly Accessed in `authStore` Alongside `persist` Middleware

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/authStore.ts` — lines 49–53, 68, 77–78, 81–82

**Problem**: The store uses `zustand/middleware/persist` to sync to `localStorage`, but also manually calls `localStorage.setItem` and `localStorage.removeItem` directly inside `setToken`, `setAuth`, `logout`, and `clearAuth`. The `persist` middleware already handles serialisation and writes. The manual calls create two competing sources of truth and cause double-writes on every auth action. Additionally, `api/auth.ts` (lines 30–32, 87–89) and `api/client.ts` (line 27, 84) also directly read and write `auth_token` from `localStorage`, meaning four separate code paths touch the same key with no single point of control.

**Fix**: Remove the manual `localStorage` calls from the store. Let `persist` handle the write. The Axios interceptor should read from the Zustand store state rather than `localStorage` directly.

```typescript
// api/client.ts — read from store, not localStorage
import { useAuthStore } from '../store/authStore';

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

### 5. `handleDragEnd` Logic Duplicated Between `MealPlannerPage` and `MealPlannerBoard`

**Files**:
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/pages/MealPlannerPage.tsx` — lines 97–142
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/MealPlannerBoard.tsx` — lines 131–186

The DnD logic (`handleDragStart`, `handleDragEnd`, `handleDragCancel`, sensor configuration, `DragData` interface, and the ternary for swap vs. move at lines 173–185 in both files) is copy-pasted identically into both files. A bug fix or behaviour change must be applied in two places.

The inline ternary to determine the target meal key is also duplicated:
```typescript
// Both files, same lines
const targetMealKey = target.mealType === 'breakfast' ? 'breakfast'
  : target.mealType === 'lunch' ? 'lunch' : 'dinner';
```
This bypasses `getMealTypeKey` which already exists in the store and handles the mapping correctly.

**Fix**: Extract the DnD logic into a custom hook `useMealPlannerDnd` that returns `sensors`, `activeId`, `activeDragData`, `handleDragStart`, `handleDragEnd`, and `handleDragCancel`. Consume it from both `MealPlannerPage` and `MealPlannerBoard`. Replace the inline ternary with a call to `getMealTypeKey` (make it exported from `mealPlanStore.ts`).

---

### 6. `shoppingListStore` and `shortlistStore` Use Nested State Pattern Anti-Pattern

**Files**:
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/shoppingListStore.ts`
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/shortlistStore.ts`

**Problem**: Both stores wrap their actual state in a nested `state` object (e.g., `state.state.items`, `state.state.recipes`). This conflicts with the Zustand store's own root-level properties and makes the `partialize` serialisation for `persist` unnecessarily complex. By contrast, `authStore` and `nutritionGoalsStore` correctly place fields at the top level.

Selectors in `ShortlistPanel` directly access `state.recipes` (line 65) while `ShortlistStore` exposes `state.state.recipes` — the component works only because it destructures `state` from the store, which aliases to the nested object.

**Fix**: Flatten the state to the top level, consistent with `authStore` and `mealPlanStore`.

```typescript
// Before
export const useShoppingListStore = create<ShoppingListStore>()(persist(
  (set, get) => ({
    state: { items: [], sortBy: 'category', showChecked: true },
    addItem: (item) => set((s) => ({ state: { ...s.state, items: [...s.state.items, item] } })),
    ...

// After
export const useShoppingListStore = create<ShoppingListStore>()(persist(
  (set, get) => ({
    items: [],
    sortBy: 'category' as const,
    showChecked: true,
    addItem: (item) => set((s) => ({ items: [...s.items, item] })),
    ...
```

---

### 7. `MealPlannerPage` Contains Unfinished "Save" Feature With Hardcoded `alert`

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/pages/MealPlannerPage.tsx` — lines 259–271

```typescript
const handleSavePlan = async () => {
  if (totalRecipes === 0) {
    alert('Add some recipes to your meal plan first!');
    return;
  }
  try {
    // Show a placeholder message
    alert('Save functionality requires backend integration. Plan is saved locally via localStorage.');
  } catch (error) {
    ...
  }
};
```

`useSaveMealPlan` is imported and instantiated (`saveMutation`) but never called. The "Save Plan" button is wired to this placeholder handler. This is a shipped stub that misleads users.

**Fix**: Either complete the integration using `saveMutation.mutateAsync(...)` or remove the button until the feature is ready. The `saveMutation` import can be dropped if the button is removed.

---

### 8. Widespread Use of Browser-Native Dialogs (`alert`, `confirm`, `prompt`)

**Files and lines**:
- `MealPlannerPage.tsx` lines 255, 261, 267, 270, 277, 303 — `alert`, `confirm`, `prompt`
- `MealPlanDetailPage.tsx` lines 41, 47, 70 — `confirm`, `alert`
- `ShoppingListPage.tsx` lines 25, 31 — `confirm`
- `DayColumn.tsx` line 67 — `confirm`
- `FavoritesList.tsx` line 35 — `confirm`
- `RecipeDetailPage.tsx` line 66 — `alert`

Native dialogs block the browser's main thread, cannot be styled, are inaccessible to screen readers, and are disabled in some embedded browser contexts. The project already has a `Modal` component in `components/common/Modal.tsx`.

**Fix**: Replace `confirm` dialogs with a reusable `ConfirmDialog` component using the existing `Modal`. Replace `alert` calls with toast notifications (a lightweight `react-hot-toast` or similar). Replace the `prompt` for date input in `MealPlannerPage` with the existing date input pattern already used in `GeneratePlanModal`.

---

### 9. `useToggleFavorite` in `useFavorites.ts` Reads Query Cache Without Guaranteeing Freshness

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useFavorites.ts` — lines 154–167

```typescript
const toggleFavorite = async (recipeId: number, notes?: string): Promise<void> => {
  const isFavorite = queryClient.getQueryData<boolean>(favoriteKeys.check(recipeId));
  // isFavorite will be undefined if the check query has never been fetched
  if (isFavorite) {
    await removeMutation.mutateAsync(recipeId);
  } else {
    await addMutation.mutateAsync(request);
  }
};
```

If `favoriteKeys.check(recipeId)` has not been loaded yet (e.g., the recipe card was never rendered), `getQueryData` returns `undefined`, which is falsy. The toggle will always call `addFavorite` on a recipe that was never fetched, potentially creating duplicates.

**Fix**: Use `queryClient.ensureQueryData` or fall back to checking the `favoriteIds` list query.

```typescript
const toggleFavorite = async (recipeId: number, notes?: string): Promise<void> => {
  // Check ids list (likely already cached) before the per-recipe check
  const ids = queryClient.getQueryData<number[]>(favoriteKeys.ids()) ?? [];
  const isFavorite = ids.includes(recipeId)
    ?? queryClient.getQueryData<boolean>(favoriteKeys.check(recipeId))
    ?? false;
  ...
};
```

---

### 10. `NutritionDashboard` Has a Stale `useMemo` Dependency

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/nutrition/NutritionDashboard.tsx` — lines 62–73

```typescript
const weeklyTrendsData = useMemo(() => {
  return DAYS_OF_WEEK.map((day) => {
    const nutrition = getDayNutrition(day);
    ...
  });
}, [getDayNutrition]); // Missing: plan.days as a dependency
```

`getDayNutrition` is a function defined inside the Zustand store via `get()`. The function reference itself is stable (it does not change between renders), so `useMemo` will not recompute when the plan changes — only `plan.days` changing triggers a re-render, but the memo dependency does not include it. The weekly trends chart will display stale data.

**Fix**: Add `plan.days` to the dependency array.

```typescript
const weeklyTrendsData = useMemo(() => {
  return DAYS_OF_WEEK.map((day) => {
    const nutrition = getDayNutrition(day);
    ...
  });
}, [getDayNutrition, plan.days]);
```

---

### 11. `isAuthenticated` is a Derived Value Stored as State, Vulnerable to Desync

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/authStore.ts` — lines 13–17, 48–65

`isAuthenticated` is stored as a boolean in state but is always just `!!token && !!user`. When `persist` rehydrates from `localStorage`, it only restores `token` and `user` (per the `partialize` config at line 89–93), but `isAuthenticated` starts as `false` from `initialState`. There is no rehydration step that recomputes it, so immediately after page load `isAuthenticated` will be `false` even though `token` and `user` are populated in storage.

**Fix**: Replace with a computed selector and remove `isAuthenticated` from stored state.

```typescript
// Remove isAuthenticated from AuthState
// Remove setToken, setUser isAuthenticated updates

// Add a selector
export const selectIsAuthenticated = (state: AuthStore): boolean =>
  !!state.token && !!state.user;

// Usage in components
const isAuthenticated = useAuthStore(selectIsAuthenticated);
```

---

## Suggestions (Consider Improving)

### 12. Missing `React.memo` on High-Render-Frequency Components

**Files**:
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/DraggableRecipe.tsx`
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/MealSlot.tsx`
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/DayColumn.tsx`

During drag operations, the DnD library triggers frequent re-renders of the entire tree. `DraggableRecipe`, `MealSlot`, and `DayColumn` are rendered 21 times (7 days × 3 slots) on every drag move event. None are wrapped in `React.memo`, so all 21 instances re-render even when their props haven't changed.

Similarly, callbacks defined inline in `DayColumn` (lines 106–124) are re-created on every render:
```typescript
onRemove={() => removeRecipe(day, MealType.BREAKFAST)}
onUpdateServings={(servings) => updateServings(day, MealType.BREAKFAST, servings)}
```
These should be wrapped in `useCallback`.

**Recommended fix**:
```typescript
export const DraggableRecipe = React.memo<DraggableRecipeProps>(({ ... }) => {
  ...
});

export const MealSlot = React.memo<MealSlotProps>(({ ... }) => {
  ...
});

// In DayColumn
const handleRemoveBreakfast = useCallback(() => removeRecipe(day, MealType.BREAKFAST), [day, removeRecipe]);
```

---

### 13. `PlannerSidebar` Renders `recipe: any` Instead of `RecipeListItem`

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/PlannerSidebar.tsx` — line 254

```typescript
{recipes.map((recipe: any) => (
```

`recipes` is typed as `RecipeListItem[]` via the `infiniteQuery` (the flatMap return type is correctly `RecipeListItem[]`). The `any` annotation is unnecessary and silences type checking on the `recipe` being passed to `DraggableRecipe`. Remove it.

```typescript
{recipes.map((recipe) => (
```

---

### 14. Recharts `CustomTooltip` and Render Functions Use `any` Instead of Recharts Types

**Files**:
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/nutrition/WeeklyTrends.tsx` — lines 77, 83
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/nutrition/DailyBreakdown.tsx` — lines 54, 57, 62, 86
- `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/nutrition/MacroChart.tsx` — lines 78, 95, 152

Recharts exports `TooltipProps`, `LegendProps`, and typed payload types. Use them instead of `any`.

```typescript
import type { TooltipProps } from 'recharts';
import type { ValueType, NameType } from 'recharts/types/component/DefaultTooltipContent';

const CustomTooltip = ({ active, payload, label }: TooltipProps<ValueType, NameType>) => {
  ...
};
```

---

### 15. `RecipeBrowserPage` Uses `difficulty as any[]` for URL Parameter Parsing

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/pages/RecipeBrowserPage.tsx` — line 62

```typescript
filters.difficulty = difficulty as any[];
```

`difficulty` from URL params is `string[]`. `DifficultyLevel` is a string enum. A type guard can replace the cast safely.

```typescript
import { DifficultyLevel } from '../types';

const isDifficultyLevel = (v: string): v is DifficultyLevel =>
  Object.values(DifficultyLevel).includes(v as DifficultyLevel);

filters.difficulty = difficulty.filter(isDifficultyLevel);
```

---

### 16. `mealPlanKeys` Has Redundant `list()` and `lists()` Methods

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useMealPlan.ts` — lines 27–33

```typescript
export const mealPlanKeys = {
  all: ['mealPlans'] as const,
  lists: () => [...mealPlanKeys.all, 'list'] as const,
  list: () => [...mealPlanKeys.lists()] as const,  // identical to lists()
  ...
};
```

`list()` is a wrapper around `lists()` that returns the same value. The same pattern exists in `shoppingListKeys`. This makes invalidation confusing — some mutations call `lists()` and some call `list()`. Consolidate to one.

---

### 17. `generateId` in `shoppingListStore` Uses `Date.now()` Collision Risk

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/shoppingListStore.ts` — lines 61–63

```typescript
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
};
```

While unlikely, two items added in the same millisecond could collide. The `crypto.randomUUID()` API is available in all modern browsers and produces a guaranteed-unique UUID.

```typescript
const generateId = (): string => crypto.randomUUID();
```

---

### 18. `snack` Meal Type Silently Maps to `dinner` in `mealPlanStore`

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/mealPlanStore.ts` — lines 119–127

```typescript
const getMealTypeKey = (mealType: MealType): keyof DayState => {
  const mealTypeMap: Record<MealType, keyof DayState> = {
    breakfast: 'breakfast',
    lunch: 'lunch',
    dinner: 'dinner',
    snack: 'dinner', // Map snack to dinner as fallback
  };
  return mealTypeMap[mealType];
};
```

Mapping `snack` to `dinner` means any snack-typed recipe silently overwrites the dinner slot without any warning. The `MealType` enum includes `snack` but `DayState` does not have a snack slot. Either add a `snack` slot to `DayState`, or remove `snack` from the `MealType` enum (or guard against it at call sites). The current silent fallback is a data-integrity risk.

---

### 19. Tailwind Class String Fragmentation Reduces Readability

Multiple components concatenate conditional Tailwind strings with template literals in ways that cannot be statically analysed (Tailwind's JIT compiler may not detect all classes):

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/components/meal-planner/MealSlot.tsx` — lines 73–83

```typescript
className={`
  relative min-h-[100px] rounded-lg border-2 transition-all duration-200
  ${isEmpty ? 'border-dashed' : 'border-solid'}
  ${
    isDraggingOver
      ? 'border-indigo-500 bg-indigo-50 shadow-lg scale-105'
      : isEmpty
      ? 'border-gray-300 bg-gray-50'
      : 'border-gray-200 bg-white'
  }
`}
```

**Recommendation**: Use the `clsx` or `tailwind-merge` library (already a common pairing with Tailwind) for conditional class composition. This enables static analysis by Tailwind tooling and removes whitespace artefacts.

```typescript
import { clsx } from 'clsx';

className={clsx(
  'relative min-h-[100px] rounded-lg border-2 transition-all duration-200',
  isEmpty ? 'border-dashed' : 'border-solid',
  isDraggingOver ? 'border-indigo-500 bg-indigo-50 shadow-lg scale-105'
    : isEmpty ? 'border-gray-300 bg-gray-50'
    : 'border-gray-200 bg-white'
)}
```

---

### 20. `useInfiniteRecipes` and `useRecipes` Share the Same Query Key

**File**: `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/hooks/useRecipes.ts` — lines 53–58, 70

Both `useRecipes` (regular paginated) and `useInfiniteRecipes` (infinite scroll) use `recipeKeys.list(filters, sort)` as the query key. This means they would collide in the cache if both are mounted with the same filters — data from a `useInfiniteQuery` stored under a key will be returned to a `useQuery` using the same key (and vice versa), with incorrect type shape. Currently both are used in different pages, so the collision has not manifested, but it's fragile.

**Fix**: Differentiate the keys:
```typescript
infiniteList: (filters?: RecipeFilters, sort?: SortParams) =>
  [...recipeKeys.lists(), 'infinite', { filters, sort }] as const,
```

---

## Test Coverage Observations

The store tests in `/Users/matthewdeane/Documents/Data Science/python/_projects/_p-meal-planner/frontend/src/store/__tests__/mealPlanStore.test.ts` are thorough and cover all store actions correctly.

**Gaps to address**:

1. No tests for `useCurrentUser` side effects (the render-phase mutation bug in issue #1 would be caught by a test asserting no double-calls in Strict Mode).
2. No tests for the `PlannerSidebar`, `MealPlannerBoard`, or `MealPlannerPage` — the most complex components have zero test coverage.
3. No tests exist for `shoppingListStore` or `shortlistStore`.
4. `useToggleFavorite` (from `useFavorites.ts`) lacks a test for the undefined cache case described in issue #9.

---

## Issue Index

| # | Severity | Category | File |
|---|---|---|---|
| 1 | Critical | React rules violation | `hooks/useAuth.ts:120-128` |
| 2 | Critical | Code duplication / data inconsistency | `hooks/useFavorites.ts`, `hooks/useUser.ts` |
| 3 | Critical | TypeScript safety | `pages/MealPlannerPage.tsx:157-247` |
| 4 | High | State management | `store/authStore.ts`, `api/auth.ts`, `api/client.ts` |
| 5 | High | Code duplication | `pages/MealPlannerPage.tsx`, `components/meal-planner/MealPlannerBoard.tsx` |
| 6 | High | State management | `store/shoppingListStore.ts`, `store/shortlistStore.ts` |
| 7 | High | Unfinished feature shipped | `pages/MealPlannerPage.tsx:259-271` |
| 8 | High | UX / accessibility | Multiple pages and components |
| 9 | High | Logic bug | `hooks/useFavorites.ts:154-167` |
| 10 | High | Stale memo | `components/nutrition/NutritionDashboard.tsx:62-73` |
| 11 | High | State management | `store/authStore.ts:13-17` |
| 12 | Medium | Performance | `meal-planner/DraggableRecipe.tsx`, `MealSlot.tsx`, `DayColumn.tsx` |
| 13 | Medium | TypeScript safety | `components/meal-planner/PlannerSidebar.tsx:254` |
| 14 | Medium | TypeScript safety | `components/nutrition/WeeklyTrends.tsx`, `DailyBreakdown.tsx`, `MacroChart.tsx` |
| 15 | Medium | TypeScript safety | `pages/RecipeBrowserPage.tsx:62` |
| 16 | Low | Code clarity | `hooks/useMealPlan.ts`, `hooks/useShoppingList.ts` |
| 17 | Low | Correctness | `store/shoppingListStore.ts:61-63` |
| 18 | Low | Data integrity | `store/mealPlanStore.ts:119-127` |
| 19 | Low | Maintainability | `meal-planner/MealSlot.tsx` and others |
| 20 | Low | Cache correctness | `hooks/useRecipes.ts:53-70` |
