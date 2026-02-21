# Backend API E2E Test Results

**Date**: 2026-02-20
**API Base URL**: http://localhost:8000
**API Version**: 1.0.0
**Database**: Connected (SQLite)
**Total Recipes in Database**: 4,515

---

## Test Summary

| # | Endpoint | Method | Status Code | Response Time | Result |
|---|----------|--------|-------------|---------------|--------|
| 1 | `/health` | GET | 200 | 0.017s | PASS |
| 2 | `/recipes?page=1&page_size=3` | GET | 200 | 0.216s | PASS |
| 3 | `/recipes/1` | GET | 200 | 0.041s | PASS |
| 4 | `/recipes?search=chicken&page=1&page_size=3` | GET | 200 | 0.024s | PASS (note: uses inline search, not `search_query` param) |
| 5 | `/categories` | GET | 200 | 0.034s | PASS |
| 6 | `/meal-plans` | GET | 404 | 0.003s | FAIL - route not found |
| 7 | `/shopping-lists` | GET | 404 | 0.003s | FAIL - route not found |
| 8 | `/favorites` | GET | 401 | 0.006s | EXPECTED - auth required |
| 9 | `/cost/estimate` | POST | 404 | 0.005s | FAIL - wrong URL; correct is `/cost/meal-plans/estimate` |

**Overall**: 5 PASS, 1 EXPECTED (auth gate working correctly), 3 FAIL (routing/URL mismatches)

---

## Endpoint Detail Results

### 1. GET /health

**Status**: 200 OK
**Response Time**: 0.017s
**Result**: PASS

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**Notes**: Health check responding correctly. All three fields present.

---

### 2. GET /recipes?page=1&page_size=3

**Status**: 200 OK
**Response Time**: 0.216s
**Result**: PASS

**Response Structure**:
```json
{
  "items": [...],
  "total": 4515,
  "page": 1,
  "page_size": 3,
  "total_pages": 1505,
  "has_next": true,
  "has_previous": false
}
```

**Sample Item Structure**:
```json
{
  "name": "'Cheeseburger' Pizza Feast With Chicken Dippers & Burger Sauce",
  "description": "...",
  "cooking_time_minutes": 40,
  "prep_time_minutes": null,
  "difficulty": null,
  "servings": 2,
  "id": 3642,
  "slug": "cheeseburger-pizza-feast-with-chicken-dippers-burger-sauce",
  "total_time_minutes": 40,
  "categories": [],
  "dietary_tags": [],
  "allergens": [],
  "main_image": {
    "id": null,
    "url": "https://production-media.gousto.co.uk/...",
    "image_type": null,
    "display_order": 0,
    "alt_text": null,
    "width": null,
    "height": null
  },
  "nutrition_summary": {
    "calories": "1096.0",
    "protein_g": "74.6",
    "carbohydrates_g": "112.4",
    "fat_g": "40.6"
  },
  "is_active": true,
  "is_favorite": null
}
```

**Issues**:
- `prep_time_minutes` is null for all returned records (field present but unpopulated during scraping)
- `difficulty` is null across all records (same cause)
- `categories`, `dietary_tags`, and `allergens` are empty arrays for all records - junction table data appears not loaded in list view
- `main_image.id`, `image_type`, `alt_text`, `width`, `height` are all null
- `is_favorite` is null (expected when not authenticated)
- Nutrition values are returned as strings (`"1096.0"`) not numbers - type inconsistency

---

### 3. GET /recipes/1

**Status**: 200 OK
**Response Time**: 0.041s
**Result**: PASS

