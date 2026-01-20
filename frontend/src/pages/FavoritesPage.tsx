/**
 * FavoritesPage - Display and manage user's favorite recipes.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FavoritesList } from '../components/favorites/FavoritesList';
import { Button } from '../components/common/Button';
import { FavoritesSortBy } from '../types';

export const FavoritesPage: React.FC = () => {
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState<FavoritesSortBy>(FavoritesSortBy.DATE_ADDED_DESC);

  const handleAddAllToMealPlan = (recipeIds: number[]): void => {
    console.log('Adding recipes to meal plan:', recipeIds);
    navigate('/meal-plans/new', { state: { recipeIds } });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Favorites</h1>
              <p className="mt-2 text-sm text-gray-600">
                Manage your favorite recipes and quickly add them to meal plans
              </p>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as FavoritesSortBy)}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value={FavoritesSortBy.DATE_ADDED_DESC}>Recently Added</option>
                <option value={FavoritesSortBy.DATE_ADDED_ASC}>Oldest First</option>
                <option value={FavoritesSortBy.NAME_ASC}>Name (A-Z)</option>
                <option value={FavoritesSortBy.NAME_DESC}>Name (Z-A)</option>
              </select>

              <Button
                variant="outline"
                onClick={() => navigate('/recipes')}
              >
                Browse Recipes
              </Button>
            </div>
          </div>
        </div>

        {/* Favorites List */}
        <FavoritesList
          sortBy={sortBy}
          onSortChange={setSortBy}
          showAddAllToMealPlan={true}
          onAddAllToMealPlan={handleAddAllToMealPlan}
        />
      </div>
    </div>
  );
};
