/**
 * Zustand store for onboarding state with localStorage persistence.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// ============================================================================
// TYPES
// ============================================================================

export interface OnboardingPreferences {
  dietaryTags: string[];
  allergens: string[];
  householdSize: number;
  maxCookingTime: number | null;
}

interface OnboardingState {
  isComplete: boolean;
  currentStep: number;
  preferences: OnboardingPreferences;
}

interface OnboardingActions {
  setStep: (step: number) => void;
  setDietaryTags: (tags: string[]) => void;
  setAllergens: (allergens: string[]) => void;
  setHouseholdSize: (size: number) => void;
  setMaxCookingTime: (minutes: number | null) => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
}

type OnboardingStore = OnboardingState & OnboardingActions;

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialPreferences: OnboardingPreferences = {
  dietaryTags: [],
  allergens: [],
  householdSize: 2,
  maxCookingTime: null,
};

const initialState: OnboardingState = {
  isComplete: false,
  currentStep: 0,
  preferences: initialPreferences,
};

// ============================================================================
// STORE
// ============================================================================

export const useOnboardingStore = create<OnboardingStore>()(
  persist(
    (set) => ({
      ...initialState,

      setStep: (step) => set({ currentStep: step }),

      setDietaryTags: (tags) =>
        set((state) => ({
          preferences: { ...state.preferences, dietaryTags: tags },
        })),

      setAllergens: (allergens) =>
        set((state) => ({
          preferences: { ...state.preferences, allergens },
        })),

      setHouseholdSize: (size) =>
        set((state) => ({
          preferences: { ...state.preferences, householdSize: size },
        })),

      setMaxCookingTime: (minutes) =>
        set((state) => ({
          preferences: { ...state.preferences, maxCookingTime: minutes },
        })),

      completeOnboarding: () => set({ isComplete: true }),

      resetOnboarding: () => set(initialState),
    }),
    {
      name: 'onboarding-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
