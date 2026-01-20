# Meal Planner - Interactive Drag & Drop Interface

A comprehensive meal planning system with drag-and-drop functionality, nutrition tracking, and meal plan generation.

## Features

- **Drag & Drop Interface**: Intuitive recipe placement using @dnd-kit
- **Weekly Planning**: Plan meals for 7 days (Monday-Sunday)
- **Three Meal Types**: Breakfast, Lunch, and Dinner slots per day
- **Nutrition Tracking**: Real-time daily and weekly nutrition summaries
- **Recipe Library**: Browse, search, and filter recipes
- **Meal Plan Generation**: AI-powered meal plan generation with constraints
- **Local Storage**: Automatic persistence of meal plans
- **Export Functionality**: Export plans to JSON/Markdown
- **Shopping List Integration**: Generate shopping lists from meal plans

## Components

### MealPlannerBoard
Main container with drag-and-drop context.

```tsx
import { MealPlannerBoard } from './components/meal-planner';

<MealPlannerBoard />
```

### DayColumn
Displays a single day with three meal slots.

**Features**:
- Day header with date
- Breakfast, lunch, dinner slots
- Daily nutrition summary
- Clear day action

### MealSlot
Individual droppable zone for a meal.

**Features**:
- Meal type indicator (icon + label)
- Empty state with drop hint
- Recipe display when populated
- Servings adjuster
- Remove button

### DraggableRecipe
Compact recipe card that can be dragged.

**Props**:
```tsx
interface DraggableRecipeProps {
  recipe: RecipeListItem;
  servings?: number;
  onRemove?: () => void;
  dragId: string;
  compact?: boolean;
  showRemoveButton?: boolean;
}
```

**Features**:
- Recipe image thumbnail
- Name and cooking time
- Nutrition badges (calories, protein)
- Dietary tags
- Difficulty indicator
- Drag handle

### PlannerSidebar
Recipe library with search and filters.

**Features**:
- Recipe search
- Filter by:
  - Cooking time
  - Difficulty level
  - Dietary preferences
- Infinite scroll
- Generate plan button

### NutritionSummary
Weekly nutrition overview with goals tracking.

**Features**:
- Weekly totals
- Daily averages
- Progress bars toward goals
- Recipe statistics (total, unique, variety)
- Macronutrient breakdown

### GeneratePlanModal
Modal for configuring AI meal plan generation.

**Options**:
- Number of days (3, 5, 7)
- Meal types to include
- Nutrition constraints (calories, protein)
- Max cooking time
- Recipe variety settings
- Shopping list optimization

## State Management

### Zustand Store (`useMealPlanStore`)

**State**:
```typescript
interface MealPlanState {
  days: Record<DayOfWeek, DayState>;
  startDate: string | null;
  nutritionGoals: {
    daily_calories?: number;
    daily_protein_g?: number;
    daily_carbs_g?: number;
    daily_fat_g?: number;
  };
}
```

**Actions**:
- `addRecipe(day, mealType, recipe, servings?)`
- `removeRecipe(day, mealType)`
- `moveRecipe(fromDay, fromMeal, toDay, toMeal)`
- `swapRecipes(day1, meal1, day2, meal2)`
- `updateServings(day, mealType, servings)`
- `clearDay(day)`
- `clearMeal(mealType)`
- `clearAll()`
- `setStartDate(date)`
- `setNutritionGoals(goals)`

**Selectors**:
- `getDayNutrition(day)`: Calculate daily nutrition
- `getWeeklyNutrition()`: Calculate weekly totals
- `getDailyAverage()`: Calculate daily averages
- `getTotalRecipes()`: Count total meal slots filled
- `getUniqueRecipes()`: Count unique recipes used

**Persistence**:
- Automatically saved to localStorage
- Key: `meal-plan-storage`

## Pages

### MealPlannerPage
Main meal planning interface.

**Route**: `/meal-planner`

**Features**:
- Drag-and-drop board
- Collapsible sidebar
- Nutrition summary footer
- Actions toolbar:
  - Set start date
  - Configure nutrition goals
  - Export plan
  - Save plan
  - Clear all

### MealPlanDetailPage
View saved meal plan.

**Route**: `/meal-plans/:id`

