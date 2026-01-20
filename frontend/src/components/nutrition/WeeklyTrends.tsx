/**
 * Line chart showing nutrition trends over 7 days with target lines.
 */

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import clsx from 'clsx';

// ============================================================================
// TYPES
// ============================================================================

interface DayNutrition {
  day: string;
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
}

interface WeeklyTrendsProps {
  data: DayNutrition[];
  calorieGoal?: number;
  proteinGoal?: number;
  title?: string;
}

type MetricKey = 'calories' | 'protein_g' | 'carbohydrates_g' | 'fat_g';

// ============================================================================
// CONSTANTS
// ============================================================================

const METRICS: Array<{ key: MetricKey; label: string; color: string }> = [
  { key: 'calories', label: 'Calories', color: '#3b82f6' },
  { key: 'protein_g', label: 'Protein (g)', color: '#8b5cf6' },
  { key: 'carbohydrates_g', label: 'Carbs (g)', color: '#10b981' },
  { key: 'fat_g', label: 'Fat (g)', color: '#f59e0b' },
];

// ============================================================================
// COMPONENT
// ============================================================================

export const WeeklyTrends: React.FC<WeeklyTrendsProps> = ({
  data,
  calorieGoal,
  proteinGoal,
  title = 'Weekly Nutrition Trends',
}) => {
  const [selectedMetrics, setSelectedMetrics] = useState<Set<MetricKey>>(
    new Set(['calories'])
  );

  const toggleMetric = (metric: MetricKey) => {
    setSelectedMetrics((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(metric)) {
        newSet.delete(metric);
      } else {
        newSet.add(metric);
      }
      return newSet;
    });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-700">
              {entry.name}: <span className="font-medium">{entry.value.toFixed(1)}</span>
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-80 text-gray-500">
          No nutrition data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>

        <div className="flex gap-2 flex-wrap">
          {METRICS.map((metric) => (
            <button
              key={metric.key}
              onClick={() => toggleMetric(metric.key)}
              className={clsx(
                'px-3 py-1 rounded-full text-xs font-medium transition-colors',
                selectedMetrics.has(metric.key)
                  ? 'text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
              style={
                selectedMetrics.has(metric.key)
                  ? { backgroundColor: metric.color }
                  : undefined
              }
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="day"
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <YAxis stroke="#6b7280" tick={{ fill: '#6b7280', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            formatter={(value) => <span className="text-gray-700">{value}</span>}
          />

          {calorieGoal && selectedMetrics.has('calories') && (
            <ReferenceLine
              y={calorieGoal}
              stroke="#3b82f6"
              strokeDasharray="5 5"
              label={{
                value: 'Calorie Goal',
                fill: '#3b82f6',
                fontSize: 12,
                position: 'right',
              }}
            />
          )}

          {proteinGoal && selectedMetrics.has('protein_g') && (
            <ReferenceLine
              y={proteinGoal}
              stroke="#8b5cf6"
              strokeDasharray="5 5"
              label={{
                value: 'Protein Goal',
                fill: '#8b5cf6',
                fontSize: 12,
                position: 'right',
              }}
            />
          )}

          {METRICS.filter((m) => selectedMetrics.has(m.key)).map((metric) => (
            <Line
              key={metric.key}
              type="monotone"
              dataKey={metric.key}
              stroke={metric.color}
              strokeWidth={2}
              dot={{ fill: metric.color, r: 4 }}
              activeDot={{ r: 6 }}
              name={metric.label}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
