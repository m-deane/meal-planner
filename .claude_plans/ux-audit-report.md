# UX/UI Audit Report: Gousto Meal Planner Frontend

**Audit Date**: 2026-02-19
**Scope**: All pages and key components in `/frontend/src/`
**Priority focus**: MealPlannerPage layout cramping and recipe library sidebar

---

## Executive Summary

The frontend has a solid foundation with good component decomposition, consistent Tailwind patterns, and strong coverage of loading/empty states. The core problem is the Meal Planner page, which attempts to force a 7-column weekly board into a fixed viewport alongside a 384px sidebar, leaving each day column approximately 120–140px wide. This makes recipe names unreadable and interaction targets too small. Several secondary issues exist across other pages: blocking UX patterns (browser `alert`/`confirm` dialogs), missing accessibility attributes, and underused design system components.

---

## Section 1: Meal Planner Page — Primary Issue

### 1.1 Root Cause of Cramped 7-Column Layout

**File**: `frontend/src/components/meal-planner/MealPlannerBoard.tsx`, line 96

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
```

This is the single class causing the reported cramping. At the `xl` breakpoint (1280px+), all seven day columns are forced into one row. The parent chain is:

```
MealPlannerPage (h-screen flex flex-col)
  └── flex-1 flex overflow-hidden
        ├── flex-1 overflow-auto p-6        ← board area
        │     └── BoardContent
        │           └── grid xl:grid-cols-7  ← THE PROBLEM
        └── w-96 bg-white border-l          ← sidebar (384px fixed)
