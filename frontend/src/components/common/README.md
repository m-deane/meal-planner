# Common UI Components

A comprehensive library of reusable React components for the meal-planner application. All components are fully typed with TypeScript, styled with Tailwind CSS, and designed with accessibility in mind.

## Components

### Button

Versatile button component with multiple variants, sizes, and states.

**Features:**
- 5 variants: primary, secondary, outline, ghost, danger
- 3 sizes: sm, md, lg
- Loading state with spinner
- Icon support (left/right)
- Disabled state
- Full width option

**Usage:**
```tsx
import { Button } from '@/components/common';

// Basic usage
<Button variant="primary" onClick={handleClick}>
  Click me
</Button>

// With icon
<Button variant="outline" iconLeft={<PlusIcon />}>
  Add Recipe
</Button>

// Loading state
<Button loading>
  Saving...
</Button>
```

---

### Card

Container component for displaying content in an elevated box.

**Features:**
- Header, body, and footer sections
- Optional image with aspect ratio control
- Hover effects
- Click handler with keyboard accessibility
- Selected state
- Customizable padding

**Usage:**
```tsx
import { Card } from '@/components/common';

<Card
  image={{ src: '/recipe.jpg', alt: 'Recipe', aspectRatio: 'video' }}
  header={<h3>Recipe Title</h3>}
  footer={<Button>View Recipe</Button>}
  hoverable
  onClick={() => navigate(`/recipe/${id}`)}
>
  <p>Recipe description...</p>
</Card>
```

---

### Modal

Accessible modal dialog using Headless UI.

**Features:**
- 4 sizes: sm, md, lg, full
- Backdrop click to close
- Close button
- Smooth animations
- Title and description slots
- Action buttons footer

**Usage:**
```tsx
import { Modal } from '@/components/common';

const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Delete Recipe"
  description="Are you sure you want to delete this recipe?"
  actions={
    <>
      <Button variant="outline" onClick={() => setIsOpen(false)}>
        Cancel
      </Button>
      <Button variant="danger" onClick={handleDelete}>
        Delete
      </Button>
    </>
  }
>
  This action cannot be undone.
</Modal>
```

---

### Spinner

Loading indicator with multiple sizes and colors.

**Features:**
- 3 sizes: sm, md, lg
- 6 color variants
- Accessible aria labels
- Overlay variant for full-page loading

**Usage:**
```tsx
import { Spinner, SpinnerOverlay } from '@/components/common';

// Inline spinner
<Spinner size="md" color="primary" label="Loading recipes..." />

// Full-page overlay
<SpinnerOverlay visible={isLoading} message="Fetching data..." />
```

---

### Pagination

Full-featured pagination with page numbers and items per page selector.

**Features:**
- Page numbers with ellipsis
- Previous/Next navigation
- Items per page selector
- Total items display
- Fully accessible

**Usage:**
```tsx
import { Pagination } from '@/components/common';

<Pagination
  currentPage={page}
  totalPages={totalPages}
  onPageChange={setPage}
  totalItems={totalRecipes}
  itemsPerPage={perPage}
  itemsPerPageOptions={[10, 25, 50, 100]}
  onItemsPerPageChange={setPerPage}
  showItemsPerPage
/>
```

---

### SearchBar

Debounced search input with clear button and loading state.

**Features:**
- Configurable debounce delay (default 300ms)
- Loading indicator
- Clear button
- Auto-focus option
- Keyboard shortcuts (Escape to clear)
- Multiple sizes

**Usage:**
```tsx
import { SearchBar } from '@/components/common';

const [searchQuery, setSearchQuery] = useState('');

<SearchBar
  value={searchQuery}
  onChange={setSearchQuery}
  loading={isSearching}
  placeholder="Search recipes..."
  debounceMs={300}
  fullWidth
/>
```

---

### Badge

Labels and tags for displaying metadata and status.

**Features:**
- 6 color variants: default, primary, success, warning, error, info
- 2 sizes: sm, md
- Removable option
- Pill shape option
- Outline variant
- Icon support

**Usage:**
```tsx
import { Badge, BadgeGroup } from '@/components/common';

// Single badge
<Badge color="success">Vegetarian</Badge>

// Removable badge
<Badge color="warning" removable onRemove={handleRemove}>
  Gluten-Free
</Badge>

// Badge group
<BadgeGroup gap="md">
  <Badge color="info">High Protein</Badge>
  <Badge color="success">Low Carb</Badge>
  <Badge color="primary">Quick</Badge>
</BadgeGroup>
```

