/**
 * Meal slot component - a droppable zone for a single meal.
 */

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { MealType } from '../../types';
import type { MealSlotState, DayOfWeek } from '../../store/mealPlanStore';
import { DraggableRecipe } from './DraggableRecipe';
import { Coffee, Sun, Moon, Plus } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface MealSlotProps {
  day: DayOfWeek;
  mealType: MealType;
  slot: MealSlotState | null;
  onRemove: () => void;
  onUpdateServings?: (servings: number) => void;
}

// ============================================================================
// HELPERS
// ============================================================================

const getMealIcon = (mealType: MealType): React.ReactNode => {
  switch (mealType) {
    case 'breakfast':
      return <Coffee className="w-4 h-4" />;
    case 'lunch':
      return <Sun className="w-4 h-4" />;
    case 'dinner':
      return <Moon className="w-4 h-4" />;
    default:
      return <Plus className="w-4 h-4" />;
  }
};

const getMealLabel = (mealType: MealType): string => {
  return mealType.charAt(0).toUpperCase() + mealType.slice(1);
};

// ============================================================================
// COMPONENT
// ============================================================================

export const MealSlot: React.FC<MealSlotProps> = ({
  day,
  mealType,
  slot,
  onRemove,
  onUpdateServings,
}) => {
  const dropId = `${day}-${mealType}`;

  const { setNodeRef, isOver, active } = useDroppable({
    id: dropId,
    data: {
      day,
      mealType,
      accepts: ['recipe'],
    },
  });

  const isDraggingOver = isOver && active;
  const isEmpty = !slot;

  return (
    <div
      ref={setNodeRef}
      className={`
        relative min-h-[100px] rounded-lg border-2 transition-all duration-200
        ${isEmpty ? 'border-dashed' : 'border-solid'}
        ${
          isDraggingOver
            ? 'border-indigo-500 bg-indigo-50 shadow-lg scale-105'
            : isEmpty
            ? 'border-gray-300 bg-gray-50'
            : 'border-gray-200 bg-white'
        }
      `}
    >
      {/* Meal Type Label */}
      <div className="absolute -top-2 left-2 px-2 py-0.5 bg-white rounded-full border border-gray-300 shadow-sm">
        <div className="flex items-center gap-1 text-xs font-medium text-gray-700">
          {getMealIcon(mealType)}
          <span>{getMealLabel(mealType)}</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-3 pt-5">
        {isEmpty ? (
          // Empty State
          <div className="flex flex-col items-center justify-center text-center py-4">
            <div className="text-gray-400 mb-1">
              <Plus className="w-6 h-6 mx-auto" />
            </div>
            <p className="text-xs text-gray-500">
              {isDraggingOver ? 'Drop recipe here' : 'Drag a recipe here'}
            </p>
          </div>
        ) : slot.recipe ? (
          // Recipe Card
          <div>
            <DraggableRecipe
              recipe={slot.recipe}
              servings={slot.servings}
              onRemove={onRemove}
              dragId={`${day}-${mealType}-recipe`}
              compact
              showRemoveButton
            />

            {/* Servings Adjuster */}
            {onUpdateServings && (
              <div className="mt-2 flex items-center gap-2">
                <label className="text-xs text-gray-600">Servings:</label>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => onUpdateServings(Math.max(1, slot.servings - 1))}
                    className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300 text-gray-700 flex items-center justify-center text-sm font-medium"
                    aria-label="Decrease servings"
                  >
                    −
                  </button>
                  <span className="w-8 text-center text-sm font-medium">{slot.servings}</span>
                  <button
                    onClick={() => onUpdateServings(slot.servings + 1)}
                    className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300 text-gray-700 flex items-center justify-center text-sm font-medium"
                    aria-label="Increase servings"
                  >
                    +
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Drop Indicator Overlay */}
      {isDraggingOver && (
        <div className="absolute inset-0 border-2 border-indigo-500 rounded-lg pointer-events-none bg-indigo-100 bg-opacity-20">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
              Drop here
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
