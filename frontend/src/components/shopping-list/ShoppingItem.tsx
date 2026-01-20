/**
 * Individual shopping list item component with checkbox and actions.
 */

import React, { useState } from 'react';
import { Trash2, Edit2, X, Check } from 'lucide-react';
import type { ShoppingListItem } from '../../store/shoppingListStore';
import { formatQuantity } from '../../utils/shoppingList';

export interface ShoppingItemProps {
  item: ShoppingListItem;
  onToggle: (id: string) => void;
  onRemove: (id: string) => void;
  onUpdate: (
    id: string,
    updates: Partial<Pick<ShoppingListItem, 'quantity' | 'unit' | 'notes'>>
  ) => void;
}

export const ShoppingItem: React.FC<ShoppingItemProps> = ({
  item,
  onToggle,
  onRemove,
  onUpdate,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editQuantity, setEditQuantity] = useState(item.quantity?.toString() || '');
  const [editUnit, setEditUnit] = useState(item.unit || '');

  const handleSaveEdit = (): void => {
    const quantity = editQuantity ? parseFloat(editQuantity) : null;
    onUpdate(item.id, {
      quantity,
      unit: editUnit || null,
    });
    setIsEditing(false);
  };

  const handleCancelEdit = (): void => {
    setEditQuantity(item.quantity?.toString() || '');
    setEditUnit(item.unit || '');
    setIsEditing(false);
  };

  return (
    <div
      className={`flex items-center gap-3 py-2 px-3 rounded-lg transition-all ${
        item.checked
          ? 'bg-gray-50 opacity-60'
          : 'bg-white hover:bg-gray-50'
      }`}
    >
      {/* Checkbox */}
      <input
        type="checkbox"
        checked={item.checked}
        onChange={() => onToggle(item.id)}
        className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
        aria-label={`Mark ${item.ingredient_name} as ${item.checked ? 'unchecked' : 'checked'}`}
      />

      {/* Content */}
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <span
              className={`font-medium ${
                item.checked ? 'line-through text-gray-500' : 'text-gray-900'
              }`}
            >
              {item.ingredient_name}
            </span>
            <span className="text-gray-400">-</span>
            <input
              type="number"
              step="0.1"
              value={editQuantity}
              onChange={(e) => setEditQuantity(e.target.value)}
              className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Qty"
            />
            <input
              type="text"
              value={editUnit}
              onChange={(e) => setEditUnit(e.target.value)}
              className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Unit"
            />
          </div>
        ) : (
          <div className="flex items-baseline gap-2">
            <span
              className={`font-medium ${
                item.checked ? 'line-through text-gray-500' : 'text-gray-900'
              } ${item.is_optional ? 'italic' : ''}`}
            >
              {item.ingredient_name}
            </span>
            {(item.quantity !== null || item.unit) && (
              <>
                <span className="text-gray-400">-</span>
                <span
                  className={`text-sm ${
                    item.checked ? 'line-through text-gray-400' : 'text-gray-600'
                  }`}
                >
                  {formatQuantity(item.quantity, item.unit)}
                </span>
              </>
            )}
          </div>
        )}

        {/* Recipe names */}
        {item.recipe_names.length > 0 && (
          <div className="mt-1 text-xs text-gray-500">
            Used in: {item.recipe_names.join(', ')}
          </div>
        )}

        {/* Notes */}
        {item.notes && (
          <div className="mt-1 text-xs text-gray-500 italic">
            Note: {item.notes}
          </div>
        )}

        {/* Optional badge */}
        {item.is_optional && (
          <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium text-gray-600 bg-gray-100 rounded">
            Optional
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        {isEditing ? (
          <>
            <button
              onClick={handleSaveEdit}
              className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
              aria-label="Save changes"
            >
              <Check className="w-4 h-4" />
            </button>
            <button
              onClick={handleCancelEdit}
              className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              aria-label="Cancel editing"
            >
              <X className="w-4 h-4" />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setIsEditing(true)}
              className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
              aria-label="Edit quantity"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => onRemove(item.id)}
              className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
              aria-label="Remove item"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}
      </div>
    </div>
  );
};