---

### FilterPanel

Advanced filtering component with collapsible sections.

**Features:**
- Checkbox groups
- Range sliders
- Collapsible sections
- Clear all button
- Apply button option

**Usage:**
```tsx
import { FilterPanel } from '@/components/common';

const sections = [
  {
    id: 'dietary',
    title: 'Dietary Preferences',
    type: 'checkbox',
    options: [
      { id: 'veg', label: 'Vegetarian', selected: false, count: 45 },
      { id: 'vegan', label: 'Vegan', selected: false, count: 23 },
    ],
  },
  {
    id: 'nutrition',
    title: 'Nutrition',
    type: 'range',
    range: {
      id: 'protein',
      label: 'Minimum Protein',
      min: 0,
      max: 100,
      value: 30,
      unit: 'g',
    },
  },
];

<FilterPanel
  sections={sections}
  onCheckboxChange={handleCheckboxChange}
  onRangeChange={handleRangeChange}
  onClearAll={clearFilters}
  showApplyButton
/>
```

---

### EmptyState

Component for displaying empty or no-data states.

**Features:**
- Icon slot
- Title and description
- Primary and secondary action buttons
- Multiple sizes
- Custom content support

**Usage:**
```tsx
import { EmptyState } from '@/components/common';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

<EmptyState
  icon={<MagnifyingGlassIcon className="h-12 w-12" />}
  title="No recipes found"
  description="Try adjusting your search or filters."
  action={{
    label: 'Clear filters',
    onClick: clearFilters,
  }}
  secondaryAction={{
    label: 'Browse all recipes',
    onClick: () => navigate('/recipes'),
  }}
/>
```

---

### ErrorBoundary

React error boundary for graceful error handling.

**Features:**
- Catches React errors
- Retry functionality
- Custom fallback UI
- Error details view
- Error reporting callback

**Usage:**
```tsx
import { ErrorBoundary } from '@/components/common';

// Wrap your app or components
<ErrorBoundary
  onError={(error, errorInfo) => {
    logErrorToService(error, errorInfo);
  }}
>
  <App />
</ErrorBoundary>

// Custom fallback
<ErrorBoundary
  fallback={(error, resetError) => (
    <div>
      <h1>Something went wrong</h1>
      <button onClick={resetError}>Try again</button>
    </div>
  )}
>
  <MyComponent />
</ErrorBoundary>
```

---

### LoadingScreen

Full-page or inline loading states.

**Features:**
- Full page or inline
- Logo/icon slot
- Message display
- Overlay option
- Skeleton loaders
- Page loader with minimum duration

**Usage:**
```tsx
import { LoadingScreen, PageLoader, SkeletonLoader } from '@/components/common';

// Full page loading
<LoadingScreen message="Loading recipes..." />

// Page loader (route transitions)
<PageLoader isLoading={isNavigating} message="Loading page..." />

// Skeleton loaders
<SkeletonLoader variant="text" lines={3} />
<SkeletonLoader variant="card" height={200} />
<SkeletonLoader variant="circular" width={48} height={48} />
```

---

## Accessibility

All components follow WAI-ARIA best practices:

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader announcements
- Semantic HTML elements

## TypeScript

All components are fully typed with comprehensive interfaces exported for use in your application.

```tsx
import type { ButtonProps, BadgeColor, ModalSize } from '@/components/common';
```

## Testing

Comprehensive test suites using Vitest and React Testing Library ensure component reliability.

Run tests:
```bash
npm test src/components/common/__tests__/
```

## Dependencies

- React 18+
- Tailwind CSS 3+
- @headlessui/react (Modal component)
- @heroicons/react (Icons)

## File Structure

```
components/common/
├── Badge.tsx
├── Button.tsx
├── Card.tsx
├── EmptyState.tsx
├── ErrorBoundary.tsx
├── FilterPanel.tsx
├── LoadingScreen.tsx
├── Modal.tsx
├── Pagination.tsx
├── SearchBar.tsx
├── Spinner.tsx
├── index.ts
├── README.md
└── __tests__/
    ├── Badge.test.tsx
    ├── Button.test.tsx
    ├── Card.test.tsx
    └── SearchBar.test.tsx
```
