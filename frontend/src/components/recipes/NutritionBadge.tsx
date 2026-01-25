import React from 'react';
import { FireIcon, BeakerIcon, CakeIcon } from '@heroicons/react/24/outline';
import { Badge, BadgeColor } from '../common';

/**
 * Nutrition type for the badge
 */
export type NutritionType = 'calories' | 'protein' | 'carbs' | 'fat' | 'fiber' | 'sugar';

/**
 * NutritionBadge component props
 */
export interface NutritionBadgeProps {
  /**
   * Type of nutrition value
   */
  type: NutritionType;

  /**
   * Numeric value to display
   */
  value: number;

  /**
   * Unit to display (e.g., 'g', 'kcal', 'mg')
   * If not provided, defaults based on type
   */
  unit?: string;

  /**
   * Whether to show the icon
   * @default true
   */
  showIcon?: boolean;

  /**
   * Override color (if not provided, color is determined by value and type)
   */
  color?: BadgeColor;

  /**
   * Size of the badge
   * @default 'sm'
   */
  size?: 'sm' | 'md';

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Default units for each nutrition type
 */
const defaultUnits: Record<NutritionType, string> = {
  calories: 'kcal',
  protein: 'g',
  carbs: 'g',
  fat: 'g',
  fiber: 'g',
  sugar: 'g',
};

/**
 * Icons for each nutrition type
 */
const nutritionIcons: Record<NutritionType, React.ReactNode> = {
  calories: <FireIcon />,
  protein: <BeakerIcon />,
  carbs: <CakeIcon />,
  fat: <CakeIcon />,
  fiber: <BeakerIcon />,
  sugar: <CakeIcon />,
};

/**
 * Determine badge color based on nutrition type and value
 */
const getColorForNutrition = (type: NutritionType, value: number): BadgeColor => {
  switch (type) {
    case 'calories':
      if (value < 400) return 'success';
      if (value < 600) return 'warning';
      return 'error';

    case 'protein':
      if (value >= 30) return 'success';
      if (value >= 20) return 'info';
      return 'default';

    case 'carbs':
      if (value < 30) return 'success';
      if (value < 50) return 'default';
      return 'warning';

    case 'fat':
      if (value < 15) return 'success';
      if (value < 25) return 'default';
      return 'warning';

    case 'fiber':
      if (value >= 8) return 'success';
      if (value >= 5) return 'info';
      return 'default';

    case 'sugar':
      if (value < 10) return 'success';
      if (value < 20) return 'default';
      return 'warning';

    default:
      return 'default';
  }
};

/**
 * NutritionBadge component
 *
 * Small inline badge showing a nutrition value with color coding based on the value.
 *
 * @example
 * ```tsx
 * <NutritionBadge type="calories" value={450} />
 * <NutritionBadge type="protein" value={32} showIcon />
 * <NutritionBadge type="carbs" value={45} unit="g" color="success" />
 * ```
 */
export const NutritionBadge: React.FC<NutritionBadgeProps> = ({
  type,
  value,
  unit,
  showIcon = true,
  color,
  size = 'sm',
  className = '',
}) => {
  const displayUnit = unit ?? defaultUnits[type];
  // Handle null, undefined, or non-numeric values for color calculation
  const safeValue = typeof value === 'number' ? value : Number(value) || 0;
  const badgeColor = color ?? getColorForNutrition(type, safeValue);
  const icon = showIcon ? nutritionIcons[type] : undefined;

  // Handle null, undefined, or non-numeric values
  const numericValue = typeof value === 'number' ? value : Number(value) || 0;
  const formattedValue = Number.isInteger(numericValue) ? numericValue : numericValue.toFixed(1);

  return (
    <Badge
      color={badgeColor}
      size={size}
      icon={icon}
      className={className}
      pill
    >
      {formattedValue}
      {displayUnit}
    </Badge>
  );
};

export default NutritionBadge;