```

At 1440px viewport width the sidebar consumes 384px, leaving approximately 1056px for the board minus 24px padding on each side (p-6 = 48px total). That gives roughly 1008px divided among 7 columns with gap-4 (16px × 6 = 96px of gap), leaving approximately **130px per column**. The column content — header, three meal slots, nutrition footer — is designed to function at a minimum of around 200px.

**Contributing factors in `MealPlannerPage.tsx`**:
- Line 383: `<div className="flex-1 overflow-auto p-6">` — adds 24px padding on each side, compressing usable board width
- Line 389–392: `${showSidebar ? 'w-96' : 'w-0'}` — the `w-96` (384px) sidebar is hardcoded with no intermediate sizes

**Contributing factors in `DayColumn.tsx`**:
- Line 73: `overflow-hidden` on the column root clips content instead of allowing wrapping
- Line 78: `<h3 className="font-bold text-lg">` — the day label ("Wednesday") is 9 characters and will overflow at 130px
- The daily nutrition grid at the bottom (4 cells) requires at minimum 180px to render legibly

**Contributing factors in `DraggableRecipe.tsx`**:
- Line 103–112: Recipe name uses `line-clamp-2` — this is correct, but at 130px column width the image thumbnail (`w-12 h-12`) plus the name container leaves the name with approximately 60–70px of available width, causing nearly all recipe names to show only one word before clamping

### 1.2 Sidebar Width and Filter Visibility

**File**: `frontend/src/components/meal-planner/PlannerSidebar.tsx`

The sidebar is 384px (`w-96`) which is adequate as a raw number, but the filter panel is collapsed by default (`showFilters` state initialises to `false`, line 44). This means filters are hidden behind an extra click every time the user opens the planner. The filter surface itself (cooking time number input and difficulty toggle buttons) is minimal compared to the full RecipeFilters panel available on the Recipe Browser page. Missing filter options in the sidebar compared to the browser:

- No category filter
- No dietary tag filter
- No allergen exclusion
- No nutrition range filters (calories, protein, carbs, fat)

Recipe cards in the sidebar are rendered with `compact={true}` (line 259 in `PlannerSidebar.tsx`), which hides the difficulty badge and nutrition badges. While the compact mode is correct for space efficiency, it does not provide enough information for a user to make a confident drag decision when they cannot see allergen info or calorie data.

### 1.3 Settings Modal Issues

**File**: `frontend/src/pages/MealPlannerPage.tsx`, lines 447–549

The settings (Nutrition Goals) modal uses a raw `div` with `fixed inset-0 z-50` instead of the existing `Modal` component from `components/common/Modal.tsx`. This means:
- No focus trap (keyboard users can tab behind the modal)
- No Escape key handler to close
- The close button uses `<ChevronRight />` instead of an `X` icon, which is semantically wrong and visually confusing
- No accessible `Dialog` role or `aria-modal` attribute

### 1.4 Blocking Dialog Patterns

**File**: `frontend/src/pages/MealPlannerPage.tsx`

- Line 256: `alert('Failed to generate meal plan...')` — synchronous browser alert blocks the UI
- Line 266: `alert('Save functionality requires backend integration...')` — exposes an implementation detail to the user with no actionable next step
- Line 277: `window.confirm('Are you sure you want to clear the entire meal plan?')` — native browser confirm dialogs cannot be styled and break the visual language

**File**: `frontend/src/components/meal-planner/DayColumn.tsx`, line 67:
- `window.confirm(...)` for clearing a single day — same problem

**File**: `frontend/src/pages/ShoppingListPage.tsx`, lines 25, 31:
- Two `window.confirm(...)` calls for clear actions

### 1.5 Missing Empty State on Board

When the meal plan is empty (zero recipes added), `BoardContent` renders 7 `DayColumn` components each showing 3 empty `MealSlot` components. There is no page-level guidance telling the user what to do. The empty slot text "Drag a recipe here" is helpful but only visible after the user has already oriented themselves. There is no call-to-action linking back to the Generate Plan feature when the board is in a completely empty state.

---

## Section 2: Proposed Meal Planner Redesign

### 2.1 Layout Architecture Options

Three options are evaluated in order of implementation effort and user impact.

**Option A — Horizontal Scroll with Wider Columns (Recommended)**

Replace `xl:grid-cols-7` with a horizontally scrollable row of fixed-width columns. Each column gets a guaranteed minimum width.

```
Design spec:
- Each DayColumn: min-width: 220px (currently ~130px)
- Board container: overflow-x-auto, display: flex, gap: 16px
- Sidebar: 340px (reduced from 384px), always visible, filters always expanded
- Sticky day headers: position: sticky, top: 0 within the scroll container
- Week navigation: left/right arrow buttons to jump 3 days for keyboard users
```

Benefits:
- Zero disruption to existing drag-and-drop implementation (DnD Kit handles scroll containers well)
- Day columns gain 69% more width (220px vs 130px)
- Recipe names can display 2 full lines at 220px
- Implementation is a targeted CSS change to `BoardContent.tsx` and `MealPlannerPage.tsx`

The key CSS change is in `BoardContent.tsx`:
```
// Current (problematic):
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">

// Proposed:
<div className="flex gap-4 min-w-0">
  // each DayColumn gets: className="flex-shrink-0 w-56" (224px)
```

**Option B — Paginated Day View (3-Day Viewport)**

Show 3 days at a time with Previous / Next navigation. Each column gets approximately 300px at 1440px viewport.

Benefits: Much more comfortable column width, allows richer slot cards (showing image thumbnail always)
Drawbacks: Breaks the "full week at a glance" mental model; user cannot see Monday vs Sunday simultaneously; increases cognitive load for planning across the week

**Option C — Single Day Focus with Week Strip**

A horizontal "week strip" at the top shows all 7 days as compact chips with meal-filled indicators. Clicking a day expands it into a single-column detail view.

Benefits: Maximum readability per day
Drawbacks: Highest implementation effort; fundamentally changes the drag-and-drop paradigm (cross-day dragging becomes navigation-dependent)

### 2.2 Recommended Sidebar Redesign

**Current sidebar structure**: 384px, filters hidden behind toggle, limited filter options

**Proposed sidebar structure**: 340px with a two-panel layout

```
Sidebar (340px, fixed height, overflow hidden)
  ├── Tab bar: [Library] [Shortlist]
  ├── Search input (always visible)
  ├── Filter row (always visible, collapsed to icon-pills)
  │     Filters: Difficulty (Easy / Medium / Hard toggle pills)
  │               Max time (quick buttons: 20m / 30m / 45m / Any)
  │               Dietary (dropdown or popover)
  ├── Sort: small inline dropdown
  ├── Generate Plan button (full width, prominent)
  └── Recipe list (flex-1, overflow-y-auto)
        └── DraggableRecipe cards (compact=true)
              Show: name (2 lines), time, difficulty badge, dietary tags
