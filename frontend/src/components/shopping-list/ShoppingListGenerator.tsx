/**
 * Generate shopping list from meal plan with options.
 */

import React, { useState } from 'react';
import { ShoppingCart, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { useMealPlanStore } from '../../store/mealPlanStore';
import { useShoppingListStore } from '../../store/shoppingListStore';
import { useGenerateShoppingList } from '../../hooks/useShoppingList';
import type { ShoppingListGenerateRequest } from '../../types';

export interface ShoppingListGeneratorProps {
  className?: string;
}

export const ShoppingListGenerator: React.FC<ShoppingListGeneratorProps> = ({
  className = '',
}) => {
  const [showOptions, setShowOptions] = useState(false);
  const [servingsMultiplier, setServingsMultiplier] = useState(1);
  const [combineSimilar, setCombineSimilar] = useState(true);
  const [excludePantry, setExcludePantry] = useState(false);
  const [includeOptional, setIncludeOptional] = useState(false);
  const [roundQuantities, setRoundQuantities] = useState(true);

  const mealPlanStore = useMealPlanStore();
  const shoppingListStore = useShoppingListStore();
  const generateMutation = useGenerateShoppingList();

  const recipeIds = React.useMemo(() => {
    const ids = new Set<number>();
    const days = [
      'monday',
      'tuesday',
      'wednesday',
      'thursday',
      'friday',
      'saturday',
      'sunday',
    ] as const;

    days.forEach((day) => {
      const dayData = mealPlanStore.plan.days[day];
      if (dayData.breakfast?.recipe) ids.add(dayData.breakfast.recipe.id);
      if (dayData.lunch?.recipe) ids.add(dayData.lunch.recipe.id);
      if (dayData.dinner?.recipe) ids.add(dayData.dinner.recipe.id);
    });

    return Array.from(ids);
  }, [mealPlanStore.plan.days]);

  const hasRecipes = recipeIds.length > 0;

  const handleGenerate = async (): Promise<void> => {
    if (!hasRecipes) return;

    const options: Partial<ShoppingListGenerateRequest> = {
      servings_multiplier: servingsMultiplier,
      group_by_category: true,
      combine_similar_ingredients: combineSimilar,
      exclude_pantry_staples: excludePantry,
      include_optional_ingredients: includeOptional,
      round_quantities: roundQuantities,
    };

    try {
      const result = await generateMutation.mutateAsync({ recipeIds, options });

      // Extract all items from categories and transform to frontend format
      const allItems = result.categories.flatMap((category) =>
        category.items.map((item: Record<string, unknown>) => {
          // Get quantity and unit from the quantities array if available
          let quantity: number | null = null;
          let unit: string | null = null;

          const quantities = item.quantities as Array<{ unit?: string; total?: number }> | undefined;
          if (quantities && quantities.length > 0) {
            const firstQuantity = quantities[0];
            quantity = firstQuantity.total ?? null;
            unit = firstQuantity.unit ?? null;
          }

          // Transform backend format to frontend format
          return {
            ingredient_name: (item.name as string) ?? (item.ingredient_name as string) ?? 'Unknown',
            quantity,
            unit,
            category: (category.name?.toLowerCase().replace(/[^a-z]/g, '') ?? 'other') as import('../../types').IngredientCategory,
            is_optional: (item.is_optional as boolean) ?? false,
            notes: (item.notes as string) ?? null,
            recipe_count: (item.times_needed as number) ?? (item.recipe_count as number) ?? 1,
            recipe_names: (item.recipe_names as string[]) ?? [],
          };
        })
      );

      // Load into shopping list store
      shoppingListStore.loadFromResponse(allItems);
    } catch (error) {
      console.error('Failed to generate shopping list:', error);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Generate from Meal Plan
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {hasRecipes
              ? `${recipeIds.length} ${recipeIds.length === 1 ? 'recipe' : 'recipes'} in your meal plan`
              : 'No recipes in your meal plan'}
          </p>
        </div>

        <button
          onClick={() => setShowOptions(!showOptions)}
          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label={showOptions ? 'Hide options' : 'Show options'}
        >
          {showOptions ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Options */}
      {showOptions && (
        <div className="space-y-4 mb-4 pb-4 border-b border-gray-200">
          {/* Servings multiplier */}
          <div>
            <label
              htmlFor="servings-multiplier"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Servings Multiplier: {servingsMultiplier}x
            </label>
            <input
              id="servings-multiplier"
              type="range"
              min="0.5"
              max="3"
              step="0.5"
              value={servingsMultiplier}
              onChange={(e) => setServingsMultiplier(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>0.5x</span>
              <span>1x</span>
              <span>2x</span>
              <span>3x</span>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={combineSimilar}
                onChange={(e) => setCombineSimilar(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Combine similar ingredients
              </span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={excludePantry}
                onChange={(e) => setExcludePantry(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Exclude pantry staples (salt, pepper, oil, etc.)
              </span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeOptional}
                onChange={(e) => setIncludeOptional(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Include optional ingredients
              </span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={roundQuantities}
                onChange={(e) => setRoundQuantities(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                Round quantities to convenient amounts
              </span>
            </label>
          </div>
        </div>
      )}

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={!hasRecipes || generateMutation.isPending}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {generateMutation.isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <ShoppingCart className="w-5 h-5" />
            Generate Shopping List
          </>
        )}
      </button>

      {/* Error message */}
      {generateMutation.isError && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">
            Failed to generate shopping list. Please try again.
          </p>
        </div>
      )}

      {/* Success message */}
      {generateMutation.isSuccess && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-700">
            Shopping list generated successfully!
          </p>
        </div>
      )}
    </div>
  );
};
