/**
 * Zustand store for shopping list state management with local storage persistence.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ShoppingItem, IngredientCategory } from '../types';

// ============================================================================
// TYPES
// ============================================================================

export interface ShoppingListItem extends ShoppingItem {
  id: string;
  checked: boolean;
  customAdded: boolean;
}

export interface ShoppingListState {
  items: ShoppingListItem[];
  sortBy: 'category' | 'alphabetical';
  showChecked: boolean;
}

export interface ShoppingListStore {
  // State
  state: ShoppingListState;

  // Actions
  addItem: (item: Omit<ShoppingListItem, 'id' | 'checked' | 'customAdded'>) => void;
  addCustomItem: (
    name: string,
    quantity: number | null,
    unit: string | null,
    category: IngredientCategory
  ) => void;
  removeItem: (id: string) => void;
  toggleItem: (id: string) => void;
  toggleAll: (checked: boolean) => void;
  clearChecked: () => void;
  clearAll: () => void;
  updateItem: (
    id: string,
    updates: Partial<Pick<ShoppingListItem, 'quantity' | 'unit' | 'notes'>>
  ) => void;
  setSortBy: (sortBy: 'category' | 'alphabetical') => void;
  setShowChecked: (show: boolean) => void;
  loadFromResponse: (items: ShoppingItem[]) => void;

  // Computed
  getCheckedCount: () => number;
  getTotalCount: () => number;
  getItemsByCategory: () => Map<IngredientCategory, ShoppingListItem[]>;
  getUncheckedItems: () => ShoppingListItem[];
}

// ============================================================================
// HELPERS
// ============================================================================

const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
};

const sortItems = (
  items: ShoppingListItem[],
  sortBy: 'category' | 'alphabetical'
): ShoppingListItem[] => {
  if (sortBy === 'alphabetical') {
    return [...items].sort((a, b) => {
      const nameA = a.ingredient_name ?? '';
      const nameB = b.ingredient_name ?? '';
      return nameA.localeCompare(nameB);
    });
  }

  // Sort by category
  return [...items].sort((a, b) => {
    const catA = a.category ?? 'other';
    const catB = b.category ?? 'other';
    const nameA = a.ingredient_name ?? '';
    const nameB = b.ingredient_name ?? '';

    if (catA === catB) {
      return nameA.localeCompare(nameB);
    }
    return catA.localeCompare(catB);
  });
};

// ============================================================================
// STORE
// ============================================================================

export const useShoppingListStore = create<ShoppingListStore>()(
  persist(
    (set, get) => ({
      // Initial state
      state: {
        items: [],
        sortBy: 'category',
        showChecked: true,
      },

      // Actions
      addItem: (item) => {
        set((state) => ({
          state: {
            ...state.state,
            items: [
              ...state.state.items,
              {
                ...item,
                id: generateId(),
                checked: false,
                customAdded: false,
              },
            ],
          },
        }));
      },

      addCustomItem: (name, quantity, unit, category) => {
        set((state) => ({
          state: {
            ...state.state,
            items: [
              ...state.state.items,
              {
                id: generateId(),
                ingredient_name: name,
                quantity,
                unit,
                category,
                is_optional: false,
                notes: null,
                recipe_count: 0,
                recipe_names: [],
                checked: false,
                customAdded: true,
              },
            ],
          },
        }));
      },

      removeItem: (id) => {
        set((state) => ({
          state: {
            ...state.state,
            items: state.state.items.filter((item) => item.id !== id),
          },
        }));
      },

      toggleItem: (id) => {
        set((state) => ({
          state: {
            ...state.state,
            items: state.state.items.map((item) =>
              item.id === id ? { ...item, checked: !item.checked } : item
            ),
          },
        }));
      },

      toggleAll: (checked) => {
        set((state) => ({
          state: {
            ...state.state,
            items: state.state.items.map((item) => ({ ...item, checked })),
          },
        }));
      },

      clearChecked: () => {
        set((state) => ({
          state: {
            ...state.state,
            items: state.state.items.filter((item) => !item.checked),
          },
        }));
      },

      clearAll: () => {
        set((state) => ({
          state: {
            ...state.state,
            items: [],
          },
        }));
      },

      updateItem: (id, updates) => {
        set((state) => ({
          state: {
            ...state.state,
            items: state.state.items.map((item) =>
              item.id === id ? { ...item, ...updates } : item
            ),
          },
        }));
      },

      setSortBy: (sortBy) => {
        set((state) => ({
          state: {
            ...state.state,
            sortBy,
          },
        }));
      },

      setShowChecked: (show) => {
        set((state) => ({
          state: {
            ...state.state,
            showChecked: show,
          },
        }));
      },

      loadFromResponse: (items) => {
        const existingItems = get().state.items;
        const existingChecked = new Map(
          existingItems.map((item) => [item.ingredient_name, item.checked])
        );

        set((state) => ({
          state: {
            ...state.state,
            items: items.map((item) => ({
              ...item,
              id: generateId(),
              checked: existingChecked.get(item.ingredient_name) ?? false,
              customAdded: false,
            })),
          },
        }));
      },

      // Computed
      getCheckedCount: () => {
        return get().state.items.filter((item) => item.checked).length;
      },

      getTotalCount: () => {
        return get().state.items.length;
      },

      getItemsByCategory: () => {
        const { items, sortBy } = get().state;
        const sorted = sortItems(items, sortBy);
        const grouped = new Map<IngredientCategory, ShoppingListItem[]>();

        sorted.forEach((item) => {
          const category = (item.category ?? 'other') as IngredientCategory;
          const categoryItems = grouped.get(category) || [];
          categoryItems.push(item);
          grouped.set(category, categoryItems);
        });

        return grouped;
      },

      getUncheckedItems: () => {
        return get().state.items.filter((item) => !item.checked);
      },
    }),
    {
      name: 'shopping-list-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        state: {
          items: state.state.items,
          sortBy: state.state.sortBy,
          showChecked: state.state.showChecked,
        },
      }),
    }
  )
);
