# Gousto Meal Planner — Next-Phase Functionality

This document captures the roadmap for the next development phase. It builds on
the fixes delivered in the multi-dimensional review (see commit history and
`.claude_plans/`), which closed the critical correctness, security, and
domain-validity gaps. The items below are the high-value features and
investments that should come next, grouped by theme and ordered roughly by
value-to-effort.

> **Context:** The review uncovered a single systemic root cause — the scraper
> populated recipes/ingredients/nutrition but **not** allergens, ingredient
> categories, or prices. That ingestion gap has now been closed (allergens and
> categories are derived from a shared food taxonomy during scraping). Several
> next-phase items deepen that data model rather than work around it.

---

## 1. Account-bound meal plans (High value · Medium effort)

The `saved_meal_plans` table and `User.saved_meal_plans` relationship already
exist but are unused; the planner persists only to browser `localStorage`.

- Add `POST/GET/PUT/DELETE /meal-plans` endpoints backed by `SavedMealPlan`,
  scoped to the authenticated user (`SavedMealPlan.user_id == current_user`).
  **Security note:** enforce ownership on every by-id route to avoid IDOR.
- Wire the frontend planner to load/save server-side; surface a "My plans" list.
- Move the generation/shopping/cost endpoints behind authentication once plans
  are account-bound (they are currently public but protected by an
  un-spoofable rate limiter and no longer leak internal errors).

## 2. Allergen safety: `contains` vs `may_contain` (High value · Medium effort)

Allergen filtering is now functional (table + ingredient-name analysis), but it
cannot yet distinguish a listed ingredient from a trace/cross-contamination
risk, so the `trace_ok` severity is coarse.

- Add a `may_contain: bool` column to `recipe_allergens` and populate it
  (definite "contains" when the allergen is a listed ingredient; "may contain"
  for advisory statements).
- Make `trace_ok` exclude definite-contains recipes while permitting genuine
  trace cases.
- Expand the `food_taxonomy` lexicon with regional/processed terms and add a
  curated test corpus of real Gousto ingredient strings to measure
  precision/recall of allergen detection.

## 3. Real ingredient pricing & pantry tracking (High value · Large effort)

Cost estimation now differentiates by category (and no longer flattens every
ingredient to a flat rate), but it still relies on category averages rather than
real per-ingredient prices.

- Seed/ingest a real price reference into `ingredient_prices` (a curated CSV or
  a supermarket price feed), keyed by ingredient.
- Add pack-size rounding (you buy a whole onion / a 400g can, not 137g) and a
  configurable waste/trim factor for realistic basket totals.
- **Pantry/inventory tracking:** let users record staples they already own and
  subtract them from generated shopping lists. The new unit-conversion layer in
  `shopping_list.py` is the prerequisite for this.

## 4. Personalised nutrition targets (Medium value · Medium effort)

Nutrition goals are currently fixed defaults in a frontend-only store.

- Compute TDEE and macro targets from `UserPreference` (sex, weight, height,
  activity level, goal) and persist them server-side.
- Reconcile the two competing goal stores (`mealPlanStore.nutritionGoals` vs
  `nutritionGoalsStore`) into a single source of truth.
- Feed onboarding preferences (dietary tags, allergens, max cooking time) into
  the default recipe filters so the onboarding flow is no longer decorative.

## 5. Production hardening (Medium value · Medium effort)

- **Database:** move production to PostgreSQL (the connection layer already
  supports it); use `JSONB` for `saved_meal_plans.plan_data` and the
  `user_preferences` JSON columns; add the FK indexes noted in the review.
- **Auth:** implement real refresh-token rotation (the access-token lifetime is
  long); the `logout`/`refresh`/`verify` endpoints and `token_version`
  revocation are now in place to build on.
- **Password reset:** implement the backend `/auth/password-reset/*` endpoints
  (the frontend already calls them) with an email provider, or remove the
  unused client functions.
- **Rate limiting:** back the limiter with Redis so it works across workers and
  survives restarts (it is currently in-memory per-process); set
  `TRUSTED_PROXIES` in the deployment environment.
- **Secrets/CORS:** set a strong `JWT_SECRET` and explicit `CORS_EXTRA_ORIGINS`
  in every deployment (the app now refuses to boot in production with the
  default secret and rejects wildcard CORS with credentials).
- Add a Content-Security-Policy header (baseline `nosniff`/frame-deny/referrer
  headers are now set).

## 6. API & frontend polish (Medium value · Medium effort)

- **API versioning:** mount routers under `/api/v1` and type the remaining
  `response_model=dict` endpoints with the existing Pydantic schemas.
- **Router consolidation:** merge `safe_recipes` into `recipes` (single
  serializer, no shared-prefix fragility).
- **Token storage:** move the JWT from `localStorage` to an httpOnly cookie (or
  in-memory + short TTL) with CSRF protection to reduce XSS exposure.
- **Meal-plan export:** use the backend markdown/PDF export endpoints instead of
  dumping raw Zustand JSON.
- **Accessibility follow-ups:** replace the hand-rolled `GeneratePlanModal` with
  the shared `Modal` (focus trap + Escape), and remove nested interactive
  controls inside `role="button"` recipe cards. (Keyboard + touch drag-and-drop
  is now supported.)

## 7. New capabilities (Exploratory · Large effort)

- **Recipe recommendations:** content-based (ingredient/nutrition similarity) or
  collaborative (favorites-driven) suggestions.
- **PWA / offline:** meal plans and shopping lists are ideal offline-first
  surfaces; add a service worker and installable manifest.
- **Plan sharing:** shareable read-only links for a saved meal plan.
- **Smarter variety scoring:** detect the dominant protein by quantity rather
  than first-keyword match, and resolve cuisine ambiguity via recipe categories.

---

## Testing investments

The 80% coverage gate is not yet met (it was already unmet before this phase).
Highest-value gaps to close next:

- `src/scrapers/nutrition_scraper.py` (currently untested) — the single largest
  uncovered module.
- Frontend hooks, pages, and API modules (currently near-zero coverage); start
  with the pure `utils/*` functions and `authStore`/`ProtectedRoute`.
- Integration tests for the generate-meal-plan → shopping-list → cost flow.

---

_Last updated as part of the post-review remediation phase._
