# Meal Planner Frontend

React + TypeScript + Vite frontend for the Gousto Recipe Database Scraper meal planning application.

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Utility-first styling
- **Headless UI** - Accessible UI components
- **DnD Kit** - Drag-and-drop functionality
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Vitest** - Unit testing
- **Testing Library** - Component testing

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
npm run test:ui      # Run tests with UI
npm run test:coverage # Generate coverage report
npm run lint         # Lint code
npm run type-check   # TypeScript type checking
```

## Project Structure

```
frontend/
├── src/
│   ├── api/          # API client and hooks
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page components
│   ├── hooks/        # Custom React hooks
│   ├── store/        # Zustand state stores
│   ├── types/        # TypeScript type definitions
│   ├── utils/        # Utility functions
│   ├── styles/       # Global styles
│   ├── test/         # Test setup
│   ├── App.tsx       # Root component
│   └── main.tsx      # Entry point
├── public/           # Static assets
├── index.html        # HTML template
└── vite.config.ts    # Vite configuration
```

## Features

### Current Routes

- `/dashboard` - Main dashboard (placeholder)
- `/recipes` - Recipe browsing (placeholder)
- `/recipes/:id` - Recipe details (placeholder)
- `/meal-plans` - Meal plans list (placeholder)
- `/meal-plans/new` - Create meal plan (placeholder)
- `/meal-plans/:id` - Meal plan details (placeholder)
- `/shopping-list` - Shopping list (placeholder)

### Planned Features

- Recipe browsing with filtering and search
- Meal plan creation with drag-and-drop
- Nutrition tracking and visualization
- Shopping list generation
- Dietary preference management
- Allergen filtering

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Meal Planner
VITE_APP_VERSION=1.0.0
```

### TypeScript Configuration

The project uses strict TypeScript settings:
- Strict mode enabled
- No unchecked indexed access
- Explicit function return types recommended
- Path aliases configured (@/, @components/, etc.)

### Tailwind Configuration

Custom color palette and utilities configured in `tailwind.config.js`:
- Primary color scheme (green)
- Secondary color scheme (purple)
- Custom animations
- Utility classes for buttons, cards, badges, etc.

## Testing

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## Building for Production

```bash
# Build the application
npm run build

# Preview the production build
npm run preview
```

The build output will be in the `dist/` directory.

## Code Quality

### ESLint

Configured with strict TypeScript rules:
- No `any` types
- Explicit function return types
- Unused variable detection
- React hooks rules

### Type Safety

- Strict TypeScript configuration
- Path aliases for clean imports
- Type definitions for environment variables
- Comprehensive type coverage

## Contributing

When adding new features:

1. Create components in `src/components/`
2. Add API calls in `src/api/`
3. Define types in `src/types/`
4. Write tests alongside implementation
5. Follow existing naming conventions
6. Use TypeScript strict mode
7. Run linting and type checking before committing

## License

Private - Part of the Meal Planner application
