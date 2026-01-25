/**
 * Shortlist panel for meal planner sidebar.
 * Displays saved recipes that can be dragged to meal slots.
 */

import React from 'react';
import { useShortlistStore } from '../../store/shortlistStore';
import { DraggableRecipe } from './DraggableRecipe';
import { Bookmark, Trash2 } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface ShortlistPanelProps {
  className?: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const ShortlistPanel: React.FC<ShortlistPanelProps> = ({
  className = '',
}) => {
  const { state, removeRecipe, clearAll, getCount } = useShortlistStore();
  const count = getCount();

  return (
    <div className={`flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 pb-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bookmark className="w-4 h-4 text-amber-500" />
            <span className="text-sm font-medium text-gray-700">
              {count} {count === 1 ? 'recipe' : 'recipes'} saved
            </span>
          </div>
          {count > 0 && (
            <button
              onClick={clearAll}
              className="text-xs text-gray-500 hover:text-red-600 flex items-center gap-1 transition-colors"
              title="Clear all"
            >
              <Trash2 className="w-3 h-3" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Recipe List */}
      <div className="flex-1 overflow-y-auto p-4">
        {count === 0 ? (
          <div className="text-center py-8">
            <Bookmark className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No saved recipes</p>
            <p className="text-sm text-gray-400 mt-1">
              Save recipes from the browser to add them here
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {state.recipes.map((recipe) => (
              <DraggableRecipe
                key={recipe.id}
                recipe={recipe}
                dragId={`shortlist-recipe-${recipe.id}`}
                compact
                showRemoveButton
                onRemove={() => removeRecipe(recipe.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ShortlistPanel;
