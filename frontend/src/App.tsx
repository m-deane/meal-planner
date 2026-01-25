import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layout
import { Layout } from './components/layout';

// Pages
import { DashboardPage } from './pages/DashboardPage';
import { RecipeBrowserPage } from './pages/RecipeBrowserPage';
import { RecipeDetailPage } from './pages/RecipeDetailPage';
import { MealPlannerPage } from './pages/MealPlannerPage';
import { MealPlanDetailPage } from './pages/MealPlanDetailPage';
import { MultiWeekPlannerPage } from './pages/MultiWeekPlannerPage';
import { NutritionDashboardPage } from './pages/NutritionDashboardPage';
import { ShoppingListPage } from './pages/ShoppingListPage';
import { FavoritesPage } from './pages/FavoritesPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

const App: React.FC = () => {
  return (
    <Routes>
      {/* Auth routes (no layout) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Main app routes (with layout) */}
      <Route element={<Layout />}>
        {/* Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />

        {/* Recipes */}
        <Route path="/recipes" element={<RecipeBrowserPage />} />
        <Route path="/recipes/:slug" element={<RecipeDetailPage />} />

        {/* Meal Planning */}
        <Route path="/meal-planner" element={<MealPlannerPage />} />
        <Route path="/meal-plans" element={<Navigate to="/meal-planner" replace />} />
        <Route path="/meal-plans/new" element={<MealPlannerPage />} />
        <Route path="/meal-plans/:id" element={<MealPlanDetailPage />} />
        <Route path="/multi-week-planner" element={<MultiWeekPlannerPage />} />

        {/* Nutrition */}
        <Route path="/nutrition" element={<NutritionDashboardPage />} />

        {/* Shopping List */}
        <Route path="/shopping-list" element={<ShoppingListPage />} />

        {/* Favorites */}
        <Route path="/favorites" element={<FavoritesPage />} />

        {/* Profile */}
        <Route path="/profile" element={<ProfilePage />} />

        {/* 404 Not Found */}
        <Route
          path="*"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
                <p className="text-xl text-gray-600 mb-8">Page not found</p>
                <a
                  href="/dashboard"
                  className="text-green-600 hover:text-green-700 underline font-medium"
                >
                  Go back to dashboard
                </a>
              </div>
            </div>
          }
        />
      </Route>
    </Routes>
  );
};

export default App;
