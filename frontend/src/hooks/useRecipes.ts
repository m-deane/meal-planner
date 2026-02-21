/**
 * React Query hooks for recipe data fetching.
 */

import {
  useQuery,
  useInfiniteQuery,
  UseQueryResult,
  UseInfiniteQueryResult,
} from '@tanstack/react-query';
import { useDebounce } from './useDebounce';
import {
  getRecipes,
  getRecipeById,
  getRecipeBySlug,
  searchRecipes,
  getRandomRecipes,
  getFeaturedRecipes,
} from '../api/recipes';
import type {
  Recipe,
  RecipeListItem,
  RecipeFilters,
  PaginatedResponse,
  PaginationParams,
  SortParams,
} from '../types';

/**
 * Query keys for recipes.
 */
export const recipeKeys = {
  all: ['recipes'] as const,
  lists: () => [...recipeKeys.all, 'list'] as const,
  list: (filters?: RecipeFilters, sort?: SortParams) =>
    [...recipeKeys.lists(), { filters, sort }] as const,
  details: () => [...recipeKeys.all, 'detail'] as const,
  detail: (id: number) => [...recipeKeys.details(), id] as const,
  detailBySlug: (slug: string) => [...recipeKeys.details(), 'slug', slug] as const,
  search: (query: string) => [...recipeKeys.all, 'search', query] as const,
  random: () => [...recipeKeys.all, 'random'] as const,
  featured: () => [...recipeKeys.all, 'featured'] as const,
};

/**
 * Fetch paginated recipes with filters (basic query).
 */
export const useRecipes = (
  filters?: RecipeFilters,
  pagination?: PaginationParams,
  sort?: SortParams
): UseQueryResult<PaginatedResponse<RecipeListItem>> => {
  return useQuery({
    queryKey: recipeKeys.list(filters, sort),
    queryFn: () => getRecipes(filters, pagination, sort),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
};

/**
 * Fetch paginated recipes with infinite scroll.
 */
export const useInfiniteRecipes = (
  filters?: RecipeFilters,
  sort?: SortParams,
  pageSize: number = 20
): UseInfiniteQueryResult<PaginatedResponse<RecipeListItem>> => {
  return useInfiniteQuery({
    queryKey: [...recipeKeys.list(filters, sort), 'infinite'],
    queryFn: ({ pageParam = 1 }) => {
      const pagination: PaginationParams = {
        page: pageParam as number,
        page_size: pageSize,
      };
      return getRecipes(filters, pagination, sort);
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      if (!lastPage || !allPages || allPages.length === 0) return undefined;
      return lastPage.has_next ? lastPage.page + 1 : undefined;
    },
    getPreviousPageParam: (firstPage, allPages) => {
      if (!firstPage || !allPages || allPages.length === 0) return undefined;
      return firstPage.has_previous ? firstPage.page - 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

/**
 * Fetch a single recipe by ID.
 */
export const useRecipe = (id: number): UseQueryResult<Recipe> => {
  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: () => getRecipeById(id),
    enabled: !!id && id > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
};

/**
 * Fetch a single recipe by slug.
 */
export const useRecipeBySlug = (slug: string): UseQueryResult<Recipe> => {
  return useQuery({
    queryKey: recipeKeys.detailBySlug(slug),
    queryFn: () => getRecipeBySlug(slug),
    enabled: !!slug,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
};

/**
 * Search recipes with debouncing.
 */
export const useRecipeSearch = (
  query: string,
  debounceMs: number = 300
): UseQueryResult<PaginatedResponse<RecipeListItem>> => {
  const debouncedQuery = useDebounce(query, debounceMs);

  return useQuery({
    queryKey: recipeKeys.search(debouncedQuery),
    queryFn: () => searchRecipes(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Fetch random recipes.
 */
export const useRandomRecipes = (count: number = 10): UseQueryResult<RecipeListItem[]> => {
  return useQuery({
    queryKey: [...recipeKeys.random(), count],
    queryFn: () => getRandomRecipes(count),
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000,
  });
};

/**
 * Fetch featured recipes.
 */
export const useFeaturedRecipes = (): UseQueryResult<RecipeListItem[]> => {
  return useQuery({
    queryKey: recipeKeys.featured(),
    queryFn: getFeaturedRecipes,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000,
  });
};
