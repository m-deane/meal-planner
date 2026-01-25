/**
 * Shortlist toggle button for recipe cards.
 * Allows users to add/remove recipes from their shortlist.
 */

import React from 'react';
import { BookmarkIcon } from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { useShortlistStore } from '../../store/shortlistStore';
import type { RecipeListItem } from '../../types';

// ============================================================================
// TYPES
// ============================================================================

export interface ShortlistButtonProps {
  recipe: RecipeListItem;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showLabel?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const ShortlistButton: React.FC<ShortlistButtonProps> = ({
  recipe,
  size = 'md',
  className = '',
  showLabel = false,
}) => {
  const { toggleRecipe, isInShortlist } = useShortlistStore();
  const inShortlist = isInShortlist(recipe.id);

  const sizeClasses = {
    sm: 'p-1',
    md: 'p-1.5',
    lg: 'p-2',
  };

  const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggleRecipe(recipe);
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`
        inline-flex items-center gap-1.5 rounded-md transition-all
        ${sizeClasses[size]}
        ${
          inShortlist
            ? 'bg-amber-100 text-amber-600 hover:bg-amber-200'
            : 'bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-700'
        }
        focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-1
        ${className}
      `}
      title={inShortlist ? 'Remove from shortlist' : 'Add to shortlist'}
      aria-label={inShortlist ? 'Remove from shortlist' : 'Add to shortlist'}
      aria-pressed={inShortlist}
    >
      {inShortlist ? (
        <BookmarkSolidIcon className={iconSizes[size]} aria-hidden="true" />
      ) : (
        <BookmarkIcon className={iconSizes[size]} aria-hidden="true" />
      )}
      {showLabel && (
        <span className="text-sm font-medium">
          {inShortlist ? 'Saved' : 'Save'}
        </span>
      )}
    </button>
  );
};

export default ShortlistButton;