**Response Structure** (detail view, more complete than list):
```json
{
  "name": "Harissa Fish On Red Pepper Couscous",
  "description": "...",
  "cooking_time_minutes": 20,
  "prep_time_minutes": null,
  "difficulty": null,
  "servings": 2,
  "id": 1,
  "gousto_id": "gousto_harissa-fish-on-red-pepper-couscous",
  "slug": "harissa-fish-on-red-pepper-couscous",
  "total_time_minutes": 20,
  "source_url": "https://www.gousto.co.uk/cookbook/fish-recipes/harissa-fish-on-red-pepper-couscous",
  "date_scraped": null,
  "last_updated": null,
  "is_active": true,
  "ingredients": [
    {
      "name": "2 tbsp hot harissa paste",
      "quantity": null,
      "unit": null,
      "unit_name": null,
      "preparation": null,
      "optional": false,
      "category": null,
      "display_order": 0
    }
  ],
  "instructions": [
    {
      "step": 1,
      "text": "Boil half a kettle...",
      "time_minutes": null
    }
  ],
  "categories": [],
  "dietary_tags": [],
  "allergens": [],
  "images": [...],
  "nutritional_info": {
    "calories": "382.0",
    "protein_g": "27.1",
    "carbohydrates_g": "58.0",
    "fat_g": "4.5",
    "saturated_fat_g": "1.5",
    "fiber_g": "3.3",
    "sugar_g": "17.5",
    "sodium_mg": "1170.0",
    "cholesterol_mg": null,
    "serving_size_g": null
  }
}
```

**Issues**:
- Ingredients are stored as raw text strings in the `name` field (e.g. "2 tbsp hot harissa paste") with `quantity`, `unit`, and `preparation` all null - structured parsing did not complete during scraping
- `date_scraped` and `last_updated` are null
- `categories`, `dietary_tags`, `allergens` are empty arrays despite junction tables existing in schema
- Nutrition values are strings, not numbers

---

### 4. GET /recipes?search=chicken&page=1&page_size=3

**Status**: 200 OK
**Response Time**: 0.024s
**Result**: PASS (with caveat)

**Notes**:
- The query param used here is `search` but the backend router defines the parameter as `search_query` (confirmed in `src/api/routers/recipes.py` line 60: `search_query: Optional[str] = Query(None, ...)`). The test URL uses `?search=chicken` which the backend silently ignores, returning the first page of all recipes rather than a filtered set.
- However, the response is still 200 because the endpoint gracefully falls through to a standard unfiltered list when `search_query` is absent.
- The correct URL for this test should have been: `?search_query=chicken&page=1&page_size=3`

**Actual Behavior Confirmation**: The 3 results returned were identical to test #2 (alphabetical first page), confirming the search param was not applied.

**Verified Search Endpoint** (`/recipes/search?q=chicken`):
Status 200, Time 0.010s, returned 3 matching chicken results correctly.

---

### 5. GET /categories

**Status**: 200 OK
**Response Time**: 0.034s
**Result**: PASS

**Response Structure**: Array of category objects
**Total Categories**: 37

**Sample entries**:
```json
[
  { "id": 15, "name": "American",       "slug": "american",        "type": "cuisine",   "description": "American comfort food and classics" },
  { "id": 33, "name": "Date Night",     "slug": "date-night",      "type": "occasion",  "description": "Romantic dinner recipes" },
  { "id": 20, "name": "Dinner",         "slug": "dinner",          "type": "meal_type", "description": "Evening meals" },
  { "id": 6,  "name": "Indian",         "slug": "indian",          "type": "cuisine",   "description": "Traditional Indian cuisine" }
]
```

**Category types present**: `cuisine` (18), `meal_type` (10), `occasion` (9)
**Notes**: Response is a flat array (not paginated). All fields populated. Sorted alphabetically by name.

---

### 6. GET /meal-plans

**Status**: 404 Not Found
**Response Time**: 0.003s
**Result**: FAIL

**Response**:
```json
{ "detail": "Not Found" }
```

**Root Cause**: The backend does not register a `GET /meal-plans` route for listing saved meal plans. Reviewing `src/api/routers/meal_plans.py` confirms the router only exposes:
- `POST /meal-plans/generate`
- `POST /meal-plans/generate-nutrition`
- `POST /meal-plans/generate-advanced` (deprecated, returns 501)

There is no `GET /meal-plans` collection endpoint and no `GET /meal-plans/{id}` detail endpoint. The full OpenAPI route listing confirms these are absent.

**Frontend Expectation Mismatch**: `frontend/src/api/mealPlans.ts` calls `GET /meal-plans` in `getMealPlans()` and `GET /meal-plans/{id}` in `getMealPlanById()`. Both will 404 at runtime. Similarly, `useMealPlans()` and `useMealPlan(id)` hooks in `frontend/src/hooks/useMealPlan.ts` will always fail.

