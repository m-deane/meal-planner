import { describe, it, expect } from 'vitest';
import { mapBackendCategoryName } from '../shoppingList';
import { IngredientCategory } from '../../types';

describe('mapBackendCategoryName', () => {
  it('maps multi-word backend categories without losing them to "other"', () => {
    expect(mapBackendCategoryName('Grains & Pasta')).toBe(IngredientCategory.GRAINS);
    expect(mapBackendCategoryName('Herbs & Spices')).toBe(IngredientCategory.SPICES);
    expect(mapBackendCategoryName('Sauces & Condiments')).toBe(IngredientCategory.CONDIMENTS);
    expect(mapBackendCategoryName('Nuts & Seeds')).toBe(IngredientCategory.PANTRY);
  });

  it('maps the plural "Proteins" to the protein enum', () => {
    expect(mapBackendCategoryName('Proteins')).toBe(IngredientCategory.PROTEIN);
  });

  it('maps simple categories', () => {
    expect(mapBackendCategoryName('Dairy')).toBe(IngredientCategory.DAIRY);
    expect(mapBackendCategoryName('Vegetables')).toBe(IngredientCategory.VEGETABLES);
  });

  it('is case and whitespace insensitive', () => {
    expect(mapBackendCategoryName('  vegetables  ')).toBe(IngredientCategory.VEGETABLES);
  });

  it('falls back to OTHER for unknown categories', () => {
    expect(mapBackendCategoryName('Unrecognised Thing')).toBe(IngredientCategory.OTHER);
  });
});
