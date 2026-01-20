"""
Shopping list schemas for API endpoints.
"""

from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# ENUMS
# ============================================================================

class IngredientCategory(str, Enum):
    """Categories for organizing shopping list."""
    PROTEIN = "protein"
    DAIRY = "dairy"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    GRAINS = "grains"
    PANTRY = "pantry"
    SPICES = "spices"
    CONDIMENTS = "condiments"
    BEVERAGES = "beverages"
    FROZEN = "frozen"
    BAKERY = "bakery"
    OTHER = "other"


class ShoppingListFormat(str, Enum):
    """Output formats for shopping list."""
    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"
    PDF = "pdf"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ShoppingListGenerateRequest(BaseModel):
    """Request to generate a shopping list."""

    # Source options (mutually exclusive)
    recipe_ids: Optional[list[int]] = Field(
        None,
        description="Generate shopping list from specific recipe IDs"
    )
    meal_plan_id: Optional[int] = Field(
        None,
        description="Generate shopping list from saved meal plan"
    )

    # Servings adjustment
    servings_multiplier: float = Field(
        1.0,
        gt=0,
        description="Multiply ingredient quantities by this factor"
    )

    # Grouping options
    group_by_category: bool = Field(
        True,
        description="Group ingredients by category"
    )
    combine_similar_ingredients: bool = Field(
        True,
        description="Combine similar ingredients (e.g., '2 onions' + '1 onion' = '3 onions')"
    )

    # Filtering options
    exclude_pantry_staples: bool = Field(
        False,
        description="Exclude common pantry items (salt, pepper, oil, etc.)"
    )
    pantry_staples: Optional[list[str]] = Field(
        None,
        description="Custom list of pantry staples to exclude"
    )

    # Output options
    include_optional_ingredients: bool = Field(
        True,
        description="Include optional ingredients from recipes"
    )
    round_quantities: bool = Field(
        True,
        description="Round quantities to common fractions"
    )

    @field_validator('recipe_ids', 'meal_plan_id')
    @classmethod
    def validate_source(cls, v, info):
        """Ensure at least one source is provided."""
        recipe_ids = info.data.get('recipe_ids')
        meal_plan_id = info.data.get('meal_plan_id')

        if v is None and recipe_ids is None and meal_plan_id is None:
            raise ValueError('Either recipe_ids or meal_plan_id must be provided')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipe_ids": [1, 2, 3],
                    "servings_multiplier": 1.5,
                    "group_by_category": True,
                    "combine_similar_ingredients": True,
                    "exclude_pantry_staples": True
                },
                {
                    "meal_plan_id": 5,
                    "group_by_category": True,
                    "round_quantities": True
                }
            ]
        }
    }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ShoppingItem(BaseModel):
    """A single item on the shopping list."""

    ingredient_name: str = Field(..., description="Ingredient name")
    quantity: Optional[Decimal] = Field(None, ge=0, description="Total quantity needed")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    category: IngredientCategory = Field(
        IngredientCategory.OTHER,
        description="Ingredient category"
    )
    is_optional: bool = Field(False, description="Whether this ingredient is optional")
    notes: Optional[str] = Field(None, description="Additional notes (preparation, substitutions)")
    recipe_count: int = Field(1, ge=1, description="Number of recipes using this ingredient")
    recipe_names: list[str] = Field(
        default_factory=list,
        description="Names of recipes using this ingredient"
    )

    @property
    def display_quantity(self) -> str:
        """Format quantity with unit for display."""
        if self.quantity and self.unit:
            return f"{self.quantity} {self.unit}"
        elif self.quantity:
            return str(self.quantity)
        return ""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "ingredient_name": "Chicken Breast",
                    "quantity": 1.2,
                    "unit": "kg",
                    "category": "protein",
                    "is_optional": False,
                    "notes": "Boneless, skinless",
                    "recipe_count": 3,
                    "recipe_names": ["Grilled Chicken", "Chicken Stir-fry", "Chicken Salad"]
                }
            ]
        }
    )


class ShoppingCategory(BaseModel):
    """A category of shopping items."""

    name: IngredientCategory = Field(..., description="Category name")
    display_name: str = Field(..., description="Human-readable category name")
    items: list[ShoppingItem] = Field(..., description="Items in this category")
    item_count: int = Field(..., ge=0, description="Number of items in category")

    @field_validator('item_count')
    @classmethod
    def validate_item_count(cls, v: int, info) -> int:
        """Ensure item_count matches actual items."""
        items = info.data.get('items', [])
        return len(items)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "protein",
                    "display_name": "Protein",
                    "items": [],
                    "item_count": 5
                }
            ]
        }
    )