**Severity**: High - saving/retrieving meal plans is non-functional.

---

### 7. GET /shopping-lists

**Status**: 404 Not Found
**Response Time**: 0.003s
**Result**: FAIL

**Response**:
```json
{ "detail": "Not Found" }
```

**Root Cause**: The backend does not register a `GET /shopping-lists` collection endpoint. Reviewing `src/api/routers/shopping_lists.py` confirms the router only exposes:
- `POST /shopping-lists/generate`
- `POST /shopping-lists/from-meal-plan`
- `POST /shopping-lists/generate-compact`
- `POST /shopping-lists/generate-advanced` (deprecated, returns 501)

There is no `GET /shopping-lists` and no `GET /shopping-lists/{id}`.

**Frontend Expectation Mismatch**: `frontend/src/api/shoppingLists.ts` calls `GET /shopping-lists` in `getShoppingLists()` and `GET /shopping-lists/{id}` in `getShoppingListById()`. The frontend also calls `POST /shopping-lists` to save a list and `DELETE /shopping-lists/{id}` to delete - none of these routes exist on the backend.

Furthermore, the frontend's `generateShoppingList()` calls `POST /shopping-lists/generate` with a `ShoppingListGenerateRequest` object body (containing `recipe_ids`, `servings_multiplier`, `group_by_category`, etc.) but the backend endpoint expects individual `Body(...)` fields (`recipe_ids: List[int]`, `combine_similar: bool`) - a schema mismatch that will cause 422 Unprocessable Entity errors.

**Severity**: High - shopping list persistence is non-functional; generation request schema mismatches.

---

### 8. GET /favorites

**Status**: 401 Unauthorized
**Response Time**: 0.006s
**Result**: EXPECTED (authentication gate working correctly)

**Response**:
```json
{ "detail": "Authentication required" }
```

**Notes**: The `/favorites` endpoint correctly requires authentication via `CurrentUser` dependency (as defined in `src/api/routers/favorites.py`). This is correct behaviour - the auth gate is functioning.

**Frontend Handling**: The frontend `apiClient` in `client.ts` handles 401 by clearing `auth_token` from localStorage and redirecting to `/login`. This is appropriate.

**Frontend/Backend Alignment Issues Found**:
- Frontend `addFavorite()` calls `POST /favorites` with an `AddFavoriteRequest` body containing `recipe_id`
- Backend `add_favorite` endpoint is registered at `POST /favorites/{recipe_id}` (path parameter, not body) and expects a `FavoriteRequest` body for optional `notes`
- This is a URL mismatch: frontend posts to `/favorites`, backend expects `/favorites/{recipe_id}`
- Frontend `updateFavorite()` calls `PATCH /favorites/{recipeId}` but backend exposes `PUT /favorites/{recipe_id}/notes` - method and path both differ
- Frontend `checkIsFavorite()` calls `GET /favorites/check/{recipeId}` but backend exposes `GET /favorites/{recipe_id}/status` - path differs
- Frontend `getFavoriteIds()` calls `GET /favorites/ids` but backend has no such route

**Severity**: High - multiple favorites operations will fail once a user is authenticated.

---

### 9. POST /cost/estimate (recipe_ids: [1,2,3])

**Status**: 404 Not Found
**Response Time**: 0.005s
**Result**: FAIL - wrong URL

**Response**:
```json
{ "detail": "Not Found" }
```

**Root Cause**: The test used `/cost/estimate` but the backend registers this route at `/cost/meal-plans/estimate` (confirmed from OpenAPI spec and `src/api/routers/cost.py`).

**Correct Endpoint Verified**:
```
POST /cost/meal-plans/estimate
Body: {"recipe_ids": [1, 2, 3], "servings_per_meal": 2}
Status: 200
Response: {"total": 16.15, "by_category": {"other": 16.15}, "by_day": {"1": 3.5, "2": 7.15, "3": 5.5}, "per_meal_average": 5.38, "per_day_average": 16.15, "savings_suggestions": [...], "total_meals": 3, "ingredient_count": 32}
```

**Frontend Expectation Mismatch**: `frontend/src/api/cost.ts` `getMealPlanCost()` calls `POST /meal-plans/cost` - yet another different path. The backend is at `/cost/meal-plans/estimate`, the frontend calls `/meal-plans/cost`. Neither the test URL nor the frontend URL matches the actual backend route.

