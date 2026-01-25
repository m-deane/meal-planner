/**
 * Weekly nutrition summary component with goals tracking.
 */

import React from 'react';
import { useMealPlanStore } from '../../store/mealPlanStore';
import { TrendingUp, Target, Activity } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface NutritionSummaryProps {
  className?: string;
}

interface NutritionBarProps {
  label: string;
  value: number;
  goal?: number | undefined;
  unit: string;
  color: string;
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const NutritionBar: React.FC<NutritionBarProps> = ({
  label,
  value,
  goal,
  unit,
  color,
}) => {
  const percentage = goal ? Math.min((value / goal) * 100, 100) : 0;
  const isOverGoal = goal && value > goal;

  return (
    <div>
      <div className="flex items-center justify-between mb-0.5">
        <span className="text-xs font-medium text-gray-700">{label}</span>
        <div className="flex items-center gap-1">
          <span className="text-xs font-bold text-gray-900">
            {Math.round(value)}{unit}
          </span>
          {goal && (
            <span className="text-xs text-gray-500">
              /{Math.round(goal)}
            </span>
          )}
        </div>
      </div>
      {goal && (
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-300 ${
              isOverGoal ? 'bg-red-500' : color
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const NutritionSummary: React.FC<NutritionSummaryProps> = ({ className = '' }) => {
  const {
    getWeeklyNutrition,
    getDailyAverage,
    getTotalRecipes,
    getUniqueRecipes,
    plan,
  } = useMealPlanStore();

  const weeklyNutrition = getWeeklyNutrition();
  const dailyAverage = getDailyAverage();
  const totalRecipes = getTotalRecipes();
  const uniqueRecipes = getUniqueRecipes();
  const goals = plan.nutritionGoals;

  const hasGoals = !!(
    goals.daily_calories ||
    goals.daily_protein_g ||
    goals.daily_carbs_g ||
    goals.daily_fat_g
  );

  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 p-4 ${className}`}>
      {/* Compact header inline with first row */}
      <div className="flex items-center gap-2 mb-3">
        <Activity className="w-4 h-4 text-indigo-600" />
        <h2 className="text-base font-bold text-gray-900">Nutrition Summary</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Weekly Totals - Compact */}
        <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
            <h3 className="text-sm font-semibold text-gray-900">Weekly</h3>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">Cal:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.calories).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Pro:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.protein_g)}g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Carb:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.carbohydrates_g)}g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Fat:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.fat_g)}g
              </span>
            </div>
          </div>
        </div>

        {/* Daily Average - Compact */}
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Target className="w-3.5 h-3.5 text-green-600" />
            <h3 className="text-sm font-semibold text-gray-900">Daily Avg</h3>
          </div>
          <div className="space-y-1.5">
            <NutritionBar
              label="Calories"
              value={dailyAverage.calories}
              goal={goals.daily_calories ?? undefined}
              unit=""
              color="bg-orange-500"
            />
            <NutritionBar
              label="Protein"
              value={dailyAverage.protein_g}
              goal={goals.daily_protein_g ?? undefined}
              unit="g"
              color="bg-blue-500"
            />
            {hasGoals && (
              <>
                <NutritionBar
                  label="Carbs"
                  value={dailyAverage.carbohydrates_g}
                  goal={goals.daily_carbs_g ?? undefined}
                  unit="g"
                  color="bg-yellow-500"
                />
                <NutritionBar
                  label="Fat"
                  value={dailyAverage.fat_g}
                  goal={goals.daily_fat_g ?? undefined}
                  unit="g"
                  color="bg-purple-500"
                />
              </>
            )}
          </div>
        </div>

        {/* Plan Stats - Compact inline */}
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Plan Stats</h3>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between px-2 py-1.5 bg-white rounded">
              <span className="text-xs text-gray-600">Meals</span>
              <span className="text-lg font-bold text-purple-600">{totalRecipes}</span>
            </div>
            <div className="flex items-center justify-between px-2 py-1.5 bg-white rounded">
              <span className="text-xs text-gray-600">Unique</span>
              <span className="text-lg font-bold text-purple-600">{uniqueRecipes}</span>
            </div>
            {totalRecipes > 0 && (
              <div className="flex items-center justify-between px-2 py-1.5 bg-white rounded">
                <span className="text-xs text-gray-600">Variety</span>
                <span className="text-sm font-bold text-purple-600">
                  {Math.round((uniqueRecipes / totalRecipes) * 100)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Additional Metrics - Compact grid */}
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">More</h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="text-center px-2 py-1 bg-white rounded">
              <div className="text-sm font-bold text-gray-900">
                {Math.round(weeklyNutrition.sugar_g)}g
              </div>
              <div className="text-xs text-gray-500">Sugar/wk</div>
            </div>
            <div className="text-center px-2 py-1 bg-white rounded">
              <div className="text-sm font-bold text-gray-900">
                {Math.round(weeklyNutrition.fiber_g)}g
              </div>
              <div className="text-xs text-gray-500">Fiber/wk</div>
            </div>
            <div className="text-center px-2 py-1 bg-white rounded">
              <div className="text-sm font-bold text-gray-900">
                {Math.round(dailyAverage.fiber_g)}g
              </div>
              <div className="text-xs text-gray-500">Fiber/day</div>
            </div>
            <div className="text-center px-2 py-1 bg-white rounded">
              <div className="text-sm font-bold text-gray-900">
                {(weeklyNutrition.sodium_mg / 1000).toFixed(1)}k
              </div>
              <div className="text-xs text-gray-500">Na mg/wk</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