**Features**:
- Read-only plan view
- Nutrition statistics
- Export to Markdown
- Print layout
- Generate shopping list
- Delete plan

## Drag & Drop Behavior

### Drag Sources
1. **Sidebar recipes**: Dragging adds to board
2. **Board recipes**: Dragging moves/swaps

### Drop Targets
- Any meal slot (breakfast, lunch, dinner)
- Dropping on empty slot: Places recipe
- Dropping on filled slot: Swaps recipes

### Visual Feedback
- Drag overlay with rotated card
- Drop zone highlighting
- Border color changes
- Scale animation on hover

### Touch Support
- Pointer sensor with 8px activation distance
- Works on mobile/tablet devices

## Usage Examples

### Adding a Recipe Manually
```typescript
const { addRecipe } = useMealPlanStore();

addRecipe('monday', 'breakfast', recipe, 2); // 2 servings
```

### Generating a Meal Plan
```typescript
const request: MealPlanGenerateRequest = {
  days: 7,
  meal_preferences: {
    include_breakfast: true,
    include_lunch: true,
    include_dinner: true,
    include_snacks: false,
  },
  nutrition_constraints: {
    target_calories: 2000,
    target_protein_g: 150,
  },
  avoid_duplicate_recipes: true,
  max_recipe_reuse: 1,
  variety_score_weight: 0.3,
  optimize_shopping_list: true,
};

const plan = await generateMealPlan(request);
```

### Setting Nutrition Goals
```typescript
const { setNutritionGoals } = useMealPlanStore();

setNutritionGoals({
  daily_calories: 2000,
  daily_protein_g: 150,
  daily_carbs_g: 200,
  daily_fat_g: 60,
});
```

### Calculating Nutrition
```typescript
const { getDayNutrition, getWeeklyNutrition } = useMealPlanStore();

const mondayNutrition = getDayNutrition('monday');
console.log(mondayNutrition.calories); // Total calories for Monday

const weeklyNutrition = getWeeklyNutrition();
console.log(weeklyNutrition.protein_g); // Total protein for the week
```

## Styling

Uses Tailwind CSS with:
- Gradient backgrounds
- Shadow effects
- Smooth transitions
- Responsive grid layouts
- Custom animations

### Color Scheme
- Primary: Indigo (500-600)
- Success: Green (500-600)
- Danger: Red (500-600)
- Warning: Yellow (500-600)
- Info: Blue (500-600)

## Testing

### Unit Tests
```bash
npm test src/store/__tests__/mealPlanStore.test.ts
```

### Component Tests
```bash
npm test src/components/meal-planner/__tests__/
```

### Integration Tests
Run full test suite:
```bash
npm test
```

## Dependencies

Required packages:
- `@dnd-kit/core`: ^6.1.0 - Core drag & drop
- `@dnd-kit/sortable`: ^8.0.0 - Sortable utilities
- `@dnd-kit/utilities`: ^3.2.2 - Helper utilities
- `zustand`: ^4.4.0 - State management
- `date-fns`: ^3.0.0 - Date formatting
- `lucide-react`: ^0.309.0 - Icons
- `react-router-dom`: ^6.21.0 - Routing

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 14+, Chrome Android

## Performance Considerations

- Lazy loading of recipe images
- Infinite scroll for recipe library
- Debounced search (300ms)
- Memoized nutrition calculations
- LocalStorage persistence (async)

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus management
- Color contrast compliance (WCAG AA)

## Future Enhancements

- [ ] Snack meal type support
- [ ] Recipe substitution suggestions
- [ ] Meal plan templates
- [ ] Collaborative meal planning
- [ ] Mobile app version
- [ ] Offline support with service workers
- [ ] Recipe scaling calculator
- [ ] Leftover tracking
- [ ] Meal prep mode
- [ ] Calendar integration

## Troubleshooting

### Drag not working
- Ensure `@dnd-kit` packages are installed
- Check DndContext wraps components
- Verify unique drag IDs

### Nutrition not calculating
- Check recipe has `nutritional_info` field
- Verify servings are set correctly
- Ensure recipes are properly added to store

### LocalStorage issues
- Clear browser storage and refresh
- Check storage quota limits
- Verify localStorage is enabled

## Support

For issues or questions:
1. Check this documentation
2. Review component props and types
3. Examine test files for usage examples
4. Check browser console for errors
