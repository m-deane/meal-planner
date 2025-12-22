"""
Data validation against schema.org Recipe spec and custom rules.
Validates recipe data before database insertion.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ValidationError

from src.config import config
from src.utils.logger import get_logger

logger = get_logger("data_validator")


class ValidationResult:
    """Result of validation with errors and warnings."""

    def __init__(self):
        """Initialize validation result."""
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, field: str, message: str) -> None:
        """Add validation error."""
        self.errors.append(f"{field}: {message}")
        self.is_valid = False

    def add_warning(self, field: str, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(f"{field}: {message}")

    def __bool__(self) -> bool:
        """Check if validation passed."""
        return self.is_valid

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ValidationResult(valid={self.is_valid}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


class RecipeValidator:
    """Validates recipe data against schema.org Recipe specification."""

    def __init__(self, strict: bool = False):
        """
        Initialize recipe validator.

        Args:
            strict: Fail validation on warnings
        """
        self.strict = strict or config.validation_strict

    def validate(self, recipe_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate recipe data.

        Args:
            recipe_data: Normalized recipe data dictionary

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()

        self._validate_required_fields(recipe_data, result)
        self._validate_name(recipe_data, result)
        self._validate_ingredients(recipe_data, result)
        self._validate_instructions(recipe_data, result)
        self._validate_nutrition(recipe_data, result)
        self._validate_times(recipe_data, result)
        self._validate_servings(recipe_data, result)
        self._validate_url(recipe_data, result)

        if self.strict and result.warnings:
            for warning in result.warnings:
                result.add_error("strict_mode", f"Warning treated as error: {warning}")

        return result

    def _validate_required_fields(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate presence of required fields."""
        required_fields = ['name', 'source_url']

        for field in required_fields:
            if not data.get(field):
                result.add_error(field, "Required field is missing or empty")

        if config.validation_require_ingredients:
            if not data.get('ingredients'):
                result.add_error('ingredients', "At least one ingredient is required")

        if config.validation_require_instructions:
            if not data.get('instructions'):
                result.add_error('instructions', "At least one instruction is required")

    def _validate_name(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate recipe name."""
        name = data.get('name', '')

        if len(name) < 3:
            result.add_error('name', "Name must be at least 3 characters")

        if len(name) > 500:
            result.add_error('name', "Name must not exceed 500 characters")

        if not any(c.isalpha() for c in name):
            result.add_error('name', "Name must contain at least one letter")

    def _validate_ingredients(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate ingredients list."""
        ingredients = data.get('ingredients', [])

        if not ingredients:
            return

        for i, ingredient in enumerate(ingredients, start=1):
            if not isinstance(ingredient, dict):
                result.add_error(
                    f'ingredient_{i}',
                    "Ingredient must be a dictionary"
                )
                continue

            if not ingredient.get('name'):
                result.add_error(
                    f'ingredient_{i}',
                    "Ingredient name is required"
                )

            if ingredient.get('quantity'):
                try:
                    qty = Decimal(str(ingredient['quantity']))
                    if qty < 0:
                        result.add_error(
                            f'ingredient_{i}',
                            "Quantity cannot be negative"
                        )
                    if qty == 0:
                        result.add_warning(
                            f'ingredient_{i}',
                            "Quantity is zero"
                        )
                except Exception:
                    result.add_warning(
                        f'ingredient_{i}',
                        f"Invalid quantity format: {ingredient['quantity']}"
                    )

    def _validate_instructions(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate cooking instructions."""
        instructions = data.get('instructions', [])

        if not instructions:
            return

        for i, instruction in enumerate(instructions, start=1):
            if isinstance(instruction, dict):
                inst_text = instruction.get('instruction', '')
            else:
                inst_text = str(instruction)

            if not inst_text or len(inst_text.strip()) < 5:
                result.add_warning(
                    f'instruction_{i}',
                    "Instruction is too short or empty"
                )

            if isinstance(instruction, dict):
                time_min = instruction.get('time_minutes')
                if time_min is not None:
                    try:
                        time_val = int(time_min)
                        if time_val < 0:
                            result.add_warning(
                                f'instruction_{i}',
                                "Time cannot be negative"
                            )
                        if time_val > 1440:
                            result.add_warning(
                                f'instruction_{i}',
                                "Time exceeds 24 hours"
                            )
                    except (ValueError, TypeError):
                        result.add_warning(
                            f'instruction_{i}',
                            f"Invalid time format: {time_min}"
                        )

    def _validate_nutrition(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate nutritional information."""
        nutrition = data.get('nutrition')

        if not nutrition:
            result.add_warning('nutrition', "Nutritional information not provided")
            return

        if not isinstance(nutrition, dict):
            result.add_error('nutrition', "Nutrition must be a dictionary")
            return

        calories = nutrition.get('calories')
        if calories is not None:
            try:
                cal_val = Decimal(str(calories))
                if cal_val < config.validation_min_calories:
                    result.add_warning(
                        'nutrition.calories',
                        f"Calories below minimum ({config.validation_min_calories})"
                    )
                if cal_val > config.validation_max_calories:
                    result.add_warning(
                        'nutrition.calories',
                        f"Calories above maximum ({config.validation_max_calories})"
                    )
                if cal_val < 0:
                    result.add_error('nutrition.calories', "Calories cannot be negative")
            except Exception:
                result.add_error(
                    'nutrition.calories',
                    f"Invalid calorie format: {calories}"
                )

        macro_fields = [
            'protein_g',
            'carbohydrates_g',
            'fat_g',
            'fiber_g',
            'sugar_g'
        ]

        for field in macro_fields:
            value = nutrition.get(field)
            if value is not None:
                try:
                    decimal_val = Decimal(str(value))
                    if decimal_val < 0:
                        result.add_error(
                            f'nutrition.{field}',
                            f"{field} cannot be negative"
                        )
                    if decimal_val > 1000:
                        result.add_warning(
                            f'nutrition.{field}',
                            f"{field} value seems unusually high (>1000g)"
                        )
                except Exception:
                    result.add_warning(
                        f'nutrition.{field}',
                        f"Invalid format: {value}"
                    )

    def _validate_times(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate time fields."""
        total_time = data.get('total_time_minutes')

        if total_time is not None:
            try:
                time_val = int(total_time)
                if time_val < 0:
                    result.add_error('total_time_minutes', "Time cannot be negative")
                if time_val == 0:
                    result.add_warning('total_time_minutes', "Total time is zero")
                if time_val > 1440:
                    result.add_warning(
                        'total_time_minutes',
                        "Total time exceeds 24 hours"
                    )
            except (ValueError, TypeError):
                result.add_error(
                    'total_time_minutes',
                    f"Invalid time format: {total_time}"
                )

    def _validate_servings(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate servings."""
        servings = data.get('servings')

        if servings is not None:
            try:
                serv_val = int(servings)
                if serv_val < 1:
                    result.add_error('servings', "Servings must be at least 1")
                if serv_val > 100:
                    result.add_warning('servings', "Servings exceeds 100")
            except (ValueError, TypeError):
                result.add_error('servings', f"Invalid servings format: {servings}")

    def _validate_url(
        self,
        data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate source URL."""
        url = data.get('source_url', '')

        if not url:
            result.add_error('source_url', "Source URL is required")
            return

        if not url.startswith(('http://', 'https://')):
            result.add_error('source_url', "URL must start with http:// or https://")

        if 'gousto.co.uk' not in url.lower():
            result.add_warning('source_url', "URL does not appear to be from Gousto")


def validate_recipe(
    recipe_data: Dict[str, Any],
    strict: bool = False
) -> ValidationResult:
    """
    Validate recipe data.

    Args:
        recipe_data: Normalized recipe data
        strict: Enable strict mode (warnings become errors)

    Returns:
        ValidationResult
    """
    validator = RecipeValidator(strict=strict)
    result = validator.validate(recipe_data)

    if not result.is_valid:
        logger.error(
            f"Recipe validation failed: {recipe_data.get('name', 'Unknown')} | "
            f"Errors: {len(result.errors)}"
        )
        for error in result.errors:
            logger.error(f"  - {error}")

    if result.warnings:
        logger.warning(
            f"Recipe validation warnings: {recipe_data.get('name', 'Unknown')} | "
            f"Warnings: {len(result.warnings)}"
        )
        for warning in result.warnings:
            logger.warning(f"  - {warning}")

    return result
