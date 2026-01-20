/**
 * Manual item entry form with autocomplete.
 */

import React, { useState } from 'react';
import { Plus, X } from 'lucide-react';
import { useShoppingListStore } from '../../store/shoppingListStore';
import { IngredientCategory } from '../../types';
import { getCategoryDisplayName } from '../../utils/shoppingList';

export interface AddItemFormProps {
  className?: string;
}

const COMMON_UNITS = [
  'g',
  'kg',
  'ml',
  'l',
  'cup',
  'tbsp',
  'tsp',
  'oz',
  'lb',
  'piece',
  'clove',
  'bunch',
  'can',
  'package',
];

export const AddItemForm: React.FC<AddItemFormProps> = ({ className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('');
  const [category, setCategory] = useState<IngredientCategory>(IngredientCategory.OTHER);

  const { addCustomItem } = useShoppingListStore();

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();

    if (!name.trim()) {
      return;
    }

    const parsedQuantity = quantity ? parseFloat(quantity) : null;

    addCustomItem(
      name.trim(),
      parsedQuantity,
      unit.trim() || null,
      category
    );

    // Reset form
    setName('');
    setQuantity('');
    setUnit('');
    setCategory(IngredientCategory.OTHER);
    setIsExpanded(false);
  };

  const handleCancel = (): void => {
    setName('');
    setQuantity('');
    setUnit('');
    setCategory(IngredientCategory.OTHER);
    setIsExpanded(false);
  };

  if (!isExpanded) {
    return (
      <div className={className}>
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-dashed border-gray-300 text-gray-600 font-medium rounded-lg hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
        >
          <Plus className="w-5 h-5" />
          Add Custom Item
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Add Custom Item</h3>
        <button
          onClick={handleCancel}
          className="p-1 text-gray-600 hover:bg-gray-100 rounded transition-colors"
          aria-label="Cancel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Ingredient name */}
        <div>
          <label
            htmlFor="ingredient-name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Ingredient Name *
          </label>
          <input
            id="ingredient-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Tomatoes"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Quantity and unit */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label
              htmlFor="quantity"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Quantity
            </label>
            <input
              id="quantity"
              type="number"
              step="0.1"
              min="0"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="2"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="unit"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Unit
            </label>
            <div className="relative">
              <input
                id="unit"
                type="text"
                list="unit-suggestions"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                placeholder="kg, cup, etc."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <datalist id="unit-suggestions">
                {COMMON_UNITS.map((u) => (
                  <option key={u} value={u} />
                ))}
              </datalist>
            </div>
          </div>
        </div>

        {/* Category */}
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Category
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value as IngredientCategory)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.values(IngredientCategory).map((cat) => (
              <option key={cat} value={cat}>
                {getCategoryDisplayName(cat)}
              </option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Item
          </button>
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
