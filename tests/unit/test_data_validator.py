"""
Unit tests for data validator module.
Tests recipe validation against schema.org and custom rules.
"""

import pytest
from decimal import Decimal

from src.validators.data_validator import (
    ValidationResult,
    RecipeValidator,
    validate_recipe
)


class TestValidationResult:
    """Test ValidationResult class."""

    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Test adding validation error."""
        result = ValidationResult()
        result.add_error('name', 'Name is required')

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert 'name: Name is required' in result.errors

    def test_add_warning(self):
        """Test adding validation warning."""
        result = ValidationResult()
        result.add_warning('nutrition', 'Nutrition data missing')

        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert 'nutrition: Nutrition data missing' in result.warnings

    def test_bool_conversion(self):
        """Test boolean conversion of ValidationResult."""
        result = ValidationResult()
        assert bool(result) is True

        result.add_error('test', 'error')
        assert bool(result) is False

    def test_repr(self):
        """Test string representation."""
        result = ValidationResult()
        repr_str = repr(result)

        assert 'ValidationResult' in repr_str
        assert 'valid=True' in repr_str


class TestRecipeValidator:
    """Test RecipeValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return RecipeValidator(strict=False)

    @pytest.fixture
    def strict_validator(self):
        """Create strict validator instance."""
        return RecipeValidator(strict=True)

    @pytest.fixture
    def valid_recipe_data(self):
        """Create valid recipe data."""
        return {
            'name': 'Valid Recipe Name',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'description': 'A valid recipe description',
            'total_time_minutes': 30,
            'servings': 2,
            'ingredients': [
                {
                    'name': 'Tomato',
                    'quantity': '250',
                    'unit': 'g'
                }
            ],
            'instructions': [
                {
                    'step_number': 1,
                    'instruction': 'Cook the ingredients'
                }
            ],
            'nutrition': {
                'calories': 350,
                'protein_g': 15,
                'carbohydrates_g': 40,
                'fat_g': 12
            }
        }

    def test_validate_valid_recipe(self, validator, valid_recipe_data):
        """Test validation of valid recipe."""
        result = validator.validate(valid_recipe_data)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_missing_name(self, validator):
        """Test validation fails with missing name."""
        data = {
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('name' in error.lower() for error in result.errors)

    def test_validate_missing_url(self, validator):
        """Test validation fails with missing URL."""
        data = {
            'name': 'Test Recipe'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('source_url' in error.lower() for error in result.errors)

    def test_validate_name_too_short(self, validator):
        """Test validation fails with short name."""
        data = {
            'name': 'AB',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('at least 3 characters' in error for error in result.errors)

    def test_validate_name_too_long(self, validator):
        """Test validation fails with very long name."""
        data = {
            'name': 'A' * 501,
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('500 characters' in error for error in result.errors)

    def test_validate_name_no_letters(self, validator):
        """Test validation fails with no letters in name."""
        data = {
            'name': '12345',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('at least one letter' in error for error in result.errors)

    def test_validate_ingredients_required(self, validator, test_config):
        """Test validation requires ingredients when configured."""
        test_config.validation_require_ingredients = True

        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('ingredient' in error.lower() for error in result.errors)

    def test_validate_instructions_required(self, validator, test_config):
        """Test validation requires instructions when configured."""
        test_config.validation_require_instructions = True

        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'ingredients': [{'name': 'Tomato'}]
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('instruction' in error.lower() for error in result.errors)

    def test_validate_ingredient_missing_name(self, validator):
        """Test validation fails with ingredient missing name."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'ingredients': [
                {
                    'quantity': '100',
                    'unit': 'g'
                }
            ]
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('Ingredient name is required' in error for error in result.errors)

    def test_validate_ingredient_negative_quantity(self, validator):
        """Test validation fails with negative quantity."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'ingredients': [
                {
                    'name': 'Tomato',
                    'quantity': '-5',
                    'unit': 'g'
                }
            ]
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('cannot be negative' in error for error in result.errors)

    def test_validate_ingredient_zero_quantity_warning(self, validator):
        """Test validation warns with zero quantity."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'ingredients': [
                {
                    'name': 'Tomato',
                    'quantity': '0',
                    'unit': 'g'
                }
            ]
        }

        result = validator.validate(data)

        # Note: Zero quantity generates a warning but recipe is still valid unless strict mode
        assert any('Quantity is zero' in warning for warning in result.warnings)

    def test_validate_instruction_too_short(self, validator):
        """Test validation warns with short instruction."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'instructions': [
                {
                    'step_number': 1,
                    'instruction': 'Mix'
                }
            ]
        }

        result = validator.validate(data)

        assert any('too short' in warning.lower() for warning in result.warnings)

    def test_validate_instruction_negative_time(self, validator):
        """Test validation warns with negative time."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'instructions': [
                {
                    'step_number': 1,
                    'instruction': 'Cook the food',
                    'time_minutes': -10
                }
            ]
        }

        result = validator.validate(data)

        assert any('cannot be negative' in warning for warning in result.warnings)

    def test_validate_instruction_excessive_time(self, validator):
        """Test validation warns with excessive time."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'instructions': [
                {
                    'step_number': 1,
                    'instruction': 'Cook the food',
                    'time_minutes': 2000
                }
            ]
        }

        result = validator.validate(data)

        assert any('exceeds 24 hours' in warning for warning in result.warnings)

    def test_validate_nutrition_missing_warning(self, validator):
        """Test validation warns with missing nutrition."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert any('Nutritional information not provided' in warning for warning in result.warnings)

    def test_validate_nutrition_negative_calories(self, validator):
        """Test validation fails with negative calories."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'calories': -100
            }
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('cannot be negative' in error for error in result.errors)

    def test_validate_nutrition_calories_too_low(self, validator, test_config):
        """Test validation warns with low calories."""
        test_config.validation_min_calories = 50

        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'calories': 10
            }
        }

        result = validator.validate(data)

        assert any('below minimum' in warning for warning in result.warnings)

    def test_validate_nutrition_calories_too_high(self, validator, test_config):
        """Test validation warns with high calories."""
        test_config.validation_max_calories = 5000

        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'calories': 6000
            }
        }

        result = validator.validate(data)

        assert any('above maximum' in warning for warning in result.warnings)

    def test_validate_nutrition_negative_macros(self, validator):
        """Test validation fails with negative macros."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'protein_g': -5
            }
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('cannot be negative' in error for error in result.errors)

    def test_validate_nutrition_excessive_macros(self, validator):
        """Test validation warns with excessive macros."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {
                'protein_g': 1500
            }
        }

        result = validator.validate(data)

        assert any('unusually high' in warning for warning in result.warnings)

    def test_validate_total_time_negative(self, validator):
        """Test validation fails with negative time."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'total_time_minutes': -10
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('cannot be negative' in error for error in result.errors)

    def test_validate_total_time_zero_warning(self, validator):
        """Test validation warns with zero time."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'total_time_minutes': 0
        }

        result = validator.validate(data)

        assert any('Total time is zero' in warning for warning in result.warnings)

    def test_validate_total_time_excessive(self, validator):
        """Test validation warns with excessive time."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'total_time_minutes': 2000
        }

        result = validator.validate(data)

        assert any('exceeds 24 hours' in warning for warning in result.warnings)

    def test_validate_servings_too_low(self, validator):
        """Test validation fails with servings less than 1."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'servings': 0
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('at least 1' in error for error in result.errors)

    def test_validate_servings_excessive(self, validator):
        """Test validation warns with excessive servings."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'servings': 150
        }

        result = validator.validate(data)

        assert any('exceeds 100' in warning for warning in result.warnings)

    def test_validate_url_missing_protocol(self, validator):
        """Test validation fails with URL missing protocol."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'www.gousto.co.uk/cookbook/recipes/test'
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert any('http://' in error for error in result.errors)

    def test_validate_url_not_gousto(self, validator):
        """Test validation warns with non-Gousto URL."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.example.com/recipe'
        }

        result = validator.validate(data)

        assert any('not appear to be from Gousto' in warning for warning in result.warnings)

    def test_strict_mode_converts_warnings_to_errors(self, strict_validator):
        """Test strict mode converts warnings to errors."""
        data = {
            'name': 'Test Recipe',
            'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test',
            'nutrition': {}
        }

        result = strict_validator.validate(data)

        assert result.is_valid is False
        assert any('strict_mode' in error for error in result.errors)


def test_validate_recipe_function(sample_recipe_data):
    """Test validate_recipe function."""
    result = validate_recipe(sample_recipe_data, strict=False)

    assert isinstance(result, ValidationResult)
    assert result.is_valid is True


def test_validate_recipe_function_strict():
    """Test validate_recipe function with strict mode."""
    data = {
        'name': 'Test Recipe',
        'source_url': 'https://www.gousto.co.uk/cookbook/recipes/test'
    }

    result = validate_recipe(data, strict=True)

    assert result.is_valid is False
