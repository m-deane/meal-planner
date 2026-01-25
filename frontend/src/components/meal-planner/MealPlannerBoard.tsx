/**
 * Main meal planner board with drag-and-drop functionality.
 */

import React from 'react';
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
import { useMealPlanStore, type DayOfWeek } from '../../store/mealPlanStore';
import { DayColumn } from './DayColumn';
import type { RecipeListItem, MealType } from '../../types';
import { DraggableRecipe } from './DraggableRecipe';

// ============================================================================
// TYPES
// ============================================================================

export interface MealPlannerBoardProps {
  className?: string;
}

interface DragData {
  recipe: RecipeListItem;
  servings: number;
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

export const parseDragId = (
  id: string
): { day: DayOfWeek; mealType: MealType } | null => {
  // Format: "day-mealType-recipe" or "sidebar-recipe-id"
  if (id.startsWith('sidebar-')) {
    return null; // From sidebar, not from board
  }

  const parts = id.split('-');
  if (parts.length >= 2) {
    const day = parts[0] as DayOfWeek;
    const mealType = parts[1] as MealType;
    return { day, mealType };
  }

  return null;
};

export const parseDropId = (
  id: string
): { day: DayOfWeek; mealType: MealType } | null => {
  // Format: "day-mealType"
  const parts = id.split('-');
  if (parts.length >= 2) {
    const day = parts[0] as DayOfWeek;
    const mealType = parts[1] as MealType;
    return { day, mealType };
  }

  return null;
};

// ============================================================================
// BOARD CONTENT COMPONENT (no DndContext - expects parent to provide it)
// ============================================================================

export interface BoardContentProps {
  className?: string;
}

export const BoardContent: React.FC<BoardContentProps> = ({
  className = '',
}) => {
  const { plan } = useMealPlanStore();

  return (
    <div className={`${className}`}>
      {/* Days Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-4">
        {DAYS_OF_WEEK.map((day) => (
          <DayColumn
            key={day}
            day={day}
            dayData={plan.days[day]}
            startDate={plan.startDate}
            showNutrition
          />
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT (wraps content with DndContext for standalone use)
// ============================================================================

export const MealPlannerBoard: React.FC<MealPlannerBoardProps> = ({
  className = '',
}) => {
  const { plan, addRecipe, moveRecipe, swapRecipes } = useMealPlanStore();
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [activeDragData, setActiveDragData] = React.useState<DragData | null>(null);

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

    const activeId = active.id as string;
    const overId = over.id as string;

    // Parse source (where drag started)
    const source = parseDragId(activeId);
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

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <BoardContent className={className} />

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
  );
};
