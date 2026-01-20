import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Button } from './Button';

/**
 * Filter option for checkbox groups
 */
export interface FilterOption {
  /**
   * Unique identifier
   */
  id: string;

  /**
   * Display label
   */
  label: string;

  /**
   * Whether the option is selected
   */
  selected: boolean;

  /**
   * Optional count to display
   */
  count?: number;
}

/**
 * Range filter configuration
 */
export interface RangeFilter {
  /**
   * Unique identifier
   */
  id: string;

  /**
   * Display label
   */
  label: string;

  /**
   * Minimum value
   */
  min: number;

  /**
   * Maximum value
   */
  max: number;

  /**
   * Current value
   */
  value: number;

  /**
   * Step increment
   */
  step?: number;

  /**
   * Unit to display (e.g., 'g', 'kcal')
   */
  unit?: string;
}

/**
 * Filter section configuration
 */
export interface FilterSection {
  /**
   * Unique identifier
   */
  id: string;

  /**
   * Section title
   */
  title: string;

  /**
   * Whether the section is initially collapsed
   * @default false
   */
  defaultCollapsed?: boolean;

  /**
   * Filter type
   */
  type: 'checkbox' | 'range';

  /**
   * Checkbox options (for type: 'checkbox')
   */
  options?: FilterOption[];

  /**
   * Range configuration (for type: 'range')
   */
  range?: RangeFilter;
}

/**
 * FilterPanel component props interface
 */
export interface FilterPanelProps {
  /**
   * Filter sections to display
   */
  sections: FilterSection[];

  /**
   * Callback when a checkbox option is toggled
   */
  onCheckboxChange?: (sectionId: string, optionId: string, checked: boolean) => void;

  /**
   * Callback when a range value changes
   */
  onRangeChange?: (sectionId: string, rangeId: string, value: number) => void;

  /**
   * Callback when clear all button is clicked
   */
  onClearAll?: () => void;

  /**
   * Callback when apply button is clicked
   */
  onApply?: () => void;

  /**
   * Whether to show the apply button
   * @default false
   */
  showApplyButton?: boolean;

  /**
   * Whether to show the clear all button
   * @default true
   */
  showClearButton?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Title of the filter panel
   */
  title?: string;
}

/**
 * Collapsible filter section component
 */
interface FilterSectionComponentProps {
  section: FilterSection;
  onCheckboxChange?: (optionId: string, checked: boolean) => void;
  onRangeChange?: (rangeId: string, value: number) => void;
}

const FilterSectionComponent: React.FC<FilterSectionComponentProps> = ({
  section,
  onCheckboxChange,
  onRangeChange,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(section.defaultCollapsed ?? false);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className="border-b border-gray-200 last:border-b-0">
      {/* Section header */}
      <button
        type="button"
        onClick={toggleCollapse}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
        aria-expanded={!isCollapsed}
      >
        <span className="font-medium text-gray-900">{section.title}</span>
        {isCollapsed ? (
          <ChevronDownIcon className="h-5 w-5 text-gray-500" aria-hidden="true" />
        ) : (
          <ChevronUpIcon className="h-5 w-5 text-gray-500" aria-hidden="true" />
        )}
      </button>

      {/* Section content */}
      {!isCollapsed && (
        <div className="px-4 pb-4">
          {section.type === 'checkbox' && section.options && (
            <div className="space-y-2">
              {section.options.map((option) => (
                <label
                  key={option.id}
                  className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 rounded p-1"
                >
                  <input
                    type="checkbox"
                    checked={option.selected}
                    onChange={(e) => onCheckboxChange?.(option.id, e.target.checked)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="flex-1 text-sm text-gray-700">{option.label}</span>
                  {option.count !== undefined && (
                    <span className="text-xs text-gray-500">({option.count})</span>
                  )}
                </label>
              ))}
            </div>
          )}

          {section.type === 'range' && section.range && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{section.range.label}</span>
                <span className="text-sm font-medium text-gray-900">
                  {section.range.value}
                  {section.range.unit && ` ${section.range.unit}`}
                </span>
              </div>
              <input
                type="range"
                min={section.range.min}
                max={section.range.max}
                step={section.range.step ?? 1}
                value={section.range.value}
                onChange={(e) => onRangeChange?.(section.range!.id, Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                aria-label={section.range.label}
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>
                  {section.range.min}
                  {section.range.unit}
                </span>
                <span>
                  {section.range.max}
                  {section.range.unit}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * FilterPanel component with collapsible sections, checkboxes, and range sliders
 *
 * @example
 * ```tsx
 * const sections: FilterSection[] = [
 *   {
 *     id: 'dietary',
 *     title: 'Dietary Preferences',
 *     type: 'checkbox',
 *     options: [
 *       { id: 'veg', label: 'Vegetarian', selected: false, count: 45 },
 *       { id: 'vegan', label: 'Vegan', selected: true, count: 23 },
 *     ],
 *   },
 *   {
 *     id: 'nutrition',
 *     title: 'Nutrition',
 *     type: 'range',
 *     range: {
 *       id: 'protein',
 *       label: 'Minimum Protein',
 *       min: 0,
 *       max: 100,
 *       value: 30,
 *       unit: 'g',
 *     },
 *   },
 * ];
 *
 * <FilterPanel
 *   sections={sections}
 *   onCheckboxChange={(sectionId, optionId, checked) => {...}}
 *   onRangeChange={(sectionId, rangeId, value) => {...}}
 *   onApply={() => {...}}
 *   showApplyButton
 * />
 * ```
 */
export const FilterPanel: React.FC<FilterPanelProps> = ({
  sections,
  onCheckboxChange,
  onRangeChange,
  onClearAll,
  onApply,
  showApplyButton = false,
  showClearButton = true,
  className = '',
  title = 'Filters',
}) => {
  const handleCheckboxChange = (sectionId: string, optionId: string, checked: boolean) => {
    onCheckboxChange?.(sectionId, optionId, checked);
  };

  const handleRangeChange = (sectionId: string, rangeId: string, value: number) => {
    onRangeChange?.(sectionId, rangeId, value);
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {showClearButton && (
          <button
            type="button"
            onClick={onClearAll}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
            aria-label="Clear all filters"
          >
            <XMarkIcon className="h-4 w-4" aria-hidden="true" />
            Clear all
          </button>
        )}
      </div>

      {/* Sections */}
      <div className="divide-y divide-gray-200">
        {sections.map((section) => (
          <FilterSectionComponent
            key={section.id}
            section={section}
            onCheckboxChange={(optionId, checked) =>
              handleCheckboxChange(section.id, optionId, checked)
            }
            onRangeChange={(rangeId, value) => handleRangeChange(section.id, rangeId, value)}
          />
        ))}
      </div>

      {/* Apply button */}
      {showApplyButton && (
        <div className="border-t border-gray-200 px-4 py-3">
          <Button variant="primary" onClick={onApply} fullWidth>
            Apply Filters
          </Button>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
