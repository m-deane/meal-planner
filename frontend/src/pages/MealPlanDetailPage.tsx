/**
 * Meal plan detail page for viewing and exporting saved meal plans.
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useMealPlan,
  useDeleteMealPlan,
  useExportMealPlanMarkdown,
} from '../hooks/useMealPlan';
import {
  ArrowLeft,
  Download,
  Printer,
  ShoppingCart,
  Trash2,
  Calendar,
  TrendingUp,
  Loader2,
} from 'lucide-react';
import { format, parseISO } from 'date-fns';

// ============================================================================
// COMPONENT
// ============================================================================

export const MealPlanDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isPrintMode, setIsPrintMode] = useState(false);

  const mealPlanId = id ? parseInt(id, 10) : 0;
  const { data: mealPlan, isLoading, error } = useMealPlan(mealPlanId);
  const deleteMutation = useDeleteMealPlan();
  const exportMutation = useExportMealPlanMarkdown();

  const handleDelete = async () => {
    if (!mealPlan?.id) return;

    if (window.confirm('Are you sure you want to delete this meal plan?')) {
      try {
        await deleteMutation.mutateAsync(mealPlan.id);
        navigate('/meal-plans');
      } catch (error) {
        console.error('Failed to delete meal plan:', error);
        alert('Failed to delete meal plan. Please try again.');
      }
    }
  };

  const handleExportMarkdown = async () => {
    if (!mealPlan?.id) return;

    try {
      const markdown = await exportMutation.mutateAsync(mealPlan.id);

      // Download as file
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meal-plan-${mealPlan.id}.md`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export meal plan:', error);
      alert('Failed to export meal plan. Please try again.');
    }
  };

  const handlePrint = () => {
    setIsPrintMode(true);
    setTimeout(() => {
      window.print();
      setIsPrintMode(false);
    }, 100);
  };

  const handleGenerateShoppingList = () => {
    if (!mealPlan?.id) return;
    navigate(`/shopping-list?mealPlanId=${mealPlan.id}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error || !mealPlan) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-red-600 mb-4">Failed to load meal plan</p>
        <button
          onClick={() => navigate('/meal-plans')}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Meal Plans
        </button>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${isPrintMode ? 'print-mode' : ''}`}>
      {/* Header - Hide in print mode */}
      {!isPrintMode && (
        <header className="bg-white border-b border-gray-200 shadow-sm print:hidden">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => navigate('/meal-plans')}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Meal Plan Details</h1>
                  {mealPlan.start_date && mealPlan.end_date && (
                    <p className="text-sm text-gray-600 mt-1">
                      <Calendar className="w-4 h-4 inline mr-1" />
                      {format(parseISO(mealPlan.start_date), 'MMM d, yyyy')} -{' '}
                      {format(parseISO(mealPlan.end_date), 'MMM d, yyyy')}
                    </p>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handleGenerateShoppingList}
                  className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                >
                  <ShoppingCart className="w-4 h-4" />
                  Shopping List
                </button>

                <button
                  onClick={handleExportMarkdown}
                  disabled={exportMutation.isPending}
                  className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>

                <button
                  onClick={handlePrint}
                  className="flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Printer className="w-4 h-4" />
                  Print
                </button>

                <button
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                  className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Days</p>
                <p className="text-2xl font-bold text-gray-900">{mealPlan.total_days}</p>
              </div>
              <Calendar className="w-8 h-8 text-indigo-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Meals</p>
                <p className="text-2xl font-bold text-gray-900">{mealPlan.summary.total_meals}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Unique Recipes</p>
                <p className="text-2xl font-bold text-gray-900">{mealPlan.summary.unique_recipes}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Cook Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {mealPlan.summary.average_cooking_time
                    ? `${Math.round(mealPlan.summary.average_cooking_time)}m`
                    : 'N/A'}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Nutrition Overview */}
        {mealPlan.average_daily_nutrition && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Average Daily Nutrition</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Calories</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(mealPlan.average_daily_nutrition.calories ?? 0)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Protein</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(mealPlan.average_daily_nutrition.protein_g ?? 0)}g
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Carbs</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(mealPlan.average_daily_nutrition.carbohydrates_g ?? 0)}g
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Fat</p>
                <p className="text-xl font-bold text-gray-900">
                  {Math.round(mealPlan.average_daily_nutrition.fat_g ?? 0)}g
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Daily Meals */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold text-gray-900">Daily Meals</h2>
          {mealPlan.days.map((day) => (
            <div key={day.day} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Day {day.day}</h3>
                  {day.date && (
                    <p className="text-sm text-gray-600">
                      {format(parseISO(day.date), 'EEEE, MMM d')}
                    </p>
                  )}
                </div>
                {day.daily_nutrition && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">
                      {Math.round(day.daily_nutrition.calories ?? 0)} cal
                    </span>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                {day.meals.map((meal, index) => (
                  <div key={index} className="flex items-start gap-4 p-3 bg-gray-50 rounded-lg">
                    {meal.recipe.main_image && (
                      <img
                        src={meal.recipe.main_image.url}
                        alt={meal.recipe.name}
                        className="w-16 h-16 object-cover rounded"
                      />
                    )}
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-xs font-medium text-indigo-600 uppercase">
                            {meal.meal_type}
                          </span>
                          <h4 className="font-semibold text-gray-900">{meal.recipe.name}</h4>
                          <p className="text-sm text-gray-600">
                            {meal.servings} servings
                            {meal.recipe.total_time_minutes && (
                              <> • {meal.recipe.total_time_minutes} min</>
                            )}
                          </p>
                        </div>
                        {meal.nutrition && (
                          <div className="text-sm text-gray-600">
                            {Math.round(meal.nutrition.calories ?? 0)} cal
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          .print\\:hidden {
            display: none !important;
          }

          body {
            background: white;
          }

          .print-mode {
            background: white;
          }
        }
      `}</style>
    </div>
  );
};
