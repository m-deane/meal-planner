/**
 * Main shopping list container with grouped items and controls.
 */

import React from 'react';
import { SortAsc, Eye, EyeOff } from 'lucide-react';
import { CategorySection } from './CategorySection';
import { useShoppingListStore } from '../../store/shoppingListStore';

export interface ShoppingListProps {
  className?: string;
}

export const ShoppingList: React.FC<ShoppingListProps> = ({ className = '' }) => {
  const {
    state,
    toggleItem,
    removeItem,
    updateItem,
    setSortBy,
    setShowChecked,
    getItemsByCategory,
    getCheckedCount,
    getTotalCount,
  } = useShoppingListStore();

  const itemsByCategory = getItemsByCategory();
  const checkedCount = getCheckedCount();
  const totalCount = getTotalCount();

  const visibleItems = state.showChecked
    ? state.items
    : state.items.filter((item) => !item.checked);

  const visibleItemsByCategory = React.useMemo(() => {
    const filtered = new Map(itemsByCategory);
    if (!state.showChecked) {
      filtered.forEach((items, category) => {
        const unchecked = items.filter((item) => !item.checked);
        if (unchecked.length === 0) {
          filtered.delete(category);
        } else {
          filtered.set(category, unchecked);
        }
      });
    }
    return filtered;
  }, [itemsByCategory, state.showChecked]);

  if (totalCount === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <span className="text-3xl">🛒</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No items in your shopping list
        </h3>
        <p className="text-gray-600">
          Generate a list from your meal plan or add items manually
        </p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header with stats and controls */}
      <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Shopping List</h2>
            <p className="text-sm text-gray-600 mt-1">
              {checkedCount} of {totalCount} {totalCount === 1 ? 'item' : 'items'} checked
            </p>
          </div>

          {/* Progress indicator */}
          <div className="flex items-center gap-4">
            <div className="w-32">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500 transition-all duration-300"
                  style={{ width: `${totalCount > 0 ? (checkedCount / totalCount) * 100 : 0}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1 text-center">
                {totalCount > 0 ? Math.round((checkedCount / totalCount) * 100) : 0}% Complete
              </p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
          {/* Sort by */}
          <div className="flex items-center gap-2">
            <SortAsc className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Sort:</span>
            <select
              value={state.sortBy}
              onChange={(e) => setSortBy(e.target.value as 'category' | 'alphabetical')}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="category">By Category</option>
              <option value="alphabetical">Alphabetical</option>
            </select>
          </div>

          {/* Show/hide checked */}
          <button
            onClick={() => setShowChecked(!state.showChecked)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {state.showChecked ? (
              <>
                <EyeOff className="w-4 h-4" />
                Hide Checked
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                Show Checked
              </>
            )}
          </button>

          {/* Items count */}
          <div className="ml-auto text-sm text-gray-600">
            Showing {visibleItems.length} of {totalCount} {totalCount === 1 ? 'item' : 'items'}
          </div>
        </div>
      </div>

      {/* Category sections */}
      <div className="space-y-4">
        {Array.from(visibleItemsByCategory.entries()).map(([category, items]) => (
          <CategorySection
            key={category}
            category={category}
            items={items}
            onToggleItem={toggleItem}
            onRemoveItem={removeItem}
            onUpdateItem={updateItem}
          />
        ))}
      </div>

      {/* Empty state when all checked and hidden */}
      {visibleItems.length === 0 && totalCount > 0 && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            All items checked!
          </h3>
          <p className="text-gray-600 mb-4">
            Great job! You've checked everything on your list.
          </p>
          <button
            onClick={() => setShowChecked(true)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Show checked items
          </button>
        </div>
      )}
    </div>
  );
};
