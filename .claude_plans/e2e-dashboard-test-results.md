# E2E API Integration Test Results

**Date**: 2026-02-20
**Backend**: http://localhost:8000
**Frontend**: http://localhost:3002
**Tester**: Claude Code (automated curl testing)

---

## Summary

- **Total endpoints tested**: 32
- **Passing (2xx, shape match)**: 14
- **Passing (2xx, shape mismatch)**: 11
- **Failing (4xx/5xx)**: 7
- **Missing from backend**: 2 (`/recipes/random`, `/recipes/featured`)
- **Route ordering bugs**: 2 (`/cost/recipes/budget`, `/recipes/random`, `/recipes/featured`)

---

## Results Table

| Endpoint | Frontend Function | Curl Status | Response Match | Notes |
|----------|------------------|-------------|----------------|-------|
| `GET /recipes` | `getRecipes` | 200 | PARTIAL | Shape matches `PaginatedResponse` but also returns `has_next`, `has_previous` which frontend doesn't type. Items field is `items` — matches frontend. |
| `GET /recipes/search?q=chicken` | `searchRecipes` | 200 | MATCH | Returns same paginated shape as `getRecipes`. |
| `GET /recipes/{id}` | `getRecipeById` | 200 | MATCH | Returns full `Recipe` object with all expected fields. |
| `GET /recipes/slug/{slug}` | `getRecipeBySlug` | 200 | MATCH | Returns same full `Recipe` shape. |
| `GET /recipes/random?count=5` | `getRandomRecipes` | 422 | FAIL | **Route ordering bug**: `/recipes/random` is captured by `/recipes/{recipe_id}` which tries to parse "random" as an integer. Endpoint does not exist in backend. |
| `GET /recipes/featured` | `getFeaturedRecipes` | 422 | FAIL | **Route ordering bug**: Same as above — "featured" is captured by `/recipes/{recipe_id}`. Endpoint does not exist in backend. |
| `GET /categories` | `getCategories` | 200 | MATCH | Returns `Category[]` with `{id, name, slug, type, description}`. |
| `GET /categories/{slug}` | `getCategoryBySlug` | 200 | MATCH | Returns single `Category` object. |
| `GET /categories/dietary-tags` | (none in frontend) | 404 | N/A | This OpenAPI-listed route 404s — it is shadowed by `GET /categories/{slug}` where slug="dietary-tags". Not used by frontend. |
| `GET /dietary-tags` | `getDietaryTags` | 200 | MATCH | Returns `DietaryTag[]` with `{id, name, slug, description}`. |
| `GET /dietary-tags/{slug}` | `getDietaryTagBySlug` | 200 | MATCH | Returns single `DietaryTag`. |
| `GET /allergens` | `getAllergens` (categories.ts) | 200 | PARTIAL | Returns `{id, name, description}`. Frontend `Allergen` type not verified but fields align. |
| `POST /meal-plans/generate-nutrition` | `generateMealPlan` (default) | 201 | MISMATCH | Backend returns `{plan, weekly_totals, weekly_averages, metadata}`. Frontend `MealPlanResponse` expects `{id, days: DayPlan[], total_days, start_date, end_date, average_daily_nutrition, total_nutrition, summary, ...}`. Structure is fundamentally different — backend uses day-name keys inside `plan`, frontend expects a `days` array. |
| `POST /meal-plans/generate` | `generateMealPlan` (basic) | 201 | MISMATCH | Same shape mismatch as above. |
| `POST /meal-plans/generate-nutrition` (with body) | `generateNutritionMealPlan` | 201 | MISMATCH | Frontend sends a `MealPlanGenerateRequest` body but backend reads all inputs from query params only. Body is silently ignored. |
| `GET /favorites` | `getFavorites` | 200 (with auth) / 401 (no auth) | MISMATCH | Backend returns `{items, total, page, page_size, total_pages, has_next, has_previous}`. Frontend `FavoritesResponse` expects `{favorites: FavoriteRecipe[], total, page, page_size, total_pages}`. Key name `items` vs `favorites` is a breaking mismatch. |
| `POST /favorites/{recipe_id}` | `addFavorite` | 201 (with auth) / 401 (no auth) | MISMATCH | Backend returns `{id, recipe, notes, created_at}`. Frontend `FavoriteRecipe` expects `{id, user_id, recipe_id, notes, date_added, recipe}`. Missing: `user_id`, `recipe_id`. Field name mismatch: `created_at` vs `date_added`. |
| `GET /favorites/{recipe_id}/status` | `checkIsFavorite` | 200 (with auth) | PARTIAL | Backend returns `{is_favorite: bool, notes: string, created_at: string}`. Frontend only reads `is_favorite`. Extra fields are ignored. Functional match. |
| `PUT /favorites/{recipe_id}/notes` | `updateFavorite` | 200 (with auth) | MISMATCH | Same shape mismatch as `addFavorite` — `user_id`, `recipe_id`, `date_added` missing from backend response. |
| `DELETE /favorites/{recipe_id}` | `removeFavorite` | 200 (with auth) | MISMATCH | Backend returns `{"message": "Recipe removed from favorites"}` (200). Frontend expects void/204. Non-breaking but inconsistent. |
| `GET /cost/recipes/{recipe_id}` | `getRecipeCost` | 200 | MISMATCH | Backend returns `{recipe_id, recipe_name, total_cost, cost_per_serving, servings, estimated, cost_breakdown, missing_prices}`. Frontend `RecipeCost` expects `{recipe_id, recipe_name, servings, total_cost, cost_per_serving, ingredient_costs, last_updated}`. Key mismatches: `cost_breakdown` vs `ingredient_costs`, `last_updated` is absent from backend. |
| `GET /cost/recipes/budget` | `getBudgetRecipes` | 422 | FAIL | **Route ordering bug**: `/cost/recipes/budget` is declared after `/cost/recipes/{recipe_id}` in the FastAPI router. FastAPI matches "budget" as a `recipe_id` integer, causing a 422 validation error. The budget endpoint is unreachable. |
| `POST /cost/meal-plans/estimate` | `getMealPlanCost` | 200 | MISMATCH | Backend returns `{total, by_category, by_day, per_meal_average, per_day_average, savings_suggestions, total_meals, ingredient_count}`. Frontend `MealPlanCostBreakdown` expects `{total_cost, average_daily_cost, average_per_meal, days_covered, total_servings, cost_per_serving, daily_breakdown}`. Field names are completely different. |
| `GET /cost/recipes/{recipe_id}/alternatives` | `getCheaperAlternatives` | 200 | PARTIAL | Backend returns `{recipes, total_count, max_cost, average_cost}`. Frontend `CostAlternativesResponse` expects `{original_recipe_id, original_recipe_name, original_cost, alternatives, max_budget}`. Field names differ (`recipes` vs `alternatives`, `max_cost` vs `max_budget`). |
| `POST /shopping-lists/generate` | `generateShoppingList` | 201 | MISMATCH | Backend returns `{categories, summary, recipe_ids}`. Frontend `ShoppingListResponse` expects `{id, categories, uncategorized_items, summary, source_recipe_ids, source_meal_plan_id, servings_multiplier, pantry_staples_excluded, optional_items, markdown_url, pdf_url}`. Many fields missing from backend: `id`, `uncategorized_items`, `source_recipe_ids`, `optional_items`, etc. Category item shape also differs: backend `{name, times_needed, quantities, preparations}` vs frontend `ShoppingItem {ingredient_name, quantity, unit, category, is_optional, notes, recipe_count, recipe_names}`. |
| `POST /shopping-lists/from-meal-plan` | `generateShoppingListFromMealPlan` | 500 | FAIL | Server error: "Method `Session.query` may not be passed as a SQL expression". Backend bug — the service is passing the SQLAlchemy session incorrectly when processing a meal plan dict. |
| `GET /users/me/preferences` | `getPreferences` | 200 (with auth) | MISMATCH | Backend returns `{default_servings, calorie_target, protein_target_g, carb_limit_g, fat_limit_g, preferred_cuisines, excluded_ingredients, id, user_id, dietary_tags, created_at, updated_at}`. Frontend `UserPreference` expects `carb_target_g` (backend: `carb_limit_g`) and `fat_target_g` (backend: `fat_limit_g`). Breaking field name mismatch. |
| `PUT /users/me/preferences` | `updatePreferences` | 200 (with auth) | MISMATCH | Same field name mismatch as GET. Also `protein_target_g` returns as a decimal string `"150.00"` instead of a number. |
| `GET /users/me/allergens` | `getAllergens` (users.ts) | 200 (with auth) | MISMATCH | Backend returns `{allergens: [...], count: int}`. Frontend expects `UserAllergen[]` (a direct array). Also, each backend item is `{user_id, allergen_id, severity, allergen: {id, name, description}, created_at}` — missing `id` (favorite row id), `allergen_name` (nested under `allergen.name`), and `notes`. |
| `PUT /users/me/allergens` | `updateAllergens` | 422 (wrong body) / 200 (correct body) | MISMATCH | Frontend sends `{allergen_ids: [int]}`. Backend requires `{allergens: [{allergen_id, severity}]}`. The frontend `AllergenUpdateRequest` type has the correct structure `{allergens: [{allergen_id, severity}]}` but the API function passes it directly, so if the store sends the right shape it works. Response is same mismatch as GET: wrapped object vs direct array. |
| `POST /meal-plans/generate-multi-week` | `generateMultiWeekPlan` | 500 | FAIL | Server error: "Unable to serialize unknown type: `<class 'src.database.models.Recipe'>`". The multi-week planner stores SQLAlchemy `Recipe` ORM objects inside the plan dict and FastAPI cannot JSON-serialize them. Backend bug — ORM objects need to be converted to dicts before returning. |
| `POST /meal-plans/calculate-variety-score` | `getVarietyAnalysis` | 500 | FAIL | Frontend sends `{recipe_ids: [int]}`. Backend expects `{weeks: [{days: [{meals: {meal_type: Recipe}}]}]}` — a full meal plan structure. Even with the correct structure, the endpoint fails because `_calculate_variety_score` also tries to access `.id` on what it expects to be ORM `Recipe` objects, not dicts. Double bug: wrong request schema expectation + internal ORM serialization error. |

