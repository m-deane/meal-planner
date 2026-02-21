/**
 * FavoritesList - Grid display of favorite recipes with management options.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useFavorites, useRemoveFavorite } from '../../hooks/useFavorites';
import { FavoriteNoteModal } from './FavoriteNoteModal';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { EmptyState } from '../common/EmptyState';
import { Spinner } from '../common/Spinner';
import type { FavoriteRecipe, FavoritesSortBy } from '../../types';

interface FavoritesListProps {
  sortBy?: FavoritesSortBy;
  onSortChange?: (sortBy: FavoritesSortBy) => void;
  showAddAllToMealPlan?: boolean;
  onAddAllToMealPlan?: (recipeIds: number[]) => void;
}

export const FavoritesList: React.FC<FavoritesListProps> = ({
  sortBy,
  showAddAllToMealPlan = false,
  onAddAllToMealPlan,
}) => {
  const [page, setPage] = useState(1);
  const [editingFavorite, setEditingFavorite] = useState<FavoriteRecipe | null>(null);

  const { data, isLoading, isError } = useFavorites({ page, page_size: 12 }, sortBy);
  const removeMutation = useRemoveFavorite();

  const handleRemove = async (recipeId: number): Promise<void> => {
    if (!window.confirm('Remove this recipe from your favorites?')) {
      return;
    }

    try {
      await removeMutation.mutateAsync(recipeId);
    } catch (error) {
      console.error('Failed to remove favorite:', error);
    }
  };

  const handleAddAllToMealPlan = (): void => {
    if (data && onAddAllToMealPlan) {
      const recipeIds = data.items.map(fav => fav.recipe.id);
      onAddAllToMealPlan(recipeIds);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-sm text-red-600">Failed to load favorites. Please try again.</p>
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <EmptyState
        icon={
          <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        }
        title="No favorites yet"
        description="Start adding recipes to your favorites to see them here"
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">My Favorites</h2>
          <p className="mt-1 text-sm text-gray-600">
            {data.total} {data.total === 1 ? 'recipe' : 'recipes'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {showAddAllToMealPlan && data.items.length > 0 && (
            <Button variant="primary" onClick={handleAddAllToMealPlan}>
              Add All to Meal Plan
            </Button>
          )}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.items.map((favorite) => (
          <Card key={favorite.id} className="flex flex-col">
            <Link to={`/recipes/${favorite.recipe.slug}`} className="block">
              {favorite.recipe.image_url && (
                <img
                  src={favorite.recipe.image_url}
                  alt={favorite.recipe.name}
                  className="w-full h-48 object-cover rounded-t-lg"
                />
              )}
            </Link>

            <div className="flex-1 p-4 space-y-3">
              <Link to={`/recipes/${favorite.recipe.slug}`}>
                <h3 className="font-semibold text-gray-900 hover:text-primary-600 transition-colors">
                  {favorite.recipe.name}
                </h3>
              </Link>

              {favorite.recipe.difficulty && (
                <div className="flex flex-wrap gap-1">
                  <Badge color="default" size="sm">
                    {favorite.recipe.difficulty}
                  </Badge>
                </div>
              )}

              {favorite.notes && (
                <p className="text-sm text-gray-600 line-clamp-2">{favorite.notes}</p>
              )}

              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Added {new Date(favorite.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="px-4 pb-4 pt-2 border-t border-gray-100 flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setEditingFavorite(favorite)}
                className="flex-1"
              >
                {favorite.notes ? 'Edit Notes' : 'Add Notes'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleRemove(favorite.recipe.id)}
                disabled={removeMutation.isPending}
                className="text-red-600 hover:text-red-700 hover:border-red-300"
              >
                Remove
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-6">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-600">
            Page {page} of {data.total_pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
          >
            Next
          </Button>
        </div>
      )}

      {/* Note Modal */}
      {editingFavorite && (
        <FavoriteNoteModal
          isOpen={!!editingFavorite}
          onClose={() => setEditingFavorite(null)}
          favorite={editingFavorite}
        />
      )}
    </div>
  );
};
