# Ultra-Review Report — Gousto Meal Planner

_Generated: 2026-05-30. Synthesised from a multi-dimensional adversarial review (functionality, architecture/DB, UX/UI, subject-matter/domain, security, tests). Refuted findings: 0. All Critical/High findings below survived adversarial refutation and were re-verified against source._

This review post-dates the prior remediation merged to `main` (see `NEXT_PHASE.md`). That remediation closed the headline correctness/security/domain gaps; the findings here are residual gaps — most pre-existing, several where a merged fix is present but does not reach a particular caller or data shape.

---

## Executive summary

- **Domain safety is the top risk.** The merged allergen taxonomy holds for the false-*positive* guards, but has systematic false-*negatives* against real Gousto ingredient strings (named cheeses, Italian breads/pastas, plurals, named fish/nuts). Combined with an effectively-empty `recipe_allergens` seed (13/4529 recipes linked), the entire safety burden falls on a name-scanner with known holes — a severe-dairy user is served Camembert; a severe-gluten user is served ciabatta + linguine. These are **Critical**.
- **The documented primary nutrition CLI is broken.** `meal-plan --with-nutrition` never calls the merged candidate-builder; it truncates a 7-day plan to `len(candidates)` meals and ignores the seedable RNG. The fix exists but is dead code for the CLI (**High**).
- **The canonical `python -m pytest` is red** — passes 718 assertions but fails its own 80% coverage gate (74.03%); `nutrition_scraper.py` is 0% (**High**).
- **Architecture:** several N+1 / wrong-pagination-total paths in the list/search/safe-recipes/scoring code (**High**), plus two un-remediated error-leak paths the prior security pass missed (**Medium**).
- **Frontend:** two unsynchronised nutrition-goal stores (**High**) and a clutch of UX/a11y/type-hole gaps (**Medium/Low**).

**Severity counts (deduped):** Critical 4 · High 9 · Medium 11 · Low 14.

---

## Dimension 1 — Functionality / Correctness

### F1 (High) — CLI `meal-plan --with-nutrition` bypasses the merged nutrition-candidate fix
- **File:** `src/cli.py:477-490`
- **Evidence:** The documented primary nutrition command uses an inline sequential-fill loop (`recipe_index`-stepped over `candidates`), so with only 5 qualifying recipes it produces 5 meals across 2/7 days (Wed–Sun empty). It also ignores `planner._rng` (fully deterministic protein-desc/carb-asc order) and does not split breakfast vs main pools. The API path (`meal_plan_service.py:104`) correctly calls `generate_weekly_meal_plan_from_candidates`; only the CLI is broken. The merged method is verified to exist (`nutrition_planner.py:103`).
- **Fix:** Replace lines 477-490 with `meal_plan_dict = planner.generate_weekly_meal_plan_from_candidates(candidates)`; keep the existing `format_nutrition_meal_plan(meal_plan_dict)` call.
- **Status:** Confirmed (source re-read). Verified end-to-end in the source review.

### F2 (High) — `x0`/`xN` token dropped when a parenthesised quantity precedes it (the realistic Gousto format)
- **File:** `src/scrapers/data_normalizer.py:83-119`
- **Evidence:** Line 95 sets `ingredient_name = original[:quantity_in_parens.start()]`, so the optional/multiplier regex (lines 104-119) only sees the text *before* the parens. `parse('Free Range Egg (60g) x0')` → `is_optional=False` (optional flag lost, persisted as required 60g); `parse('Garlic Clove (5g) x2')` → quantity `5` (multiplier lost; should be 10g). The merged `x0` fix only works for the no-parens form. Pre-existing tests enshrine the broken behaviour (`tests/unit/test_data_normalizer.py:46-52`).
- **Fix:** Run the optional/multiplier regex against the full `original` string (or the trailing remainder after the closing paren), apply the multiplier to `quantity_str`, set `is_optional` for `x0`, and strip the token from the final name. Add tests: `Free Range Egg (60g) x0` → optional; `Garlic Clove (5g) x2` → quantity `10`.
- **Status:** Confirmed (source re-read).

### F3 (Medium) — Cost categoriser mis-bins peppers, green beans, peanut butter
- **File:** `src/utils/food_taxonomy.py:117-143, 188-205`
- **Evidence:** `categorize_ingredient` returns on first match in a fixed order (`protein, dairy, oil, herb, spice, fruit, grain, condiment, vegetable`). `pepper` is in both `spice` (checked first) and `vegetable`, so `red pepper`/`bell pepper` → `spice` (£0.20 vs £0.80). `bean`/`beans` is in `grain` (before `vegetable`), so `green beans` → `grain`. No exclusion list exists for cost (unlike allergens), so `peanut butter` → `dairy`. Persisted to `Ingredient.category` and drives `DEFAULT_PRICES`.
- **Fix:** Make matching specificity-aware (prefer multi-word matches), remove bare `pepper` from `spice` and `bean`/`beans` from `grain` (keep explicit `black pepper`, `kidney bean`, etc.), or add an exclusion mechanism mirroring `_ALLERGEN_DEFS`. Add regression tests.
- **Status:** Confirmed (source re-read). Behaviour-changing for cost output → backlog, not autopilot.

### F4 (Low) — Preparation note after a parenthesised quantity is discarded
- **File:** `src/scrapers/data_normalizer.py:95,121-131`
- **Evidence:** Same root cause as F2: prep parsing runs on the pre-parens slice. `parse('Chicken Breast (300g) x2, diced')` → `preparation=None`. Test `tests/unit/test_data_normalizer.py:77-85` documents this with a `# BUG` comment.
- **Fix:** After stripping the `xN`/`x0` token, examine the trailing remainder of `original` for a `, <prep>` clause. Resolved simultaneously with F2.

### F5 (Low) — `MealPlanService.generate_meal_plan(use_nutrition_data=True)` does not use nutrition data (latent dead branch)
- **File:** `src/api/services/meal_plan_service.py:53-61`
- **Evidence:** The `True` branch calls the inherited keyword `generate_weekly_meal_plan` (not overridden by `NutritionMealPlanner`), so actual nutrition values are never consulted; `min_protein_score`/`max_carb_score` (0-100) are semantically wrong for a nutrition request. Currently unreachable (router only passes `False`).
- **Fix:** Remove the `use_nutrition_data` parameter, or have the `True` branch delegate to `generate_nutrition_meal_plan` with gram parameters.

