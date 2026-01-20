# Schema Quick Reference Guide

Quick copy-paste examples for common schema usage patterns.

## Import Patterns

```python
# Common responses
from src.api.schemas import ErrorResponse, SuccessResponse, MessageResponse

# Pagination
from src.api.schemas import PaginationParams, PaginatedResponse

# Recipe schemas
from src.api.schemas import (
    RecipeResponse,
    RecipeListItem,
    RecipeFilters,
    NutritionFilters,
    IngredientResponse,
)

# Meal planning
from src.api.schemas import (
    MealPlanGenerateRequest,
    MealPlanResponse,
    NutritionConstraints,
    MealPreferences,
)

# Shopping lists
from src.api.schemas import (
    ShoppingListGenerateRequest,
    ShoppingListResponse,
    ShoppingItem,
)

# Auth
from src.api.schemas import (
    LoginRequest,
    UserCreate,
    TokenResponse,
    UserResponse,
)
```

## FastAPI Endpoint Examples

### List Endpoint with Pagination

```python
from fastapi import APIRouter, Depends
from src.api.schemas import PaginationParams, PaginatedResponse, RecipeListItem

router = APIRouter()

@router.get("/recipes", response_model=PaginatedResponse[RecipeListItem])
async def list_recipes(
    pagination: PaginationParams = Depends(),
):
    recipes = get_recipes(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total = count_recipes()

    return PaginatedResponse[RecipeListItem].create(
        items=recipes,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )
```

### Detail Endpoint

```python
from fastapi import APIRouter, HTTPException
from src.api.schemas import RecipeResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_recipe(recipe_id: int):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )
    return RecipeResponse.from_orm(recipe)
```

### Create Endpoint

```python
from fastapi import APIRouter, status
from src.api.schemas import UserCreate, UserResponse, SuccessResponse

router = APIRouter()

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(user_data: UserCreate):
    user = create_user_in_db(user_data)
    return UserResponse.from_orm(user)
```

### Filter Endpoint

```python
from fastapi import APIRouter, Query
from src.api.schemas import RecipeFilters, RecipeListItem, PaginatedResponse

router = APIRouter()

@router.get("/recipes/search", response_model=PaginatedResponse[RecipeListItem])
async def search_recipes(
    category_slugs: list[str] | None = Query(None),
    max_cooking_time: int | None = None,
    min_protein_g: float | None = None,
    max_calories: int | None = None,
):
    filters = RecipeFilters(
        category_slugs=category_slugs,
        max_cooking_time=max_cooking_time,
        nutrition=NutritionFilters(
            min_protein_g=min_protein_g,
            max_calories=max_calories
        ) if min_protein_g or max_calories else None
    )

    recipes = search_recipes_with_filters(filters)
    return recipes
```

### Authentication Endpoint

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.schemas import TokenResponse, LoginRequest

router = APIRouter()

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600
    )
```

## ORM Conversion Examples

### Single Object

```python
from src.database.models import Recipe
from src.api.schemas import RecipeResponse

# From ORM to schema
recipe_orm = session.query(Recipe).first()
recipe_response = RecipeResponse.from_orm(recipe_orm)

# To dict
recipe_dict = recipe_response.model_dump()

# To JSON
recipe_json = recipe_response.model_dump_json()
```

### List of Objects

```python
from src.database.models import Recipe
from src.api.schemas import RecipeListItem

recipes_orm = session.query(Recipe).limit(10).all()
recipes_response = [
    RecipeListItem.from_orm(recipe)
    for recipe in recipes_orm
]
```

### With Pagination

```python
from src.api.schemas import PaginatedResponse, RecipeListItem

# Get data
recipes = session.query(Recipe).offset(20).limit(20).all()
total = session.query(Recipe).count()

# Create response
response = PaginatedResponse[RecipeListItem].create(
    items=[RecipeListItem.from_orm(r) for r in recipes],
    total=total,
    page=2,
    page_size=20
)
```

## Validation Examples

### Custom Validation

```python
from pydantic import BaseModel, Field, field_validator

class MyRequest(BaseModel):
    min_value: int = Field(..., ge=0)
    max_value: int = Field(..., ge=0)

    @field_validator('max_value')
    @classmethod
    def validate_max_value(cls, v: int, info) -> int:
        if v < info.data.get('min_value', 0):
            raise ValueError('max_value must be >= min_value')
        return v
```

### Complex Filters

```python
from src.api.schemas import RecipeFilters, NutritionFilters

# High protein, low carb recipes
filters = RecipeFilters(
    dietary_tag_slugs=["keto", "low-carb"],
    exclude_allergen_names=["dairy", "nuts"],
    max_cooking_time=30,
    nutrition=NutritionFilters(
        min_protein_g=30,
        max_carbs_g=20,
        max_calories=500
    )
)
```

### Meal Plan Request

```python
from datetime import date
from src.api.schemas import (
    MealPlanGenerateRequest,
    MealPreferences,
    NutritionConstraints
)

