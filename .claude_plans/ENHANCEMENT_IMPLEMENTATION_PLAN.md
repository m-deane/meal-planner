# Meal Planner Enhancement Implementation Plan

## Executive Summary

This plan enhances the Gousto Recipe Database Scraper with a **FastAPI REST layer**, **React frontend**, and **advanced meal planning features**. Implementation builds incrementally upon existing SQLAlchemy ORM models, Pydantic validation, and meal planning modules.

**Estimated New Code**: ~95 files across all phases

---

## Phase 1: REST API Layer (FastAPI)

### 1.1 New Dependencies

Add to `requirements.txt`:
```
# API Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Testing
httpx==0.26.0
pytest-asyncio==0.23.3
```

### 1.2 Directory Structure

```
src/api/
    __init__.py
    main.py                    # FastAPI app, CORS, middleware
    config.py                  # API-specific configuration
    dependencies.py            # Dependency injection (db, auth)

    routers/
        __init__.py
        recipes.py             # /api/v1/recipes
        meal_plans.py          # /api/v1/meal-plans
        shopping_lists.py      # /api/v1/shopping-lists
        categories.py          # /api/v1/categories
        dietary_tags.py        # /api/v1/dietary-tags
        allergens.py           # /api/v1/allergens
        auth.py                # /api/v1/auth
        users.py               # /api/v1/users (Phase 3 prep)

    schemas/
        __init__.py
        recipe.py              # Recipe request/response schemas
        meal_plan.py           # Meal plan schemas
        shopping_list.py       # Shopping list schemas
        nutrition.py           # Nutrition schemas
        pagination.py          # Pagination, filtering, sorting
        auth.py                # Auth schemas (tokens, credentials)
        user.py                # User schemas
        common.py              # Shared schemas (errors, responses)

    services/
        __init__.py
        recipe_service.py      # Business logic for recipes
        meal_plan_service.py   # Meal plan generation
        shopping_list_service.py
        auth_service.py        # Authentication logic

    middleware/
        __init__.py
        error_handler.py       # Global exception handling
        logging.py             # Request/response logging
        rate_limit.py          # API rate limiting
```

### 1.3 API Endpoints

#### Recipes Router
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/recipes` | List with pagination/filtering | Optional |
| GET | `/api/v1/recipes/{id}` | Get by ID | Optional |
| GET | `/api/v1/recipes/slug/{slug}` | Get by slug | Optional |
| GET | `/api/v1/recipes/search` | Search by name | Optional |
| GET | `/api/v1/recipes/{id}/nutrition` | Get nutrition | Optional |
| GET | `/api/v1/recipes/{id}/ingredients` | Get ingredients | Optional |

**Query Parameters**:
- `page`, `page_size` (pagination)
- `category`, `dietary_tag`, `exclude_allergens` (filtering)
- `max_cooking_time`, `difficulty`
- `min_protein`, `max_carbs`, `min_calories`, `max_calories`
- `sort_by`, `sort_order`

#### Meal Plans Router
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/meal-plans/generate` | Generate plan | Optional |
| POST | `/api/v1/meal-plans/generate-nutrition` | Generate with constraints | Optional |
| GET | `/api/v1/meal-plans/{id}` | Get saved plan | Required |
| PUT | `/api/v1/meal-plans/{id}` | Update plan | Required |
| DELETE | `/api/v1/meal-plans/{id}` | Delete plan | Required |

#### Shopping Lists Router
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/shopping-lists/generate` | From recipe IDs | Optional |
| POST | `/api/v1/shopping-lists/from-meal-plan/{id}` | From meal plan | Optional |
| GET | `/api/v1/shopping-lists/{id}` | Get saved list | Required |

### 1.4 Key Schemas

```python
# pagination.py
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

# recipe.py
class RecipeResponse(BaseModel):
    id: int
    gousto_id: str
    slug: str
    name: str
    description: Optional[str]
    cooking_time_minutes: Optional[int]
    servings: int
    difficulty: Optional[str]
    source_url: str
    categories: List[CategoryResponse]
    dietary_tags: List[str]
    allergens: List[str]
    images: List[ImageResponse]
    nutrition: Optional[NutritionResponse]

    class Config:
        from_attributes = True

# meal_plan.py
class MealPlanGenerateRequest(BaseModel):
    days: int = 7
    include_breakfast: bool = True
    include_lunch: bool = True
    include_dinner: bool = True
    min_protein_g: Optional[float] = None
    max_carbs_g: Optional[float] = None
    exclude_allergens: List[str] = []
    dietary_preferences: List[str] = []
