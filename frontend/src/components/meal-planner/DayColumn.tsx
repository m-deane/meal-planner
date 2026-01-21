/**
 * Day column component - contains all meal slots for a single day.
 */

import React from 'react';
import type { DayOfWeek, DayState } from '../../store/mealPlanStore';
import { useMealPlanStore } from '../../store/mealPlanStore';
import { MealSlot } from './MealSlot';
import { MealType } from '../../types';
import { Trash2, Calendar } from 'lucide-react';
import { format, addDays, parseISO } from 'date-fns';

// ============================================================================
// TYPES
// ============================================================================

export interface DayColumnProps {
  day: DayOfWeek;
  dayData: DayState;
  startDate?: string | null;
  showNutrition?: boolean;
}

// ============================================================================
// HELPERS
// ============================================================================

const getDayLabel = (day: DayOfWeek): string => {
  return day.charAt(0).toUpperCase() + day.slice(1);
};

const getDayIndex = (day: DayOfWeek): number => {
  const days: DayOfWeek[] = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  return days.indexOf(day);
};

const getFormattedDate = (startDate: string | null | undefined, day: DayOfWeek): string | null => {
  if (!startDate) return null;

  try {
    const start = parseISO(startDate);
    const dayIndex = getDayIndex(day);
    const date = addDays(start, dayIndex);
    return format(date, 'MMM d');
  } catch {
    return null;
  }
};

// ============================================================================
// COMPONENT
// ============================================================================

export const DayColumn: React.FC<DayColumnProps> = ({
  day,
  dayData,
  startDate,
  showNutrition = true,
}) => {
  const { removeRecipe, updateServings, clearDay, getDayNutrition } = useMealPlanStore();

  const formattedDate = getFormattedDate(startDate, day);
  const dayNutrition = showNutrition ? getDayNutrition(day) : null;
  const hasMeals = !!(dayData.breakfast || dayData.lunch || dayData.dinner);

  const handleClearDay = () => {
    if (hasMeals && window.confirm(`Clear all meals for ${getDayLabel(day)}?`)) {
      clearDay(day);
    }
  };

  return (
    <div className="flex flex-col bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Day Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 text-white p-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-lg">{getDayLabel(day)}</h3>
            {formattedDate && (
              <div className="flex items-center gap-1 text-xs text-indigo-100 mt-0.5">
                <Calendar className="w-3 h-3" />
                <span>{formattedDate}</span>
              </div>
            )}
          </div>

          {hasMeals && (
            <button
              onClick={handleClearDay}
              className="p-1.5 rounded hover:bg-indigo-400 transition-colors"
              title={`Clear ${getDayLabel(day)}`}
              aria-label={`Clear all meals for ${getDayLabel(day)}`}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Meal Slots */}
      <div className="flex-1 p-3 space-y-4">
        <MealSlot
          day={day}
          mealType={MealType.BREAKFAST}
          slot={dayData.breakfast}
          onRemove={() => removeRecipe(day, MealType.BREAKFAST)}
          onUpdateServings={(servings) => updateServings(day, MealType.BREAKFAST, servings)}
        />

        <MealSlot
          day={day}
          mealType={MealType.LUNCH}
          slot={dayData.lunch}
          onRemove={() => removeRecipe(day, MealType.LUNCH)}
          onUpdateServings={(servings) => updateServings(day, MealType.LUNCH, servings)}
        />

        <MealSlot
          day={day}
          mealType={MealType.DINNER}
          slot={dayData.dinner}
          onRemove={() => removeRecipe(day, MealType.DINNER)}
          onUpdateServings={(servings) => updateServings(day, MealType.DINNER, servings)}
        />
      </div>

      {/* Daily Nutrition Summary */}
      {showNutrition && dayNutrition && hasMeals && (
        <div className="border-t border-gray-200 bg-gray-50 p-3">
          <h4 className="text-xs font-semibold text-gray-700 mb-2">Daily Totals</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">Calories:</span>
              <span className="font-medium text-gray-900">
                {Math.round(dayNutrition.calories)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Protein:</span>
              <span className="font-medium text-gray-900">
                {Math.round(dayNutrition.protein_g)}g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Carbs:</span>
              <span className="font-medium text-gray-900">
                {Math.round(dayNutrition.carbohydrates_g)}g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Fat:</span>
              <span className="font-medium text-gray-900">
                {Math.round(dayNutrition.fat_g)}g
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
