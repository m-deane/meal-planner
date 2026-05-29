/**
 * Draggable recipe card component for meal planner.
 */

import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import {
  ClockIcon,
  XMarkIcon,
  FireIcon,
  ScaleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '../common/Button';
import { Badge, BadgeGroup } from '../common/Badge';
import { getDifficultyColor, getDifficultyLabel } from '../../utils/recipeUtils';
import type { RecipeListItem } from '../../types';

// ============================================================================
// TYPES
// ============================================================================

export interface DraggableRecipeProps {
  recipe: RecipeListItem;
  servings?: number;
  onRemove?: () => void;
  dragId: string;
  compact?: boolean;
  showRemoveButton?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const DraggableRecipe: React.FC<DraggableRecipeProps> = ({
  recipe,
  servings,
  onRemove,
  dragId,
  compact = false,
  showRemoveButton = true,
}) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: dragId,
    data: {
      recipe,
      servings: servings ?? recipe.servings,
    },
  });

  const style: React.CSSProperties = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  const nutrition = recipe.nutrition_summary;
  const hasNutrition = nutrition != null && (nutrition.calories != null || nutrition.protein_g != null);

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      aria-label={`Recipe: ${recipe.name}. Press space or enter to pick up, arrow keys to move, space to drop.`}
      className={`
        relative bg-white rounded-lg border-2 border-gray-200
        hover:border-indigo-400 hover:shadow-md
        transition-all duration-200
        ${compact ? 'p-2' : 'p-3'}
        ${isDragging ? 'shadow-xl ring-2 ring-indigo-500' : ''}
      `}
    >
      {/* Remove Button */}
      {showRemoveButton && onRemove && (
        <div className="absolute -top-2 -right-2 z-10">
          <Button
            variant="danger"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            className="!p-0 w-6 h-6 rounded-full shadow-md"
            aria-label="Remove recipe"
          >
            <XMarkIcon className="w-4 h-4" aria-hidden="true" />
          </Button>
        </div>
      )}

      <div className="flex gap-3">
        {/* Recipe Image */}
        {recipe.main_image && (
          <div className={`flex-shrink-0 ${compact ? 'w-12 h-12' : 'w-16 h-16'}`}>
            <img
              src={recipe.main_image.url}
              alt={recipe.main_image.alt_text ?? recipe.name}
              className="w-full h-full object-cover rounded-md"
            />
          </div>
        )}

        {/* Recipe Info */}
        <div className="flex-1 min-w-0">
          <h4
            className={`
              font-semibold text-gray-900
              ${compact ? 'text-sm' : 'text-base'}
              line-clamp-2
            `}
            title={recipe.name}
          >
            {recipe.name}
          </h4>

          {/* Meta Info */}
          <div className={`flex items-center gap-3 mt-1 ${compact ? 'text-xs' : 'text-sm'} text-gray-600`}>
            {recipe.total_time_minutes && (
              <div className="flex items-center gap-1">
                <ClockIcon className="w-3 h-3" aria-hidden="true" />
                <span>{recipe.total_time_minutes}m</span>
              </div>
            )}

            {servings && (
              <div className="flex items-center gap-1">
                <span className="font-medium">{servings} servings</span>
              </div>
            )}
          </div>

          {/* Nutrition Badges */}
          {hasNutrition && !compact && (
            <BadgeGroup gap="sm" className="mt-2">
              {nutrition.calories && (
                <Badge
                  color="warning"
                  size="sm"
                  pill
                  icon={<FireIcon className="w-3 h-3" aria-hidden="true" />}
                >
                  {Math.round(nutrition.calories)}
                </Badge>
              )}
              {nutrition.protein_g && (
                <Badge
                  color="primary"
                  size="sm"
                  pill
                  icon={<ScaleIcon className="w-3 h-3" aria-hidden="true" />}
                >
                  {Math.round(nutrition.protein_g)}g
                </Badge>
              )}
            </BadgeGroup>
          )}

          {/* Dietary Tags (compact mode) */}
          {compact && recipe.dietary_tags.length > 0 && (
            <BadgeGroup gap="sm" className="mt-1 flex-wrap">
              {recipe.dietary_tags.slice(0, 2).map((tag) => (
                <Badge key={tag.id} color="info" size="sm">
                  {tag.name}
                </Badge>
              ))}
              {recipe.dietary_tags.length > 2 && (
                <Badge color="default" size="sm">
                  +{recipe.dietary_tags.length - 2}
                </Badge>
              )}
            </BadgeGroup>
          )}
        </div>
      </div>

      {/* Difficulty Badge */}
      {recipe.difficulty && !compact && (
        <div className="mt-2">
          <Badge color={getDifficultyColor(recipe.difficulty)} size="sm">
            {getDifficultyLabel(recipe.difficulty)}
          </Badge>
        </div>
      )}
    </div>
  );
};
