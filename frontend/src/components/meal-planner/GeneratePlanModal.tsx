/**
 * Modal for meal plan generation with configuration options.
 */

import React, { useState, useMemo } from 'react';
import type { MealPlanGenerateRequest } from '../../types';
import { X, Loader2, Sparkles, Info } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface GeneratePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: MealPlanGenerateRequest & { useNutritionEndpoint?: boolean }) => void;
  isGenerating?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const GeneratePlanModal: React.FC<GeneratePlanModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  isGenerating = false,
}) => {
  const [formData, setFormData] = useState({
    days: 7,
    include_breakfast: true,
    include_lunch: true,
    include_dinner: true,
    // Meal counts - how many of each meal to plan
    num_breakfasts: 7,
    num_lunches: 7,
    num_dinners: 7,
    // Use custom meal counts instead of days
    use_custom_meal_counts: false,
    target_calories: '',
    target_protein_g: '',
    max_cooking_time: '',
    avoid_duplicate_recipes: true,
    optimize_shopping_list: true,
    // Use nutrition endpoint for accurate nutrition data
    include_nutrition_data: true,
  });

  // Calculate total meals based on mode
  const totalMeals = useMemo(() => {
    if (formData.use_custom_meal_counts) {
      return formData.num_breakfasts + formData.num_lunches + formData.num_dinners;
    }
    let total = 0;
    if (formData.include_breakfast) total += formData.days;
    if (formData.include_lunch) total += formData.days;
    if (formData.include_dinner) total += formData.days;
    return total;
  }, [formData]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const request: MealPlanGenerateRequest & {
      useNutritionEndpoint?: boolean;
      mealCounts?: { breakfasts: number; lunches: number; dinners: number };
    } = {
      days: formData.days,
      meal_preferences: {
        include_breakfast: formData.use_custom_meal_counts
          ? formData.num_breakfasts > 0
          : formData.include_breakfast,
        include_lunch: formData.use_custom_meal_counts
          ? formData.num_lunches > 0
          : formData.include_lunch,
        include_dinner: formData.use_custom_meal_counts
          ? formData.num_dinners > 0
          : formData.include_dinner,
        include_snacks: false,
      },
      avoid_duplicate_recipes: formData.avoid_duplicate_recipes,
      max_recipe_reuse: formData.avoid_duplicate_recipes ? 1 : 3,
      variety_score_weight: 0.3,
      optimize_shopping_list: formData.optimize_shopping_list,
      // Use nutrition endpoint for accurate nutrition data
      useNutritionEndpoint: formData.include_nutrition_data,
    };

    // Add custom meal counts if enabled
    if (formData.use_custom_meal_counts) {
      request.mealCounts = {
        breakfasts: formData.num_breakfasts,
        lunches: formData.num_lunches,
        dinners: formData.num_dinners,
      };
    }

    // Add nutrition constraints if provided
    if (formData.target_calories || formData.target_protein_g) {
      request.nutrition_constraints = {};
      request.nutrition_goals = {};
      if (formData.target_calories) {
        request.nutrition_constraints.target_calories = Number(formData.target_calories);
        request.nutrition_goals.daily_calories = Number(formData.target_calories);
      }
      if (formData.target_protein_g) {
        request.nutrition_constraints.target_protein_g = Number(formData.target_protein_g);
        request.nutrition_goals.daily_protein_g = Number(formData.target_protein_g);
      }
    }

    // Add cooking time filter
    if (formData.max_cooking_time) {
      request.max_cooking_time = Number(formData.max_cooking_time);
    }

    onGenerate(request);
  };

  const handleChange = (key: string, value: unknown) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-gray-900">Generate Meal Plan</h2>
          </div>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="p-1 rounded-lg hover:bg-gray-100 disabled:opacity-50"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Planning Mode Toggle */}
          <div className="bg-gray-50 rounded-lg p-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.use_custom_meal_counts}
                onChange={(e) => handleChange('use_custom_meal_counts', e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Custom meal counts
              </span>
              <div className="relative group">
                <Info className="w-4 h-4 text-gray-400" />
                <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-10">
                  Enable to specify exact number of each meal type. Useful when some meals cover multiple days (e.g., batch cooking).
                </div>
              </div>
            </label>
          </div>

          {!formData.use_custom_meal_counts ? (
            <>
              {/* Days Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Days
                </label>
                <div className="flex gap-2">
                  {[3, 5, 7].map((days) => (
                    <button
                      key={days}
                      type="button"
                      onClick={() => handleChange('days', days)}
                      className={`
                        flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                        ${
                          formData.days === days
                            ? 'bg-indigo-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {days} Days
                    </button>
                  ))}
                </div>
              </div>

              {/* Meal Types */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Include Meals
                </label>
                <div className="space-y-2">
                  {[
                    { key: 'include_breakfast', label: 'Breakfast' },
                    { key: 'include_lunch', label: 'Lunch' },
                    { key: 'include_dinner', label: 'Dinner' },
                  ].map(({ key, label }) => (
                    <label key={key} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData[key as keyof typeof formData] as boolean}
                        onChange={(e) => handleChange(key, e.target.checked)}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-700">{label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Custom Meal Counts */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Each Meal
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Specify exactly how many of each meal to plan. Set to 0 to skip a meal type.
                  Lower counts mean some meals cover multiple days.
                </p>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">
                      Breakfasts
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="14"
                      value={formData.num_breakfasts}
                      onChange={(e) => handleChange('num_breakfasts', Math.max(0, Math.min(14, Number(e.target.value))))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">
                      Lunches
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="14"
                      value={formData.num_lunches}
                      onChange={(e) => handleChange('num_lunches', Math.max(0, Math.min(14, Number(e.target.value))))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">
                      Dinners
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="14"
                      value={formData.num_dinners}
                      onChange={(e) => handleChange('num_dinners', Math.max(0, Math.min(14, Number(e.target.value))))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Days for custom mode */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plan Duration (Days)
                </label>
                <div className="flex gap-2">
                  {[3, 5, 7].map((days) => (
                    <button
                      key={days}
                      type="button"
                      onClick={() => handleChange('days', days)}
                      className={`
                        flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                        ${
                          formData.days === days
                            ? 'bg-indigo-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {days} Days
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Total Meals Summary */}
          <div className="bg-indigo-50 rounded-lg p-3 flex items-center justify-between">
            <span className="text-sm text-indigo-700">Total meals to generate:</span>
            <span className="text-lg font-bold text-indigo-600">{totalMeals}</span>
          </div>

          {/* Nutrition Constraints */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nutrition Goals (Optional)
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">
                  Target Daily Calories
                </label>
                <input
                  type="number"
                  value={formData.target_calories}
                  onChange={(e) => handleChange('target_calories', e.target.value)}
                  placeholder="e.g., 2000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">
                  Target Daily Protein (g)
                </label>
                <input
                  type="number"
                  value={formData.target_protein_g}
                  onChange={(e) => handleChange('target_protein_g', e.target.value)}
                  placeholder="e.g., 150"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Cooking Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Cooking Time (minutes)
            </label>
            <input
              type="number"
              value={formData.max_cooking_time}
              onChange={(e) => handleChange('max_cooking_time', e.target.value)}
              placeholder="e.g., 45"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Options
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.include_nutrition_data}
                  onChange={(e) => handleChange('include_nutrition_data', e.target.checked)}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">
                  Include nutrition information (recommended)
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.avoid_duplicate_recipes}
                  onChange={(e) => handleChange('avoid_duplicate_recipes', e.target.checked)}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">
                  Avoid duplicate recipes (maximize variety)
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.optimize_shopping_list}
                  onChange={(e) => handleChange('optimize_shopping_list', e.target.checked)}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">
                  Optimize for shopping efficiency
                </span>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isGenerating}
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isGenerating}
              className="flex-1 px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-lg font-medium hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Plan
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
