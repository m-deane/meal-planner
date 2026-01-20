/**
 * MultiWeekView - Grid view for multi-week meal plans with expandable weeks.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import type { MultiWeekPlan, WeekPlanSummary } from '../../types';

interface MultiWeekViewProps {
  multiWeekPlan: MultiWeekPlan;
  onEditWeek?: (weekNumber: number) => void;
  onDeleteWeek?: (weekNumber: number) => void;
  className?: string;
}

export const MultiWeekView: React.FC<MultiWeekViewProps> = ({
  multiWeekPlan,
  onEditWeek,
  onDeleteWeek,
  className = '',
}) => {
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([1]));

  const toggleWeek = (weekNumber: number): void => {
    setExpandedWeeks(prev => {
      const next = new Set(prev);
      if (next.has(weekNumber)) {
        next.delete(weekNumber);
      } else {
        next.add(weekNumber);
      }
      return next;
    });
  };

  const expandAll = (): void => {
    setExpandedWeeks(new Set(multiWeekPlan.week_summaries.map(w => w.week_number)));
  };

  const collapseAll = (): void => {
    setExpandedWeeks(new Set());
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{multiWeekPlan.name}</h2>
          <p className="text-sm text-gray-600 mt-1">
            {multiWeekPlan.weeks_count} weeks ({multiWeekPlan.start_date} to {multiWeekPlan.end_date})
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={expandAll}>
            Expand All
          </Button>
          <Button variant="outline" size="sm" onClick={collapseAll}>
            Collapse All
          </Button>
        </div>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="p-4">
            <div className="text-2xl font-bold text-gray-900">
              ${multiWeekPlan.total_cost.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">Total Cost</div>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <div className="text-2xl font-bold text-gray-900">
              {multiWeekPlan.overall_variety_score.toFixed(0)}/100
            </div>
            <div className="text-sm text-gray-600">Variety Score</div>
          </div>
        </Card>

        <Card>
          <div className="p-4">
            <div className="text-2xl font-bold text-gray-900">
              {multiWeekPlan.weeks_count}
            </div>
            <div className="text-sm text-gray-600">Weeks Planned</div>
          </div>
        </Card>
      </div>

      {/* Week Cards */}
      <div className="space-y-4">
        {multiWeekPlan.week_summaries.map((weekSummary) => {
          const isExpanded = expandedWeeks.has(weekSummary.week_number);
          const weekPlan = multiWeekPlan.weeks[weekSummary.week_number - 1];

          return (
            <Card key={weekSummary.week_number} className="overflow-hidden">
              {/* Week Header - Always Visible */}
              <div
                className="p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleWeek(weekSummary.week_number)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        Week {weekSummary.week_number}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {weekSummary.start_date} - {weekSummary.end_date}
                      </p>
                    </div>

                    <div className="flex items-center gap-6 text-sm">
                      <div>
                        <span className="text-gray-600">Recipes:</span>{' '}
                        <span className="font-semibold text-gray-900">
                          {weekSummary.unique_recipes}/{weekSummary.total_recipes}
                        </span>
                      </div>

                      <div>
                        <span className="text-gray-600">Cost:</span>{' '}
                        <span className="font-semibold text-gray-900">
                          ${weekSummary.total_cost.toFixed(2)}
                        </span>
                      </div>

                      <div>
                        <span className="text-gray-600">Variety:</span>{' '}
                        <Badge
                          variant={
                            weekSummary.variety_score >= 75
                              ? 'success'
                              : weekSummary.variety_score >= 50
                              ? 'warning'
                              : 'error'
                          }
                          size="sm"
                        >
                          {weekSummary.variety_score.toFixed(0)}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <svg
                    className={`w-6 h-6 text-gray-400 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </div>

              {/* Week Details - Expandable */}
              {isExpanded && weekPlan && (
                <div className="p-6 border-t border-gray-200">
                  <div className="space-y-4">
                    {weekPlan.days.map((day) => (
                      <div key={day.date} className="pb-4 border-b border-gray-100 last:border-0">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold text-gray-900">
                            {new Date(day.date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </h4>
                          <span className="text-sm text-gray-500">
                            {day.total_calories} cal
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          {day.breakfast && (
                            <div className="bg-gray-50 rounded-lg p-3">
                              <div className="text-xs text-gray-500 mb-1">Breakfast</div>
                              <Link
                                to={`/recipes/${day.breakfast.recipe_id}`}
                                className="text-sm font-medium text-gray-900 hover:text-primary-600"
                              >
                                {day.breakfast.recipe_name}
                              </Link>
                            </div>
                          )}

                          {day.lunch && (
                            <div className="bg-gray-50 rounded-lg p-3">
                              <div className="text-xs text-gray-500 mb-1">Lunch</div>
                              <Link
                                to={`/recipes/${day.lunch.recipe_id}`}
                                className="text-sm font-medium text-gray-900 hover:text-primary-600"
                              >
                                {day.lunch.recipe_name}
                              </Link>
                            </div>
                          )}

                          {day.dinner && (
                            <div className="bg-gray-50 rounded-lg p-3">
                              <div className="text-xs text-gray-500 mb-1">Dinner</div>
                              <Link
                                to={`/recipes/${day.dinner.recipe_id}`}
                                className="text-sm font-medium text-gray-900 hover:text-primary-600"
                              >
                                {day.dinner.recipe_name}
                              </Link>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Week Actions */}
                  <div className="flex items-center gap-2 mt-6 pt-4 border-t border-gray-200">
                    {onEditWeek && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onEditWeek(weekSummary.week_number)}
                      >
                        Edit Week
                      </Button>
                    )}
                    {onDeleteWeek && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDeleteWeek(weekSummary.week_number)}
                        className="text-red-600 hover:text-red-700 hover:border-red-300"
                      >
                        Remove Week
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
};
