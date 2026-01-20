/**
 * FavoriteButton - Toggle button for adding/removing recipes from favorites.
 */

import React, { useState } from 'react';
import { useAddFavorite, useRemoveFavorite, useIsFavorite } from '../../hooks/useFavorites';
import { Spinner } from '../common/Spinner';

interface FavoriteButtonProps {
  recipeId: number;
  recipeName?: string;
  size?: 'sm' | 'md' | 'lg';
  showTooltip?: boolean;
  onToggle?: (isFavorite: boolean) => void;
  className?: string;
}

export const FavoriteButton: React.FC<FavoriteButtonProps> = ({
  recipeId,
  recipeName = 'this recipe',
  size = 'md',
  showTooltip = true,
  onToggle,
  className = '',
}) => {
  const [showFeedback, setShowFeedback] = useState(false);

  const { data: isFavorite = false, isLoading: isCheckingFavorite } = useIsFavorite(recipeId);
  const addMutation = useAddFavorite();
  const removeMutation = useRemoveFavorite();

  const isLoading = isCheckingFavorite || addMutation.isPending || removeMutation.isPending;

  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const handleToggle = async (e: React.MouseEvent): Promise<void> => {
    e.preventDefault();
    e.stopPropagation();

    try {
      if (isFavorite) {
        await removeMutation.mutateAsync(recipeId);
      } else {
        await addMutation.mutateAsync({ recipe_id: recipeId });
      }

      if (onToggle) {
        onToggle(!isFavorite);
      }

      setShowFeedback(true);
      setTimeout(() => setShowFeedback(false), 2000);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const tooltipText = isFavorite
    ? `Remove ${recipeName} from favorites`
    : `Add ${recipeName} to favorites`;

  const feedbackText = isFavorite
    ? `Added to favorites!`
    : `Removed from favorites`;

  return (
    <div className="relative inline-block">
      <button
        onClick={handleToggle}
        disabled={isLoading}
        className={`
          relative inline-flex items-center justify-center
          ${sizeClasses[size]}
          rounded-full
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
          ${isLoading ? 'cursor-wait opacity-50' : 'cursor-pointer hover:scale-110'}
          ${isFavorite ? 'text-red-500' : 'text-gray-400 hover:text-red-400'}
          ${className}
        `}
        aria-label={tooltipText}
        title={showTooltip ? tooltipText : undefined}
      >
        {isLoading ? (
          <Spinner size="sm" className={iconSize[size]} />
        ) : (
          <svg
            className={`${iconSize[size]} transition-all duration-200`}
            fill={isFavorite ? 'currentColor' : 'none'}
            stroke="currentColor"
            strokeWidth={isFavorite ? '0' : '2'}
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        )}
      </button>

      {showFeedback && !isLoading && (
        <div
          className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-md whitespace-nowrap z-50 animate-fade-in-up"
          role="status"
          aria-live="polite"
        >
          {feedbackText}
        </div>
      )}
    </div>
  );
};
