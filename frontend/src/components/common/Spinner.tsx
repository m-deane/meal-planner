import React from 'react';

/**
 * Spinner size types
 */
export type SpinnerSize = 'sm' | 'md' | 'lg';

/**
 * Spinner color variants
 */
export type SpinnerColor = 'primary' | 'secondary' | 'white' | 'gray' | 'success' | 'danger';

/**
 * Spinner component props interface
 */
export interface SpinnerProps {
  /**
   * Size of the spinner
   * @default 'md'
   */
  size?: SpinnerSize;

  /**
   * Color variant of the spinner
   * @default 'primary'
   */
  color?: SpinnerColor;

  /**
   * Accessible label for screen readers
   * @default 'Loading...'
   */
  label?: string;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Whether to center the spinner in its container
   * @default false
   */
  centered?: boolean;
}

const sizeClasses: Record<SpinnerSize, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-3',
  lg: 'h-12 w-12 border-4',
};

const colorClasses: Record<SpinnerColor, string> = {
  primary: 'border-blue-600 border-t-transparent',
  secondary: 'border-gray-600 border-t-transparent',
  white: 'border-white border-t-transparent',
  gray: 'border-gray-400 border-t-transparent',
  success: 'border-green-600 border-t-transparent',
  danger: 'border-red-600 border-t-transparent',
};

/**
 * Spinner component for loading states
 *
 * @example
 * ```tsx
 * <Spinner size="md" color="primary" />
 *
 * <Spinner size="lg" color="white" centered label="Loading data..." />
 * ```
 */
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  label = 'Loading...',
  className = '',
  centered = false,
}) => {
  const spinnerClasses = `
    ${sizeClasses[size]}
    ${colorClasses[color]}
    rounded-full
    animate-spin
    ${className}
  `.trim().replace(/\s+/g, ' ');

  const spinner = (
    <div
      className={spinnerClasses}
      role="status"
      aria-label={label}
      aria-live="polite"
    >
      <span className="sr-only">{label}</span>
    </div>
  );

  if (centered) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        {spinner}
      </div>
    );
  }

  return spinner;
};

/**
 * SpinnerOverlay component for full-page loading states
 */
export interface SpinnerOverlayProps {
  /**
   * Whether the overlay is visible
   */
  visible: boolean;

  /**
   * Size of the spinner
   * @default 'lg'
   */
  size?: SpinnerSize;

  /**
   * Message to display below the spinner
   */
  message?: string;

  /**
   * Accessible label for screen readers
   * @default 'Loading...'
   */
  label?: string;
}

/**
 * SpinnerOverlay component for full-page loading with backdrop
 *
 * @example
 * ```tsx
 * <SpinnerOverlay
 *   visible={isLoading}
 *   message="Fetching recipes..."
 * />
 * ```
 */
export const SpinnerOverlay: React.FC<SpinnerOverlayProps> = ({
  visible,
  size = 'lg',
  message,
  label = 'Loading...',
}) => {
  if (!visible) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      role="alert"
      aria-busy="true"
      aria-live="assertive"
    >
      <div className="rounded-lg bg-white p-8 shadow-xl">
        <div className="flex flex-col items-center gap-4">
          <Spinner size={size} color="primary" label={label} />
          {message && (
            <p className="text-sm font-medium text-gray-700">{message}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Spinner;
