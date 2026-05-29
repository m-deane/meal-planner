/**
 * Main meal planner page with drag-and-drop interface.
 */

import React, { useState } from 'react';
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  KeyboardSensor,
  TouchSensor,
  useSensor,
  useSensors,
  closestCenter,
} from '@dnd-kit/core';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import toast from 'react-hot-toast';
import { useMealPlanStore } from '../store/mealPlanStore';
import {
  BoardContent,
  parseDragId,
  parseDropId,
  PlannerSidebar,
  NutritionSummary,
  GeneratePlanModal,
  DraggableRecipe,
} from '../components/meal-planner';
import {
  useGenerateMealPlan,
  useSaveMealPlan,
} from '../hooks/useMealPlan';
import { mealPlanStateToResponse } from '../utils/mealPlanAdapter';
import { MealType, ImageType } from '../types';
import type { MealPlanGenerateRequest, RecipeListItem, DifficultyLevel } from '../types';
import type { DayOfWeek } from '../store/mealPlanStore';
import {
  Save,
  Trash2,
  Download,
  Settings,
  Calendar,
  Wand2,
  PanelRight,
} from 'lucide-react';
import { format } from 'date-fns';
import { ConfirmModal } from '../components/common/ConfirmModal';
import { Modal } from '../components/common/Modal';

// ============================================================================
// TYPES
// ============================================================================

interface DragData {
  recipe: RecipeListItem;
  servings: number;
}

/** Shape of the nutrition data in the raw API meal response. */
interface RawMealNutrition {
  calories?: number;
  protein_g?: number;
  carbohydrates_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
}

/** Shape of a single meal in the raw API response. */
interface RawMealData {
  id: number;
  slug: string;
  name: string;
  cooking_time_minutes?: number;
  difficulty?: string;
  servings?: number;
  image_url?: string;
  nutrition?: RawMealNutrition;
}

/** Shape of a single day in the raw API response. */
interface RawDayData {
  meals: {
    breakfast?: RawMealData;
    lunch?: RawMealData;
    dinner?: RawMealData;
  };
}

/** Shape of the raw generate endpoint response (differs from typed MealPlanResponse). */
interface RawGenerateResponse {
  plan?: Record<string, RawDayData>;
}

/** Extended request type used for generation, including frontend-only fields. */
interface ExtendedGenerateRequest extends MealPlanGenerateRequest {
  useNutritionEndpoint?: boolean;
  mealCounts?: { breakfasts: number; lunches: number; dinners: number };
  nutrition_goals?: {
    daily_calories?: number;
    daily_protein_g?: number;
    daily_carbs_g?: number;
    daily_fat_g?: number;
  };
}

// ============================================================================
// COMPONENT
// ============================================================================

