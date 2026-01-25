import React, { useState, useEffect } from 'react';
import { FilterPanel, FilterSection, FilterOption, RangeFilter } from '../common';
import type { RecipeFilters as RecipeFiltersType, SortParams } from '../../types';
import { DifficultyLevel, SortOrder } from '../../types';
import { ArrowsUpDownIcon } from '@heroicons/react/24/outline';

// Sort options for recipes
const SORT_OPTIONS = [
  { value: 'name', label: 'Name (A-Z)', order: SortOrder.ASC },
  { value: 'name', label: 'Name (Z-A)', order: SortOrder.DESC },
  { value: 'cooking_time', label: 'Quickest First', order: SortOrder.ASC },
  { value: 'cooking_time', label: 'Longest First', order: SortOrder.DESC },
  { value: 'calories', label: 'Lowest Calories', order: SortOrder.ASC },
  { value: 'calories', label: 'Highest Calories', order: SortOrder.DESC },
  { value: 'protein', label: 'Highest Protein', order: SortOrder.DESC },
  { value: 'protein', label: 'Lowest Protein', order: SortOrder.ASC },
];

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
   * Current sort parameters
   */
  sortParams?: SortParams;

  /**
   * Callback when sort changes
   */
  onSortChange?: (params: SortParams) => void;

  /**
   * Whether to show sorting dropdown
   * @default true
   */
  showSorting?: boolean;

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
  sortParams,
  onSortChange,
  showSorting = true,
  className = '',
}) => {
  const [localFilters, setLocalFilters] = useState<RecipeFiltersType>(filters);

  // Get current sort option key for dropdown
  const getCurrentSortKey = () => {
    if (!sortParams?.sort_by) return '0'; // Default to first option
    const idx = SORT_OPTIONS.findIndex(
      opt => opt.value === sortParams.sort_by && opt.order === sortParams.sort_order
    );
    return idx >= 0 ? idx.toString() : '0';
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idx = parseInt(e.target.value, 10);
    const option = SORT_OPTIONS[idx];
    if (option) {
      onSortChange?.({
        sort_by: option.value,
        sort_order: option.order,
      });
    }
  };

  // Sync local filters with prop changes
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleCheckboxChange = (sectionId: string, optionId: string, checked: boolean) => {
    setLocalFilters((prev) => {
      const updated = { ...prev };

      switch (sectionId) {
        case 'categories':
          // Use slugs instead of IDs for API compatibility
          const categorySlugs = new Set(prev.category_slugs || []);
          if (checked) {
            categorySlugs.add(optionId);
          } else {
            categorySlugs.delete(optionId);
          }
          updated.category_slugs = Array.from(categorySlugs);
          // Clear category_ids to avoid conflicts
          delete updated.category_ids;
          break;

        case 'dietary_tags':
          // Use slugs instead of IDs for API compatibility
          const dietaryTagSlugs = new Set(prev.dietary_tag_slugs || []);
          if (checked) {
            dietaryTagSlugs.add(optionId);
          } else {
            dietaryTagSlugs.delete(optionId);
          }
          updated.dietary_tag_slugs = Array.from(dietaryTagSlugs);
          // Clear dietary_tag_ids to avoid conflicts
          delete updated.dietary_tag_ids;
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

        case 'nutrition_calories':
        case 'nutrition_protein':
        case 'nutrition_carbs':
        case 'nutrition_fat':
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

  // Categories section - use slugs for API compatibility
  if (categories.length > 0) {
    sections.push({
      id: 'categories',
      title: 'Categories',
      type: 'checkbox',
      options: categories.map(
        (cat): FilterOption => ({
          id: cat.slug,
          label: cat.name,
          selected: localFilters.category_slugs?.includes(cat.slug) ?? false,
        })
      ),
    });
  }

  // Dietary tags section - use slugs for API compatibility
  if (dietaryTags.length > 0) {
    sections.push({
      id: 'dietary_tags',
      title: 'Dietary Preferences',
      type: 'checkbox',
      options: dietaryTags.map(
        (tag): FilterOption => ({
          id: tag.slug,
          label: tag.name,
          selected: localFilters.dietary_tag_slugs?.includes(tag.slug) ?? false,
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

  // Nutrition sections - each with unique id to avoid duplicate key warnings
  sections.push({
    id: 'nutrition_calories',
    title: 'Maximum Calories',
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
    id: 'nutrition_protein',
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
    id: 'nutrition_carbs',
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
    id: 'nutrition_fat',
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
    <div className={`space-y-4 ${className}`}>
      {/* Sort dropdown */}
      {showSorting && onSortChange && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <ArrowsUpDownIcon className="h-4 w-4" />
            Sort By
          </label>
          <select
            value={getCurrentSortKey()}
            onChange={handleSortChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {SORT_OPTIONS.map((option, idx) => (
              <option key={idx} value={idx}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Filters */}
      <FilterPanel
        title="Filter Recipes"
        sections={sections}
        onCheckboxChange={handleCheckboxChange}
        onRangeChange={handleRangeChange}
        onClearAll={handleClearAll}
        {...(showApplyButton ? { onApply: handleApply } : {})}
        showApplyButton={showApplyButton}
        showClearButton
      />
    </div>
  );
};

export default RecipeFilters;
