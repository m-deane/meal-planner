/**
 * MultiWeekGenerateModal - Modal for generating multi-week meal plans.
 */

import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useGenerateMultiWeekPlan } from '../../hooks/useMultiWeek';
import type { MultiWeekGenerateRequest } from '../../types';

interface MultiWeekGenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (planId: number) => void;
}

export const MultiWeekGenerateModal: React.FC<MultiWeekGenerateModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [weeksCount, setWeeksCount] = useState(4);
  const [startDate, setStartDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [planName, setPlanName] = useState('');
  const [budgetPerWeek, setBudgetPerWeek] = useState<number | ''>('');
  const [varietyPreferences, setVarietyPreferences] = useState({
    minimize_repetition: true,
    protein_variety_weight: 0.8,
    cuisine_variety_weight: 0.6,
    max_recipe_repeat_frequency: 2,
  });

  const generateMutation = useGenerateMultiWeekPlan();

  const handleGenerate = async (): Promise<void> => {
    const request: MultiWeekGenerateRequest = {
      weeks_count: weeksCount,
      start_date: startDate,
      name: planName.trim() || undefined,
      budget_per_week: budgetPerWeek ? Number(budgetPerWeek) : undefined,
      variety_preferences: varietyPreferences,
    };

    try {
      const result = await generateMutation.mutateAsync(request);
      if (onSuccess) {
        onSuccess(result.id);
      }
      onClose();
    } catch (error) {
      console.error('Failed to generate multi-week plan:', error);
    }
  };

  const resetForm = (): void => {
    setWeeksCount(4);
    setStartDate(new Date().toISOString().split('T')[0]);
    setPlanName('');
    setBudgetPerWeek('');
    setVarietyPreferences({
      minimize_repetition: true,
      protein_variety_weight: 0.8,
      cuisine_variety_weight: 0.6,
      max_recipe_repeat_frequency: 2,
    });
  };

  const handleClose = (): void => {
    resetForm();
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Generate Multi-Week Meal Plan"
      size="xl"
    >
      <div className="space-y-6">
        {/* Basic Settings */}
        <div className="space-y-4">
          <div>
            <label htmlFor="plan-name" className="block text-sm font-medium text-gray-700 mb-1">
              Plan Name (Optional)
            </label>
            <input
              id="plan-name"
              type="text"
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., January Meal Plan"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="weeks-count" className="block text-sm font-medium text-gray-700 mb-1">
                Number of Weeks
              </label>
              <select
                id="weeks-count"
                value={weeksCount}
                onChange={(e) => setWeeksCount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((num) => (
                  <option key={num} value={num}>
                    {num} {num === 1 ? 'week' : 'weeks'}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>

          <div>
            <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-1">
              Budget per Week (Optional)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                id="budget"
                type="number"
                value={budgetPerWeek}
                onChange={(e) => setBudgetPerWeek(e.target.value ? Number(e.target.value) : '')}
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="0.00"
                min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>

        {/* Variety Preferences */}
        <div className="space-y-4 pt-4 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900">Variety Preferences</h3>

          <div className="flex items-center">
            <input
              id="minimize-repetition"
              type="checkbox"
              checked={varietyPreferences.minimize_repetition}
              onChange={(e) =>
                setVarietyPreferences({ ...varietyPreferences, minimize_repetition: e.target.checked })
              }
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="minimize-repetition" className="ml-2 text-sm text-gray-700">
              Minimize recipe repetition
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Protein Variety Weight: {varietyPreferences.protein_variety_weight.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={varietyPreferences.protein_variety_weight}
              onChange={(e) =>
                setVarietyPreferences({
                  ...varietyPreferences,
                  protein_variety_weight: Number(e.target.value),
                })
              }
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cuisine Variety Weight: {varietyPreferences.cuisine_variety_weight.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={varietyPreferences.cuisine_variety_weight}
              onChange={(e) =>
                setVarietyPreferences({
                  ...varietyPreferences,
                  cuisine_variety_weight: Number(e.target.value),
                })
              }
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>

          <div>
            <label htmlFor="max-repeat" className="block text-sm font-medium text-gray-700 mb-1">
              Maximum Times to Repeat Recipe
            </label>
            <select
              id="max-repeat"
              value={varietyPreferences.max_recipe_repeat_frequency}
              onChange={(e) =>
                setVarietyPreferences({
                  ...varietyPreferences,
                  max_recipe_repeat_frequency: Number(e.target.value),
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={1}>1 time</option>
              <option value={2}>2 times</option>
              <option value={3}>3 times</option>
              <option value={4}>4 times</option>
              <option value={5}>5 times</option>
            </select>
          </div>
        </div>

        {/* Error Display */}
        {generateMutation.isError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              Failed to generate meal plan. Please try again.
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={generateMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleGenerate}
            disabled={generateMutation.isPending || !startDate}
            isLoading={generateMutation.isPending}
          >
            Generate Plan
          </Button>
        </div>
      </div>
    </Modal>
  );
};
