/**
 * React Query hooks for categories, dietary tags, and allergens.
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import {
  getCategories,
  getDietaryTags,
  getAllergens,
  getCategoryBySlug,
  getDietaryTagBySlug,
} from '../api/categories';
import type { Category, DietaryTag, Allergen } from '../types';

/**
 * Query keys for categories and tags.
 */
export const categoryKeys = {
  all: ['categories'] as const,
  lists: () => [...categoryKeys.all, 'list'] as const,
  list: () => [...categoryKeys.lists()] as const,
  details: () => [...categoryKeys.all, 'detail'] as const,
  detail: (slug: string) => [...categoryKeys.details(), slug] as const,
};

export const dietaryTagKeys = {
  all: ['dietaryTags'] as const,
  lists: () => [...dietaryTagKeys.all, 'list'] as const,
  list: () => [...dietaryTagKeys.lists()] as const,
  details: () => [...dietaryTagKeys.all, 'detail'] as const,
  detail: (slug: string) => [...dietaryTagKeys.details(), slug] as const,
};

export const allergenKeys = {
  all: ['allergens'] as const,
  lists: () => [...allergenKeys.all, 'list'] as const,
  list: () => [...allergenKeys.lists()] as const,
};

/**
 * Fetch all recipe categories.
 */
export const useCategories = (): UseQueryResult<Category[]> => {
  return useQuery({
    queryKey: categoryKeys.list(),
    queryFn: getCategories,
    staleTime: 30 * 60 * 1000, // 30 minutes (categories don't change often)
    gcTime: 60 * 60 * 1000, // 1 hour
  });
};

/**
 * Fetch all dietary tags.
 */
export const useDietaryTags = (): UseQueryResult<DietaryTag[]> => {
  return useQuery({
    queryKey: dietaryTagKeys.list(),
    queryFn: getDietaryTags,
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};

/**
 * Fetch all allergens.
 */
export const useAllergens = (): UseQueryResult<Allergen[]> => {
  return useQuery({
    queryKey: allergenKeys.list(),
    queryFn: getAllergens,
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};

/**
 * Fetch category by slug.
 */
export const useCategoryBySlug = (slug: string): UseQueryResult<Category> => {
  return useQuery({
    queryKey: categoryKeys.detail(slug),
    queryFn: () => getCategoryBySlug(slug),
    enabled: !!slug,
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};

/**
 * Fetch dietary tag by slug.
 */
export const useDietaryTagBySlug = (slug: string): UseQueryResult<DietaryTag> => {
  return useQuery({
    queryKey: dietaryTagKeys.detail(slug),
    queryFn: () => getDietaryTagBySlug(slug),
    enabled: !!slug,
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
};
