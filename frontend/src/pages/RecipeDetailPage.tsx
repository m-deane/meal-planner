import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeftIcon, HomeIcon } from '@heroicons/react/24/outline';
import { RecipeDetail } from '../components/recipes';
import { LoadingScreen, EmptyState, Button } from '../components/common';
import { useRecipeBySlug } from '../hooks/useRecipes';
import type { Recipe } from '../types';

/**
 * RecipeDetailPage component props
 */
export interface RecipeDetailPageProps {
  /**
   * Callback when "Add to meal plan" is clicked
   */
  onAddToMealPlan?: (recipe: Recipe) => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * RecipeDetailPage component
 *
 * Page component that displays full recipe details, handles loading/error states,
 * and provides breadcrumb navigation.
 *
 * @example
 * ```tsx
 * <RecipeDetailPage
 *   onAddToMealPlan={(recipe) => handleAddToMealPlan(recipe)}
 * />
 * ```
 */
export const RecipeDetailPage: React.FC<RecipeDetailPageProps> = ({
  onAddToMealPlan,
  className = '',
}) => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const { data: recipe, isLoading, error } = useRecipeBySlug(slug || '');

  const handlePrint = () => {
    window.print();
  };

  const handleShare = async () => {
    if (recipe && navigator.share) {
      try {
        await navigator.share({
          title: recipe.name,
          text: recipe.description || `Check out this recipe: ${recipe.name}`,
          url: window.location.href,
        });
      } catch (err) {
        // User cancelled or share failed
        console.error('Error sharing:', err);
      }
    } else if (recipe) {
      // Fallback: Copy URL to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href);
        alert('Recipe link copied to clipboard!');
      } catch (err) {
        console.error('Error copying to clipboard:', err);
      }
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  // Loading state
  if (isLoading) {
    return <LoadingScreen message="Loading recipe..." />;
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <EmptyState
          title="Error loading recipe"
          description={error.message || 'The recipe could not be loaded. Please try again.'}
        >
          <Button variant="primary" onClick={() => navigate('/recipes')}>
            Browse All Recipes
          </Button>
        </EmptyState>
      </div>
    );
  }

  // Not found state
  if (!recipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <EmptyState
          title="Recipe not found"
          description="The recipe you're looking for doesn't exist or has been removed."
        >
          <Button variant="primary" onClick={() => navigate('/recipes')}>
            Browse All Recipes
          </Button>
        </EmptyState>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Breadcrumb navigation */}
      <nav className="bg-white border-b border-gray-200 print:hidden">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-2 text-sm">
            <Link
              to="/"
              className="flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <HomeIcon className="h-4 w-4" aria-hidden="true" />
              Home
            </Link>
            <ChevronLeftIcon className="h-4 w-4 text-gray-400 rotate-180" aria-hidden="true" />
            <Link
              to="/recipes"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Recipes
            </Link>
            <ChevronLeftIcon className="h-4 w-4 text-gray-400 rotate-180" aria-hidden="true" />
            <span className="text-gray-900 font-medium truncate max-w-xs">
              {recipe.name}
            </span>
          </div>
        </div>
      </nav>

      {/* Back button (mobile) */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 print:hidden">
        <button
          type="button"
          onClick={handleBack}
          className="
            flex items-center gap-2 text-gray-600 hover:text-gray-900
            focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1
            transition-colors
          "
        >
          <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
          Back
        </button>
      </div>

      {/* Recipe detail */}
      <RecipeDetail
        recipe={recipe}
        {...(onAddToMealPlan && { onAddToMealPlan })}
        onPrint={handlePrint}
        onShare={handleShare}
      />

      {/* Print styles */}
      <style>
        {`
          @media print {
            .print\\:hidden {
              display: none !important;
            }

            body {
              background: white;
            }

            /* Hide navigation and buttons when printing */
            button, nav {
              display: none !important;
            }

            /* Adjust layout for printing */
            .max-w-5xl {
              max-width: 100% !important;
            }

            /* Ensure ingredients and instructions are on the same page if possible */
            .md\\:col-span-1, .md\\:col-span-2 {
              break-inside: avoid;
            }

            /* Page breaks */
            h1, h2, h3 {
              break-after: avoid;
              page-break-after: avoid;
            }
          }
        `}
      </style>
    </div>
  );
};

export default RecipeDetailPage;
