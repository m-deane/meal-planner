import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Meal Planner
                </h1>
                <p className="text-lg text-gray-600">
                  Dashboard page - Coming soon
                </p>
              </div>
            </div>
          }
        />

        {/* Recipes */}
        <Route
          path="/recipes"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Recipes
                </h1>
                <p className="text-lg text-gray-600">
                  Recipe browsing page - Coming soon
                </p>
              </div>
            </div>
          }
        />
        <Route
          path="/recipes/:id"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Recipe Details
                </h1>
                <p className="text-lg text-gray-600">
                  Recipe detail page - Coming soon
                </p>
              </div>
            </div>
          }
        />

        {/* Meal Planning */}
        <Route
          path="/meal-plans"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Meal Plans
                </h1>
                <p className="text-lg text-gray-600">
                  Meal planning page - Coming soon
                </p>
              </div>
            </div>
          }
        />
        <Route
          path="/meal-plans/new"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Create Meal Plan
                </h1>
                <p className="text-lg text-gray-600">
                  Meal plan creation page - Coming soon
                </p>
              </div>
            </div>
          }
        />
        <Route
          path="/meal-plans/:id"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Meal Plan Details
                </h1>
                <p className="text-lg text-gray-600">
                  Meal plan detail page - Coming soon
                </p>
              </div>
            </div>
          }
        />

        {/* Shopping List */}
        <Route
          path="/shopping-list"
          element={
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Shopping List
                </h1>
                <p className="text-lg text-gray-600">
                  Shopping list page - Coming soon
                </p>
              </div>
            </div>
          }
        />

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
                  className="text-primary-600 hover:text-primary-700 underline"
                >
                  Go back to dashboard
                </a>
              </div>
            </div>
          }
        />
      </Routes>
    </div>
  );
};

export default App;