request = MealPlanGenerateRequest(
    days=7,
    start_date=date.today(),
    meal_preferences=MealPreferences(
        include_breakfast=True,
        include_lunch=True,
        include_dinner=True,
        breakfast_calories_pct=25,
        lunch_calories_pct=35,
        dinner_calories_pct=40
    ),
    nutrition_constraints=NutritionConstraints(
        target_calories=2000,
        min_protein_g=100,
        max_carbs_g=250,
        max_sugar_g=50
    ),
    dietary_tag_slugs=["vegetarian"],
    exclude_allergen_names=["nuts", "shellfish"],
    avoid_duplicate_recipes=True,
    max_cooking_time=45
)
```

## Error Handling

### Standard Error Response

```python
from fastapi import HTTPException
from src.api.schemas import ErrorResponse

# Return 404
raise HTTPException(
    status_code=404,
    detail=ErrorResponse(
        error="NotFound",
        message="Recipe not found",
        details={"recipe_id": 123}
    ).model_dump()
)

# Return 400
raise HTTPException(
    status_code=400,
    detail=ErrorResponse(
        error="ValidationError",
        message="Invalid input parameters",
        details={"field": "email", "reason": "Invalid format"}
    ).model_dump()
)
```

### Success Response

```python
from src.api.schemas import SuccessResponse

return SuccessResponse(
    message="Recipe created successfully",
    data={"recipe_id": 123}
)
```

## Testing Examples

### Schema Validation Test

```python
import pytest
from pydantic import ValidationError
from src.api.schemas import RecipeFilters

def test_recipe_filters_validation():
    # Valid filters
    filters = RecipeFilters(
        category_slugs=["italian"],
        max_cooking_time=30
    )
    assert filters.max_cooking_time == 30

    # Invalid range should raise error
    with pytest.raises(ValidationError):
        RecipeFilters(
            nutrition=NutritionFilters(
                min_calories=600,
                max_calories=300
            )
        )
```

### Integration Test

```python
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_list_recipes():
    response = client.get("/recipes?page=1&page_size=10")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
```

## Common Patterns

### Builder Pattern for Complex Requests

```python
def build_meal_plan_request(
    days: int = 7,
    calories: int = 2000,
    protein_g: int = 100,
    dietary_tags: list[str] | None = None,
    exclude_allergens: list[str] | None = None
) -> MealPlanGenerateRequest:
    return MealPlanGenerateRequest(
        days=days,
        nutrition_constraints=NutritionConstraints(
            target_calories=calories,
            min_protein_g=protein_g
        ),
        dietary_tag_slugs=dietary_tags or [],
        exclude_allergen_names=exclude_allergens or [],
        avoid_duplicate_recipes=True
    )
```

### Repository Pattern

```python
from typing import Optional
from src.api.schemas import RecipeResponse, RecipeFilters, PaginatedResponse

class RecipeRepository:
    def get_by_id(self, recipe_id: int) -> Optional[RecipeResponse]:
        recipe_orm = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe_orm:
            return None
        return RecipeResponse.from_orm(recipe_orm)

    def list(
        self,
        filters: RecipeFilters,
        pagination: PaginationParams
    ) -> PaginatedResponse[RecipeListItem]:
        query = self._apply_filters(session.query(Recipe), filters)

        total = query.count()
        recipes = query.offset(pagination.offset).limit(pagination.limit).all()

        return PaginatedResponse[RecipeListItem].create(
            items=[RecipeListItem.from_orm(r) for r in recipes],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
```

## Performance Tips

### Lazy Loading vs Eager Loading

```python
from sqlalchemy.orm import selectinload

# Eager load relationships for RecipeResponse
recipe = session.query(Recipe)\
    .options(
        selectinload(Recipe.ingredients_association),
        selectinload(Recipe.categories),
        selectinload(Recipe.dietary_tags),
        selectinload(Recipe.allergens),
        selectinload(Recipe.images),
        selectinload(Recipe.nutritional_info)
    )\
    .filter_by(id=recipe_id)\
    .first()

# Convert to schema (all relationships already loaded)
response = RecipeResponse.from_orm(recipe)
```

### Batch Processing

```python
from typing import List
from src.api.schemas import RecipeListItem

def convert_recipes_batch(recipes: List[Recipe]) -> List[RecipeListItem]:
    """Convert multiple recipes efficiently."""
    return [RecipeListItem.from_orm(r) for r in recipes]

# Use in endpoint
recipes = session.query(Recipe).limit(100).all()
response_items = convert_recipes_batch(recipes)
```

## Debugging

### Print Schema Structure

```python
from src.api.schemas import RecipeResponse

# Print schema
print(RecipeResponse.model_json_schema())

# Print field info
for field_name, field_info in RecipeResponse.model_fields.items():
    print(f"{field_name}: {field_info.annotation}")
```

### Validate Dict Before Creating Schema

```python
from src.api.schemas import RecipeResponse

data = {
    "id": 1,
    "name": "Test Recipe",
    # ... more fields
}

# Validate and parse
try:
    recipe = RecipeResponse.model_validate(data)
except ValidationError as e:
    print(e.errors())
```
