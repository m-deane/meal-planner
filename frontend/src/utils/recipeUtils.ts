import { DifficultyLevel } from '../types';
import type { BadgeColor } from '../components/common/Badge';

/**
 * Returns the Badge color variant for a given difficulty level.
 * Extracted from RecipeCard so it can be shared with DraggableRecipe.
 */
export const getDifficultyColor = (difficulty: DifficultyLevel | null): BadgeColor => {
  switch (difficulty) {
    case DifficultyLevel.EASY:
      return 'success';
    case DifficultyLevel.MEDIUM:
      return 'warning';
    case DifficultyLevel.HARD:
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Returns a human-readable label for a given difficulty level.
 */
export const getDifficultyLabel = (difficulty: DifficultyLevel | null): string => {
  if (!difficulty) return 'Unknown';
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
};
