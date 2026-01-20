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
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-gray-900">
            {Math.round(value)}{unit}
          </span>
          {goal && (
            <span className="text-xs text-gray-500">
              / {Math.round(goal)}{unit}
            </span>
          )}
        </div>
      </div>
      {goal && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
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
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-600" />
          Nutrition Summary
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Weekly Totals */}
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-indigo-600" />
            <h3 className="font-semibold text-gray-900">Weekly Totals</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Calories:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.calories).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Protein:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.protein_g)}g
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Carbs:</span>
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
            <div className="flex justify-between">
              <span className="text-gray-600">Fiber:</span>
              <span className="font-bold text-gray-900">
                {Math.round(weeklyNutrition.fiber_g)}g
              </span>
            </div>
          </div>
        </div>

        {/* Daily Average */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-4 h-4 text-green-600" />
            <h3 className="font-semibold text-gray-900">Daily Average</h3>
          </div>
          <div className="space-y-3">
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
          </div>

          {!hasGoals && (
            <p className="text-xs text-gray-500 mt-3 italic">
              Set nutrition goals to track progress
            </p>
          )}
        </div>

        {/* Recipe Stats */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Plan Stats</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <span className="text-sm text-gray-600">Total Meals</span>
              <span className="text-2xl font-bold text-purple-600">{totalRecipes}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <span className="text-sm text-gray-600">Unique Recipes</span>
              <span className="text-2xl font-bold text-purple-600">{uniqueRecipes}</span>
            </div>
            {totalRecipes > 0 && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <span className="text-sm text-gray-600">Variety</span>
                <span className="text-lg font-bold text-purple-600">
                  {Math.round((uniqueRecipes / totalRecipes) * 100)}%
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(weeklyNutrition.sugar_g)}g
            </div>
            <div className="text-xs text-gray-600">Sugar (weekly)</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(weeklyNutrition.sodium_mg).toLocaleString()}mg
            </div>
            <div className="text-xs text-gray-600">Sodium (weekly)</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(dailyAverage.fiber_g)}g
            </div>
            <div className="text-xs text-gray-600">Fiber (daily avg)</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(dailyAverage.sugar_g)}g
            </div>
            <div className="text-xs text-gray-600">Sugar (daily avg)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
