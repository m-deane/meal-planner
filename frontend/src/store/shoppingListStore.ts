/**
 * Zustand store for shopping list state management with local storage persistence.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { ShoppingCategory, IngredientCategory } from '../types';

// ============================================================================
// TYPES
// ============================================================================

/**
 * UI-friendly representation of a shopping list item used by the store and components.
 * This is NOT the same as the backend ShoppingItem type; the store's loadFromResponse
 * transforms backend items into this display format.
 */
export interface ShoppingListItem {
  id: string;
  ingredient_name: string;
  quantity: number | null;
  unit: string | null;
  category: string;
  is_optional: boolean;
  notes: string | null;
  recipe_count: number;
  recipe_names: string[];
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
  loadFromResponse: (categories: ShoppingCategory[]) => void;

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
    return [...items].sort((a, b) =>
      a.ingredient_name.localeCompare(b.ingredient_name)
    );
  }

  // Sort by category, then by name within category
  return [...items].sort((a, b) => {
    if (a.category === b.category) {
      return a.ingredient_name.localeCompare(b.ingredient_name);
    }
    return a.category.localeCompare(b.category);
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

      loadFromResponse: (categories) => {
        const existingItems = get().state.items;
        const existingChecked = new Map(
          existingItems.map((item) => [item.ingredient_name, item.checked])
        );

        // Transform backend ShoppingCategory[] into UI ShoppingListItem[]
        const newItems: ShoppingListItem[] = categories.flatMap((category) =>
          category.items.map((item) => {
            // Extract first quantity entry for display
            let quantity: number | null = null;
            let unit: string | null = null;
            const firstQty = item.quantities[0];
            if (firstQty) {
              quantity = firstQty.total;
              unit = firstQty.unit;
            }

            return {
              id: generateId(),
              ingredient_name: item.name,
              quantity,
              unit,
              category: category.name.toLowerCase().replace(/[^a-z]/g, ''),
              is_optional: false,
              notes: item.preparations.length > 0 ? item.preparations.join(', ') : null,
              recipe_count: item.times_needed,
              recipe_names: [],
              checked: existingChecked.get(item.name) ?? false,
              customAdded: false,
            };
          })
        );

        set((state) => ({
          state: {
            ...state.state,
            items: newItems,
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
          const category = item.category as IngredientCategory;
          const categoryItems = grouped.get(category) ?? [];
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