```

The filter state should default to expanded (or rendered as always-visible inline filters rather than a collapsible panel), because filters are the primary tool users use to find the right recipes to drag.

### 2.3 DraggableRecipe Card in Compact Mode

**Current compact card dimensions at 130px column**: unusable
**Proposed compact card at 220px column**:

```
Card layout (p-2, rounded-lg, border):
  ├── Row: [12x12 thumbnail] [Name - 2 lines, text-xs font-semibold] [Remove button]
  └── Row: [Clock icon + time] [Difficulty badge]
```

No change to the `compact` prop logic is needed — at 220px the existing `line-clamp-2` will show meaningful content. The current `w-12 h-12` thumbnail and name container will have approximately 140px of text width, enough for recipe names up to approximately 35 characters on two lines.

---

## Section 3: Recipe Browser Page Audit

**File**: `frontend/src/pages/RecipeBrowserPage.tsx`

### 3.1 Layout

The two-column layout (`lg:w-80 flex-shrink-0` sidebar + `flex-1` grid) is well-structured and does not have the same cramping issue as the Meal Planner. The 320px sidebar (`w-80`) is appropriate here because the recipe grid adapts fluidly.

### 3.2 Issues Found

**No result count shown during loading**: When `isLoading` is true the subtitle shows the "search and filter" placeholder text rather than a spinner or skeleton count message. Users have no feedback that a search is in progress after typing a query.

**Sidebar state not persisted**: `isSidebarOpen` initialises to `true` on every page visit (line 171). If a user closes the filter sidebar and navigates away then returns, the sidebar is open again. This should be persisted to `localStorage` or the URL.

**Load More button only — no infinite scroll trigger**: The `hasNextPage` condition renders a manual "Load More Recipes" button (line 295–319). The pattern is correct, but there is no `IntersectionObserver` sentinel to auto-trigger loading, which is a higher-friction pattern. This is a nice-to-have improvement, not a blocking issue.

**Sort placement**: The sort dropdown is nested inside the `RecipeFilters` component inside the sidebar. On mobile, when the sidebar is hidden, sorting is inaccessible. Sort controls should be outside the collapsible sidebar, placed above the recipe grid alongside the result count.

**No active filter count badge on the mobile "Show Filters" button**: When filters are active on mobile, the toggle button has no visual indicator that filters are applied. Users cannot tell that results are filtered when the sidebar is collapsed.

### 3.3 RecipeCard (`RecipeCard.tsx`)

The card is well designed. Two minor issues:

- `min-h-[3.5rem]` on the title (line 152) reserves space for two lines at all times, which is good for grid alignment, but at narrow grid columns (1-column mobile view) it creates excessive whitespace for short recipe names
- The `onAddToMealPlan` button renders at the bottom with `w-full` — this is correct behaviour but the button only appears if the prop is passed. On the Recipe Browser page the prop is not passed (line 286 in `RecipeBrowserPage.tsx` — no `onAddToMealPlan` prop), so users cannot add recipes to the meal plan directly from the browser. The intended workflow is browse → detail page → add, which is correct, but the sidebar in the Meal Planner page is the primary add mechanism and the two experiences are disconnected

---

## Section 4: Recipe Detail Page Audit

**File**: `frontend/src/pages/RecipeDetailPage.tsx` and `frontend/src/components/recipes/RecipeDetail.tsx`

### 4.1 Strong Points

- Excellent loading state (`LoadingScreen` component used correctly)
- Correct not-found and error states with actionable CTAs
- Servings multiplier with accessible `aria-label` on buttons
- Print styles are thoughtfully implemented

### 4.2 Issues Found

**Full-page loading spinner blocks navigation context**: The `LoadingScreen` component renders as `fixed inset-0 z-40` (see `LoadingScreen.tsx` line 95). This covers the navigation bar, which means the user loses spatial context while the recipe loads. A skeleton layout matching the recipe page structure (hero image placeholder + text skeletons) would be less disorienting.

**Breadcrumb uses ChevronLeft for forward separators**: `RecipeDetailPage.tsx` line 127 and 134 use `<ChevronLeftIcon className="... rotate-180" />` to create a right-pointing chevron. This is a CSS hack. The semantic separator should be a `ChevronRightIcon` directly, which is already imported in the file.

**`alert()` for clipboard copy**: Line 66 in `RecipeDetailPage.tsx` uses `alert('Recipe link copied to clipboard!')`. This should be a toast notification.

**Recipe footer exposes internal ID**: Line 353 in `RecipeDetail.tsx` renders `Recipe ID: {recipe.gousto_id}` in the visible page footer. This is internal metadata that has no user value and could confuse users.

**No related recipes section**: After viewing a recipe, there is no discovery path to similar recipes. Users must navigate back to the browser and re-filter. This is a significant missed engagement opportunity.

---

## Section 5: Nutrition Dashboard Page Audit

**File**: `frontend/src/pages/NutritionDashboardPage.tsx` and `frontend/src/components/nutrition/NutritionDashboard.tsx`

### 5.1 Strong Points

- Good use of `useMemo` for expensive calculations
- Four-card summary row with responsive grid is well structured
- `hasData` check with yellow warning panel guides the user appropriately

### 5.2 Issues Found

**Empty state lacks actionable link**: The "No meal plan data available" panel (lines 140–147) tells users what to do but provides no link to the Meal Planner page. A "Go to Meal Planner" CTA button should be embedded in the empty state.

**Dashboard is statically bound to current meal plan only**: The page title says "Nutrition Dashboard" but the data is exclusively from the Zustand `mealPlanStore` (current week only). Users with multiple saved plans or historical plans have no way to compare. This is a product-level gap, noted here for backlog prioritisation.

**Duplicate `import` of `Calendar` from `lucide-react`**: `NutritionDashboard.tsx` line 6 imports `Calendar` from `lucide-react`, but the layout page that wraps it also uses the same icon name from the same library — no conflict, but worth noting the component is import-heavy.

**`NutritionDashboardPage` is a thin wrapper**: It adds only a `max-w-7xl` container around `NutritionDashboard`. The page header ("Weekly nutrition overview") is inside `NutritionDashboard` itself (line 122). This mixing of page-level and component-level concerns makes the page harder to extend with navigation breadcrumbs or page actions.

---

## Section 6: Shopping List Page Audit

**File**: `frontend/src/pages/ShoppingListPage.tsx`

### 6.1 Strong Points

- Clean 3-column grid (`lg:grid-cols-3`) with generator on the left and list on the right is logical
- Print styles correctly hide the generator column
- Export options appear conditionally when items exist (good progressive disclosure)

### 6.2 Issues Found

**`window.confirm()` used for destructive actions**: Lines 25 and 31 use native browser confirm dialogs. The `Modal` component in the common library should be used for these confirmations.

**No undo mechanism after clearing**: Once the user confirms "Clear All", items are gone permanently. A short-duration toast with an "Undo" action (with a 5-second window backed by storing the previous state) would significantly reduce the anxiety around this destructive action.

**No visual progress indicator on list**: When items are checked off, there is no progress indicator (e.g., "12 of 18 items checked"). This would help users track shopping progress.

**Duplicate `Trash2` icon**: Both clear buttons ("Clear Checked" and "Clear All") share the same `Trash2` icon with different colors. Colour alone differentiates them (`text-orange-600` vs `text-red-600`). Users with colour vision deficiencies cannot distinguish them. The "Clear Checked" button should use a different icon (e.g., a checkmark-with-trash or archive icon).

---

## Section 7: Dashboard Page Audit

**File**: `frontend/src/pages/DashboardPage.tsx`

### 7.1 Strong Points

- Hero gradient section with two clear CTAs
- Quick links grid with icons is well-executed
- Skeleton loading for the recipe grid is implemented correctly with `animate-pulse`

### 7.2 Issues Found

**Hardcoded fallback value**: Line 131 renders `recipesData?.total?.toLocaleString() ?? '4,500+'`. Showing a hardcoded marketing number when the API hasn't responded yet is misleading. It should show a loading skeleton or `0`.

**Third stat card is always static**: The "Healthy / Nutrition Tracking" card (lines 149–157) shows literal text "Healthy" as the metric, which is meaningless. This should show a real metric such as daily average calories from the meal plan store, or the card should be removed until meaningful data is available.

**No keyboard navigation ring on QuickLink cards**: The `QuickLink` component (line 26) is an `<a>` element wrapping rich content, which is correct semantics. However there is no explicit `focus-visible:ring` class, relying on the browser default focus outline which may be overridden by the Tailwind base reset.

---

## Section 8: Favorites Page Audit

**File**: `frontend/src/pages/FavoritesPage.tsx`

### 8.1 Issues Found

**`handleAddAllToMealPlan` navigates to `/meal-plans/new` which redirects to `/meal-planner`**: Lines 15–18 navigate with `recipeIds` in router state, but `MealPlannerPage` at `/meal-plans/new` does not read `location.state`. The feature is completely non-functional — clicking "Add All to Meal Plan" navigates to the meal planner with no recipes added.

**Sort dropdown uses `focus:ring-primary-500`**: Line 36 references `focus:ring-primary-500` which is not a standard Tailwind class and is not defined in the design system. The ring will not render, removing the focus indicator for keyboard users.

**`FavoritesSortBy` enum values are exposed to UI**: The `<select>` options use enum values like `FavoritesSortBy.DATE_ADDED_DESC`. The implementation is correct but if enum values change, the option labels will still show correctly since they are hardcoded strings — this is fine.

---

## Section 9: Navigation Audit

**File**: `frontend/src/components/layout/Navigation.tsx`

### 9.1 Strong Points

- Mobile hamburger menu with `aria-expanded` and `aria-controls` is accessible
- `aria-hidden="true"` on all decorative icons
- NavLink active state styling is clear and consistent

### 9.2 Issues Found

**Missing `aria-current="page"` on active links**: The active link gets a visual style (`bg-green-50 text-green-700`) but no `aria-current="page"` attribute. Screen reader users cannot identify the current page from the navigation.

**Navigation height (h-16, 64px) consumes viewport on Meal Planner**: The Meal Planner page uses `h-screen flex flex-col` and the navigation bar is outside the flex column (it is part of the `Layout` component which renders `<Navigation />` above `<Outlet />`). This means the Meal Planner's `h-screen` does not account for the 64px navigation bar, causing a vertical scroll on the page. The board and sidebar therefore overflow below the fold by 64px. The Meal Planner page should use `calc(100vh - 64px)` height or use a CSS custom property for nav height.

**No skip-to-content link**: There is no "Skip to main content" link at the top of the page for keyboard users who must tab through the entire navigation on every page.

---

## Section 10: Common Components Audit

### 10.1 Button (`Button.tsx`)

Well implemented with loading states, icon slots, and all variants. One issue: the `ghost` variant has no border, making it invisible in disabled state on white backgrounds (disabled text colour `text-gray-300` on `bg-transparent` on `bg-white` is near-invisible).

### 10.2 Modal (`Modal.tsx`)

Excellent implementation using Headless UI Dialog with proper focus trap, escape key handling, and `aria-modal`. The `MealPlannerPage` settings dialog bypasses this entirely, which is the primary accessibility regression on that page.

### 10.3 EmptyState (`EmptyState.tsx`)

Strong component. When `icon` is passed as a string (`"error"`, `"search"`) from `RecipeList.tsx` lines 160 and 183, the component receives a string where it expects `React.ReactNode`. The EmptyState component renders nothing for the icon in these cases (since a string is falsy in the `{icon && ...}` check — actually a string is truthy, which means it will attempt to render the string "error" or "search" directly inside the icon container div). This is a type error masked by the loose `React.ReactNode` type acceptance.

### 10.4 FilterPanel (`FilterPanel.tsx`)

The collapsible section pattern is correct. One accessibility gap: the expand/collapse button (`aria-expanded`) does not have an `aria-controls` attribute referencing the panel ID. Screen reader users get the expanded state but no reference to which panel is being controlled.

### 10.5 Card (`Card.tsx`)

When `onClick` is provided, the card renders with `role="button"` and `tabIndex={0}`. This is correct. However `aria-pressed` is set when `selected && isClickable` (line 140). `aria-pressed` is appropriate for toggle buttons, not for navigation cards. Recipe cards that navigate to a detail page should use `role="link"` (or simply be wrapped in `<a>` tags) rather than `role="button"`.

---

## Section 11: Accessibility Summary

| Issue | Severity | Affected Components |
|---|---|---|
| No `aria-current="page"` on active nav links | High | Navigation.tsx |
| Settings modal is not an accessible dialog | High | MealPlannerPage.tsx |
| No skip-to-content link | High | Layout.tsx |
| `focus:ring-primary-500` undefined class | High | FavoritesPage.tsx |
| Native `alert()`/`confirm()` dialogs block screen readers | Medium | MealPlannerPage, ShoppingListPage, DayColumn |
| `aria-controls` missing on FilterPanel sections | Medium | FilterPanel.tsx |
| `aria-pressed` misused on navigation cards | Medium | Card.tsx |
| No keyboard-accessible week navigation on board | Medium | MealPlannerBoard / planned redesign |
| Colour-only differentiation on shopping list clear buttons | Medium | ShoppingListPage.tsx |
| Full-page loading spinner covers navigation context | Low | RecipeDetailPage.tsx |
| Empty icon string type mismatch in EmptyState | Low | RecipeList.tsx → EmptyState.tsx |

---

## Section 12: Prioritised Recommendations

### Priority 1 — Critical (Fix First, Unblocks User Goals)

1. **Fix the 7-column board layout**: Replace `xl:grid-cols-7` in `MealPlannerBoard.tsx` with a horizontally scrollable flex container giving each `DayColumn` a minimum width of 220px (`min-w-56` or `w-56 flex-shrink-0`). This is a targeted 3-line change to `BoardContent.tsx`.

2. **Fix the Meal Planner viewport height**: In `MealPlannerPage.tsx`, change `h-screen` to `h-[calc(100vh-4rem)]` (4rem = 64px nav height) to prevent the board from overflowing below the fold.

3. **Replace the Settings modal with the `Modal` component**: Remove the raw `div` implementation in `MealPlannerPage.tsx` lines 447–549 and use the existing accessible `Modal` component.

4. **Replace all `alert()`/`confirm()` calls with toast notifications and modal confirmations**: This affects `MealPlannerPage.tsx`, `DayColumn.tsx`, and `ShoppingListPage.tsx`. At minimum, use the existing `Modal` component for destructive confirmations.

### Priority 2 — High (Significant UX Improvement)

5. **Always-visible sidebar filters**: Remove the `showFilters` toggle in `PlannerSidebar.tsx`. Render cooking time and difficulty as inline chips that are always visible. Add quick-access dietary tag pills.

6. **Add `aria-current="page"` to Navigation active links**: One-line change per nav item in `Navigation.tsx`.

7. **Add skip-to-content link at the top of `Layout.tsx`**.

8. **Fix the broken "Add All to Meal Plan" flow in `FavoritesPage.tsx`**: Either implement the `location.state` reading in `MealPlannerPage`, or change the button to navigate to the Shortlist workflow.

9. **Add an empty state CTA to the Meal Planner board**: When `totalRecipes === 0`, render a centred prompt above the board with a "Generate Plan" button and a "Browse Recipes" link.

### Priority 3 — Medium (Polish and Consistency)

10. **Widen the recipe library sidebar sort/filter options** to include categories and dietary tags, matching the Recipe Browser page.

11. **Fix the `focus:ring-primary-500` class in `FavoritesPage.tsx`**: Change to `focus:ring-indigo-500`.

12. **Replace `ChevronRight` close button icon in the Settings modal** with the correct `X` icon (currently uses `ChevronRight` which is semantically incorrect — line 456 in `MealPlannerPage.tsx`).

13. **Remove the `Recipe ID` footer from `RecipeDetail.tsx`**: This is internal metadata with no user value.

14. **Add a "Go to Meal Planner" link in the Nutrition Dashboard empty state**.

15. **Add an IntersectionObserver-based load-more trigger** to `RecipeBrowserPage.tsx` as an alternative to the manual button.

### Priority 4 — Low (Future Improvements)

16. **Skeleton layout for Recipe Detail loading state** instead of full-page spinner.
17. **Related recipes section on the Recipe Detail page**.
18. **Filter sidebar state persistence** (localStorage) on the Recipe Browser page.
19. **Shopping list progress indicator** (N of M items checked).
20. **Undo action for destructive operations** on the Shopping List page.

---

## Section 13: Specific Code Locations Reference

| Issue | File | Line(s) |
|---|---|---|
| 7-column grid cramping | `components/meal-planner/MealPlannerBoard.tsx` | 96 |
| Sidebar hardcoded 384px width | `pages/MealPlannerPage.tsx` | 389–392 |
| Board p-6 reduces available width | `pages/MealPlannerPage.tsx` | 383 |
| Viewport height overflow (h-screen) | `pages/MealPlannerPage.tsx` | 310 |
| Filters collapsed by default | `components/meal-planner/PlannerSidebar.tsx` | 44 |
| `alert()` on generate failure | `pages/MealPlannerPage.tsx` | 256 |
| `alert()` on save | `pages/MealPlannerPage.tsx` | 267 |
| `window.confirm()` on clear all | `pages/MealPlannerPage.tsx` | 277 |
| `window.confirm()` on clear day | `components/meal-planner/DayColumn.tsx` | 67 |
| Inaccessible Settings modal | `pages/MealPlannerPage.tsx` | 447–549 |
| Wrong close icon in Settings modal | `pages/MealPlannerPage.tsx` | 456 |
| `window.confirm()` on shopping list | `pages/ShoppingListPage.tsx` | 25, 31 |
| `focus:ring-primary-500` undefined | `pages/FavoritesPage.tsx` | 36 |
| Broken Add All to Meal Plan | `pages/FavoritesPage.tsx` | 15–18 |
| `aria-current` missing on nav | `components/layout/Navigation.tsx` | 51–65 |
| No skip-to-content link | `components/layout/Layout.tsx` | 5–14 |
| Recipe ID shown to user | `components/recipes/RecipeDetail.tsx` | 353 |
| Wrong breadcrumb chevron | `pages/RecipeDetailPage.tsx` | 127, 134 |
| `alert()` on clipboard copy | `pages/RecipeDetailPage.tsx` | 66 |
| Hardcoded "4,500+" fallback | `pages/DashboardPage.tsx` | 131 |
| Static "Healthy" metric card | `pages/DashboardPage.tsx` | 149–157 |
| EmptyState receives string icon | `components/recipes/RecipeList.tsx` | 160, 183 |
| `aria-pressed` misused on cards | `components/common/Card.tsx` | 140 |
| `aria-controls` missing on filter sections | `components/common/FilterPanel.tsx` | 181–193 |

---

*End of audit. Total issues identified: 30+. Of these, 4 are Priority 1 (critical), 5 are Priority 2 (high), and the remainder are medium to low. The single most impactful change is replacing `xl:grid-cols-7` in `MealPlannerBoard.tsx` line 96 with a horizontally scrollable flex layout.*
