# Gap Analysis: Gousto Meal Planner vs Best-in-Class Competitors

**Date:** February 2026
**Compared Against:** Mealime, Eat This Much, Plan to Eat, Paprika, Samsung Food, MealPrepPro, PlateJoy

---

## 1. Executive Summary

### Overall Assessment

The Gousto Meal Planner is a **feature-rich prototype** that covers an unusually broad surface area for a self-hosted project. It has a working scraper, REST API, interactive drag-and-drop planner, nutrition dashboard, shopping list generator, allergen filtering, multi-week planning, cost estimation, and a favorites system. Few personal projects reach this breadth.

However, the gap between "feature exists" and "feature is production-quality" is significant across most of the application. The app sits at roughly **60-65% feature parity** with mid-tier competitors like Plan to Eat or Mealime, and approximately **40-45% parity** with the full-featured leaders like Samsung Food or Eat This Much. The strongest areas are recipe data quality (Gousto's curated database), backend architecture (clean service layer, proper ORM), and the breadth of planning features (multi-week, variety scoring, allergen severity). The weakest areas are UX polish, mobile experience, onboarding, and the absence of several table-stakes features that users expect in 2026.

**The core problem is not missing features -- it is unfinished features.** Most of the backend capabilities (cost estimation, allergen substitutions, multi-week variety scoring) have no or minimal frontend exposure. The shopping list lacks aisle organization on the frontend. The meal planner board has a layout that makes day columns unreadable at standard viewport widths. Several user flows dead-end (e.g., "Add All to Meal Plan" from Favorites does nothing). These gaps create an experience where the app feels like a demo rather than a tool someone would use weekly.

### Top 5 Strengths

1. **Curated Gousto recipe database** -- 4,500+ recipes with structured nutrition, ingredients, and images. Eliminates the cold-start problem that kills Plan to Eat and Paprika adoption.
2. **Cost estimation system** -- Backend estimates per-recipe and per-plan costs with category breakdowns and savings suggestions. Only Eat This Much touches this; most competitors ignore budget entirely.
3. **Multi-week planning with variety scoring** -- 1-12 week plans with protein rotation, cuisine variety enforcement, and a 0-100 variety score. No competitor offers this level of variety control.
4. **Allergen filtering with severity levels and substitutions** -- Three severity tiers (severe/avoid/trace_ok) plus ingredient substitution suggestions. More granular than any competitor except PlateJoy.
5. **Open source / self-hosted** -- No subscription fees, no data lock-in, full data ownership. In a market where Yummly's shutdown destroyed all user data, this is a real advantage.

### Top 5 Critical Gaps

1. **No onboarding flow** -- The app drops users at a dashboard with no preference capture, no first-run guidance, and no path to a first meal plan. Every successful competitor starts with a preferences questionnaire that generates an immediate plan. This is the single highest-impact gap.
2. **Meal planner board is unusable at standard viewport widths** -- The 7-column grid forces day columns to ~130px wide, making recipe names unreadable and interaction targets too small. The UX audit confirms this is the primary layout problem.
3. **Shopping list lacks aisle/store-section organization on the frontend** -- The backend has ingredient categorization (Proteins, Vegetables, Dairy, etc.) but the frontend does not visually organize by grocery store aisle. This is the table-stakes feature most users cite as the reason they use meal planning apps.
4. **No recipe import from URLs** -- Users cannot add their own recipes from the web. The app is locked to the Gousto database. Plan to Eat and Paprika make this the centerpiece of their UX. For a self-hosted app where users expect customization, this is a glaring omission.
5. **No mobile-optimized experience** -- The app is responsive via Tailwind breakpoints but has no mobile-specific interactions, no touch-optimized drag targets, no installable PWA, and no native mobile app. Competitors treat mobile as the primary platform.

---

## 2. Feature Gap Matrix

### Recipe Management

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Built-in recipe database | Yes (4,500+) | Yes (curated) | Yes | No | No | **Ahead** |
| Recipe search by name | Yes | Yes | Yes | Yes | Yes | At Parity |
| Filter by category/cuisine | Yes | Yes | Yes | No | No | **Ahead** |
| Filter by dietary tags | Yes | Yes | Yes | No | No | At Parity |
| Filter by cooking time | Yes | Yes | No | No | No | At Parity |
| Filter by difficulty | Yes | No | No | No | No | **Ahead** |
| Filter by nutrition ranges | Yes (backend) | No | Yes | No | No | At Parity |
| Recipe import from URL | No | No | No | Yes | Yes | **Missing** |
| Manual recipe entry | No | No | No | Yes | Yes | **Missing** |
| Recipe scaling (arbitrary) | Per-serving multiplier | Fixed 2/4/6 | Yes | Yes | Yes | At Parity |
| Recipe images | Yes (from Gousto) | Yes | Yes | Yes | Yes | At Parity |
| Cooking instructions | Yes (step-by-step) | Yes | Partial | Yes | Yes | At Parity |
| Print-friendly recipe view | Yes (CSS print styles) | No | No | Yes | Yes | At Parity |
| Related/similar recipes | No | No | No | No | No | Behind |
| Recipe ratings/reviews | No | No | No | No | Yes | **Missing** |
| Cook mode (screen-on, large text) | No | No | No | No | Yes | **Missing** |

### Meal Planning

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Drag-and-drop weekly board | Yes | No | No | Yes | Yes | At Parity |
| Auto-generate meal plan | Yes (backend) | Yes | Yes | No | No | At Parity |
| Lock-and-regenerate pattern | No | No | Yes | No | No | **Missing** |
| 7-day weekly view | Yes (cramped) | List view | Grid | Board | Board | Behind |
| Multi-week planning | Yes (1-12 weeks) | No | No | No | No | **Ahead** |
| Variety scoring | Yes (0-100) | No | No | No | No | **Ahead** |
| Protein rotation | Yes | No | No | No | No | **Ahead** |
| Cuisine variety enforcement | Yes | No | No | No | No | **Ahead** |
| Plan copying/templates | Backend (is_template flag) | No | No | Yes | Yes | Behind |
| Leftover management | No | No | No | Yes | No | **Missing** |
| Snack slots | No (snack maps to dinner) | No | No | Yes | Yes | Behind |
| Calendar date binding | Partial (startDate field) | No | No | Yes | Yes | Behind |
| Batch cooking workflow | No | No | No | No | No | Missing |

### Shopping Lists

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Auto-generate from plan | Yes | Yes | Yes | Yes | Partial | At Parity |
| Ingredient merging | Yes (backend) | Yes | Yes | Yes | Yes | At Parity |
| Category grouping (backend) | Yes (9 categories) | Yes | Yes | Yes | Yes | At Parity |
| Aisle/store-section organization (frontend) | No | Yes | Yes | Yes | Yes | **Missing** |
| Checkbox persistence | Yes (Zustand store) | Yes | Yes | Yes | Yes | At Parity |
| One-tap generation | Yes (single button) | Yes | Yes | Yes | No | At Parity |
| Servings multiplier | Yes | No | Yes | Yes | Yes | At Parity |
| Exclude pantry staples option | Yes (UI toggle) | No | Yes | No | Yes | **Ahead** |
| Export (text/clipboard) | Yes | No | No | Yes | Yes | At Parity |
| Export (PDF) | No | No | No | Yes | No | Behind |
| Grocery delivery integration | No | Yes (4 stores) | Yes (2) | No | No | **Missing** |
| Shareable list link | No | Yes | No | Yes | No | **Missing** |
| Progress indicator (N/M checked) | No | No | No | No | No | Behind |

### Nutrition Tracking

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Per-recipe nutrition display | Yes | Basic | Yes | Basic | No | At Parity |
| Daily nutrition totals | Yes (dashboard) | No | Yes | No | No | At Parity |
| Weekly nutrition trends | Yes (charts) | No | Yes | No | No | At Parity |
| Macro distribution chart | Yes (Recharts) | No | Yes | No | No | At Parity |
| Calorie/macro targeting | Yes (goals store) | No | Yes | No | No | At Parity |
| Per-day vs. goal comparison | Partial | No | Yes | No | No | Behind |
| Historical nutrition tracking | No | No | Yes | No | No | **Missing** |
| Health Score per recipe | No | No | No | No | No | **Missing** |

### User Experience

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Onboarding questionnaire | No | Yes (60 sec) | Yes (macros) | Yes (tour) | No | **Missing** |
| First-run plan generation | No | Yes | Yes | No | No | **Missing** |
| Toast notifications | Yes (react-hot-toast) | Yes | Yes | Yes | Yes | At Parity |
| Loading skeletons | Partial (dashboard only) | Yes | No | No | No | Behind |
| Empty state guidance | Partial | Yes | Yes | Yes | Yes | Behind |
| Keyboard navigation | Minimal | Minimal | Minimal | Minimal | Yes | Behind |
| Accessibility (WCAG) | Multiple issues (UX audit) | Basic | Basic | Basic | Good | Behind |
| Cross-device sync | No (localStorage only) | Yes | Yes | Yes | Yes (cloud) | **Missing** |

### Social/Sharing

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Samsung Food | Status |
|---|---|---|---|---|---|---|
| Share recipe link | Yes (clipboard copy) | No | No | Yes | Yes | At Parity |
| Collaborative recipe books | No | No | No | Basic | Yes | **Missing** |
| Family/household sharing | No | Limited | No | Yes | Yes | **Missing** |
| Public recipe sharing | No | No | No | No | Yes | Missing |
| Community features | No | No | No | No | Yes | Missing |

### Integrations

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Grocery delivery (Instacart etc.) | No | Yes | Yes | No | No | **Missing** |
| Calendar sync (Google/Apple) | No | No | No | No | No | Behind |
| Health app sync (Apple Health etc.) | No | No | No | No | No | Missing |
| Export to external formats | JSON, text, clipboard | No | No | CSV | No | At Parity |

### Mobile

| Feature | This App | Mealime | Eat This Much | Plan to Eat | Paprika | Status |
|---|---|---|---|---|---|---|
| Responsive web layout | Yes (Tailwind breakpoints) | Yes | Yes | Yes | No web | At Parity |
| Mobile-optimized interactions | No | Yes | Partial | Yes | Yes (native) | **Missing** |
| PWA / installable | No | No | No | No | No | Behind |
| Native iOS/Android app | No | Yes | Yes | Yes | Yes | **Missing** |
| Offline access | No | No | No | No | Yes | **Missing** |

---

## 3. UX/Usability Gaps

### Onboarding
**Severity: Critical**

**Best apps do:** Mealime captures dietary preferences, household size, and allergens in a 60-second questionnaire at first launch, then immediately generates a personalized meal plan. The user has a full week planned within 3 minutes of first opening the app. Eat This Much calculates calorie/macro targets first, then generates a plan to hit those targets.

**This app does:** Drops the user at a dashboard page (`DashboardPage.tsx`) showing a hero section, stats cards, and a recipe grid. There is no preference capture, no dietary questionnaire, no household size prompt, and no path to a first meal plan beyond navigation links. The user must discover the meal planner, understand drag-and-drop, find the sidebar, and manually add recipes one by one. The `DashboardPage.tsx` "welcome" section references the user's name from auth but does not detect whether this is a first visit.

**Impact:** First-visit abandonment is the primary killer of meal planning apps. Without a guided first experience, users who try the app once will not return.

### Recipe Discovery
**Severity: Medium**

**Best apps do:** Samsung Food surfaces 240,000 recipes with search by ingredient, cook time, cuisine, and dietary type. Eat This Much lets users describe what they want ("something quick with chicken") and generates options. All apps show recipe images prominently.

**This app does:** The Recipe Browser page (`RecipeBrowserPage.tsx`) has a solid filter panel with category, dietary tag, allergen exclusion, cooking time, difficulty, and search by name. The recipe cards show images, time, difficulty, and dietary tags. This is functional but lacks ingredient-based search ("what can I make with chicken and rice?"), and the filter sidebar is hidden on mobile with no indication that filters are active.

### Plan Creation Flow
**Severity: High**

**Best apps do:** Mealime: 3 taps (preferences -> generate -> done). Eat This Much: set goals -> generate -> lock meals you like -> regenerate rest. Plan to Eat: browse library -> drag to calendar.

**This app does:** Navigate to Meal Planner -> open sidebar -> scroll through recipes -> drag to slot. Repeat 21 times for a full week. The auto-generate feature exists (`GeneratePlanModal.tsx`) but is a modal with configuration options that generates via the backend. There is no lock-and-regenerate pattern -- the user either accepts the entire generated plan or starts from scratch. The board layout is cramped (130px columns at standard viewports, per UX audit), making the entire drag workflow frustrating.

**Clicks to full week:** Manual: ~50+ (search + drag for each slot). Auto-generate: ~5 (open modal, configure, generate). But no hybrid workflow exists.

### Shopping List UX
**Severity: High**

**Best apps do:** One-tap generation from the plan. List is organized by grocery store aisle (Produce, Dairy, Meat, Bakery, Pantry). Ingredients are merged across all planned meals. Items can be checked off and the list tracks progress ("12 of 18 items").

**This app does:** One-tap generation works (`ShoppingListGenerator.tsx`). The backend categorizes ingredients into 9 groups (Proteins, Vegetables, Dairy, Grains & Pasta, etc.) and merges duplicates. However, the frontend does not display these categories as aisle sections -- the shopping list store (`shoppingListStore.ts`) flattens everything into a single checklist. There is no progress indicator. The export options exist (clipboard, text) but no PDF export.

### Mobile Experience
**Severity: High**

**Best apps do:** Mealime and Plan to Eat have native iOS/Android apps. Samsung Food is mobile-first. Even web-only apps like Eat This Much have mobile-responsive layouts with touch-friendly drag targets.

**This app does:** Tailwind responsive breakpoints exist (`md:`, `lg:`, `xl:`) so the layout adapts to smaller screens. At mobile widths, the meal planner board stacks to 1-2 columns (which actually works better than the cramped 7-column desktop layout). However, drag-and-drop on mobile is not tested or optimized. The sidebar collapses but recipe cards in the sidebar have small touch targets. There is no PWA manifest, no service worker, and no offline capability.

### Feedback and Loading States
**Severity: Medium**

**Best apps do:** Loading skeletons matching the page layout (not spinners). Toast notifications for all actions. Progress indicators for long operations.

**This app does:** Has `react-hot-toast` set up and some components use it. But multiple pages still use blocking `alert()` and `window.confirm()` dialogs (identified in UX audit: `MealPlannerPage.tsx` lines 256, 266, 277; `DayColumn.tsx` line 67; `ShoppingListPage.tsx` lines 25, 31). Loading states use a full-page `LoadingScreen` spinner that covers navigation context. The dashboard has skeleton loading for recipe cards but other pages do not.

### Navigation
**Severity: Low**

**Best apps do:** 4-5 top-level items maximum. The current page is clearly indicated. Mobile navigation uses a bottom tab bar for quick switching.

**This app does:** Navigation has 7 items (Dashboard, Recipes, Meal Planner, Nutrition, Shopping List, Favorites, Profile) plus auth pages. This is on the edge of too many for a top nav bar. The active state is visually styled but missing `aria-current="page"`. Mobile uses a hamburger menu rather than a bottom tab bar. The navigation structure is logical but could benefit from consolidation (e.g., Nutrition could be a tab within Meal Planner).

### Empty States
**Severity: Medium**

**Best apps do:** When no data exists, show an illustration, a brief explanation, and a call-to-action button that takes the user to the first step.

**This app does:** Has an `EmptyState` component in the common library. The Nutrition Dashboard shows a yellow warning panel but no link to the Meal Planner. The Meal Planner board shows empty "Drag a recipe here" slots but no page-level CTA for the completely-empty state. The Favorites page handles empty state.

### Error Recovery
**Severity: Medium**

**Best apps do:** Inline error messages with retry buttons. Non-blocking notifications. Undo for destructive actions.

**This app does:** Has error boundaries at the page level. API errors are logged to console. Some mutations show error toasts. But `alert()` is used for error display in several places. No undo mechanism exists for clearing the meal plan or shopping list.

---

## 4. Missing Functionality (Prioritized)

### Must-Have (Table Stakes That Are Missing)

| Feature | User Impact | Competitive Necessity | Implementation Effort | Priority Score |
|---|---|---|---|---|
| Onboarding flow (preferences questionnaire + first plan) | High | Table Stakes | M | **10** |
| Fix meal planner board layout (horizontal scroll, 220px columns) | High | Table Stakes | S | **10** |
| Aisle-organized shopping list on frontend | High | Table Stakes | S | **9** |
| Replace all `alert()`/`confirm()` with toasts and modals | High | Table Stakes | S | **9** |
| Lock-and-regenerate pattern for generated plans | High | Table Stakes | M | **8** |
| Fix Settings modal accessibility (use `Modal` component) | Medium | Table Stakes | S | **8** |
| Empty state CTAs across all pages | Medium | Table Stakes | S | **7** |

### Should-Have (Features Most Competitors Offer)

| Feature | User Impact | Competitive Necessity | Implementation Effort | Priority Score |
|---|---|---|---|---|
| Recipe import from URL | High | Differentiator | L | **8** |
| Plan copying / templates (frontend for existing backend `is_template` flag) | Medium | Differentiator | M | **7** |
| Mobile-optimized touch interactions | High | Table Stakes | M | **7** |
| Cross-device sync (user accounts + saved plans in DB) | High | Table Stakes | L | **7** |
| Shareable shopping list link | Medium | Differentiator | M | **6** |
| Shopping list progress indicator | Medium | Differentiator | S | **6** |
| Ingredient-based recipe search ("what can I make with...") | Medium | Differentiator | M | **6** |
| Related recipes on detail page | Medium | Differentiator | M | **5** |
| PDF export for shopping list and meal plan | Medium | Differentiator | M | **5** |
| Historical nutrition tracking (week-over-week comparison) | Low | Differentiator | L | **4** |

### Could-Have (Differentiators That Would Set This App Apart)

| Feature | User Impact | Competitive Necessity | Implementation Effort | Priority Score |
|---|---|---|---|---|
| Leftover propagation (4 servings for household of 2 = auto-schedule leftovers) | High | Nice-to-Have | L | **7** |
| Pantry tracking (what you already have, exclude from shopping list) | High | Differentiator | L | **6** |
| Cost-per-meal transparency on meal planner board (frontend for existing backend) | Medium | Nice-to-Have | M | **6** |
| Ingredient reuse optimization (prefer recipes sharing ingredients) | Medium | Nice-to-Have | L | **6** |
| Batch cooking consolidated timeline | Medium | Nice-to-Have | XL | **5** |
| Recipe Health Score (nutrient density rating) | Low | Nice-to-Have | M | **4** |
| PWA with offline access | Medium | Differentiator | M | **4** |
| Grocery delivery API integration | Medium | Nice-to-Have | XL | **3** |

### Won't-Need (Features Competitors Have But Don't Add Value Here)

| Feature | Reasoning |
|---|---|
| Community/social features | This is a personal/self-hosted tool; social features add complexity without matching Samsung Food's scale |
| AI-powered recipe recommendations | The variety scoring algorithm already handles intelligent selection; AI would require significant infrastructure |
| Smart appliance integration | No user base for this; Samsung-specific |
| Water intake tracking | Out of scope for a meal planner |
| Fitness/activity sync | Out of scope unless nutrition tracking deepens substantially |
| Per-platform native apps | PWA covers this adequately for a self-hosted project |

---

## 5. Unique Strengths

### 1. Gousto Recipe Database (No Cold-Start Problem)
The single biggest adoption barrier for Plan to Eat and Paprika is that new users start with zero recipes. They must import from URLs or type them manually before they can plan a single meal. This app launches with 4,500+ recipes that have structured ingredients, nutrition data, step-by-step instructions, and images. A new user can generate a full week plan within seconds of their first visit. This advantage is significant and should be leaned into hard.

### 2. Cost Estimation (Rare Feature)
The `CostEstimator` class in `src/meal_planner/cost_estimator.py` is a genuine differentiator. It estimates per-recipe and per-plan costs using ingredient price lookups with intelligent fallback estimation, generates savings suggestions based on spending patterns, and offers budget-constrained alternative recipe suggestions. No major competitor except Eat This Much even touches budget/cost, and Eat This Much does it minimally. The backend is solid, but the frontend (`CostEstimate.tsx`) only exists in the multi-week planner view -- it should be promoted to the main meal planner.

### 3. Multi-Week Planning with Variety Scoring
The `MultiWeekPlanner` in `src/meal_planner/multi_week_planner.py` supports 1-12 week plans with:
- Minimum days between recipe repeats
- Maximum same-cuisine-per-week limits
- Protein source rotation (chicken, beef, fish, vegetarian, legumes, etc.)
- A 0-100 variety score combining recipe uniqueness, protein variety, cuisine variety, and ingredient variety

No competitor offers this level of variety control. Plan to Eat and Paprika have no auto-generation at all. Mealime and Eat This Much generate one week at a time with no cross-week variety enforcement.

### 4. Allergen Filtering with Severity Levels and Substitutions
The `AllergenFilter` class supports three severity tiers (`severe`, `avoid`, `trace_ok`) and provides ingredient-level substitution suggestions for 8 allergen categories. Most competitors treat allergens as binary (exclude or don't exclude). The `trace_ok` tier -- where a recipe with trace amounts is flagged but not excluded -- is genuinely useful for users with mild sensitivities. The substitution mapping (e.g., "use oat milk instead of cow's milk for dairy allergy") adds practical value.

### 5. Open Source / Self-Hosted / Data Ownership
In a market where Yummly's December 2024 shutdown destroyed all user data and recipe collections, the self-hosted model is a real advantage. Users own their data permanently. There is no subscription fee, no ads, no risk of service discontinuation. For technically-inclined users who care about data sovereignty, this is a meaningful selling point. Paprika is the only competitor in this space, and it still requires purchasing per-platform licenses.

### 6. Clean Backend Architecture
The separation between scraper, database ORM, service layer, API routers, and schemas is well-structured. The 15-table normalized database, Pydantic validation, and SQLAlchemy ORM provide a solid foundation. The API surface is comprehensive. This is not a user-facing advantage but it makes future development substantially faster and reduces technical debt.

---

## 6. Recommended Roadmap

### Phase 1: Quick Wins (1-2 weeks)
*High impact, low effort. Fix the things that make the app feel broken.*

| Item | Impact | Files to Change | Effort |
|---|---|---|---|
| **Fix meal planner board layout** -- Replace `xl:grid-cols-7` with horizontal scroll flex container, min-width 220px per column | Critical | `frontend/src/components/meal-planner/MealPlannerBoard.tsx` (line 96), `frontend/src/pages/MealPlannerPage.tsx` (line 383, 389-392) | 1 day |
| **Fix viewport height overflow** -- Change `h-screen` to `h-[calc(100vh-4rem)]` | Critical | `frontend/src/pages/MealPlannerPage.tsx` (line 310) | 1 hour |
| **Replace all `alert()`/`confirm()` with toasts and ConfirmModal** | High | `frontend/src/pages/MealPlannerPage.tsx` (lines 256, 266, 277), `frontend/src/components/meal-planner/DayColumn.tsx` (line 67), `frontend/src/pages/ShoppingListPage.tsx` (lines 25, 31), `frontend/src/pages/RecipeDetailPage.tsx` (line 66) | 1 day |
| **Replace Settings modal with accessible `Modal` component** | High | `frontend/src/pages/MealPlannerPage.tsx` (lines 447-549) | 0.5 day |
| **Surface backend shopping list categories on frontend** -- Display the 9 ingredient categories as collapsible sections instead of flat list | High | `frontend/src/store/shoppingListStore.ts`, `frontend/src/pages/ShoppingListPage.tsx` | 1 day |
| **Add shopping list progress indicator** ("12 of 18 items checked") | Medium | `frontend/src/pages/ShoppingListPage.tsx` | 0.5 day |
| **Add empty state CTAs** -- "Go to Meal Planner" on Nutrition Dashboard; "Generate Plan" CTA on empty board | Medium | `frontend/src/components/nutrition/NutritionDashboard.tsx` (lines 140-147), `frontend/src/components/meal-planner/MealPlannerBoard.tsx` | 0.5 day |
| **Fix broken "Add All to Meal Plan" from Favorites** | Medium | `frontend/src/pages/FavoritesPage.tsx` (lines 15-18), `frontend/src/pages/MealPlannerPage.tsx` | 0.5 day |
| **Add `aria-current="page"` to navigation** | Medium | `frontend/src/components/layout/Navigation.tsx` | 0.5 hour |
| **Remove Recipe ID from detail footer** | Low | `frontend/src/components/recipes/RecipeDetail.tsx` (line 353) | 5 minutes |
| **Fix hardcoded "4,500+" fallback on dashboard** | Low | `frontend/src/pages/DashboardPage.tsx` (line 131) | 5 minutes |

### Phase 2: Core Gaps (2-4 weeks)
*Table stakes features that are missing. Without these, the app cannot compete.*

| Item | Impact | Files to Change / Create | Effort |
|---|---|---|---|
| **Onboarding flow** -- First-run preferences questionnaire (dietary type, allergens, household size, cooking time preference) that generates an immediate plan | Critical | New: `frontend/src/components/onboarding/OnboardingWizard.tsx`, `frontend/src/components/onboarding/DietaryStep.tsx`, `frontend/src/components/onboarding/AllergenStep.tsx`, `frontend/src/components/onboarding/HouseholdStep.tsx`, `frontend/src/components/onboarding/PlanPreview.tsx`. Modify: `frontend/src/App.tsx` (add onboarding route), `frontend/src/store/authStore.ts` (track onboarding completion) | 1 week |
| **Lock-and-regenerate pattern** -- On the meal planner board, allow users to "lock" individual meal slots and regenerate only the unlocked ones | High | Modify: `frontend/src/store/mealPlanStore.ts` (add `locked` field to `MealSlotState`), `frontend/src/components/meal-planner/MealSlot.tsx` (add lock toggle), `frontend/src/components/meal-planner/GeneratePlanModal.tsx` (pass locked slots), `src/api/routers/meal_plans.py` (accept locked recipe IDs) | 3 days |
| **Sidebar filter improvements** -- Always-visible filters (not collapsed), add dietary tag and allergen filters to planner sidebar to match Recipe Browser | High | `frontend/src/components/meal-planner/PlannerSidebar.tsx` (line 44 -- change default, add filter options) | 2 days |
| **Cost display on meal planner** -- Show per-recipe and per-day cost estimates on the board, leveraging existing backend `CostEstimator` | Medium | Modify: `frontend/src/components/meal-planner/DayColumn.tsx`, `frontend/src/components/meal-planner/MealPlannerBoard.tsx`. Use: `frontend/src/hooks/useCost.ts`, `frontend/src/api/cost.ts` | 2 days |
| **Plan templates** -- Save current plan as template, load template to populate the board. Backend already has `is_template` flag on `SavedMealPlan` | Medium | Modify: `frontend/src/pages/MealPlannerPage.tsx`, `frontend/src/api/mealPlans.ts`. New: `frontend/src/components/meal-planner/TemplateSelector.tsx` | 3 days |
| **Loading skeletons** -- Replace full-page spinners with skeleton layouts on Recipe Detail, Meal Planner, and Shopping List pages | Medium | Modify: `frontend/src/pages/RecipeDetailPage.tsx`, `frontend/src/pages/MealPlannerPage.tsx`. New: skeleton components in `frontend/src/components/common/` | 2 days |

### Phase 3: Differentiation (4-8 weeks)
*Features that would make this app stand out from competitors.*

| Item | Impact | Files to Change / Create | Effort |
|---|---|---|---|
| **Recipe import from URL** -- Add ability to paste a recipe URL and parse it into the database using recipe-scrapers library (already a backend dependency) | High | New: `src/api/routers/recipe_import.py`, `src/scrapers/url_importer.py`, `frontend/src/components/recipes/RecipeImportModal.tsx`, `frontend/src/pages/RecipeImportPage.tsx` | 1 week |
| **Leftover propagation** -- When a recipe makes 4 servings and the household is 2, automatically offer to schedule leftovers for a later meal | High | New: `src/meal_planner/leftover_planner.py`, `frontend/src/components/meal-planner/LeftoverIndicator.tsx`. Modify: `frontend/src/store/mealPlanStore.ts` (add leftover tracking) | 1 week |
| **Ingredient reuse optimization** -- When generating plans, prefer recipes that share ingredients with already-planned meals to reduce waste and shopping cost | Medium | Modify: `src/meal_planner/planner.py`, `src/meal_planner/multi_week_planner.py` (add ingredient overlap scoring) | 3 days |
| **Pantry tracking** -- Users can maintain a list of ingredients they already have; shopping list excludes pantry items | Medium | New: `src/api/routers/pantry.py`, `src/database/models.py` (add Pantry table), `frontend/src/components/pantry/PantryManager.tsx`, `frontend/src/pages/PantryPage.tsx` | 1 week |
| **Related recipes on detail page** -- Show recipes with similar ingredients, cuisine, or nutrition profile | Medium | New: `src/api/services/recommendation_service.py`. Modify: `src/api/routers/recipes.py`, `frontend/src/components/recipes/RelatedRecipes.tsx`, `frontend/src/pages/RecipeDetailPage.tsx` | 3 days |
| **Ingredient-based search** -- "What can I make with chicken and broccoli?" reverse search | Medium | Modify: `src/api/routers/recipes.py` (add ingredient search endpoint), `frontend/src/components/recipes/IngredientSearch.tsx` | 3 days |
| **PWA support** -- Add manifest.json, service worker for offline access, installable on mobile | Medium | New: `frontend/public/manifest.json`, `frontend/src/sw.ts`. Modify: `frontend/index.html`, `frontend/vite.config.ts` (add PWA plugin) | 3 days |

### Phase 4: Polish (Ongoing)
*UX refinement that compounds over time.*

| Item | Impact | Files | Effort |
|---|---|---|---|
| **Comprehensive accessibility audit fixes** -- Skip-to-content link, `aria-controls` on filters, `aria-pressed` correction on cards, focus rings | Medium | `frontend/src/components/layout/Layout.tsx`, `frontend/src/components/common/FilterPanel.tsx`, `frontend/src/components/common/Card.tsx`, `frontend/src/pages/FavoritesPage.tsx` | Ongoing |
| **Mobile-specific optimizations** -- Bottom tab bar, larger touch targets, swipe gestures for day navigation on planner | Medium | `frontend/src/components/layout/Navigation.tsx`, all meal planner components | 1 week |
| **Undo for destructive actions** -- Toast with "Undo" button after clearing plan or shopping list, backed by short-term state retention | Medium | `frontend/src/pages/ShoppingListPage.tsx`, `frontend/src/pages/MealPlannerPage.tsx` | 2 days |
| **IntersectionObserver infinite scroll** on Recipe Browser | Low | `frontend/src/pages/RecipeBrowserPage.tsx` | 0.5 day |
| **Sort controls outside sidebar** on Recipe Browser (accessible on mobile) | Low | `frontend/src/pages/RecipeBrowserPage.tsx`, `frontend/src/components/recipes/RecipeFilters.tsx` | 0.5 day |
| **Sidebar state persistence** to localStorage | Low | `frontend/src/pages/RecipeBrowserPage.tsx` | 0.5 day |
| **Active filter count badge** on mobile filter toggle | Low | `frontend/src/pages/RecipeBrowserPage.tsx` | 0.5 day |
| **PDF export for meal plan and shopping list** | Low | New: `frontend/src/utils/pdfExport.ts` | 2 days |
| **Calendar integration** (Google Calendar, Apple Calendar export) | Low | New: `frontend/src/utils/calendarExport.ts` | 1 day |

---

## Summary

The Gousto Meal Planner has a strong backend and an unusually complete feature set for a self-hosted project. Its multi-week variety scoring, allergen severity system, and cost estimation are genuine differentiators that no competitor matches. The Gousto recipe database eliminates the cold-start problem that plagues recipe-first competitors.

The path to a competitive product is not about building more features -- it is about finishing the features that already exist. The backend has capabilities (aisle-organized shopping lists, cost estimation, plan templates, allergen substitutions) that the frontend does not expose. The meal planner board layout is broken at standard viewports. There is no onboarding to guide first-time users. Multiple user flows dead-end or use blocking browser dialogs.

Phase 1 (quick wins) addresses the most visible breakages and can be completed in 1-2 weeks. Phase 2 (core gaps) adds the table-stakes features that would make the app viable for daily use. Phase 3 (differentiation) builds on the unique backend capabilities to create features no competitor offers. Phase 4 (polish) is ongoing refinement.

The recommended priority order is: **fix what is broken -> finish what is half-built -> build what is missing -> polish what is working**.
