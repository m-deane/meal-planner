import React, { useState } from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';
import type { Ingredient } from '../../types';

/**
 * IngredientList component props
 */
export interface IngredientListProps {
  /**
   * Array of ingredients to display
   */
  ingredients: Ingredient[];

  /**
   * Whether to show checkboxes for each ingredient
   * @default true
   */
  showCheckboxes?: boolean;

  /**
   * Callback when an ingredient is checked/unchecked
   */
  onIngredientToggle?: (ingredientName: string, checked: boolean) => void;

  /**
   * Set of ingredient names that are initially checked
   */
  checkedIngredients?: Set<string>;

  /**
   * Whether to show preparation notes
   * @default true
   */
  showPreparationNotes?: boolean;

  /**
   * Servings multiplier (for scaling quantities)
   * @default 1
   */
  servingsMultiplier?: number;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Individual ingredient item component
 */
interface IngredientItemProps {
  ingredient: Ingredient;
  checked: boolean;
  onToggle: (checked: boolean) => void;
  showCheckbox: boolean;
  showPreparationNote: boolean;
  servingsMultiplier: number;
}

const IngredientItem: React.FC<IngredientItemProps> = ({
  ingredient,
  checked,
  onToggle,
  showCheckbox,
  showPreparationNote,
  servingsMultiplier,
}) => {
  const scaledQuantity = ingredient.quantity
    ? (ingredient.quantity * servingsMultiplier).toFixed(1).replace(/\.0$/, '')
    : null;

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onToggle(e.target.checked);
  };

  return (
    <li
      className={`
        flex items-start gap-3 py-2 px-3 rounded-lg transition-colors
        ${checked ? 'bg-gray-50 text-gray-500' : 'hover:bg-gray-50'}
      `}
    >
      {showCheckbox && (
        <button
          type="button"
          onClick={() => onToggle(!checked)}
          className="flex-shrink-0 pt-0.5 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
          aria-label={`Mark ${ingredient.name} as ${checked ? 'unchecked' : 'checked'}`}
        >
          {checked ? (
            <CheckCircleIconSolid className="h-5 w-5 text-green-600" aria-hidden="true" />
          ) : (
            <CheckCircleIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          )}
        </button>
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2 flex-wrap">
          {scaledQuantity && (
            <span className={`font-medium ${checked ? 'line-through' : ''}`}>
              {scaledQuantity}
            </span>
          )}
          {ingredient.unit_name && (
            <span className={`text-sm text-gray-600 ${checked ? 'line-through' : ''}`}>
              {ingredient.unit_name}
            </span>
          )}
          <span className={`${checked ? 'line-through' : ''}`}>
            {ingredient.name}
            {ingredient.is_optional && (
              <span className="ml-1 text-sm text-gray-500 italic">(optional)</span>
            )}
          </span>
        </div>

        {showPreparationNote && ingredient.preparation_note && (
          <p className="mt-1 text-sm text-gray-500 italic">
            {ingredient.preparation_note}
          </p>
        )}

        {ingredient.category && (
          <span className="inline-block mt-1 text-xs text-gray-400 uppercase tracking-wide">
            {ingredient.category}
          </span>
        )}
      </div>
    </li>
  );
};

/**
 * IngredientList component
 *
 * Displays a list of recipe ingredients with optional checkboxes, quantities,
 * preparation notes, and servings scaling.
 *
 * @example
 * ```tsx
 * <IngredientList
 *   ingredients={recipe.ingredients}
 *   showCheckboxes
 *   onIngredientToggle={(name, checked) => console.log(name, checked)}
 *   servingsMultiplier={2}
 * />
 * ```
 */
export const IngredientList: React.FC<IngredientListProps> = ({
  ingredients,
  showCheckboxes = true,
  onIngredientToggle,
  checkedIngredients = new Set(),
  showPreparationNotes = true,
  servingsMultiplier = 1,
  className = '',
}) => {
  const [internalChecked, setInternalChecked] = useState<Set<string>>(checkedIngredients);

  const handleToggle = (ingredientName: string, checked: boolean) => {
    const newChecked = new Set(internalChecked);
    if (checked) {
      newChecked.add(ingredientName);
    } else {
      newChecked.delete(ingredientName);
    }
    setInternalChecked(newChecked);
    onIngredientToggle?.(ingredientName, checked);
  };

  // Sort ingredients by display_order
  const sortedIngredients = [...ingredients].sort(
    (a, b) => a.display_order - b.display_order
  );

  // Group ingredients by category if categories exist
  const groupedIngredients = sortedIngredients.reduce((acc, ingredient) => {
    const category = ingredient.category || 'Ingredients';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(ingredient);
    return acc;
  }, {} as Record<string, Ingredient[]>);

  const hasCategories = Object.keys(groupedIngredients).length > 1;

  if (!hasCategories) {
    return (
      <ul className={`space-y-1 ${className}`}>
        {sortedIngredients.map((ingredient, index) => (
          <IngredientItem
            key={`${ingredient.name}-${index}`}
            ingredient={ingredient}
            checked={internalChecked.has(ingredient.name)}
            onToggle={(checked) => handleToggle(ingredient.name, checked)}
            showCheckbox={showCheckboxes}
            showPreparationNote={showPreparationNotes}
            servingsMultiplier={servingsMultiplier}
          />
        ))}
      </ul>
    );
  }

  return (
    <div className={className}>
      {Object.entries(groupedIngredients).map(([category, categoryIngredients]) => (
        <div key={category} className="mb-6 last:mb-0">
          <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
            {category}
          </h4>
          <ul className="space-y-1">
            {categoryIngredients.map((ingredient, index) => (
              <IngredientItem
                key={`${ingredient.name}-${index}`}
                ingredient={ingredient}
                checked={internalChecked.has(ingredient.name)}
                onToggle={(checked) => handleToggle(ingredient.name, checked)}
                showCheckbox={showCheckboxes}
                showPreparationNote={showPreparationNotes}
                servingsMultiplier={servingsMultiplier}
              />
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default IngredientList;