---

## Backend Routes vs Frontend Coverage

### Backend routes used by frontend (tested above)

All 29 routes listed in the results table.

### Backend routes NOT covered by any frontend API function

| Route | Notes |
|-------|-------|
| `POST /auth/register` | Auth flow exists in backend but no `api/auth.ts` module |
| `POST /auth/login` | Same — no auth API module |
| `GET /auth/me` | Same |
| `PUT /auth/me` | Same |
| `DELETE /auth/me` | Same |
| `POST /auth/change-password` | Same |
| `GET /recipes/safe` | Allergen-safe recipe list — not wired to frontend |
| `GET /recipes/{id}/allergen-warnings` | Not wired to frontend |
| `GET /recipes/{id}/allergen-substitutions` | Not wired to frontend |
| `GET /recipes/{id}/nutrition` | Not wired to frontend |
| `GET /recipes/{id}/ingredients` | Not wired to frontend |
| `GET /allergens/{allergen_id}` | Not wired to frontend |
| `POST /meal-plans/generate-advanced` | Not wired to frontend |
| `POST /shopping-lists/generate-compact` | Not wired to frontend |
| `POST /shopping-lists/generate-advanced` | Not wired to frontend |
| `GET /meal-plans/variety-guidelines` | Not wired to frontend |
| `GET /favorites/count` | Not wired to frontend |
| `POST /users/me/allergens` | Frontend only uses PUT |
| `DELETE /users/me/allergens/{allergen_id}` | Frontend only uses PUT (bulk replace) |
| `GET /users/me/dietary-tags` | Not wired to frontend |
| `PUT /users/me/dietary-tags` | Not wired to frontend |

