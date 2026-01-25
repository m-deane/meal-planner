import React, { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Button } from './Button';

/**
 * ErrorBoundary component props interface
 */
export interface ErrorBoundaryProps {
  /**
   * Child components to render
   */
  children: ReactNode;

  /**
   * Optional fallback UI to render when an error occurs
   */
  fallback?: (error: Error, resetError: () => void) => ReactNode;

  /**
   * Callback when an error is caught
   */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;

  /**
   * Whether to show the default error UI
   * @default true
   */
  showDefaultUI?: boolean;

  /**
   * Custom error title
   */
  errorTitle?: string;

  /**
   * Custom error description
   */
  errorDescription?: string;
}

/**
 * ErrorBoundary component state interface
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Default error fallback component
 */
interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  title?: string;
  description?: string;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  title = 'Something went wrong',
  description = "We're sorry, but something unexpected happened. Please try again.",
}) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div className="flex min-h-[400px] items-center justify-center p-8">
      <div className="max-w-md w-full">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          {/* Icon */}
          <div className="flex items-center justify-center mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600">
              <ExclamationTriangleIcon className="h-6 w-6" aria-hidden="true" />
            </div>
          </div>

          {/* Title */}
          <h2 className="text-center text-lg font-semibold text-gray-900 mb-2">{title}</h2>

          {/* Description */}
          <p className="text-center text-sm text-gray-600 mb-6">{description}</p>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            <Button
              variant="primary"
              onClick={resetError}
              iconLeft={<ArrowPathIcon className="h-4 w-4" />}
              fullWidth
            >
              Try Again
            </Button>

            <Button
              variant="ghost"
              onClick={() => { setShowDetails(!showDetails); }}
              size="sm"
              fullWidth
            >
              {showDetails ? 'Hide Details' : 'Show Details'}
            </Button>
          </div>

          {/* Error details */}
          {showDetails && (
            <div className="mt-4 rounded-md bg-white p-4 border border-red-200">
              <div className="text-xs">
                <div className="font-semibold text-gray-900 mb-2">Error Details:</div>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium text-gray-700">Message: </span>
                    <span className="text-gray-600">{error.message}</span>
                  </div>
                  {error.stack && (
                    <div>
                      <span className="font-medium text-gray-700">Stack trace: </span>
                      <pre className="mt-1 overflow-auto rounded bg-gray-100 p-2 text-xs text-gray-800">
                        {error.stack}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * ErrorBoundary component to catch and handle React errors gracefully
 *
 * @example
 * ```tsx
 * // Basic usage
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 *
 * // With custom fallback
 * <ErrorBoundary
 *   fallback={(error, resetError) => (
 *     <div>
 *       <h1>Oops! {error.message}</h1>
 *       <button onClick={resetError}>Try again</button>
 *     </div>
 *   )}
 * >
 *   <App />
 * </ErrorBoundary>
 *
 * // With error reporting
 * <ErrorBoundary
 *   onError={(error, errorInfo) => {
 *     logErrorToService(error, errorInfo);
 *   }}
 * >
 *   <App />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    this.setState({
      errorInfo,
    });

    // Call onError callback if provided
    this.props.onError?.(error, errorInfo);
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  override render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback, showDefaultUI = true, errorTitle, errorDescription } = this.props;

    if (hasError && error) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback(error, this.resetError);
      }

      // Use default error UI if enabled
      if (showDefaultUI) {
        const fallbackProps: ErrorFallbackProps = {
          error,
          resetError: this.resetError,
          ...(errorTitle && { title: errorTitle }),
          ...(errorDescription && { description: errorDescription }),
        };

        return <ErrorFallback {...fallbackProps} />;
      }

      // Return null if no UI should be shown
      return null;
    }

    return children;
  }
}

/**
 * Hook to use with ErrorBoundary for functional components
 * This is a helper to trigger error boundaries from event handlers
 */
export const useErrorHandler = (): ((error: Error) => void) => {
  const [, setError] = React.useState<Error>();

  return React.useCallback((error: Error) => {
    setError(() => {
      throw error;
    });
  }, []);
};

export default ErrorBoundary;
