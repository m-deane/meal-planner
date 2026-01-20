/**
 * Stacked bar chart showing daily meal breakdown by calories.
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface DayBreakdown {
  day: string;
  breakfast: number;
  lunch: number;
  dinner: number;
  total: number;
}

interface DailyBreakdownProps {
  data: DayBreakdown[];
  title?: string;
  onDayClick?: (day: string) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MEAL_COLORS = {
  breakfast: '#f59e0b', // amber-500
  lunch: '#10b981',     // green-500
  dinner: '#3b82f6',    // blue-500
};

// ============================================================================
// COMPONENT
// ============================================================================

export const DailyBreakdown: React.FC<DailyBreakdownProps> = ({
  data,
  title = 'Daily Calorie Breakdown',
  onDayClick,
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const total = payload.reduce((sum: number, entry: any) => sum + entry.value, 0);

    return (
      <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-700 capitalize">{entry.name}:</span>
            </div>
            <span className="font-medium text-gray-900">
              {entry.value.toFixed(0)} cal
            </span>
          </div>
        ))}
        <div className="mt-2 pt-2 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm font-semibold">
            <span className="text-gray-700">Total:</span>
            <span className="text-gray-900">{total.toFixed(0)} cal</span>
          </div>
        </div>
      </div>
    );
  };

  const handleBarClick = (data: any) => {
    if (onDayClick && data) {
      onDayClick(data.day);
    }
  };

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-80 text-gray-500">
          No meal data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      <ResponsiveContainer width="100%" height={320}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="day"
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <YAxis
            stroke="#6b7280"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            label={{
              value: 'Calories',
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#6b7280', fontSize: 12 },
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            formatter={(value) => (
              <span className="text-gray-700 capitalize">{value}</span>
            )}
          />

          <Bar
            dataKey="breakfast"
            stackId="meals"
            fill={MEAL_COLORS.breakfast}
            radius={[0, 0, 0, 0]}
            onClick={handleBarClick}
            cursor={onDayClick ? 'pointer' : 'default'}
          />
          <Bar
            dataKey="lunch"
            stackId="meals"
            fill={MEAL_COLORS.lunch}
            radius={[0, 0, 0, 0]}
            onClick={handleBarClick}
            cursor={onDayClick ? 'pointer' : 'default'}
          />
          <Bar
            dataKey="dinner"
            stackId="meals"
            fill={MEAL_COLORS.dinner}
            radius={[4, 4, 0, 0]}
            onClick={handleBarClick}
            cursor={onDayClick ? 'pointer' : 'default'}
          />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 flex items-center justify-center gap-6 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: MEAL_COLORS.breakfast }}
          />
          <span>Breakfast</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: MEAL_COLORS.lunch }}
          />
          <span>Lunch</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: MEAL_COLORS.dinner }}
          />
          <span>Dinner</span>
        </div>
      </div>
    </div>
  );
};
