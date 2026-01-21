import React, { useState } from 'react';
import {
  ClockIcon,
  UserGroupIcon,
  SignalIcon,
  PrinterIcon,
  PlusCircleIcon,
  ShareIcon,
} from '@heroicons/react/24/outline';
import { Badge, BadgeGroup, Button } from '../common';
import { IngredientList } from './IngredientList';
import { InstructionSteps } from './InstructionSteps';
import { NutritionBadge } from './NutritionBadge';
import type { Recipe, DifficultyLevel } from '../../types';

/**
 * RecipeDetail component props
 */
export interface RecipeDetailProps {
  /**
   * Full recipe data to display
   */
  recipe: Recipe;

  /**
   * Callback when "Add to meal plan" button is clicked
   */
  onAddToMealPlan?: (recipe: Recipe) => void;

  /**
   * Callback when "Print" button is clicked
   */
  onPrint?: () => void;

  /**
   * Callback when "Share" button is clicked
   */
  onShare?: () => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get difficulty level color
 */
const getDifficultyColor = (difficulty: DifficultyLevel | null): 'success' | 'warning' | 'error' | 'default' => {
  switch (difficulty) {
    case 'easy':
      return 'success';
    case 'medium':
      return 'warning';
    case 'hard':
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Get difficulty level label
 */
const getDifficultyLabel = (difficulty: DifficultyLevel | null): string => {
  if (!difficulty) return 'Unknown';
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
};

/**
 * RecipeDetail component
 *
 * Full recipe display with large image, ingredients list, step-by-step
 * instructions, nutrition information, dietary tags, allergens, and actions.
 *
 * @example
 * ```tsx
 * <RecipeDetail
 *   recipe={recipeData}
 *   onAddToMealPlan={(recipe) => handleAddToMealPlan(recipe)}
 *   onPrint={() => window.print()}
 *   onShare={() => handleShare()}
 * />
 * ```
 */
export const RecipeDetail: React.FC<RecipeDetailProps> = ({
  recipe,
  onAddToMealPlan,
  onPrint,
  onShare,
  className = '',
}) => {
  const [servingsMultiplier, setServingsMultiplier] = useState(1);

  const mainImage = recipe.images.find((img) => img.image_type === 'main' || img.image_type === 'hero');
  const imageUrl = mainImage?.url || '/placeholder-recipe.jpg';
  const imageAlt = mainImage?.alt_text || recipe.name;

  const adjustedServings = recipe.servings * servingsMultiplier;

  const handleServingsDecrease = () => {
    if (servingsMultiplier > 0.5) {
      setServingsMultiplier((prev) => prev - 0.5);
    }
  };

  const handleServingsIncrease = () => {
    if (servingsMultiplier < 5) {
      setServingsMultiplier((prev) => prev + 0.5);
    }
  };

  return (
    <div className={`bg-white ${className}`}>
      {/* Hero image */}
      <div className="w-full h-96 overflow-hidden bg-gray-200">
        <img
          src={imageUrl}
          alt={imageAlt}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">{recipe.name}</h1>

          {recipe.description && (
            <p className="text-lg text-gray-600 mb-6">{recipe.description}</p>
          )}

          {/* Meta information */}
          <div className="flex flex-wrap items-center gap-6 mb-6">
            {recipe.total_time_minutes && (
              <div className="flex items-center gap-2">
                <ClockIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
                <div>
                  <div className="text-sm text-gray-500">Total Time</div>
                  <div className="text-lg font-semibold">{recipe.total_time_minutes} min</div>
                </div>
              </div>
            )}

            {recipe.prep_time_minutes && (
              <div className="flex items-center gap-2">
                <ClockIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
                <div>
                  <div className="text-sm text-gray-500">Prep Time</div>
                  <div className="text-lg font-semibold">{recipe.prep_time_minutes} min</div>
                </div>
              </div>
            )}

            {recipe.cooking_time_minutes && (
              <div className="flex items-center gap-2">
                <ClockIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
                <div>
                  <div className="text-sm text-gray-500">Cook Time</div>
                  <div className="text-lg font-semibold">{recipe.cooking_time_minutes} min</div>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <UserGroupIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
              <div>
                <div className="text-sm text-gray-500">Servings</div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleServingsDecrease}
                    className="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm font-semibold"
                    disabled={servingsMultiplier <= 0.5}
                  >
                    -
                  </button>
                  <span className="text-lg font-semibold min-w-[3rem] text-center">
                    {adjustedServings}
                  </span>
                  <button
                    type="button"
                    onClick={handleServingsIncrease}
                    className="px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm font-semibold"
                    disabled={servingsMultiplier >= 5}
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            {recipe.difficulty && (
              <div className="flex items-center gap-2">
                <SignalIcon className="h-6 w-6 text-gray-500" aria-hidden="true" />
                <div>
                  <div className="text-sm text-gray-500">Difficulty</div>
                  <Badge color={getDifficultyColor(recipe.difficulty)} size="md">
                    {getDifficultyLabel(recipe.difficulty)}
                  </Badge>
                </div>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-3">
            {onAddToMealPlan && (
              <Button
                variant="primary"
                onClick={() => onAddToMealPlan(recipe)}
                iconLeft={<PlusCircleIcon className="h-5 w-5" />}
              >
                Add to Meal Plan
              </Button>
            )}
            {onPrint && (
              <Button
                variant="secondary"
                onClick={onPrint}
                iconLeft={<PrinterIcon className="h-5 w-5" />}
              >
                Print
              </Button>
            )}
            {onShare && (
              <Button
                variant="secondary"
                onClick={onShare}
                iconLeft={<ShareIcon className="h-5 w-5" />}
              >
                Share
              </Button>
            )}
          </div>
        </div>

        {/* Tags and categories */}
        <div className="mb-8 space-y-4">
          {recipe.dietary_tags.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Dietary Tags</h3>
              <BadgeGroup gap="sm">
                {recipe.dietary_tags.map((tag) => (
                  <Badge key={tag.id} color="info" size="md">
                    {tag.name}
                  </Badge>
                ))}
              </BadgeGroup>
            </div>
          )}

          {recipe.categories.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Categories</h3>
              <BadgeGroup gap="sm">
                {recipe.categories.map((category) => (
                  <Badge key={category.id} color="default" size="md">
                    {category.name}
                  </Badge>
                ))}
              </BadgeGroup>
            </div>
          )}

          {recipe.allergens.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Allergens</h3>
              <BadgeGroup gap="sm">
                {recipe.allergens.map((allergen) => (
                  <Badge key={allergen.id} color="warning" size="md">
                    {allergen.name}
                  </Badge>
                ))}
              </BadgeGroup>
            </div>
          )}
        </div>

        {/* Nutrition information */}
        {recipe.nutritional_info && (
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Nutrition Information</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {recipe.nutritional_info.calories !== null && (
                <div className="text-center">
                  <NutritionBadge type="calories" value={recipe.nutritional_info.calories} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Calories</div>
                </div>
              )}
              {recipe.nutritional_info.protein_g !== null && (
                <div className="text-center">
                  <NutritionBadge type="protein" value={recipe.nutritional_info.protein_g} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Protein</div>
                </div>
              )}
              {recipe.nutritional_info.carbohydrates_g !== null && (
                <div className="text-center">
                  <NutritionBadge type="carbs" value={recipe.nutritional_info.carbohydrates_g} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Carbs</div>
                </div>
              )}
              {recipe.nutritional_info.fat_g !== null && (
                <div className="text-center">
                  <NutritionBadge type="fat" value={recipe.nutritional_info.fat_g} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Fat</div>
                </div>
              )}
              {recipe.nutritional_info.fiber_g !== null && (
                <div className="text-center">
                  <NutritionBadge type="fiber" value={recipe.nutritional_info.fiber_g} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Fiber</div>
                </div>
              )}
              {recipe.nutritional_info.sugar_g !== null && (
                <div className="text-center">
                  <NutritionBadge type="sugar" value={recipe.nutritional_info.sugar_g} size="md" />
                  <div className="text-sm text-gray-600 mt-1">Sugar</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Two-column layout for ingredients and instructions */}
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Ingredients */}
          <div className="md:col-span-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Ingredients</h2>
            <IngredientList
              ingredients={recipe.ingredients}
              servingsMultiplier={servingsMultiplier}
              showCheckboxes
              showPreparationNotes
            />
          </div>

          {/* Instructions */}
          <div className="md:col-span-2">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Instructions</h2>
            <InstructionSteps
              instructions={recipe.instructions}
              showCheckboxes
              expandable
            />
          </div>
        </div>

        {/* Footer metadata */}
        <div className="pt-6 border-t border-gray-200 text-sm text-gray-500">
          <p>
            Recipe ID: {recipe.gousto_id} | Last updated:{' '}
            {new Date(recipe.last_updated).toLocaleDateString()}
          </p>
          {recipe.source_url && (
            <p className="mt-1">
              Source:{' '}
              <a
                href={recipe.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {recipe.source_url}
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecipeDetail;