### F6 (Low) — Resume stats double-count, producing >100% success rate (cosmetic)
- **File:** `src/scrapers/gousto_scraper.py:112,128; src/cli.py:131`
- **Evidence:** On resume `stats['success']` carries over the checkpoint count but `stats['total']=len(remaining)`; `cli.py:131` computes `10/7 = 142.9%`. URL processing itself is correct.
- **Fix:** Set `stats['total']` to `checkpoint.total_urls`, or compute the rate against `(success+failed+skipped)`.

---

## Dimension 2 — Architecture / Database / Performance

### ARCH-01 (High) — `safe_recipes` pagination re-runs the full filtered query at `limit=10000` to count
- **File:** `src/api/routers/safe_recipes.py:70-95`
- **Evidence:** `get_safe_recipes()` runs twice per request — once for the page, once at `limit=10000, offset=0` to compute `total=len(...)`. Each call executes the allergen-exclusion subquery + optional joins (`allergen_filter.py:328-376`), materialises up to 10000 ORM rows, then post-filters every one through `_is_recipe_safe`. The code comment at 82-83 admits the gap.
- **Fix:** Add `count_safe_recipes()` returning `query.distinct().count()`; better, fold allergen exclusion into `queries.count_filtered_recipes` via `exclude_allergen_ids`, reusing `_apply_recipe_filters`. Accept small COUNT skew vs the in-memory post-filter.

### ARCH-02 (High) — `list_recipes` reports wrong pagination total in allergen and search branches
- **File:** `src/api/routers/recipes.py:117-123, 150-155, 162`
- **Evidence:** Allergen branch sets `'total': len(safe_recipes)` — only the current page's count, so `total_pages`/`has_next` are wrong. Search branch runs the full filter query (line 131) then throws it away to run `search_recipes` (wasted query); `search_recipes` returns `count=len(page)`, so total is page-sized. `search_by_name` (`queries.py:62-85`) ignores every other active filter, silently dropping category/allergen/nutrition.
- **Fix:** Allergen branch → dedicated count (see ARCH-01). Guard `service.get_recipes` behind `if not search_query`; add `count_searched_recipes()`; ideally route search through `_apply_recipe_filters` with an `ilike` name predicate so search composes with other filters.

### ARCH-03 (High) — `MealPlanner` scoring issues 2-3 ingredient queries per recipe over all active recipes (N+1)
- **File:** `src/meal_planner/planner.py:104-106,144-146,199-201,226-255`
- **Evidence:** `find_high_protein_low_carb_recipes()` loads every active recipe, then per recipe `_calculate_protein_score` and `_calculate_carb_score` each run a fresh `session.query(Ingredient).join(RecipeIngredient)...` (two round-trips), plus `_is_breakfast_suitable` a possible third. The relax-constraints path re-runs all scoring (doubling). ~6N queries per public `/meal-plans/generate` call.
- **Fix:** Eager-load via `selectinload(Recipe.ingredients_association).selectinload(RecipeIngredient.ingredient)` once; read `recipe.ingredients` in scoring; memoise the per-recipe ingredient-name string; reuse the scored list in the relax path.

### ARCH-04 (Medium) — `RecipeIngredient.ingredient`/`.unit` are lazy='select' → N+1 during serialization
- **File:** `src/database/models.py:309-311; src/api/services/recipe_service.py:344-355; src/database/queries.py:453-462`
- **Evidence:** `Recipe.ingredients_association` is `lazy='selectin'`, but the nested `.ingredient`/`.unit` use default `lazy='select'`. Serializers dereference `ri.ingredient.name`, `ri.unit.abbreviation/.name`, so a 20-item page with ~10 ingredients each fires up to 20×10×2 lazy SELECTs after the selectin batch.
- **Fix:** Set `lazy='selectin'` (or `joined`) on `RecipeIngredient.ingredient` and `.unit`, or chain `selectinload` in the list/detail query paths. Verify with `echo=True`.

### ARCH-05 (Medium) — No global `HTTPException` handler → inconsistent 4xx error envelope
- **File:** `src/api/middleware/error_handler.py:97-401`
- **Evidence:** Handlers are registered for `APIException`, validation, SQLAlchemy errors, and bare `Exception`, but NOT for `fastapi`/`starlette` `HTTPException`. Routers raise `HTTPException` everywhere (e.g. `recipes.py:316`, `auth.py:137-141`), so 4xx bodies fall through to FastAPI's default `{"detail": ...}` while the custom handlers return `{"detail","status","error_type"}`. Clients cannot rely on a single error schema.
- **Fix:** Register `@app.exception_handler(StarletteHTTPException)` wrapping `exc.detail` in `format_error_response(..., error_type='http_error')`, preserving `status_code`/`headers`.

### ARCH-06 (Medium) — No API versioning; meal-plan/cost endpoints typed `response_model=dict`
- **File:** `src/api/main.py:214-228; src/api/routers/meal_plans.py:23,76,134`
- **Evidence:** Routers mount at root (no `/api/v1`), so a breaking change forces all clients to migrate at once; the SPA catch-all `@app.get('/{full_path:path}')` (main.py:163) collides with any future top-level API path. Generate endpoints declare `response_model=dict`, so responses are untyped in OpenAPI despite `MealPlanResponse` existing.
- **Fix:** Introduce an `/api/v1` prefix aggregate, restrict the SPA fallback to non-`/api` paths, and type the generate endpoints with the existing schemas.

### ARCH-07 (Low) — `SavedMealPlan` table + relationship exist but no router/service (dead schema)
- **File:** `src/database/models.py:506-511,582-608`
- **Evidence:** `SavedMealPlan` is fully modelled with indexes and wired to `User.saved_meal_plans`, but no persistence router/service reads or writes it; the planner persists only to browser localStorage. Already tracked as NEXT_PHASE item 1.
- **Fix:** Implement account-bound `/meal-plans` CRUD scoped to `user_id` (enforce ownership on every by-id route to avoid IDOR), or document the table as intentionally deferred.

