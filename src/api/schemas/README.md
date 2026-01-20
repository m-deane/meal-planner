# API Schemas Documentation

Comprehensive Pydantic v2 schemas for the Meal Planner FastAPI application.

## Overview

This package contains all Pydantic schemas used for request validation, response serialization, and data transformation in the FastAPI application. All schemas use Pydantic v2 syntax with proper type hints, validation, and documentation.

## Module Structure

```
src/api/schemas/
├── __init__.py          # Central exports for all schemas
├── common.py            # Common response schemas
├── pagination.py        # Pagination and sorting utilities
├── recipe.py            # Recipe-related schemas
├── meal_plan.py         # Meal planning schemas
├── shopping_list.py     # Shopping list schemas
└── auth.py              # Authentication and user schemas
```

## Schema Files

### 1. common.py

Standard response formats used across all endpoints.

**Classes:**
- `ErrorResponse` - Standardized error response with error code, message, and optional details
- `SuccessResponse` - Success response with message and optional data payload
- `MessageResponse` - Simple message-only response

**Usage:**
```python
from src.api.schemas import ErrorResponse, SuccessResponse

# Return error
return ErrorResponse(
    error="ValidationError",
    message="Invalid input parameters",
    details={"field": "email", "reason": "Invalid format"}
)

# Return success
return SuccessResponse(
    message="Recipe created successfully",
    data={"recipe_id": 123}
)
```

### 2. pagination.py

Pagination and sorting functionality for list endpoints.

**Classes:**
- `PaginationParams` - Query parameters for pagination (page, page_size)
- `SortParams` - Query parameters for sorting (sort_by, sort_order)
- `PaginatedResponse[T]` - Generic paginated response wrapper

**Features:**
- Automatic page size clamping (max 100 items)
- Built-in offset calculation
- Factory method for easy creation
- Total pages and navigation info

**Usage:**
```python
from src.api.schemas import PaginationParams, PaginatedResponse, RecipeListItem

# In endpoint
def list_recipes(pagination: PaginationParams):
    recipes = get_recipes(offset=pagination.offset, limit=pagination.limit)
    total = count_recipes()

    return PaginatedResponse[RecipeListItem].create(
        items=recipes,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )
```

### 3. recipe.py

Complete recipe schemas with all related entities.

**Enums:**
- `DifficultyLevel` - easy, medium, hard
- `ImageType` - main, step, thumbnail, hero
- `CategoryType` - cuisine, meal_type, occasion

**Response Schemas:**
- `IngredientResponse` - Ingredient with quantity, unit, preparation notes
- `InstructionResponse` - Cooking step with time and instructions
- `ImageResponse` - Recipe image metadata
- `NutritionResponse` - Complete nutritional information
- `CategoryResponse` - Category information
- `DietaryTagResponse` - Dietary tag (vegan, keto, etc.)
- `AllergenResponse` - Allergen information
- `UnitResponse` - Measurement unit details

**Main Schemas:**
- `RecipeBase` - Base recipe fields
- `RecipeListItem` - Lightweight recipe for list views
- `RecipeResponse` - Complete recipe with all relationships

**Filter Schemas:**
- `NutritionFilters` - Filter recipes by nutrition values
- `RecipeFilters` - Comprehensive filtering (categories, tags, time, difficulty, etc.)

**Key Features:**
- Nutrition carbs_g alias for carbohydrates_g
- Automatic validation of ranges (min/max)
- Rich filtering capabilities
- Complete type safety with enums

**Usage:**
```python
from src.api.schemas import RecipeFilters, RecipeListItem

filters = RecipeFilters(
    category_slugs=["italian", "pasta"],
    max_total_time=45,
    difficulty=[DifficultyLevel.EASY, DifficultyLevel.MEDIUM],
    nutrition=NutritionFilters(
        max_calories=600,
        min_protein_g=20
    )
)
```

### 4. meal_plan.py

Meal planning and generation schemas.

**Enums:**
- `MealType` - breakfast, lunch, dinner, snack

**Request Schemas:**
- `NutritionConstraints` - Daily nutrition targets and limits
- `MealPreferences` - Meal type preferences and calorie distribution
- `MealPlanGenerateRequest` - Complete meal plan generation request

**Response Schemas:**
- `MealSlot` - Single meal in a day
- `DayPlan` - Complete day with all meals
- `MealPlanSummary` - Statistics and summary
- `ShoppingListPreview` - Preview of ingredients needed
- `MealPlanResponse` - Complete meal plan with all days

**Key Features:**
- Flexible day range (1-30 days)
- Customizable meal preferences
- Nutrition constraint validation
- Variety and duplicate prevention options
- Shopping list optimization

**Usage:**
```python
from src.api.schemas import MealPlanGenerateRequest, MealPreferences

request = MealPlanGenerateRequest(
    days=7,
    meal_preferences=MealPreferences(
        include_breakfast=True,
        include_lunch=True,
        include_dinner=True
    ),
    nutrition_constraints=NutritionConstraints(
        target_calories=2000,
        min_protein_g=100
    ),
    dietary_tag_slugs=["vegetarian"],
    avoid_duplicate_recipes=True
)
```

