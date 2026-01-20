/**
 * Main nutrition dashboard container with grid layout and date range selector.
 */

import React, { useMemo } from 'react';
import { Calendar } from 'lucide-react';
import { useMealPlanStore, type DayOfWeek } from '../../store/mealPlanStore';
import { useNutritionGoalsStore } from '../../store/nutritionGoalsStore';
import { NutritionCard } from './NutritionCard';
import { MacroChart } from './MacroChart';
import { WeeklyTrends } from './WeeklyTrends';
import { DailyBreakdown } from './DailyBreakdown';
import { MacroBreakdown } from './MacroBreakdown';
import { NutritionGoals } from './NutritionGoals';

// ============================================================================
// TYPES
// ============================================================================

interface NutritionDashboardProps {
  className?: string;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const DAYS_OF_WEEK: DayOfWeek[] = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
];

const DAY_LABELS: Record<DayOfWeek, string> = {
  monday: 'Mon',
  tuesday: 'Tue',
  wednesday: 'Wed',
  thursday: 'Thu',
  friday: 'Fri',
  saturday: 'Sat',
  sunday: 'Sun',
};

// ============================================================================
// COMPONENT
// ============================================================================

export const NutritionDashboard: React.FC<NutritionDashboardProps> = ({
  className = '',
}) => {
  const { getDayNutrition, getDailyAverage, plan } = useMealPlanStore();
  const { goals } = useNutritionGoalsStore();

  // Calculate all nutrition data
  const dailyAverage = useMemo(() => getDailyAverage(), [getDailyAverage]);

  // Prepare weekly trends data
  const weeklyTrendsData = useMemo(() => {
    return DAYS_OF_WEEK.map((day) => {
      const nutrition = getDayNutrition(day);
      return {
        day: DAY_LABELS[day],
        calories: nutrition.calories,
        protein_g: nutrition.protein_g,
        carbohydrates_g: nutrition.carbohydrates_g,
        fat_g: nutrition.fat_g,
      };
    });
  }, [getDayNutrition]);

  // Prepare daily breakdown data
  const dailyBreakdownData = useMemo(() => {
    return DAYS_OF_WEEK.map((day) => {
      const dayData = plan.days[day];

      const breakfastCal =
        dayData.breakfast?.recipe?.nutrition_summary?.calories ?? 0;
      const lunchCal = dayData.lunch?.recipe?.nutrition_summary?.calories ?? 0;
      const dinnerCal = dayData.dinner?.recipe?.nutrition_summary?.calories ?? 0;

      return {
        day: DAY_LABELS[day],
        breakfast: breakfastCal,
        lunch: lunchCal,
        dinner: dinnerCal,
        total: breakfastCal + lunchCal + dinnerCal,
      };
    });
  }, [plan.days]);

  // Calculate macro data for chart
  const macroData = useMemo(() => {
    return {
      protein_g: dailyAverage.protein_g,
      carbohydrates_g: dailyAverage.carbohydrates_g,
      fat_g: dailyAverage.fat_g,
    };
  }, [dailyAverage]);

  // Calculate macro data including fiber for breakdown
  const macroBreakdownData = useMemo(() => {
    return {
      protein_g: dailyAverage.protein_g,
      carbohydrates_g: dailyAverage.carbohydrates_g,
      fat_g: dailyAverage.fat_g,
      fiber_g: dailyAverage.fiber_g,
    };
  }, [dailyAverage]);

  const hasData = weeklyTrendsData.some((day) => day.calories > 0);

  return (
    <div className={className}>
      {/* Header with date range */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Nutrition Dashboard
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Weekly nutrition overview and goals tracking
          </p>
        </div>

        {plan.startDate && (
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
            <Calendar className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">
              Week of {new Date(plan.startDate).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {!hasData && (
        <div className="mb-6 p-8 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
          <p className="text-yellow-800 font-medium mb-2">
            No meal plan data available
          </p>
          <p className="text-sm text-yellow-700">
            Add recipes to your meal plan to see nutrition analytics and trends.
          </p>
        </div>
      )}

      {/* Top Row - Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <NutritionCard
          label="Daily Calories"
          value={dailyAverage.calories}
          unit="cal"
          goal={goals.daily_calories}
          subtitle="Average per day"
          colorClass="text-blue-600"
          decimals={0}
        />

        <NutritionCard
          label="Daily Protein"
          value={dailyAverage.protein_g}
          unit="g"
          goal={goals.protein_g}
          subtitle="Average per day"
          colorClass="text-purple-600"
          decimals={1}
        />

        <NutritionCard
          label="Daily Carbs"
          value={dailyAverage.carbohydrates_g}
          unit="g"
          goal={goals.carbs_g}
          subtitle="Average per day"
          colorClass="text-green-600"
          decimals={1}
        />

        <NutritionCard
          label="Daily Fat"
          value={dailyAverage.fat_g}
          unit="g"
          goal={goals.fat_g}
          subtitle="Average per day"
          colorClass="text-amber-600"
          decimals={1}
        />
      </div>

      {/* Middle Row - Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <MacroChart data={macroData} />
        <WeeklyTrends
          data={weeklyTrendsData}
          calorieGoal={goals.daily_calories}
          proteinGoal={goals.protein_g}
        />
      </div>

      {/* Bottom Row - Detailed Views */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DailyBreakdown data={dailyBreakdownData} />
        </div>

        <div className="space-y-6">
          <MacroBreakdown
            data={macroBreakdownData}
            goals={{
              protein_g: goals.protein_g,
              carbs_g: goals.carbs_g,
              fat_g: goals.fat_g,
              fiber_g: goals.fiber_g,
            }}
          />
        </div>
      </div>

      {/* Goals Section */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <NutritionGoals />
        </div>

        {/* Additional Stats */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Weekly Summary
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Fiber</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.fiber_g.toFixed(1)}
                <span className="text-sm font-normal text-gray-500 ml-1">g</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Goal: {goals.fiber_g}g
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Sugar</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.sugar_g.toFixed(1)}
                <span className="text-sm font-normal text-gray-500 ml-1">g</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Average daily</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Sodium</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.sodium_mg.toFixed(0)}
                <span className="text-sm font-normal text-gray-500 ml-1">mg</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Average daily</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Protein %</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.calories > 0
                  ? ((dailyAverage.protein_g * 4) / dailyAverage.calories * 100).toFixed(0)
                  : 0}
                <span className="text-sm font-normal text-gray-500 ml-1">%</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Of total calories</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Carbs %</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.calories > 0
                  ? ((dailyAverage.carbohydrates_g * 4) / dailyAverage.calories * 100).toFixed(0)
                  : 0}
                <span className="text-sm font-normal text-gray-500 ml-1">%</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Of total calories</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Fat %</p>
              <p className="text-2xl font-bold text-gray-900">
                {dailyAverage.calories > 0
                  ? ((dailyAverage.fat_g * 9) / dailyAverage.calories * 100).toFixed(0)
                  : 0}
                <span className="text-sm font-normal text-gray-500 ml-1">%</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">Of total calories</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