### ARCH-08 (Low) — FK columns lack covering indexes PostgreSQL will need (SQLite masks the gap)
- **File:** `src/database/models.py:300-302,534,564,650-652`
- **Evidence:** `RecipeIngredient.unit_id` is joined for serialization but unindexed; on the documented Postgres prod target, un-indexed FKs cause slow joins and lock-escalation on parent deletes. SQLite auto-creates some constraint indexes so the gap is invisible in dev. Tracked as NEXT_PHASE item 5.
- **Fix:** Add `Index` entries for `RecipeIngredient.unit_id` and any FK used in joins/filters; audit each `ForeignKey` before the Postgres migration.

### ARCH-09 (Low) — Filter/pagination schemas use raw `model_config` dict instead of `ConfigDict`
- **File:** `src/api/schemas/recipe.py:388-399,436-453; src/api/schemas/pagination.py:40-47,56-63,101-115`
- **Evidence:** `NutritionFilters`, `RecipeFilters`, `PaginationParams`, `SortParams`, `PaginatedResponse` declare `model_config = {...}` as a plain dict while every response model uses `ConfigDict(...)`. Functionally valid in Pydantic v2; a consistency/maintenance nit (these request-only models silently lack `from_attributes`).
- **Fix:** Normalise to `ConfigDict(...)`; add `from_attributes` only where a model is fed ORM objects.

---

## Dimension 3 — UX / UI / Frontend

### FE-01 (High) — Two unsynchronised nutrition-goal stores: planner Goals vs Nutrition Dashboard
- **File:** `frontend/src/pages/MealPlannerPage.tsx:571-642; frontend/src/components/nutrition/NutritionDashboard.tsx:56,154-219`
- **Evidence:** The planner Goals modal writes `mealPlanStore.plan.nutritionGoals` (keys `daily_calories/daily_protein_g/...`); `NutritionSummary` reads it. The Nutrition Dashboard + `NutritionGoals` editor read/write a completely separate `useNutritionGoalsStore` (keys `daily_calories/protein_g/carbs_g/fat_g/fiber_g`), persisted to a different localStorage key. No code bridges the two, so a goal set in one place never appears in the other.
- **Fix:** Consolidate to a single source of truth: either point the planner Goals modal at `useNutritionGoalsStore` (mapping `daily_protein_g→protein_g`) and drop `mealPlanStore.nutritionGoals`, or make the Dashboard read `mealPlanStore`. Normalise key names; update `NutritionSummary` + `NutritionDashboard`. (Tracked partially as NEXT_PHASE item 4.)

### FE-02 (Medium) — `RecipeList` passes string icons `'error'`/`'search'` rendered as literal text
- **File:** `frontend/src/components/recipes/RecipeList.tsx:159,181`
- **Evidence:** `<EmptyState icon="error" />` / `icon="search"`. `EmptyState.icon` is `React.ReactNode` rendered directly inside a circle with no string→icon mapping, so the user sees the literal word "error"/"search" in the badge. The error path is worst: a failed fetch shows a circle containing "error".
- **Fix:** Pass real icon elements (e.g. `<ExclamationTriangleIcon className="h-8 w-8" />`, `<MagnifyingGlassIcon className="h-8 w-8" />` — heroicons already used elsewhere), or add a string→icon token map in `EmptyState`.

### FE-03 (Medium) — `PlannerSidebar` recipe search has no debounce
- **File:** `frontend/src/components/meal-planner/PlannerSidebar.tsx:44,56-63,121-128`
- **Evidence:** `onChange → setSearchQuery` directly, and `searchQuery` is spread into the `useInfiniteRecipes` query key with no debounce/SearchBar wrapper. Typing "chicken" fires 7 paginated `/recipes` requests.
- **Fix:** Use the existing `useDebounce(searchQuery, 300)` in the query key, or swap the raw `<input>` for the common debounced `SearchBar`.

### FE-04 (Low) — `PlannerSidebar` maps recipes with `recipe: any`, defeating type safety
- **File:** `frontend/src/components/meal-planner/PlannerSidebar.tsx:186`
- **Evidence:** `recipes.map((recipe: any) => ...)` annotates `any` even though `recipes` is `RecipeListItem[]`, disabling checks that `DraggableRecipe` receives a valid item (`dietary_tags` dereferenced at `DraggableRecipe.tsx:162`). Strict mode is otherwise on.
- **Fix:** Remove the `: any`; the param infers to `RecipeListItem`.

### FE-05 (Low) — MealPlannerPage Export is desktop-only and dumps internal JSON
- **File:** `frontend/src/pages/MealPlannerPage.tsx:436-444,358-376`
- **Evidence:** Export button uses `hidden sm:flex` (absent on mobile); `handleExport` downloads a raw Zustand JSON blob rather than using `useExportMealPlanMarkdown`/`useExportMealPlanPDF` (`useMealPlan.ts:131-144`). Tracked as NEXT_PHASE item 6.
- **Fix:** Surface export in the mobile row/overflow menu and export via the markdown hook.

### FE-06 (Medium) — 401 handler hard-redirects via `window.location.href`, leaving authStore inconsistent
- **File:** `frontend/src/api/client.ts:82-86`
- **Evidence:** On any 401 the interceptor removes `auth_token` and does `window.location.href = '/login'` (full reload), losing React Query cache + unsaved Zustand state, and does NOT clear the persisted `authStore` (so on reload it can rehydrate authenticated-ish state with the token gone). Fires for background/optimistic requests too.
- **Fix:** Reject with a typed 401 and let a central auth boundary (`ProtectedRoute`/`useCurrentUser onError`) call `clearAuth()` and navigate via React Router. If a redirect must remain, also call `useAuthStore.getState().clearAuth()`.