### 5. shopping_list.py

Shopping list generation and export.

**Enums:**
- `IngredientCategory` - protein, dairy, vegetables, etc.
- `ShoppingListFormat` - json, markdown, text, pdf

**Request Schemas:**
- `ShoppingListGenerateRequest` - Generate from recipes or meal plan
- `ShoppingListExportRequest` - Export in different formats

**Response Schemas:**
- `ShoppingItem` - Single ingredient with quantity and metadata
- `ShoppingCategory` - Grouped ingredients by category
- `ShoppingListSummary` - Summary statistics
- `ShoppingListResponse` - Complete shopping list
- `ShoppingListExportResponse` - Export result with download URL

**Key Features:**
- Automatic ingredient combination
- Category-based organization
- Pantry staples exclusion
- Servings multiplier
- Multiple export formats
- Recipe tracking (which recipes use each ingredient)

**Usage:**
```python
from src.api.schemas import ShoppingListGenerateRequest

request = ShoppingListGenerateRequest(
    recipe_ids=[1, 2, 3],
    servings_multiplier=1.5,
    group_by_category=True,
    combine_similar_ingredients=True,
    exclude_pantry_staples=True
)
```

### 6. auth.py

Authentication and user management.

**Request Schemas:**
- `LoginRequest` - User login credentials
- `UserCreate` - New user registration
- `UserUpdate` - Profile updates
- `PasswordChangeRequest` - Change password
- `PasswordResetRequest` - Request password reset
- `PasswordResetConfirm` - Confirm password reset
- `RefreshTokenRequest` - Refresh access token
- `EmailVerificationRequest` - Verify email

**Response Schemas:**
- `TokenResponse` - JWT tokens with expiration
- `UserBase` - Basic user information
- `UserResponse` - Complete user profile

**Key Features:**
- Strong password validation (min 8 chars, uppercase, lowercase, number)
- Username format validation (alphanumeric, underscores, hyphens)
- Email validation using email-validator
- Automatic username lowercasing
- User preferences support

**Usage:**
```python
from src.api.schemas import UserCreate, LoginRequest

# Register
user = UserCreate(
    username="john_doe",
    email="john@example.com",
    password="SecureP@ssw0rd123",
    full_name="John Doe"
)

# Login
login = LoginRequest(
    username="john_doe",
    password="SecureP@ssw0rd123"
)
```

## Common Patterns

### ORM Compatibility

All response schemas use `ConfigDict(from_attributes=True)` for SQLAlchemy ORM compatibility:

```python
from src.database.models import Recipe
from src.api.schemas import RecipeResponse

# Direct conversion from ORM model
recipe_orm = session.query(Recipe).first()
recipe_response = RecipeResponse.from_orm(recipe_orm)
```

### Validation

Schemas use Pydantic v2 field validators:

```python
@field_validator('max_calories')
@classmethod
def validate_max_calories(cls, v: Optional[int], info) -> Optional[int]:
    if v is not None and info.data.get('min_calories') is not None:
        if v < info.data['min_calories']:
            raise ValueError('max_calories must be >= min_calories')
    return v
```

### Examples

All schemas include `json_schema_extra` with examples for OpenAPI documentation:

```python
model_config = {
    "json_schema_extra": {
        "examples": [
            {
                "username": "john_doe",
                "email": "john@example.com"
            }
        ]
    }
}
```

## Testing

Comprehensive test suite in `/home/user/meal-planner/tests/unit/test_schemas.py`:

- 41 unit tests covering all schemas
- Validation edge cases
- Error handling
- Integration tests for complex structures

Run tests:
```bash
pytest tests/unit/test_schemas.py -v
```

## Dependencies

- **pydantic** ^2.5.2 - Core validation framework
- **pydantic-settings** ^2.1.0 - Settings management
- **email-validator** ^2.2.0 - Email validation for UserCreate schema

## Type Safety

All schemas are fully typed with proper type hints:
- `Optional[T]` for nullable fields
- `list[T]` for arrays
- `dict[str, Any]` for flexible objects
- Enum types for constrained choices
- Generic types for `PaginatedResponse[T]`

## Best Practices

1. **Use appropriate schemas** - ListItem for lists, full Response for details
2. **Leverage filters** - Use RecipeFilters and NutritionFilters for complex queries
3. **Validate early** - Let Pydantic catch errors before database operations
4. **Document examples** - Keep json_schema_extra examples up to date
5. **Test edge cases** - Add tests for new validation rules

## Future Enhancements

Potential additions:
- Saved meal plan schemas (CRUD operations)
- User preferences and favorites
- Recipe ratings and reviews
- Cooking history tracking
- Ingredient substitution suggestions
- Advanced nutrition analysis
