/**
 * Zustand store for shortlist state management with local storage persistence.
 * Allows users to save recipes for later use in meal planning.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { RecipeListItem } from '../types';

// ============================================================================
// TYPES
// ============================================================================

export interface ShortlistState {
  recipes: RecipeListItem[];
}

export interface ShortlistStore {
  // State
  state: ShortlistState;

  // Actions
  addRecipe: (recipe: RecipeListItem) => void;
  removeRecipe: (recipeId: number) => void;
  toggleRecipe: (recipe: RecipeListItem) => void;
  clearAll: () => void;
  isInShortlist: (recipeId: number) => boolean;

  // Computed
  getCount: () => number;
  getRecipeIds: () => number[];
}

// ============================================================================
// STORE
// ============================================================================

export const useShortlistStore = create<ShortlistStore>()(
  persist(
    (set, get) => ({
      // Initial state
      state: {
        recipes: [],
      },

      // Actions
      addRecipe: (recipe) => {
        const currentRecipes = get().state.recipes;
        // Don't add duplicates
        if (currentRecipes.some((r) => r.id === recipe.id)) {
          return;
        }
        set((state) => ({
          state: {
            ...state.state,
            recipes: [...state.state.recipes, recipe],
          },
        }));
      },

      removeRecipe: (recipeId) => {
        set((state) => ({
          state: {
            ...state.state,
            recipes: state.state.recipes.filter((r) => r.id !== recipeId),
          },
        }));
      },

      toggleRecipe: (recipe) => {
        const currentRecipes = get().state.recipes;
        const isInList = currentRecipes.some((r) => r.id === recipe.id);

        if (isInList) {
          set((state) => ({
            state: {
              ...state.state,
              recipes: state.state.recipes.filter((r) => r.id !== recipe.id),
            },
          }));
        } else {
          set((state) => ({
            state: {
              ...state.state,
              recipes: [...state.state.recipes, recipe],
            },
          }));
        }
      },

      clearAll: () => {
        set(() => ({
          state: {
            recipes: [],
          },
        }));
      },

      isInShortlist: (recipeId) => {
        return get().state.recipes.some((r) => r.id === recipeId);
      },

      // Computed
      getCount: () => {
        return get().state.recipes.length;
      },

      getRecipeIds: () => {
        return get().state.recipes.map((r) => r.id);
      },
    }),
    {
      name: 'shortlist-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        state: {
          recipes: state.state.recipes,
        },
      }),
    }
  )
);
