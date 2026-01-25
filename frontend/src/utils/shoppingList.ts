/**
 * Utility functions for shopping list formatting and manipulation.
 */

import type { ShoppingListItem } from '../store/shoppingListStore';
import type { IngredientCategory } from '../types';

// ============================================================================
// CATEGORY DISPLAY
// ============================================================================

export const getCategoryDisplayName = (category: IngredientCategory): string => {
  const displayNames: Record<IngredientCategory, string> = {
    protein: 'Protein',
    dairy: 'Dairy & Eggs',
    vegetables: 'Vegetables',
    fruits: 'Fruits',
    grains: 'Grains & Bread',
    pantry: 'Pantry Staples',
    spices: 'Spices & Seasonings',
    condiments: 'Condiments & Sauces',
    beverages: 'Beverages',
    frozen: 'Frozen',
    bakery: 'Bakery',
    other: 'Other',
  };
  return displayNames[category] || category;
};

export const getCategoryIcon = (category: IngredientCategory): string => {
  const icons: Record<IngredientCategory, string> = {
    protein: '🥩',
    dairy: '🥛',
    vegetables: '🥬',
    fruits: '🍎',
    grains: '🌾',
    pantry: '🏺',
    spices: '🧂',
    condiments: '🍯',
    beverages: '☕',
    frozen: '❄️',
    bakery: '🥖',
    other: '📦',
  };
  return icons[category] || '📦';
};

// ============================================================================
// FORMATTING
// ============================================================================

export const formatQuantity = (
  quantity: number | null | undefined,
  unit: string | null | undefined
): string => {
  if (quantity == null) {
    return unit || '';
  }

  const formattedQuantity = quantity % 1 === 0 ? quantity.toString() : quantity.toFixed(2);

  if (!unit) {
    return formattedQuantity;
  }

  return `${formattedQuantity} ${unit}`;
};

export const formatItemForDisplay = (item: ShoppingListItem): string => {
  const quantity = formatQuantity(item.quantity, item.unit);
  const name = item.ingredient_name ?? 'Unknown Item';

  if (quantity) {
    return `${name} - ${quantity}`;
  }

  return name;
};

// ============================================================================
// EXPORT FORMATTING
// ============================================================================

export const formatForClipboard = (items: ShoppingListItem[]): string => {
  const grouped = groupItemsByCategory(items);
  const lines: string[] = ['SHOPPING LIST', ''];

  grouped.forEach((categoryItems, category) => {
    lines.push(getCategoryDisplayName(category).toUpperCase());
    lines.push('─'.repeat(40));

    categoryItems.forEach((item) => {
      const checkbox = item.checked ? '[✓]' : '[ ]';
      const quantity = formatQuantity(item.quantity, item.unit);
      const line = quantity
        ? `${checkbox} ${item.ingredient_name} - ${quantity}`
        : `${checkbox} ${item.ingredient_name}`;

      lines.push(line);
    });

    lines.push('');
  });

  const stats = [
    'SUMMARY',
    '─'.repeat(40),
    `Total items: ${items.length}`,
    `Checked: ${items.filter((i) => i.checked).length}`,
    `Remaining: ${items.filter((i) => !i.checked).length}`,
  ];

  lines.push(...stats);

  return lines.join('\n');
};