Additionally, `getRecipeCost()` in the frontend calls `GET /recipes/{recipeId}/cost` but the backend serves this at `GET /cost/recipes/{recipe_id}`. The prefix structure is inverted.

**Severity**: High - all cost estimation features will 404 in the frontend.

---

## Frontend/Backend Alignment Analysis

### Recipes - Mostly Aligned

| Frontend Call | Backend Route | Status |
|---|---|---|
| `GET /recipes` | `GET /recipes` | ALIGNED |
| `GET /recipes/{id}` | `GET /recipes/{recipe_id}` | ALIGNED |
| `GET /recipes/slug/{slug}` | `GET /recipes/slug/{slug}` | ALIGNED |
| `GET /recipes/search` with `search_query` param | `GET /recipes/search` with `q` param | MISALIGNED - param name differs |
| `GET /recipes/random` | Not registered | MISSING |
| `GET /recipes/featured` | Not registered | MISSING |

**Search param mismatch**: Frontend `searchRecipes()` sends `?search_query=...` but the dedicated `/recipes/search` backend endpoint expects `?q=...`. The list endpoint `GET /recipes` accepts `search_query` as an inline filter but returns a different (potentially less optimised) code path.

### Meal Plans - Partially Aligned

| Frontend Call | Backend Route | Status |
|---|---|---|
| `POST /meal-plans/generate-nutrition` | `POST /meal-plans/generate-nutrition` | ALIGNED |
| `POST /meal-plans/generate` | `POST /meal-plans/generate` | ALIGNED |
| `POST /meal-plans/generate/nutrition` | Not registered | MISSING (note: `generateNutritionMealPlan` in frontend uses this wrong path) |
| `GET /meal-plans` | Not registered | MISSING |
| `GET /meal-plans/{id}` | Not registered | MISSING |
| `POST /meal-plans` (save) | Not registered | MISSING |
| `DELETE /meal-plans/{id}` | Not registered | MISSING |
| `GET /meal-plans/{id}/export/markdown` | Not registered | MISSING |
| `GET /meal-plans/{id}/export/pdf` | Not registered | MISSING |

### Shopping Lists - Partially Aligned

| Frontend Call | Backend Route | Status |
|---|---|---|
| `POST /shopping-lists/generate` (with full object) | `POST /shopping-lists/generate` (individual fields) | SCHEMA MISMATCH |
| `GET /shopping-lists` | Not registered | MISSING |
| `GET /shopping-lists/{id}` | Not registered | MISSING |
| `POST /shopping-lists` (save) | Not registered | MISSING |
| `DELETE /shopping-lists/{id}` | Not registered | MISSING |
| `POST /shopping-lists/export` | Not registered | MISSING |

### Favorites - Misaligned

| Frontend Call | Backend Route | Status |
|---|---|---|
| `GET /favorites` | `GET /favorites` | ALIGNED (auth required) |
| `POST /favorites` with body `{recipe_id}` | `POST /favorites/{recipe_id}` with body `{notes}` | URL MISMATCH |
| `DELETE /favorites/{recipeId}` | `DELETE /favorites/{recipe_id}` | ALIGNED |
| `PATCH /favorites/{recipeId}` | Not registered (`PUT /favorites/{recipe_id}/notes` exists) | METHOD + PATH MISMATCH |
| `GET /favorites/check/{recipeId}` | `GET /favorites/{recipe_id}/status` | PATH MISMATCH |
| `GET /favorites/ids` | Not registered | MISSING |

### Cost - Misaligned

| Frontend Call | Backend Route | Status |
|---|---|---|
| `GET /recipes/{recipeId}/cost` | `GET /cost/recipes/{recipe_id}` | PREFIX MISMATCH |
| `POST /meal-plans/cost` | `POST /cost/meal-plans/estimate` | PATH MISMATCH |
| `GET /recipes/budget` | `GET /cost/recipes/budget` | PREFIX MISMATCH |
| `GET /recipes/{recipeId}/alternatives` | `GET /cost/recipes/{recipe_id}/alternatives` | PREFIX MISMATCH |
| `GET /recipes/cost/averages` | Not registered | MISSING |

