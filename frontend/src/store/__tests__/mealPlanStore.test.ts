/**
 * Tests for meal plan store.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useMealPlanStore, type DayOfWeek } from '../mealPlanStore';
import type { RecipeListItem, MealType } from '../../types';
import { DifficultyLevel } from '../../types';

// ============================================================================
// TEST DATA
// ============================================================================

const mockRecipe1: RecipeListItem = {
  id: 1,
  name: 'Chicken Pasta',
  slug: 'chicken-pasta',
  description: 'Delicious pasta',
  cooking_time_minutes: 30,
  prep_time_minutes: 10,
  total_time_minutes: 40,
  difficulty: DifficultyLevel.EASY,
  servings: 4,
  categories: [],
  dietary_tags: [],
  allergens: [],
  main_image: null,
  nutrition_summary: {
    calories: 600,
    protein_g: 30,
    carbohydrates_g: 50,
    fat_g: 20,
  },
  is_active: true,
};

const mockRecipe2: RecipeListItem = {
  id: 2,
  name: 'Salmon Salad',
  slug: 'salmon-salad',
  description: 'Fresh salad',
  cooking_time_minutes: 15,
  prep_time_minutes: 10,
  total_time_minutes: 25,
  difficulty: DifficultyLevel.EASY,
  servings: 2,
  categories: [],
  dietary_tags: [],
  allergens: [],
  main_image: null,
  nutrition_summary: {
    calories: 400,
    protein_g: 35,
    carbohydrates_g: 20,
    fat_g: 25,
  },
  is_active: true,
};

// ============================================================================
// TESTS
// ============================================================================

describe('mealPlanStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    useMealPlanStore.getState().clearAll();
  });

  describe('addRecipe', () => {
    it('should add a recipe to a meal slot', () => {
      const { addRecipe } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);

      const { plan } = useMealPlanStore.getState();
      const mondayBreakfast = plan.days.monday.breakfast;
      expect(mondayBreakfast).toBeDefined();
      expect(mondayBreakfast?.recipe?.id).toBe(1);
      expect(mondayBreakfast?.servings).toBe(4);
    });

    it('should add recipe with custom servings', () => {
      const { addRecipe } = useMealPlanStore.getState();

      addRecipe('tuesday', 'lunch' as MealType, mockRecipe1, 2);

      const { plan } = useMealPlanStore.getState();
      const tuesdayLunch = plan.days.tuesday.lunch;
      expect(tuesdayLunch?.servings).toBe(2);
    });

    it('should replace existing recipe in slot', () => {
      const { addRecipe } = useMealPlanStore.getState();

      addRecipe('wednesday', 'dinner' as MealType, mockRecipe1);
      addRecipe('wednesday', 'dinner' as MealType, mockRecipe2);

      const { plan } = useMealPlanStore.getState();
      const wednesdayDinner = plan.days.wednesday.dinner;
      expect(wednesdayDinner?.recipe?.id).toBe(2);
    });
  });

  describe('removeRecipe', () => {
    it('should remove a recipe from a meal slot', () => {
      const { addRecipe, removeRecipe } = useMealPlanStore.getState();

      addRecipe('thursday', 'breakfast' as MealType, mockRecipe1);
      removeRecipe('thursday', 'breakfast' as MealType);

      const { plan } = useMealPlanStore.getState();
      const thursdayBreakfast = plan.days.thursday.breakfast;
      expect(thursdayBreakfast).toBeNull();
    });

    it('should do nothing if slot is already empty', () => {
      const { removeRecipe } = useMealPlanStore.getState();

      removeRecipe('friday', 'lunch' as MealType);

      const { plan } = useMealPlanStore.getState();
      const fridayLunch = plan.days.friday.lunch;
      expect(fridayLunch).toBeNull();
    });
  });

  describe('moveRecipe', () => {
    it('should move a recipe from one slot to another', () => {
      const { addRecipe, moveRecipe } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      moveRecipe('monday', 'breakfast' as MealType, 'tuesday', 'lunch' as MealType);

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
      expect(plan.days.tuesday.lunch?.recipe?.id).toBe(1);
    });

    it('should not move if source slot is empty', () => {
      const { moveRecipe } = useMealPlanStore.getState();

      moveRecipe('monday', 'breakfast' as MealType, 'tuesday', 'lunch' as MealType);

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
      expect(plan.days.tuesday.lunch).toBeNull();
    });
  });

  describe('swapRecipes', () => {
    it('should swap two recipes between slots', () => {
      const { addRecipe, swapRecipes } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('tuesday', 'lunch' as MealType, mockRecipe2);

      swapRecipes(
        'monday',
        'breakfast' as MealType,
        'tuesday',
        'lunch' as MealType
      );

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast?.recipe?.id).toBe(2);
      expect(plan.days.tuesday.lunch?.recipe?.id).toBe(1);
    });

    it('should handle swap when one slot is empty', () => {
      const { addRecipe, swapRecipes } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);

      swapRecipes(
        'monday',
        'breakfast' as MealType,
        'tuesday',
        'lunch' as MealType
      );

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
      expect(plan.days.tuesday.lunch?.recipe?.id).toBe(1);
    });
  });

  describe('updateServings', () => {
    it('should update servings for a recipe', () => {
      const { addRecipe, updateServings } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      updateServings('monday', 'breakfast' as MealType, 6);

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast?.servings).toBe(6);
    });

    it('should not update if slot is empty', () => {
      const { updateServings } = useMealPlanStore.getState();

      updateServings('monday', 'breakfast' as MealType, 6);

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
    });
  });

  describe('clearDay', () => {
    it('should clear all meals for a day', () => {
      const { addRecipe, clearDay } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('monday', 'lunch' as MealType, mockRecipe2);
      addRecipe('monday', 'dinner' as MealType, mockRecipe1);

      clearDay('monday');

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
      expect(plan.days.monday.lunch).toBeNull();
      expect(plan.days.monday.dinner).toBeNull();
    });
  });

  describe('clearMeal', () => {
    it('should clear a specific meal type across all days', () => {
      const { addRecipe, clearMeal } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('tuesday', 'breakfast' as MealType, mockRecipe2);
      addRecipe('monday', 'lunch' as MealType, mockRecipe1);

      clearMeal('breakfast' as MealType);

      const { plan } = useMealPlanStore.getState();
      expect(plan.days.monday.breakfast).toBeNull();
      expect(plan.days.tuesday.breakfast).toBeNull();
      expect(plan.days.monday.lunch?.recipe?.id).toBe(1); // Lunch should remain
    });
  });

  describe('clearAll', () => {
    it('should clear the entire plan', () => {
      const { addRecipe, clearAll } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('tuesday', 'lunch' as MealType, mockRecipe2);
      addRecipe('wednesday', 'dinner' as MealType, mockRecipe1);

      clearAll();

      const { plan } = useMealPlanStore.getState();
      const allDays: DayOfWeek[] = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

      allDays.forEach((day) => {
        expect(plan.days[day].breakfast).toBeNull();
        expect(plan.days[day].lunch).toBeNull();
        expect(plan.days[day].dinner).toBeNull();
      });
    });
  });

  describe('setStartDate', () => {
    it('should set the start date', () => {
      const { setStartDate } = useMealPlanStore.getState();

      setStartDate('2024-01-01');

      const { plan } = useMealPlanStore.getState();
      expect(plan.startDate).toBe('2024-01-01');
    });
  });

  describe('setNutritionGoals', () => {
    it('should set nutrition goals', () => {
      const { setNutritionGoals } = useMealPlanStore.getState();

      const goals = {
        daily_calories: 2000,
        daily_protein_g: 150,
        daily_carbs_g: 200,
        daily_fat_g: 60,
      };

      setNutritionGoals(goals);

      const { plan } = useMealPlanStore.getState();
      expect(plan.nutritionGoals).toEqual(goals);
    });
  });

  describe('getDayNutrition', () => {
    it('should calculate daily nutrition totals', () => {
      const { addRecipe, getDayNutrition } = useMealPlanStore.getState();

      // Add recipes with known nutrition values
      const recipe1WithNutrition: RecipeListItem = {
        ...mockRecipe1,
        servings: 2,
        nutrition_summary: {
          calories: 600,
          protein_g: 30,
          carbohydrates_g: 50,
          fat_g: 20,
        },
      };

      addRecipe('monday', 'breakfast' as MealType, recipe1WithNutrition, 2);

      const nutrition = getDayNutrition('monday');

      expect(nutrition.calories).toBe(600);
      expect(nutrition.protein_g).toBe(30);
    });

    it('should handle servings multiplier correctly', () => {
      const { addRecipe, getDayNutrition } = useMealPlanStore.getState();

      const recipe: RecipeListItem = {
        ...mockRecipe1,
        servings: 2,
        nutrition_summary: {
          calories: 600,
          protein_g: 30,
          carbohydrates_g: 50,
          fat_g: 20,
        },
      };

      // Add with 4 servings (2x the recipe servings)
      addRecipe('monday', 'breakfast' as MealType, recipe, 4);

      const nutrition = getDayNutrition('monday');

      expect(nutrition.calories).toBe(1200); // 600 * 2
      expect(nutrition.protein_g).toBe(60); // 30 * 2
    });
  });

  describe('getWeeklyNutrition', () => {
    it('should calculate weekly nutrition totals', () => {
      const { addRecipe, getWeeklyNutrition } = useMealPlanStore.getState();

      const recipe: RecipeListItem = {
        ...mockRecipe1,
        nutrition_summary: {
          calories: 600,
          protein_g: 30,
          carbohydrates_g: 50,
          fat_g: 20,
        },
      };

      addRecipe('monday', 'breakfast' as MealType, recipe);
      addRecipe('tuesday', 'lunch' as MealType, recipe);

      const nutrition = getWeeklyNutrition();

      expect(nutrition.calories).toBe(1200);
      expect(nutrition.protein_g).toBe(60);
    });
  });

  describe('getDailyAverage', () => {
    it('should calculate daily average nutrition', () => {
      const { addRecipe, getDailyAverage } = useMealPlanStore.getState();

      const recipe: RecipeListItem = {
        ...mockRecipe1,
        nutrition_summary: {
          calories: 600,
          protein_g: 30,
          carbohydrates_g: 50,
          fat_g: 20,
        },
      };

      addRecipe('monday', 'breakfast' as MealType, recipe);
      addRecipe('tuesday', 'lunch' as MealType, recipe);

      const average = getDailyAverage();

      expect(average.calories).toBe(600); // 1200 / 2 days
      expect(average.protein_g).toBe(30); // 60 / 2 days
    });
  });

  describe('getTotalRecipes', () => {
    it('should count total number of recipes in plan', () => {
      const { addRecipe, getTotalRecipes } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('monday', 'lunch' as MealType, mockRecipe2);
      addRecipe('tuesday', 'dinner' as MealType, mockRecipe1);

      expect(getTotalRecipes()).toBe(3);
    });

    it('should return 0 for empty plan', () => {
      const { getTotalRecipes } = useMealPlanStore.getState();

      expect(getTotalRecipes()).toBe(0);
    });
  });

  describe('getUniqueRecipes', () => {
    it('should count unique recipes', () => {
      const { addRecipe, getUniqueRecipes } = useMealPlanStore.getState();

      addRecipe('monday', 'breakfast' as MealType, mockRecipe1);
      addRecipe('monday', 'lunch' as MealType, mockRecipe2);
      addRecipe('tuesday', 'dinner' as MealType, mockRecipe1); // Duplicate

      expect(getUniqueRecipes()).toBe(2);
    });

    it('should return 0 for empty plan', () => {
      const { getUniqueRecipes } = useMealPlanStore.getState();

      expect(getUniqueRecipes()).toBe(0);
    });
  });
});
