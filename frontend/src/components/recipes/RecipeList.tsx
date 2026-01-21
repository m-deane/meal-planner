import React from 'react';
import { RecipeCard } from './RecipeCard';
import { EmptyState, SkeletonLoader } from '../common';
import type { RecipeListItem } from '../../types';

/**
 * RecipeList component props
 */
export interface RecipeListProps {
  /**
   * Array of recipes to display
   */
  recipes: RecipeListItem[];

  /**
   * Whether data is currently loading
   * @default false
   */
  loading?: boolean;

  /**
   * Error message to display
   */
  error?: string | null;

  /**
   * Number of skeleton cards to show when loading
   * @default 8
   */
  skeletonCount?: number;

  /**
   * Callback when "Add to meal plan" is clicked on a recipe
   */
  onAddToMealPlan?: (recipe: RecipeListItem) => void;

  /**
   * Grid columns configuration (responsive)
   * @default { sm: 1, md: 2, lg: 3, xl: 4 }
   */
  columns?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };

  /**
   * Whether to show nutrition info on cards
   * @default true
   */
  showNutrition?: boolean;

  /**
   * Whether to show categories on cards
   * @default true
   */
  showCategories?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Get grid column classes based on configuration
 */
const getGridClasses = (columns: RecipeListProps['columns']): string => {
  const defaults = { sm: 1, md: 2, lg: 3, xl: 4 };
  const config = { ...defaults, ...columns };

  const classes = [];

  if (config.sm === 1) classes.push('grid-cols-1');
  else if (config.sm === 2) classes.push('grid-cols-2');
  else if (config.sm === 3) classes.push('grid-cols-3');
  else if (config.sm === 4) classes.push('grid-cols-4');

  if (config.md === 1) classes.push('md:grid-cols-1');
  else if (config.md === 2) classes.push('md:grid-cols-2');
  else if (config.md === 3) classes.push('md:grid-cols-3');
  else if (config.md === 4) classes.push('md:grid-cols-4');

  if (config.lg === 1) classes.push('lg:grid-cols-1');
  else if (config.lg === 2) classes.push('lg:grid-cols-2');
  else if (config.lg === 3) classes.push('lg:grid-cols-3');
  else if (config.lg === 4) classes.push('lg:grid-cols-4');

  if (config.xl === 1) classes.push('xl:grid-cols-1');
  else if (config.xl === 2) classes.push('xl:grid-cols-2');
  else if (config.xl === 3) classes.push('xl:grid-cols-3');
  else if (config.xl === 4) classes.push('xl:grid-cols-4');

  return classes.join(' ');
};

/**
 * RecipeSkeleton component for loading state
 */
const RecipeSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <SkeletonLoader className="h-48 w-full" />
      <div className="p-4 space-y-3">
        <SkeletonLoader className="h-6 w-3/4" />
        <SkeletonLoader className="h-4 w-full" />
        <SkeletonLoader className="h-4 w-5/6" />
        <div className="flex gap-2">
          <SkeletonLoader className="h-6 w-20" />
          <SkeletonLoader className="h-6 w-16" />
          <SkeletonLoader className="h-6 w-24" />
        </div>
        <div className="flex gap-2">
          <SkeletonLoader className="h-6 w-16" />
          <SkeletonLoader className="h-6 w-20" />
        </div>
      </div>
    </div>
  );
};

/**
 * RecipeList component
 *
 * Displays recipes in a responsive grid layout with loading skeletons
 * and empty state handling.
 *
 * @example
 * ```tsx
 * <RecipeList
 *   recipes={recipes}
 *   loading={isLoading}
 *   error={error}
 *   onAddToMealPlan={(recipe) => handleAddToMealPlan(recipe)}
 *   columns={{ sm: 1, md: 2, lg: 3, xl: 4 }}
 * />
 * ```
 */
export const RecipeList: React.FC<RecipeListProps> = ({
  recipes,
  loading = false,
  error = null,
  skeletonCount = 8,
  onAddToMealPlan,
  columns,
  showNutrition = true,
  showCategories = true,
  className = '',
}) => {
  const gridClasses = getGridClasses(columns);

  // Error state
  if (error) {
    return (
      <EmptyState
        title="Error loading recipes"
        description={error}
        icon="error"
      />
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className={`grid ${gridClasses} gap-6 ${className}`}>
        {Array.from({ length: skeletonCount }).map((_, index) => (
          <RecipeSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Empty state
  if (recipes.length === 0) {
    return (
      <EmptyState
        title="No recipes found"
        description="Try adjusting your filters or search criteria"
        icon="search"
      />
    );
  }

  // Recipe grid
  return (
    <div className={`grid ${gridClasses} gap-6 ${className}`}>
      {recipes.map((recipe) => (
        <RecipeCard
          key={recipe.id}
          recipe={recipe}
          {...(onAddToMealPlan ? { onAddToMealPlan } : {})}
          showNutrition={showNutrition}
          showCategories={showCategories}
        />
      ))}
    </div>
  );
};

export default RecipeList;
