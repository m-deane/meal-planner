import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ClockIcon,
  PlusCircleIcon,
  SignalIcon,
} from '@heroicons/react/24/outline';
import { Card, Badge, BadgeGroup } from '../common';
import { NutritionBadge } from './NutritionBadge';
import type { RecipeListItem, DifficultyLevel } from '../../types';

/**
 * RecipeCard component props
 */
export interface RecipeCardProps {
  /**
   * Recipe data to display
   */
  recipe: RecipeListItem;

  /**
   * Callback when "Add to meal plan" button is clicked
   */
  onAddToMealPlan?: (recipe: RecipeListItem) => void;

  /**
   * Whether to show nutrition badges
   * @default true
   */
  showNutrition?: boolean;

  /**
   * Whether to show category tags
   * @default true
   */
  showCategories?: boolean;

  /**
   * Whether to show dietary tags
   * @default true
   */
  showDietaryTags?: boolean;

  /**
   * Maximum number of categories to display
   * @default 3
   */
  maxCategories?: number;

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
 * RecipeCard component
 *
 * Displays a recipe in a card format with image, name, cooking time,
 * difficulty, nutrition badges, and category tags. Includes hover effects
 * and navigation to recipe detail page.
 *
 * @example
 * ```tsx
 * <RecipeCard
 *   recipe={recipeData}
 *   onAddToMealPlan={(recipe) => console.log('Add to meal plan:', recipe)}
 *   showNutrition
 *   showCategories
 * />
 * ```
 */
export const RecipeCard: React.FC<RecipeCardProps> = ({
  recipe,
  onAddToMealPlan,
  showNutrition = true,
  showCategories = true,
  showDietaryTags = true,
  maxCategories = 3,
  className = '',
}) => {
  const navigate = useNavigate();

  const handleCardClick = () => {
    navigate(`/recipes/${recipe.slug}`);
  };

  const handleAddToMealPlan = (e: React.MouseEvent) => {
    e.stopPropagation();
    onAddToMealPlan?.(recipe);
  };

  const mainImage = recipe.main_image?.url || '/placeholder-recipe.jpg';
  const altText = recipe.main_image?.alt_text || recipe.name;

  // Filter categories by type for display
  const displayCategories = showCategories
    ? recipe.categories.slice(0, maxCategories)
    : [];

  const displayDietaryTags = showDietaryTags
    ? recipe.dietary_tags.slice(0, 3)
    : [];

  return (
    <Card
      image={{
        src: mainImage,
        alt: altText,
        aspectRatio: 'video',
      }}
      hoverable
      onClick={handleCardClick}
      className={className}
      padding="none"
    >
      <div className="p-4 space-y-3">
        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 min-h-[3.5rem]">
          {recipe.name}
        </h3>

        {/* Description */}
        {recipe.description && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {recipe.description}
          </p>
        )}

        {/* Meta information */}
        <div className="flex items-center gap-4 text-sm text-gray-600">
          {recipe.total_time_minutes && (
            <div className="flex items-center gap-1">
              <ClockIcon className="h-4 w-4" aria-hidden="true" />
              <span>{recipe.total_time_minutes} min</span>
            </div>
          )}

          {recipe.difficulty && (
            <div className="flex items-center gap-1">
              <SignalIcon className="h-4 w-4" aria-hidden="true" />
              <Badge
                color={getDifficultyColor(recipe.difficulty)}
                size="sm"
              >
                {getDifficultyLabel(recipe.difficulty)}
              </Badge>
            </div>
          )}

          {recipe.servings > 0 && (
            <span>{recipe.servings} servings</span>
          )}
        </div>

        {/* Nutrition badges */}
        {showNutrition && recipe.nutrition_summary && (
          <BadgeGroup gap="sm">
            {recipe.nutrition_summary.calories !== null &&
              recipe.nutrition_summary.calories !== undefined && (
                <NutritionBadge
                  type="calories"
                  value={recipe.nutrition_summary.calories}
                />
              )}
            {recipe.nutrition_summary.protein_g !== null &&
              recipe.nutrition_summary.protein_g !== undefined && (
                <NutritionBadge
                  type="protein"
                  value={recipe.nutrition_summary.protein_g}
                />
              )}
            {recipe.nutrition_summary.carbohydrates_g !== null &&
              recipe.nutrition_summary.carbohydrates_g !== undefined && (
                <NutritionBadge
                  type="carbs"
                  value={recipe.nutrition_summary.carbohydrates_g}
                />
              )}
          </BadgeGroup>
        )}

        {/* Dietary tags */}
        {displayDietaryTags.length > 0 && (
          <BadgeGroup gap="sm">
            {displayDietaryTags.map((tag) => (
              <Badge key={tag.id} color="info" size="sm">
                {tag.name}
              </Badge>
            ))}
          </BadgeGroup>
        )}

        {/* Category tags */}
        {displayCategories.length > 0 && (
          <BadgeGroup gap="sm">
            {displayCategories.map((category) => (
              <Badge key={category.id} color="default" size="sm">
                {category.name}
              </Badge>
            ))}
            {recipe.categories.length > maxCategories && (
              <Badge color="default" size="sm">
                +{recipe.categories.length - maxCategories}
              </Badge>
            )}
          </BadgeGroup>
        )}

        {/* Add to meal plan button */}
        {onAddToMealPlan && (
          <button
            type="button"
            onClick={handleAddToMealPlan}
            className="
              w-full flex items-center justify-center gap-2 px-4 py-2
              bg-blue-600 text-white rounded-lg font-medium
              hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              transition-colors
            "
            aria-label={`Add ${recipe.name} to meal plan`}
          >
            <PlusCircleIcon className="h-5 w-5" aria-hidden="true" />
            Add to Meal Plan
          </button>
        )}
      </div>
    </Card>
  );
};

export default RecipeCard;
