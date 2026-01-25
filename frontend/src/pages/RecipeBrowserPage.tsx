import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { InfiniteData } from '@tanstack/react-query';
import { SearchBar } from '../components/common';
import { RecipeList, RecipeFilters } from '../components/recipes';
import { useInfiniteRecipes } from '../hooks/useRecipes';
import { useCategories, useDietaryTags, useAllergens } from '../hooks/useCategories';
import type { RecipeFilters as RecipeFiltersType, RecipeListItem, PaginatedResponse, SortParams } from '../types';
import { SortOrder } from '../types';
import { ChevronRightIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';

/**
 * RecipeBrowserPage component props
 */
export interface RecipeBrowserPageProps {
  /**
   * Callback when a recipe is added to meal plan
   */
  onAddToMealPlan?: (recipe: RecipeListItem) => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Parse filters from URL search params
 */
const parseFiltersFromUrl = (searchParams: URLSearchParams): RecipeFiltersType => {
  const filters: RecipeFiltersType = {
    only_active: true,
  };

  // Search query
  const search = searchParams.get('search');
  if (search) {
    filters.search_query = search;
  }

  // Categories
  const categories = searchParams.getAll('category');
  if (categories.length > 0) {
    filters.category_slugs = categories;
  }

  // Dietary tags
  const dietaryTags = searchParams.getAll('dietary');
  if (dietaryTags.length > 0) {
    filters.dietary_tag_slugs = dietaryTags;
  }

  // Allergens
  const allergens = searchParams.getAll('exclude_allergen');
  if (allergens.length > 0) {
    filters.exclude_allergen_names = allergens;
  }

  // Difficulty
  const difficulty = searchParams.getAll('difficulty');
  if (difficulty.length > 0) {
    filters.difficulty = difficulty as any[];
  }

  // Max cooking time
  const maxTime = searchParams.get('max_time');
  if (maxTime) {
    filters.max_cooking_time = parseInt(maxTime, 10);
  }

  // Nutrition filters
  const maxCalories = searchParams.get('max_calories');
  const minProtein = searchParams.get('min_protein');
  const maxCarbs = searchParams.get('max_carbs');
  const maxFat = searchParams.get('max_fat');

  if (maxCalories || minProtein || maxCarbs || maxFat) {
    filters.nutrition = {};
    if (maxCalories) filters.nutrition.max_calories = parseInt(maxCalories, 10);
    if (minProtein) filters.nutrition.min_protein_g = parseInt(minProtein, 10);
    if (maxCarbs) filters.nutrition.max_carbs_g = parseInt(maxCarbs, 10);
    if (maxFat) filters.nutrition.max_fat_g = parseInt(maxFat, 10);
  }

  return filters;
};

/**
 * Parse sort params from URL search params
 */
const parseSortFromUrl = (searchParams: URLSearchParams): SortParams => {
  const sortBy = searchParams.get('sort_by');
  const sortOrderStr = searchParams.get('sort_order');
  const sortOrder = sortOrderStr === 'desc' ? SortOrder.DESC : SortOrder.ASC;

  const params: SortParams = { sort_order: sortOrder };
  if (sortBy) {
    params.sort_by = sortBy;
  }
  return params;
};

/**
 * Update URL with current filters and sort params
 */
const updateUrlWithFilters = (
  filters: RecipeFiltersType,
  sortParams: SortParams,
  setSearchParams: (params: URLSearchParams) => void
) => {
  const params = new URLSearchParams();

  if (filters.search_query) {
    params.set('search', filters.search_query);
  }

  filters.category_slugs?.forEach((cat) => params.append('category', cat));
  filters.dietary_tag_slugs?.forEach((tag) => params.append('dietary', tag));
  filters.exclude_allergen_names?.forEach((allergen) => params.append('exclude_allergen', allergen));
  filters.difficulty?.forEach((diff) => params.append('difficulty', diff));

  if (filters.max_cooking_time) {
    params.set('max_time', filters.max_cooking_time.toString());
  }

  if (filters.nutrition) {
    if (filters.nutrition.max_calories) {
      params.set('max_calories', filters.nutrition.max_calories.toString());
    }
    if (filters.nutrition.min_protein_g) {
      params.set('min_protein', filters.nutrition.min_protein_g.toString());
    }
    if (filters.nutrition.max_carbs_g) {
      params.set('max_carbs', filters.nutrition.max_carbs_g.toString());
    }
    if (filters.nutrition.max_fat_g) {
      params.set('max_fat', filters.nutrition.max_fat_g.toString());
    }
  }

  // Sort params
  if (sortParams.sort_by) {
    params.set('sort_by', sortParams.sort_by);
    params.set('sort_order', sortParams.sort_order);
  }

  setSearchParams(params);
};

/**
 * RecipeBrowserPage component
 *
 * Main recipe browsing page with search, filters, and infinite scroll.
 * Filters are synced with URL parameters.
 *
 * @example
 * ```tsx
 * <RecipeBrowserPage
 *   onAddToMealPlan={(recipe) => handleAddToMealPlan(recipe)}
 * />
 * ```
 */
export const RecipeBrowserPage: React.FC<RecipeBrowserPageProps> = ({
  onAddToMealPlan,
  className = '',
}) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<RecipeFiltersType>(() => parseFiltersFromUrl(searchParams));
  const [sortParams, setSortParams] = useState<SortParams>(() => parseSortFromUrl(searchParams));
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Fetch filter options
  const { data: categories = [] } = useCategories();
  const { data: dietaryTags = [] } = useDietaryTags();
  const { data: allergens = [] } = useAllergens();

  // Fetch recipes with infinite scroll
  const {
    data: infiniteData,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteRecipes(filters, sortParams, 20);

  // Flatten paginated results from infinite query
  const recipes = (infiniteData as InfiniteData<PaginatedResponse<RecipeListItem>> | undefined)?.pages?.flatMap((page) => page.items) ?? [];

  // Update filters when search query changes
  useEffect(() => {
    setFilters((prev) => {
      const newFilters = { ...prev };
      if (searchQuery) {
        newFilters.search_query = searchQuery;
      } else {
        delete newFilters.search_query;
      }
      return newFilters;
    });
  }, [searchQuery]);

  // Sync URL with filters and sort params
  useEffect(() => {
    updateUrlWithFilters(filters, sortParams, setSearchParams);
  }, [filters, sortParams, setSearchParams]);

  const handleFiltersChange = (newFilters: RecipeFiltersType) => {
    setFilters(newFilters);
  };

  const handleSortChange = (newSortParams: SortParams) => {
    setSortParams(newSortParams);
  };

  const handleLoadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const totalResults = (infiniteData as InfiniteData<PaginatedResponse<RecipeListItem>> | undefined)?.pages?.[0]?.total ?? 0;

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Browse Recipes</h1>
          <p className="text-gray-600">
            {totalResults > 0
              ? `Showing ${recipes.length} of ${totalResults} recipes`
              : 'Search and filter to find your perfect recipe'}
          </p>
        </div>

        {/* Search bar */}
        <div className="mb-6">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search recipes by name or ingredient..."
            size="lg"
            fullWidth
            aria-label="Search recipes"
          />
        </div>

        {/* Main content with sidebar */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar - Filters */}
          <div className="lg:w-80 flex-shrink-0">
            {/* Mobile filter toggle */}
            <button
              type="button"
              onClick={toggleSidebar}
              className="lg:hidden w-full mb-4 flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <AdjustmentsHorizontalIcon className="h-5 w-5" aria-hidden="true" />
              {isSidebarOpen ? 'Hide Filters' : 'Show Filters'}
            </button>

            {/* Filter panel */}
            <div className={`${isSidebarOpen ? 'block' : 'hidden lg:block'}`}>
              <RecipeFilters
                filters={filters}
                onFiltersChange={handleFiltersChange}
                categories={categories}
                dietaryTags={dietaryTags}
                allergens={allergens}
                showApplyButton={false}
                sortParams={sortParams}
                onSortChange={handleSortChange}
                showSorting
              />
            </div>
          </div>

          {/* Recipe grid */}
          <div className="flex-1">
            <RecipeList
              recipes={recipes}
              loading={isLoading}
              {...(error?.message && { error: error.message })}
              {...(onAddToMealPlan && { onAddToMealPlan })}
              columns={{ sm: 1, md: 2, lg: 2, xl: 3 }}
            />

            {/* Load more button */}
            {hasNextPage && (
              <div className="mt-8 flex justify-center">
                <button
                  type="button"
                  onClick={handleLoadMore}
                  disabled={isFetchingNextPage}
                  className="
                    flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg
                    hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    transition-colors
                  "
                >
                  {isFetchingNextPage ? (
                    <>
                      <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                      Loading...
                    </>
                  ) : (
                    <>
                      Load More Recipes
                      <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                    </>
                  )}
                </button>
              </div>
            )}

            {/* No more results message */}
            {!hasNextPage && recipes.length > 0 && (
              <div className="mt-8 text-center text-gray-500">
                You've reached the end of the results
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeBrowserPage;
