/**
 * VarietyIndicator - Display variety score and breakdown for meal plans.
 */

import React, { useState } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Spinner } from '../common/Spinner';
import type { VarietyBreakdown } from '../../types';

interface VarietyIndicatorProps {
  varietyData: VarietyBreakdown | undefined;
  isLoading?: boolean;
  isError?: boolean;
  className?: string;
}

export const VarietyIndicator: React.FC<VarietyIndicatorProps> = ({
  varietyData,
  isLoading = false,
  isError = false,
  className = '',
}) => {
  const [showDetails, setShowDetails] = useState(false);

  if (isLoading) {
    return (
      <Card className={className}>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Variety Score</h3>
          <div className="flex items-center justify-center py-8">
            <Spinner size="md" />
          </div>
        </div>
      </Card>
    );
  }

  if (isError || !varietyData) {
    return (
      <Card className={className}>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Variety Score</h3>
          <p className="text-sm text-gray-500">Unable to calculate variety score</p>
        </div>
      </Card>
    );
  }

  const { metrics, suggestions, score_interpretation, score_color } = varietyData;

  const getScoreColorClass = (): string => {
    switch (score_color) {
      case 'green':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'yellow':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'orange':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'red':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getScoreInterpretationText = (): string => {
    switch (score_interpretation) {
      case 'excellent':
        return 'Excellent variety!';
      case 'good':
        return 'Good variety';
      case 'fair':
        return 'Fair variety';
      case 'poor':
        return 'Limited variety';
      default:
        return 'Unknown';
    }
  };

  const getPriorityIcon = (priority: string): JSX.Element => {
    switch (priority) {
      case 'high':
        return (
          <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'medium':
        return (
          <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  return (
    <Card className={className}>
      <div className="p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Variety Score</h3>

          <div className={`inline-flex items-center justify-center px-6 py-3 rounded-lg border-2 ${getScoreColorClass()}`}>
            <div className="text-4xl font-bold">
              {metrics.overall_variety_score.toFixed(0)}
            </div>
            <div className="ml-2 text-xl">/100</div>
          </div>

          <p className="text-sm font-medium text-gray-700 mt-2">
            {getScoreInterpretationText()}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-900">
              {metrics.unique_recipes_count}
            </div>
            <div className="text-xs text-gray-600">
              Unique Recipes
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-900">
              {(metrics.recipe_repetition_rate * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-600">
              Repetition
            </div>
          </div>
        </div>

        {/* Toggle Details */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
        >
          <span>{showDetails ? 'Hide' : 'Show'} Breakdown</span>
          <svg
            className={`w-5 h-5 transition-transform ${showDetails ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Detailed Breakdown */}
        {showDetails && (
          <div className="space-y-4 pt-4 border-t border-gray-200">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Protein Diversity</h4>
              <div className="flex items-center gap-2 mb-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${metrics.protein_diversity_score}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600 w-12 text-right">
                  {metrics.protein_diversity_score.toFixed(0)}%
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {metrics.unique_proteins.slice(0, 5).map((protein, index) => (
                  <Badge key={index} variant="secondary" size="sm">
                    {protein}
                  </Badge>
                ))}
                {metrics.unique_proteins.length > 5 && (
                  <Badge variant="secondary" size="sm">
                    +{metrics.unique_proteins.length - 5}
                  </Badge>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Cuisine Diversity</h4>
              <div className="flex items-center gap-2 mb-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${metrics.cuisine_diversity_score}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600 w-12 text-right">
                  {metrics.cuisine_diversity_score.toFixed(0)}%
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {metrics.unique_cuisines.slice(0, 5).map((cuisine, index) => (
                  <Badge key={index} variant="secondary" size="sm">
                    {cuisine}
                  </Badge>
                ))}
                {metrics.unique_cuisines.length > 5 && (
                  <Badge variant="secondary" size="sm">
                    +{metrics.unique_cuisines.length - 5}
                  </Badge>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Cooking Methods</h4>
              <div className="flex items-center gap-2 mb-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${metrics.cooking_method_diversity}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600 w-12 text-right">
                  {metrics.cooking_method_diversity.toFixed(0)}%
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {metrics.unique_cooking_methods.slice(0, 5).map((method, index) => (
                  <Badge key={index} variant="secondary" size="sm">
                    {method}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-gray-700">Improvement Suggestions</h4>
            <ul className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start gap-2 text-xs">
                  {getPriorityIcon(suggestion.priority)}
                  <span className="text-gray-600">{suggestion.message}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
};
