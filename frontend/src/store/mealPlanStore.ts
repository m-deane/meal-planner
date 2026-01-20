/**
 * Zustand store for interactive meal planner state management.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { RecipeListItem, MealType } from '../types';

// ============================================================================
// TYPES
// ============================================================================

export interface MealSlotState {
  recipe: RecipeListItem | null;
  servings: number;
}

export interface DayState {
  breakfast: MealSlotState | null;
  lunch: MealSlotState | null;
  dinner: MealSlotState | null;
}

export type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

export interface MealPlanState {
  days: Record<DayOfWeek, DayState>;
  startDate: string | null; // ISO date string
  nutritionGoals: {
    daily_calories?: number;
    daily_protein_g?: number;
    daily_carbs_g?: number;
    daily_fat_g?: number;
  };
}

export interface NutritionTotals {
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  sodium_mg: number;
}

// ============================================================================
// STORE INTERFACE
// ============================================================================

interface MealPlanStore {
  // State
  plan: MealPlanState;

  // Actions
  addRecipe: (day: DayOfWeek, mealType: MealType, recipe: RecipeListItem, servings?: number) => void;
  removeRecipe: (day: DayOfWeek, mealType: MealType) => void;
  moveRecipe: (
    fromDay: DayOfWeek,
    fromMeal: MealType,
    toDay: DayOfWeek,
    toMeal: MealType
  ) => void;
  swapRecipes: (
    day1: DayOfWeek,
    meal1: MealType,
    day2: DayOfWeek,
    meal2: MealType
  ) => void;
  updateServings: (day: DayOfWeek, mealType: MealType, servings: number) => void;
  clearDay: (day: DayOfWeek) => void;
  clearMeal: (mealType: MealType) => void;
  clearAll: () => void;
  setStartDate: (date: string) => void;
  setNutritionGoals: (goals: MealPlanState['nutritionGoals']) => void;

  // Computed/Selectors
  getDayNutrition: (day: DayOfWeek) => NutritionTotals;
  getWeeklyNutrition: () => NutritionTotals;
  getDailyAverage: () => NutritionTotals;
  getTotalRecipes: () => number;
  getUniqueRecipes: () => number;
}

// ============================================================================
// HELPERS
// ============================================================================

const DAYS_OF_WEEK: DayOfWeek[] = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
];

const createEmptyDay = (): DayState => ({
  breakfast: null,
  lunch: null,
  dinner: null,
});

const createEmptyPlan = (): MealPlanState => ({
  days: {
    monday: createEmptyDay(),
    tuesday: createEmptyDay(),
    wednesday: createEmptyDay(),
    thursday: createEmptyDay(),
    friday: createEmptyDay(),
    saturday: createEmptyDay(),
    sunday: createEmptyDay(),
  },
  startDate: null,
  nutritionGoals: {},
});

const getMealTypeKey = (mealType: MealType): keyof DayState => {
  const mealTypeMap: Record<MealType, keyof DayState> = {
    breakfast: 'breakfast',
    lunch: 'lunch',
    dinner: 'dinner',
    snack: 'dinner', // Map snack to dinner as fallback
  };
  return mealTypeMap[mealType];
};

const calculateNutrition = (slots: Array<MealSlotState | null>): NutritionTotals => {
  const totals: NutritionTotals = {
    calories: 0,
    protein_g: 0,
    carbohydrates_g: 0,
    fat_g: 0,
    fiber_g: 0,
    sugar_g: 0,
    sodium_mg: 0,
  };

  slots.forEach((slot) => {
    if (!slot?.recipe?.nutrition_summary) return;

    const nutrition = slot.recipe.nutrition_summary;
    const servingsMultiplier = slot.servings / (slot.recipe.servings || 1);

    totals.calories += (nutrition.calories ?? 0) * servingsMultiplier;
    totals.protein_g += (nutrition.protein_g ?? 0) * servingsMultiplier;
    totals.carbohydrates_g += (nutrition.carbohydrates_g ?? 0) * servingsMultiplier;
    totals.fat_g += (nutrition.fat_g ?? 0) * servingsMultiplier;
    // Note: nutrition_summary doesn't include fiber, sugar, sodium
    // These remain at 0 since the data is not available in RecipeListItem
  });

  return totals;
};

// ============================================================================
// STORE
// ============================================================================

export const useMealPlanStore = create<MealPlanStore>()(
  persist(
    (set, get) => ({
      // Initial state
      plan: createEmptyPlan(),

      // Actions
      addRecipe: (day, mealType, recipe, servings = recipe.servings) => {
        set((state) => ({
          plan: {
            ...state.plan,
            days: {
              ...state.plan.days,
              [day]: {
                ...state.plan.days[day],
                [getMealTypeKey(mealType)]: {
                  recipe,
                  servings,
                },
              },
            },
          },
        }));
      },

      removeRecipe: (day, mealType) => {
        set((state) => ({
          plan: {
            ...state.plan,
            days: {
              ...state.plan.days,
              [day]: {
                ...state.plan.days[day],
                [getMealTypeKey(mealType)]: null,
              },
            },
          },
        }));
      },

      moveRecipe: (fromDay, fromMeal, toDay, toMeal) => {
        set((state) => {
          const fromSlot = state.plan.days[fromDay][getMealTypeKey(fromMeal)];

          if (!fromSlot) return state;

          return {
            plan: {
              ...state.plan,
              days: {
                ...state.plan.days,
                [fromDay]: {
                  ...state.plan.days[fromDay],
                  [getMealTypeKey(fromMeal)]: null,
                },
                [toDay]: {
                  ...state.plan.days[toDay],
                  [getMealTypeKey(toMeal)]: fromSlot,
                },
              },
            },
          };
        });
      },

      swapRecipes: (day1, meal1, day2, meal2) => {
        set((state) => {
          const slot1 = state.plan.days[day1][getMealTypeKey(meal1)];
          const slot2 = state.plan.days[day2][getMealTypeKey(meal2)];

          return {
            plan: {
              ...state.plan,
              days: {
                ...state.plan.days,
                [day1]: {
                  ...state.plan.days[day1],
                  [getMealTypeKey(meal1)]: slot2,
                },
                [day2]: {
                  ...state.plan.days[day2],
                  [getMealTypeKey(meal2)]: slot1,
                },
              },
            },
          };
        });
      },

      updateServings: (day, mealType, servings) => {
        set((state) => {
          const slot = state.plan.days[day][getMealTypeKey(mealType)];
          if (!slot) return state;

          return {
            plan: {
              ...state.plan,
              days: {
                ...state.plan.days,
                [day]: {
                  ...state.plan.days[day],
                  [getMealTypeKey(mealType)]: {
                    ...slot,
                    servings,
                  },
                },
              },
            },
          };
        });
      },

      clearDay: (day) => {
        set((state) => ({
          plan: {
            ...state.plan,
            days: {
              ...state.plan.days,
              [day]: createEmptyDay(),
            },
          },
        }));
      },

      clearMeal: (mealType) => {
        set((state) => {
          const mealKey = getMealTypeKey(mealType);
          const newDays = { ...state.plan.days };

          DAYS_OF_WEEK.forEach((day) => {
            newDays[day] = {
              ...newDays[day],
              [mealKey]: null,
            };
          });

          return {
            plan: {
              ...state.plan,
              days: newDays,
            },
          };
        });
      },

      clearAll: () => {
        set({ plan: createEmptyPlan() });
      },

      setStartDate: (date) => {
        set((state) => ({
          plan: {
            ...state.plan,
            startDate: date,
          },
        }));
      },

      setNutritionGoals: (goals) => {
        set((state) => ({
          plan: {
            ...state.plan,
            nutritionGoals: goals,
          },
        }));
      },

      // Computed/Selectors
      getDayNutrition: (day) => {
        const state = get();
        const dayData = state.plan.days[day];
        const slots = [dayData.breakfast, dayData.lunch, dayData.dinner];
        return calculateNutrition(slots);
      },

      getWeeklyNutrition: () => {
        const state = get();
        const allSlots: Array<MealSlotState | null> = [];

        DAYS_OF_WEEK.forEach((day) => {
          const dayData = state.plan.days[day];
          allSlots.push(dayData.breakfast, dayData.lunch, dayData.dinner);
        });

        return calculateNutrition(allSlots);
      },

      getDailyAverage: () => {
        const weeklyTotals = get().getWeeklyNutrition();
        const daysWithMeals = DAYS_OF_WEEK.filter((day) => {
          const dayData = get().plan.days[day];
          return dayData.breakfast || dayData.lunch || dayData.dinner;
        }).length;

        const divisor = daysWithMeals || 1;

        return {
          calories: weeklyTotals.calories / divisor,
          protein_g: weeklyTotals.protein_g / divisor,
          carbohydrates_g: weeklyTotals.carbohydrates_g / divisor,
          fat_g: weeklyTotals.fat_g / divisor,
          fiber_g: weeklyTotals.fiber_g / divisor,
          sugar_g: weeklyTotals.sugar_g / divisor,
          sodium_mg: weeklyTotals.sodium_mg / divisor,
        };
      },

      getTotalRecipes: () => {
        const state = get();
        let count = 0;

        DAYS_OF_WEEK.forEach((day) => {
          const dayData = state.plan.days[day];
          if (dayData.breakfast) count++;
          if (dayData.lunch) count++;
          if (dayData.dinner) count++;
        });

        return count;
      },

      getUniqueRecipes: () => {
        const state = get();
        const recipeIds = new Set<number>();

        DAYS_OF_WEEK.forEach((day) => {
          const dayData = state.plan.days[day];
          if (dayData.breakfast?.recipe) recipeIds.add(dayData.breakfast.recipe.id);
          if (dayData.lunch?.recipe) recipeIds.add(dayData.lunch.recipe.id);
          if (dayData.dinner?.recipe) recipeIds.add(dayData.dinner.recipe.id);
        });

        return recipeIds.size;
      },
    }),
    {
      name: 'meal-plan-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