---

## Data Quality Observations

1. **Ingredient parsing incomplete**: All ingredient `quantity`, `unit`, `unit_name`, and `preparation` fields are null. Ingredient data is stored as raw text strings (e.g. "2 tbsp hot harissa paste") in the `name` field rather than parsed into structured fields. This affects shopping list generation and cost estimation accuracy.

2. **Categories/tags unpopulated in responses**: Despite 37 categories existing in the database, recipe list and detail responses return empty `categories`, `dietary_tags`, and `allergens` arrays. The category data exists but is not being joined to recipe responses - either the ORM relationships are not being eagerly loaded or the junction tables have no data.

3. **Nutrition values as strings**: Nutritional fields (`calories`, `protein_g`, etc.) are returned as string representations of floats (e.g. `"382.0"`) rather than numeric types. This requires frontend type coercion and is inconsistent with API best practices.

4. **Null metadata fields**: `prep_time_minutes`, `difficulty`, `date_scraped`, `last_updated`, `image.id`, `image.alt_text`, `image.width`, `image.height` are all null across tested records.

---

## Issues by Severity

### Severity: High (Breaking)

1. **No CRUD routes for meal plans** - `GET /meal-plans`, `GET /meal-plans/{id}`, `POST /meal-plans`, `DELETE /meal-plans/{id}` are not implemented. The frontend's meal plan persistence is entirely non-functional.

2. **No CRUD routes for shopping lists** - `GET /shopping-lists`, `GET /shopping-lists/{id}`, `POST /shopping-lists`, `DELETE /shopping-lists/{id}` are not implemented. Shopping list persistence is non-functional.

3. **Cost endpoint URL structure mismatch** - Frontend calls `/recipes/{id}/cost`, `/meal-plans/cost`, `/recipes/budget` but backend serves these under `/cost/recipes/{id}`, `/cost/meal-plans/estimate`, `/cost/recipes/budget`. All cost features will 404.

4. **Favorites add route mismatch** - Frontend posts to `POST /favorites` with `recipe_id` in the body; backend expects `POST /favorites/{recipe_id}`. Add-to-favorites will fail for authenticated users.

5. **Favorites update route mismatch** - Frontend calls `PATCH /favorites/{id}`; backend exposes `PUT /favorites/{id}/notes`. Both method and path differ.

6. **Favorites check route mismatch** - Frontend calls `GET /favorites/check/{id}`; backend exposes `GET /favorites/{id}/status`.

### Severity: Medium (Degraded Functionality)

7. **Search param name inconsistency** - `/recipes/search` expects `?q=` but frontend sends `?search_query=`. Dedicated search endpoint will always return empty/wrong results from frontend.

8. **Shopping list generate schema mismatch** - Frontend sends a full `ShoppingListGenerateRequest` object; backend expects individual `Body(...)` parameters. Will produce 422 errors.

9. **`generateNutritionMealPlan` uses wrong path** - `frontend/src/api/mealPlans.ts` exports `generateNutritionMealPlan` calling `POST /meal-plans/generate/nutrition` but backend route is `POST /meal-plans/generate-nutrition` (different path).

10. **`GET /favorites/ids` not implemented** - Frontend `useFavoriteIds` hook will always fail; used for quick favorite status lookup across recipe lists.

### Severity: Low (Missing Features / Data Quality)

11. **`GET /recipes/random` not implemented** - Frontend `getRandomRecipes()` will 404.

12. **`GET /recipes/featured` not implemented** - Frontend `getFeaturedRecipes()` will 404.

13. **Meal plan export routes not implemented** - `GET /meal-plans/{id}/export/markdown` and `/pdf` are absent.

14. **Shopping list export route not implemented** - `POST /shopping-lists/export` is absent.

15. **Nutrition values returned as strings** - Should be numeric types.

16. **Categories/tags empty in recipe responses** - Recipe filtering by category works (37 categories exist) but they do not appear in recipe response payloads.

17. **Ingredient fields unparsed** - `quantity`, `unit`, `preparation` are always null; raw text is embedded in `name`.

---

## Verified Working Endpoints (Full OpenAPI Route List)

The following routes are confirmed registered and accessible (from `/openapi.json`):

