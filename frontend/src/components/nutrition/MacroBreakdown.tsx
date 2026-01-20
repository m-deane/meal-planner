/**
 * Horizontal progress bars showing macro nutrients vs goals.
 */

import React from 'react';
import clsx from 'clsx';

// ============================================================================
// TYPES
// ============================================================================

interface MacroData {
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
}

interface MacroGoals {
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

interface MacroBreakdownProps {
  data: MacroData;
  goals: MacroGoals;
  title?: string;
}

interface MacroRow {
  label: string;
  current: number;
  goal: number;
  unit: string;
  color: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const MacroBreakdown: React.FC<MacroBreakdownProps> = ({
  data,
  goals,
  title = 'Macro Breakdown',
}) => {
  const macros: MacroRow[] = [
    {
      label: 'Protein',
      current: data.protein_g,
      goal: goals.protein_g,
      unit: 'g',
      color: 'bg-blue-500',
    },
    {
      label: 'Carbohydrates',
      current: data.carbohydrates_g,
      goal: goals.carbs_g,
      unit: 'g',
      color: 'bg-green-500',
    },
    {
      label: 'Fat',
      current: data.fat_g,
      goal: goals.fat_g,
      unit: 'g',
      color: 'bg-amber-500',
    },
    {
      label: 'Fiber',
      current: data.fiber_g,
      goal: goals.fiber_g,
      unit: 'g',
      color: 'bg-purple-500',
    },
  ];

  const getPercentage = (current: number, goal: number): number => {
    if (goal === 0) return 0;
    return Math.min((current / goal) * 100, 100);
  };

  const getStatusColor = (current: number, goal: number): string => {
    const percentage = (current / goal) * 100;

    if (percentage >= 90 && percentage <= 110) {
      return 'text-green-600';
    } else if (percentage >= 75 && percentage < 90) {
      return 'text-orange-600';
    } else if (percentage < 75) {
      return 'text-red-600';
    } else {
      return 'text-blue-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>

      <div className="space-y-6">
        {macros.map((macro) => {
          const percentage = getPercentage(macro.current, macro.goal);
          const statusColor = getStatusColor(macro.current, macro.goal);

          return (
            <div key={macro.label}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {macro.label}
                </span>
                <div className="flex items-center gap-2">
                  <span className={clsx('text-sm font-semibold', statusColor)}>
                    {macro.current.toFixed(1)} / {macro.goal.toFixed(0)} {macro.unit}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({percentage.toFixed(0)}%)
                  </span>
                </div>
              </div>

              <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={clsx(
                    'h-full rounded-full transition-all duration-300',
                    macro.color
                  )}
                  style={{ width: `${percentage}%` }}
                />

                {/* Goal marker */}
                {percentage < 100 && (
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-gray-400"
                    style={{ left: '100%' }}
                  />
                )}
              </div>

              {/* Additional info */}
              <div className="mt-1 flex items-center justify-between text-xs text-gray-500">
                <span>
                  {percentage < 90
                    ? `${(macro.goal - macro.current).toFixed(1)}${macro.unit} remaining`
                    : percentage > 110
                    ? `${(macro.current - macro.goal).toFixed(1)}${macro.unit} over`
                    : 'On target'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-600 mb-1">Total Macros</p>
            <p className="text-lg font-semibold text-gray-900">
              {(data.protein_g + data.carbohydrates_g + data.fat_g).toFixed(0)}g
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 mb-1">Total Goal</p>
            <p className="text-lg font-semibold text-gray-900">
              {(goals.protein_g + goals.carbs_g + goals.fat_g).toFixed(0)}g
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
