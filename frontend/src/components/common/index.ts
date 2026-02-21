/**
 * Common UI Components
 *
 * This module exports all reusable UI components for the meal-planner application.
 * All components are fully typed with TypeScript and use Tailwind CSS for styling.
 */

// Button components
export { Button } from './Button';
export type { ButtonProps, ButtonVariant, ButtonSize } from './Button';

// Card components
export { Card } from './Card';
export type { CardProps } from './Card';

// Modal components
export { Modal } from './Modal';
export type { ModalProps, ModalSize } from './Modal';

// ConfirmModal components
export { ConfirmModal } from './ConfirmModal';
export type { ConfirmModalProps, ConfirmModalVariant } from './ConfirmModal';

// Spinner components
export { Spinner, SpinnerOverlay } from './Spinner';
export type {
  SpinnerProps,
  SpinnerOverlayProps,
  SpinnerSize,
  SpinnerColor,
} from './Spinner';

// Pagination components
export { Pagination } from './Pagination';
export type { PaginationProps } from './Pagination';

// SearchBar components
export { SearchBar } from './SearchBar';
export type { SearchBarProps } from './SearchBar';

// Badge components
export { Badge, BadgeGroup } from './Badge';
export type { BadgeProps, BadgeGroupProps, BadgeColor, BadgeSize } from './Badge';

// FilterPanel components
export { FilterPanel } from './FilterPanel';
export type {
  FilterPanelProps,
  FilterSection,
  FilterOption,
  RangeFilter,
} from './FilterPanel';

// EmptyState components
export { EmptyState } from './EmptyState';
export type { EmptyStateProps } from './EmptyState';

// ErrorBoundary components
export { ErrorBoundary, useErrorHandler } from './ErrorBoundary';
export type { ErrorBoundaryProps } from './ErrorBoundary';

// LoadingScreen components
export { LoadingScreen, PageLoader, SkeletonLoader } from './LoadingScreen';
export type {
  LoadingScreenProps,
  PageLoaderProps,
  SkeletonLoaderProps,
} from './LoadingScreen';
