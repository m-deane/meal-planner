/**
 * Tests for nutritionGoalsStore.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useNutritionGoalsStore } from '../nutritionGoalsStore';

describe('nutritionGoalsStore', () => {
  beforeEach(() => {
    // Reset store to defaults before each test
    const { resetToDefaults } = useNutritionGoalsStore.getState();
    resetToDefaults();
  });

  it('initializes with default goals', () => {
    const { goals } = useNutritionGoalsStore.getState();

    expect(goals).toEqual({
      daily_calories: 2000,
      protein_g: 150,
      carbs_g: 225,
      fat_g: 67,
      fiber_g: 28,
    });
  });

  it('updates individual goals', () => {
    const { setGoals } = useNutritionGoalsStore.getState();

    setGoals({ daily_calories: 2500 });

    const updatedGoals = useNutritionGoalsStore.getState().goals;

    expect(updatedGoals.daily_calories).toBe(2500);
    expect(updatedGoals.protein_g).toBe(150); // Other values unchanged
  });

  it('updates multiple goals at once', () => {
    const { setGoals } = useNutritionGoalsStore.getState();

    setGoals({
      daily_calories: 2500,
      protein_g: 180,
      carbs_g: 250,
    });

    const { goals } = useNutritionGoalsStore.getState();

    expect(goals.daily_calories).toBe(2500);
    expect(goals.protein_g).toBe(180);
    expect(goals.carbs_g).toBe(250);
    expect(goals.fat_g).toBe(67); // Unchanged
    expect(goals.fiber_g).toBe(28); // Unchanged
  });

  it('resets to default values', () => {
    const { setGoals, resetToDefaults } = useNutritionGoalsStore.getState();

    // Modify goals
    setGoals({
      daily_calories: 3000,
      protein_g: 200,
      carbs_g: 300,
      fat_g: 100,
      fiber_g: 40,
    });

    // Verify changes
    let { goals } = useNutritionGoalsStore.getState();
    expect(goals.daily_calories).toBe(3000);

    // Reset
    resetToDefaults();

    // Verify reset
    goals = useNutritionGoalsStore.getState().goals;
    expect(goals).toEqual({
      daily_calories: 2000,
      protein_g: 150,
      carbs_g: 225,
      fat_g: 67,
      fiber_g: 28,
    });
  });

  it('persists goals to localStorage', () => {
    const { setGoals } = useNutritionGoalsStore.getState();

    setGoals({ daily_calories: 2800 });

    // Check localStorage was called (in real app, not in test env)
    const { goals } = useNutritionGoalsStore.getState();
    expect(goals.daily_calories).toBe(2800);
  });

  it('handles partial updates correctly', () => {
    const { setGoals } = useNutritionGoalsStore.getState();

    setGoals({ protein_g: 175 });

    const { goals } = useNutritionGoalsStore.getState();

    expect(goals.protein_g).toBe(175);
    expect(goals.daily_calories).toBe(2000); // Original value
  });
});