```

### 1.5 Database Changes

```python
# Add to src/database/models.py
class APIKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    key_hash = Column(String(255), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
```

### 1.6 CLI Addition

```python
# Add to src/cli.py
@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8000)
@click.option('--reload', is_flag=True)
def serve(host, port, reload):
    """Run the API server."""
    import uvicorn
    uvicorn.run("src.api.main:app", host=host, port=port, reload=reload)
```

### 1.7 Implementation Steps

1. Create `src/api/` directory structure
2. Implement `main.py` with FastAPI app factory, CORS, middleware
3. Implement `config.py` extending existing Pydantic settings
4. Implement `dependencies.py` (database session, auth)
5. Implement schemas: `common.py` → `pagination.py` → `recipe.py` → `meal_plan.py`
6. Implement routers: `recipes.py` → `categories.py` → `meal_plans.py` → `shopping_lists.py` → `auth.py`
7. Add middleware (error handling, logging, rate limiting)
8. Add `serve` command to CLI
9. Write tests in `tests/api/`

### 1.8 Testing

```
tests/api/
    __init__.py
    conftest.py                # TestClient, auth fixtures
    test_recipes.py
    test_meal_plans.py
    test_shopping_lists.py
    test_auth.py
    test_pagination.py
```

---

## Phase 2: React Frontend

### 2.1 Technology Stack

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "axios": "^1.6.0",
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "recharts": "^2.10.0",
    "tailwindcss": "^3.4.0",
    "@headlessui/react": "^1.7.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "@testing-library/react": "^14.1.0",
    "vitest": "^1.1.0"
  }
}
```

### 2.2 Directory Structure

```
frontend/
    package.json
    vite.config.ts
    tsconfig.json
    tailwind.config.js
    index.html

    src/
        main.tsx
        App.tsx

        api/
            client.ts              # Axios instance
            recipes.ts
            mealPlans.ts
            shoppingLists.ts
            auth.ts

        components/
            common/
                Button.tsx
                Card.tsx
                Modal.tsx
                Spinner.tsx
                Pagination.tsx
                FilterPanel.tsx
                SearchBar.tsx

            recipes/
                RecipeCard.tsx
                RecipeList.tsx
                RecipeDetail.tsx
                RecipeFilters.tsx
                NutritionBadge.tsx
                IngredientList.tsx
                InstructionSteps.tsx

            meal-planner/
                MealPlannerBoard.tsx    # Drag-and-drop board
                DayColumn.tsx
                MealSlot.tsx
                DraggableRecipe.tsx
                PlannerSidebar.tsx

            nutrition/
                NutritionDashboard.tsx
                MacroChart.tsx          # Pie chart
                WeeklyTrends.tsx        # Line chart
                DailyBreakdown.tsx      # Bar chart
                NutritionSummary.tsx

            shopping-list/
                ShoppingList.tsx
                CategorySection.tsx
                ShoppingItem.tsx
                ExportOptions.tsx

        pages/
            HomePage.tsx
            RecipeBrowserPage.tsx
            RecipeDetailPage.tsx
            MealPlannerPage.tsx
            NutritionDashboardPage.tsx
            ShoppingListPage.tsx
            LoginPage.tsx
            ProfilePage.tsx

        hooks/
            useRecipes.ts
            useMealPlan.ts
            useShoppingList.ts
            useAuth.ts
            useFilters.ts

        store/
            mealPlanStore.ts           # Zustand
            userStore.ts

        types/
            recipe.ts
            mealPlan.ts
            nutrition.ts
            api.ts

        utils/
            formatting.ts
            nutrition.ts
            validation.ts

        styles/
            globals.css
```

### 2.3 Key Components

#### Recipe Browser
- Grid/list view toggle
- Multi-select filters (cuisine, dietary, difficulty)
- Nutrition range sliders
- Debounced search
- Infinite scroll
- Allergen exclusion

#### Interactive Meal Planner
Using `@dnd-kit`:
- 7 day columns (Mon-Sun)
- 3 meal slots per day
- Recipe search sidebar
- Drag from sidebar to slots
- Auto-save to localStorage + API