export const formatForPrint = (items: ShoppingListItem[]): string => {
  const grouped = groupItemsByCategory(items);
  const html: string[] = [
    '<!DOCTYPE html>',
    '<html>',
    '<head>',
    '<meta charset="utf-8">',
    '<title>Shopping List</title>',
    '<style>',
    '  body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }',
    '  h1 { text-align: center; color: #333; }',
    '  h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 8px; margin-top: 24px; }',
    '  .item { display: flex; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }',
    '  .checkbox { width: 20px; height: 20px; border: 2px solid #999; margin-right: 12px; }',
    '  .name { flex: 1; }',
    '  .quantity { color: #666; margin-left: 12px; }',
    '  .summary { margin-top: 40px; padding: 16px; background: #f5f5f5; border-radius: 8px; }',
    '  .optional { opacity: 0.6; font-style: italic; }',
    '  @media print { body { margin: 0; } }',
    '</style>',
    '</head>',
    '<body>',
    '<h1>Shopping List</h1>',
  ];

  grouped.forEach((categoryItems, category) => {
    html.push(`<h2>${getCategoryIcon(category)} ${getCategoryDisplayName(category)}</h2>`);

    categoryItems.forEach((item) => {
      const quantity = formatQuantity(item.quantity, item.unit);
      const optionalClass = item.is_optional ? ' optional' : '';

      html.push('<div class="item">');
      html.push('  <div class="checkbox"></div>');
      html.push(`  <div class="name${optionalClass}">${item.ingredient_name}</div>`);
      if (quantity) {
        html.push(`  <div class="quantity">${quantity}</div>`);
      }
      html.push('</div>');
    });
  });

  const totalItems = items.length;
  const checkedItems = items.filter((i) => i.checked).length;

  html.push('<div class="summary">');
  html.push(`<strong>Total items:</strong> ${totalItems}<br>`);
  html.push(`<strong>Checked:</strong> ${checkedItems}<br>`);
  html.push(`<strong>Remaining:</strong> ${totalItems - checkedItems}`);
  html.push('</div>');

  html.push('</body>');
  html.push('</html>');

  return html.join('\n');
};

// ============================================================================
// AGGREGATION
// ============================================================================

export const aggregateItems = (items: ShoppingListItem[]): ShoppingListItem[] => {
  const aggregated = new Map<string, ShoppingListItem>();

  items.forEach((item) => {
    const ingredientName = item.ingredient_name ?? 'unknown';
    const key = `${ingredientName.toLowerCase()}-${item.unit || 'none'}`;
    const existing = aggregated.get(key);

    if (existing) {
      // Combine quantities
      const newQuantity =
        existing.quantity !== null && item.quantity !== null
          ? existing.quantity + item.quantity
          : existing.quantity ?? item.quantity;

      // Merge recipe names
      const recipeNames = Array.from(
        new Set([...existing.recipe_names, ...item.recipe_names])
      );

      aggregated.set(key, {
        ...existing,
        quantity: newQuantity,
        recipe_count: existing.recipe_count + item.recipe_count,
        recipe_names: recipeNames,
        is_optional: existing.is_optional && item.is_optional,
      });
    } else {
      aggregated.set(key, { ...item });
    }
  });

  return Array.from(aggregated.values());
};

// ============================================================================
// SORTING
// ============================================================================

export const sortByCategory = (items: ShoppingListItem[]): ShoppingListItem[] => {
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

export const sortAlphabetically = (items: ShoppingListItem[]): ShoppingListItem[] => {
  return [...items].sort((a, b) => {
    const nameA = a.ingredient_name ?? '';
    const nameB = b.ingredient_name ?? '';
    return nameA.localeCompare(nameB);
  });
};

export const groupItemsByCategory = (
  items: ShoppingListItem[]
): Map<IngredientCategory, ShoppingListItem[]> => {
  const grouped = new Map<IngredientCategory, ShoppingListItem[]>();

  items.forEach((item) => {
    const category = (item.category ?? 'other') as IngredientCategory;
    const categoryItems = grouped.get(category) || [];
    categoryItems.push(item);
    grouped.set(category, categoryItems);
  });

  return grouped;
};

// ============================================================================
// SHARING
// ============================================================================

export const canShare = (): boolean => {
  return typeof navigator !== 'undefined' && 'share' in navigator;
};

export const shareList = async (items: ShoppingListItem[]): Promise<void> => {
  if (!canShare()) {
    throw new Error('Web Share API is not supported');
  }

  const text = formatForClipboard(items);

  await navigator.share({
    title: 'Shopping List',
    text,
  });
};

export const copyToClipboard = async (text: string): Promise<void> => {
  if (typeof navigator === 'undefined' || !navigator.clipboard) {
    throw new Error('Clipboard API is not supported');
  }

  await navigator.clipboard.writeText(text);
};

// ============================================================================
// PRINT
// ============================================================================

export const printList = (items: ShoppingListItem[]): void => {
  const html = formatForPrint(items);
  const printWindow = window.open('', '_blank');

  if (!printWindow) {
    throw new Error('Failed to open print window');
  }

  printWindow.document.write(html);
  printWindow.document.close();
  printWindow.focus();

  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};
