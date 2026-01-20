/**
 * Configurable nutrition targets with localStorage persistence.
 */

import React, { useState, useEffect } from 'react';
import { Save, RotateCcw, Target } from 'lucide-react';
import { useNutritionGoalsStore } from '../../store/nutritionGoalsStore';
import clsx from 'clsx';

// ============================================================================
// TYPES
// ============================================================================

interface GoalInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  unit: string;
}

// ============================================================================
// COMPONENTS
// ============================================================================

const GoalInput: React.FC<GoalInputProps> = ({
  label,
  value,
  onChange,
  min = 0,
  max = 10000,
  step = 1,
  unit,
}) => {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          min={min}
          max={max}
          step={step}
          className="w-full px-3 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500">
          {unit}
        </span>
      </div>
    </div>
  );
};

export const NutritionGoals: React.FC = () => {
  const { goals, setGoals, resetToDefaults } = useNutritionGoalsStore();

  const [localGoals, setLocalGoals] = useState(goals);
  const [hasChanges, setHasChanges] = useState(false);
  const [showSavedMessage, setShowSavedMessage] = useState(false);

  useEffect(() => {
    setLocalGoals(goals);
  }, [goals]);

  useEffect(() => {
    const changed =
      localGoals.daily_calories !== goals.daily_calories ||
      localGoals.protein_g !== goals.protein_g ||
      localGoals.carbs_g !== goals.carbs_g ||
      localGoals.fat_g !== goals.fat_g ||
      localGoals.fiber_g !== goals.fiber_g;

    setHasChanges(changed);
  }, [localGoals, goals]);

  const handleSave = () => {
    setGoals(localGoals);
    setHasChanges(false);
    setShowSavedMessage(true);

    setTimeout(() => {
      setShowSavedMessage(false);
    }, 3000);
  };

  const handleReset = () => {
    resetToDefaults();
    setHasChanges(false);
  };

  const handleCancel = () => {
    setLocalGoals(goals);
    setHasChanges(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Target className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Nutrition Goals</h3>
      </div>

      <div className="space-y-4">
        <GoalInput
          label="Daily Calories"
          value={localGoals.daily_calories}
          onChange={(value) =>
            setLocalGoals({ ...localGoals, daily_calories: value })
          }
          min={1000}
          max={5000}
          step={50}
          unit="cal"
        />

        <GoalInput
          label="Protein Target"
          value={localGoals.protein_g}
          onChange={(value) =>
            setLocalGoals({ ...localGoals, protein_g: value })
          }
          min={0}
          max={500}
          step={5}
          unit="g"
        />

        <GoalInput
          label="Carbohydrate Limit"
          value={localGoals.carbs_g}
          onChange={(value) =>
            setLocalGoals({ ...localGoals, carbs_g: value })
          }
          min={0}
          max={1000}
          step={5}
          unit="g"
        />

        <GoalInput
          label="Fat Limit"
          value={localGoals.fat_g}
          onChange={(value) =>
            setLocalGoals({ ...localGoals, fat_g: value })
          }
          min={0}
          max={300}
          step={5}
          unit="g"
        />

        <GoalInput
          label="Fiber Minimum"
          value={localGoals.fiber_g}
          onChange={(value) =>
            setLocalGoals({ ...localGoals, fiber_g: value })
          }
          min={0}
          max={100}
          step={1}
          unit="g"
        />
      </div>

      {/* Macro Distribution Info */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-xs font-medium text-blue-900 mb-2">
          Macro Calorie Distribution
        </p>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div>
            <p className="text-blue-700">Protein:</p>
            <p className="font-semibold text-blue-900">
              {(localGoals.protein_g * 4).toFixed(0)} cal (
              {((localGoals.protein_g * 4) / localGoals.daily_calories * 100).toFixed(0)}%)
            </p>
          </div>
          <div>
            <p className="text-blue-700">Carbs:</p>
            <p className="font-semibold text-blue-900">
              {(localGoals.carbs_g * 4).toFixed(0)} cal (
              {((localGoals.carbs_g * 4) / localGoals.daily_calories * 100).toFixed(0)}%)
            </p>
          </div>
          <div>
            <p className="text-blue-700">Fat:</p>
            <p className="font-semibold text-blue-900">
              {(localGoals.fat_g * 9).toFixed(0)} cal (
              {((localGoals.fat_g * 9) / localGoals.daily_calories * 100).toFixed(0)}%)
            </p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-3">
        <button
          onClick={handleSave}
          disabled={!hasChanges}
          className={clsx(
            'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
            hasChanges
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          )}
        >
          <Save className="w-4 h-4" />
          Save Goals
        </button>

        <button
          onClick={handleReset}
          className="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
      </div>

      {hasChanges && (
        <button
          onClick={handleCancel}
          className="mt-2 w-full text-sm text-gray-600 hover:text-gray-900"
        >
          Cancel Changes
        </button>
      )}

      {/* Success Message */}
      {showSavedMessage && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800 font-medium text-center">
            Goals saved successfully!
          </p>
        </div>
      )}
    </div>
  );
};