**Zustand Store**:
```typescript
interface MealPlanState {
  days: {
    [day: string]: {
      breakfast?: Recipe;
      lunch?: Recipe;
      dinner?: Recipe;
    };
  };
  addRecipe: (day: string, mealType: string, recipe: Recipe) => void;
  removeRecipe: (day: string, mealType: string) => void;
  moveRecipe: (from: Position, to: Position) => void;
  generatePlan: (options: GenerateOptions) => Promise<void>;
  clearPlan: () => void;
}
```

#### Nutrition Dashboard
Using Recharts:
- **Macro Distribution**: Pie chart (protein/carbs/fat)
- **Weekly Trends**: Line chart (calories over 7 days)
- **Daily Breakdown**: Stacked bar (each meal's contribution)
- **Summary Cards**: Total calories, avg protein, avg carbs

#### Shopping List
- Auto-generate from meal plan
- Ingredient aggregation
- Category grouping
- Checkbox persistence
- Export to text/PDF

### 2.4 API Client

```typescript
// api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### 2.5 React Query Hooks

```typescript
// hooks/useRecipes.ts
export function useRecipes(filters: RecipeFilters) {
  return useInfiniteQuery({
    queryKey: ['recipes', filters],
    queryFn: ({ pageParam = 1 }) => getRecipes({ ...filters, page: pageParam }),
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  });
}
```

### 2.6 Implementation Steps

1. Initialize Vite + React + TypeScript in `/frontend`
2. Configure Tailwind CSS, ESLint, Prettier
3. Set up API client with interceptors
4. Configure React Query provider
5. Set up React Router
6. Build common components (Button, Card, Spinner)
7. Build recipe components (Card, List, Filters)
8. Build RecipeBrowserPage and RecipeDetailPage
9. Build Zustand store for meal plan
10. Build MealPlannerBoard with drag-and-drop
11. Build nutrition chart components
12. Build NutritionDashboardPage
13. Build shopping list components
14. Add loading states, error boundaries
15. Responsive design and accessibility

---

## Phase 3: Advanced Features

### 3.1 Database Schema Additions

```python
# Add to src/database/models.py

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    preferences = relationship('UserPreference', back_populates='user', uselist=False)
    favorite_recipes = relationship('FavoriteRecipe', back_populates='user')
    saved_meal_plans = relationship('SavedMealPlan', back_populates='user')
    allergen_profile = relationship('UserAllergen', back_populates='user')


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    default_servings = Column(Integer, default=2)
    calorie_target = Column(Integer)
    protein_target_g = Column(Numeric(10, 2))
    carb_limit_g = Column(Numeric(10, 2))
    fat_limit_g = Column(Numeric(10, 2))
    preferred_cuisines = Column(Text)  # JSON
    excluded_ingredients = Column(Text)  # JSON

    user = relationship('User', back_populates='preferences')


class FavoriteRecipe(Base):
    __tablename__ = 'favorite_recipes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('user_id', 'recipe_id'),)

    user = relationship('User', back_populates='favorite_recipes')
    recipe = relationship('Recipe')


class SavedMealPlan(Base):
    __tablename__ = 'saved_meal_plans'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    plan_data = Column(Text, nullable=False)  # JSON
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='saved_meal_plans')


class UserAllergen(Base):
    __tablename__ = 'user_allergens'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    allergen_id = Column(Integer, ForeignKey('allergens.id'), primary_key=True)
    severity = Column(String(50), default='avoid')  # 'avoid', 'severe', 'trace_ok'

    user = relationship('User', back_populates='allergen_profile')
    allergen = relationship('Allergen')


class IngredientPrice(Base):
    __tablename__ = 'ingredient_prices'

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'))
    store = Column(String(100), default='average')
    currency = Column(String(3), default='GBP')
    last_updated = Column(DateTime, default=datetime.utcnow)

    ingredient = relationship('Ingredient')
    unit = relationship('Unit')
```

### 3.2 New Backend Files

```
src/api/routers/
    users.py                    # User profile management
    favorites.py                # Favorite recipes
    preferences.py              # User preferences

src/api/services/
    user_service.py
    favorites_service.py
    variety_service.py          # Variety enforcement
    cost_service.py             # Cost estimation

src/meal_planner/
    multi_week_planner.py       # Multi-week with variety
    allergen_filter.py          # Advanced allergen filtering
    cost_estimator.py           # Shopping cost estimation