class ShoppingListSummary(BaseModel):
    """Summary statistics for the shopping list."""

    total_items: int = Field(..., ge=0, description="Total number of unique items")
    total_categories: int = Field(..., ge=0, description="Number of categories with items")
    total_recipes: int = Field(..., ge=0, description="Number of recipes included")
    estimated_cost: Optional[Decimal] = Field(None, description="Estimated total cost (if available)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_items": 35,
                    "total_categories": 8,
                    "total_recipes": 7,
                    "estimated_cost": 75.50
                }
            ]
        }
    }


class ShoppingListResponse(BaseModel):
    """Complete shopping list response."""

    id: Optional[int] = Field(None, description="Shopping list ID if saved")
    categories: list[ShoppingCategory] = Field(..., description="Items grouped by category")
    uncategorized_items: list[ShoppingItem] = Field(
        default_factory=list,
        description="Items without a category"
    )
    summary: ShoppingListSummary = Field(..., description="Shopping list summary")

    # Metadata
    source_recipe_ids: list[int] = Field(
        default_factory=list,
        description="Recipe IDs used to generate this list"
    )
    source_meal_plan_id: Optional[int] = Field(
        None,
        description="Meal plan ID if generated from meal plan"
    )
    servings_multiplier: float = Field(1.0, description="Applied servings multiplier")

    # Optional sections
    pantry_staples_excluded: list[str] = Field(
        default_factory=list,
        description="Pantry staples that were excluded"
    )
    optional_items: list[ShoppingItem] = Field(
        default_factory=list,
        description="Optional ingredients (if separated)"
    )

    # Export options
    markdown_url: Optional[str] = Field(None, description="URL to markdown export")
    pdf_url: Optional[str] = Field(None, description="URL to PDF export")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "categories": [
                        {
                            "name": "protein",
                            "display_name": "Protein",
                            "items": [
                                {
                                    "ingredient_name": "Chicken Breast",
                                    "quantity": 1.2,
                                    "unit": "kg",
                                    "category": "protein",
                                    "recipe_count": 3
                                }
                            ],
                            "item_count": 1
                        }
                    ],
                    "uncategorized_items": [],
                    "summary": {
                        "total_items": 35,
                        "total_categories": 8,
                        "total_recipes": 7
                    },
                    "source_recipe_ids": [1, 2, 3, 4, 5, 6, 7],
                    "servings_multiplier": 1.0
                }
            ]
        }
    )


# ============================================================================
# EXPORT SCHEMAS
# ============================================================================

class ShoppingListExportRequest(BaseModel):
    """Request to export shopping list in different formats."""

    shopping_list_id: int = Field(..., description="Shopping list ID to export")
    format: ShoppingListFormat = Field(
        ShoppingListFormat.MARKDOWN,
        description="Export format"
    )
    include_recipe_names: bool = Field(
        True,
        description="Include recipe names for each ingredient"
    )
    include_checkboxes: bool = Field(
        True,
        description="Include checkboxes for markdown/text format"
    )
    group_by_store_section: bool = Field(
        False,
        description="Group by typical store layout"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "shopping_list_id": 1,
                    "format": "markdown",
                    "include_recipe_names": True,
                    "include_checkboxes": True
                }
            ]
        }
    }


class ShoppingListExportResponse(BaseModel):
    """Response for shopping list export."""

    format: ShoppingListFormat = Field(..., description="Export format")
    content: Optional[str] = Field(None, description="Exported content (for text-based formats)")
    download_url: Optional[str] = Field(None, description="Download URL (for file-based formats)")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    expires_at: Optional[str] = Field(None, description="When the download URL expires")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "format": "markdown",
                    "content": "# Shopping List\\n\\n## Protein\\n- [ ] Chicken Breast - 1.2 kg",
                    "download_url": None,
                    "file_size_bytes": None
                },
                {
                    "format": "pdf",
                    "content": None,
                    "download_url": "https://example.com/shopping-list.pdf",
                    "file_size_bytes": 52480,
                    "expires_at": "2026-01-21T10:00:00Z"
                }
            ]
        }
    }
