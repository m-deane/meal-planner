/**
 * Shopping list page with generation, viewing, and export functionality.
 */

import React from 'react';
import { Trash2 } from 'lucide-react';
import {
  ShoppingList,
  ShoppingListGenerator,
  ExportOptions,
  AddItemForm,
} from '../components/shopping-list';
import { useShoppingListStore } from '../store/shoppingListStore';

export const ShoppingListPage: React.FC = () => {
  const { clearAll, clearChecked, getTotalCount, getCheckedCount } =
    useShoppingListStore();

  const totalCount = getTotalCount();
  const checkedCount = getCheckedCount();
  const hasItems = totalCount > 0;
  const hasCheckedItems = checkedCount > 0;

  const handleClearAll = (): void => {
    if (window.confirm('Are you sure you want to clear all items?')) {
      clearAll();
    }
  };

  const handleClearChecked = (): void => {
    if (window.confirm('Remove all checked items from the list?')) {
      clearChecked();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Shopping List</h1>
              <p className="mt-1 text-gray-600">
                Generate from your meal plan or add items manually
              </p>
            </div>

            {/* Clear buttons */}
            {hasItems && (
              <div className="flex items-center gap-2">
                {hasCheckedItems && (
                  <button
                    onClick={handleClearChecked}
                    className="flex items-center gap-2 px-4 py-2 text-orange-600 border border-orange-300 rounded-lg hover:bg-orange-50 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear Checked
                  </button>
                )}
                <button
                  onClick={handleClearAll}
                  className="flex items-center gap-2 px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left column: Generator and add form */}
          <div className="lg:col-span-1 space-y-6">
            {/* Generator */}
            <ShoppingListGenerator />

            {/* Add item form */}
            <AddItemForm />

            {/* Export options */}
            {hasItems && <ExportOptions />}
          </div>

          {/* Right column: Shopping list */}
          <div className="lg:col-span-2">
            <ShoppingList />
          </div>
        </div>
      </main>

      {/* Print styles */}
      <style>{`
        @media print {
          header,
          .lg\\:col-span-1 {
            display: none !important;
          }

          .lg\\:col-span-2 {
            grid-column: span 3 / span 3;
          }

          body {
            background: white;
          }

          .min-h-screen {
            min-height: auto;
          }
        }
      `}</style>
    </div>
  );
};

export default ShoppingListPage;
