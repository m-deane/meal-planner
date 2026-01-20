/**
 * Collapsible category section for grouped shopping items.
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, CheckSquare, Square } from 'lucide-react';
import { ShoppingItem } from './ShoppingItem';
import type { ShoppingListItem } from '../../store/shoppingListStore';
import type { IngredientCategory } from '../../types';
import { getCategoryDisplayName, getCategoryIcon } from '../../utils/shoppingList';

export interface CategorySectionProps {
  category: IngredientCategory;
  items: ShoppingListItem[];
  onToggleItem: (id: string) => void;
  onRemoveItem: (id: string) => void;
  onUpdateItem: (
    id: string,
    updates: Partial<Pick<ShoppingListItem, 'quantity' | 'unit' | 'notes'>>
  ) => void;
  defaultExpanded?: boolean;
}

export const CategorySection: React.FC<CategorySectionProps> = ({
  category,
  items,
  onToggleItem,
  onRemoveItem,
  onUpdateItem,
  defaultExpanded = true,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const checkedCount = items.filter((item) => item.checked).length;
  const totalCount = items.length;
  const allChecked = totalCount > 0 && checkedCount === totalCount;
  const someChecked = checkedCount > 0 && !allChecked;

  const handleToggleAll = (): void => {
    const newCheckedState = !allChecked;
    items.forEach((item) => {
      if (item.checked !== newCheckedState) {
        onToggleItem(item.id);
      }
    });
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between p-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-3 flex-1 text-left hover:opacity-70 transition-opacity"
          >
            {isExpanded ? (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-600" />
            )}

            <span className="text-2xl" aria-hidden="true">
              {getCategoryIcon(category)}
            </span>

            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {getCategoryDisplayName(category)}
              </h3>
              <p className="text-sm text-gray-600">
                {checkedCount} of {totalCount} {totalCount === 1 ? 'item' : 'items'}
              </p>
            </div>
          </button>

          {/* Item count badge */}
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-8 h-8 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-full">
              {totalCount}
            </span>

            {/* Toggle all button */}
            <button
              onClick={handleToggleAll}
              className="p-2 text-gray-600 hover:bg-white rounded-lg transition-colors"
              aria-label={allChecked ? 'Uncheck all items' : 'Check all items'}
              title={allChecked ? 'Uncheck all' : 'Check all'}
            >
              {allChecked ? (
                <CheckSquare className="w-5 h-5 text-blue-600" />
              ) : someChecked ? (
                <CheckSquare className="w-5 h-5 text-blue-400" />
              ) : (
                <Square className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Progress bar */}
        {totalCount > 0 && (
          <div className="h-1 bg-gray-200">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${(checkedCount / totalCount) * 100}%` }}
            />
          </div>
        )}
      </div>

      {/* Items list */}
      {isExpanded && (
        <div className="p-3 space-y-1">
          {items.length === 0 ? (
            <p className="text-center text-gray-500 py-4">No items in this category</p>
          ) : (
            items.map((item) => (
              <ShoppingItem
                key={item.id}
                item={item}
                onToggle={onToggleItem}
                onRemove={onRemoveItem}
                onUpdate={onUpdateItem}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
};
