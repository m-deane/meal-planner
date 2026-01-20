# Nutrition Dashboard Components

Comprehensive nutrition tracking and visualization components for the meal planner frontend.

## Components Overview

### 📊 Main Dashboard

**`NutritionDashboard.tsx`** - Main container component with complete nutrition analytics
- Grid layout with responsive design
- Summary cards for key metrics
- Multiple chart visualizations
- Weekly summary statistics

### 📈 Chart Components

**`MacroChart.tsx`** - Pie chart for macronutrient distribution
- Interactive tooltips with calories and grams
- Color-coded segments (Protein: blue, Carbs: green, Fat: amber)
- Percentage labels on segments
- Legend with gram values

**`WeeklyTrends.tsx`** - Line chart for nutrition trends over 7 days
- Toggle between metrics (Calories, Protein, Carbs, Fat)
- Reference lines for goals
- Hover tooltips with daily values
- Responsive to container size

**`DailyBreakdown.tsx`** - Stacked bar chart for meal-by-meal calories
- Each bar represents one day
- Segments for Breakfast/Lunch/Dinner
- Color-coded by meal type
- Click handler for meal details (optional)

**`MacroBreakdown.tsx`** - Horizontal progress bars for macros
- Shows current vs goal for Protein, Carbs, Fat, Fiber
- Color-coded status indicators
- Percentage completion display
- Summary statistics

### 🎯 Interactive Components

**`NutritionGoals.tsx`** - Configurable nutrition targets
- Input fields for all goals (Calories, Protein, Carbs, Fat, Fiber)
- Auto-save to localStorage via Zustand
- Reset to defaults button
- Macro calorie distribution calculator
- Validation and error handling

**`NutritionCard.tsx`** - Single stat display card
- Large number with unit display
- Goal comparison with trend indicator
- Up/Down/Neutral arrows based on percentage
- Customizable colors and decimals

## Store

**`nutritionGoalsStore.ts`** - Zustand store for nutrition goals
- Persists to localStorage automatically
- Default values based on standard 2000-cal diet
- Type-safe interface
- Reset functionality

```typescript
interface NutritionGoals {
  daily_calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}
```

## Usage

### Basic Setup

```tsx
import { NutritionDashboard } from '@/components/nutrition';

function MyPage() {
  return (
    <div className="container mx-auto p-6">
      <NutritionDashboard />
    </div>
  );
}
```

### Using Individual Components

```tsx
import {
  MacroChart,
  WeeklyTrends,
  NutritionCard,
  NutritionGoals
} from '@/components/nutrition';
import { useMealPlanStore } from '@/store/mealPlanStore';
import { useNutritionGoalsStore } from '@/store/nutritionGoalsStore';

function CustomDashboard() {
  const { getDailyAverage } = useMealPlanStore();
  const { goals } = useNutritionGoalsStore();

  const dailyAvg = getDailyAverage();

  return (
    <div className="grid grid-cols-2 gap-6">
      <NutritionCard
        label="Calories"
        value={dailyAvg.calories}
        unit="cal"
        goal={goals.daily_calories}
      />

      <MacroChart
        data={{
          protein_g: dailyAvg.protein_g,
          carbohydrates_g: dailyAvg.carbohydrates_g,
          fat_g: dailyAvg.fat_g,
        }}
      />

      <NutritionGoals />
    </div>
  );
}
```

### Setting Nutrition Goals

```tsx
import { useNutritionGoalsStore } from '@/store/nutritionGoalsStore';

function GoalsManager() {
  const { goals, setGoals, resetToDefaults } = useNutritionGoalsStore();

  const handleUpdateGoals = () => {
    setGoals({
      daily_calories: 2500,
      protein_g: 180,
    });
  };

  return (
    <button onClick={handleUpdateGoals}>
      Update Goals
    </button>
  );
}
```

## Data Flow

```
MealPlanStore (recipes + servings)
    ↓
calculateNutrition() → NutritionTotals
    ↓
getDayNutrition() / getDailyAverage()
    ↓
NutritionDashboard
    ↓
Individual Chart Components
```

## Props Reference

### NutritionCard