```

### 3.3 New Frontend Files

```
frontend/src/
    pages/
        FavoritesPage.tsx
        PreferencesPage.tsx
        MultiWeekPlannerPage.tsx

    components/
        user/
            ProfileForm.tsx
            AllergenSelector.tsx
            PreferencesForm.tsx

        favorites/
            FavoriteButton.tsx
            FavoritesList.tsx

        planner/
            MultiWeekView.tsx
            VarietyIndicator.tsx
            CostEstimate.tsx
            AllergenWarning.tsx
```

### 3.4 Feature Implementations

#### Multi-Week Planning with Variety

```python
# src/meal_planner/multi_week_planner.py
class MultiWeekPlanner:
    def __init__(self, session: Session, weeks: int = 4):
        self.session = session
        self.weeks = weeks
        self.variety_config = {
            'min_days_between_repeat': 7,
            'max_same_cuisine_per_week': 3,
            'protein_rotation': True,
        }

    def generate_multi_week_plan(
        self,
        preferences: UserPreference,
        exclude_recent: List[int] = None,
    ) -> Dict[int, Dict[str, Dict[str, Recipe]]]:
        """Generate multi-week plan with variety enforcement."""

    def _calculate_variety_score(self, plan: Dict) -> float:
        """Score plan based on ingredient/cuisine variety."""

    def _enforce_variety_constraints(
        self,
        candidates: List[Recipe],
        history: List[Recipe]
    ) -> List[Recipe]:
        """Filter based on variety rules."""
```

#### Allergen Filtering

```python
# src/meal_planner/allergen_filter.py
class AllergenFilter:
    def __init__(self, session: Session, user_allergens: List[UserAllergen]):
        self.session = session
        self.allergens = {ua.allergen_id: ua.severity for ua in user_allergens}

    def filter_recipes(self, recipes: List[Recipe]) -> List[Recipe]:
        """Remove recipes containing user's allergens."""

    def get_warnings(self, recipe: Recipe) -> List[AllergenWarning]:
        """Return warnings based on severity."""

    def suggest_substitutions(self, recipe: Recipe) -> List[Substitution]:
        """Suggest ingredient substitutions."""
```

#### Cost Estimation

```python
# src/meal_planner/cost_estimator.py
class CostEstimator:
    def __init__(self, session: Session):
        self.session = session

    def estimate_recipe_cost(self, recipe: Recipe, servings: int = 2) -> Decimal:
        """Estimate cost for a single recipe."""

    def estimate_meal_plan_cost(self, meal_plan: Dict) -> MealPlanCostBreakdown:
        """Estimate total shopping cost."""

    def get_budget_alternatives(
        self,
        recipe: Recipe,
        max_budget: Decimal
    ) -> List[Recipe]:
        """Suggest cheaper alternatives."""
```

### 3.5 Implementation Steps

1. Create migration script for new tables
2. Add seed data for ingredient prices
3. Implement User model and authentication
4. Implement preferences CRUD
5. Implement allergen profile management
6. Implement favorites backend and frontend
7. Implement allergen filter and warning system
8. Implement multi-week planner with variety
9. Implement cost estimator
10. Build frontend components for all features
11. Write comprehensive tests

---

## Configuration Updates

Add to `src/config.py`:

```python
class Config(BaseSettings):
    # ... existing ...

    # API (Phase 1)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_debug: bool = Field(default=False)
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    jwt_secret: str = Field(default="change-me-in-production")
    jwt_expire_minutes: int = Field(default=60)

    # Frontend (Phase 2)
    frontend_url: str = Field(default="http://localhost:5173")

    # Advanced (Phase 3)
    enable_cost_estimation: bool = Field(default=True)
    default_currency: str = Field(default="GBP")
    variety_enforcement_days: int = Field(default=7)
```

---

## Summary

| Phase | New Files | Key Deliverables |
|-------|-----------|------------------|
| **Phase 1** | ~25 | REST API, OpenAPI docs, JWT auth |
| **Phase 2** | ~50 | React app, drag-drop planner, nutrition charts |
| **Phase 3** | ~20 | User accounts, favorites, variety, cost estimation |
| **Total** | ~95 | Full-stack meal planning application |

### Critical Integration Points

1. **`src/database/models.py`** - Extend for user tables (Phase 3)
2. **`src/database/queries.py`** - `RecipeQuery` used by API routers
3. **`src/meal_planner/planner.py`** - Wrapped by API service
4. **`src/meal_planner/shopping_list.py`** - Exposed via API
5. **`src/config.py`** - Extend for all phases
