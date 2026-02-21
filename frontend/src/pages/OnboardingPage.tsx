/**
 * Onboarding page - shown to first-time users before the dashboard.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { OnboardingWizard } from '../components/onboarding';
import { useOnboardingStore } from '../store/onboardingStore';

export const OnboardingPage: React.FC = () => {
  const isComplete = useOnboardingStore((state) => state.isComplete);

  if (isComplete) {
    return <Navigate to="/dashboard" replace />;
  }

  return <OnboardingWizard />;
};

export default OnboardingPage;