```typescript
interface NutritionCardProps {
  label: string;              // Card title
  value: number;              // Current value
  unit: string;               // Unit (e.g., "cal", "g")
  goal?: number;              // Target value (optional)
  subtitle?: string;          // Additional text (optional)
  showTrend?: boolean;        // Show up/down indicator (default: true)
  colorClass?: string;        // Tailwind color class (default: "text-blue-600")
  decimals?: number;          // Decimal places (default: 0)
}
```

### MacroChart

```typescript
interface MacroChartProps {
  data: {
    protein_g: number;
    carbohydrates_g: number;
    fat_g: number;
  };
  title?: string;             // Chart title (default: "Macronutrient Distribution")
}
```

### WeeklyTrends

```typescript
interface WeeklyTrendsProps {
  data: Array<{
    day: string;              // Day label (e.g., "Mon")
    calories: number;
    protein_g: number;
    carbohydrates_g: number;
    fat_g: number;
  }>;
  calorieGoal?: number;       // Reference line for calorie goal
  proteinGoal?: number;       // Reference line for protein goal
  title?: string;             // Chart title
}
```

### DailyBreakdown

```typescript
interface DailyBreakdownProps {
  data: Array<{
    day: string;
    breakfast: number;
    lunch: number;
    dinner: number;
    total: number;
  }>;
  title?: string;
  onDayClick?: (day: string) => void;  // Optional click handler
}
```

### MacroBreakdown

```typescript
interface MacroBreakdownProps {
  data: {
    protein_g: number;
    carbohydrates_g: number;
    fat_g: number;
    fiber_g: number;
  };
  goals: {
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
  };
  title?: string;
}
```

## Styling

All components use Tailwind CSS and follow the existing design system:

- **Colors**: Blue (primary), Green (success), Amber (warning), Purple (accent)
- **Spacing**: Consistent 6-unit grid system
- **Shadows**: `shadow-sm` for cards, `shadow-lg` for tooltips
- **Borders**: `border-gray-200` for subtle separation
- **Responsive**: Mobile-first with `sm:`, `md:`, `lg:` breakpoints

## Testing

Comprehensive test suite with 27 passing tests:

```bash
# Run all nutrition tests
npm test -- src/components/nutrition/__tests__/ --run

# Run individual test files
npm test -- src/components/nutrition/__tests__/NutritionCard.test.tsx --run
npm test -- src/store/__tests__/nutritionGoalsStore.test.ts --run
```

### Test Coverage

- ✅ Component rendering
- ✅ Props validation
- ✅ User interactions
- ✅ State management
- ✅ Store persistence
- ✅ Calculations and formatting
- ✅ Edge cases (zero values, missing data)

## Dependencies

- **recharts** (^2.10.0) - Chart library
- **zustand** (^4.4.0) - State management
- **lucide-react** (^0.309.0) - Icons
- **clsx** (^2.1.0) - Class name utilities
- **tailwindcss** (^3.4.0) - Styling

## Features

### ✨ Key Features

- **Real-time Updates**: Automatically recalculates when meal plan changes
- **Persistent Goals**: Goals saved to localStorage
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Interactive Charts**: Hover tooltips, clickable elements, metric toggles
- **Goal Tracking**: Visual indicators for meeting nutrition targets
- **Type Safety**: Full TypeScript support with strict types
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation

### 🎨 Visual Enhancements

- Smooth animations and transitions
- Color-coded status indicators
- Professional chart styling with Recharts
- Consistent spacing and alignment
- Loading states for async data

## Future Enhancements

Potential improvements:

- [ ] Export nutrition data to CSV/PDF
- [ ] Historical trend comparison (week-over-week)
- [ ] Micronutrient tracking (vitamins, minerals)
- [ ] Custom goal presets (keto, high-protein, balanced)
- [ ] Meal timing analysis
- [ ] Hydration tracking
- [ ] Integration with fitness trackers
- [ ] AI-powered nutrition insights

## Troubleshooting

### Charts not rendering

Ensure ResizeObserver is mocked in test environment:

```typescript
// test/setup.ts
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

### Data not persisting

Check localStorage permissions and clear cache:

```typescript
localStorage.clear();
// Refresh page
```

### Type errors

Ensure you're using the correct import paths:

```typescript
import { useMealPlanStore } from '@/store/mealPlanStore';
import { useNutritionGoalsStore } from '@/store/nutritionGoalsStore';
```

## Support

For issues or questions:
1. Check the component props in this README
2. Review test files for usage examples
3. Verify data structure from mealPlanStore
4. Check browser console for errors
