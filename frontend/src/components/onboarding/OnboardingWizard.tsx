/**
 * Multi-step onboarding wizard for new users.
 * Captures dietary preferences, allergens, household size, and cooking time.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UtensilsCrossed,
  Leaf,
  ShieldAlert,
  Users,
  Clock,
  ChevronRight,
  ChevronLeft,
  Check,
  Sparkles,
} from 'lucide-react';
import { useOnboardingStore } from '../../store/onboardingStore';
import { useDietaryTags, useAllergens } from '../../hooks/useCategories';

// ============================================================================
// STEP DEFINITIONS
// ============================================================================

const STEPS = [
  { id: 'welcome', label: 'Welcome', icon: Sparkles },
  { id: 'dietary', label: 'Diet', icon: Leaf },
  { id: 'allergens', label: 'Allergens', icon: ShieldAlert },
  { id: 'household', label: 'Household', icon: Users },
] as const;

// ============================================================================
// STEP COMPONENTS
// ============================================================================

const WelcomeStep: React.FC = () => (
  <div className="text-center max-w-lg mx-auto">
    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
      <UtensilsCrossed className="w-10 h-10 text-green-600" />
    </div>
    <h2 className="text-3xl font-bold text-gray-900 mb-4">
      Welcome to Meal Planner
    </h2>
    <p className="text-lg text-gray-600 mb-6">
      Let's personalise your experience in a few quick steps. We'll use your
      preferences to suggest recipes and generate meal plans tailored to you.
    </p>
    <div className="grid grid-cols-3 gap-4 text-sm text-gray-500">
      <div className="flex flex-col items-center gap-2 p-4 bg-gray-50 rounded-lg">
        <Leaf className="w-5 h-5 text-green-500" />
        <span>Dietary preferences</span>
      </div>
      <div className="flex flex-col items-center gap-2 p-4 bg-gray-50 rounded-lg">
        <ShieldAlert className="w-5 h-5 text-amber-500" />
        <span>Allergen safety</span>
      </div>
      <div className="flex flex-col items-center gap-2 p-4 bg-gray-50 rounded-lg">
        <Users className="w-5 h-5 text-blue-500" />
        <span>Household size</span>
      </div>
    </div>
  </div>
);

interface DietaryStepProps {
  selected: string[];
  onToggle: (tag: string) => void;
}

const DietaryStep: React.FC<DietaryStepProps> = ({ selected, onToggle }) => {
  const { data: dietaryTags, isLoading } = useDietaryTags();

  return (
    <div className="max-w-lg mx-auto">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Leaf className="w-7 h-7 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Dietary Preferences
        </h2>
        <p className="text-gray-600">
          Select any dietary requirements. We'll filter recipes accordingly.
          Skip if none apply.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {(dietaryTags ?? []).map((tag) => {
            const isSelected = selected.includes(tag.slug);
            return (
              <button
                key={tag.id}
                onClick={() => onToggle(tag.slug)}
                className={`
                  flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left
                  ${isSelected
                    ? 'border-green-500 bg-green-50 text-green-800'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
                    ${isSelected ? 'border-green-500 bg-green-500' : 'border-gray-300'}
                  `}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
                <span className="font-medium text-sm">{tag.name}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

interface AllergenStepProps {
  selected: string[];
  onToggle: (allergen: string) => void;
}

const AllergenStep: React.FC<AllergenStepProps> = ({ selected, onToggle }) => {
  const { data: allergens, isLoading } = useAllergens();

  return (
    <div className="max-w-lg mx-auto">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShieldAlert className="w-7 h-7 text-amber-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Allergen Awareness
        </h2>
        <p className="text-gray-600">
          Select any allergens to avoid. We'll flag recipes that contain these
          ingredients. Skip if none apply.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="w-8 h-8 border-4 border-amber-200 border-t-amber-600 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {(allergens ?? []).map((allergen) => {
            const isSelected = selected.includes(allergen.name);
            return (
              <button
                key={allergen.id}
                onClick={() => onToggle(allergen.name)}
                className={`
                  flex items-center gap-3 p-4 rounded-lg border-2 transition-all text-left
                  ${isSelected
                    ? 'border-amber-500 bg-amber-50 text-amber-800'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
                    ${isSelected ? 'border-amber-500 bg-amber-500' : 'border-gray-300'}
                  `}
                >
                  {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
                <span className="font-medium text-sm">{allergen.name}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

interface HouseholdStepProps {
  householdSize: number;
  maxCookingTime: number | null;
  onHouseholdSizeChange: (size: number) => void;
  onMaxCookingTimeChange: (minutes: number | null) => void;
}

const HouseholdStep: React.FC<HouseholdStepProps> = ({
  householdSize,
  maxCookingTime,
  onHouseholdSizeChange,
  onMaxCookingTimeChange,
}) => {
  const cookingTimeOptions = [
    { value: null, label: 'Any time', description: 'No preference' },
    { value: 20, label: 'Quick', description: '20 min or less' },
    { value: 30, label: 'Medium', description: '30 min or less' },
    { value: 45, label: 'Standard', description: '45 min or less' },
    { value: 60, label: 'Leisurely', description: '60 min or less' },
  ];

  return (
    <div className="max-w-lg mx-auto">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Users className="w-7 h-7 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Household & Cooking
        </h2>
        <p className="text-gray-600">
          Tell us about your household so we can adjust portions and find recipes
          that fit your schedule.
        </p>
      </div>

      {/* Household Size */}
      <div className="mb-8">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          How many people are you cooking for?
        </label>
        <div className="flex items-center gap-4">
          <button
            onClick={() => onHouseholdSizeChange(Math.max(1, householdSize - 1))}
            disabled={householdSize <= 1}
            className="w-10 h-10 rounded-full border-2 border-gray-300 flex items-center justify-center text-lg font-bold text-gray-600 hover:border-blue-400 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            -
          </button>
          <div className="flex-1 text-center">
            <span className="text-4xl font-bold text-gray-900">{householdSize}</span>
            <p className="text-sm text-gray-500 mt-1">
              {householdSize === 1 ? 'person' : 'people'}
            </p>
          </div>
          <button
            onClick={() => onHouseholdSizeChange(Math.min(10, householdSize + 1))}
            disabled={householdSize >= 10}
            className="w-10 h-10 rounded-full border-2 border-gray-300 flex items-center justify-center text-lg font-bold text-gray-600 hover:border-blue-400 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            +
          </button>
        </div>
      </div>

      {/* Cooking Time Preference */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          <Clock className="w-4 h-4 inline mr-1" />
          Preferred cooking time
        </label>
        <div className="grid grid-cols-1 gap-2">
          {cookingTimeOptions.map((option) => {
            const isSelected = maxCookingTime === option.value;
            return (
              <button
                key={option.label}
                onClick={() => onMaxCookingTimeChange(option.value)}
                className={`
                  flex items-center justify-between p-3 rounded-lg border-2 transition-all
                  ${isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                <span className={`font-medium text-sm ${isSelected ? 'text-blue-800' : 'text-gray-700'}`}>
                  {option.label}
                </span>
                <span className={`text-xs ${isSelected ? 'text-blue-600' : 'text-gray-500'}`}>
                  {option.description}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN WIZARD
// ============================================================================

export const OnboardingWizard: React.FC = () => {
  const navigate = useNavigate();
  const {
    preferences,
    setDietaryTags,
    setAllergens,
    setHouseholdSize,
    setMaxCookingTime,
    completeOnboarding,
  } = useOnboardingStore();

  const [step, setStep] = useState(0);
  const totalSteps = STEPS.length;

  const toggleDietaryTag = (slug: string) => {
    const current = preferences.dietaryTags;
    setDietaryTags(
      current.includes(slug)
        ? current.filter((t) => t !== slug)
        : [...current, slug]
    );
  };

  const toggleAllergen = (name: string) => {
    const current = preferences.allergens;
    setAllergens(
      current.includes(name)
        ? current.filter((a) => a !== name)
        : [...current, name]
    );
  };

  const handleNext = () => {
    if (step < totalSteps - 1) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  const handleFinish = () => {
    completeOnboarding();
    navigate('/meal-planner');
  };

  const handleSkip = () => {
    completeOnboarding();
    navigate('/dashboard');
  };

  const isLastStep = step === totalSteps - 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex flex-col">
      {/* Progress Bar */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-2xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <UtensilsCrossed className="w-6 h-6 text-green-600" />
              <span className="font-bold text-gray-900">Meal Planner Setup</span>
            </div>
            <button
              onClick={handleSkip}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Skip setup
            </button>
          </div>

          {/* Step Indicators */}
          <div className="flex items-center gap-2">
            {STEPS.map((s, i) => {
              const StepIcon = s.icon;
              const isActive = i === step;
              const isDone = i < step;
              return (
                <React.Fragment key={s.id}>
                  {i > 0 && (
                    <div
                      className={`flex-1 h-0.5 ${isDone ? 'bg-green-500' : 'bg-gray-200'}`}
                    />
                  )}
                  <div
                    className={`
                      flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                      ${isActive
                        ? 'bg-green-100 text-green-700'
                        : isDone
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-100 text-gray-500'
                      }
                    `}
                  >
                    {isDone ? (
                      <Check className="w-3.5 h-3.5" />
                    ) : (
                      <StepIcon className="w-3.5 h-3.5" />
                    )}
                    <span className="hidden sm:inline">{s.label}</span>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        {step === 0 && <WelcomeStep />}
        {step === 1 && (
          <DietaryStep
            selected={preferences.dietaryTags}
            onToggle={toggleDietaryTag}
          />
        )}
        {step === 2 && (
          <AllergenStep
            selected={preferences.allergens}
            onToggle={toggleAllergen}
          />
        )}
        {step === 3 && (
          <HouseholdStep
            householdSize={preferences.householdSize}
            maxCookingTime={preferences.maxCookingTime}
            onHouseholdSizeChange={setHouseholdSize}
            onMaxCookingTimeChange={setMaxCookingTime}
          />
        )}
      </div>

      {/* Navigation Footer */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={step === 0}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 disabled:opacity-0 disabled:pointer-events-none"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </button>

          <span className="text-sm text-gray-400">
            {step + 1} of {totalSteps}
          </span>

          {isLastStep ? (
            <button
              onClick={handleFinish}
              className="flex items-center gap-2 px-6 py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              Get Started
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-6 py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors shadow-sm"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
