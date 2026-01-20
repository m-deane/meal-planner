/**
 * Zustand store for nutrition goals with localStorage persistence.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ============================================================================
// TYPES
// ============================================================================

export interface NutritionGoals {
  daily_calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

interface NutritionGoalsStore {
  goals: NutritionGoals;
  setGoals: (goals: Partial<NutritionGoals>) => void;
  resetToDefaults: () => void;
}

// ============================================================================
// DEFAULTS
// ============================================================================

const DEFAULT_GOALS: NutritionGoals = {
  daily_calories: 2000,
  protein_g: 150,
  carbs_g: 225,
  fat_g: 67,
  fiber_g: 28,
};

// ============================================================================
// STORE
// ============================================================================

export const useNutritionGoalsStore = create<NutritionGoalsStore>()(
  persist(
    (set) => ({
      goals: DEFAULT_GOALS,

      setGoals: (newGoals) => {
        set((state) => ({
          goals: {
            ...state.goals,
            ...newGoals,
          },
        }));
      },

      resetToDefaults: () => {
        set({ goals: DEFAULT_GOALS });
      },
    }),
    {
      name: 'nutrition-goals-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