### FE-07 (Low) — Standalone `MealPlannerBoard` DnD context registers only `PointerSensor` (a11y regression risk)
- **File:** `frontend/src/components/meal-planner/MealPlannerBoard.tsx:131-137,201-226`
- **Evidence:** The live page supplies the correct multi-sensor context (Pointer+Touch+Keyboard) via `BoardContent`, but the standalone `MealPlannerBoard` wrapper duplicates the handlers and registers only `PointerSensor`. It appears unused in routing; if rendered directly it silently loses keyboard/touch drag — the exact regression the merged fix addressed.
- **Fix:** Delete the standalone wrapper (keep `BoardContent` + `parseDragId`/`parseDropId`), or mirror the page's sensors.

### FE-08 (Low) — Mobile bottom-sheet sidebar not tap-away dismissable, lacks dialog a11y
- **File:** `frontend/src/pages/MealPlannerPage.tsx:511-525`
- **Evidence:** The mobile sheet has no backdrop/scrim, no tap-away/swipe-down, no `role="dialog"`/`aria-label`, and does not trap/restore focus. Keyboard/SR users get no signal a sheet opened; it can obscure the NutritionSummary footer.
- **Fix:** Add a dismissable backdrop/swipe, `role`+`aria-label`, focus management; or reuse the common Modal/Headless UI Dialog for the mobile variant.

### FE-09 (Low) — Planner "Goals" modal commits on every keystroke with no Save/Cancel
- **File:** `frontend/src/pages/MealPlannerPage.tsx:649-655`
- **Evidence:** The modal mutates `plan.nutritionGoals` live on each keystroke, so "Save Goals" only closes — no save action, toast, or revert (unlike `NutritionGoals.tsx`). Combined with FE-01, edits have no visible Dashboard effect.
- **Fix:** After consolidating stores (FE-01), edit a local draft committed on Save with a toast, or relabel the button "Done".

### FE-1 (Low) — `MacroBreakdown` divide-by-zero renders "NaN% over" when a macro goal is 0
- **File:** `frontend/src/components/nutrition/MacroBreakdown.tsx:85-97,148`
- **Evidence:** `getPercentage` guards `goal===0` but `getStatusColor` and the over/remaining label do not; a 0 fat/fiber goal yields `Infinity`/`NaN`, rendering "NaN% over" in the over-target colour. Cosmetic.
- **Fix:** Guard `getStatusColor` with `if (goal === 0) return 'text-gray-400'` and the label with a `goal>0` check, mirroring `getPercentage`.

---

## Dimension 4 — Subject-matter validity / Domain (Allergen, Nutrition, Cost)

> **The merged allergen *false-positive* guards all hold** (eggplant≠eggs, peanut/almond butter≠dairy, butternut≠dairy, coconut/oat milk≠dairy, water chestnut/nutmeg≠tree nuts). True-positive controls (whole milk, cheddar, plain flour, penne, king prawns) fire. **But the *false-negative* gaps below mean the safety layer cannot be trusted against real Gousto data.**

### ALG-1 (Critical) — Dairy false negatives: named cheeses not detected
- **File:** `src/utils/food_taxonomy.py:39-54`
- **Evidence:** `detect_allergens('camembert')=[]`, `('brie')=[]`, `('2 burrata balls')=[]` — all pure dairy. These are real seeded ingredients (`data/seed_ingredients.sql`: camembert, brie, burrata). End-to-end: `AllergenFilter._is_recipe_safe()` returns SAFE for a Camembert recipe with a severe-dairy user (`recipe_allergens` cannot catch it — only 13/4529 recipes are linked).
- **Fix:** Add to `dairy` include: camembert, brie, burrata, gruyere/gruyère, gorgonzola, stilton, quark, skyr, gouda, emmental, manchego, pecorino, comte/comté, taleggio, provolone, soft cheese, goats cheese; handle `cheesecake` (`\bcheese\b` misses `cheesecakes`). Add a curated corpus test.

### ALG-2 (Critical) — Gluten false negatives: ciabatta, focaccia, baguette, linguine, farfalle, lasagne, ravioli, freekeh
- **File:** `src/utils/food_taxonomy.py:23-37`
- **Evidence:** `detect_allergens` returns `[]` for ciabatta, 200g linguine, farfalle, lasagne sheets, 75g freekeh, focaccia, baguettes, sourdough pittas — all in the seed (ciabatta ×7, linguine ×5, lasagne sheets ×5, freekeh ×4). A recipe with ciabatta+linguine is SAFE for a severe-gluten user. 42 distinct gluten-bearing seed names missed.
- **Fix:** Extend `gluten` include: ciabatta, focaccia, baguette, linguine, farfalle, fusilli, rigatoni, tortiglioni, lasagne, lasagna, ravioli, tortellini, freekeh, sourdough, bagel, crumpet, bao bun, spring roll wrapper. Keep rice-vermicelli/gluten-free exclusions. Add corpus tests.

### ALG-3 (Critical) — Pluralised tokens defeat whole-word matching
- **File:** `src/utils/food_taxonomy.py:151-159`
- **Evidence:** `_phrase_in` uses `\bphrase\b` for single tokens, so `bread`≠`breads`/`flatbreads`, `pita`≠`pittas`, `wrap`≠`wraps`, `bun`≠`buns`, `pancake`≠`pancakes`, `batter`≠`batters`. Seed contains `2 wholemeal pittas`, `2 hot dog buns`, `bao buns`, `2 focaccia breads` — all missed.
- **Fix:** Make single-token matching plural-aware: `rf'\b{re.escape(phrase)}(?:e?s)?\b'`, OR add explicit plural entries. **Re-run the false-positive guards after the change** (e.g. `butters` must still be excluded for dairy) — this is why this is Medium-risk, not autopilot.

### ALG-4 (High) — Fish false negatives: monkfish, whitebait, kipper, caviar, roe, surimi
- **File:** `src/utils/food_taxonomy.py:76-83`
- **Evidence:** `detect_allergens('monkfish')=[]` (bare `fish` token fails `\bfish\b` on `monkfish`), plus whitebait/kipper/caviar/roe/surimi absent.
- **Fix:** Add to `fish` include: monkfish, swordfish, eel, whitebait, kipper, caviar, roe, surimi, sea bream/seabream, snapper, sole, sprat, rollmop. `monkfish` needs its own entry.

