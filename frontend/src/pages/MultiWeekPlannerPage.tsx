/**
 * MultiWeekPlannerPage - Create and manage multi-week meal plans.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMultiWeekPlans } from '../hooks/useMultiWeek';
import { useVarietyAnalysis } from '../hooks/useMultiWeek';
import { useMealPlanCost } from '../hooks/useCost';
import { MultiWeekView } from '../components/planner/MultiWeekView';
import { MultiWeekGenerateModal } from '../components/planner/MultiWeekGenerateModal';
import { VarietyIndicator } from '../components/planner/VarietyIndicator';
import { CostEstimate } from '../components/planner/CostEstimate';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { EmptyState } from '../components/common/EmptyState';
import { Spinner } from '../components/common/Spinner';

export const MultiWeekPlannerPage: React.FC = () => {
  const navigate = useNavigate();
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);

  const { data: plansData, isLoading, isError } = useMultiWeekPlans({ page: 1, page_size: 10 });

  const selectedPlan = plansData?.items.find(plan => plan.id === selectedPlanId);

  // Get all recipe IDs from the selected plan
  const recipeIds = selectedPlan?.weeks.flatMap(week =>
    week.days.flatMap(day =>
      day.meals.map(meal => meal.recipe.id)
    )
  ) || [];

  // Fetch variety analysis and cost for selected plan
  const { data: varietyData, isLoading: isLoadingVariety } = useVarietyAnalysis(
    recipeIds,
    !!selectedPlan
  );

  const { data: costData, isLoading: isLoadingCost } = useMealPlanCost(
    {
      recipe_ids: recipeIds,
      ...(selectedPlan?.start_date && { start_date: selectedPlan.start_date }),
      ...(selectedPlan?.end_date && { end_date: selectedPlan.end_date }),
    },
    !!selectedPlan
  );

  const handleGenerateSuccess = (planId: number): void => {
    setSelectedPlanId(planId);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-6 max-w-md">
          <p className="text-red-600">Failed to load meal plans. Please try again.</p>
        </Card>
      </div>
    );
  }

  const hasPlans = plansData && plansData.items.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Multi-Week Meal Planner</h1>
              <p className="mt-2 text-sm text-gray-600">
                Plan multiple weeks at once with optimized variety and cost
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={() => navigate('/meal-plans')}>
                View All Plans
              </Button>
              <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
                Generate New Plan
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        {!hasPlans ? (
          <EmptyState
            icon={
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            }
            title="No multi-week plans yet"
            description="Create your first multi-week meal plan to get started"
          >
            <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
              Generate Plan
            </Button>
          </EmptyState>
        ) : (
          <>
            {/* Plan Selector */}
            {plansData.items.length > 1 && (
              <div className="mb-6">
                <label htmlFor="plan-select" className="block text-sm font-medium text-gray-700 mb-2">
                  Select Plan
                </label>
                <select
                  id="plan-select"
                  value={selectedPlanId || ''}
                  onChange={(e) => setSelectedPlanId(Number(e.target.value))}
                  className="w-full md:w-96 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Choose a plan...</option>
                  {plansData.items.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name} ({plan.weeks_count} weeks)
                    </option>
                  ))}
                </select>
              </div>
            )}

            {!selectedPlan && plansData.items.length === 1 && plansData.items[0] && (
              <div className="mb-6">
                <Button
                  variant="primary"
                  onClick={() => setSelectedPlanId(plansData.items[0]!.id)}
                >
                  View {plansData.items[0]!.name}
                </Button>
              </div>
            )}

            {/* Main Content Layout */}
            {selectedPlan && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Plan View - 2 columns */}
                <div className="lg:col-span-2">
                  <MultiWeekView
                    multiWeekPlan={selectedPlan}
                    onEditWeek={(weekNum) => console.log('Edit week', weekNum)}
                    onDeleteWeek={(weekNum) => console.log('Delete week', weekNum)}
                  />
                </div>

                {/* Sidebar - 1 column */}
                <div className="space-y-6">
                  <VarietyIndicator
                    varietyData={varietyData}
                    isLoading={isLoadingVariety}
                  />

                  <CostEstimate
                    costData={costData}
                    isLoading={isLoadingCost}
                  />
                </div>
              </div>
            )}
          </>
        )}

        {/* Generate Modal */}
        <MultiWeekGenerateModal
          isOpen={showGenerateModal}
          onClose={() => setShowGenerateModal(false)}
          onSuccess={handleGenerateSuccess}
        />
      </div>
    </div>
  );
};
