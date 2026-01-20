/**
 * Meal planner sidebar with recipe search and filters.
 */

import React, { useState } from 'react';
import { useInfiniteRecipes } from '../../hooks/useRecipes';
import { DraggableRecipe } from './DraggableRecipe';
import type { RecipeFilters, DifficultyLevel } from '../../types';
import {
  Search,
  Filter,
  X,
  ChevronDown,
  ChevronUp,
  Loader2,
} from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface PlannerSidebarProps {
  onGeneratePlan: () => void;
  isGenerating?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const PlannerSidebar: React.FC<PlannerSidebarProps> = ({
  onGeneratePlan,
  isGenerating = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<RecipeFilters>({
    search_query: '',
    only_active: true,
  });

  // Fetch recipes with infinite scroll
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteRecipes(
    {
      ...filters,
      search_query: searchQuery.length > 0 ? searchQuery : undefined,
    },
    undefined,
    20
  );

  const recipes = data?.pages?.flatMap((page: any) => page.items) ?? [];

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleFilterChange = (key: keyof RecipeFilters, value: unknown) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({ search_query: '', only_active: true });
    setSearchQuery('');
  };

  const hasActiveFilters = !!(
    filters.max_cooking_time ||
    filters.difficulty?.length ||
    filters.dietary_tag_slugs?.length ||
    filters.exclude_allergen_names?.length
  );

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Recipe Library</h2>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search recipes..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="mt-3 w-full flex items-center justify-between px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium">Filters</span>
            {hasActiveFilters && (
              <span className="px-2 py-0.5 bg-indigo-500 text-white text-xs rounded-full">
                Active
              </span>
            )}
          </div>
          {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg space-y-3 border border-gray-200">
            {/* Max Cooking Time */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Max Cooking Time (minutes)
              </label>
              <input
                type="number"
                value={filters.max_cooking_time || ''}
                onChange={(e) =>
                  handleFilterChange('max_cooking_time', e.target.value ? Number(e.target.value) : undefined)
                }
                placeholder="e.g., 30"
                className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Difficulty */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Difficulty
              </label>
              <div className="flex gap-2">
                {(['easy', 'medium', 'hard'] as DifficultyLevel[]).map((level) => (
                  <button
                    key={level}
                    onClick={() => {
                      const current = filters.difficulty || [];
                      const updated = current.includes(level)
                        ? current.filter((d) => d !== level)
                        : [...current, level];
                      handleFilterChange('difficulty', updated.length ? updated : undefined);
                    }}
                    className={`
                      flex-1 px-2 py-1.5 text-xs rounded transition-colors
                      ${
                        filters.difficulty?.includes(level)
                          ? 'bg-indigo-500 text-white'
                          : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                      }
                    `}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="w-full flex items-center justify-center gap-2 px-3 py-1.5 bg-white border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50"
              >
                <X className="w-3 h-3" />
                Clear Filters
              </button>
            )}
          </div>
        )}

        {/* Generate Plan Button */}
        <button
          onClick={onGeneratePlan}
          disabled={isGenerating}
          className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-lg font-medium hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : (
            'Generate Meal Plan'
          )}
        </button>
      </div>

      {/* Recipe List */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : recipes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No recipes found</p>
            <p className="text-sm text-gray-400 mt-1">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recipes.map((recipe: any) => (
              <DraggableRecipe
                key={recipe.id}
                recipe={recipe}
                dragId={`sidebar-recipe-${recipe.id}`}
                compact
                showRemoveButton={false}
              />
            ))}

            {/* Load More Button */}
            {hasNextPage && (
              <button
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                className="w-full py-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {isFetchingNextPage ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading...
                  </span>
                ) : (
                  'Load More'
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
