/**
 * Full page layout for nutrition dashboard with navigation and meta information.
 */

import React from 'react';
import { NutritionDashboard } from '../components/nutrition';

// ============================================================================
// COMPONENT
// ============================================================================

export const NutritionDashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NutritionDashboard />
      </div>
    </div>
  );
};

export default NutritionDashboardPage;
