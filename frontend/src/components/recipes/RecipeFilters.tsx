import React, { useState, useEffect } from 'react';
import { FilterPanel, FilterSection, FilterOption, RangeFilter } from '../common';
import type { RecipeFilters as RecipeFiltersType } from '../../types';
import { DifficultyLevel } from '../../types';

/**
 * RecipeFilters component props
 */
export interface RecipeFiltersProps {
  /**
   * Current filter values
   */
  filters: RecipeFiltersType;

  /**
   * Callback when filters change
   */
  onFiltersChange: (filters: RecipeFiltersType) => void;

  /**
   * Available categories for filtering
   */
  categories?: Array<{ id: number; name: string; slug: string }>;

  /**
   * Available dietary tags for filtering
   */
  dietaryTags?: Array<{ id: number; name: string; slug: string }>;

  /**
   * Available allergens for filtering
   */
  allergens?: Array<{ id: number; name: string }>;

  /**
   * Whether to show the apply button
   * @default true
   */
  showApplyButton?: boolean;

  /**
   * Callback when apply button is clicked
   */
  onApply?: () => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * RecipeFilters component
 *
 * Provides comprehensive filtering UI for recipes including categories,
 * dietary tags, allergen exclusions, cooking time, difficulty, and
 * nutrition ranges.
 *
 * @example
 * ```tsx
 * <RecipeFilters
 *   filters={currentFilters}
 *   onFiltersChange={setFilters}
 *   categories={categories}
 *   dietaryTags={dietaryTags}
 *   allergens={allergens}
 *   showApplyButton
 *   onApply={() => refetch()}
 * />
 * ```
 */
export const RecipeFilters: React.FC<RecipeFiltersProps> = ({
  filters,
  onFiltersChange,
  categories = [],
  dietaryTags = [],
  allergens = [],
  showApplyButton = true,
  onApply,
  className = '',
}) => {
  const [localFilters, setLocalFilters] = useState<RecipeFiltersType>(filters);

  // Sync local filters with prop changes
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleCheckboxChange = (sectionId: string, optionId: string, checked: boolean) => {
    setLocalFilters((prev) => {
      const updated = { ...prev };

      switch (sectionId) {
        case 'categories':
          const categoryIds = new Set(prev.category_ids || []);
          const categoryId = parseInt(optionId, 10);
          if (checked) {
            categoryIds.add(categoryId);
          } else {
            categoryIds.delete(categoryId);
          }
          updated.category_ids = Array.from(categoryIds);
          break;

        case 'dietary_tags':
          const dietaryTagIds = new Set(prev.dietary_tag_ids || []);
          const tagId = parseInt(optionId, 10);
          if (checked) {
            dietaryTagIds.add(tagId);
          } else {
            dietaryTagIds.delete(tagId);
          }
          updated.dietary_tag_ids = Array.from(dietaryTagIds);
          break;

        case 'allergens':
          const allergenIds = new Set(prev.exclude_allergen_ids || []);
          const allergenId = parseInt(optionId, 10);
          if (checked) {
            allergenIds.add(allergenId);
          } else {
            allergenIds.delete(allergenId);
          }
          updated.exclude_allergen_ids = Array.from(allergenIds);
          break;

        case 'difficulty':
          const difficulties = new Set(prev.difficulty || []);
          if (checked) {
            difficulties.add(optionId as DifficultyLevel);
          } else {
            difficulties.delete(optionId as DifficultyLevel);
          }
          updated.difficulty = Array.from(difficulties);
          break;
      }

      if (!showApplyButton) {
        onFiltersChange(updated);
      }

      return updated;
    });
  };

  const handleRangeChange = (sectionId: string, rangeId: string, value: number) => {
    setLocalFilters((prev) => {
      const updated = { ...prev };

      switch (sectionId) {
        case 'cooking_time':
          updated.max_cooking_time = value;
          break;

        case 'nutrition':
          if (!updated.nutrition) {
            updated.nutrition = {};
          }
          switch (rangeId) {
            case 'max_calories':
              updated.nutrition.max_calories = value;
              break;
            case 'min_protein':
              updated.nutrition.min_protein_g = value;
              break;
            case 'max_carbs':
              updated.nutrition.max_carbs_g = value;
              break;
            case 'max_fat':
              updated.nutrition.max_fat_g = value;
              break;
          }
          break;
      }

      if (!showApplyButton) {
        onFiltersChange(updated);
      }

      return updated;
    });
  };

  const handleClearAll = () => {
    const clearedFilters: RecipeFiltersType = {
      only_active: true,
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const handleApply = () => {
    onFiltersChange(localFilters);
    onApply?.();
  };

  // Build filter sections
  const sections: FilterSection[] = [];

  // Categories section
  if (categories.length > 0) {
    sections.push({
      id: 'categories',
      title: 'Categories',
      type: 'checkbox',
      options: categories.map(
        (cat): FilterOption => ({
          id: cat.id.toString(),
          label: cat.name,
          selected: localFilters.category_ids?.includes(cat.id) ?? false,
        })
      ),
    });
  }

  // Dietary tags section
  if (dietaryTags.length > 0) {
    sections.push({
      id: 'dietary_tags',
      title: 'Dietary Preferences',
      type: 'checkbox',
      options: dietaryTags.map(
        (tag): FilterOption => ({
          id: tag.id.toString(),
          label: tag.name,
          selected: localFilters.dietary_tag_ids?.includes(tag.id) ?? false,
        })
      ),
    });
  }

  // Allergens section
  if (allergens.length > 0) {
    sections.push({
      id: 'allergens',
      title: 'Exclude Allergens',
      type: 'checkbox',
      options: allergens.map(
        (allergen): FilterOption => ({
          id: allergen.id.toString(),
          label: allergen.name,
          selected: localFilters.exclude_allergen_ids?.includes(allergen.id) ?? false,
        })
      ),
    });
  }

  // Difficulty section
  sections.push({
    id: 'difficulty',
    title: 'Difficulty Level',
    type: 'checkbox',
    options: [
      {
        id: DifficultyLevel.EASY,
        label: 'Easy',
        selected: localFilters.difficulty?.includes(DifficultyLevel.EASY) ?? false,
      },
      {
        id: DifficultyLevel.MEDIUM,
        label: 'Medium',
        selected: localFilters.difficulty?.includes(DifficultyLevel.MEDIUM) ?? false,
      },
      {
        id: DifficultyLevel.HARD,
        label: 'Hard',
        selected: localFilters.difficulty?.includes(DifficultyLevel.HARD) ?? false,
      },
    ],
  });

  // Cooking time section
  sections.push({
    id: 'cooking_time',
    title: 'Maximum Cooking Time',
    type: 'range',
    range: {
      id: 'max_cooking_time',
      label: 'Max time',
      min: 0,
      max: 120,
      value: localFilters.max_cooking_time ?? 120,
      step: 5,
      unit: 'min',
    } as RangeFilter,
  });

  // Nutrition section
  sections.push({
    id: 'nutrition',
    title: 'Nutrition',
    type: 'range',
    defaultCollapsed: true,
    range: {
      id: 'max_calories',
      label: 'Max calories',
      min: 0,
      max: 1000,
      value: localFilters.nutrition?.max_calories ?? 1000,
      step: 50,
      unit: 'kcal',
    } as RangeFilter,
  });

  sections.push({
    id: 'nutrition',
    title: 'Minimum Protein',
    type: 'range',
    defaultCollapsed: true,
    range: {
      id: 'min_protein',
      label: 'Min protein',
      min: 0,
      max: 100,
      value: localFilters.nutrition?.min_protein_g ?? 0,
      step: 5,
      unit: 'g',
    } as RangeFilter,
  });

  sections.push({
    id: 'nutrition',
    title: 'Maximum Carbs',
    type: 'range',
    defaultCollapsed: true,
    range: {
      id: 'max_carbs',
      label: 'Max carbs',
      min: 0,
      max: 150,
      value: localFilters.nutrition?.max_carbs_g ?? 150,
      step: 5,
      unit: 'g',
    } as RangeFilter,
  });

  sections.push({
    id: 'nutrition',
    title: 'Maximum Fat',
    type: 'range',
    defaultCollapsed: true,
    range: {
      id: 'max_fat',
      label: 'Max fat',
      min: 0,
      max: 100,
      value: localFilters.nutrition?.max_fat_g ?? 100,
      step: 5,
      unit: 'g',
    } as RangeFilter,
  });

  return (
    <FilterPanel
      title="Filter Recipes"
      sections={sections}
      onCheckboxChange={handleCheckboxChange}
      onRangeChange={handleRangeChange}
      onClearAll={handleClearAll}
      {...(showApplyButton ? { onApply: handleApply } : {})}
      showApplyButton={showApplyButton}
      showClearButton
      className={className}
    />
  );
};

export default RecipeFilters;