### Frontend functions with NO matching backend route

| Frontend Function | Module | Notes |
|------------------|--------|-------|
| `getRandomRecipes` | `recipes.ts` | Calls `GET /recipes/random` — route does not exist. Captured by `/recipes/{id}`, returns 422. |
| `getFeaturedRecipes` | `recipes.ts` | Calls `GET /recipes/featured` — route does not exist. Captured by `/recipes/{id}`, returns 422. |

---

## Critical Bugs Found

### Bug 1: Route ordering — `/recipes/random` and `/recipes/featured` unreachable (422)

**Severity**: High
**Affected functions**: `getRandomRecipes`, `getFeaturedRecipes`
**Root cause**: FastAPI registers routes in declaration order. `/recipes/{recipe_id}` is declared before any static path segments like `/recipes/random`. When the request arrives for `/recipes/random`, FastAPI matches `{recipe_id}` = "random", then fails integer parsing.
**Fix**: The endpoints do not exist in the backend at all — they need to be created and registered before the `/{recipe_id}` parameterized route.

### Bug 2: Route ordering — `/cost/recipes/budget` unreachable (422)

**Severity**: High
**Affected functions**: `getBudgetRecipes`
**Root cause**: `/cost/recipes/{recipe_id}` is registered before `/cost/recipes/budget` in `cost.py`. FastAPI matches "budget" as a `recipe_id` string which fails integer parsing.
**Fix**: Move the `/recipes/budget` route registration to before `/recipes/{recipe_id}` in `cost.py`. FastAPI requires static routes before parameterized ones.

