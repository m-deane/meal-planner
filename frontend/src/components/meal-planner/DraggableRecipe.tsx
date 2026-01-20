/**
 * Draggable recipe card component for meal planner.
 */

import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { RecipeListItem } from '../../types';
import { Clock, X, Flame, Drumstick } from 'lucide-react';

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
  const hasNutrition = nutrition && (nutrition.calories || nutrition.protein_g);

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
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
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="
            absolute -top-2 -right-2 z-10
            w-6 h-6 rounded-full
            bg-red-500 hover:bg-red-600
            text-white
            flex items-center justify-center
            shadow-md
            transition-colors
          "
          aria-label="Remove recipe"
        >
          <X className="w-4 h-4" />
        </button>
      )}

      <div className="flex gap-3">
        {/* Recipe Image */}
        {recipe.main_image && (
          <div className={`flex-shrink-0 ${compact ? 'w-12 h-12' : 'w-16 h-16'}`}>
            <img
              src={recipe.main_image.url}
              alt={recipe.main_image.alt_text || recipe.name}
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
                <Clock className="w-3 h-3" />
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
            <div className="flex items-center gap-2 mt-2">
              {nutrition.calories && (
                <div className="flex items-center gap-1 px-2 py-0.5 bg-orange-100 rounded-full text-xs text-orange-800">
                  <Flame className="w-3 h-3" />
                  <span>{Math.round(nutrition.calories)}</span>
                </div>
              )}
              {nutrition.protein_g && (
                <div className="flex items-center gap-1 px-2 py-0.5 bg-blue-100 rounded-full text-xs text-blue-800">
                  <Drumstick className="w-3 h-3" />
                  <span>{Math.round(nutrition.protein_g)}g</span>
                </div>
              )}
            </div>
          )}

          {/* Dietary Tags (compact mode) */}
          {compact && recipe.dietary_tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {recipe.dietary_tags.slice(0, 2).map((tag) => (
                <span
                  key={tag.id}
                  className="px-1.5 py-0.5 bg-green-100 text-green-800 text-xs rounded"
                >
                  {tag.name}
                </span>
              ))}
              {recipe.dietary_tags.length > 2 && (
                <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                  +{recipe.dietary_tags.length - 2}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Difficulty Badge */}
      {recipe.difficulty && !compact && (
        <div className="mt-2">
          <span
            className={`
              inline-block px-2 py-1 rounded text-xs font-medium
              ${
                recipe.difficulty === 'easy'
                  ? 'bg-green-100 text-green-800'
                  : recipe.difficulty === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }
            `}
          >
            {recipe.difficulty.charAt(0).toUpperCase() + recipe.difficulty.slice(1)}
          </span>
        </div>
      )}
    </div>
  );
};
