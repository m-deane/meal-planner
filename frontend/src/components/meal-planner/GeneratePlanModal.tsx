/**
 * Modal for meal plan generation with configuration options.
 */

import React, { useState } from 'react';
import type { MealPlanGenerateRequest } from '../../types';
import { X, Loader2, Sparkles } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface GeneratePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: MealPlanGenerateRequest) => void;
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
    target_calories: '',
    target_protein_g: '',
    max_cooking_time: '',
    avoid_duplicate_recipes: true,
    optimize_shopping_list: true,
  });

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const request: MealPlanGenerateRequest = {
      days: formData.days,
      meal_preferences: {
        include_breakfast: formData.include_breakfast,
        include_lunch: formData.include_lunch,
        include_dinner: formData.include_dinner,
        include_snacks: false,
      },
      avoid_duplicate_recipes: formData.avoid_duplicate_recipes,
      max_recipe_reuse: formData.avoid_duplicate_recipes ? 1 : 3,
      variety_score_weight: 0.3,
      optimize_shopping_list: formData.optimize_shopping_list,
    };

    // Add nutrition constraints if provided
    if (formData.target_calories || formData.target_protein_g) {
      request.nutrition_constraints = {};
      if (formData.target_calories) {
        request.nutrition_constraints.target_calories = Number(formData.target_calories);
      }
      if (formData.target_protein_g) {
        request.nutrition_constraints.target_protein_g = Number(formData.target_protein_g);
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