### Bug 3: `/meal-plans/generate-multi-week` returns 500 — ORM serialization failure

**Severity**: Critical
**Affected functions**: `generateMultiWeekPlan`
**Root cause**: `MultiWeekPlanner.generate_multi_week_plan()` stores SQLAlchemy `Recipe` ORM model instances inside the returned plan dict (e.g., `day['meals']['dinner'] = <Recipe object>`). When FastAPI attempts to JSON-serialize the response, Pydantic cannot handle raw ORM objects.
**Fix**: In `multi_week_planner.py`, convert each `Recipe` ORM object to a dict (or Pydantic schema) before including it in the week/day/meal structure.

### Bug 4: `/meal-plans/calculate-variety-score` returns 500 — schema and ORM mismatch

**Severity**: High
**Affected functions**: `getVarietyAnalysis`
**Root cause (double)**: (1) Frontend sends `{recipe_ids: [int]}` but backend expects a full multi-week plan structure `{weeks: [{days: [{meals: {...}}]}]}`. (2) Even with the correct structure, `_calculate_variety_score` calls `recipe.id` expecting ORM objects, but the dict structure from the API has integer IDs, not Recipe objects.
**Fix**: Either update `_calculate_variety_score` to work with plain dicts/ints, or document and update the frontend to send the correct structure. The frontend `getVarietyAnalysis` signature (`recipeIds: number[]`) does not match the backend contract at all.

### Bug 5: `/shopping-lists/from-meal-plan` returns 500 — SQLAlchemy session misuse

**Severity**: High
**Affected functions**: `generateShoppingListFromMealPlan`
**Root cause**: The shopping list service is passing `db.query` (a bound method of the session) as a SQL expression to another SQLAlchemy call.
**Fix**: Review `ShoppingListService.generate_from_meal_plan()` — locate where `session.query` is being misused as a filter or expression argument.

---

## Response Shape Mismatches (non-crash but breaking)

### Mismatch 1: `GET/POST /favorites` — `items` vs `favorites` key

- **Backend**: `{items: [], total, page, page_size, total_pages, has_next, has_previous}`
- **Frontend expects** (`FavoritesResponse`): `{favorites: FavoriteRecipe[], total, page, page_size, total_pages}`
- **Impact**: Any component reading `response.favorites` will get `undefined`. Must access `response.items` instead.

### Mismatch 2: `POST /favorites/{id}` and `PUT /favorites/{id}/notes` — item shape

- **Backend**: `{id, recipe: {...}, notes, created_at}`
- **Frontend expects** (`FavoriteRecipe`): `{id, user_id, recipe_id, notes, date_added, recipe}`
- **Impact**: `user_id`, `recipe_id`, and `date_added` will be `undefined`. Components relying on these fields (e.g., removing a favorite by `recipe_id`) will break.

### Mismatch 3: `GET /cost/recipes/{id}` — ingredient cost shape

- **Backend**: `{recipe_id, recipe_name, total_cost, cost_per_serving, servings, estimated, cost_breakdown: {}, missing_prices}`
- **Frontend expects** (`RecipeCost`): `{recipe_id, recipe_name, servings, total_cost, cost_per_serving, ingredient_costs: IngredientCost[], last_updated}`
- **Impact**: `ingredient_costs` will be `undefined` (backend uses `cost_breakdown`). `last_updated` is absent. Cost detail views will render empty.

### Mismatch 4: `POST /cost/meal-plans/estimate` — field names completely different

- **Backend**: `{total, by_category, by_day, per_meal_average, per_day_average, savings_suggestions, total_meals, ingredient_count}`
- **Frontend expects** (`MealPlanCostBreakdown`): `{total_cost, average_daily_cost, average_per_meal, days_covered, total_servings, cost_per_serving, daily_breakdown}`
- **Impact**: All fields will be `undefined` in the frontend. The cost breakdown component will show nothing.

### Mismatch 5: `GET /users/me/preferences` — field name mismatch

- **Backend**: `carb_limit_g`, `fat_limit_g`
- **Frontend expects** (`UserPreference`): `carb_target_g`, `fat_target_g`
- **Impact**: Carb and fat targets read from preferences will always be `undefined`. Nutrition goal display will be broken.

### Mismatch 6: `GET /users/me/allergens` — wrapped object vs direct array

