/**
 * Meal planner sidebar with recipe search, filters, and shortlist.
 */

import React, { useState } from 'react';
import { useInfiniteRecipes } from '../../hooks/useRecipes';
import { DraggableRecipe } from './DraggableRecipe';
import { ShortlistPanel } from './ShortlistPanel';
import { useShortlistStore } from '../../store/shortlistStore';
import { RecipeFilters as RecipeFiltersComponent } from '../recipes/RecipeFilters';
import { useCategories, useDietaryTags, useAllergens } from '../../hooks/useCategories';
import type { RecipeFilters, PaginatedResponse, RecipeListItem } from '../../types';
import type { InfiniteData } from '@tanstack/react-query';
import {
  Search,
  Filter,
  ChevronDown,
  ChevronUp,
  Loader2,
  Library,
  Bookmark,
} from 'lucide-react';

type SidebarTab = 'library' | 'shortlist';

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
  const [activeTab, setActiveTab] = useState<SidebarTab>('library');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(true);
  const [filters, setFilters] = useState<RecipeFilters>({
    only_active: true,
  });
  const shortlistCount = useShortlistStore((state) => state.getCount());

  const { data: categoriesData } = useCategories();
  const { data: dietaryTagsData } = useDietaryTags();
  const { data: allergensData } = useAllergens();

  // Fetch recipes with infinite scroll
  const infiniteQuery = useInfiniteRecipes(
    {
      ...filters,
      ...(searchQuery.length > 0 ? { search_query: searchQuery } : {}),
    },
    undefined,
    20
  );

  const infiniteData = infiniteQuery.data as InfiniteData<PaginatedResponse<RecipeListItem>> | undefined;
  const recipes = infiniteData?.pages.flatMap((page) => page.items) ?? [];

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200">
      {/* Tab Headers */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('library')}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors
            ${
              activeTab === 'library'
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }
          `}
        >
          <Library className="w-4 h-4" />
          Library
        </button>
        <button
          onClick={() => setActiveTab('shortlist')}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors relative
            ${
              activeTab === 'shortlist'
                ? 'text-amber-600 border-b-2 border-amber-500 bg-amber-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }
          `}
        >
          <Bookmark className="w-4 h-4" />
          Shortlist
          {shortlistCount > 0 && (
            <span className="absolute top-2 right-2 px-1.5 py-0.5 bg-amber-500 text-white text-xs rounded-full min-w-[18px] text-center">
              {shortlistCount}
            </span>
          )}
        </button>
      </div>

      {/* Shortlist Tab Content */}
      {activeTab === 'shortlist' ? (
        <ShortlistPanel className="flex-1" />
      ) : (
        <>
          {/* Library Tab Header */}
          <div className="p-4 border-b border-gray-200">
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
          </div>
          {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {/* Filters Panel */}
        {showFilters && (
          <RecipeFiltersComponent
            filters={filters}
            onFiltersChange={setFilters}
            categories={categoriesData ?? []}
            dietaryTags={dietaryTagsData ?? []}
            allergens={allergensData ?? []}
            showApplyButton={false}
            showSorting={false}
            className="mt-3"
          />
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
        {infiniteQuery.isLoading ? (
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
            {infiniteQuery.hasNextPage && (
              <button
                onClick={() => infiniteQuery.fetchNextPage()}
                disabled={infiniteQuery.isFetchingNextPage}
                className="w-full py-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50"
              >
                {infiniteQuery.isFetchingNextPage ? (
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
        </>
      )}
    </div>
  );
};