export const MealPlannerPage: React.FC = () => {
  // Open sidebar by default on desktop (≥768 px); keep closed on mobile
  const [showSidebar, setShowSidebar] = useState(() => window.innerWidth >= 768);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [pendingDate, setPendingDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeDragData, setActiveDragData] = useState<DragData | null>(null);

  const {
    plan,
    clearAll,
    setStartDate,
    setNutritionGoals,
    getTotalRecipes,
    addRecipe,
    moveRecipe,
    swapRecipes,
  } = useMealPlanStore();

  const generateMutation = useGenerateMealPlan();
  const saveMutation = useSaveMealPlan();

  const totalRecipes = getTotalRecipes();

  // Configure drag sensors:
  // - PointerSensor for mouse (small movement threshold)
  // - TouchSensor with a short hold delay so the board can still be scrolled on
  //   touch devices before a drag begins
  // - KeyboardSensor so the drag-and-drop planner is fully keyboard-accessible
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200,
        tolerance: 8,
      },
    }),
    useSensor(KeyboardSensor)
  );

  const handleDragStart = (event: DragStartEvent): void => {
    const { active } = event;
    setActiveId(active.id as string);

    // Store the drag data for the overlay
    if (active.data.current) {
      setActiveDragData(active.data.current as DragData);
    }
  };

  const handleDragEnd = (event: DragEndEvent): void => {
    const { active, over } = event;

    setActiveId(null);
    setActiveDragData(null);

    if (!over) {
      return;
    }

    const dragActiveId = active.id as string;
    const overId = over.id as string;

    // Parse source (where drag started)
    const source = parseDragId(dragActiveId);
    const target = parseDropId(overId);

    if (!target) {
      return;
    }

    // Get the recipe data
    const dragData = active.data.current as DragData | null;

    if (!dragData?.recipe) {
      return;
    }

    if (!source) {
      // Dragging from sidebar to board
      addRecipe(target.day, target.mealType, dragData.recipe, dragData.servings);
    } else {
      // Moving within board
      const targetDayState = plan.days[target.day];
      const targetMealKey = target.mealType === MealType.BREAKFAST ? 'breakfast' : target.mealType === MealType.LUNCH ? 'lunch' : 'dinner';
      const targetSlot = targetDayState[targetMealKey];

      if (targetSlot) {
        // Target slot has a recipe - swap
        swapRecipes(source.day, source.mealType, target.day, target.mealType);
      } else {
        // Target slot is empty - move
        moveRecipe(source.day, source.mealType, target.day, target.mealType);
      }
    }
  };

  const handleDragCancel = (): void => {
    setActiveId(null);
    setActiveDragData(null);
  };

  const handleGeneratePlan = async (request: MealPlanGenerateRequest): Promise<void> => {
    try {
      const result = await generateMutation.mutateAsync(request);
      const extendedRequest = request as ExtendedGenerateRequest;

      // Clear existing plan first
      clearAll();

      // Handle actual API response format: { plan: { Monday: { meals: { breakfast: {...}, ... } }, ... } }
      const rawResult = result as unknown as RawGenerateResponse;
      const planData = rawResult.plan;
      if (planData) {
        // Map day names to lowercase DayOfWeek values
        const dayNameMap: Record<string, DayOfWeek> = {
          'Monday': 'monday',
          'Tuesday': 'tuesday',
          'Wednesday': 'wednesday',
          'Thursday': 'thursday',
          'Friday': 'friday',
          'Saturday': 'saturday',
          'Sunday': 'sunday',
        };

        // Map meal type strings to MealType enum values
        const mealTypeMap: Record<string, MealType> = {
          'breakfast': MealType.BREAKFAST,
          'lunch': MealType.LUNCH,
          'dinner': MealType.DINNER,
        };

        // Check for custom meal counts
        const mealCounts = extendedRequest.mealCounts;

        // Track how many of each meal type we've added
        let breakfastCount = 0;
        let lunchCount = 0;
        let dinnerCount = 0;

        Object.entries(planData).forEach(([dayName, dayData]) => {
          const dayOfWeek = dayNameMap[dayName];
          if (!dayOfWeek) return;

          const meals = dayData.meals;

          // Process each meal type
          (['breakfast', 'lunch', 'dinner'] as const).forEach((mealType) => {
            const mealData = meals[mealType];
            if (mealData) {
              // Check if we should skip this meal based on custom counts
              if (mealCounts) {
                if (mealType === 'breakfast' && breakfastCount >= mealCounts.breakfasts) return;
                if (mealType === 'lunch' && lunchCount >= mealCounts.lunches) return;
                if (mealType === 'dinner' && dinnerCount >= mealCounts.dinners) return;
              }

              // Convert API recipe format to frontend RecipeListItem format
              // Include nutrition data if available
              const nutritionData = mealData.nutrition;
              const recipe: RecipeListItem = {
                id: mealData.id,
                slug: mealData.slug,
                name: mealData.name,
                description: null,
                cooking_time_minutes: mealData.cooking_time_minutes ?? null,
                prep_time_minutes: null,
                total_time_minutes: mealData.cooking_time_minutes ?? null,
                difficulty: mealData.difficulty as DifficultyLevel | null,
                servings: mealData.servings ?? 2,
                categories: [],
                dietary_tags: [],
                allergens: [],
                main_image: mealData.image_url ? {
                  id: 0,
                  url: mealData.image_url,
                  image_type: ImageType.MAIN,
                  display_order: 0,
                  alt_text: mealData.name,
                  width: null,
                  height: null,
                } : null,
                // Include nutrition summary from API response
                nutrition_summary: nutritionData ? {
                  calories: nutritionData.calories ?? 0,
                  protein_g: nutritionData.protein_g ?? 0,
                  carbohydrates_g: nutritionData.carbohydrates_g ?? 0,
                  fat_g: nutritionData.fat_g ?? 0,
                } : null,
                is_active: true,
              };

              const mappedMealType = mealTypeMap[mealType];
              if (!mappedMealType) return;

              addRecipe(
                dayOfWeek,
                mappedMealType,
                recipe,
                mealData.servings ?? 2
              );

              // Track meal counts
              if (mealType === 'breakfast') breakfastCount++;
              if (mealType === 'lunch') lunchCount++;
              if (mealType === 'dinner') dinnerCount++;
            }
          });
        });
      }

      // Set nutrition goals from request if provided
      const nutritionGoals = extendedRequest.nutrition_goals;
      if (nutritionGoals) {
        setNutritionGoals(nutritionGoals);
      }

      setShowGenerateModal(false);
      toast.success('Meal plan generated!');
    } catch (error) {
      console.error('Failed to generate meal plan:', error);
      toast.error('Failed to generate meal plan. Please try again.');
    }
  };

  const handleSavePlan = (): void => {
    if (totalRecipes === 0) {
      toast('Add some recipes to your meal plan first!');
      return;
    }
    saveMutation.mutate(mealPlanStateToResponse(plan), {
      onSuccess: () => toast.success('Meal plan saved!'),
    });
  };

  const handleClearAll = (): void => {
    if (totalRecipes === 0) return;
    setShowClearConfirm(true);
  };

  const handleExport = (): void => {
    // Export to markdown/JSON
    const exportData = {
      plan,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `meal-plan-${format(new Date(), 'yyyy-MM-dd')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSetStartDate = (): void => {
    setPendingDate(plan.startDate ?? format(new Date(), 'yyyy-MM-dd'));
    setShowDatePicker(true);
  };

  const handleConfirmDate = (): void => {
    if (pendingDate) {
      setStartDate(pendingDate);
    }
    setShowDatePicker(false);
  };

  return (
    <div className="h-[calc(100dvh-8rem)] md:h-[calc(100dvh-4rem)] flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-3 sm:px-6 py-3 sm:py-4">
          {/* Title row */}
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0 flex-shrink">
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900 truncate">Meal Planner</h1>
              <p className="text-sm text-gray-600 mt-0.5 hidden sm:block">
                Drag and drop recipes to build your weekly meal plan
              </p>
            </div>

            {/* Secondary actions — icon-only on mobile, icon+text on sm+ */}
            <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
              {/* Generate — shown in this row on sm+; hidden on mobile (shown in row below) */}
              <button
                onClick={() => { setShowGenerateModal(true); }}
                className="hidden sm:flex items-center gap-2 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 whitespace-nowrap"
                title="Generate meal plan"
              >
                <Wand2 className="w-4 h-4 flex-shrink-0" />
                Generate
              </button>

              <button
                onClick={handleSetStartDate}
                className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                title="Set start date"
              >
                <Calendar className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">
                  {plan.startDate ? format(new Date(plan.startDate), 'MMM d') : 'Date'}
                </span>
              </button>

              <button
                onClick={() => { setShowSettingsModal(true); }}
                className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 whitespace-nowrap"
                title="Nutrition goals"
              >
                <Settings className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">Goals</span>
              </button>

              <button
                onClick={handleExport}
                disabled={totalRecipes === 0}
                className="hidden sm:flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                title="Export plan"
              >
                <Download className="w-4 h-4 flex-shrink-0" />
                Export
              </button>

              <button
                onClick={handleSavePlan}
                disabled={totalRecipes === 0 || saveMutation.isPending}
                className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 text-sm bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                title="Save plan"
              >
                <Save className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">
                  {saveMutation.isPending ? 'Saving...' : 'Save'}
                </span>
              </button>

              <button
                onClick={handleClearAll}
                disabled={totalRecipes === 0}
                className="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                title="Clear all"
              >
                <Trash2 className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">Clear</span>
              </button>

              <button
                onClick={() => { setShowSidebar(!showSidebar); }}
                className={`flex items-center gap-2 px-2 sm:px-3 py-2 text-sm border rounded-lg hover:bg-gray-50 whitespace-nowrap ${showSidebar ? 'border-indigo-300 bg-indigo-50 text-indigo-700' : 'border-gray-300'}`}
                title={showSidebar ? 'Hide recipe library' : 'Show recipe library'}
                aria-pressed={showSidebar}
              >
                <PanelRight className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">Recipes</span>
              </button>
            </div>
          </div>

          {/* Mobile-only Generate row — full-width, always visible */}
          <div className="mt-2 sm:hidden">
            <button
              onClick={() => { setShowGenerateModal(true); }}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
            >
              <Wand2 className="w-4 h-4" />
              Generate Meal Plan
            </button>
          </div>
        </div>
      </header>

      {/* Main Content with DndContext wrapping both board and sidebar */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={handleDragCancel}
      >
        <div className="flex-1 flex overflow-hidden">
          {/* Meal Planner Board */}
          <div className="flex-1 overflow-auto p-2 sm:p-6">
            <BoardContent />
          </div>

          {/* Recipe library sidebar.
              On mobile this is a bottom sheet so the board stays visible above
              and recipes can be dragged up onto a meal slot; on >=sm it is the
              usual side column. */}
          {showSidebar && (
            <div
              className="
                bg-white border-gray-200 overflow-y-auto
                fixed bottom-0 left-0 right-0 z-40 max-h-[60vh] border-t rounded-t-xl shadow-2xl
                sm:static sm:max-h-none sm:rounded-none sm:shadow-none sm:border-t-0
                sm:border-l sm:w-80 xl:w-96 sm:flex-shrink-0 sm:z-auto
              "
            >
              <PlannerSidebar
                onGeneratePlan={() => { setShowGenerateModal(true); }}
                isGenerating={generateMutation.isPending}
              />
            </div>
          )}
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeId && activeDragData ? (
            <div className="rotate-3 scale-105">
              <DraggableRecipe
                recipe={activeDragData.recipe}
                servings={activeDragData.servings}
                dragId="overlay"
                compact
                showRemoveButton={false}
              />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Nutrition Summary Footer */}
      <div className="border-t border-gray-200 bg-white pb-20 md:pb-0">
        <NutritionSummary className="shadow-none border-0 rounded-none" />
      </div>

      {/* Generate Plan Modal */}
      <GeneratePlanModal
        isOpen={showGenerateModal}
        onClose={() => { setShowGenerateModal(false); }}
        onGenerate={handleGeneratePlan}
        isGenerating={generateMutation.isPending}
      />

      {/* Settings Modal */}
      <Modal
        isOpen={showSettingsModal}
        onClose={() => { setShowSettingsModal(false); }}
        title="Nutrition Goals"
        size="sm"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Daily Calories
            </label>
            <input
              type="number"
              value={plan.nutritionGoals.daily_calories ?? ''}
              onChange={(e) => {
                const next = { ...plan.nutritionGoals };
                if (e.target.value) {
                  next.daily_calories = Number(e.target.value);
                } else {
                  delete next.daily_calories;
                }
                setNutritionGoals(next);
              }}
              placeholder="e.g., 2000"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Daily Protein (g)
            </label>
            <input
              type="number"
              value={plan.nutritionGoals.daily_protein_g ?? ''}
              onChange={(e) => {
                const next = { ...plan.nutritionGoals };
                if (e.target.value) {
                  next.daily_protein_g = Number(e.target.value);
                } else {
                  delete next.daily_protein_g;
                }
                setNutritionGoals(next);
              }}
              placeholder="e.g., 150"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Daily Carbs (g)
            </label>
            <input
              type="number"
              value={plan.nutritionGoals.daily_carbs_g ?? ''}
              onChange={(e) => {
                const next = { ...plan.nutritionGoals };
                if (e.target.value) {
                  next.daily_carbs_g = Number(e.target.value);
                } else {
                  delete next.daily_carbs_g;
                }
                setNutritionGoals(next);
              }}
              placeholder="e.g., 200"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Daily Fat (g)
            </label>
            <input
              type="number"
              value={plan.nutritionGoals.daily_fat_g ?? ''}
              onChange={(e) => {
                const next = { ...plan.nutritionGoals };
                if (e.target.value) {
                  next.daily_fat_g = Number(e.target.value);
                } else {
                  delete next.daily_fat_g;
                }
                setNutritionGoals(next);
              }}
              placeholder="e.g., 60"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <button
            type="button"
            onClick={() => { setShowSettingsModal(false); }}
            className="w-full px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600"
          >
            Save Goals
          </button>
        </div>
      </Modal>

      {/* Date Picker Modal */}
      <Modal
        isOpen={showDatePicker}
        onClose={() => { setShowDatePicker(false); }}
        title="Set Start Date"
        size="sm"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Week start date
            </label>
            <input
              type="date"
              value={pendingDate}
              onChange={(e) => { setPendingDate(e.target.value); }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => { setShowDatePicker(false); }}
              className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirmDate}
              className="px-4 py-2 text-sm bg-indigo-500 text-white rounded-lg hover:bg-indigo-600"
            >
              Set Date
            </button>
          </div>
        </div>
      </Modal>

      {/* Clear All Confirmation Modal */}
      <ConfirmModal
        isOpen={showClearConfirm}
        onClose={() => { setShowClearConfirm(false); }}
        onConfirm={clearAll}
        title="Clear Meal Plan"
        message="Are you sure you want to clear the entire meal plan? This cannot be undone."
        confirmLabel="Clear All"
        variant="danger"
      />
    </div>
  );
};
