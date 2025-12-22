"""
Data normalization for scraped recipe data.
Handles ingredient parsing, instruction formatting, and data cleaning.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger("data_normalizer")


class IngredientParser:
    """Parses ingredient strings into structured components."""

    UNIT_PATTERNS = {
        'weight': {
            'g': ['g', 'gram', 'grams'],
            'kg': ['kg', 'kilogram', 'kilograms'],
            'oz': ['oz', 'ounce', 'ounces'],
            'lb': ['lb', 'pound', 'pounds'],
        },
        'volume': {
            'ml': ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'],
            'l': ['l', 'liter', 'liters', 'litre', 'litres'],
            'tsp': ['tsp', 'teaspoon', 'teaspoons'],
            'tbsp': ['tbsp', 'tablespoon', 'tablespoons'],
            'cup': ['cup', 'cups'],
            'pint': ['pint', 'pints'],
            'fl oz': ['fl oz', 'fluid ounce', 'fluid ounces'],
        },
        'count': {
            'whole': ['whole'],
            'piece': ['piece', 'pieces'],
            'slice': ['slice', 'slices'],
            'clove': ['clove', 'cloves'],
        }
    }

    def __init__(self):
        """Initialize ingredient parser."""
        self.unit_map = self._build_unit_map()

    def _build_unit_map(self) -> Dict[str, str]:
        """
        Build map of unit variations to normalized units.

        Returns:
            Dictionary mapping unit variations to standard abbreviations
        """
        unit_map = {}
        for unit_type, units in self.UNIT_PATTERNS.items():
            for abbr, variations in units.items():
                for variation in variations:
                    unit_map[variation.lower()] = abbr
        return unit_map

    def parse(self, ingredient_str: str) -> Dict[str, Optional[str]]:
        """
        Parse ingredient string into components.

        Args:
            ingredient_str: Raw ingredient string

        Returns:
            Dictionary with parsed components:
                - name: Ingredient name
                - quantity: Numeric quantity
                - unit: Unit abbreviation
                - preparation: Preparation notes
                - is_optional: Whether ingredient is optional
                - original: Original string
        """
        original = ingredient_str.strip()

        quantity_in_parens = re.search(r'\(([^)]+)\)', original)
        quantity_str = None
        unit_str = None
        preparation = None

        if quantity_in_parens:
            quantity_part = quantity_in_parens.group(1).strip()

            qty_match = re.match(
                r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)$',
                quantity_part
            )

            if qty_match:
                quantity_str = qty_match.group(1)
                unit_str = qty_match.group(2).lower()

            ingredient_name = original[:quantity_in_parens.start()].strip()

        else:
            ingredient_name = original

        multiplier_match = re.search(r'\s+x(\d+)$', ingredient_name)
        if multiplier_match:
            multiplier = int(multiplier_match.group(1))
            ingredient_name = ingredient_name[:multiplier_match.start()].strip()

            if quantity_str and multiplier > 0:
                try:
                    base_qty = float(quantity_str)
                    quantity_str = str(base_qty * multiplier)
                except ValueError:
                    pass

        optional_match = re.search(r'\s+x0$', ingredient_name)
        is_optional = bool(optional_match)
        if is_optional:
            ingredient_name = ingredient_name[:optional_match.start()].strip()

        prep_patterns = [
            r',\s*(.+)$',
            r'\(([^)]+)\)$'
        ]

        for pattern in prep_patterns:
            prep_match = re.search(pattern, ingredient_name)
            if prep_match:
                preparation = prep_match.group(1).strip()
                ingredient_name = ingredient_name[:prep_match.start()].strip()
                break

        normalized_unit = None
        if unit_str:
            normalized_unit = self.unit_map.get(unit_str, unit_str)

        return {
            'name': ingredient_name,
            'quantity': quantity_str,
            'unit': normalized_unit,
            'preparation': preparation,
            'is_optional': is_optional,
            'original': original
        }


class InstructionParser:
    """Parses and normalizes cooking instructions."""

    def __init__(self):
        """Initialize instruction parser."""
        pass

    def parse_instructions(self, instructions: List[str]) -> List[Dict[str, str]]:
        """
        Parse instruction list into structured steps.

        Args:
            instructions: List of instruction strings

        Returns:
            List of dictionaries with step details
        """
        parsed_steps = []

        for i, instruction in enumerate(instructions, start=1):
            step_data = self.parse_single_instruction(instruction, i)
            parsed_steps.append(step_data)

        return parsed_steps

    def parse_single_instruction(
        self,
        instruction: str,
        step_number: int
    ) -> Dict[str, str]:
        """
        Parse single instruction into components.

        Args:
            instruction: Instruction text
            step_number: Step number

        Returns:
            Dictionary with instruction details
        """
        cleaned = self._clean_instruction_text(instruction)

        serving_variants = self._extract_serving_variants(cleaned)
        if serving_variants:
            cleaned = serving_variants['base_text']

        time_estimate = self._extract_time_estimate(cleaned)

        return {
            'step_number': step_number,
            'instruction': cleaned,
            'time_minutes': time_estimate,
            'serving_variants': serving_variants,
            'original': instruction
        }

    def _clean_instruction_text(self, text: str) -> str:
        """
        Clean instruction text.

        Args:
            text: Raw instruction text

        Returns:
            Cleaned text
        """
        text = text.strip()

        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'\n+', ' ', text)

        return text

    def _extract_serving_variants(
        self,
        text: str
    ) -> Optional[Dict[str, any]]:
        """
        Extract serving size variants from instruction text.

        Example: "Add 225ml [300ml] [450ml] water"
        Returns: {base: "225ml", variants: ["300ml", "450ml"]}

        Args:
            text: Instruction text

        Returns:
            Dictionary with serving variants or None
        """
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, text)

        if not brackets:
            return None

        base_text = re.sub(bracket_pattern, '', text)
        base_text = re.sub(r'\s+', ' ', base_text).strip()

        return {
            'base_text': base_text,
            'variants': brackets
        }

    def _extract_time_estimate(self, text: str) -> Optional[int]:
        """
        Extract time estimate from instruction.

        Args:
            text: Instruction text

        Returns:
            Time in minutes or None
        """
        time_patterns = [
            r'(\d+)\s*(?:to|-)\s*(\d+)\s*min(?:ute)?s?',
            r'(\d+)\s*min(?:ute)?s?',
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return int(match.group(2))
                else:
                    return int(match.group(1))

        return None


class NutritionNormalizer:
    """Normalizes nutritional information."""

    def __init__(self):
        """Initialize nutrition normalizer."""
        pass

    def normalize_nutrition(
        self,
        nutrition: Dict[str, any]
    ) -> Dict[str, Optional[Decimal]]:
        """
        Normalize nutrition data to standard format.

        Args:
            nutrition: Raw nutrition dictionary

        Returns:
            Normalized nutrition data
        """
        normalized = {}

        fields = [
            ('calories', 'calories'),
            ('carbohydrateContent', 'carbohydrates_g'),
            ('proteinContent', 'protein_g'),
            ('fatContent', 'fat_g'),
            ('fiberContent', 'fiber_g'),
            ('sugarContent', 'sugar_g'),
            ('sodiumContent', 'sodium_mg'),
            ('saturatedFatContent', 'saturated_fat_g'),
        ]

        for source_key, target_key in fields:
            value = nutrition.get(source_key)
            normalized[target_key] = self._parse_numeric_value(value)

        return normalized

    def _parse_numeric_value(self, value: any) -> Optional[Decimal]:
        """
        Parse numeric value from various formats.

        Args:
            value: Value to parse (string, int, float, etc.)

        Returns:
            Decimal value or None
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        if isinstance(value, str):
            numeric_str = re.sub(r'[^\d.]', '', value)

            if numeric_str:
                try:
                    return Decimal(numeric_str)
                except InvalidOperation:
                    logger.warning(f"Could not parse numeric value: {value}")
                    return None

        return None


