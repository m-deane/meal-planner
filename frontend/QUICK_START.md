# Quick Start Guide - Meal Planner

## Step 1: Install New Dependencies

The meal planner requires three new npm packages:

```bash
cd /home/user/meal-planner/frontend
npm install
```

This will install:
- `lucide-react@^0.309.0` - Icon library
- `date-fns@^3.0.0` - Date utilities
- `@dnd-kit/utilities@^3.2.2` - Drag & drop utilities

## Step 2: Verify Installation

Run the tests to verify everything is working:

```bash
npm test
```

You should see all 38 meal planner tests passing (24 store tests + 14 component tests).

## Step 3: Run Development Server

```bash
npm run dev
```

## Step 4: Access the Meal Planner

Navigate to: `http://localhost:5173/meal-planner`

## Features Available

### 1. Drag & Drop Recipes
- Browse recipes in the right sidebar
- Drag recipes into meal slots (Breakfast, Lunch, Dinner)
- Move recipes between days and meals
- Swap recipes by dragging one onto another

### 2. Manage Your Plan
- **Adjust Servings**: Use +/- buttons on each recipe
- **Remove Recipes**: Click the X button on recipe cards
- **Clear Day**: Use trash icon in day header
- **Clear All**: Main toolbar button

### 3. Track Nutrition
- View daily nutrition in each day column
- See weekly totals in footer summary
- Track daily averages against goals
- Monitor macronutrients (calories, protein, carbs, fat)

### 4. Set Goals
- Click "Goals" button in toolbar
- Set daily targets for calories, protein, carbs, fat
- View progress bars in nutrition summary

### 5. Generate Meal Plan
- Click "Generate Meal Plan" in sidebar
- Choose number of days (3, 5, or 7)
- Select meal types to include
- Set nutrition constraints
- Set max cooking time

### 6. Export & Save
- **Export**: Download as JSON
- **Save**: Persist to backend (requires API integration)
- **Print**: Use browser print from detail page

## File Structure

```
frontend/src/
├── store/
│   ├── mealPlanStore.ts          # Zustand state management
│   └── __tests__/
│       └── mealPlanStore.test.ts # Store tests (24 tests)
├── components/
│   └── meal-planner/
│       ├── MealPlannerBoard.tsx  # Main drag & drop board
│       ├── DayColumn.tsx         # Day with 3 meal slots
│       ├── MealSlot.tsx          # Individual meal slot
│       ├── DraggableRecipe.tsx   # Recipe card
│       ├── PlannerSidebar.tsx    # Recipe library
│       ├── NutritionSummary.tsx  # Nutrition tracking
│       ├── GeneratePlanModal.tsx # AI plan generation
│       ├── index.ts              # Exports
│       ├── README.md             # Full documentation
│       └── __tests__/
│           └── DraggableRecipe.test.tsx # Component tests
└── pages/
    ├── MealPlannerPage.tsx       # Main page
    └── MealPlanDetailPage.tsx    # View saved plan
```

## Common Tasks

### Add a Recipe to Monday Breakfast
1. Find recipe in sidebar
2. Drag it to Monday's breakfast slot
3. Adjust servings if needed

### View Nutrition for a Day
- Look at the bottom section of each day column
- See calories, protein, carbs, fat

### Set Weekly Start Date
1. Click "Set Date" button in toolbar
2. Enter date in YYYY-MM-DD format
3. Dates will appear on day headers

### Export Your Plan
1. Fill in your meal plan
2. Click "Export" in toolbar
3. JSON file will download
4. Can be re-imported later

## State Persistence

Your meal plan is automatically saved to browser localStorage:
- Key: `meal-plan-storage`
- Survives page refreshes
- Cleared on browser cache clear

## Keyboard Shortcuts

- **Tab**: Navigate between elements
- **Enter/Space**: Activate buttons
- **Escape**: Close modals

## Troubleshooting

### Drag not working
1. Ensure dependencies are installed (`npm install`)
2. Check browser console for errors
3. Try refreshing the page

### Nutrition not calculating
1. Verify recipes have nutrition data
2. Check recipe servings are set
3. Inspect store state in DevTools

### Tests failing
1. Run `npm install` to get dependencies
2. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
3. Check TypeScript errors: `npm run type-check`

## Browser Requirements

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Next Steps

1. **Integrate with Backend**: Connect save/load functionality to API
2. **Add Routes**: Add meal planner routes to your router
3. **Customize Styles**: Adjust Tailwind classes for your brand
4. **Add Features**: Extend with meal templates, sharing, etc.

## Support

- Full documentation: `src/components/meal-planner/README.md`
- Implementation summary: `MEAL_PLANNER_IMPLEMENTATION.md`
- Test examples: `src/store/__tests__/` and `src/components/meal-planner/__tests__/`

---

**Ready to use!** Just run `npm install` and start planning meals! 🍽️
