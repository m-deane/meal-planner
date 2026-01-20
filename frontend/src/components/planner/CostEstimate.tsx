/**
 * CostEstimate - Display cost breakdown for meal plans with budget comparison.
 */

import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
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

  const getBudgetColor = (utilization: number): string => {
    if (utilization <= 80) return 'bg-green-500';
    if (utilization <= 95) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getSavingsSuggestions = (): string[] => {
    const suggestions: string[] = [];

    if (costData.budget_comparison) {
      const { under_over_budget, budget_utilization_percent } = costData.budget_comparison;

      if (under_over_budget > 0) {
        suggestions.push(`You're over budget by $${under_over_budget.toFixed(2)}`);
        suggestions.push('Consider choosing more budget-friendly recipes');
      } else if (budget_utilization_percent < 80) {
        suggestions.push('You have room in your budget for variety');
      }
    }

    if (costData.average_per_meal > 15) {
      suggestions.push('Try batch cooking to reduce costs');
    }

    if (costData.days_covered > 0 && costData.average_daily_cost > 50) {
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
            ${costData.total_cost.toFixed(2)}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Total estimated cost
          </p>
        </div>

        {/* Cost Breakdown */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">Breakdown</h4>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Per Day</span>
              <span className="font-semibold text-gray-900">
                ${costData.average_daily_cost.toFixed(2)}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Per Meal</span>
              <span className="font-semibold text-gray-900">
                ${costData.average_per_meal.toFixed(2)}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Per Serving</span>
              <span className="font-semibold text-gray-900">
                ${costData.cost_per_serving.toFixed(2)}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm pt-2 border-t border-gray-200">
              <span className="text-gray-600">Days Covered</span>
              <span className="font-semibold text-gray-900">
                {costData.days_covered}
              </span>
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Servings</span>
              <span className="font-semibold text-gray-900">
                {costData.total_servings}
              </span>
            </div>
          </div>
        </div>

        {/* Budget Comparison */}
        {costData.budget_comparison && (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700">Budget Status</h4>

            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Budget</span>
                <span className="font-semibold text-gray-900">
                  ${costData.budget_comparison.budget_amount.toFixed(2)}
                </span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${getBudgetColor(
                    costData.budget_comparison.budget_utilization_percent
                  )}`}
                  style={{
                    width: `${Math.min(
                      100,
                      costData.budget_comparison.budget_utilization_percent
                    )}%`,
                  }}
                />
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                <span>
                  {costData.budget_comparison.budget_utilization_percent.toFixed(1)}% used
                </span>
                {costData.budget_comparison.under_over_budget !== 0 && (
                  <Badge
                    variant={costData.budget_comparison.under_over_budget < 0 ? 'success' : 'error'}
                    size="sm"
                  >
                    {costData.budget_comparison.under_over_budget > 0 ? '+' : ''}
                    ${Math.abs(costData.budget_comparison.under_over_budget).toFixed(2)}
                  </Badge>
                )}
              </div>
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
