/**
 * Single stat card for nutrition metrics with trend indicators.
 */

import React from 'react';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import clsx from 'clsx';

// ============================================================================
// TYPES
// ============================================================================

interface NutritionCardProps {
  label: string;
  value: number;
  unit: string;
  goal?: number;
  subtitle?: string;
  showTrend?: boolean;
  colorClass?: string;
  decimals?: number;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const NutritionCard: React.FC<NutritionCardProps> = ({
  label,
  value,
  unit,
  goal,
  subtitle,
  showTrend = true,
  colorClass = 'text-blue-600',
  decimals = 0,
}) => {
  const formattedValue = value.toFixed(decimals);

  // Calculate trend vs goal
  const getTrendInfo = () => {
    if (!goal || !showTrend) return null;

    const difference = value - goal;
    const percentDiff = (difference / goal) * 100;

    if (Math.abs(percentDiff) < 5) {
      return {
        icon: Minus,
        text: 'On target',
        color: 'text-green-600',
      };
    }

    if (difference > 0) {
      return {
        icon: ArrowUp,
        text: `${Math.abs(percentDiff).toFixed(0)}% above`,
        color: 'text-orange-600',
      };
    }

    return {
      icon: ArrowDown,
      text: `${Math.abs(percentDiff).toFixed(0)}% below`,
      color: 'text-blue-600',
    };
  };

  const trendInfo = getTrendInfo();

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex flex-col h-full">
        <h3 className="text-sm font-medium text-gray-600 mb-2">{label}</h3>

        <div className="flex items-baseline gap-2 mb-1">
          <span className={clsx('text-3xl font-bold', colorClass)}>
            {formattedValue}
          </span>
          <span className="text-lg text-gray-500">{unit}</span>
        </div>

        {goal !== undefined && (
          <div className="text-xs text-gray-500 mb-2">
            Goal: {goal.toFixed(decimals)} {unit}
          </div>
        )}

        {subtitle && (
          <div className="text-sm text-gray-600 mb-2">{subtitle}</div>
        )}

        {trendInfo && (
          <div className={clsx('flex items-center gap-1 text-sm mt-auto', trendInfo.color)}>
            <trendInfo.icon className="w-4 h-4" />
            <span>{trendInfo.text}</span>
          </div>
        )}
      </div>
    </div>
  );
};
