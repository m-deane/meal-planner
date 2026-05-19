import { MealType } from '../types';
import type { MealPlanResponse, DayPlan, MealSlot } from '../types/mealPlan';
import type { MealPlanState, DayOfWeek, DayState, MealSlotState } from '../store/mealPlanStore';

const DAY_ORDER: DayOfWeek[] = [
  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
];

function buildMealSlot(slot: MealSlotState, mealType: MealType): MealSlot | null {
  if (!slot.recipe) return null;
  return {
    meal_type: mealType,
    recipe: slot.recipe,
    servings: slot.servings,
    nutrition: null,
    notes: null,
  };
}

function offsetDate(isoDate: string, days: number): string {
  const d = new Date(isoDate);
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0] ?? isoDate;
}

/**
 * Converts the client-side Zustand MealPlanState (Record<DayOfWeek, DayState>)
 * into the MealPlanResponse shape expected by the backend POST /meal-plans endpoint.
 * Computed fields (nutrition totals, shopping preview) are set to null — the backend
 * will calculate them on save.
 */
export function mealPlanStateToResponse(state: MealPlanState): MealPlanResponse {
  const dayPlans: DayPlan[] = [];

  DAY_ORDER.forEach((dayKey, index) => {
    const dayData: DayState = state.days[dayKey];
    const meals: MealSlot[] = [];

    const breakfast = dayData.breakfast ? buildMealSlot(dayData.breakfast, MealType.BREAKFAST) : null;
    const lunch = dayData.lunch ? buildMealSlot(dayData.lunch, MealType.LUNCH) : null;
    const dinner = dayData.dinner ? buildMealSlot(dayData.dinner, MealType.DINNER) : null;

    if (breakfast) meals.push(breakfast);
    if (lunch) meals.push(lunch);
    if (dinner) meals.push(dinner);

    if (meals.length === 0) return;

    dayPlans.push({
      day: index + 1,
      date: state.startDate ? offsetDate(state.startDate, index) : null,
      meals,
      daily_nutrition: null,
      notes: null,
    });
  });

  const totalMeals = dayPlans.reduce((sum, d) => sum + d.meals.length, 0);
  const uniqueIds = new Set(dayPlans.flatMap(d => d.meals.map(m => m.recipe.id)));

  return {
    id: null,
    days: dayPlans,
    total_days: dayPlans.length,
    start_date: state.startDate,
    end_date: state.startDate ? offsetDate(state.startDate, 6) : null,
    average_daily_nutrition: null,
    total_nutrition: null,
    summary: {
      total_recipes: totalMeals,
      unique_recipes: uniqueIds.size,
      total_meals: totalMeals,
      average_cooking_time: null,
      difficulty_distribution: {},
    },
    shopping_list_preview: null,
    created_at: null,
    constraints_used: null,
  };
}
