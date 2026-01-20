"""
Pydantic schemas for FastAPI endpoints.

This module provides comprehensive schema definitions for all API endpoints,
including request/response models, validation, and serialization.
"""

from .common import (
    ErrorResponse,
    SuccessResponse,
    MessageResponse,
)

from .pagination import (
    PaginationParams,
    SortParams,
    SortOrder,
    PaginatedResponse,
)

from .recipe import (
    # Enums
    DifficultyLevel,
    ImageType,
    CategoryType,

    # Nested responses
    UnitResponse,
    IngredientResponse,
    InstructionResponse,
    ImageResponse,
    NutritionResponse,
    CategoryResponse,
    DietaryTagResponse,
    AllergenResponse,

    # Main recipe schemas
    RecipeBase,
    RecipeListItem,
    RecipeResponse,

    # Filters
    NutritionFilters,
    RecipeFilters,
)

from .meal_plan import (
    # Enums
    MealType,

    # Request schemas
    NutritionConstraints,
    MealPreferences,
    MealPlanGenerateRequest,

    # Response schemas
    MealSlot,
    DayPlan,
    ShoppingListPreview,
    MealPlanSummary,
    MealPlanResponse,
)

from .shopping_list import (
    # Enums
    IngredientCategory,
    ShoppingListFormat,

    # Request schemas
    ShoppingListGenerateRequest,
    ShoppingListExportRequest,

    # Response schemas
    ShoppingItem,
    ShoppingCategory,
    ShoppingListSummary,
    ShoppingListResponse,
    ShoppingListExportResponse,
)

from .auth import (
    # Request schemas
    LoginRequest,
    UserCreate,
    UserUpdate,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    RefreshTokenRequest,
    EmailVerificationRequest,

    # Response schemas
    TokenResponse,
    UserBase,
    UserResponse,
)

from .user import (
    # User preference schemas
    UserPreferenceBase,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,

    # Allergen profile schemas
    AllergenResponse as UserAllergenInfo,
    UserAllergenBase,
    UserAllergenCreate,
    UserAllergenBulkCreate,
    UserAllergenResponse,
    UserAllergenListResponse,

    # Dietary tags schemas
    UserDietaryTagsUpdate,
    UserDietaryTagsResponse,
)

from .cost import (
    # Request schemas
    CostEstimateRequest,
    BudgetConstraint,

    # Response schemas
    RecipeCostResponse,
    MealPlanCostBreakdown,
    RecipeWithCost,
    BudgetRecipesResponse,
    CostComparisonResponse,
)

from .favorites import (
    # Enums
    AllergenSeverity,

    # Favorite schemas
    FavoriteRequest,
    FavoriteNotesUpdate,
    FavoriteStatusResponse,
    RecipeSummary,
    FavoriteRecipeResponse,
    FavoriteCountResponse,

    # Allergen warning schemas
    AllergenWarning,
    AllergenWarningsResponse,
    IngredientSubstitution,
    SafeRecipesFilters,
)

__all__ = [
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "MessageResponse",

    # Pagination
    "PaginationParams",
    "SortParams",
    "SortOrder",
    "PaginatedResponse",

    # Recipe - Enums
    "DifficultyLevel",
    "ImageType",
    "CategoryType",

    # Recipe - Nested
    "UnitResponse",
    "IngredientResponse",
    "InstructionResponse",
    "ImageResponse",
    "NutritionResponse",
    "CategoryResponse",
    "DietaryTagResponse",
    "AllergenResponse",

    # Recipe - Main
    "RecipeBase",
    "RecipeListItem",
    "RecipeResponse",

    # Recipe - Filters
    "NutritionFilters",
    "RecipeFilters",

    # Meal Plan - Enums
    "MealType",

    # Meal Plan - Request
    "NutritionConstraints",
    "MealPreferences",
    "MealPlanGenerateRequest",

    # Meal Plan - Response
    "MealSlot",
    "DayPlan",
    "ShoppingListPreview",
    "MealPlanSummary",
    "MealPlanResponse",

    # Shopping List - Enums
    "IngredientCategory",
    "ShoppingListFormat",

    # Shopping List - Request
    "ShoppingListGenerateRequest",
    "ShoppingListExportRequest",

    # Shopping List - Response
    "ShoppingItem",
    "ShoppingCategory",
    "ShoppingListSummary",
    "ShoppingListResponse",
    "ShoppingListExportResponse",

    # Auth - Request
    "LoginRequest",
    "UserCreate",
    "UserUpdate",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "RefreshTokenRequest",
    "EmailVerificationRequest",

    # Auth - Response
    "TokenResponse",
    "UserBase",
    "UserResponse",

    # User Preferences
    "UserPreferenceBase",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",

    # User Allergen Profile
    "UserAllergenInfo",
    "UserAllergenBase",
    "UserAllergenCreate",
    "UserAllergenBulkCreate",
    "UserAllergenResponse",
    "UserAllergenListResponse",

    # User Dietary Tags
    "UserDietaryTagsUpdate",
    "UserDietaryTagsResponse",

    # Cost Estimation - Request
    "CostEstimateRequest",
    "BudgetConstraint",

    # Cost Estimation - Response
    "RecipeCostResponse",
    "MealPlanCostBreakdown",
    "RecipeWithCost",
    "BudgetRecipesResponse",
    "CostComparisonResponse",

    # Favorites - Enums
    "AllergenSeverity",

    # Favorites - Request
    "FavoriteRequest",
    "FavoriteNotesUpdate",

    # Favorites - Response
    "FavoriteStatusResponse",
    "RecipeSummary",
    "FavoriteRecipeResponse",
    "FavoriteCountResponse",

    # Allergen Warnings
    "AllergenWarning",
    "AllergenWarningsResponse",
    "IngredientSubstitution",
    "SafeRecipesFilters",
]
