import React from 'react';
import { Spinner } from './Spinner';

/**
 * LoadingScreen component props interface
 */
export interface LoadingScreenProps {
  /**
   * Optional message to display
   */
  message?: string;

  /**
   * Optional logo or icon to display
   */
  logo?: React.ReactNode;

  /**
   * Whether the loading screen is full page
   * @default true
   */
  fullPage?: boolean;

  /**
   * Background color variant
   * @default 'white'
   */
  background?: 'white' | 'gray' | 'transparent';

  /**
   * Size of the spinner
   * @default 'lg'
   */
  spinnerSize?: 'sm' | 'md' | 'lg';

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Whether to show a backdrop overlay
   * @default false
   */
  overlay?: boolean;

  /**
   * Custom content to render below the spinner
   */
  children?: React.ReactNode;
}

const backgroundClasses = {
  white: 'bg-white',
  gray: 'bg-gray-50',
  transparent: 'bg-transparent',
};

/**
 * LoadingScreen component for full-page or inline loading states
 *
 * @example
 * ```tsx
 * // Full page loading
 * <LoadingScreen message="Loading recipes..." />
 *
 * // With logo
 * <LoadingScreen
 *   logo={<img src="/logo.svg" alt="Logo" className="h-16 w-16" />}
 *   message="Initializing application..."
 * />
 *
 * // Inline loading
 * <LoadingScreen
 *   fullPage={false}
 *   message="Loading..."
 *   spinnerSize="md"
 * />
 *
 * // With overlay
 * <LoadingScreen overlay message="Saving changes..." />
 * ```
 */
export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message,
  logo,
  fullPage = true,
  background = 'white',
  spinnerSize = 'lg',
  className = '',
  overlay = false,
  children,
}) => {
  const containerClasses = fullPage
    ? `fixed inset-0 z-40 flex items-center justify-center ${backgroundClasses[background]}`
    : `flex items-center justify-center p-8 ${backgroundClasses[background]}`;

  const overlayClasses = overlay ? 'bg-black bg-opacity-50' : '';

  const content = (
    <div
      className={`
        ${containerClasses}
        ${overlayClasses}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="flex flex-col items-center gap-4">
        {/* Logo */}
        {logo && <div className="mb-2">{logo}</div>}

        {/* Spinner */}
        <Spinner
          size={spinnerSize}
          color={overlay ? 'white' : 'primary'}
          label={message ?? 'Loading...'}
        />

        {/* Message */}
        {message && (
          <p
            className={`
              text-center font-medium
              ${spinnerSize === 'sm' ? 'text-sm' : spinnerSize === 'md' ? 'text-base' : 'text-lg'}
              ${overlay ? 'text-white' : 'text-gray-700'}
            `.trim().replace(/\s+/g, ' ')}
          >
            {message}
          </p>
        )}

        {/* Custom content */}
        {children && <div className="mt-2">{children}</div>}
      </div>
    </div>
  );

  return content;
};

/**
 * PageLoader component for route transitions
 */
export interface PageLoaderProps {
  /**
   * Whether the loader is active
   */
  isLoading: boolean;

  /**
   * Optional message to display
   */
  message?: string;

  /**
   * Minimum display duration in milliseconds
   * @default 300
   */
  minimumDuration?: number;
}

/**
 * PageLoader component that ensures minimum display duration for smoother UX
 *
 * @example
 * ```tsx
 * <PageLoader isLoading={isNavigating} message="Loading page..." />
 * ```
 */
export const PageLoader: React.FC<PageLoaderProps> = ({
  isLoading,
  message = 'Loading...',
  minimumDuration = 300,
}) => {
  const [shouldShow, setShouldShow] = React.useState(isLoading);
  const startTimeRef = React.useRef<number | null>(null);

  React.useEffect(() => {
    if (isLoading) {
      startTimeRef.current = Date.now();
      setShouldShow(true);
      return undefined;
    }

    if (!startTimeRef.current) {
      return undefined;
    }

    const elapsed = Date.now() - startTimeRef.current;
    const remaining = minimumDuration - elapsed;

    if (remaining > 0) {
      const timer = setTimeout(() => {
        setShouldShow(false);
        startTimeRef.current = null;
      }, remaining);

      return () => { clearTimeout(timer); };
    }

    setShouldShow(false);
    startTimeRef.current = null;
    return undefined;
  }, [isLoading, minimumDuration]);

  if (!shouldShow) {
    return null;
  }

  return <LoadingScreen message={message} overlay />;
};

/**
 * SkeletonLoader component for content placeholders
 */
export interface SkeletonLoaderProps {
  /**
   * Type of skeleton loader
   */
  variant?: 'text' | 'circular' | 'rectangular' | 'card';

  /**
   * Width of the skeleton
   */
  width?: string | number;

  /**
   * Height of the skeleton
   */
  height?: string | number;

  /**
   * Number of lines (for text variant)
   */
  lines?: number;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * SkeletonLoader component for loading placeholders
 *
 * @example
 * ```tsx
 * // Text skeleton
 * <SkeletonLoader variant="text" lines={3} />
 *
 * // Card skeleton
 * <SkeletonLoader variant="card" height={200} />
 *
 * // Circular avatar
 * <SkeletonLoader variant="circular" width={48} height={48} />
 * ```
 */
export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'rectangular',
  width,
  height,
  lines = 1,
  className = '',
}) => {
  const baseClasses = 'animate-pulse bg-gray-200';

  if (variant === 'text') {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`h-4 ${baseClasses} rounded`}
            style={{
              width: index === lines - 1 ? '80%' : '100%',
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circular') {
    return (
      <div
        className={`${baseClasses} rounded-full ${className}`}
        style={{
          width: width ?? '48px',
          height: height ?? '48px',
        }}
      />
    );
  }

  if (variant === 'card') {
    return (
      <div className={`${baseClasses} rounded-lg ${className}`} style={{ height: height ?? 200 }}>
        <div className="p-4 space-y-3">
          <div className="h-4 bg-gray-300 rounded w-3/4" />
          <div className="h-4 bg-gray-300 rounded w-1/2" />
          <div className="h-4 bg-gray-300 rounded w-5/6" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={`${baseClasses} rounded ${className}`}
      style={{
        width: width ?? '100%',
        height: height ?? '20px',
      }}
    />
  );
};

export default LoadingScreen;
