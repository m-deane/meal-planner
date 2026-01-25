/**
 * Main meal planner page with drag-and-drop interface.
 */

import React, { useState } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCenter,
} from '@dnd-kit/core';
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
import type { MealPlanGenerateRequest, RecipeListItem } from '../types';
import {
  Save,
  Trash2,
  Download,
  Settings,
  ChevronLeft,
  ChevronRight,
  Calendar,
} from 'lucide-react';
import { format } from 'date-fns';

// ============================================================================
// TYPES
// ============================================================================

interface DragData {
  recipe: RecipeListItem;
  servings: number;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const MealPlannerPage: React.FC = () => {
  const [showSidebar, setShowSidebar] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
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

  // Configure drag sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveId(active.id as string);

    // Store the drag data for the overlay
    if (active.data.current) {
      setActiveDragData(active.data.current as DragData);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
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
    const dragData = active.data.current as DragData;

    if (!dragData?.recipe) {
      return;
    }

    if (!source) {
      // Dragging from sidebar to board
      addRecipe(target.day, target.mealType, dragData.recipe, dragData.servings);
    } else {
      // Moving within board
      const targetDayState = plan.days[target.day];
      const targetMealKey = target.mealType === 'breakfast' ? 'breakfast' : target.mealType === 'lunch' ? 'lunch' : 'dinner';
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

  const handleDragCancel = () => {
    setActiveId(null);
    setActiveDragData(null);
  };

  const handleGeneratePlan = async (request: MealPlanGenerateRequest) => {
    try {
      const result = await generateMutation.mutateAsync(request);

      // Clear existing plan first
      clearAll();

      // Handle actual API response format: { plan: { Monday: { meals: { breakfast: {...}, ... } }, ... } }
      const planData = (result as any).plan;
      if (planData) {
        // Map day names to lowercase
        const dayNameMap: Record<string, string> = {
          'Monday': 'monday',
          'Tuesday': 'tuesday',
          'Wednesday': 'wednesday',
          'Thursday': 'thursday',
          'Friday': 'friday',
          'Saturday': 'saturday',
          'Sunday': 'sunday',
        };

        // Check for custom meal counts
        const mealCounts = (request as any).mealCounts;
        const usesCustomCounts = mealCounts !== undefined;

        // Track how many of each meal type we've added
        let breakfastCount = 0;
        let lunchCount = 0;
        let dinnerCount = 0;

        Object.entries(planData).forEach(([dayName, dayData]: [string, any]) => {
          const dayOfWeek = dayNameMap[dayName];
          if (!dayOfWeek || !dayData.meals) return;

          const meals = dayData.meals;

          // Process each meal type
          (['breakfast', 'lunch', 'dinner'] as const).forEach((mealType) => {
            const mealData = meals[mealType];
            if (mealData) {
              // Check if we should skip this meal based on custom counts
              if (usesCustomCounts) {
                if (mealType === 'breakfast' && breakfastCount >= mealCounts.breakfasts) return;
                if (mealType === 'lunch' && lunchCount >= mealCounts.lunches) return;
                if (mealType === 'dinner' && dinnerCount >= mealCounts.dinners) return;
              }

              // Convert API recipe format to frontend RecipeListItem format
              // Include nutrition data if available
              const nutritionData = mealData.nutrition;
              const recipe = {
                id: mealData.id,
                slug: mealData.slug,
                name: mealData.name,
                description: null,
                cooking_time_minutes: mealData.cooking_time_minutes,
                prep_time_minutes: null,
                total_time_minutes: mealData.cooking_time_minutes,
                difficulty: mealData.difficulty,
                servings: mealData.servings,
                categories: [],
                dietary_tags: [],
                allergens: [],
                main_image: mealData.image_url ? {
                  url: mealData.image_url,
                  alt_text: mealData.name,
                } : null,
                // Include nutrition summary from API response
                nutrition_summary: nutritionData ? {
                  calories: nutritionData.calories || 0,
                  protein_g: nutritionData.protein_g || 0,
                  carbohydrates_g: nutritionData.carbohydrates_g || 0,
                  fat_g: nutritionData.fat_g || 0,
                  fiber_g: nutritionData.fiber_g || 0,
                  sugar_g: nutritionData.sugar_g || 0,
                  sodium_mg: nutritionData.sodium_mg || 0,
                } : null,
                is_active: true,
                is_favorite: null,
              };

              addRecipe(
                dayOfWeek as any,
                mealType,
                recipe as any,
                mealData.servings || 2
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
      const nutritionGoals = (request as any).nutrition_goals;
      if (nutritionGoals) {
        setNutritionGoals(nutritionGoals);
      }

      setShowGenerateModal(false);
    } catch (error) {
      console.error('Failed to generate meal plan:', error);
      alert('Failed to generate meal plan. Please try again.');
    }
  };

  const handleSavePlan = async () => {
    if (totalRecipes === 0) {
      alert('Add some recipes to your meal plan first!');
      return;
    }

    try {
      // Show a placeholder message
      alert('Save functionality requires backend integration. Plan is saved locally via localStorage.');
    } catch (error) {
      console.error('Failed to save meal plan:', error);
      alert('Failed to save meal plan. Please try again.');
    }
  };

  const handleClearAll = () => {
    if (totalRecipes === 0) return;

    if (window.confirm('Are you sure you want to clear the entire meal plan?')) {
      clearAll();
    }
  };

  const handleExport = () => {
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

  const handleSetStartDate = () => {
    const date = prompt('Enter start date (YYYY-MM-DD):', format(new Date(), 'yyyy-MM-dd'));
    if (date) {
      setStartDate(date);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Meal Planner</h1>
              <p className="text-sm text-gray-600 mt-1">
                Drag and drop recipes to build your weekly meal plan
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleSetStartDate}
                className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                title="Set start date"
              >
                <Calendar className="w-4 h-4" />
                {plan.startDate ? format(new Date(plan.startDate), 'MMM d') : 'Set Date'}
              </button>

              <button
                onClick={() => setShowSettingsModal(true)}
                className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                title="Nutrition goals"
              >
                <Settings className="w-4 h-4" />
                Goals
              </button>

              <button
                onClick={handleExport}
                disabled={totalRecipes === 0}
                className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4" />
                Export
              </button>

              <button
                onClick={handleSavePlan}
                disabled={totalRecipes === 0 || saveMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4" />
                {saveMutation.isPending ? 'Saving...' : 'Save Plan'}
              </button>

              <button
                onClick={handleClearAll}
                disabled={totalRecipes === 0}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </button>
            </div>
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
          <div className="flex-1 overflow-auto p-6">
            <BoardContent />
          </div>

          {/* Sidebar */}
          <div
            className={`
              relative transition-all duration-300 bg-white border-l border-gray-200
              ${showSidebar ? 'w-96' : 'w-0'}
            `}
          >
            {showSidebar && (
              <PlannerSidebar
                onGeneratePlan={() => setShowGenerateModal(true)}
                isGenerating={generateMutation.isPending}
              />
            )}

            {/* Sidebar Toggle */}
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="absolute -left-4 top-6 w-8 h-8 bg-white border border-gray-300 rounded-full shadow-md hover:bg-gray-50 flex items-center justify-center"
              aria-label={showSidebar ? 'Hide sidebar' : 'Show sidebar'}
            >
              {showSidebar ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>
          </div>
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
      <div className="border-t border-gray-200 bg-white">
        <NutritionSummary className="shadow-none border-0 rounded-none" />
      </div>

      {/* Generate Plan Modal */}
      <GeneratePlanModal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        onGenerate={handleGeneratePlan}
        isGenerating={generateMutation.isPending}
      />

      {/* Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Nutrition Goals</h2>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="p-1 rounded-lg hover:bg-gray-100"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Daily Calories
                </label>
                <input
                  type="number"
                  value={plan.nutritionGoals.daily_calories || ''}
                  onChange={(e) => {
                    const { daily_calories: _, ...rest } = plan.nutritionGoals;
                    setNutritionGoals(
                      e.target.value
                        ? { ...rest, daily_calories: Number(e.target.value) }
                        : rest
                    );
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
                  value={plan.nutritionGoals.daily_protein_g || ''}
                  onChange={(e) => {
                    const { daily_protein_g: _, ...rest } = plan.nutritionGoals;
                    setNutritionGoals(
                      e.target.value
                        ? { ...rest, daily_protein_g: Number(e.target.value) }
                        : rest
                    );
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
                  value={plan.nutritionGoals.daily_carbs_g || ''}
                  onChange={(e) => {
                    const { daily_carbs_g: _, ...rest } = plan.nutritionGoals;
                    setNutritionGoals(
                      e.target.value
                        ? { ...rest, daily_carbs_g: Number(e.target.value) }
                        : rest
                    );
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
                  value={plan.nutritionGoals.daily_fat_g || ''}
                  onChange={(e) => {
                    const { daily_fat_g: _, ...rest } = plan.nutritionGoals;
                    setNutritionGoals(
                      e.target.value
                        ? { ...rest, daily_fat_g: Number(e.target.value) }
                        : rest
                    );
                  }}
                  placeholder="e.g., 60"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <button
                onClick={() => setShowSettingsModal(false)}
                className="w-full px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600"
              >
                Save Goals
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