class DataNormalizer:
    """Main data normalizer combining all parsers."""

    def __init__(self):
        """Initialize data normalizer."""
        self.ingredient_parser = IngredientParser()
        self.instruction_parser = InstructionParser()
        self.nutrition_normalizer = NutritionNormalizer()

    def normalize_recipe_data(self, raw_data: Dict[str, any]) -> Dict[str, any]:
        """
        Normalize complete recipe data.

        Args:
            raw_data: Raw recipe data from scraper

        Returns:
            Normalized recipe data
        """
        normalized = {}

        normalized['name'] = raw_data.get('name', '').strip()
        normalized['description'] = raw_data.get('description', '').strip()
        normalized['source_url'] = raw_data.get('url', '')

        normalized['total_time_minutes'] = self._parse_iso_duration(
            raw_data.get('totalTime')
        )

        normalized['servings'] = self._parse_servings(
            raw_data.get('recipeYield')
        )

        if 'recipeIngredient' in raw_data:
            normalized['ingredients'] = [
                self.ingredient_parser.parse(ing)
                for ing in raw_data['recipeIngredient']
            ]

        if 'recipeInstructions' in raw_data:
            normalized['instructions'] = self.instruction_parser.parse_instructions(
                raw_data['recipeInstructions']
            )

        if 'nutrition' in raw_data:
            normalized['nutrition'] = self.nutrition_normalizer.normalize_nutrition(
                raw_data['nutrition']
            )

        normalized['category'] = raw_data.get('recipeCategory', '').strip()
        normalized['cuisine'] = raw_data.get('recipeCuisine', '').strip()

        if 'aggregateRating' in raw_data:
            rating = raw_data['aggregateRating']
            if rating and isinstance(rating, dict):
                normalized['rating'] = {
                    'value': rating.get('ratingValue'),
                    'count': rating.get('reviewCount')
                }

        normalized['image_url'] = raw_data.get('image', '')

        return normalized

    def _parse_iso_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """
        Parse ISO 8601 duration to minutes.

        Args:
            duration_str: ISO duration string (e.g., 'PT35M') or integer minutes

        Returns:
            Duration in minutes or None
        """
        if not duration_str:
            return None

        # Handle integer input (already in minutes)
        if isinstance(duration_str, (int, float)):
            return int(duration_str)

        # Handle string input
        if not isinstance(duration_str, str):
            return None

        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            return hours * 60 + minutes

        return None

    def _parse_servings(self, servings_str: Optional[str]) -> Optional[int]:
        """
        Parse servings string to integer.

        Args:
            servings_str: Servings string (e.g., '2 or 4 servings')

        Returns:
            Number of servings (minimum if range given)
        """
        if not servings_str:
            return None

        numbers = re.findall(r'\d+', str(servings_str))
        if numbers:
            return int(numbers[0])

        return None


def create_data_normalizer() -> DataNormalizer:
    """
    Factory function to create data normalizer.

    Returns:
        DataNormalizer instance
    """
    return DataNormalizer()
