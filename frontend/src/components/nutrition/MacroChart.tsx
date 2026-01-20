/**
 * Pie chart showing macronutrient distribution with interactive tooltips.
 */

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface MacroData {
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
}

interface MacroChartProps {
  data: MacroData;
  title?: string;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const COLORS = {
  protein: '#3b82f6',    // blue-500
  carbs: '#10b981',      // green-500
  fat: '#f59e0b',        // amber-500
};

const MACRO_CALORIES = {
  protein: 4,
  carbs: 4,
  fat: 9,
};

// ============================================================================
// COMPONENT
// ============================================================================

export const MacroChart: React.FC<MacroChartProps> = ({
  data,
  title = 'Macronutrient Distribution'
}) => {
  // Calculate calories from each macro
  const proteinCal = data.protein_g * MACRO_CALORIES.protein;
  const carbsCal = data.carbohydrates_g * MACRO_CALORIES.carbs;
  const fatCal = data.fat_g * MACRO_CALORIES.fat;
  const totalCal = proteinCal + carbsCal + fatCal;

  // Calculate percentages
  const chartData = [
    {
      name: 'Protein',
      value: data.protein_g,
      calories: proteinCal,
      percentage: totalCal > 0 ? ((proteinCal / totalCal) * 100).toFixed(1) : 0,
      color: COLORS.protein,
    },
    {
      name: 'Carbs',
      value: data.carbohydrates_g,
      calories: carbsCal,
      percentage: totalCal > 0 ? ((carbsCal / totalCal) * 100).toFixed(1) : 0,
      color: COLORS.carbs,
    },
    {
      name: 'Fat',
      value: data.fat_g,
      calories: fatCal,
      percentage: totalCal > 0 ? ((fatCal / totalCal) * 100).toFixed(1) : 0,
      color: COLORS.fat,
    },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    return (
      <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900 mb-1">{data.name}</p>
        <p className="text-sm text-gray-600">{data.value.toFixed(1)}g</p>
        <p className="text-sm text-gray-600">{data.calories.toFixed(0)} cal</p>
        <p className="text-sm font-medium" style={{ color: data.color }}>
          {data.percentage}% of total
        </p>
      </div>
    );
  };

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (parseFloat(percentage) < 5) return null;

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-sm font-semibold"
      >
        {`${percentage}%`}
      </text>
    );
  };

  if (totalCal === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          No nutrition data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="calories"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => (
              <span className="text-sm text-gray-700">
                {value}: {entry.payload.value.toFixed(0)}g
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