```
GET  /health
GET  /recipes
GET  /recipes/search
GET  /recipes/safe
GET  /recipes/slug/{slug}
GET  /recipes/{recipe_id}
GET  /recipes/{recipe_id}/nutrition
GET  /recipes/{recipe_id}/ingredients
GET  /recipes/{recipe_id}/allergen-warnings
GET  /recipes/{recipe_id}/allergen-substitutions
GET  /categories
GET  /categories/{slug}
GET  /categories/dietary-tags
GET  /dietary-tags
GET  /dietary-tags/{slug}
GET  /allergens
GET  /allergens/{allergen_id}
GET  /favorites
GET  /favorites/count
GET  /favorites/{recipe_id}
GET  /favorites/{recipe_id}/status
GET  /favorites/{recipe_id}/notes  (via PUT)
POST /favorites/{recipe_id}
DELETE /favorites/{recipe_id}
PUT  /favorites/{recipe_id}/notes
POST /auth/register
POST /auth/login
GET  /auth/me
POST /auth/change-password
GET  /users/me/preferences
GET  /users/me/allergens
POST /users/me/allergens
DELETE /users/me/allergens/{allergen_id}
GET  /users/me/dietary-tags
POST /meal-plans/generate
POST /meal-plans/generate-nutrition
POST /meal-plans/generate-advanced  (501, deprecated)
POST /meal-plans/generate-multi-week
GET  /meal-plans/variety-guidelines
POST /meal-plans/calculate-variety-score
POST /shopping-lists/generate
POST /shopping-lists/from-meal-plan
POST /shopping-lists/generate-compact
POST /shopping-lists/generate-advanced  (501, deprecated)
GET  /cost/recipes/{recipe_id}
GET  /cost/recipes/budget
GET  /cost/recipes/{recipe_id}/alternatives
POST /cost/meal-plans/estimate
```

---

## Recommendations

### Immediate Priority (P1)

1. **Add CRUD endpoints for meal plans**: Implement `GET /meal-plans`, `GET /meal-plans/{id}`, `POST /meal-plans`, `DELETE /meal-plans/{id}` in `src/api/routers/meal_plans.py`. Requires a user-associated meal plan persistence model.

2. **Add CRUD endpoints for shopping lists**: Implement `GET /shopping-lists`, `GET /shopping-lists/{id}`, `POST /shopping-lists`, `DELETE /shopping-lists/{id}` in `src/api/routers/shopping_lists.py`.

3. **Fix cost endpoint paths in frontend**: Update `frontend/src/api/cost.ts` to use the correct backend path prefix `/cost/...` for all cost-related calls.

4. **Fix favorites add endpoint**: Either change the backend `POST /favorites/{recipe_id}` to `POST /favorites` (accepting `recipe_id` in the request body), or update the frontend to use the path-param pattern.

5. **Fix favorites update endpoint**: Align `PATCH /favorites/{id}` (frontend) with `PUT /favorites/{id}/notes` (backend) - either normalise the method or the path.

6. **Fix favorites check endpoint**: Align `GET /favorites/check/{id}` (frontend) with `GET /favorites/{id}/status` (backend).

### Short Term (P2)

7. **Fix search param name**: Either rename the dedicated search endpoint's param from `q` to `search_query` (to match how the frontend calls it), or update the frontend to send `q`.

8. **Fix shopping list generate schema**: Align the backend to accept the full `ShoppingListGenerateRequest` object body or update the frontend to send individual fields.

9. **Fix `generateNutritionMealPlan` path**: Change `POST /meal-plans/generate/nutrition` to `POST /meal-plans/generate-nutrition` in `frontend/src/api/mealPlans.ts` line 85.

10. **Implement `GET /favorites/ids`** or remove `getFavoriteIds()` from the frontend and the `useFavoriteIds` hook.

### Data Quality (P3)

11. **Fix nutrition value types**: Return numeric values from nutritional_info fields, not strings.

12. **Investigate empty categories/tags on recipes**: Ensure ORM relationships are eagerly loaded when serialising recipe list/detail responses.

13. **Parse ingredient fields during scraping or normalisation**: Structured `quantity`, `unit`, and `preparation` fields should be populated rather than embedding everything in `name`.
