import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/solid';

/**
 * Badge color variants
 */
export type BadgeColor = 'default' | 'success' | 'warning' | 'error' | 'info' | 'primary';

/**
 * Badge size types
 */
export type BadgeSize = 'sm' | 'md';

/**
 * Badge component props interface
 */
export interface BadgeProps {
  /**
   * Badge content/text
   */
  children: React.ReactNode;

  /**
   * Color variant of the badge
   * @default 'default'
   */
  color?: BadgeColor;

  /**
   * Size of the badge
   * @default 'md'
   */
  size?: BadgeSize;

  /**
   * Whether the badge is removable (shows X button)
   * @default false
   */
  removable?: boolean;

  /**
   * Callback when remove button is clicked
   */
  onRemove?: () => void;

  /**
   * Whether to use pill shape (rounded-full)
   * @default false
   */
  pill?: boolean;

  /**
   * Whether to use outline variant
   * @default false
   */
  outline?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Icon to display on the left
   */
  icon?: React.ReactNode;
}

const colorClasses: Record<BadgeColor, { solid: string; outline: string }> = {
  default: {
    solid: 'bg-gray-100 text-gray-800 border-gray-200',
    outline: 'bg-transparent text-gray-700 border-gray-400',
  },
  primary: {
    solid: 'bg-blue-100 text-blue-800 border-blue-200',
    outline: 'bg-transparent text-blue-700 border-blue-400',
  },
  success: {
    solid: 'bg-green-100 text-green-800 border-green-200',
    outline: 'bg-transparent text-green-700 border-green-400',
  },
  warning: {
    solid: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    outline: 'bg-transparent text-yellow-700 border-yellow-400',
  },
  error: {
    solid: 'bg-red-100 text-red-800 border-red-200',
    outline: 'bg-transparent text-red-700 border-red-400',
  },
  info: {
    solid: 'bg-cyan-100 text-cyan-800 border-cyan-200',
    outline: 'bg-transparent text-cyan-700 border-cyan-400',
  },
};

const sizeClasses: Record<BadgeSize, { badge: string; icon: string; removeButton: string }> = {
  sm: {
    badge: 'px-2 py-0.5 text-xs',
    icon: 'h-3 w-3',
    removeButton: 'ml-1 h-3 w-3',
  },
  md: {
    badge: 'px-2.5 py-1 text-sm',
    icon: 'h-4 w-4',
    removeButton: 'ml-1.5 h-4 w-4',
  },
};

/**
 * Badge component for labels, tags, and status indicators
 *
 * @example
 * ```tsx
 * <Badge color="success">Active</Badge>
 *
 * <Badge color="warning" removable onRemove={() => console.log('Removed')}>
 *   Filter: Vegetarian
 * </Badge>
 *
 * <Badge color="primary" pill icon={<Icon />}>
 *   High Protein
 * </Badge>
 * ```
 */
export const Badge: React.FC<BadgeProps> = ({
  children,
  color = 'default',
  size = 'md',
  removable = false,
  onRemove,
  pill = false,
  outline = false,
  className = '',
  icon,
}) => {
  const colorClass = outline ? colorClasses[color].outline : colorClasses[color].solid;
  const { badge: sizeClass, icon: iconClass, removeButton: removeButtonClass } = sizeClasses[size];

  const shapeClass = pill ? 'rounded-full' : 'rounded-md';
  const borderClass = outline ? 'border-2' : 'border';

  const handleRemove = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    onRemove?.();
  };

  return (
    <span
      className={`
        inline-flex items-center font-medium
        ${sizeClass}
        ${colorClass}
        ${shapeClass}
        ${borderClass}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {icon && <span className={`inline-flex ${iconClass} mr-1`}>{icon}</span>}
      <span>{children}</span>
      {removable && (
        <button
          type="button"
          onClick={handleRemove}
          className={`
            inline-flex items-center justify-center rounded-full
            hover:bg-black hover:bg-opacity-10
            focus:outline-none focus:ring-2 focus:ring-offset-1
            ${removeButtonClass}
          `.trim().replace(/\s+/g, ' ')}
          aria-label="Remove"
        >
          <XMarkIcon className="h-full w-full" aria-hidden="true" />
        </button>
      )}
    </span>
  );
};

/**
 * BadgeGroup component for displaying multiple badges
 */
export interface BadgeGroupProps {
  /**
   * Array of badge items
   */
  children: React.ReactNode;

  /**
   * Gap between badges
   * @default 'md'
   */
  gap?: 'sm' | 'md' | 'lg';

  /**
   * Whether badges should wrap
   * @default true
   */
  wrap?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

const gapClasses = {
  sm: 'gap-1',
  md: 'gap-2',
  lg: 'gap-3',
};

/**
 * BadgeGroup component for displaying multiple badges in a group
 *
 * @example
 * ```tsx
 * <BadgeGroup>
 *   <Badge color="success">Vegetarian</Badge>
 *   <Badge color="info">High Protein</Badge>
 *   <Badge color="warning">Gluten-Free</Badge>
 * </BadgeGroup>
 * ```
 */
export const BadgeGroup: React.FC<BadgeGroupProps> = ({
  children,
  gap = 'md',
  wrap = true,
  className = '',
}) => {
  return (
    <div
      className={`
        flex items-center
        ${gapClasses[gap]}
        ${wrap ? 'flex-wrap' : 'flex-nowrap'}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </div>
  );
};

export default Badge;