- **Backend**: `{allergens: [{user_id, allergen_id, severity, allergen: {id, name, desc}, created_at}], count}`
- **Frontend expects** (`UserAllergen[]`): Direct array of `{id, user_id, allergen_id, allergen_name, severity, notes, created_at}`
- **Impact**: Frontend receives an object but iterates it as an array — will fail with "allergens.map is not a function". Also `allergen_name` is nested under `allergen.name`, and `id` (the row ID) is missing.

### Mismatch 7: `POST /meal-plans/generate` and `POST /meal-plans/generate-nutrition` — structure mismatch

- **Backend**: `{plan: {Monday: {meals: {breakfast, lunch, dinner}, daily_totals}}, weekly_totals, weekly_averages, metadata}`
- **Frontend expects** (`MealPlanResponse`): `{id, days: DayPlan[], total_days, start_date, end_date, average_daily_nutrition, total_nutrition, summary, ...}`
- **Impact**: The meal planner board, nutrition dashboard, and any component consuming `MealPlanResponse.days` will receive `undefined`. The generated plan cannot be displayed.

### Mismatch 8: `POST /shopping-lists/generate` — item shape mismatch

- **Backend item**: `{name, times_needed, quantities: [{unit, total, count}], preparations}`
- **Frontend expects** (`ShoppingItem`): `{ingredient_name, quantity, unit, category, is_optional, notes, recipe_count, recipe_names}`
- **Also missing from backend**: `id`, `uncategorized_items`, `source_recipe_ids`, `optional_items`, `markdown_url`, `pdf_url`, `servings_multiplier`, `pantry_staples_excluded`
- **Impact**: Shopping list will render empty or throw errors accessing `ingredient_name`.

### Mismatch 9: `generateNutritionMealPlan` sends body but backend ignores it

- **Frontend**: Posts `MealPlanGenerateRequest` body to `/meal-plans/generate-nutrition`
- **Backend**: Reads all parameters exclusively from query string (no `@Body` parameter)
- **Impact**: Any nutrition goals, dietary tags, or constraints in the request body are silently dropped. The endpoint returns a plan ignoring the user's constraints.

### Mismatch 10: `PUT /users/me/allergens` — request body field name

- **Frontend sends** (`AllergenUpdateRequest`): `{allergens: [{allergen_id, severity}]}`
- **Backend requires**: Same structure (correct match in types)
- **But**: The frontend `updateAllergens` receives `AllergenUpdateRequest` which correctly has `allergens` key. However, the function just passes the argument directly — only works if caller provides the right shape.
- **Confirmed working**: With `{allergens: [{allergen_id: 11, severity: "avoid"}]}` → 200 OK.

---

## Working Endpoints (Confirmed Functional)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /recipes` | Functional | Pagination works, filters work |
| `GET /recipes/search` | Functional | Query search works |
| `GET /recipes/{id}` | Functional | Full recipe detail returned |
| `GET /recipes/slug/{slug}` | Functional | Slug lookup works |
| `GET /categories` | Functional | Full list returned |
| `GET /categories/{slug}` | Functional | Single category returned |
| `GET /dietary-tags` | Functional | Full list returned |
| `GET /dietary-tags/{slug}` | Functional | Single tag returned |
| `GET /allergens` | Functional | Full list returned |
| `POST /meal-plans/generate` | Functional (server-side) | Returns 201 but shape incompatible with frontend |
| `POST /meal-plans/generate-nutrition` | Functional (server-side) | Returns 201 but shape incompatible with frontend |
| `POST /favorites/{recipe_id}` | Functional (with auth) | Requires Bearer token |
| `GET /favorites` | Functional (with auth) | Requires Bearer token |
| `GET /favorites/{recipe_id}/status` | Functional (with auth) | Returns `{is_favorite, notes, created_at}` |
| `PUT /favorites/{recipe_id}/notes` | Functional (with auth) | Requires Bearer token |
| `DELETE /favorites/{recipe_id}` | Functional (with auth) | Returns 200 with message (not 204) |
| `GET /cost/recipes/{recipe_id}` | Functional | Returns cost estimate |
| `POST /cost/meal-plans/estimate` | Functional (server-side) | Returns 200 but shape incompatible |
| `GET /cost/recipes/{recipe_id}/alternatives` | Functional | Returns alternatives list |
| `POST /shopping-lists/generate` | Functional (server-side) | Returns 201 but shape incompatible |
| `GET /users/me/preferences` | Functional (with auth) | Field names differ from frontend types |
| `PUT /users/me/preferences` | Functional (with auth) | Field names differ from frontend types |
| `GET /users/me/allergens` | Functional (with auth) | Wrapped object, not array |
| `PUT /users/me/allergens` | Functional (with auth) | Works with correct request body |
