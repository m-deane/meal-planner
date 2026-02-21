/**
 * CostEstimate - Display cost breakdown for meal plans with budget comparison.
 */

import React from 'react';
import { Card } from '../common/Card';
import { Spinner } from '../common/Spinner';
import type { MealPlanCostBreakdown } from '../../types';

interface CostEstimateProps {
  costData: MealPlanCostBreakdown | undefined;
  isLoading?: boolean;
  isError?: boolean;
  className?: string;
}

export const CostEstimate: React.FC<CostEstimateProps> = ({
  costData,
  isLoading = false,
  isError = false,
  className = '',
}) => {
  if (isLoading) {
    return (
      <Card className={className}>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Estimate</h3>
          <div className="flex items-center justify-center py-8">
            <Spinner size="md" />
          </div>
        </div>
      </Card>
    );
  }

  if (isError || !costData) {
    return (
      <Card className={className}>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Estimate</h3>
          <p className="text-sm text-gray-500">Unable to load cost estimate</p>
        </div>
      </Card>
    );
  }

  const getSavingsSuggestions = (): string[] => {
    const suggestions: string[] = [...costData.savings_suggestions];

    if (costData.per_meal_average > 15) {
      suggestions.push('Try batch cooking to reduce costs');
    }

    if (costData.per_day_average !== null && costData.per_day_average > 50) {
      suggestions.push('Look for seasonal ingredients for savings');
    }

    return suggestions;
  };

  const savingsSuggestions = getSavingsSuggestions();

  return (
    <Card className={className}>
      <div className="p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Cost Estimate</h3>
          <div className="text-3xl font-bold text-primary-600">
            ${costData.total.toFixed(2)}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Total estimated cost
          </p>
        </div>

        {/* Cost Breakdown */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">Breakdown</h4>

          <div className="space-y-2">
            {costData.per_day_average !== null && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Per Day</span>
                <span className="font-semibold text-gray-900">
                  ${costData.per_day_average.toFixed(2)}
                </span>
              </div>
            )}

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Per Meal</span>
              <span className="font-semibold text-gray-900">
                ${costData.per_meal_average.toFixed(2)}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm pt-2 border-t border-gray-200">
              <span className="text-gray-600">Total Meals</span>
              <span className="font-semibold text-gray-900">
                {costData.total_meals}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Unique Ingredients</span>
              <span className="font-semibold text-gray-900">
                {costData.ingredient_count}
              </span>
            </div>
          </div>
        </div>

        {/* Category breakdown */}
        {Object.keys(costData.by_category).length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700">By Category</h4>
            <div className="space-y-2">
              {Object.entries(costData.by_category).map(([category, cost]) => (
                <div key={category} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 capitalize">{category}</span>
                  <span className="font-semibold text-gray-900">
                    ${cost.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Savings Suggestions */}
        {savingsSuggestions.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-gray-700">Tips</h4>
            <ul className="space-y-1">
              {savingsSuggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start gap-2 text-xs text-gray-600">
                  <svg className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
};