### ALG-5 (High) — Tree-nut false negatives: pine kernel(s), cobnut, frangipane, gianduja, amaretti
- **File:** `src/utils/food_taxonomy.py:59-67`
- **Evidence:** `detect_allergens('pine kernel & seed mix')=[]` (a real seed ingredient), plus cobnut/frangipane/gianduja/amaretti. Include has `pine nut`/`pine nuts` but not the British `pine kernel(s)`.
- **Fix:** Add to `tree nuts` include: pine kernel, pine kernels, cobnut, frangipane, gianduja, amaretti. Existing exclusions (butternut, water chestnut, peanut, doughnut) remain correct.

### SEED-1 (Critical) — `recipe_allergens` effectively empty in the production seed
- **File:** `data/seed.sql` + `data/seed_ingredients.sql`
- **Evidence:** 4529 recipes but only 28 `recipe_allergens` rows across 13 recipe_ids; `seed_ingredients.sql` inserts zero. So `AllergenFilter._recipe_has_allergen()`'s table branch almost never fires; ALL safety depends on the name-scanner with the ALG-1..5 holes. The intended defense-in-depth is in practice a single point of failure.
- **Fix:** Backfill `recipe_allergens` for all seeded recipes by running `detect_allergens` over ingredient names (the scraper's `_populate_recipe_allergens` logic), or ship a precomputed seed. Fixing ALG-1..5 is the prerequisite that makes either layer trustworthy.

### SEED-2 (High) — Seeded ingredient names embed quantities/units, degrading every name heuristic and breaking aggregation
- **File:** `data/seed_ingredients.sql`
- **Evidence:** `normalized_name` equals the raw scraped string incl. amounts (`2 basa fillets`, `120g golden couscous`, `2 camemberts 250g`). `categorize_ingredient`/`detect_allergens` work by substring luck and fail where the food word is plural/fused (amplifies ALG-1..3). `shopping_list.generate_from_recipes` groups by `normalized_name`, so `2 ciabatta` and `1 ciabatta` are separate lines. `cost_estimator` can double-count the embedded amount vs the quantity column.
- **Fix:** Normalise ingredient names at ingest (strip leading quantity/unit tokens, singularise) before storing `normalized_name` — belongs in `data_normalizer` — and backfill the seed.

### SEED-3 (Medium) — Seeded `ingredient.category` is 96% NULL, uses labels absent from cost tables; `is_allergen` uniformly 0
- **File:** `data/seed_ingredients.sql; src/utils/food_taxonomy.py:117-143; src/meal_planner/cost_estimator.py:76-87`
- **Evidence:** 1696/1760 (96%) `category=NULL`, ALL `is_allergen=0`. Of the 64 non-null, `legume`/`nuts` are not keys in `DEFAULT_PRICES`/`_CATEGORY_KEYWORDS`, so they price at the `other` £1.00/100g default. NULL categories recover via runtime fallback, but stored data is misleading.
- **Fix:** Backfill with `categorize_ingredient(normalized_name)` and `is_allergen=bool(detect_allergens(name))`. Reconcile vocabulary (`legume`/`nuts` vs the `grain` that `categorize_ingredient` returns for lentils/beans).

### COST-1 (Medium) — `IngredientPrice` never populated; cost always uses flat category averages
- **File:** `src/meal_planner/cost_estimator.py:204-220`
- **Evidence:** `IngredientPrice` is referenced only in `models.py` and the estimator query; no seed/scraper/CLI inserts a row, so `_base_price_per_100g` always falls through to `DEFAULT_PRICES`. No pack-size rounding. Tracked as NEXT_PHASE item 3.
- **Fix:** Seed `ingredient_prices` from a curated CSV + pack-size rounding + waste factor; until then document costs as category-average estimates.

### COST-2 (Low) — `COMMON_WEIGHTS` multiplies per-unit weight by quantity even for amount-bearing names
- **File:** `src/meal_planner/cost_estimator.py:316-319`
- **Evidence:** For count/None-unit ingredients whose name contains e.g. `potato`, returns `180*quantity`. With seed names carrying embedded amounts (SEED-2), `180g potato` parsed as quantity 180 yields `180*180g`. Bounded (true weight-unit rows short-circuit), but ambiguous rows inflate.
- **Fix:** Apply `COMMON_WEIGHTS` only when `unit_type=='count'` or unit is None AND quantity is a plausible piece count (<~20); best fixed upstream via SEED-2.

### PLAN-1 (Low) — Keyword protein/carb scoring misclassifies; low-carb plan can silently include high-carb meals
- **File:** `src/meal_planner/planner.py:94-178,243-254`
- **Evidence:** Scores normalise by `len(ingredients)`, inverting true density (a 3-ingredient recipe with one protein scores higher than a 15-ingredient one with two). `find_high_protein_low_carb_recipes` fully relaxes constraints when <21 qualify, so a "high protein low carb" plan can be filled with recipes meeting neither bound. The actual-nutrition path is sound and should be preferred.
- **Fix:** Prefer `NutritionMealPlanner` for labelled plans; when falling back, surface an "estimated" caveat and flag when the carb ceiling was relaxed.

---

## Dimension 5 — Security & Tests

### SEC-1 (Medium) — `multi_week` router leaks raw internal exception text in 500 responses
- **File:** `src/api/routers/multi_week.py:190,338`
- **Evidence:** Both generic `except Exception as e` blocks return `detail=f'...: {str(e)}'` unconditionally (not gated by `api_debug`). Confirmed `multi_week.py` does NOT import `safe_error_detail` (only `DatabaseSession, OptionalUser`). Public (OptionalUser, no auth). Same leak class the remediation closed elsewhere; this file (last modified Feb 22) was missed.
- **Fix:** `from src.api.dependencies import safe_error_detail` and replace both f-strings with `safe_error_detail('Failed to generate multi-week meal plan', e)` / `safe_error_detail('Failed to calculate variety score', e)`.
- **Status:** Confirmed (source re-read).

### SEC-2 (Medium) — `FavoritesService` leaks raw SQLAlchemy `IntegrityError` text to client
- **File:** `src/api/services/favorites_service.py:118`
- **Evidence:** `raise HTTPException(status_code=400, detail=f'Failed to add favorite: {str(e)}')` — `str(e)` of an `IntegrityError` includes the SQL, bound params, and driver error. Returned unconditionally; the global handler's `api_debug` gate is bypassed because the error is converted to `HTTPException` inside the service. Reachable by any authenticated user (recipe deleted between check and insert → FK error).
- **Fix:** Return generic `detail='Could not add recipe to favorites'`; log the full exception server-side via `logger.error`.
- **Status:** Confirmed (source re-read).

### SEC-3 (Low) — `get_current_user_optional` does not re-check `token_version`/`is_active`
- **File:** `src/api/dependencies.py:199-233`
- **Evidence:** `get_current_user` was hardened to reject revoked/inactive accounts; `get_current_user_optional` takes no `db` parameter and only decodes signature/expiry. A token minted with `ver=0` for a user whose `token_version` was later bumped still returns a payload. Backs all read-only OptionalUser endpoints (e.g. `GET /recipes?exclude_user_allergens=true`). Bounded by access-token TTL → Low.
- **Fix:** Add an optional `db` dependency and apply the same `is_active`+`token_version` recheck (return None instead of raising) via a shared helper. Also shorten `jwt_expire_minutes` (currently 1440).

### SEC-4 (Low) — JWT stored in localStorage (XSS-exfiltratable), long TTL, no CSP
- **File:** `frontend/src/api/auth.ts:27,49,87; frontend/src/store/authStore.ts:48-92; frontend/src/api/client.ts:84-85`
- **Evidence:** Access token persisted in localStorage (readable by any origin JS) with a 24h TTL, no httpOnly/CSRF, no CSP header. Tracked as NEXT_PHASE item 6.
- **Fix:** Move the token to an httpOnly Secure SameSite cookie (with CSRF) or hold in memory with short TTL + silent refresh; stop persisting the raw token. Interim: shorten TTL, add a strict CSP.

### TQ-1 (High) — Default `python -m pytest` fails its own 80% coverage gate (74.03%)
- **File:** `pytest.ini:29 (--cov-fail-under=80)`; coverage TOTAL 74.03%
- **Evidence:** Default `python -m pytest`: 718 passed, then `FAIL Required test coverage of 80% not reached. Total coverage: 74.03%` (non-zero exit). Largest hole: `nutrition_scraper.py` 0% (170 stmts). CI/devs will treat the suite as broken though all assertions pass.
- **Fix:** Add tests to lift coverage over 80% (start with TQ-2), or lower `--cov-fail-under` to the real floor. Do not leave the canonical command red.
- **Status:** Confirmed (`pytest.ini:29` re-read; gate present).

### TQ-2 (High) — `nutrition_scraper.py` per-serving nutrition parsing is 0% covered
- **File:** `src/scrapers/nutrition_scraper.py:54-178 (0% / 170 stmts)`
- **Evidence:** The "Second value is per serving" heuristic (selecting `g_matches[1]` over `g_matches[0]` for calories/fat/carbs/sugar/protein/sodium) produces every `NutritionalInfo` row used by the macro planner and is entirely untested. A regression in the per-serving index would silently halve/double every macro with no test failing.
- **Fix:** Extract the parsing block (122-178) into a pure `parse_nutrition_lines(lines) -> dict[str, Decimal]` and add `tests/unit/test_nutrition_scraper.py`: (a) per-100g + per-serving pair asserts index 1; (b) single value asserts index 0 fallback; (c) sodium g→mg ×1000; (d) malformed/empty → `{}` without raising. No Playwright needed.

### TQ-3 (Medium) — `ShoppingListGenerator._categorize_ingredient` mis-buckets butter beans/peanut butter as Dairy — no test
- **File:** `src/meal_planner/shopping_list.py:74-92; test gap tests/unit/test_shopping_list_generator.py:82-86`
- **Evidence:** Naive `keyword in name_lower` with dict-order precedence where Dairy (`butter`) precedes Legumes/Nuts. Runtime: `butter beans`/`peanut butter`/`coconut cream`/`almond milk` → Dairy. The only categorisation test asserts just `'Proteins' in result` for chicken.
- **Fix:** Add parametrized asserts (butter beans→Legumes, peanut butter→Nuts & Seeds, cannellini beans→Legumes); fix with word-boundary + most-specific-first, or delegate to `food_taxonomy` (two parallel implementations exist).

### TQ-4 (Medium) — `food_taxonomy.categorize_ingredient` classifies butter beans as 'dairy' for cost — untested collision
- **File:** `src/utils/food_taxonomy.py:124,202-205; test gap tests/unit/test_food_taxonomy.py:84-99`
- **Evidence:** `dairy` (`butter`) is checked before `grain`/`vegetable`; runtime `categorize_ingredient('butter beans') == 'dairy'`. The allergen path excludes `butter bean` but the cost path has no exclusion list. Tests only cover clean single-word cases. (Same root cause as F3.)
- **Fix:** Add collision tests (butter beans→grain, almond milk→non-dairy); give `categorize_ingredient` an exclusion mechanism or word-boundary+phrase precedence.

### TQ-5 (Low) — `test_known_allergens_cover_14_fic` is misnamed — asserts 13 and merges crustaceans/molluscs
- **File:** `tests/unit/test_food_taxonomy.py:72-78`
- **Evidence:** Name claims "14 FIC" but the list has 13 names; `known_allergens()` returns 13 (crustaceans+molluscs folded into one `shellfish`). Membership-only loop cannot fail if a required category is missing.
- **Fix:** Rename to `test_lexicon_covers_seeded_allergens` and assert `set(known_allergens()) == set(seeded allergen names)`, or split shellfish for true 14-FIC coverage.

### TQ-6 (Low) — `test_detect_multiple_allergens` docstring describes a pesto case it never asserts
- **File:** `tests/unit/test_food_taxonomy.py:64-67`
- **Evidence:** Docstring says "Pesto = tree nuts + dairy" but the body only asserts `detect_allergens('creamy cheese sauce')` contains `dairy`. `detect_allergens('basil pesto') == {'tree nuts'}` only.
- **Fix:** Assert an input that genuinely yields ≥2 allergens, e.g. `{'gluten','eggs'} <= detect_allergens('fresh egg pasta')`; drop the inaccurate comment.

### TQ-7 (Medium) — No test covers the actual scraper resume loop
- **File:** `tests/unit/test_checkpoint_resume.py:39-52 vs src/scrapers/gousto_scraper.py:103-145`
- **Evidence:** `test_no_urls_skipped_when_marking_during_iteration` iterates `list(manager.data.pending_urls)` — wrapping in `list()` copies first, so it passes even against the OLD aliasing bug; it tests `list()`, not the fix. The real resume path (`gousto_scraper.py:109-111,145,115`) is in the uncovered ranges.
- **Fix:** Add an integration test calling `GoustoScraper.scrape_recipes(resume=True)` against a checkpoint with pending+failed URLs (mock scrape via `responses`); assert each URL visited once, marks mutate the snapshot, a still-failing URL keeps the checkpoint not-complete.

### TQ-8 (Medium) — `get_warnings` ignores ingredient-name analysis (asymmetric vs exclusion)
- **File:** `src/meal_planner/allergen_filter.py:195-198`
- **Evidence:** `_is_recipe_safe`/`get_safe_recipes` use BOTH the table link and ingredient-name analysis, but `get_warnings` relies ONLY on `recipe.allergens` (the table). For an allergen in the ingredient name but missing from `recipe_allergens`, a `trace_ok` user is shown NO warning while a `severe` user is correctly excluded — inconsistent safety surface; no test exercises this.
- **Fix:** Add a DB-backed test (recipe with `Peanut Butter` ingredient, no RecipeAllergen row, `trace_ok` peanut user → expect a warning, fails today); fix `get_warnings` to derive allergens via `ingredient_contains_allergen`, mirroring `_recipe_has_allergen`.

### TQ-9 (Low) — Shopping-list aggregation: weight/volume unit with `metric_equivalent=None` falls into a count bucket — untested
- **File:** `src/meal_planner/shopping_list.py:116-129`
- **Evidence:** Conversion only fires when `unit_type in {weight,volume}` AND `metric_equivalent is not None`; otherwise a weight unit with NULL `metric_equivalent` is treated as a labeled count, fragmenting a real weight line. New fixtures always supply `metric_equivalent`, so this dirty-data branch is never exercised (module at 50%).
- **Fix:** Add a test with two recipes sharing an ingredient on a weight unit with `metric_equivalent=None`; assert the intended behaviour and document the contract.

### TQ-10 (Low) — `auth_headers` fixture swallows login failure by returning `{}`
- **File:** `tests/integration/conftest.py`
- **Evidence:** When `/auth/login` is not 200, the fixture yields `{}` instead of failing fast. Tests like `test_password_change_revokes_old_tokens` then send no Authorization header; the asserted 401 could be produced by the missing token rather than revocation, masking a regression.
- **Fix:** Assert `response.status_code == 200` and `'access_token' in body` in the fixture so a broken login is an immediate attributable failure.

---

## Prior fixes validation

All merged fixes from the prior remediation were re-verified. They **hold** except where a fix does not reach a specific caller/data-shape (F1, F2/F4) or where pre-existing gaps remain that the prior phase did not target.

| Area | Merged fix | Status |
|---|---|---|
| Functionality | Scraper resume (checkpoint + `scrape_all`): full cycle, no drops/dupes, checkpoint cleared only on full completion | **Holds** (verified end-to-end) |
| Functionality | Seedable RNG (`planner._rng`): deterministic per seed | **Holds** |
| Functionality | Cost cache caches base per-100g, not scaled cost (no leakage) | **Holds** |
| Functionality | Shopping-list unit-aware aggregation (200g+1kg→1.2kg; counts per-label) | **Holds** |
| Functionality | Allergen population + exclusion-before-inclusion detection | **Holds for false-positives** (see Domain for false-negative gaps) |
| Functionality | Nutrition plan from actual candidates (API path) | **Holds for API; NOT for CLI** (F1) |
| Functionality | `x0`/optional parsing | **Holds for no-parens form only** (F2/F4 break the `Name (NNNg) x0` form) |
| Architecture/DB | Shared engine (`configure_database` + module-level engine/factory) | **Holds** |
| Architecture/DB | Filtered pagination count (`count_filtered_recipes` reuses `_apply_recipe_filters`) | **Holds for the standard branch** (allergen/search branches bypass it — ARCH-01/02) |
| Architecture/DB | Categories route ordering; `safe_recipes` registered before `recipes` | **Holds** |
| Architecture/DB | Merged `model_config` (single `ConfigDict` on response schemas) | **Holds** (filter/pagination schemas still use raw dict — ARCH-09, cosmetic) |
| Security | Default-JWT-secret refusal, short-secret + wildcard-CORS validators | **Holds** |
| Security | HF-origin CORS derivation + security headers + SPA path-traversal containment | **Holds** |
| Security | `get_current_user` token_version + is_active recheck; logout/refresh/verify bump version | **Holds** (`get_current_user_optional` not hardened — SEC-3) |
| Security | Trusted-proxy rate-limiting gating (default ignores XFF) | **Holds** |
| Security | `safe_error_detail` leak guard | **Holds in remediated files** (multi_week + favorites_service missed — SEC-1/SEC-2) |
| UX/UI | `VITE_API_URL`, Keyboard+Touch sensors, draggable aria-label, mobile bottom-sheet, `mapBackendCategoryName`, NutritionDashboard memo deps | **All hold** (standalone `MealPlannerBoard` could re-regress — FE-07) |
| Tests | 718 backend pass, 132 frontend pass, type-check clean | **Holds** (but default pytest fails the 80% gate — TQ-1) |

---

## Ranked fix backlog

Effort: S (localized, <1h) · M (multi-file or test-heavy) · L (cross-cutting / data + schema).

| # | Issue | Dimension | Severity | Effort | Risk |
|---|---|---|---|---|---|
| 1 | ALG-1 Dairy false negatives (named cheeses) | Domain | Critical | S | Low |
| 2 | ALG-2 Gluten false negatives (Italian breads/pastas) | Domain | Critical | S | Low |
| 3 | SEED-1 Backfill `recipe_allergens` for all seeded recipes | Domain/Data | Critical | M | Low |
| 4 | ALG-3 Plural-aware single-token matching | Domain | Critical | S | Medium |
| 5 | F1 CLI `meal-plan --with-nutrition` → use merged candidate builder | Functionality | High | S | Low |
| 6 | SEC-1 multi_week leak → `safe_error_detail` | Security | Medium* | S | Low |
| 7 | SEC-2 FavoritesService IntegrityError leak | Security | Medium* | S | Low |
| 8 | ALG-4 Fish false negatives (monkfish, etc.) | Domain | High | S | Low |
| 9 | ALG-5 Tree-nut false negatives (pine kernel, etc.) | Domain | High | S | Low |
| 10 | F2/F4 Parens-first `x0`/`xN`/prep parsing | Functionality | High | M | Medium |
| 11 | TQ-1/TQ-2 nutrition_scraper extraction + tests → lift coverage | Tests | High | M | Low |
| 12 | FE-01 Consolidate the two nutrition-goal stores | UX/Frontend | High | M | Medium |
| 13 | ARCH-02 Fix list_recipes pagination total (allergen + search) | Architecture | High | M | Medium |
| 14 | ARCH-01 `count_safe_recipes()` to avoid 10000-row count | Architecture | High | M | Low |
| 15 | ARCH-03 Eager-load ingredients in MealPlanner scoring (N+1) | Architecture | High | M | Medium |
| 16 | SEED-2 Normalise ingredient names at ingest + backfill | Domain/Data | High | L | Medium |
| 17 | TQ-3/TQ-4 Categoriser collision tests + word-boundary fix | Tests/Domain | Medium | M | Medium |
| 18 | F3 Cost categoriser specificity ordering | Functionality | Medium | M | Low |
| 19 | ARCH-04 Eager-load RecipeIngredient.ingredient/.unit | Architecture | Medium | S | Low |
| 20 | ARCH-05 Global HTTPException handler | Architecture | Medium | S | Low |
| 21 | FE-02 RecipeList real icon elements | UX/Frontend | Medium | S | Low |
| 22 | FE-03 Debounce PlannerSidebar search | UX/Frontend | Medium | S | Low |
| 23 | FE-06 401 handler via auth boundary, clear persisted store | UX/Frontend | Medium | M | Medium |
| 24 | TQ-7 Integration test for scraper resume loop | Tests | Medium | M | Low |
| 25 | TQ-8 get_warnings name-based + test | Tests/Domain | Medium | M | Medium |
| 26 | ARCH-06 API versioning + typed generate responses | Architecture | Medium | M | Medium |
| 27 | SEED-3 Backfill ingredient category + is_allergen | Domain/Data | Medium | M | Low |
| 28 | COST-1 Seed IngredientPrice + pack-size rounding | Domain/Cost | Medium | L | Low |
| 29 | SEC-3 Harden get_current_user_optional | Security | Low | S | Low |
| 30 | SEC-4 JWT storage / CSP | Security | Low | L | Medium |
| 31 | FE-04 Remove `recipe: any` | UX/Frontend | Low | S | Low |
| 32 | FE-1 MacroBreakdown divide-by-zero guard | UX/Frontend | Low | S | Low |
| 33 | F5 Remove/redirect use_nutrition_data dead branch | Functionality | Low | S | Low |
| 34 | F6 Resume stats total | Functionality | Low | S | Low |
| 35 | FE-05/07/08/09 Planner export, dead board wrapper, sheet a11y, Goals modal | UX/Frontend | Low | M | Low |
| 36 | ARCH-07/08/09 Dead schema, FK indexes, ConfigDict normalise | Architecture | Low | M | Low |
| 37 | COST-2 COMMON_WEIGHTS guard | Domain/Cost | Low | S | Medium |
| 38 | PLAN-1 Prefer NutritionMealPlanner for labelled plans | Domain | Low | M | Low |
| 39 | TQ-5/6/9/10 Test-quality fixes | Tests | Low | S–M | Low |

_*SEC-1/SEC-2 are Medium severity but are autopilot-eligible: clear, localized, single-line, behaviour-preserving for legitimate clients._

---

## Autopilot fixes (high-confidence, low-risk, applied automatically)

Selected for being clear, localized, testable, and non-behaviour-changing for users. Applied in a separate step:

1. **F1** — `src/cli.py:477-490`: replace the inline build loop with `meal_plan_dict = planner.generate_weekly_meal_plan_from_candidates(candidates)`. Reuses the verified merged method.
2. **ALG-1** — `src/utils/food_taxonomy.py`: extend the `dairy` include list with named cheeses (purely additive; false-positive guards re-checked).
3. **ALG-2** — `src/utils/food_taxonomy.py`: extend the `gluten` include list with Italian breads/pastas/freekeh (additive).
4. **ALG-4** — `src/utils/food_taxonomy.py`: extend the `fish` include list (additive).
5. **ALG-5** — `src/utils/food_taxonomy.py`: extend the `tree nuts` include list (additive).
6. **SEC-1** — `src/api/routers/multi_week.py:190,338`: import and use `safe_error_detail`.
7. **SEC-2** — `src/api/services/favorites_service.py:118`: generic detail + server-side log.

**Deliberately NOT auto-applied:** ALG-3 (plural regex change risks new false positives — needs a full guard re-run), F2/F4 (parsing refactor changes stored quantities), F3/TQ-3/TQ-4 (categoriser reorder changes cost output), all ARCH N+1/pagination fixes (cross-cutting query changes), FE-01 (store consolidation), SEED backfills (data migrations), anything requiring schema/migration changes.

_Note: this report and the autopilot fixes were generated by the review workflow; the workflow harness applies the autopilot subset separately. The body of this report records all findings regardless of autopilot status._
