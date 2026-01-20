import React from 'react';
import { Button } from './Button';

/**
 * EmptyState component props interface
 */
export interface EmptyStateProps {
  /**
   * Icon to display (SVG or icon component)
   */
  icon?: React.ReactNode;

  /**
   * Title text
   */
  title: string;

  /**
   * Description text
   */
  description?: string;

  /**
   * Primary action button
   */
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };

  /**
   * Secondary action button
   */
  secondaryAction?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Size variant
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Custom content to render below description
   */
  children?: React.ReactNode;
}

const sizeClasses = {
  sm: {
    container: 'py-8',
    icon: 'h-12 w-12',
    title: 'text-base',
    description: 'text-sm',
  },
  md: {
    container: 'py-12',
    icon: 'h-16 w-16',
    title: 'text-lg',
    description: 'text-base',
  },
  lg: {
    container: 'py-16',
    icon: 'h-24 w-24',
    title: 'text-xl',
    description: 'text-lg',
  },
};

/**
 * EmptyState component for displaying empty or no-data states
 *
 * @example
 * ```tsx
 * <EmptyState
 *   icon={<MagnifyingGlassIcon />}
 *   title="No recipes found"
 *   description="Try adjusting your search or filters to find what you're looking for."
 *   action={{
 *     label: 'Clear filters',
 *     onClick: () => clearFilters(),
 *   }}
 * />
 *
 * <EmptyState
 *   icon={<PlusIcon />}
 *   title="No meal plans yet"
 *   description="Create your first meal plan to get started."
 *   action={{
 *     label: 'Create meal plan',
 *     onClick: () => navigate('/meal-plans/new'),
 *     icon: <PlusIcon />,
 *   }}
 *   secondaryAction={{
 *     label: 'Browse recipes',
 *     onClick: () => navigate('/recipes'),
 *   }}
 * />
 * ```
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className = '',
  size = 'md',
  children,
}) => {
  const classes = sizeClasses[size];

  return (
    <div
      className={`
        flex flex-col items-center justify-center text-center
        ${classes.container}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {/* Icon */}
      {icon && (
        <div
          className={`
            mb-4 flex items-center justify-center rounded-full
            bg-gray-100 text-gray-400
            ${classes.icon}
          `.trim().replace(/\s+/g, ' ')}
          aria-hidden="true"
        >
          {icon}
        </div>
      )}

      {/* Title */}
      <h3 className={`font-semibold text-gray-900 ${classes.title}`}>{title}</h3>

      {/* Description */}
      {description && (
        <p className={`mt-2 max-w-md text-gray-600 ${classes.description}`}>{description}</p>
      )}

      {/* Custom content */}
      {children && <div className="mt-4">{children}</div>}

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row">
          {action && (
            <Button
              variant="primary"
              onClick={action.onClick}
              iconLeft={action.icon}
              size={size === 'sm' ? 'sm' : 'md'}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant="outline"
              onClick={secondaryAction.onClick}
              iconLeft={secondaryAction.icon}
              size={size === 'sm' ? 'sm' : 'md'}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default EmptyState;
